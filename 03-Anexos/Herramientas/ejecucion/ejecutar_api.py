#!/usr/bin/env python3
"""Ejecuta los casos de prueba de API/seguridad de Atlas contra el stack Docker local.

Uso:  python3 ejecutar_api.py            (requiere Atlas en http://localhost:4450 y el contenedor atlas-postgres)
Salida: 06-Evidencias/ejecucion/<CASO>_01_*.txt (evidencia por caso) y 06-Evidencias/ejecucion/resultados_api.json

El resultado esperado de cada criterio se deriva del ERS (no del comportamiento actual del código).
Solo se usan datos ficticios y solo se ataca el entorno local (Ley 21.459).
"""
import base64
import datetime
import hashlib
import hmac
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EV = REPO / '06-Evidencias' / 'ejecucion'
EV.mkdir(parents=True, exist_ok=True)
API = os.environ.get('API', 'http://localhost:4450')
SUF = str(int(time.time()))
RESULTS = {}
HITS = set()
OPENAPI = json.load(open(REPO / 'CodigoFuenteA/BACKEND/src/openapi.json', encoding='utf-8'))


# ------------------------------------------------------------------ utilidades
def norm(path):
    p = path.split('?')[0]
    return re.sub(r'/\d+', '/{id}', p)


def http(method, path, body=None, token=None, headers=None, raw=None, ctype=None, timeout=120):
    h = dict(headers or {})
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        h['Content-Type'] = 'application/json'
    if raw is not None:
        data = raw
        if ctype:
            h['Content-Type'] = ctype
    if token:
        h['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(API + path, data=data, headers=h, method=method)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            st, hd, bd = r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        st, hd, bd = e.code, dict(e.headers), e.read()
    except Exception as e:  # noqa
        st, hd, bd = 0, {}, str(e).encode()
    ms = int((time.time() - t0) * 1000)
    HITS.add((method.upper(), norm(path)))
    return st, hd, bd, ms


def jl(b):
    try:
        return json.loads(b)
    except Exception:
        return {}


def multipart(fields, files):
    bd = '----atlasqa' + uuid.uuid4().hex
    out = b''
    for k, v in fields.items():
        out += f'--{bd}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for k, (fn, ct, content) in files.items():
        out += f'--{bd}\r\nContent-Disposition: form-data; name="{k}"; filename="{fn}"\r\nContent-Type: {ct}\r\n\r\n'.encode() + content + b'\r\n'
    out += f'--{bd}--\r\n'.encode()
    return out, f'multipart/form-data; boundary={bd}'


def db(sql):
    r = subprocess.run(['sg', 'docker', '-c', f'docker exec atlas-postgres psql -U postgres -d atlas -At -F "|" -c "{sql}"'],
                       capture_output=True, text=True)
    return (r.stdout + r.stderr).strip()


def sh(cmd, timeout=120):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return (r.stdout + r.stderr).strip()


class Case:
    def __init__(self, cid, titulo, req, tipo, slug):
        self.cid, self.titulo, self.req, self.tipo, self.slug = cid, titulo, req, tipo, slug
        self.lines = []
        self.crit = []
        self.obs = []
        self.t0 = datetime.datetime.now()

    def log(self, s=''):
        self.lines.append(s)

    def req_(self, method, path, st, ms, note=''):
        self.log(f'  {method} {path} -> HTTP {st} ({ms} ms) {note}')

    def chk(self, texto, ok, detalle=''):
        self.crit.append((texto, bool(ok), detalle))
        self.log(f'  [{"CUMPLE" if ok else "NO CUMPLE"}] {texto}' + (f' — {detalle}' if detalle else ''))

    def note(self, s):
        self.obs.append(s)
        self.log('  Observación: ' + s)

    def done(self, verdict=None):
        if verdict is None:
            verdict = 'Aprobado' if self.crit and all(c[1] for c in self.crit) else 'Fallido'
        self.log('')
        self.log(f'VEREDICTO: {verdict}  ({sum(1 for c in self.crit if c[1])}/{len(self.crit)} criterios cumplidos)')
        head = [f'Caso: {self.cid} — {self.titulo}', f'Requerimiento(s): {self.req}', f'Tipo: {self.tipo}',
                f'Inicio: {self.t0:%Y-%m-%d %H:%M:%S}   Fin: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}',
                f'Entorno: Docker local (atlas-backend/atlas-frontend/atlas-postgres), API {API}', '']
        fn = EV / f'{self.cid}_01_{self.slug}.txt'
        fn.write_text('\n'.join(head + self.lines) + '\n', encoding='utf-8')
        RESULTS[self.cid] = {'titulo': self.titulo, 'req': self.req, 'tipo': self.tipo, 'veredicto': verdict,
                             'criterios': [{'texto': t, 'cumple': o, 'detalle': d} for t, o, d in self.crit],
                             'observaciones': self.obs, 'evidencia': f'06-Evidencias/ejecucion/{fn.name}',
                             'fecha': self.t0.strftime('%Y-%m-%d %H:%M')}
        print(f'{self.cid:12s} {verdict:10s} {sum(1 for c in self.crit if c[1])}/{len(self.crit)}')


def login(user, pwd):
    st, _, b, ms = http('POST', '/autenticacion/login', {'nombre_usuario': user, 'password': pwd})
    return st, jl(b).get('token'), ms


def jwt_payload(tok):
    p = tok.split('.')[1]
    return json.loads(base64.urlsafe_b64decode(p + '=' * (-len(p) % 4)))


def forge(payload, secret, alg='HS256'):
    def b64(x):
        return base64.urlsafe_b64encode(x).rstrip(b'=').decode(errors="replace")
    h = b64(json.dumps({'alg': alg, 'typ': 'JWT'}).encode())
    p = b64(json.dumps(payload).encode())
    if alg == 'none':
        return f'{h}.{p}.'
    sig = b64(hmac.new(secret.encode(), f'{h}.{p}'.encode(), hashlib.sha256).digest())
    return f'{h}.{p}.{sig}'


# ------------------------------------------------------------------ preparación
print('Preparando sesiones y datos ficticios...')
res = {}
ths = [threading.Thread(target=lambda k, u, p: res.__setitem__(k, login(u, p)), args=(k, u, p))
       for k, u, p in (('A', 'admin', 'admin'), ('E', 'editor', 'editor'))]
[t.start() for t in ths]
[t.join() for t in ths]
TA, TE = res['A'][1], res['E'][1]
assert TA and TE, 'No se pudo iniciar sesión con los usuarios semilla'

# Empresa B (para aislamiento entre empresas)
st, _, b, _ = http('POST', '/empresas', {'usuario': {'nombre_usuario': f'qa_b_{SUF}', 'contrasena_hash': 'Qa#EmpresaB-2026x', 'correo': f'qa_b_{SUF}@atlasfake.com'},
                                         'empresa': {'nombre': f'Empresa B QA {SUF}', 'correo': f'empresab_{SUF}@atlasfake.com'}})
_, TB, _ = login(f'qa_b_{SUF}', 'Qa#EmpresaB-2026x')

# Cliente y contrato de la empresa A (semilla para varios casos)
st, _, b, _ = http('POST', '/clientes', {'nombre': f'Cliente Base {SUF}', 'correo': f'base_{SUF}@atlasfake.com'}, TA)
C_BASE = jl(b).get('id')
PDF5 = b'%PDF-1.4\n' + os.urandom(150_000) + b'\n%%EOF'
body, ct = multipart({'cliente_id': C_BASE, 'titulo': 'Contrato base', 'descripcion': 'semilla', 'fecha_inicio': '2026-01-01', 'fecha_fin': '2026-12-31'},
                     {'file': ('base.pdf', 'application/pdf', PDF5)})
st, _, b, _ = http('POST', '/contratos', raw=body, ctype=ct, token=TA)
K_BASE = jl(b).get('id')
print(f'  TA/TE/TB listos; cliente base {C_BASE}, contrato base {K_BASE}, empresaB token={bool(TB)}')


# ================================================================== FUNCIONALES
def func002():
    L = Case('PT-FUNC-002', 'Autenticación y emisión de JWT', 'RF-1.1', 'Funcional', 'login')
    L.log('1) Login válido (admin)')
    st, tok, ms = login('admin', 'admin')
    L.req_('POST', '/autenticacion/login', st, ms, '(credenciales válidas)')
    pl = jwt_payload(tok) if tok else {}
    L.log(f'  Payload JWT: {json.dumps(pl)}')
    L.chk('Login válido responde 200 con JWT', st == 200 and bool(tok))
    L.chk('El JWT incluye expiración (exp)', 'exp' in pl, f'exp={pl.get("exp")}')
    L.log('2) Login inválido y vacío')
    st1, _, b1, ms1 = http('POST', '/autenticacion/login', {'nombre_usuario': 'admin', 'password': 'incorrecta'})
    L.req_('POST', '/autenticacion/login', st1, ms1, '(contraseña incorrecta)  ' + b1.decode(errors="replace")[:80])
    st2, _, b2, ms2 = http('POST', '/autenticacion/login', {'nombre_usuario': 'noexiste', 'password': 'x'})
    L.req_('POST', '/autenticacion/login', st2, ms2, '(usuario inexistente)  ' + b2.decode(errors="replace")[:80])
    st3, _, b3, ms3 = http('POST', '/autenticacion/login', {})
    L.req_('POST', '/autenticacion/login', st3, ms3, '(cuerpo vacío)  ' + b3.decode(errors="replace")[:80])
    L.chk('100 % de credenciales inválidas rechazadas con 401', st1 == 401 and st2 == 401 and st3 in (400, 401), f'{st1}/{st2}/{st3}')
    L.note(f'Latencia del login medida: {ms} ms (el ERS exige < 300 ms; ver PT-PERF-001).')
    L.done()


def func003():
    L = Case('PT-FUNC-003', 'Cierre de sesión y revocación de token', 'RF-1.2', 'Funcional / seguridad', 'logout')
    _, tok, _ = login('admin', 'admin')
    for m, p in (('POST', '/autenticacion/logout'), ('GET', '/autenticacion/logout'), ('POST', '/autenticacion/refresh')):
        st, _, b, ms = http(m, p, token=tok)
        L.req_(m, p, st, ms, b.decode(errors="replace")[:90].replace('\n', ' '))
    st_l = http('POST', '/autenticacion/logout', token=tok)[0]
    L.chk('Existe una operación de cierre de sesión en el servidor', st_l not in (404, 405), f'logout -> {st_l}')
    st, _, b, ms = http('GET', '/clientes', token=tok)
    L.req_('GET', '/clientes', st, ms, '(reutilizar el token tras "cerrar sesión")')
    L.chk('El token queda revocado: 401 tras el logout', st == 401, f'respuesta {st}: el token sigue válido hasta su expiración ({jwt_payload(tok)["exp"] - jwt_payload(tok)["iat"]} s)')
    L.done()


def func004():
    L = Case('PT-FUNC-004', 'Registro de usuario y unicidad de correo', 'RF-2.1, RB-1', 'Funcional', 'registro_correo')
    u1 = {'nombre_usuario': f'qa_u1_{SUF}', 'contrasena_hash': 'Qa#Segura-2026ab', 'correo': f'qa_dup_{SUF}@atlasfake.com'}
    st, _, b, ms = http('POST', '/usuarios', u1)
    L.req_('POST', '/usuarios', st, ms, '(correo nuevo)')
    L.chk('Alta con correo nuevo → 201', st == 201)
    u2 = {'nombre_usuario': f'qa_u2_{SUF}', 'contrasena_hash': 'Qa#Segura-2026ab', 'correo': u1['correo']}
    st2, _, b2, ms2 = http('POST', '/usuarios', u2)
    L.req_('POST', '/usuarios', st2, ms2, '(correo repetido) ' + b2.decode(errors="replace")[:150])
    n = db(f"select count(*) from usuarios where correo='{u1['correo']}'")
    L.chk('0 correos principales duplicados en la base de datos', n == '1', f'filas con ese correo: {n}')
    if st2 >= 500:
        L.note('El duplicado se rechaza por la restricción UNIQUE de la BD, pero la API responde 500 y expone err.message (defecto de manejo de errores; ver PT-SEG-006).')
    e1 = {'nombre': f'Empresa Dup {SUF}', 'correo': f'empdup_{SUF}@atlasfake.com'}
    s1 = http('POST', '/empresas', e1, TA)[0]
    s2, _, b3, _ = http('POST', '/empresas', e1, TA)
    L.log(f'  Empresa con correo repetido: primer alta {s1}, segundo alta {s2}')
    L.chk('Un correo no puede existir en dos empresas como correo principal (RB-1)', s1 == 201 and s2 >= 400, f'{s1}/{s2}')
    L.done()


def func005():
    L = Case('PT-FUNC-005', 'Creación de empresa y rol administrador por defecto', 'RF-2.2, RF-2.3', 'Funcional', 'empresa_rol')
    nu = f'qa_adm_{SUF}'
    st, _, b, ms = http('POST', '/empresas', {'usuario': {'nombre_usuario': nu, 'contrasena_hash': 'Qa#Admin-2026xx', 'correo': f'{nu}@atlasfake.com'},
                                              'empresa': {'nombre': f'Empresa QA {SUF}', 'direccion': 'Calle 1', 'telefono': '+56911111111', 'correo': f'e_{nu}@atlasfake.com'}})
    L.req_('POST', '/empresas', st, ms, '(formato usuario+empresa)')
    L.chk('Empresa y usuario creados (201)', st == 201)
    out = db(f"select eu.rol_id, r.nombre from empresa_usuarios eu join usuarios u on u.id=eu.usuario_id left join roles r on r.id=eu.rol_id where u.nombre_usuario='{nu}'")
    L.log(f'  BD empresa_usuarios (rol_id|nombre): {out}')
    L.chk('El primer usuario de la empresa obtiene rol administrador (rol_id 1)', out.startswith('1'), out)
    _, t, _ = login(nu, 'Qa#Admin-2026xx')
    L.chk('El usuario creado puede iniciar sesión y recibe empresaId en el token', bool(t) and jwt_payload(t).get('empresaId'), json.dumps(jwt_payload(t)) if t else '')
    L.done()


def func006():
    L = Case('PT-FUNC-006', 'Alta, edición y baja de usuarios con rol', 'RF-3.1, RF-3.3', 'Funcional', 'usuarios_rol')
    nu = f'qa_ed_{SUF}'
    r = {}
    for rol in (1, 2):
        st, _, b, ms = http('POST', '/empresa-usuarios', {'rol_id': rol, 'nombre_usuario': f'{nu}_{rol}', 'contrasena_hash': 'Qa#Rol-2026xxxx', 'correo': f'{nu}_{rol}@atlasfake.com'}, TA)
        L.req_('POST', '/empresa-usuarios', st, ms, f'(rol {rol})')
        r[rol] = jl(b)
    L.chk('Admin crea usuarios con rol administrador (1) y editor (2)', all(r[k].get('id') for k in r))
    eid = r[2].get('id')
    st, _, b, ms = http('PUT', f'/empresa-usuarios/{eid}', {'empresa_id': r[2].get('empresa_id'), 'usuario_id': r[2].get('usuario_id'), 'rol_id': 1}, TA)
    L.req_('PUT', f'/empresa-usuarios/{eid}', st, ms)
    L.chk('El administrador puede modificar el rol', st == 200)
    st, _, b, ms = http('DELETE', f'/empresa-usuarios/{eid}', token=TA)
    L.req_('DELETE', f'/empresa-usuarios/{eid}', st, ms)
    L.chk('El administrador puede eliminar el vínculo', st == 200)
    au = db("select accion from auditoria where accion like 'EMPRESA_USUARIOS_%' order by id desc limit 3")
    L.log('  Auditoría reciente:\n    ' + au.replace('\n', '\n    '))
    L.chk('Las operaciones quedan registradas en auditoría', 'EMPRESA_USUARIOS_CREAR' in au and 'EMPRESA_USUARIOS_ELIMINAR' in au)
    L.done()


def func007():
    L = Case('PT-FUNC-007', 'Creación de cliente y validaciones', 'RF-4.1, RF-4.3', 'Funcional', 'cliente_validaciones')
    ok = {'nombre': 'Cliente Valido', 'correo': f'val_{SUF}@atlasfake.com', 'telefono': '+56912345678', 'rut': '12.345.678-5'}
    st, _, b, ms = http('POST', '/clientes', ok, TA)
    L.req_('POST', '/clientes', st, ms, '(datos válidos)')
    L.chk('Datos válidos → 201', st == 201)
    invalid = [('correo sin formato', {'nombre': 'X', 'correo': 'no-es-correo'}),
               ('teléfono alfanumérico', {'nombre': 'X', 'correo': f'tel_{SUF}@atlasfake.com', 'telefono': 'abc-xyz'}),
               ('RUT inválido', {'nombre': 'X', 'correo': f'rut_{SUF}@atlasfake.com', 'rut': '11.111.111-9'}),
               ('nombre vacío', {'nombre': '', 'correo': f'vac_{SUF}@atlasfake.com'})]
    rej = 0
    for etq, p in invalid:
        s, _, bb, m = http('POST', '/clientes', p, TA)
        L.req_('POST', '/clientes', s, m, f'({etq}) {bb.decode(errors="replace")[:70]}')
        if 400 <= s < 500:
            rej += 1
    L.chk('100 % de las entradas inválidas rechazadas con 400 y mensaje', rej == len(invalid), f'{rej}/{len(invalid)} rechazadas')
    n = db(f"select count(*) from clientes where correo in ('no-es-correo','tel_{SUF}@atlasfake.com','rut_{SUF}@atlasfake.com','vac_{SUF}@atlasfake.com')")
    L.log(f'  Registros inválidos persistidos en la BD: {n}')
    L.done()


def func008():
    L = Case('PT-FUNC-008', 'Listar, filtrar, editar y eliminar clientes', 'RF-4.2', 'Funcional', 'clientes_crud')
    ids = []
    for i in range(3):
        s, _, b, _ = http('POST', '/clientes', {'nombre': f'Lista {SUF} {i}', 'correo': f'lst{i}_{SUF}@atlasfake.com'}, TA)
        ids.append(jl(b).get('id'))
    st, _, b, ms = http('GET', '/clientes?page=1&limit=2', token=TA)
    data = jl(b)
    n = len(data) if isinstance(data, list) else len(data.get('data', data.get('clientes', [])) if isinstance(data, dict) else [])
    L.req_('GET', '/clientes?page=1&limit=2', st, ms, f'(elementos devueltos: {n})')
    L.chk('El listado admite paginación (limit=2 devuelve ≤ 2 elementos)', st == 200 and n <= 2, f'devolvió {n}')
    st, _, b, ms = http('GET', '/clientes/search?name=' + urllib.parse.quote(f'Lista {SUF} 1'), token=TA)
    L.req_('GET', '/clientes/search?name=…', st, ms, b.decode(errors="replace")[:100])
    L.chk('El filtro por nombre devuelve el cliente buscado', st == 200 and f'Lista {SUF} 1' in b.decode(errors="replace"))
    st, _, b, ms = http('PUT', f'/clientes/{ids[0]}', {'nombre': f'Editado {SUF}', 'correo': f'lst0_{SUF}@atlasfake.com'}, TA)
    L.req_('PUT', f'/clientes/{ids[0]}', st, ms)
    L.chk('Edición correcta (200)', st == 200)
    st, _, b, ms = http('DELETE', f'/clientes/{ids[2]}', token=TA)
    L.req_('DELETE', f'/clientes/{ids[2]}', st, ms, b.decode(errors="replace")[:60])
    fila = db(f'select count(*) from clientes where id={ids[2]}')
    L.log(f'  Filas con id={ids[2]} tras DELETE: {fila}')
    L.chk('Eliminación lógica: el registro sigue en la BD con marca de baja', fila == '1', 'el registro fue borrado físicamente' if fila == '0' else '')
    L.done()


def func009():
    L = Case('PT-FUNC-009', 'Estado del contrato y enlace compartido', 'RF-5.4, RF-5.5', 'Funcional / seguridad', 'estado_enlace')
    hoy = datetime.date.today()
    fechas = {'vencido': (hoy - datetime.timedelta(days=60), hoy - datetime.timedelta(days=5)),
              'por_vencer': (hoy - datetime.timedelta(days=60), hoy + datetime.timedelta(days=10)),
              'vigente': (hoy - datetime.timedelta(days=5), hoy + datetime.timedelta(days=200))}
    ids = {}
    for k, (a, f) in fechas.items():
        body, ct = multipart({'cliente_id': C_BASE, 'titulo': f'Estado {k} {SUF}', 'fecha_inicio': str(a), 'fecha_fin': str(f)}, {})
        s, _, b, _ = http('POST', '/contratos', raw=body, ctype=ct, token=TA)
        ids[k] = jl(b).get('id')
    st, _, b, ms = http('GET', '/contratos/estados', token=TA)
    est = jl(b)
    L.req_('GET', '/contratos/estados', st, ms, json.dumps(est)[:200] if est else '')
    txt = json.dumps(est)
    L.chk('El estado por fechas distingue contratos por vencer y expirados', st == 200 and str(ids['por_vencer']) in txt and str(ids['vencido']) in txt, f'ids {ids}')
    cand = [f'/contratos/{K_BASE}/compartir', f'/contratos/{K_BASE}/share', f'/contratos/{K_BASE}/enlace', f'/contratos/{K_BASE}/link']
    codes = []
    for p in cand:
        s, _, b, _ = http('POST', p, token=TA)
        codes.append(s)
        L.log(f'  POST {p} -> {s}')
    gr = [p for p in OPENAPI['paths'] if re.search('compart|share|enlace|link', p, re.I)]
    L.chk('Existe una función para generar y revocar un enlace compartido (RF-5.5)', any(c in (200, 201) for c in codes) or bool(gr), f'rutas probadas → {codes}; en openapi.json: {gr or "ninguna"}')
    L.done()


def func010():
    L = Case('PT-FUNC-010', 'Registro de auditoría de acciones críticas', 'RF-6.1', 'Funcional', 'auditoria')
    marca = f'AUD{SUF}'
    s, _, b, _ = http('POST', '/clientes', {'nombre': f'Cliente {marca}', 'correo': f'{marca}@atlasfake.com'}, TA)
    cid = jl(b).get('id')
    http('PUT', f'/clientes/{cid}', {'nombre': f'Cliente {marca} v2', 'correo': f'{marca}@atlasfake.com'}, TA)
    body, ct = multipart({'cliente_id': cid, 'titulo': f'Contrato {marca}', 'fecha_inicio': '2026-01-01', 'fecha_fin': '2026-12-31'}, {'file': ('a.pdf', 'application/pdf', PDF5)})
    s, _, b, _ = http('POST', '/contratos', raw=body, ctype=ct, token=TA)
    kid = jl(b).get('id')
    http('GET', f'/contratos/{kid}/file', token=TA)
    http('DELETE', f'/contratos/{kid}', token=TA)
    time.sleep(1)
    acc = db(f"select usuario_id||' | '||accion from auditoria where accion like '%{marca}%' or accion like '%contrato ID {kid}%' or accion like '%cliente ID {cid}%' or accion like '%contratos/{kid}/file%' order by id")
    L.log('  Registros de auditoría generados por las acciones:\n    ' + acc.replace('\n', '\n    '))
    for etq, patron in (('crear cliente', 'CLIENTES_CREAR'), ('editar cliente', 'CLIENTES_ACTUALIZAR'), ('crear contrato / subir documento', 'CONTRATOS_CREAR'),
                        ('descargar documento', 'DESCARG'), ('eliminar contrato', 'CONTRATOS_ELIMINAR')):
        L.chk(f'Se audita: {etq}', patron in acc.upper())
    L.log('  Acceso a la auditoría sin autenticación:')
    st, _, b, ms = http('GET', '/auditoria')
    n = len(jl(b)) if isinstance(jl(b), list) else 0
    L.req_('GET', '/auditoria', st, ms, f'(sin Authorization) registros devueltos: {n}')
    L.chk('La auditoría solo es consultable con autenticación', st in (401, 403), f'HTTP {st}, {n} registros expuestos')
    L.done()


def func011():
    L = Case('PT-FUNC-011', 'Colección OpenAPI: cobertura de endpoints', '§3.1.2 ERS', 'Funcional (API)', 'openapi')
    ops = {(m.upper(), norm(p).replace('{id}', '{id}')) for p, v in OPENAPI['paths'].items() for m in v if m in ('get', 'post', 'put', 'delete')}
    ops = {(m, re.sub(r'\{[^}]+\}', '{id}', p)) for m, p in ops}
    # ejercitar endpoints no cubiertos por otros casos (lectura y alta/baja de datos ficticios)
    http('GET', '/roles', token=TA)
    http('GET', '/roles/1', token=TA)
    http('GET', '/empresas', token=TA)
    http('GET', '/empresas/1', token=TA)
    http('GET', '/metricas', token=TA)
    http('GET', '/contratos/dashboard', token=TA)
    http('GET', '/usuarios', token=TA)
    http('GET', '/usuarios/1', token=TA)
    http('GET', '/empresa-usuarios', token=TA)
    http('GET', '/empresa-usuarios/1', token=TA)
    http('GET', f'/clientes/{C_BASE}', token=TA)
    http('GET', f'/contratos/{K_BASE}', token=TA)
    http('GET', '/contratos', token=TA)
    http('GET', '/clientes', token=TA)
    s, _, b, _ = http('POST', '/roles', {'nombre': f'rol_qa_{SUF}'}, TA)
    rid = jl(b).get('id')
    if rid:
        http('PUT', f'/roles/{rid}', {'nombre': f'rol_qa2_{SUF}'}, TA)
        http('DELETE', f'/roles/{rid}', token=TA)
    s, _, b, _ = http('POST', '/usuarios', {'nombre_usuario': f'qa_x_{SUF}', 'contrasena_hash': 'Qa#X-2026abcdef', 'correo': f'qa_x_{SUF}@atlasfake.com'})
    uid = jl(b).get('id')
    if uid:
        http('PUT', f'/usuarios/{uid}', {'nombre_usuario': f'qa_x2_{SUF}', 'correo': f'qa_x2_{SUF}@atlasfake.com'}, TA)
        http('DELETE', f'/usuarios/{uid}', token=TA)
    s, _, b, _ = http('POST', '/empresas', {'nombre': f'E QA {SUF}', 'correo': f'eqa_{SUF}@atlasfake.com'}, TA)
    eid = jl(b).get('id')
    if eid:
        http('PUT', f'/empresas/{eid}', {'nombre': f'E QA2 {SUF}', 'correo': f'eqa2_{SUF}@atlasfake.com'}, TA)
        http('DELETE', f'/empresas/{eid}', token=TA)
    http('POST', '/auditoria', {'accion': 'QA', 'detalles': 'prueba'}, TA)
    http('GET', f'/contratos/{K_BASE}/file', token=TA)
    body, ct = multipart({'cliente_id': C_BASE, 'titulo': 'Para editar', 'fecha_inicio': '2026-01-01', 'fecha_fin': '2026-12-31'}, {})
    s, _, b, _ = http('POST', '/contratos', raw=body, ctype=ct, token=TA)
    kid = jl(b).get('id')
    if kid:
        http('PUT', f'/contratos/{kid}', {'cliente_id': C_BASE, 'titulo': 'Editado', 'descripcion': 'x', 'fecha_inicio': '2026-01-01', 'fecha_fin': '2026-12-31'}, TA)
        http('DELETE', f'/contratos/{kid}', token=TA)
    http('GET', '/clientes/search?name=a', token=TA)
    http('GET', '/usuarios', token=TA)
    http('GET', '/auditoria', token=TA)
    http('POST', '/empresa-usuarios', {'rol_id': 2, 'nombre_usuario': f'qa_y_{SUF}', 'contrasena_hash': 'Qa#Y-2026abcdef', 'correo': f'qa_y_{SUF}@atlasfake.com'}, TA)
    cubiertos = {o for o in ops if o in {(m, re.sub(r'\{[^}]+\}', '{id}', p)) for m, p in HITS}}
    pct = 100 * len(cubiertos) / len(ops)
    L.log(f'  Operaciones en openapi.json: {len(ops)}; ejercitadas: {len(cubiertos)} ({pct:.0f} %)')
    faltan = sorted(ops - cubiertos)
    L.log('  No ejercitadas: ' + (', '.join(f'{m} {p}' for m, p in faltan) or 'ninguna'))
    L.chk('≥ 80 % de los endpoints del backend cubiertos', pct >= 80, f'{pct:.0f} % ({len(cubiertos)}/{len(ops)})')
    L.note('Se ejecutó con un cliente HTTP propio sobre openapi.json (equivalente a la colección Newman); no se evaluó contrato de respuesta campo a campo.')
    L.done()
    RESULTS['_cobertura_endpoints'] = {'total': len(ops), 'cubiertos': len(cubiertos), 'pct': round(pct, 1)}


# ================================================================== SEGURIDAD
def seg001():
    L = Case('PT-SEG-001', 'Hashing de contraseñas y política de contraseñas', 'NFR-SEG-2; restricción ERS §2.4', 'Seguridad (SAST + BD + API)', 'hash_politica')
    pk = (REPO / 'CodigoFuenteA/BACKEND/package.json').read_text()
    code = sh(f'grep -rniE "bcrypt|argon2|scrypt" {REPO}/CodigoFuenteA/BACKEND/src {REPO}/CodigoFuenteA/BACKEND/package.json | head')
    L.log(f'1) SAST: búsqueda de bcrypt/argon2/scrypt en backend → "{code or "sin coincidencias"}"')
    L.chk('La dependencia y las llamadas de hashing existen en el backend', 'bcrypt' in pk.lower() or bool(code))
    out = db('select nombre_usuario, contrasena_hash from usuarios order by id limit 6')
    L.log('2) Base de datos: SELECT nombre_usuario, contrasena_hash FROM usuarios:\n    ' + out.replace('\n', '\n    '))
    filas = [x.split('|') for x in out.splitlines()]
    L.chk('100 % de los registros tienen hash bcrypt ($2a$/$2b$/$2y$)', all(f[1].startswith(('$2a$', '$2b$', '$2y$')) for f in filas), f'{sum(1 for f in filas if f[1].startswith("$2"))}/{len(filas)}')
    L.log('3) Política de contraseñas: alta con tres contraseñas')
    pols = {}
    for etq, pw in (('débil "abc"', 'abc'), ('sin símbolo', 'Atlas2026Segura'), ('conforme', 'Atlas#2026-Segura')):
        s, _, b, ms = http('POST', '/usuarios', {'nombre_usuario': f'qa_h_{etq[:3]}{SUF}', 'contrasena_hash': pw, 'correo': f'qa_h_{etq[:3]}{SUF}@atlasfake.com'})
        pols[etq] = s
        L.req_('POST', '/usuarios', s, ms, f'({etq})')
    L.chk('El backend rechaza las contraseñas que incumplen la política (≥ 12, mayúscula, minúscula, número y símbolo)', pols['débil "abc"'] >= 400 and pols['sin símbolo'] >= 400, str(pols))
    nu = f'qa_h_con{SUF}'
    row = db(f"select contrasena_hash from usuarios where nombre_usuario='{nu}'")
    L.log(f'4) Valor almacenado para la contraseña conforme: "{row}"')
    L.chk('La contraseña almacenada no es legible (hash con sal)', row.startswith('$2'), f'valor en BD: {row}')
    L.done()


def seg002():
    L = Case('PT-SEG-002', 'Control de acceso por rol en el backend (RBAC)', 'NFR-SEG-4, RF-3.2, RB-4, RB-5', 'Seguridad (autorización)', 'rbac')
    L.log(f'1) Payload JWT editor: {json.dumps(jwt_payload(TE))}')
    L.log(f'   Payload JWT admin : {json.dumps(jwt_payload(TA))}')
    L.chk('El token incluye el rol del usuario', any('rol' in k.lower() for k in jwt_payload(TE)), f'campos: {list(jwt_payload(TE))}')
    s, _, b, _ = http('POST', '/clientes', {'nombre': f'RBAC {SUF}', 'correo': f'rbac_{SUF}@atlasfake.com'}, TA)
    c1 = jl(b).get('id')
    body, ct = multipart({'cliente_id': c1, 'titulo': f'RBAC K {SUF}', 'fecha_inicio': '2026-01-01', 'fecha_fin': '2026-12-31'}, {})
    s, _, b, _ = http('POST', '/contratos', raw=body, ctype=ct, token=TA)
    k1 = jl(b).get('id')
    s, _, b, _ = http('POST', '/usuarios', {'nombre_usuario': f'rb_del_{SUF}', 'contrasena_hash': 'Qa#Del-2026abcdef', 'correo': f'rb_del_{SUF}@atlasfake.com'})
    uid = jl(b).get('id')
    ops = [('GET', '/clientes', None, 'lectura'),
           ('POST', '/clientes', {'nombre': f'Editor crea {SUF}', 'correo': f'edit_{SUF}@atlasfake.com'}, 'escritura'),
           ('PUT', f'/clientes/{c1}', {'nombre': f'Editor edita {SUF}', 'correo': f'rbac_{SUF}@atlasfake.com'}, 'escritura'),
           ('DELETE', f'/clientes/{c1}', None, 'escritura'),
           ('POST', '/contratos', 'MP', 'escritura'),
           ('DELETE', f'/contratos/{k1}', None, 'escritura'),
           ('POST', '/empresa-usuarios', {'rol_id': 1, 'nombre_usuario': f'esc_{SUF}', 'contrasena_hash': 'Qa#Esc-2026abcdef', 'correo': f'esc_{SUF}@atlasfake.com'}, 'escritura'),
           ('DELETE', f'/usuarios/{uid}', None, 'escritura')]
    L.log('2) Operaciones con TOKEN_EDITOR (esperado: lectura 200; escritura 403):')
    exitos = 0
    escrit = 0
    sts_esc = []
    for m, p, bd, tipo in ops:
        if bd == 'MP':
            body, ct = multipart({'cliente_id': c1, 'titulo': f'Editor K {SUF}', 'fecha_inicio': '2026-01-01', 'fecha_fin': '2026-12-31'}, {})
            s, _, b, ms = http(m, p, raw=body, ctype=ct, token=TE)
        else:
            s, _, b, ms = http(m, p, bd, TE)
        if tipo == 'escritura':
            escrit += 1
            sts_esc.append(s)
            if 200 <= s < 300:
                exitos += 1
        L.req_(m, p, s, ms, f'[{tipo}] ' + b.decode(errors="replace")[:70].replace('\n', ' '))
    L.chk('0 operaciones de escritura exitosas con rol editor', exitos == 0, f'{exitos}/{escrit} escrituras exitosas')
    L.chk('Las escrituras del editor se deniegan con 403', all(x == 403 for x in sts_esc), f'códigos obtenidos: {sts_esc}')
    L.log('3) Con TOKEN_ADMIN las operaciones permitidas funcionan (2xx):')
    sa, _, _, _ = http('POST', '/clientes', {'nombre': f'Admin crea {SUF}', 'correo': f'adm_{SUF}@atlasfake.com'}, TA)
    L.log(f'  POST /clientes -> {sa}')
    L.chk('100 % de las operaciones permitidas para el administrador', sa == 201)
    L.note('El paso 4 (manipular localStorage.role en el navegador) no se ejecutó: el backend ya acepta las escrituras del editor sin consultar rol, por lo que la restricción solo existe en la interfaz.')
    L.done()


def seg003():
    L = Case('PT-SEG-003', 'TLS y redirección HTTP→HTTPS', 'NFR-SEG-1', 'Seguridad (configuración)', 'tls')
    out = sh('curl -sI -m 5 http://localhost:3350/ | head -5')
    L.log('1) curl -I http://localhost:3350/\n    ' + out.replace('\n', '\n    '))
    https_f = sh('curl -skI -m 5 https://localhost:3350/ 2>&1 | head -2; echo "exit=$?"')
    L.log('2) curl -k https://localhost:3350/ →\n    ' + https_f.replace('\n', '\n    '))
    https_a = sh('curl -skI -m 5 https://localhost:4450/ 2>&1 | head -2')
    L.log('3) curl -k https://localhost:4450/ →\n    ' + (https_a or '(sin respuesta TLS)').replace('\n', '\n    '))
    ng = sh(f'grep -nE "listen|ssl" {REPO}/CodigoFuenteA/FRONTEND/nginx.conf')
    L.log('4) nginx.conf:\n    ' + ng.replace('\n', '\n    '))
    L.chk('El tráfico HTTP es redirigido a HTTPS (301/308)', ' 301 ' in out or ' 308 ' in out or ' 302 ' in out)
    L.chk('El frontend responde por TLS ≥ 1.2', 'HTTP/' in https_f and '200' in https_f)
    L.chk('La API responde por TLS ≥ 1.2', 'HTTP/' in https_a)
    L.done()


def seg004():
    L = Case('PT-SEG-004', 'Cifrado de datos sensibles en reposo', 'NFR-SEG-3', 'Seguridad (BD)', 'cifrado_reposo')
    s, _, b, _ = http('POST', '/clientes', {'nombre': f'Banco {SUF}', 'correo': f'banco_{SUF}@atlasfake.com', 'nombre_banco': 'Banco Ficticio', 'numero_cuenta': '123456789012', 'titular_cuenta': 'Titular Ficticio'}, TA)
    cid = jl(b).get('id')
    out = db(f'select nombre_banco, numero_cuenta, titular_cuenta from clientes where id={cid}')
    L.log(f'1) Cliente creado id={cid}. SELECT en la BD →\n    {out}')
    L.chk('numero_cuenta no es legible en la base de datos (cifrado en reposo)', '123456789012' not in out, f'valor leído directamente: {out}')
    col = db("select column_name, data_type from information_schema.columns where table_name='clientes' and column_name in ('numero_cuenta','nombre_banco','titular_cuenta')")
    L.log('2) Tipos de columna:\n    ' + col.replace('\n', '\n    '))
    L.done()


def seg005():
    L = Case('PT-SEG-005', 'Inyección SQL, XSS, CSRF y validación de entrada', 'NFR-SEG-5', 'Seguridad (DAST manual)', 'inyeccion_xss')
    s, _, b, ms = http('GET', '/clientes/search?name=' + urllib.parse.quote("' OR '1'='1"), token=TA)
    sa = http('GET', '/clientes/search?name=zzzzzzzz_inexistente', token=TA)
    L.req_('GET', "/clientes/search?name=' OR '1'='1", s, ms, f'filas: {len(jl(b)) if isinstance(jl(b), list) else "?"}; búsqueda inexistente → {len(jl(sa[2])) if isinstance(jl(sa[2]), list) else "?"}')
    L.chk('SQL Injection en búsqueda: sin datos extra ni error SQL (consultas parametrizadas)', s == 200 and 'syntax' not in b.decode(errors="replace").lower() and (not isinstance(jl(b), list) or len(jl(b)) == 0))
    s2, _, b2, ms2 = http('POST', '/autenticacion/login', {'nombre_usuario': "admin' --", 'password': 'x'})
    L.req_('POST', '/autenticacion/login', s2, ms2, '(nombre_usuario = "admin\' --")')
    L.chk('Inyección en el login rechazada (401)', s2 == 401)
    xss = '<img src=x onerror=alert(1)>'
    s3, _, b3, _ = http('POST', '/clientes', {'nombre': xss, 'correo': f'xss_{SUF}@atlasfake.com'}, TA)
    cid = jl(b3).get('id')
    s4, _, b4, _ = http('GET', f'/clientes/{cid}', token=TA)
    L.log(f'  XSS almacenado: POST /clientes -> {s3}; GET devuelve nombre = {jl(b4).get("nombre")!r}')
    L.chk('La entrada con HTML/JS se sanea o codifica en el servidor', jl(b4).get('nombre') != xss, 'el payload se almacena y devuelve sin modificar (la mitigación depende solo del escapado de React)')
    inv = [('JSON mal formado', None), ('correo inválido', {'nombre': 'x', 'correo': 'no-correo'}), ('nombre de 10 000 caracteres', {'nombre': 'A' * 10000, 'correo': f'long_{SUF}@atlasfake.com'})]
    rej = 0
    for etq, bd in inv:
        if bd is None:
            s5, _, b5, _ = http('POST', '/clientes', raw=b'{"nombre": ', ctype='application/json', token=TA)
        else:
            s5, _, b5, _ = http('POST', '/clientes', bd, TA)
        L.log(f'  Entrada inválida ({etq}) -> HTTP {s5}')
        if 400 <= s5 < 500:
            rej += 1
    L.chk('100 % de las entradas inválidas rechazadas por el servidor (4xx)', rej == len(inv), f'{rej}/{len(inv)}')
    st, hd, _, _ = http('GET', '/')
    hdr = {k.lower(): v for k, v in hd.items()}
    L.log('  Cabeceras de la API (GET /):\n    ' + '\n    '.join(f'{k}: {v}' for k, v in hdr.items()))
    faltan = [h for h in ('content-security-policy', 'x-content-type-options', 'strict-transport-security') if h not in hdr]
    L.chk('Cabeceras de seguridad mínimas presentes (CSP, X-Content-Type-Options, HSTS)', not faltan, f'faltan: {", ".join(faltan)}')
    L.chk('CORS restringido a orígenes autorizados', hdr.get('access-control-allow-origin', '') not in ('*',), f'Access-Control-Allow-Origin: {hdr.get("access-control-allow-origin")}')
    L.chk('No se divulga la tecnología del servidor (X-Powered-By)', 'x-powered-by' not in hdr, f'X-Powered-By: {hdr.get("x-powered-by")}')
    L.log('  CSRF: la sesión usa cabecera Authorization: Bearer (sin cookies); no aplica CSRF clásico.')
    L.log('  Fuerza bruta: 8 intentos fallidos consecutivos en paralelo')
    rs = []
    ths = [threading.Thread(target=lambda: rs.append(http('POST', '/autenticacion/login', {'nombre_usuario': 'admin', 'password': f'mala{i}'})[0])) for i in range(8)]
    [t.start() for t in ths]
    [t.join() for t in ths]
    L.log(f'  Resultados: {rs}')
    L.chk('Existe limitación de intentos de autenticación (429 o bloqueo)', any(r == 429 for r in rs), f'respuestas: {sorted(set(rs))}')
    L.note('OWASP ZAP baseline no se ejecutó en este ciclo; las verificaciones DAST se hicieron manualmente con peticiones HTTP.')
    L.done()


def seg006():
    L = Case('PT-SEG-006', 'Gestión segura de errores y logs', 'NFR-SEG-6', 'Seguridad', 'errores_logs')
    casos = [('GET', '/clientes/abc', None, 'ID no numérico'), ('GET', '/clientes/99999999', None, 'ID inexistente'),
             ('POST', '/clientes', 'JSON', 'JSON mal formado'), ('POST', '/usuarios', {'nombre_usuario': 'admin', 'contrasena_hash': 'x', 'correo': 'x@x.cl'}, 'usuario duplicado'),
             ('GET', '/contratos/abc', None, 'contrato ID no numérico')]
    leaks = 0
    for m, p, bd, etq in casos:
        if bd == 'JSON':
            s, _, b, ms = http(m, p, raw=b'{"x":', ctype='application/json', token=TA)
        else:
            s, _, b, ms = http(m, p, bd, TA)
        txt = b.decode(errors='replace')
        fuga = bool(re.search(r'syntax|violates|invalid input|relation|constraint|stack|at .*\.js|pg_|duplicate key', txt, re.I))
        leaks += fuga
        L.req_(m, p, s, ms, f'({etq}) {"FUGA " if fuga else ""}{txt[:140].replace(chr(10), " ")}')
    L.chk('0 respuestas con detalle interno (err.message, SQL, rutas, stack)', leaks == 0, f'{leaks}/{len(casos)} respuestas exponen detalles internos')
    logs = sh('sg docker -c "docker logs --tail 40 atlas-backend 2>&1" | grep -iE "password|secret|token" | head -5')
    L.log('  Búsqueda de secretos en los logs del backend (últimas 40 líneas): ' + (logs or 'sin coincidencias'))
    L.chk('Los logs no contienen contraseñas ni secretos', not logs)
    L.done()


def seg007():
    L = Case('PT-SEG-007', 'Cumplimiento técnico de protección de datos personales', 'NFR-SEG-8', 'Seguridad / normativo', 'datos_personales')
    sec = sh(f'cd {REPO} && grep -nE "alone15|POSTGRES_PASSWORD:-postgres|your-secret-key|\\"inseguro\\"" CodigoFuenteA/BACKEND/src/db.js CodigoFuenteA/docker-compose.yml CodigoFuenteA/BACKEND/src/routes/auth.js | head -12')
    L.log('1) Secretos y credenciales por defecto en el código/compose:\n    ' + sec.replace('\n', '\n    '))
    L.chk('0 secretos o credenciales por defecto en el código y la infraestructura', not sec)
    L.log('2) Datos personales almacenados (columnas de clientes con datos personales/bancarios): ' + db("select string_agg(column_name,', ') from information_schema.columns where table_name='clientes' and column_name in ('rut','correo','telefono','direccion','numero_cuenta','nombre_banco','titular_cuenta','correo_representante')"))
    cons = sh(f'grep -rniE "consentimiento|politica de privacidad|privacidad|eliminar.*datos" {REPO}/CodigoFuenteA/FRONTEND/src | head -3')
    L.log('3) Búsqueda de consentimiento / política de privacidad en el frontend: ' + (cons or 'sin coincidencias'))
    L.chk('Existe consentimiento informado o política de privacidad visible (Ley 19.628 art. 4)', bool(cons))
    acc = db("select count(*) from auditoria")
    L.log(f'4) Trazabilidad de acceso: {acc} registros de auditoría; consulta de /auditoria sin autenticación posible (ver PT-FUNC-010).')
    L.chk('El acceso a datos personales requiere autenticación en todos los endpoints (art. 11 Ley 19.628)', http('GET', f'/contratos/{K_BASE}/file')[0] in (401, 403), f'GET /contratos/{K_BASE}/file sin token → {http("GET", f"/contratos/{K_BASE}/file")[0]}')
    L.note('Gitleaks no se ejecutó en este ciclo; la búsqueda de secretos se hizo con grep sobre los archivos de configuración.')
    L.done()


def seg008():
    L = Case('PT-SEG-008', 'Sesión JWT: expiración, firma y secreto', 'NFR-SEG-9', 'Seguridad (sesión)', 'jwt')
    pl = jwt_payload(TA)
    now = int(time.time())
    env = sh('sg docker -c "docker exec atlas-backend printenv JWT_SECRET"')
    L.log(f'1) JWT_SECRET efectivo en el contenedor del backend: "{env}"')
    L.chk('El secreto JWT es robusto y no es un valor por defecto público', env not in ('your-secret-key-change-in-production', 'inseguro', ''), f'valor: {env}')
    forjado = forge({**pl, 'iat': now, 'exp': now + 3600}, env or 'inseguro')
    s, _, b, ms = http('GET', '/clientes', token=forjado)
    L.req_('GET', '/clientes', s, ms, '(token forjado con el secreto por defecto del docker-compose)')
    L.chk('Un token firmado con el secreto por defecto es rechazado', s == 401, f'HTTP {s}')
    mal = TA[:-3] + ('AAA' if not TA.endswith('AAA') else 'BBB')
    s, _, _, _ = http('GET', '/clientes', token=mal)
    L.log(f'  Token con firma alterada -> {s}')
    L.chk('Un token con firma alterada es rechazado', s == 401)
    s, _, _, _ = http('GET', '/clientes', token=forge({**pl, 'iat': now, 'exp': now + 3600}, '', alg='none'))
    L.log(f'  Token con alg=none -> {s}')
    L.chk('Un token con alg=none es rechazado', s == 401)
    exp = forge({**pl, 'iat': now - 7200, 'exp': now - 3600}, env or 'inseguro')
    s, _, _, _ = http('GET', '/clientes', token=exp)
    L.log(f'  Token expirado (firmado correctamente) -> {s}')
    L.chk('Un token expirado es rechazado', s == 401)
    L.chk('El tiempo de vida del token es acotado (≤ 2 h)', pl['exp'] - pl['iat'] <= 7200, f'{pl["exp"] - pl["iat"]} s')
    L.done()


def seg009():
    L = Case('PT-SEG-009', 'Aislamiento entre empresas (IDOR)', 'RB-2', 'Seguridad (autorización)', 'aislamiento')
    L.log('Recursos de la empresa A: cliente %s, contrato %s. Actor: usuario administrador de la empresa B.' % (C_BASE, K_BASE))
    pruebas = [('GET', f'/clientes/{C_BASE}', TB, None), ('GET', f'/contratos/{K_BASE}', TB, None), ('GET', f'/contratos/{K_BASE}/file', TB, None),
               ('PUT', f'/clientes/{C_BASE}', TB, {'nombre': 'modificado por B', 'correo': f'base_{SUF}@atlasfake.com'}),
               ('GET', '/auditoria', TB, None), ('GET', f'/contratos/{K_BASE}/file', None, None), ('GET', f'/contratos/{K_BASE}', None, None)]
    mp_body, mp_ct = multipart({'cliente_id': C_BASE, 'titulo': f'Contrato intruso {SUF}', 'fecha_inicio': '2026-01-01', 'fecha_fin': '2026-12-31'}, {})
    pruebas += [('POST', '/contratos', TB, ('MP', mp_body, mp_ct)), ('POST', '/contratos', None, ('MP', mp_body, mp_ct))]
    accesibles = 0
    for m, p, t, bd in pruebas:
        if isinstance(bd, tuple):
            s, _, b, ms = http(m, p, raw=bd[1], ctype=bd[2], token=t)
        else:
            s, _, b, ms = http(m, p, bd, t)
        quien = 'empresa B' if t else 'sin token'
        ok = 200 <= s < 300
        accesibles += ok
        L.req_(m, p, s, ms, f'[{quien}] {"ACCESIBLE " if ok else ""}{b.decode(errors="replace")[:60]!r}')
    n_int = db(f"select count(*) from contratos where titulo='Contrato intruso {SUF}'")
    L.log(f'  Contratos "intruso" persistidos en la BD (creados por la empresa B y sin token): {n_int} (el POST sin token responde 500 al auditar, pero el INSERT ya se ejecutó)')
    cuerpo = http('GET', '/auditoria', token=TB)[2]
    ev = {a.get('usuario_id') for a in jl(cuerpo)} if isinstance(jl(cuerpo), list) else set()
    L.log(f'  /auditoria con token de B muestra acciones de otros usuarios: {sorted(x for x in ev if x)[:6]}')
    nombre = jl(http('GET', f'/clientes/{C_BASE}', token=TA)[2]).get('nombre')
    L.log(f'  Nombre actual del cliente de A tras el PUT de B: {nombre!r}')
    L.chk('0 recursos de otra empresa accesibles o modificables', accesibles == 0, f'{accesibles}/{len(pruebas)} accesos permitidos')
    L.done()


# ================================================================== EJECUCIÓN
def func001():
    L = Case('PT-FUNC-001', 'Flujo completo de contrato con documento adjunto', 'RF-5.1, RF-5.2, RF-5.3, RB-3', 'Funcional E2E', 'flujo_contrato')
    st, _, b, ms = http('POST', '/clientes', {'nombre': 'Cliente Prueba SpA', 'correo': f'prueba_{SUF}@atlasfake.com'}, TA)
    cid = jl(b).get('id')
    L.req_('POST', '/clientes', st, ms, f'cliente_id={cid}')
    pdf = b'%PDF-1.4\n' + os.urandom(700_000) + b'\n%%EOF'
    h0 = hashlib.sha256(pdf).hexdigest()
    body, ct = multipart({'cliente_id': cid, 'titulo': 'Servicios 2026', 'descripcion': 'Contrato de prueba', 'fecha_inicio': '2026-01-01', 'fecha_fin': '2026-12-31'}, {'file': ('contrato.pdf', 'application/pdf', pdf)})
    t0 = time.time()
    st, _, b, ms = http('POST', '/contratos', raw=body, ctype=ct, token=TA)
    kid = jl(b).get('id')
    L.req_('POST', '/contratos', st, ms, f'contrato_id={kid} cliente_id={jl(b).get("cliente_id")} (subida contrato.pdf {len(pdf)//1024} KB)')
    L.chk('Contrato creado con 201 y asociado a un único cliente (RB-3)', st == 201 and str(jl(b).get('cliente_id')) == str(cid))
    t1 = time.time()
    s2, h2, b2, ms2 = http('GET', f'/contratos/{kid}/file', token=TA)
    h1 = hashlib.sha256(b2).hexdigest()
    L.req_('GET', f'/contratos/{kid}/file', s2, ms2, f'sha256 original={h0[:16]}… descargado={h1[:16]}…')
    L.chk('El archivo descargado es idéntico al subido (mismo hash sha256)', h0 == h1)
    L.chk('Subida y descarga completadas en ≤ 10 s', (ms + ms2) <= 10000, f'subida {ms} ms + descarga {ms2} ms')
    exe, ct2 = multipart({'cliente_id': cid, 'titulo': 'macro', 'fecha_inicio': '2026-01-01', 'fecha_fin': '2026-12-31'}, {'file': ('macro.exe', 'application/x-msdownload', b'MZ' + os.urandom(20_000))})
    s3, _, b3, ms3 = http('POST', '/contratos', raw=exe, ctype=ct2, token=TA)
    L.req_('POST', '/contratos', s3, ms3, '(archivo macro.exe)')
    L.chk('Solo se aceptan PDF, DOC, PPT, JPG y PNG: macro.exe devuelve 4xx', 400 <= s3 < 500, f'HTTP {s3}: el ejecutable fue aceptado' if s3 == 201 else f'HTTP {s3}')
    big = b'%PDF-1.4\n' + os.urandom(30 * 1024 * 1024)
    gb, ct3 = multipart({'cliente_id': cid, 'titulo': 'grande', 'fecha_inicio': '2026-01-01', 'fecha_fin': '2026-12-31'}, {'file': ('grande.pdf', 'application/pdf', big)})
    s4, _, b4, ms4 = http('POST', '/contratos', raw=gb, ctype=ct3, token=TA, timeout=180)
    L.req_('POST', '/contratos', s4, ms4, '(archivo de 30 MB)')
    L.chk('Existe y se aplica un límite de tamaño de archivo (400/413)', s4 in (400, 413), f'HTTP {s4}: archivo de 30 MB aceptado' if s4 == 201 else f'HTTP {s4}')
    d = db(f'select contract_id, length(document) from documentos_contrato where contract_id={kid}')
    L.log(f'  BD documentos_contrato (contract_id|bytes): {d}')
    L.chk('El documento se guarda en almacenamiento interno y la BD guarda solo la referencia (RF-5.3)', False, f'el binario se guarda dentro de la BD (bytea, {d.split("|")[-1]} bytes)')
    body7, ct7 = multipart({'cliente_id': 99999999, 'titulo': 'huérfano', 'fecha_inicio': '2026-01-01', 'fecha_fin': '2026-12-31'}, {})
    s5, _, b5, ms5 = http('POST', '/contratos', raw=body7, ctype=ct7, token=TA)
    L.req_('POST', '/contratos', s5, ms5, '(cliente inexistente) ' + b5.decode(errors="replace")[:110])
    L.chk('Cliente inexistente → error 4xx con mensaje controlado y sin contrato huérfano', 400 <= s5 < 500, f'HTTP {s5} con err.message expuesto')
    au = db("select accion from auditoria where accion like 'CONTRATOS_CREAR%' order by id desc limit 1")
    L.log(f'  Auditoría: {au}')
    L.chk('Registro de auditoría de la creación del contrato (RF-6.1)', 'CONTRATOS_CREAR' in au)
    L.done()


def perf004():
    L = Case('PT-PERF-004', 'Subida y descarga de documentos ≤ 10 s', 'Criterio de aceptación de RF-5', 'Rendimiento', 'documentos')
    pdf = b'%PDF-1.4\n' + os.urandom(5 * 1024 * 1024) + b'\n%%EOF'
    sub, baj = [], []
    for i in range(10):
        body, ct = multipart({'cliente_id': C_BASE, 'titulo': f'Perf doc {i} {SUF}', 'fecha_inicio': '2026-01-01', 'fecha_fin': '2026-12-31'}, {'file': ('doc5mb.pdf', 'application/pdf', pdf)})
        s1, _, b1, m1 = http('POST', '/contratos', raw=body, ctype=ct, token=TA)
        kid = jl(b1).get('id')
        s2, _, b2, m2 = http('GET', f'/contratos/{kid}/file', token=TA)
        sub.append(m1)
        baj.append(m2)
        L.log(f'  Repetición {i + 1}: subida {m1} ms (HTTP {s1}), descarga {m2} ms (HTTP {s2}, {len(b2) // 1024} KB)')
    L.log(f'  Subida: máx {max(sub)} ms, prom {sum(sub) // len(sub)} ms | Descarga: máx {max(baj)} ms, prom {sum(baj) // len(baj)} ms')
    L.chk('100 % de las operaciones de subida y descarga de un PDF de 5 MB ≤ 10 s', max(sub) <= 10000 and max(baj) <= 10000, f'máximos: subida {max(sub)} ms, descarga {max(baj)} ms (entorno local)')
    L.done()


def main():
    sel = set(sys.argv[1:])
    prev = EV / 'resultados_api.json'
    if sel and prev.exists():
        RESULTS.update(json.loads(prev.read_text(encoding='utf-8')))
    for f in (func001, func002, func003, func004, func005, func006, func007, func008, func009, func010,
              seg001, seg002, seg003, seg004, seg005, seg006, seg007, seg008, seg009, func011, perf004):
        if sel and f.__name__ not in sel:
            continue
        try:
            f()
        except Exception as e:  # noqa
            print('ERROR en', f.__name__, repr(e))
            RESULTS[f.__name__] = {'veredicto': 'Bloqueado', 'error': repr(e)}
    out = EV / 'resultados_api.json'
    out.write_text(json.dumps(RESULTS, ensure_ascii=False, indent=2), encoding='utf-8')
    ap = sum(1 for v in RESULTS.values() if isinstance(v, dict) and v.get('veredicto') == 'Aprobado')
    fa = sum(1 for v in RESULTS.values() if isinstance(v, dict) and v.get('veredicto') == 'Fallido')
    print(f'\nTotal: {ap} aprobados, {fa} fallidos. Resultados en {out}')


if __name__ == '__main__':
    main()
