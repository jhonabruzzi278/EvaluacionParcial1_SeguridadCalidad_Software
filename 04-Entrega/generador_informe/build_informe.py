#!/usr/bin/env python3
"""Genera el informe EP3 sobre la plantilla del docente. Uso: ver make.sh (3 pasadas para fijar los números del índice)."""
import copy
import datetime
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from lxml import etree

import tempfile
REPO = Path(__file__).resolve().parents[2]
SCR = Path(tempfile.gettempdir()) / 'atlas_informe'
SCR.mkdir(exist_ok=True)
TEMPLATE = REPO / '04-Entrega/EP3_ISY1102_Estudiante_Formato_Informe.docx'
OUT = REPO / '04-Entrega/EP3/EP3_ISY1102_Informe_Atlas.docx'
WORK = SCR / 'build'

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NSDECL = f'xmlns:w="{W}"'
NSBODY = (f'xmlns:w="{W}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
          'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
          'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
          'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"')
ns = {'w': W}
FULL = 9746  # ancho útil de página en dxa

PAGES = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}

# ----------------------------------------------------------------- helpers XML

def rpr(size=22, bold=False, italic=False, color=None):
    s = '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial" w:cs="Arial"/>'
    s += '<w:b w:val="1"/><w:bCs w:val="1"/>' if bold else ''
    s += '<w:i w:val="1"/><w:iCs w:val="1"/>' if italic else ''
    s += f'<w:color w:val="{color}"/>' if color else ''
    s += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/><w:lang w:val="es-ES"/></w:rPr>'
    return s


def runs(text, size=22, bold=False, italic=False, color=None):
    """Texto con **negrita** inline."""
    out = []
    for i, part in enumerate(re.split(r'\*\*', text)):
        if part == '':
            continue
        b = bold or (i % 2 == 1)
        out.append(f'<w:r>{rpr(size, b, italic, color)}<w:t xml:space="preserve">{escape(part)}</w:t></w:r>')
    return ''.join(out)


def P(text, size=22, jc='both', after=120, line=360, bold=False, italic=False, color=None, keep_next=False, ind=None):
    ppr = '<w:pPr>'
    ppr += '<w:keepNext/>' if keep_next else ''
    ppr += f'<w:spacing w:before="0" w:after="{after}" w:line="{line}" w:lineRule="auto"/>'
    ppr += f'<w:ind w:left="{ind}"/>' if ind else ''
    ppr += f'<w:jc w:val="{jc}"/></w:pPr>'
    return f'<w:p>{ppr}{runs(text, size, bold, italic, color)}</w:p>'


def B(text, size=22):
    ppr = ('<w:pPr><w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="34"/></w:numPr>'
           '<w:spacing w:before="0" w:after="60" w:line="360" w:lineRule="auto"/><w:contextualSpacing w:val="0"/><w:jc w:val="both"/></w:pPr>')
    return f'<w:p>{ppr}{runs(text, size)}</w:p>'


HEADINGS = []  # (nivel, texto, bookmark)


def H(level, text, pb=False):
    bid = len(HEADINGS) + 100
    name = f'_Toc{9000000 + bid}'
    HEADINGS.append((level, text, name))
    pbb = '<w:pageBreakBefore/>' if pb else ''
    bdr = '<w:pBdr><w:bottom w:val="single" w:sz="6" w:space="2" w:color="808080"/></w:pBdr>' if level == 1 else ''
    return (f'<w:p><w:pPr><w:pStyle w:val="Heading{level}"/>{pbb}{bdr}<w:jc w:val="left"/></w:pPr>'
            f'<w:bookmarkStart w:id="{bid}" w:name="{name}"/>{runs(text, 24, True)}'
            f'<w:bookmarkEnd w:id="{bid}"/></w:p>')


def PAGEBREAK():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def SPACER(after=120):
    return f'<w:p><w:pPr><w:spacing w:before="0" w:after="{after}" w:line="240" w:lineRule="auto"/></w:pPr></w:p>'


BORDERS = ('<w:tblBorders><w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/><w:left w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
           '<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/><w:right w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
           '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="808080"/><w:insideV w:val="single" w:sz="4" w:space="0" w:color="808080"/></w:tblBorders>')


def cell_paras(spec, size, bold, color, jc):
    paras = spec if isinstance(spec, list) else [spec]
    out = ''
    for t in paras:
        hang = ''
        m = re.match(r'^(\d+\.|[-•☐])\s', t)
        if m:
            hang = '<w:ind w:left="284" w:hanging="284"/>'
        out += (f'<w:p><w:pPr><w:spacing w:before="20" w:after="20" w:line="240" w:lineRule="auto"/>{hang}'
                f'<w:jc w:val="{jc}"/></w:pPr>{runs(t, size, bold, False, color)}</w:p>')
    return out


def tc(spec, width, span=1, fill=None, bold=False, color=None, size=20, jc='left'):
    if isinstance(spec, dict):
        fill = spec.get('fill', fill)
        bold = spec.get('bold', bold)
        color = spec.get('color', color)
        span = spec.get('span', span)
        width = spec.get('width', width)
        jc = spec.get('jc', jc)
        spec = spec['t']
    pr = f'<w:tcW w:w="{width}" w:type="dxa"/>'
    pr += f'<w:gridSpan w:val="{span}"/>' if span > 1 else ''
    pr += f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>' if fill else ''
    pr += '<w:tcMar><w:left w:w="100" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tcMar><w:vAlign w:val="center"/>'
    return f'<w:tc><w:tcPr>{pr}</w:tcPr>{cell_paras(spec, size, bold, color, jc)}</w:tc>'


def tr(cells, header=False, cant_split=False):
    pr = ''
    pr += '<w:cantSplit/>' if cant_split else ''
    pr += '<w:tblHeader/>' if header else ''
    return f'<w:tr><w:trPr>{pr}<w:trHeight w:val="320"/></w:trPr>{"".join(cells)}</w:tr>'


TABLES = []  # textos de leyenda, en orden


def CAP(text):
    n = len(TABLES) + 1
    TABLES.append(text)
    bid = 500 + n
    return (f'<w:p><w:pPr><w:keepNext/><w:spacing w:before="120" w:after="60" w:line="240" w:lineRule="auto"/><w:jc w:val="left"/></w:pPr>'
            f'<w:bookmarkStart w:id="{bid}" w:name="_TocTbl{n}"/>{runs("Tabla ", 20, True)}'
            '<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> SEQ Tabla \\* ARABIC </w:instrText></w:r>'
            f'<w:r><w:fldChar w:fldCharType="separate"/></w:r>{runs(str(n), 20, True)}<w:r><w:fldChar w:fldCharType="end"/></w:r>'
            f'{runs(". " + text, 20, True)}<w:bookmarkEnd w:id="{bid}"/></w:p>')


def TABLE(widths, rows, header=True, size=20, first_col_bold=False, fills=None, cap=None):
    """rows: lista de filas; cada fila lista de celdas (str | list | dict)."""
    grid = ''.join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    x = (CAP(cap) if cap else '')
    x += (f'<w:tbl><w:tblPr><w:tblW w:w="{sum(widths)}" w:type="dxa"/>{BORDERS}<w:tblLayout w:type="fixed"/>'
         '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr>'
         f'<w:tblGrid>{grid}</w:tblGrid>')
    for ri, row in enumerate(rows):
        cells = []
        for ci, c in enumerate(row):
            if ri == 0 and header:
                cells.append(tc(c, widths[ci], fill='000000', bold=True, color='FFFFFF', size=size))
            else:
                cells.append(tc(c, widths[ci], bold=(first_col_bold and ci == 0), size=size))
        x += tr(cells, header=(ri == 0 and header), cant_split=True)
    return x + '</w:tbl>'


def CASE(cid, nombre, req, tipo, desc, pre, pasos, esperado, criterios, datos):
    w = [1750, 4950, 3046]
    x = CAP(f'Caso de prueba {cid}: {nombre}')
    x += (f'<w:tbl><w:tblPr><w:tblW w:w="{FULL}" w:type="dxa"/>{BORDERS}<w:tblLayout w:type="fixed"/></w:tblPr>'
         f'<w:tblGrid>{"".join(f"<w:gridCol w:w=\"{i}\"/>" for i in w)}</w:tblGrid>')
    x += tr([tc('ID', w[0], fill='000000', bold=True, color='FFFFFF'), tc('NOMBRE', w[1], fill='000000', bold=True, color='FFFFFF'),
             tc('REQUERIMIENTO', w[2], fill='000000', bold=True, color='FFFFFF')], header=False, cant_split=True)
    x += tr([tc(cid, w[0], bold=True), tc(nombre, w[1]), tc(req, w[2])], cant_split=True)
    for label, body in [('DESCRIPCIÓN', desc), ('PRECONDICIONES', pre), ('PASOS', pasos), ('RESULTADO ESPERADO', esperado),
                        ('CRITERIO DE ACEPTACIÓN', criterios), ('DATOS DE PRUEBA', datos), ('TIPO DE PRUEBA', tipo)]:
        x += tr([tc(label, FULL, span=3, fill='E8E8E8', bold=True)], cant_split=True)
        x += tr([tc(body, FULL, span=3)])
    return x + '</w:tbl>'


IMGS = []  # (rId, archivo origen, nombre destino)


def IMG(src, alt, width_in=5.9, px=(1440, 1000)):
    n = len(IMGS) + 1
    rid = f'rIdSonar{n}'
    IMGS.append((rid, src, f'sonar_{n}.png'))
    cx = int(width_in * 914400)
    cy = int(cx * px[1] / px[0])
    return (f'<w:p><w:pPr><w:keepNext/><w:spacing w:before="0" w:after="60"/><w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
            f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
            f'<wp:docPr id="{900 + n}" name="sonar_{n}" descr="{escape(alt)}"/>'
            '<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic>'
            f'<pic:nvPicPr><pic:cNvPr id="{900 + n}" name="sonar_{n}.png"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
            '</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')


def MONO(title, lines_):
    paras = ''.join(f'<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/><w:jc w:val="left"/></w:pPr>'
                    f'<w:r><w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New"/><w:sz w:val="16"/><w:szCs w:val="16"/><w:lang w:val="es-ES"/></w:rPr>'
                    f'<w:t xml:space="preserve">{escape(l)}</w:t></w:r></w:p>' for l in lines_)
    return (CAP(title) + f'<w:tbl><w:tblPr><w:tblW w:w="{FULL}" w:type="dxa"/>{BORDERS}<w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid><w:gridCol w:w="{FULL}"/></w:tblGrid>'
            f'<w:tr><w:tc><w:tcPr><w:tcW w:w="{FULL}" w:type="dxa"/><w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/><w:tcMar><w:left w:w="120" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tcMar></w:tcPr>{paras}</w:tc></w:tr></w:tbl>')


SEV = {'CRÍTICO': 'FF0000', 'GRAVE': 'FFA500', 'MODERADO': 'FFE066', 'LEVE': '92D050'}

# ------------------------------------------------------------------ contenido

KEEP = ['PT-FUNC-001', 'PT-FUNC-002', 'PT-FUNC-008', 'PT-FUNC-010', 'PT-SEG-001', 'PT-SEG-002', 'PT-SEG-008', 'PT-SEG-009', 'PT-PERF-001', 'PT-USAB-001']
_mat = (REPO / '03-Anexos/Matrices/matriz_trazabilidad.md').read_text(encoding='utf-8').split('## 9.')[0]
MAT = []
for _l in _mat.splitlines():
    if re.match(r'^\| (RF-|NFR-|RB-|§|Criterio)', _l):
        _c = [x.strip() for x in _l.strip().strip('|').split('|')]
        MAT.append((_c[0], _c[2], _c[3]))
assert len(MAT) == 45, len(MAT)
COVM = [m for m in MAT if any(k in m[1] for k in KEEP)]
ALC_REQ = [m for m in COVM if not m[0].startswith(('§', 'Criterio'))]
ALC_N = len(ALC_REQ)

body = []
A = body.append

# =========================================================== 1. Introducción
A(H(1, '1. Introducción', pb=True))
A(H(2, '1.1 Contexto del sistema'))
A(P('Atlas es una plataforma web de gestión de clientes y contratos para pequeñas y medianas empresas (pymes) chilenas. Permite registrar empresas, administrar usuarios con roles '
    '(administrador y editor), gestionar clientes y contratos, adjuntar un documento a cada contrato y auditar las acciones críticas. Se compone de un frontend React, un backend '
    'Node.js/Express y una base de datos PostgreSQL, desplegados con Docker Compose (frontend en el puerto 3350 y API en el 4450). Su Especificación de Requerimientos de Software (ERS v1.1) '
    'define **42 requerimientos**: 17 funcionales (RF), 20 no funcionales (NFR) y 5 reglas de negocio (RB).'))
A(P('Atlas maneja datos sensibles de terceros (RUT, direcciones, correos, teléfonos, datos bancarios y documentos contractuales). Un defecto puede comprometer la privacidad de los clientes finales de cada pyme y el cumplimiento de la normativa chilena.'))
A(H(2, '1.2 Propósito y alcance'))
A(P('El plan de pruebas busca asegurar que Atlas **cumple el ERS** (calidad), **protege los datos y los accesos** (seguridad) y **respeta el marco legal y ético aplicable** (cumplimiento normativo).'))
A(P(f'**Dentro del alcance:** {ALC_N} de los 42 requerimientos del ERS (más el criterio de aceptación de interfaz §3.1.1), elegidos por riesgo (probabilidad × impacto) y verificados con 10 casos de prueba funcionales, de seguridad, de rendimiento y de usabilidad, '
    'además del análisis estático del código y la verificación técnica del cumplimiento de las leyes 19.628 y 20.422. El ERS no se modificó: los demás requerimientos quedan **fuera del alcance de este ciclo**. '
    '**Fuera del alcance:** compatibilidad, disponibilidad, TLS, cifrado en reposo y la mayor parte de usabilidad (riesgo residual declarado), pruebas unitarias (el código no las incluye y el ERS no las exige), auditoría legal formal, escalabilidad horizontal y despliegue en producción.'))
A(H(2, '1.3 Objetivos'))
A(TABLE([600, 3500, 3446, 2200], [
    ['N.º', 'Objetivo', 'Indicador de logro', 'Requerimiento / norma'],
    ['O1', 'Verificar las funciones y reglas de negocio del ERS.', 'Resultado verificado y con evidencia para cada RF y RB del alcance.', 'RF-1 a 6; RB-1 a 5'],
    ['O2', 'Verificar los controles de seguridad.', '0 escrituras con rol editor; contraseñas con bcrypt; 0 alertas altas en ZAP.', 'NFR-SEG-1 a 9; Ley 19.628'],
    ['O3', 'Medir el rendimiento frente a los umbrales del ERS.', 'p95 < 300 ms en CRUD simples; error 5xx < 1 %.', 'NFR-PERF-1 a 3'],
    ['O4', 'Evaluar usabilidad y accesibilidad.', 'Lighthouse ≥ 90 y 0 incidencias críticas en axe.', 'NFR-USAB-1; Ley 20.422'],
    ['O5', 'Asegurar trazabilidad y cobertura.', 'Cobertura de diseño del alcance: 100 %; cobertura frente al ERS completo informada.', 'Anexo A'],
    ['O6', 'Clasificar los defectos y analizar su impacto ético y normativo.', 'Cada incidente con ID, caso, requerimiento, evidencia, criticidad y norma.', 'Secciones 5 y 6'],
], cap='Objetivos del plan de pruebas'))
A(SPACER())
A(H(2, '1.4 Ajustes respecto de la primera evaluación'))
A(P('Se incorporó la retroalimentación del docente a EP1: el índice quedó definido (índice general e índice de tablas); la cobertura se midió sobre los 42 requerimientos reales del ERS (en EP1 se contaban 6) '
    'y se separó cobertura de diseño y de ejecución (sección 4.2); y los casos usan las rutas reales del backend y se priorizan por riesgo.'))

# =========================================================== 2. Criterios
A(H(1, '2. Criterios de calidad'))
A(H(2, '2.1 Importancia de la calidad, la seguridad y el cumplimiento legal'))
A(P('**Calidad.** El ERS fija 300 ms para operaciones CRUD simples, pero la ejecución midió un p95 de 4,0 s en el login y en el listado de clientes por un retardo artificial en el código: cada ingreso de una pyme es lento y se incumple un requisito medible. '
    'El análisis estático detectó además 25 bugs de confiabilidad, como promesas sin manejo de errores en la interfaz.'))
A(P('**Seguridad.** En la ejecución, el token de sesión no incluye el rol y un usuario editor pudo crear, modificar y eliminar datos e incluso crear un usuario administrador, aunque el ERS indica que solo puede leer (RB-4). '
    'Las consecuencias recaen en los clientes finales de las pymes, que nunca interactúan con el sistema.'))
A(P('**Cumplimiento legal.** Atlas almacena datos personales y bancarios: el artículo 11 de la Ley 19.628 obliga a quien administra el banco de datos a cuidarlos, y la Ley 20.422 y WCAG 2.1 AA orientan la accesibilidad para adultos mayores. '
    'Los tres aspectos se verifican a la vez y cada resultado se vincula a un requerimiento y a una norma.'))
A(H(2, '2.2 Criterios de calidad del producto'))
A(TABLE([2000, 5546, 2200], [
    ['Característica', 'Criterio de calidad (medible)', 'Requerimiento'],
    ['Usabilidad y accesibilidad', 'Tipografía legible, contraste ≥ 4,5:1 y controles grandes para adultos mayores; flujos de registro, creación de empresa y cliente → contratos claros; ayuda contextual y mensajes de error amigables.', 'NFR-USAB-1 a 4'],
    ['Rendimiento', 'CRUD simples < 300 ms (p95); página principal < 2 s en conexión móvil; 200 usuarios concurrentes; subida y descarga de documentos ≤ 10 s.', 'NFR-PERF-1 a 3; criterio RF-5'],
    ['Estabilidad y confiabilidad', 'Disponibilidad objetivo 99,5 % mensual; recuperación tras caída y datos persistentes tras reinicio.', 'NFR-DIS-1'],
    ['Mantenibilidad', 'Ventana de mantenimiento y migración segura; sin defectos de alta severidad según análisis estático.', 'NFR-DIS-2'],
    ['Compatibilidad', 'Funcionamiento idéntico en las últimas 2 versiones de Chrome, Firefox, Safari y Edge; diseño responsivo.', 'NFR-COMPAT-1, 2'],
    ['Adecuación funcional', 'Autenticación, usuarios y roles, clientes, contratos con documento y auditoría operan según el ERS.', 'RF-1 a 6; RB-1 a 5'],
], cap='Criterios de calidad del producto'))
A(SPACER())
A(H(2, '2.3 Criterios de seguridad'))
A(B('**Protección de datos:** contraseñas con hash bcrypt (NFR-SEG-2), TLS (NFR-SEG-1), cifrado de datos sensibles en reposo (NFR-SEG-3) y cumplimiento de protección de datos personales (NFR-SEG-8).'))
A(B('**Control de acceso:** autorización por rol validada en el backend (NFR-SEG-4; RB-4 y RB-5), aislamiento entre empresas (RB-2) y sesión JWT con expiración (NFR-SEG-9).'))
A(B('**Manejo de errores:** respuestas genéricas al usuario y detalle solo en logs internos, sin secretos (NFR-SEG-6).'))
A(B('**Integridad:** validación de entradas contra inyección SQL, XSS y CSRF (NFR-SEG-5), auditoría de acciones críticas (RF-6.1) y respaldo y recuperación (NFR-SEG-7).'))
A(H(2, '2.4 Normativa y estándares aplicables'))
A(TABLE([2300, 5346, 2100], [
    ['Norma / estándar', 'Aplicación a Atlas', 'Vínculo con el ERS'],
    ['Ley 19.628 (vida privada)', 'Atlas almacena datos personales y bancarios; el art. 11 exige deber de cuidado del responsable del banco de datos.', 'NFR-SEG-1, 2, 3, 8'],
    ['Ley 21.719 (datos personales)', 'Publicada en diciembre de 2024 con vigencia diferida (a confirmar: 1 de diciembre de 2026). Se usa como referencia de buenas prácticas.', 'NFR-SEG-8'],
    ['Ley 20.422 y WCAG 2.1 AA', 'Accesibilidad para personas con discapacidad y adultos mayores: contraste, teclado, etiquetas.', 'NFR-USAB-1'],
    ['ISO/IEC 25010', 'Modelo de calidad que estructura los criterios de la sección 2.2.', 'NFR-PERF, USAB, DIS, COMPAT'],
    ['OWASP Top 10 (2021) y Testing Guide', 'Clasificación de vulnerabilidades y metodología de pruebas de seguridad.', 'NFR-SEG-4, 5, 6, 9'],
    ['Ley 21.459 (delitos informáticos)', 'Límite ético: las pruebas intrusivas se hacen solo en el entorno Docker entregado, con datos ficticios.', 'Marco de ejecución'],
], cap='Normativa y estándares aplicables'))
A(SPACER())

# =========================================================== 3. Plan de pruebas
A(H(1, '3. Plan de pruebas'))
A(H(2, '3.1 Estrategia de pruebas'))
A(P('Enfoque **mixto y basado en riesgo**: se automatiza lo repetible y medible (API, carga, escaneo de código y de la aplicación) y se ejecuta manualmente lo que exige juicio humano '
    '(revisión de código e interpretación de los resultados de las herramientas). La seguridad tiene prioridad porque Atlas maneja datos personales.'))
A(B('**Enfoque:** SAST (análisis estático), DAST (aplicación en ejecución) y pruebas de caja negra basadas en el ERS, ejecutadas con scripts reproducibles.'))
A(B('**Etapas:** preparación del entorno y datos ficticios; análisis estático; pruebas funcionales vía API; seguridad de autenticación y autorización; seguridad dinámica; rendimiento; accesibilidad; consolidación de incidentes y matriz.'))
A(B('**Priorización:** P1 seguridad (autenticación, autorización, datos) y funciones núcleo (login, clientes, contratos); P2 rendimiento, accesibilidad y trazabilidad (auditoría); compatibilidad y disponibilidad quedan fuera del alcance de este ciclo (sección 1.2).'))
A(B('**Criterios de entrada:** código versionado, stack Docker operativo, datos de prueba ficticios cargados y casos revisados.'))
A(B('**Criterios de salida:** casos P1 y P2 ejecutados con evidencia, informando la cobertura de ejecución real; incidentes clasificados y trazados a su caso y requerimiento; matriz actualizada.'))
A(B('**Regresión:** la re-ejecución de los casos fallidos se diseña para después de corregir el código; no se ejecuta en este ciclo porque la corrección del sistema no forma parte del alcance.'))

A(H(2, '3.2 Tipos de prueba'))
A(P('Los tipos se clasifican por objetivo en **funcionales**, **no funcionales** (rendimiento, usabilidad, compatibilidad, disponibilidad) y de **seguridad**. Se indica su propósito, origen, impacto si falla y casos asociados.'))
A(TABLE([1450, 2500, 1300, 1800, 1200, 1496], [
    ['Tipo', 'Propósito y aplicación en Atlas', 'Origen', 'Impacto si falla', 'Casos', 'Ejecución'],
    ['Funcionales (caja negra, API y E2E)', 'Comprobar que cada función cumple lo especificado, sobre los endpoints REST y los flujos de login, clientes, contratos con documento y auditoría.', 'RF-1 a 6; RB-1 a 5', 'Datos corruptos o procesos de negocio rotos.', 'PT-FUNC-001, 002, 008, 010', 'Ejecutado: 4 de 4'],
    ['Integración', 'Verificar la comunicación entre frontend, API, base de datos y almacenamiento de documentos.', 'Arquitectura del ERS', 'Flujos completos rotos aunque cada módulo funcione.', 'PT-FUNC-001', 'Ejecutado'],
    ['Seguridad estática (SAST)', 'Detectar vulnerabilidades leyendo el código sin ejecutarlo (SonarQube, Semgrep, Gitleaks, Trivy).', 'NFR-SEG; OWASP', 'Defectos de diseño que otras pruebas no ven (credenciales en el código).', 'Transversal', 'Ejecutado: SonarQube, Trivy, Gitleaks, Semgrep'],
    ['Seguridad dinámica y de autorización (DAST)', 'Atacar la aplicación en ejecución: control de acceso por rol, aislamiento entre empresas y sesión JWT; ZAP baseline revisa cabeceras y CORS.', 'NFR-SEG-4, 5, 9; RB-2, 4', 'Acceso no autorizado a datos de otra empresa o suplantación de usuarios.', 'PT-SEG-002, 008, 009; ZAP', 'Ejecutado: 3 de 3'],
    ['Seguridad de datos y normativa', 'Verificar el hash de contraseñas y el cumplimiento técnico de la Ley 19.628.', 'NFR-SEG-2, 8', 'Fuga de credenciales y datos personales; responsabilidad legal.', 'PT-SEG-001', 'Ejecutado: 1 de 1'],
    ['Rendimiento (carga)', 'Medir tiempos de respuesta de las operaciones CRUD con k6.', 'NFR-PERF-1', 'Sistema lento en el uso diario.', 'PT-PERF-001', 'Ejecutado'],
    ['Usabilidad y accesibilidad', 'Evaluar si los adultos mayores pueden operar el sistema (WCAG 2.1 AA).', 'NFR-USAB-1; Ley 20.422', 'Exclusión de usuarios y errores de operación.', 'PT-USAB-001', 'Ejecutado con herramientas (sin usuarios reales)'],
    ['Compatibilidad', 'Verificar navegadores y dispositivos definidos.', 'NFR-COMPAT-1, 2', 'Funciones inutilizables en ciertos entornos.', 'Sin caso priorizado', 'No incluida (riesgo residual)'],
    ['Disponibilidad y recuperación', 'Comprobar reinicio ante caída, persistencia y respaldo restaurable.', 'NFR-DIS-1, 2; NFR-SEG-7', 'Indisponibilidad prolongada o pérdida de datos.', 'Sin caso priorizado', 'No incluida (riesgo residual)'],
    ['Regresión', 'Re-ejecutar los casos fallidos tras corregir el código.', 'ISO/IEC/IEEE 29119', 'Reaparición de defectos corregidos.', '—', 'Diseñada; se ejecuta tras corregir el código'],
    ['Aceptación', 'Validación con usuarios clave del negocio.', 'ERS §3.1.1', 'Sistema que cumple la especificación pero no la necesidad.', 'PT-USAB-001 (parcial)', 'Fuera de alcance salvo la parte con usuarios'],
], size=18, cap='Clasificación de los tipos de prueba por objetivo, origen e impacto'))
A(SPACER())
A(P('Por técnica, las pruebas funcionales, DAST, de rendimiento y de usabilidad son de **caja negra** (parten del ERS) y el análisis estático y la revisión de código son de **caja blanca**. '
    'Son **automatizadas** el cliente HTTP en Python, k6, ZAP, Lighthouse y SonarQube, y **manuales** la revisión de código y la inspección de la base de datos. '
    'Por nivel, se aplican pruebas de integración y de sistema; las unitarias no se aplican porque el código no las incluye (riesgo residual declarado en la sección 4.2).'))

A(H(2, '3.3 Criterios de aceptación'))
A(P('Un caso se aprueba solo si cumple todos sus criterios con evidencia (captura o log). Los criterios transversales son:'))
A(B('**Funcional:** el resultado coincide con el ERS (códigos HTTP, datos persistidos, registros de auditoría); el resultado esperado se deriva del ERS, no del comportamiento actual del código.'))
A(B('**No funcional:** p95 < 300 ms en CRUD simples; página principal < 2 s; error 5xx < 1 %; Lighthouse de accesibilidad ≥ 90 con 0 incidencias críticas o serias en axe.'))
A(B('**Seguridad:** 0 escrituras exitosas con rol editor; contraseñas con bcrypt (costo ≥ 10); 0 alertas de riesgo alto en ZAP; errores sin detalles internos.'))
A(B('**Reglas de negocio:** un contrato pertenece a un único cliente (RB-3); solo usuarios con relación en empresa_usuarios acceden a datos de la empresa (RB-2); el editor solo lee (RB-4).'))

A(H(2, '3.4 Herramientas utilizadas'))
A(TABLE([1900, 4146, 1800, 1900], [
    ['Herramienta', 'Fundamento de uso', 'Tipo de prueba', 'Estado'],
    ['SonarQube Community 26.10', 'SAST principal: vulnerabilidades, bugs y code smells en backend y frontend, con severidad independiente de la revisión manual.', 'Seguridad / mantenibilidad', 'Ejecutada'],
    ['Semgrep, Gitleaks y Trivy', 'Complementan a SonarQube: Semgrep aplica reglas de JavaScript y OWASP Top 10; Gitleaks busca secretos; Trivy revisa dependencias, Dockerfiles y la imagen del backend.', 'Seguridad (SAST / SCA)', 'Ejecutadas'],
    ['OWASP ZAP (baseline)', 'DAST pasivo: cabeceras, CORS y configuración del frontend y la API en ejecución.', 'Seguridad (DAST)', 'Ejecutada'],
    ['Cliente HTTP en Python (curl / OpenAPI)', 'Pruebas de API reproducibles sobre openapi.json, equivalentes a una colección Newman (§3.1.2 del ERS), con evidencia por caso.', 'Funcional / seguridad', 'Ejecutado'],
    ['k6', 'Pruebas de carga con umbrales (p95 < 300 ms, errores < 1 %) y con 200 usuarios concurrentes.', 'Rendimiento', 'Ejecutada'],
    ['Lighthouse y axe-core', 'Auditoría automatizada de accesibilidad y carga de las pantallas principales.', 'Usabilidad / rendimiento', 'Ejecutadas'],
    ['Docker y Docker Compose', 'Entorno reproducible y aislado entregado por la asignatura.', 'Todas', 'En uso'],
], cap='Herramientas de prueba, fundamento y estado'))
A(SPACER())

A(H(2, '3.5 Recursos y entorno de prueba'))
A(B('**Recursos humanos:** tres integrantes (Victor Silva, Jonathan Guerra y Darlette Morales) que comparten los roles de coordinación, ejecución funcional/API y seguridad/rendimiento.'))
A(B('**Recursos técnicos:** equipo Linux con Docker, Chrome y las herramientas de la sección 3.4. Limitación: no se reunieron adultos mayores, por lo que la usabilidad se mide solo con herramientas automáticas.'))
A(B('**Entorno:** stack Docker Compose de Atlas (frontend http://localhost:3350, API http://localhost:4450, Swagger en /docs, PostgreSQL en atlas-postgres), con usuarios semilla admin y editor y datos ficticios.'))

A(H(2, '3.6 Cronograma'))
A(TABLE([600, 5446, 2000, 1700], [
    ['N.º', 'Actividad', 'Estado', 'Momento'],
    ['1', 'Análisis del ERS, matriz de trazabilidad y diseño de los 10 casos priorizados.', 'Completada', 'Antes de la ejecución'],
    ['2', 'Revisión estática manual del código (19 hallazgos con archivo y línea).', 'Completada', 'Antes de la ejecución'],
    ['3', 'Análisis estático con SonarQube, Trivy y Gitleaks en Docker.', 'Completada (29-oct-2026)', 'Ejecución'],
    ['4', 'Ejecución de los casos funcionales y de seguridad sobre el stack Docker de Atlas.', 'Completada (29-oct-2026)', 'Ejecución'],
    ['5', 'Ejecución de los casos de rendimiento y usabilidad.', 'Completada (29-oct-2026)', 'Ejecución'],
    ['6', 'Consolidación de incidentes, matriz de trazabilidad y elaboración del informe.', 'Completada', 'Después de la ejecución'],
    ['7', 'Re-ejecución de los casos fallidos (regresión) tras corregir el código.', 'Pendiente (posterior a esta entrega)', 'Futuro'],
], cap='Cronograma de actividades'))
A(SPACER())

# =========================================================== 4. Casos
A(H(1, '4. Diseño de casos de prueba'))
A(H(2, '4.1 Casos de prueba priorizados'))
A(P('Se priorizaron **10 casos** por riesgo (probabilidad × impacto): cuatro funcionales (PT-FUNC-001, 002, 008 y 010), cuatro de seguridad (PT-SEG-001, 002, 008 y 009), uno de rendimiento (PT-PERF-001) y uno de usabilidad (PT-USAB-001). '
    'Verifican las funciones núcleo del negocio y los controles de seguridad de mayor impacto sobre los datos personales; el alcance de requerimientos, la cobertura y las brechas se analizan en la sección 4.2 y el Anexo A. '
    'Los resultados esperados se derivan del ERS y los datos son ficticios. En los comandos, $API equivale a http://localhost:4450.'))
A(CASE('PT-FUNC-001', 'Flujo completo de contrato con documento adjunto', 'RF-5.1, RF-5.2, RF-5.3, RB-3 (apoyo: RF-6.1)',
       'Funcional – extremo a extremo (API + base de datos)',
       'Verificar que un administrador crea un cliente y un contrato asociado a un único cliente, adjunta un documento en formato permitido, lo recupera íntegro, que la acción queda auditada y que los formatos o tamaños no permitidos son rechazados.',
       'Stack Atlas levantado con docker compose; token de administrador obtenido en POST /autenticacion/login; base de datos con datos semilla; archivos de prueba disponibles.',
       ['1. POST /clientes con el token de administrador y registrar el cliente_id.',
        '2. POST /contratos (multipart) con los datos del contrato y el archivo contrato.pdf; registrar el contrato_id.',
        '3. GET /contratos/{id}/file y comparar el hash sha256 con el del archivo original.',
        '4. POST /contratos con macro.exe y, por separado, con grande.pdf.',
        '5. Consultar la tabla documentos_contrato para verificar cómo se almacena el documento.',
        '6. GET /auditoria y buscar el registro de la creación del contrato.',
        '7. POST /contratos con un cliente_id inexistente.'],
       ['Paso 2: HTTP 201 y contrato asociado a un único cliente (RB-3).',
        'Paso 3: el archivo descargado es idéntico al subido (mismo hash).',
        'Paso 4: macro.exe rechazado con 4xx (el ERS admite solo PDF, DOC, PPT, JPG y PNG); el archivo excesivo rechazado con 400 o 413.',
        'Paso 5: el documento queda en el almacenamiento interno y la base de datos guarda solo la referencia (RF-5.3).',
        'Paso 6: existe un registro de auditoría de la creación y de la subida.',
        'Paso 7: error 4xx con mensaje controlado y sin contrato huérfano.'],
       ['☐ Contrato creado con respuesta 201 y asociado a un solo cliente.',
        '☐ Hash del archivo recuperado igual al del original.',
        '☐ Solo se aceptan los 5 formatos del ERS; .exe devuelve 4xx.',
        '☐ Existe y se aplica un límite de tamaño de archivo.',
        '☐ Subida y descarga completadas en ≤ 10 s.',
        '☐ Registro de auditoría presente por cada acción crítica.'],
       ['Cliente: nombre = "Cliente Prueba SpA", correo = "prueba@atlasfake.com".',
        'Contrato: título = "Servicios 2026", descripción = "Contrato de prueba", fecha_inicio = 2026-01-01, fecha_fin = 2026-12-31.',
        'Archivos: contrato.pdf (< 1 MB), foto.png, macro.exe (no permitido), grande.pdf (≈ 30 MB).']))
A(SPACER(200))

A(CASE('PT-FUNC-002', 'Autenticación y emisión de JWT', 'RF-1.1',
       'Funcional – API',
       'Verificar que un usuario registrado inicia sesión con su nombre de usuario y contraseña, que recibe un JWT con expiración y que las credenciales inválidas son rechazadas.',
       'Stack levantado; usuarios semilla admin y editor existentes.',
       ['1. POST /autenticacion/login con admin/admin y decodificar el payload del JWT.',
        '2. POST /autenticacion/login con una contraseña incorrecta.',
        '3. POST /autenticacion/login con un usuario inexistente.',
        '4. POST /autenticacion/login con el cuerpo vacío.'],
       ['Paso 1: HTTP 200 y un JWT con expiración (exp).',
        'Pasos 2 a 4: HTTP 401 con un mensaje genérico, sin indicar si el usuario existe.'],
       ['☐ El login válido responde 200 con un JWT.',
        '☐ El JWT incluye expiración (exp).',
        '☐ El 100 % de las credenciales inválidas se rechaza con 401.'],
       ['Credenciales válidas: admin/admin (usuario semilla ficticio).',
        'Credenciales inválidas: contraseña incorrecta, usuario inexistente y cuerpo vacío.']))
A(SPACER(200))

A(CASE('PT-FUNC-008', 'Listar, filtrar, editar y eliminar clientes', 'RF-4.2',
       'Funcional – API + base de datos',
       'Verificar que el administrador lista los clientes con paginación, los filtra por nombre, los edita y los elimina de forma lógica, conservando el registro para la trazabilidad.',
       'Stack levantado; token de administrador; al menos tres clientes de prueba.',
       ['1. GET /clientes?page=1&limit=2.',
        '2. GET /clientes/search?name=<texto> con parte del nombre de un cliente.',
        '3. PUT /clientes/{id} cambiando el nombre.',
        '4. DELETE /clientes/{id} y consultar la tabla clientes por ese id.'],
       ['Paso 1: devuelve como máximo 2 elementos.',
        'Paso 2: devuelve el cliente buscado.',
        'Paso 3: HTTP 200 con el dato actualizado.',
        'Paso 4: el registro permanece en la base de datos con una marca de baja (eliminación lógica).'],
       ['☐ El listado admite paginación (limit=2 devuelve ≤ 2 elementos).',
        '☐ El filtro por nombre devuelve el cliente buscado.',
        '☐ La edición responde 200.',
        '☐ Eliminación lógica: el registro sigue en la BD con marca de baja.'],
       ['Clientes ficticios "Lista n" con correo @atlasfake.com.',
        'Búsqueda por un fragmento del nombre.']))
A(SPACER(200))
A(CASE('PT-FUNC-010', 'Registro de auditoría de acciones críticas', 'RF-6.1 (apoyo: RB-2)',
       'Funcional – API + base de datos',
       'Verificar que las acciones críticas (crear, editar y eliminar clientes y contratos; subir y descargar documentos) quedan registradas con su usuario y detalle, y que la auditoría solo puede consultarse con autenticación.',
       'Stack levantado; token de administrador; cliente y contrato de prueba.',
       ['1. Crear y editar un cliente con POST y PUT /clientes.',
        '2. Crear un contrato con documento y eliminarlo con DELETE /contratos/{id}.',
        '3. Descargar el documento con GET /contratos/{id}/file.',
        '4. GET /auditoria con token y buscar un registro por cada acción.',
        '5. GET /auditoria sin token.'],
       ['Pasos 1 a 3: cada acción crea un registro con su usuario y detalle.',
        'Paso 5: HTTP 401; la auditoría no es pública.'],
       ['☐ Se audita: crear cliente.',
        '☐ Se audita: editar cliente.',
        '☐ Se audita: crear contrato / subir documento.',
        '☐ Se audita: descargar documento.',
        '☐ Se audita: eliminar contrato.',
        '☐ La auditoría solo es consultable con autenticación.'],
       ['Cliente ficticio "Cliente AUD" y un contrato con PDF.',
        'Consulta de auditoría con y sin encabezado Authorization.']))
A(SPACER(200))
A(CASE('PT-SEG-001', 'Hashing de contraseñas y política de contraseñas', 'NFR-SEG-2; restricción ERS §2.4',
       'Seguridad – confidencialidad (SAST + inspección de BD + API)',
       'Comprobar que las contraseñas se almacenan con hash bcrypt (con sal y costo adecuado), que el sistema impone la política de contraseñas del ERS y que el inicio de sesión funciona sin exponer el valor almacenado.',
       'Stack levantado; acceso al contenedor atlas-postgres; resultados de SonarQube disponibles; usuarios semilla admin y editor existentes.',
       ['1. SAST: buscar el uso de bcrypt o argon2 en el código del backend y en package.json.',
        '2. docker exec atlas-postgres psql -U postgres -d atlas -c "SELECT nombre_usuario, contrasena_hash FROM usuarios;".',
        '3. Registrar usuarios con POST /usuarios usando las tres contraseñas de prueba.',
        '4. Consultar de nuevo la base de datos para el usuario recién creado.',
        '5. Iniciar sesión con la contraseña correcta y con una incorrecta.'],
       ['Pasos 1, 2 y 4: dependencia y llamadas de hashing presentes; la columna tiene formato bcrypt ($2a$/$2b$/$2y$) con costo ≥ 10 y ninguna contraseña es legible.',
        'Paso 3: "abc" y "Atlas2026Segura" rechazadas por el backend (política: mínimo 12 caracteres con mayúscula, minúscula, número y símbolo); "Atlas#2026-Segura" aceptada.',
        'Paso 5: credencial correcta → 200 con token; incorrecta → 401 con mensaje genérico.'],
       ['☐ 100 % de los registros de usuarios tienen hash bcrypt con costo ≥ 10.',
        '☐ Dos usuarios con la misma contraseña producen hashes distintos (sal).',
        '☐ El backend rechaza las contraseñas que incumplen la política.',
        '☐ Ninguna respuesta ni log contiene la contraseña.'],
       ['Usuarios existentes: admin, editor.',
        'Contraseñas: débil = "abc"; sin símbolo = "Atlas2026Segura"; conforme = "Atlas#2026-Segura".',
        'Alta: {"nombre_usuario":"qa_hash","contrasena_hash":"<contraseña>","correo":"qa_hash@atlasfake.com"}.']))
A(SPACER(200))

A(CASE('PT-SEG-002', 'Control de acceso por rol en el backend (RBAC)', 'NFR-SEG-4, RF-3.2, RB-4, RB-5',
       'Seguridad – autorización (caja negra por API + inspección del token)',
       'Verificar que el backend, y no solo la interfaz, impide que el rol editor cree, modifique o elimine datos, y que el administrador conserva acceso completo.',
       'Stack levantado; tokens de admin (TOKEN_ADMIN) y editor (TOKEN_EDITOR) obtenidos; un cliente C1 y un contrato K1 creados por el administrador.',
       ['1. Decodificar el payload de ambos JWT y comprobar si incluyen el rol.',
        '2. Con TOKEN_EDITOR ejecutar: GET /clientes, POST /clientes, PUT /clientes/{C1}, DELETE /clientes/{C1}, POST /contratos, DELETE /contratos/{K1}, POST /empresa-usuarios y DELETE /usuarios/{id}.',
        '3. Repetir la lista con TOKEN_ADMIN.',
        '4. En el frontend, iniciar sesión como editor, cambiar localStorage.role a "administrador", recargar e intentar crear un cliente.'],
       ['Editor: GET → 200; todas las operaciones de escritura → 403 con cuerpo genérico.',
        'Administrador: lectura y escritura permitidas (2xx).',
        'Paso 4: aunque se altere el rol en el navegador, el servidor rechaza la operación.',
        'El token contiene el rol y el servidor lo valida (o lo consulta en empresa_usuarios).'],
       ['☐ 0 operaciones de escritura exitosas con rol editor (de 8 intentos).',
        '☐ 100 % de operaciones permitidas para el administrador.',
        '☐ La decisión de autorización se toma en el servidor.',
        '☐ Las respuestas 403 no revelan detalles internos.'],
       ['TOKEN_ADMIN (admin/admin) y TOKEN_EDITOR (editor/editor), usuarios semilla ficticios.',
        'Cliente C1 y contrato K1 creados por el administrador.',
        'Operaciones: GET/POST/PUT/DELETE de clientes, POST/DELETE de contratos, POST /empresa-usuarios, DELETE /usuarios/{id}.']))
A(SPACER(200))

A(CASE('PT-SEG-008', 'Sesión JWT: expiración, firma y secreto', 'NFR-SEG-9',
       'Seguridad – autenticación y sesión',
       'Verificar que la sesión basada en JWT usa un secreto robusto y no público, rechaza los tokens alterados o expirados y limita su tiempo de vida.',
       'Stack levantado con docker compose; acceso al contenedor atlas-backend para leer su variable JWT_SECRET.',
       ['1. docker exec atlas-backend env y leer JWT_SECRET.',
        '2. Firmar un token con el secreto por defecto del docker-compose y llamar a GET /clientes.',
        '3. Enviar un token con la firma alterada.',
        '4. Enviar un token con alg=none.',
        '5. Enviar un token expirado, firmado correctamente.',
        '6. Decodificar un token válido y calcular su tiempo de vida.'],
       ['Paso 1: secreto robusto, no un valor por defecto publicado.',
        'Pasos 2 a 5: HTTP 401 en todos los casos.',
        'Paso 6: tiempo de vida ≤ 2 h.'],
       ['☐ El secreto JWT es robusto y no es un valor por defecto público.',
        '☐ Un token firmado con el secreto por defecto es rechazado.',
        '☐ Un token con firma alterada es rechazado.',
        '☐ Un token con alg=none es rechazado.',
        '☐ Un token expirado es rechazado.',
        '☐ El tiempo de vida del token es acotado (≤ 2 h).'],
       ['Secreto por defecto del docker-compose: your-secret-key-change-in-production.',
        'Tokens forjados con datos ficticios del usuario semilla admin.']))
A(SPACER(200))
A(CASE('PT-SEG-009', 'Aislamiento entre empresas y acceso sin autenticación (IDOR)', 'RB-2 (apoyo: NFR-SEG-4)',
       'Seguridad – autorización (caja negra por API)',
       'Verificar que un usuario de una empresa no puede ver ni modificar clientes, contratos, archivos ni auditoría de otra empresa, y que los endpoints de contratos y archivos exigen autenticación.',
       'Stack levantado; empresas A y B con un administrador cada una; cliente y contrato con PDF creados en la empresa A.',
       ['1. Con el token de B: GET y PUT /clientes/{cliente de A}.',
        '2. Con el token de B: GET /contratos/{contrato de A} y GET /contratos/{id}/file.',
        '3. Con el token de B: GET /auditoria y POST /contratos para el cliente de A.',
        '4. Sin token: GET /contratos/{id}, GET /contratos/{id}/file y POST /contratos.'],
       ['Pasos 1 a 3: HTTP 403 o 404; ninguna lectura ni escritura sobre datos de A, y la auditoría solo muestra acciones de B.',
        'Paso 4: HTTP 401 en las tres peticiones.'],
       ['☐ 0 recursos de otra empresa accesibles o modificables, con token de otra empresa o sin token (de 9 intentos).'],
       ['Empresa A: cliente y contrato "Contrato base" con un PDF.',
        'Empresa B: administrador creado para la prueba; todos los datos son ficticios.']))
A(SPACER(200))
A(CASE('PT-PERF-001', 'Tiempo de respuesta de operaciones CRUD', 'NFR-PERF-1 (apoyo: NFR-USAB-2)',
       'Rendimiento – carga',
       'Medir la latencia de las operaciones CRUD simples bajo carga normal y compararla con el umbral del ERS (< 300 ms).',
       'Stack levantado; base de datos con datos semilla más 1.000 clientes generados; k6 instalado; un token por usuario virtual.',
       ['1. Poblar la base de datos de prueba y obtener un token por usuario virtual.',
        '2. Ejecutar k6 con umbrales http_req_duration p(95) < 300 y http_req_failed < 1 % (script 03-Anexos/Herramientas/k6/crud_latencia.js).',
        '3. Registrar promedio, p(95), p(99) y tasa de error por endpoint.',
        '4. Repetir POST /autenticacion/login 30 veces y medir la latencia.'],
       ['p(95) < 300 ms en cada endpoint CRUD simple.',
        'Tasa de errores < 1 %.',
        'El login también cumple el umbral, por ser una operación simple del ERS.'],
       ['☐ p(95) < 300 ms para todos los endpoints CRUD simples.',
        '☐ Errores 5xx < 1 %.',
        '☐ El login cumple el mismo umbral.'],
       ['Carga normal: 20 usuarios virtuales durante 2 minutos, con tiempo de pensar de 1 s.',
        'Endpoints: GET /clientes, GET /clientes/{id}, POST /clientes, PUT /clientes/{id}, DELETE /clientes/{id}, GET /contratos y POST /autenticacion/login.',
        'El entorno es local: las cifras se reportan con las características del equipo y no se extrapolan a producción.']))
A(SPACER(200))

A(CASE('PT-USAB-001', 'Accesibilidad para adultos mayores (WCAG 2.1 AA)', 'NFR-USAB-1; criterio ERS §3.1.1',
       'Usabilidad / accesibilidad',
       'Evaluar si el login, el registro y las pantallas principales son legibles y operables por adultos mayores, con criterios WCAG 2.1 nivel AA.',
       'Frontend disponible en http://localhost:3350; Lighthouse y axe DevTools instalados; usuario de prueba creado; participantes mayores de 60 años si es posible.',
       ['1. Ejecutar Lighthouse (categoría Accesibilidad) y axe en cada URL.',
        '2. Navegar solo con teclado (Tab, Shift+Tab, Enter, Esc) verificando foco visible y ausencia de trampas.',
        '3. Medir contraste y tamaño de fuente base; ampliar el zoom al 200 %.',
        '4. Pedir a los participantes iniciar sesión, crear un cliente y ubicar su contrato; registrar tiempo, errores y ayudas; aplicar el cuestionario SUS.'],
       ['Puntaje de accesibilidad en Lighthouse ≥ 90.',
        '0 incidencias críticas o serias en axe.',
        'Contraste ≥ 4,5:1 y tarea completada sin bloqueos mayores.'],
       ['☐ Lighthouse Accesibilidad ≥ 90 en las 5 URLs.',
        '☐ 0 incidencias critical/serious en axe.',
        '☐ Contraste de texto ≥ 4,5:1 y fuente base ≥ 12 px (mínimo del ERS).',
        '☐ Objetivos táctiles ≥ 44×44 px y campos con label o ARIA.',
        '☐ SUS promedio ≥ 70 y sin bloqueos mayores.'],
       ['URLs: /login, /registro, /home, /clientes, /contratos.',
        'Participantes: hasta 5 adultos mayores; como puede no ser factible conseguirlos, la alternativa es 1 o 2 participantes más revisión heurística, y la limitación se documenta.',
        'Tareas: iniciar sesión; crear un cliente; ubicar el contrato de ese cliente.']))
A(SPACER(200))


# ---------------------------------------------------------- 4.2 Cobertura
CATS = [('Funcionales (RF-1.1 a RF-6.1)', lambda r: r.startswith('RF-')), ('Seguridad (NFR-SEG-1 a 9)', lambda r: r.startswith('NFR-SEG')),
        ('Rendimiento (NFR-PERF-1 a 3)', lambda r: r.startswith('NFR-PERF')), ('Usabilidad (NFR-USAB-1 a 4)', lambda r: r.startswith('NFR-USAB')),
        ('Disponibilidad (NFR-DIS-1 y 2)', lambda r: r.startswith('NFR-DIS')), ('Compatibilidad (NFR-COMPAT-1 y 2)', lambda r: r.startswith('NFR-COMPAT')),
        ('Reglas de negocio (RB-1 a 5)', lambda r: r.startswith('RB-'))]
crow = []
tot_req = tot_cub = 0
for nombre, f in CATS:
    filas = [m for m in MAT if f(m[0])]
    cub = [m for m in filas if m in COVM]
    casos = sorted({k for m in cub for k in KEEP if k in m[1]})
    tot_req += len(filas)
    tot_cub += len(cub)
    crow.append([nombre, str(len(filas)), str(len(cub)), f'{len(cub)} (100 %)' if cub else '—', ', '.join(c.replace('PT-', '') for c in casos) or 'Fuera del alcance'])
crow.append([{'t': 'Total ERS', 'bold': True}, {'t': str(tot_req), 'bold': True}, {'t': str(tot_cub), 'bold': True}, {'t': f'{tot_cub} (100 %)', 'bold': True}, {'t': f'{len(KEEP)} casos', 'bold': True}])
assert tot_cub == ALC_N
A(H(2, '4.2 Análisis de cobertura, pertinencia y coherencia del plan'))
A(P('**Cobertura.** Se mide de dos formas: de **diseño** (requerimientos del alcance con al menos un caso ÷ requerimientos del alcance) y de **ejecución** (casos ejecutados ÷ casos priorizados). '
    f'El ERS define {tot_req} requerimientos; el alcance de este ciclo se acotó por riesgo a {tot_cub} de ellos (sección 1.2), de modo que la cobertura de diseño del alcance es del **100 %** ({tot_cub} de {tot_cub}). '
    f'Frente al ERS completo equivale a {tot_cub / tot_req * 100:.0f} %; los {tot_req - tot_cub} requerimientos restantes no se verificaron y no pueden darse por cumplidos.', keep_next=True))
A(TABLE([2600, 1100, 1100, 1300, 3646], [['Categoría del ERS', 'En el ERS', 'En el alcance', 'Con ≥ 1 caso', 'Casos que la verifican']] + crow,
        cap='Cobertura de diseño por categoría de requerimientos'))
A(SPACER())
A(P('Los diez casos verifican con evidencia ejecutada las cuatro reglas de negocio de mayor riesgo (RB-2 a RB-5), la autenticación y la sesión JWT, el flujo de contratos con documento, la gestión de clientes, la auditoría, el hash de contraseñas, el control de acceso por rol, el rendimiento CRUD y la accesibilidad. '
    'Los requerimientos de menor probabilidad o impacto (compatibilidad, disponibilidad, ayuda contextual, TLS y cifrado en reposo, entre otros) quedan fuera del alcance; en los de seguridad se apoyan en el análisis estático (sección 5.4).'))
A(P('**Cobertura frente a estándares.**', keep_next=True, after=40))
A(TABLE([3100, 2700, 3946], [
    ['Estándar', 'Cubierto por', 'Observación'],
    ['ISO/IEC 25010: idoneidad funcional, eficiencia, usabilidad y seguridad', 'PT-FUNC-001, 002, 008, 010; PT-PERF-001; PT-USAB-001; PT-SEG-001, 002, 008, 009', 'Cobertura parcial: una muestra de los requerimientos de mayor riesgo.'],
    ['ISO/IEC 25010: compatibilidad, fiabilidad, mantenibilidad y portabilidad', 'Análisis estático (mantenibilidad)', 'Sin caso de prueba: fuera del alcance.'],
    ['OWASP A01 (control de acceso), A02 (fallas criptográficas), A07 (autenticación) y A09 (registro)', 'PT-SEG-002, 009; PT-SEG-001; PT-FUNC-002, PT-SEG-008; PT-FUNC-010', 'Cobertura directa.'],
    ['OWASP A03, A05 y A06', 'SonarQube, ZAP baseline y Trivy', 'Solo por herramienta, sin caso dirigido.'],
    ['OWASP A04, A08 y A10', 'PT-FUNC-001 (A04, parcial)', 'A08 y A10 sin cobertura.'],
    ['WCAG 2.1 AA', 'PT-USAB-001', 'Medición automatizada (Lighthouse y axe); no incluye evaluación con usuarios.'],
], size=18, cap='Cobertura frente a ISO/IEC 25010, OWASP Top 10 y WCAG'))
A(SPACER())
A(P('En el marco legal, la Ley 19.628 (art. 11) se verifica con PT-SEG-001, 002, 008 y 009; la Ley 20.422, con PT-USAB-001; la Ley 21.719 se usa como referencia prospectiva; y la Ley 21.459 es una restricción transversal. '
    'El criterio de salida "cobertura de código ≥ 80 %" no es aplicable: SonarQube mide 0,0 % porque el repositorio no tiene pruebas automatizadas.'))
A(P('**Pertinencia.** Los casos se asignan por riesgo (probabilidad × impacto), con la probabilidad respaldada por la revisión estática (hallazgos H-xx de la sección 5.4).', keep_next=True))
A(TABLE([2400, 750, 900, 2800, 1850, 1046], [
    ['Riesgo', 'Prob.', 'Impacto', 'Evidencia que sustenta la probabilidad', 'Pruebas asignadas', 'Prioridad'],
    ['Fuga de credenciales', 'Alta', 'Crítico', 'Contraseñas sin hash (H-01); sin política de contraseñas (H-15); secreto JWT por defecto (H-03)', 'PT-SEG-001, 008; PT-FUNC-002', 'P1'],
    ['Acceso a datos de otra empresa o escalada de rol', 'Alta', 'Crítico', 'Sin control de rol (H-02); endpoints sin verificación de pertenencia (H-12, H-17, H-19)', 'PT-SEG-002, 009', 'P1'],
    ['Documentos contractuales inseguros', 'Media', 'Alto', 'Carga de archivos sin filtro ni límite (H-08)', 'PT-FUNC-001', 'P1'],
    ['Operaciones lentas', 'Alta', 'Medio', 'Latencia de 4 s en login (H-05)', 'PT-PERF-001', 'P2'],
    ['Pérdida de trazabilidad', 'Media', 'Alto', 'Eliminación física (H-06); auditoría expuesta (H-19)', 'PT-FUNC-008, 010', 'P2'],
    ['Exclusión de adultos mayores', 'Media', 'Medio', 'Requisito explícito NFR-USAB-1', 'PT-USAB-001', 'P2'],
    ['Datos en tránsito o reposo sin protección; fallas de disponibilidad o compatibilidad', 'Media', 'Alto', 'Sin TLS (H-09); sin cifrado en reposo (H-13)', 'Sin caso; análisis estático', 'Fuera del alcance'],
], size=18, cap='Pertinencia: riesgos, evidencia y pruebas asignadas'))
A(SPACER())
A(P('**Coherencia y brechas.** Todo caso apunta a requerimientos existentes del ERS, los resultados esperados se derivan de su texto y los casos usan las rutas reales del backend; las herramientas se acotaron a las ejecutables en el entorno local. '
    'El criterio de salida "sin defectos críticos abiertos" no se cumple por los hallazgos de autorización, lo que es un resultado válido y no una incoherencia. '
    'Brechas declaradas (fuera del alcance): compatibilidad, disponibilidad, TLS, cifrado en reposo, enlace compartido y la mayor parte de usabilidad; no se reunieron adultos mayores, por lo que la usabilidad se midió solo con herramientas automáticas; '
    'las pruebas de carga son locales y no extrapolables; y el sistema no tiene pruebas unitarias.'))
A(P(f'**Conclusión.** El alcance es pertinente al riesgo y coherente: los {tot_cub} requerimientos del alcance tienen caso (100 %) y los diez casos se ejecutaron (100 % de cobertura de ejecución). '
    f'Los {tot_req - tot_cub} requerimientos restantes del ERS quedan como riesgo residual en la sección 5.'))
# =========================================================== 5. Ejecución
EJ = REPO / '06-Evidencias' / 'ejecucion'
RES = json.load(open(EJ / 'resultados_ejecucion.json', encoding='utf-8'))
CASOS = list(KEEP)
n_apr = sum(1 for k in CASOS if RES[k]['veredicto'] == 'Aprobado')
n_fal = sum(1 for k in CASOS if RES[k]['veredicto'] == 'Fallido')
n_noe = sum(1 for k in CASOS if RES[k]['veredicto'] == 'No ejecutado')
n_eje = n_apr + n_fal
crit_ok = sum(1 for k in CASOS for c in RES[k]['criterios'] if c['cumple'] is True)
crit_tot = sum(1 for k in CASOS for c in RES[k]['criterios'] if c['cumple'] is not None)
COB = RES['_cobertura_endpoints']

import collections
TR = {}
for nm in ('trivy_fs', 'trivy_image_backend'):
    pth = REPO / f'06-Evidencias/estatico/herramientas/{nm}.json'
    c = collections.Counter()
    mis = collections.Counter()
    if pth.exists():
        for r in json.load(open(pth, encoding='utf-8')).get('Results', []):
            for v in r.get('Vulnerabilities') or []:
                c[v['Severity']] += 1
            for m in r.get('Misconfigurations') or []:
                mis[m['Severity']] += 1
    TR[nm] = (c, mis)
GL = len(json.load(open(REPO / '06-Evidencias/estatico/herramientas/gitleaks.json', encoding='utf-8')))
SG = len(json.load(open(REPO / '06-Evidencias/estatico/herramientas/semgrep.json', encoding='utf-8'))['results'])

A(H(1, '5. Ejecución de pruebas'))
A(P('Las pruebas se ejecutaron el 29 de octubre de 2026 sobre el stack Docker Compose de Atlas (postgres:15-alpine, backend Node 18 y frontend nginx) en un equipo Linux Mint 22.3, con Chrome 156, k6 2.3.0, OWASP ZAP (imagen stable), '
    'SonarQube 26.10 y Lighthouse/axe. Se usaron datos ficticios y solo el entorno local. Solo se informa lo ejecutado; cada resultado tiene su archivo de evidencia en 06-Evidencias/ejecucion/.'))
A(H(2, '5.1 Resumen de ejecución'))
A(TABLE([6200, 3546], [
    ['Métrica', 'Valor'],
    ['Casos de prueba priorizados', str(len(KEEP))],
    ['Casos ejecutados', f'{n_eje} ({n_eje / len(KEEP) * 100:.0f} % de cobertura de ejecución)'],
    ['Aprobados', str(n_apr)],
    ['Fallidos', str(n_fal)],
    ['Bloqueados', '0'],
    ['Criterios de aceptación verificados', f'{crit_ok} cumplidos de {crit_tot} evaluados'],
    ['Análisis estático', f'SonarQube: 4 vulnerabilidades (1 Blocker), 25 bugs, 9 code smells · Trivy: {TR["trivy_fs"][0].get("HIGH", 0)} vulnerabilidades altas en dependencias y {TR["trivy_image_backend"][0].get("CRITICAL", 0)} críticas y {TR["trivy_image_backend"][0].get("HIGH", 0)} altas en la imagen del backend · Gitleaks: {GL} secretos · Semgrep: {SG} hallazgos · ZAP baseline: 0 alertas altas y 5 medias'],
    ['Incidentes identificados', '12: 4 críticos · 4 graves · 3 moderados · 1 leve'],
], cap='Resumen de ejecución'))
A(SPACER())
A(H(2, '5.2 Detalle de ejecución de casos'))
DESC = {
    'PT-FUNC-001': 'Contrato y descarga correctos (hash idéntico); se aceptan un .exe y un archivo de 30 MB; el documento se guarda en la BD; cliente inexistente → 500 con err.message.',
    'PT-FUNC-002': 'Login válido → 200 con JWT (exp 2 h); credenciales inválidas → 401. Latencia de 4 s.',
    'PT-FUNC-003': 'No existen logout ni refresh (404); el token sigue válido hasta su expiración.',
    'PT-FUNC-004': 'Correo duplicado rechazado por la restricción UNIQUE de la BD (0 duplicados); responde 500.',
    'PT-FUNC-005': 'Empresa y usuario creados; el primer usuario recibe rol administrador (rol_id 1).',
    'PT-FUNC-006': 'Alta con roles 1 y 2, edición y baja correctas y auditadas.',
    'PT-FUNC-007': '0 de 4 entradas inválidas rechazadas (correo, teléfono, RUT, nombre vacío): se persisten.',
    'PT-FUNC-008': 'Edición y filtro correctos; sin paginación (devuelve todos los clientes); eliminación física.',
    'PT-FUNC-009': 'Estado por fechas correcto; el enlace compartido (RF-5.5) no existe.',
    'PT-FUNC-010': 'Crear, editar y eliminar se auditan; las descargas no; GET /auditoria sin token entrega todos los registros.',
    'PT-FUNC-011': f'{COB["cubiertos"]} de {COB["total"]} endpoints ejercitados ({COB["pct"]:.0f} %).',
    'PT-SEG-001': 'Contraseñas en texto plano en la BD; sin bcrypt; "abc" y contraseñas sin símbolo aceptadas.',
    'PT-SEG-002': 'El token no incluye rol; el editor ejecutó 6 de 7 escrituras, incluida la creación de un usuario administrador.',
    'PT-SEG-003': 'Solo HTTP en el puerto 80; sin TLS en el frontend ni en la API.',
    'PT-SEG-004': 'El número de cuenta bancaria se almacena y lee en texto plano.',
    'PT-SEG-005': 'SQL Injection y login protegidos; sin saneo de XSS, sin cabeceras de seguridad, CORS abierto y sin límite de intentos; ZAP: 0 alertas altas y 5 medias.',
    'PT-SEG-006': '3 de 5 respuestas de error exponen mensajes internos (SQL).',
    'PT-SEG-007': 'Credenciales por defecto en código y docker-compose; sin consentimiento ni política de privacidad; descarga sin autenticación.',
    'PT-SEG-008': 'Un token firmado con el secreto por defecto es aceptado; firma alterada, alg=none y expirado se rechazan.',
    'PT-SEG-009': 'Contratos y archivos de otra empresa accesibles (también sin token) y creación de contratos sin autenticación; los clientes sí están aislados.',
    'PT-PERF-001': 'POST, PUT y DELETE p95 entre 18 y 31 ms; GET /clientes y login p95 ≈ 4,0 s (umbral 300 ms).',
    'PT-PERF-002': 'LCP móvil de 1,68 s en /login y 2,79 s en /home (umbral 2 s).',
    'PT-PERF-003': f'200 usuarios concurrentes durante 5 min: 0 % de fallos HTTP y servicio estable.',
    'PT-PERF-004': 'PDF de 5 MB: subida y descarga máximas de 40 y 62 ms (umbral 10 s).',
    'PT-USAB-001': 'Lighthouse 89 a 96; 49 nodos críticos o serios en axe (botones sin nombre, contraste); 96 de 119 objetivos < 44 px.',
    'PT-USAB-002': 'No ejecutado: requiere tareas con usuarios.',
    'PT-USAB-003': 'No ejecutado: requiere evaluación con usuarios.',
    'PT-COMP-001': 'Sin scroll horizontal, pero contenido recortado en 12 de 28 combinaciones y menú fijo de 239 px en móvil.',
    'PT-COMP-002': 'No ejecutado: solo Chrome disponible; Safari no existe en Linux.',
    'PT-DIS-001': 'Datos persistentes y respaldo restaurable (conteos idénticos); sin política de respaldo; docker kill no activa el reinicio (detención manual).',
}
TIPO = {'FUNC': 'Funcional', 'SEG': 'Seguridad', 'PERF': 'Rendimiento', 'USAB': 'Usabilidad', 'COMP': 'Compatibilidad', 'DIS': 'Disponibilidad'}
rows = [['CASO', 'DESCRIPCIÓN DEL RESULTADO', 'RESULTADO', 'EVIDENCIA', 'TIPO']]
for k in CASOS:
    r = RES[k]
    ev = r['evidencia'].split('/')[-1] if r['evidencia'] != '—' else '—'
    rows.append([k, DESC[k], r['veredicto'], ev, TIPO[k.split('-')[1]]])
A(TABLE([1150, 3800, 1300, 2246, 1250], rows, size=17, cap='Detalle de ejecución por caso (29 de octubre de 2026, Docker local)'))
A(SPACER())

A(H(2, '5.3 Criticidad de incidentes'))
A(TABLE([1500, 3900, 2500, 1846], [
    ['CASO', 'DESCRIPCIÓN', 'IMPACTO', 'EVIDENCIA'],
    [{'t': 'CRÍTICO', 'fill': SEV['CRÍTICO'], 'bold': True}, 'Compromete confidencialidad, integridad o autenticación de datos personales, o impide una función esencial; explotable con privilegios mínimos. Ej.: contraseñas sin hash, escritura sin control de rol.', 'Muy alto: el sistema no es seguro de usar', 'Remediación inmediata; bloquea la liberación'],
    [{'t': 'GRAVE', 'fill': SEV['GRAVE'], 'bold': True}, 'Incumple un requerimiento esencial del ERS o expone un vector de ataque relevante, pero el sistema funciona parcialmente. Ej.: sin cierre de sesión, auditoría pública.', 'Alto: afecta áreas principales del usuario', 'Corregir con urgencia, antes de liberar'],
    [{'t': 'MODERADO', 'fill': SEV['MODERADO'], 'bold': True}, 'Debilita una defensa o degrada la calidad sin ruptura inmediata. Ej.: CORS abierto, sin política de contraseñas.', 'Medio: el usuario puede trabajar con limitaciones', 'Próxima iteración'],
    [{'t': 'LEVE', 'fill': SEV['LEVE'], 'bold': True}, 'Desviación menor o de buenas prácticas que no afecta la funcionalidad. Ej.: divulgación de la versión del framework.', 'Bajo: no impacta la operación', 'Según disponibilidad'],
], cap='Escala de criticidad de incidentes'))
A(SPACER())
INC = [
    ('PT-SEG-002 (INC-01)', 'Sin control de rol en el backend: el editor ejecuta 6 de 7 escrituras y crea un usuario administrador (escalada de privilegios). Viola NFR-SEG-4, RF-3.2, RB-4.', 'CRÍTICO', 'Seguridad'),
    ('PT-SEG-001 (INC-02)', 'Contraseñas en texto plano en la base de datos, sin bcrypt ni política de contraseñas. Viola NFR-SEG-2.', 'CRÍTICO', 'Seguridad'),
    ('PT-SEG-009 (INC-03)', 'Contratos y archivos de otra empresa accesibles, incluso sin token, y contratos creables sin autenticación. Viola RB-2.', 'CRÍTICO', 'Seguridad'),
    ('PT-SEG-008 (INC-04)', 'El secreto JWT por defecto del docker-compose permite forjar tokens válidos y suplantar a cualquier usuario; la firma alterada, alg=none y el token expirado sí se rechazan. Viola NFR-SEG-9.', 'CRÍTICO', 'Seguridad'),
    ('PT-FUNC-010 (INC-05)', 'GET /auditoria sin autenticación entrega los registros de todas las empresas; las descargas de documentos no se auditan. Viola RF-6.1.', 'GRAVE', 'Funcional / seguridad'),
    ('PT-FUNC-001 (INC-06)', 'Se aceptan archivos .exe y de 30 MB, y el documento se guarda en la BD. Viola RF-5.2 y RF-5.3.', 'GRAVE', 'Funcional'),
    ('PT-PERF-001 (INC-07)', 'GET /clientes y el login tienen p95 de 4,0 s frente al umbral de 300 ms (retardo artificial en el código). Viola NFR-PERF-1.', 'GRAVE', 'Rendimiento'),
    ('SAST (INC-08)', 'Credencial de base de datos por defecto en db.js:6 (SonarQube Blocker) y en el docker-compose. Viola NFR-SEG-8.', 'GRAVE', 'Análisis estático'),
    ('PT-FUNC-008 (INC-09)', 'Sin paginación y eliminación física de clientes. Viola RF-4.2.', 'MODERADO', 'Funcional'),
    ('PT-USAB-001 (INC-10)', 'Accesibilidad insuficiente: Lighthouse 89 en /clientes y /contratos, botones sin nombre y contraste bajo. Viola NFR-USAB-1.', 'MODERADO', 'Usabilidad'),
    ('SAST (INC-11)', '25 bugs de confiabilidad (promesas sin manejo de errores en el frontend) y 10 vulnerabilidades altas en dependencias (p. ej. multer 1.x).', 'MODERADO', 'Análisis estático'),
    ('SAST (INC-12)', 'El framework expone su versión (X-Powered-By: Express).', 'LEVE', 'Análisis estático'),
]
rows = [['CASO', 'DESCRIPCIÓN', 'RESULTADO', 'IMPACTO', 'TIPO DE PRUEBA']]
for c, d, i, t in INC:
    rows.append([c, d, 'Fallido', {'t': i, 'fill': SEV[i], 'bold': True}, t])
A(TABLE([1450, 3500, 1500, 1350, 1946], rows, size=18, cap='Incidentes identificados y su criticidad'))
A(SPACER())

A(H(2, '5.4 Análisis estático del código'))
A(P('Se ejecutaron SonarQube Community 26.10 y Semgrep (SAST), Gitleaks (secretos) y Trivy (dependencias, configuración e imagen) en Docker, más una revisión manual del código. SonarQube analizó una copia del código con las dependencias instaladas, sin modificar el original (Anexo B). '
    'Un resultado de cero hotspots no significa ausencia de vulnerabilidades: la edición Community no hace análisis de flujo, por lo que los defectos de autorización se detectaron con los casos dinámicos.'))
fs_c, fs_m = TR['trivy_fs']
im_c, _ = TR['trivy_image_backend']
A(TABLE([3000, 6746], [
    ['Herramienta', 'Resultado'],
    ['SonarQube (6.955 líneas)', '4 vulnerabilidades (1 Blocker: credencial en db.js:6), 25 bugs, 9 code smells, 16,4 % de duplicación, 0 % de cobertura; Quality Gate OK'],
    ['Trivy: dependencias y Dockerfiles', f'{fs_c.get("HIGH", 0)} vulnerabilidades altas en BACKEND/package-lock.json (multer 1.4.5) y {fs_m.get("HIGH", 0)} configuraciones de riesgo alto en los Dockerfiles'],
    ['Trivy: imagen del backend (node:18-alpine)', f'{im_c.get("CRITICAL", 0)} vulnerabilidades críticas y {im_c.get("HIGH", 0)} altas (imagen base sin soporte)'],
    ['Gitleaks', f'{GL} secretos detectados (la credencial de db.js la identifica SonarQube, no Gitleaks)'],
    ['Semgrep (115 reglas: javascript y owasp-top-ten)', f'{SG} hallazgos: ambos Dockerfiles ejecutan el contenedor como root (regla missing-user)'],
], cap='Resultados del análisis estático'))
A(SPACER())
A(P('La revisión manual produjo 19 hallazgos con archivo y línea (4 críticos, 9 graves y 6 moderados). Los de los casos priorizados se confirman en la sección 5.2; los demás cuentan con evidencia complementaria en 06-Evidencias/ejecucion/. Además, OWASP ZAP baseline (frontend y API) reportó 0 alertas altas y 5 medias (sin Content Security Policy, sin cabecera anti-clickjacking, sin Subresource Integrity y configuración CORS abierta).', keep_next=True))
H19 = [
    ('H-01', 'Contraseñas sin hash (auth.js:26; datos semilla en texto plano)', 'NFR-SEG-2', 'CRÍTICO', 'Confirmado: PT-SEG-001'),
    ('H-02', 'Sin control de rol en el backend (token sin rol)', 'NFR-SEG-4, RB-4', 'CRÍTICO', 'Confirmado: PT-SEG-002'),
    ('H-12', 'POST /contratos sin autenticación ni verificación de empresa (IDOR)', 'RB-2, RB-3', 'CRÍTICO', 'Confirmado: PT-SEG-009'),
    ('H-17', 'Descarga de documentos sin autenticación (GET /contratos/:id/file)', 'RB-2, NFR-SEG-4', 'CRÍTICO', 'Confirmado: PT-SEG-009'),
    ('H-03', 'Secreto JWT por defecto en el código y el docker-compose', 'NFR-SEG-9', 'GRAVE', 'Confirmado: PT-SEG-008'),
    ('H-04', 'Sin cierre de sesión ni revocación de tokens', 'RF-1.2', 'GRAVE', 'Confirmado: PT-FUNC-003'),
    ('H-05', 'Latencia artificial de 4 s en login y GET /contratos', 'NFR-PERF-1', 'GRAVE', 'Confirmado: PT-PERF-001'),
    ('H-08', 'Carga de archivos sin filtro ni límite; documento guardado en la BD', 'RF-5.2, RF-5.3', 'GRAVE', 'Confirmado: PT-FUNC-001; SonarQube'),
    ('H-09', 'Sin TLS: nginx en puerto 80 y API por http', 'NFR-SEG-1', 'GRAVE', 'Confirmado: PT-SEG-003'),
    ('H-11', 'Credenciales por defecto en código y docker-compose', 'NFR-SEG-8', 'GRAVE', 'Confirmado: SonarQube; PT-SEG-007'),
    ('H-13', 'Datos bancarios sin cifrar en reposo', 'NFR-SEG-3', 'GRAVE', 'Confirmado: PT-SEG-004'),
    ('H-18', 'RF-5.5 (enlace compartido) no implementado', 'RF-5.5', 'GRAVE', 'Confirmado: PT-FUNC-009'),
    ('H-19', 'Auditoría expuesta sin autenticación y manipulable', 'RF-6.1, RB-2', 'GRAVE', 'Confirmado: PT-FUNC-010'),
    ('H-06', 'Eliminación física en lugar de lógica', 'RF-4.2', 'MODERADO', 'Confirmado: PT-FUNC-008'),
    ('H-07', 'Errores 500 devuelven err.message', 'NFR-SEG-6', 'MODERADO', 'Confirmado: PT-SEG-006'),
    ('H-10', 'CORS abierto, sin helmet ni límite de intentos de login', 'NFR-SEG-5', 'MODERADO', 'Confirmado: PT-SEG-005; SonarQube'),
    ('H-14', 'Imagen node:18 sin soporte, contenedor como root, multer 1.x', 'NFR-SEG-5', 'MODERADO', 'Confirmado: Trivy'),
    ('H-15', 'Sin política de contraseñas en el backend', '§2.4 ERS', 'MODERADO', 'Confirmado: PT-SEG-001'),
    ('H-16', 'Token JWT guardado en localStorage', 'NFR-SEG-9', 'MODERADO', 'Confirmado: código y pruebas de interfaz'),
]
def _est(e):
    ok = [x for x in re.findall(r'PT-[A-Z]+-\d+', e) if x in KEEP]
    resto = [p.strip() for p in e.replace('Confirmado:', '').split(';') if p.strip() and not p.strip().startswith('PT-')]
    partes = ok + resto
    return 'Confirmado: ' + '; '.join(partes) if partes else 'Confirmado en prueba complementaria'


H19 = [(i, d, r, s, _est(e)) for i, d, r, s, e in H19]
rows = [['ID', 'Hallazgo', 'Requerimiento', 'Criticidad', 'Estado']]
for i, d, r, s, e in H19:
    rows.append([i, d, r, {'t': s, 'fill': SEV[s], 'bold': True}, e])
A(TABLE([700, 3500, 1500, 1400, 2646], rows, size=18, cap='Hallazgos de la revisión estática manual contrastados con la ejecución'))
A(SPACER())

# =========================================================== 6. Ético-normativo
A(H(1, '6. Análisis ético y normativo de los resultados'))
A(H(2, '6.1 Resultados frente a la normativa'))
A(TABLE([2400, 1700, 2600, 3046], [
    ['Resultado', 'Requerimiento', 'Norma o principio comprometido', 'Lectura'],
    ['INC-01 y INC-04: el editor escribe y crea administradores; un token forjado suplanta a cualquiera', 'NFR-SEG-4, 9; RB-4', 'Ley 19.628 art. 11; OWASP A01 y A07', 'Cualquier persona con el secreto del compose puede operar como administrador y alterar datos de clientes de las pymes.'],
    ['INC-02: contraseñas en texto plano', 'NFR-SEG-2', 'Ley 19.628 art. 11; Ley 21.719 (seguridad)', 'Un acceso a la base de datos expone credenciales reutilizables de los usuarios.'],
    ['INC-03 y INC-05: contratos, archivos y auditoría accesibles sin control', 'RB-2; RF-6.1', 'Ley 19.628 art. 11; OWASP A01 y A09', 'Los documentos contractuales de una empresa pueden ser leídos por otra o por un anónimo; sin trazabilidad de descargas.'],
    ['INC-08: credenciales por defecto en el código y en el compose', 'NFR-SEG-8', 'Ley 19.628 art. 11; OWASP A05', 'Los secretos están publicados en el repositorio y permiten acceder a la base de datos.'],
    ['INC-10: accesibilidad insuficiente (Lighthouse 89, botones sin nombre, contraste bajo)', 'NFR-USAB-1', 'Ley 20.422; WCAG 2.1 AA', 'Barreras para adultos mayores y usuarios de lectores de pantalla; sin evaluación con usuarios reales.'],
    ['INC-07: p95 de 4,0 s frente a 300 ms', 'NFR-PERF-1', 'ISO/IEC 25010 – eficiencia', 'Más de 13 veces el umbral del ERS; defecto de calidad por un retardo artificial en el código.'],
], cap='Resultados frente a la normativa'))
A(SPACER())
A(H(2, '6.2 Análisis ético'))
A(B('**Responsabilidad profesional:** los defectos de seguridad afectan a los clientes finales de las pymes; se reportan con su criticidad real, sin minimizarlos.'))
A(B('**Honestidad de los resultados:** se informan 9 casos fallidos y 1 aprobado tal como ocurrieron y se declaran las limitaciones (sin usuarios reales, pruebas de carga locales y alcance acotado a 10 casos).'))
A(B('**Privacidad desde el diseño:** debe evaluarse si Atlas necesita guardar el número de cuenta completo y por cuánto tiempo conserva datos de clientes eliminados (hoy la eliminación es física).'))
A(B('**Inclusión:** el requerimiento para adultos mayores es un compromiso de equidad, no solo un criterio de aceptación.'))
A(B('**Uso responsable de las pruebas:** solo en el entorno entregado por la asignatura, con datos ficticios (Ley 21.459); los hallazgos se comunican al equipo docente sin detalle explotable.'))
A(H(2, '6.3 Recomendaciones'))
A(TABLE([500, 4700, 1300, 1900, 1346], [
    ['#', 'Recomendación', 'Incidente', 'Norma / principio', 'Prioridad'],
    ['R1', 'Hashear contraseñas con bcrypt (costo ≥ 10) o Argon2, migrar las existentes y exigir una política de contraseñas en el backend.', 'INC-02', 'Ley 19.628 art. 11', 'Inmediata'],
    ['R2', 'Incluir el rol en el JWT y aplicar un middleware de autorización en el backend; no confiar en el rol que envía el cliente.', 'INC-01', 'OWASP A01', 'Inmediata'],
    ['R3', 'Verificar token y pertenencia a la empresa en todos los endpoints (contratos, archivos, auditoría) con un middleware global, y auditar también las descargas.', 'INC-03, INC-05', 'RB-2; RF-6.1; OWASP A01', 'Inmediata'],
    ['R4', 'Exigir JWT_SECRET y credenciales de BD por variable de entorno; eliminar los valores por defecto del código y de docker-compose.', 'INC-04, INC-08', 'OWASP A05', 'Inmediata'],
    ['R5', 'Eliminar el retardo artificial de 4 s y volver a medir con k6 hasta cumplir p95 < 300 ms.', 'INC-07', 'ISO/IEC 25010', 'Alta'],
    ['R6', 'Validar tipo y tamaño de archivo, guardar documentos fuera de la BD y actualizar la imagen base y multer.', 'INC-06, INC-11', 'RF-5.2, RF-5.3; OWASP A06', 'Alta'],
    ['R7', 'Paginar el listado de clientes y reemplazar la eliminación física por una lógica.', 'INC-09', 'RF-4.2', 'Media'],
    ['R8', 'Hacer la interfaz accesible: nombres en botones, contraste y objetivos táctiles ≥ 44 px.', 'INC-10', 'Ley 20.422; WCAG 2.1 AA', 'Media'],
], cap='Recomendaciones vinculadas a la evidencia'))
A(SPACER())
A(H(2, '6.4 Conclusión'))
A(P(f'Se ejecutaron los {n_eje} casos priorizados: {n_apr} aprobado y {n_fal} fallidos, con 12 incidentes (4 críticos, 4 graves, 3 moderados y 1 leve). El sistema **no está en condiciones de liberarse**: la ausencia de control de rol, '
    'las contraseñas en texto plano, la falta de aislamiento entre empresas y el secreto JWT por defecto comprometen la confidencialidad e integridad de los datos personales de terceros, con incumplimiento del deber de cuidado de la Ley 19.628. '
    'Los requerimientos fuera del alcance (compatibilidad, disponibilidad y parte de usabilidad y seguridad) quedan como riesgo residual.'))
# =========================================================== Anexo A
A(H(1, 'Anexo A. Matriz de trazabilidad requerimiento–caso', pb=True))
A(P(f'La matriz relaciona cada caso con los requerimientos del alcance (ERS v1.1): {len(COVM)} filas ({ALC_N} requerimientos y {len(COVM) - ALC_N} criterio de aceptación de interfaz), todas con al menos un caso de prueba (cobertura de diseño del alcance: 100 %). '
    f'Los {42 - ALC_N} requerimientos restantes del ERS están fuera del alcance de este ciclo (sección 1.2).'))
mrows = [['Requerimiento', 'Caso(s) de prueba', 'Tipo']] + [list(r) for r in COVM]
A(TABLE([2200, 3600, 3946], mrows, size=18, cap='Matriz de trazabilidad requerimiento–caso'))

# =========================================================== Anexo B
EV = REPO / '06-Evidencias/estatico'
vul = json.load(open(EV / 'sonarqube_vulnerabilidades.json', encoding='utf-8'))
bug = json.load(open(EV / 'sonarqube_bugs.json', encoding='utf-8'))
smell = json.load(open(EV / 'sonarqube_code_smells.json', encoding='utf-8'))
met = {m['metric']: m['value'] for m in json.load(open(EV / 'sonarqube_metricas.json', encoding='utf-8'))['component']['measures']}
A(H(1, 'Anexo B. Evidencia del análisis estático con SonarQube', pb=True))
A(TABLE([3000, 6746], [
    ['Ficha del análisis', 'Detalle'],
    ['Herramienta', 'SonarQube Community 26.10.0.133078 en Docker (imagen sonarqube:community) y sonarsource/sonar-scanner-cli'],
    ['Proyecto y fecha', 'atlas-ep3 · 29 de octubre de 2026'],
    ['Alcance', 'BACKEND/src y FRONTEND/src de CodigoFuenteA, analizados con dependencias instaladas (npm install); el código original no se modificó'],
    ['Métricas', f"{met['ncloc']} líneas de código · {met['vulnerabilities']} vulnerabilidades · {met['bugs']} bugs · {met['code_smells']} code smells · {met['security_hotspots']} security hotspots · {met['duplicated_lines_density'].replace('.', ',')} % de duplicación · cobertura {met['coverage'].replace('.', ',')} %"],
    ['Archivos de evidencia', 'Carpeta 06-Evidencias/estatico/: sonarqube_metricas.json, sonarqube_vulnerabilidades.json, sonarqube_bugs.json, sonarqube_code_smells.json y capturas sonarqube_01 a 04'],
], cap='Ficha del análisis con SonarQube'))
A(SPACER())
HMAP = {('BACKEND/src/db.js', 6): 'H-11 · NFR-SEG-8', ('BACKEND/src/app.js', 22): 'H-10 · NFR-SEG-5',
        ('BACKEND/src/routes/contracts.js', 15): 'H-08 · RF-5.2', ('BACKEND/src/app.js', 20): 'H-10 · NFR-SEG-5'}
ORDER = {'BLOCKER': 0, 'CRITICAL': 1, 'MAJOR': 2, 'MINOR': 3, 'INFO': 4}
rows = [['Severidad', 'Regla', 'Ubicación', 'Mensaje de SonarQube', 'Esfuerzo', 'Hallazgo · req.']]
for i in sorted(vul['issues'], key=lambda i: ORDER[i['severity']]):
    f = i['component'].split(':', 1)[1]
    rows.append([i['severity'], i['rule'], f"{f}:{i['line']}", i['message'], i['effort'], HMAP[(f, i['line'])]])
A(TABLE([1250, 1650, 1800, 2350, 1000, 1696], rows, size=18, cap='Vulnerabilidades detectadas por SonarQube'))
A(SPACER())
from collections import Counter
bc = Counter(i['rule'] for i in bug['issues'])
A(P(f"**Bugs ({bug['total']}):** {bc['javascript:S9383']} por promesas sin await ni .catch en el frontend (regla S9383) y {bc['css:S4649']} por falta de familia de fuentes genérica; son defectos de confiabilidad, no de seguridad. "
    f"**Code smells ({smell['total']}):** todos por usar parseInt en lugar de Number.parseInt (regla S7773), con impacto bajo. "
    "El panel muestra Reliability = 34 porque agrupa por cualidad afectada: suma los 25 bugs y los 9 code smells que también inciden en confiabilidad.", jc='left'))
A(IMG(str(EV / 'sonarqube_01_overview.png'), 'Resumen del proyecto en SonarQube'))
A(P('Figura B.1. Resumen del proyecto: Quality Gate "Passed", Security 4, Reliability 34, Maintainability 9, duplicación 16,4 %.', size=18, italic=True, jc='left', after=200))
A(IMG(str(EV / 'sonarqube_02_vulnerabilidades.png'), 'Vulnerabilidades en SonarQube'))
A(P('Figura B.2. Las 4 vulnerabilidades, con db.js:6 clasificada Blocker.', size=18, italic=True, jc='left', after=200))
A(IMG(str(EV / 'sonarqube_03_bugs.png'), 'Bugs en SonarQube'))
A(P('Figura B.3. Bugs (25): promesas sin manejar en componentes del frontend.', size=18, italic=True, jc='left', after=200))

# ---------------------------------------------------------------- ensamblado

def build():
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    with zipfile.ZipFile(TEMPLATE) as z:
        z.extractall(WORK)
    for p in WORK.rglob('*'):
        if p.is_symlink():
            p.unlink()
    shutil.rmtree(WORK / '[trash]', ignore_errors=True)
    # propiedades del documento: la plantilla trae el autor original; se reemplazan por los datos del informe
    core = WORK / 'docProps/core.xml'
    c = core.read_text(encoding='utf-8')
    ahora = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    autores = 'Victor Silva, Jonathan Guerra y Darlette Morales'
    c = re.sub(r'<dc:title>.*?</dc:title>', '<dc:title>Informe EP3 - Atlas: seguridad y calidad en el desarrollo de software</dc:title>', c, flags=re.S)
    c = re.sub(r'<dc:creator>.*?</dc:creator>', f'<dc:creator>{autores}</dc:creator>', c, flags=re.S)
    c = re.sub(r'<cp:lastModifiedBy>.*?</cp:lastModifiedBy>', f'<cp:lastModifiedBy>{autores}</cp:lastModifiedBy>', c, flags=re.S)
    c = re.sub(r'(<dcterms:(?:created|modified)[^>]*>)[^<]*(</dcterms:(?:created|modified)>)', rf'\g<1>{ahora}\g<2>', c)
    core.write_text(c, encoding='utf-8')

    (WORK / 'word/media').mkdir(exist_ok=True)
    rels = WORK / 'word/_rels/document.xml.rels'
    rtxt = rels.read_text(encoding='utf-8')
    add = ''
    for rid, src, dst in IMGS:
        shutil.copy(src, WORK / 'word/media' / dst)
        add += f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{dst}"/>'
    rels.write_text(rtxt.replace('</Relationships>', add + '</Relationships>'), encoding='utf-8')

    docp = WORK / 'word/document.xml'
    tree = etree.parse(str(docp))
    root = tree.getroot()
    bd = root.find('w:body', ns)
    kids = list(bd)

    # --- portada
    def set_run_text(par, old, new):
        for t in par.iter('{%s}t' % W):
            if t.text and old in t.text:
                t.text = t.text.replace(old, new)
                return True
        return False

    p_title, p_course, p_names = kids[7], kids[13], kids[15]
    assert set_run_text(p_title, 'TITULO', 'ATLAS')

    def add_line(par, text, bold=False, size=22):
        r = etree.SubElement(par, '{%s}r' % W)
        etree.SubElement(r, '{%s}br' % W)
        r2 = etree.fromstring(f'<w:r {NSDECL}>{rpr(size, bold)}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>')
        par.append(r2)

    add_line(p_title, 'Sistema de gestión de clientes y contratos', True, 32)
    add_line(p_title, 'Evaluación Parcial N°3 – Verificando la calidad, seguridad y cumplimiento normativo', True, 24)
    assert set_run_text(p_course, 'ecci', 'ecci')
    for t in p_course.iter('{%s}t' % W):
        if t.text == 'ecci\u00f3n XX':
            t.text = 'ecci\u00f3n 003V'
    add_line(p_course, 'Carrera: Ingeniería en Informática')
    add_line(p_course, 'Docente: Cristian Eduardo Medina Cespedes')
    add_line(p_course, 'Fecha: 29 de octubre de 2026')
    nm = ['Victor Silva', 'Jonathan Guerra', 'Darlette Morales']
    ts = [t for t in p_names.iter('{%s}t' % W) if t.text and ('Nombre Apellido' in t.text or t.text.strip() in ('1', '2', '3'))]
    # los textos "Nombre Apellido Alumno" + " N" van de a dos; se reemplaza el primero por el nombre y se vacía el número
    idx = 0
    i = 0
    while i < len(ts):
        if 'Nombre Apellido' in ts[i].text:
            ts[i].text = nm[idx]
            if i + 1 < len(ts) and ts[i + 1].text.strip() in ('1', '2', '3'):
                ts[i + 1].text = ''
                i += 1
            idx += 1
        i += 1
    assert idx == 3

    # --- índice (se reconstruye el contenido cacheado del TOC)
    sdt = kids[22]
    content = sdt.find('w:sdtContent', ns)
    for c in list(content):
        content.remove(c)
    HEAD_ALL = [(1, 'INDICE', '_Toc1546197562')] + HEADINGS
    toc = ''
    for n, (lvl, text, bm) in enumerate(HEAD_ALL):
        pg = PAGES.get(text, 2 if text == 'INDICE' else '')
        begin = ''
        if n == 0:
            begin = ('<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve">TOC \\o "1-2" \\z \\u \\h</w:instrText></w:r>'
                     '<w:r><w:fldChar w:fldCharType="separate"/></w:r>')
        end = '<w:r><w:fldChar w:fldCharType="end"/></w:r>' if n == len(HEAD_ALL) - 1 else ''
        ind = '<w:ind w:left="240"/>' if lvl == 2 else ''
        toc += (f'<w:p><w:pPr><w:pStyle w:val="TOC1"/><w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9735"/></w:tabs>{ind}</w:pPr>{begin}'
                f'<w:hyperlink w:anchor="{bm}"><w:r><w:rPr><w:rStyle w:val="Hyperlink"/></w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r>'
                f'<w:r><w:tab/></w:r><w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve">PAGEREF {bm} \\h</w:instrText></w:r>'
                f'<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:rPr><w:rStyle w:val="Hyperlink"/></w:rPr><w:t>{pg}</w:t></w:r>'
                f'<w:r><w:fldChar w:fldCharType="end"/></w:r></w:hyperlink>{end}</w:p>')
    for el in etree.fromstring(f'<root {NSDECL}>{toc}</root>'):
        content.append(el)

    # --- índice de tablas (página propia, tras el índice general)
    tt = (f'<w:p><w:pPr><w:pageBreakBefore/><w:spacing w:before="360" w:after="80"/><w:jc w:val="left"/></w:pPr>{runs("ÍNDICE DE TABLAS", 24, True)}</w:p>')
    for n, cap in enumerate(TABLES, 1):
        pg = PAGES.get(f'T{n}', '')
        begin = ''
        if n == 1:
            begin = ('<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve">TOC \\h \\z \\c "Tabla"</w:instrText></w:r>'
                     '<w:r><w:fldChar w:fldCharType="separate"/></w:r>')
        end = '<w:r><w:fldChar w:fldCharType="end"/></w:r>' if n == len(TABLES) else ''
        tt += (f'<w:p><w:pPr><w:pStyle w:val="TOC1"/><w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9735"/></w:tabs></w:pPr>{begin}'
               f'<w:hyperlink w:anchor="_TocTbl{n}"><w:r><w:rPr><w:rStyle w:val="Hyperlink"/></w:rPr><w:t xml:space="preserve">Tabla {n}. {escape(cap)}</w:t></w:r>'
               f'<w:r><w:tab/></w:r><w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve">PAGEREF _TocTbl{n} \\h</w:instrText></w:r>'
               f'<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:rPr><w:rStyle w:val="Hyperlink"/></w:rPr><w:t>{pg}</w:t></w:r>'
               f'<w:r><w:fldChar w:fldCharType="end"/></w:r></w:hyperlink>{end}</w:p>')
    tbl_index = list(etree.fromstring(f'<root {NSDECL}>{tt}</root>'))
    for el in reversed(tbl_index):
        sdt.addnext(el)

    # --- cuerpo: se descartan relleno y secciones de la plantilla (23 en adelante, salvo sectPr)
    sect = kids[-1]
    assert etree.QName(sect).localname == 'sectPr'
    for el in kids[23:-1]:
        bd.remove(el)
    # salto de página tras la portada (en lugar de párrafos vacíos) y tras el índice
    for el in kids[16:20]:
        bd.remove(el)
    for el in kids[8:11]:  # relleno vacío entre título y datos: libera espacio para que la portada no desborde
        bd.remove(el)
    ref = kids[20]  # Heading1 "INDICE"
    ppr = ref.find('w:pPr', ns)
    ppr.insert(1, etree.fromstring(f'<w:pageBreakBefore {NSDECL}/>'))
    for el in etree.fromstring(f'<root {NSBODY}>{"".join(body)}</root>'):
        sect.addprevious(el)
    if etree.QName(sect.getprevious()).localname == 'tbl':  # Word exige un párrafo tras una tabla al final del cuerpo
        sect.addprevious(etree.fromstring(f'<w:p {NSDECL}><w:pPr><w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/></w:pPr></w:p>'))

    tree.write(str(docp), xml_declaration=True, encoding='UTF-8', standalone=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
        # [Content_Types].xml primero
        order = ['[Content_Types].xml'] + sorted(str(p.relative_to(WORK)) for p in WORK.rglob('*') if p.is_file() and p.name != '[Content_Types].xml')
        for name in order:
            z.write(WORK / name, name)


build()
print('OK', OUT)
json.dump([h[1] for h in HEADINGS], open(SCR / 'headings.json', 'w'), ensure_ascii=False)
json.dump(TABLES, open(SCR / 'tables.json', 'w'), ensure_ascii=False)
