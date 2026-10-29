#!/usr/bin/env python3
"""Pruebas de interfaz de Atlas con Chrome headless: accesibilidad (axe-core + Lighthouse) y responsividad.

Casos: PT-USAB-001, PT-COMP-001, PT-PERF-002.
Requiere: Atlas en http://localhost:3350 / :4450, google-chrome, y un directorio con node_modules de axe-core y lighthouse
(variable QA_DIR) y NODE_BIN con el binario de node.
Salida: 06-Evidencias/ejecucion/<CASO>_01_*.txt, capturas PT-COMP-001_*.png, informes Lighthouse y resultados_ui.json.
"""
import asyncio
import base64
import datetime
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import websockets

REPO = Path(__file__).resolve().parents[3]
EV = REPO / '06-Evidencias' / 'ejecucion'
EV.mkdir(parents=True, exist_ok=True)
WEB, API = 'http://localhost:3350', 'http://localhost:4450'
QA = Path(os.environ['QA_DIR'])
NODE_BIN = os.environ['NODE_BIN']
PORT = 9444
RESULTS = {}


class Case:
    def __init__(self, cid, titulo, req, tipo, slug):
        self.cid, self.titulo, self.req, self.tipo, self.slug = cid, titulo, req, tipo, slug
        self.lines, self.crit, self.t0 = [], [], datetime.datetime.now()

    def log(self, s=''):
        self.lines.append(s)

    def chk(self, texto, ok, detalle=''):
        self.crit.append((texto, ok, detalle))
        etq = 'NO EVALUADO' if ok is None else ('CUMPLE' if ok else 'NO CUMPLE')
        self.log(f'  [{etq}] {texto}' + (f' — {detalle}' if detalle else ''))

    def done(self):
        ev = [c for c in self.crit if c[1] is not None]
        verdict = 'Aprobado' if ev and all(c[1] for c in ev) else 'Fallido'
        self.log('')
        self.log(f'VEREDICTO: {verdict}  ({sum(1 for c in ev if c[1])}/{len(ev)} criterios evaluados cumplidos; {len(self.crit) - len(ev)} no evaluados)')
        head = [f'Caso: {self.cid} — {self.titulo}', f'Requerimiento(s): {self.req}', f'Tipo: {self.tipo}',
                f'Inicio: {self.t0:%Y-%m-%d %H:%M:%S}   Fin: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}',
                f'Entorno: Docker local (frontend {WEB}), Chrome headless {CHROME_VER}', '']
        fn = EV / f'{self.cid}_01_{self.slug}.txt'
        fn.write_text('\n'.join(head + self.lines) + '\n', encoding='utf-8')
        RESULTS[self.cid] = {'titulo': self.titulo, 'req': self.req, 'tipo': self.tipo, 'veredicto': verdict,
                             'criterios': [{'texto': t, 'cumple': o, 'detalle': d} for t, o, d in self.crit],
                             'evidencia': f'06-Evidencias/ejecucion/{fn.name}', 'fecha': self.t0.strftime('%Y-%m-%d %H:%M')}
        print(f'{self.cid:12s} {verdict}')


def api_login():
    req = urllib.request.Request(API + '/autenticacion/login', data=json.dumps({'nombre_usuario': 'admin', 'password': 'admin'}).encode(), headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=60))['token']


def jwt_payload(tok):
    p = tok.split('.')[1]
    return json.loads(base64.urlsafe_b64decode(p + '=' * (-len(p) % 4)))


def contrato_id():
    req = urllib.request.Request(API + '/contratos', headers={'Authorization': f'Bearer {TOKEN}'})
    d = json.load(urllib.request.urlopen(req, timeout=60))
    return d[0]['id'] if d else 1


TOKEN = api_login()
USER = {'nombre_usuario': 'admin', **jwt_payload(TOKEN)}
CHROME_VER = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True).stdout.strip()
chrome = subprocess.Popen(['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu', f'--remote-debugging-port={PORT}',
                           '--user-data-dir=/tmp/atlas-ui-profile', 'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(4)
tabs = json.load(urllib.request.urlopen(f'http://localhost:{PORT}/json'))
WS = [t for t in tabs if t['type'] == 'page'][0]['webSocketDebuggerUrl']
AXE = (QA / 'node_modules/axe-core/axe.min.js').read_text()


async def run():
    global KID
    KID = contrato_id()
    async with websockets.connect(WS, max_size=None) as ws:
        n = 0

        async def call(method, **params):
            nonlocal n
            n += 1
            i = n
            await ws.send(json.dumps({'id': i, 'method': method, 'params': params}))
            while True:
                m = json.loads(await ws.recv())
                if m.get('id') == i:
                    return m.get('result', m)

        async def ev(expr, await_=True):
            r = await call('Runtime.evaluate', expression=expr, awaitPromise=await_, returnByValue=True)
            return r.get('result', {}).get('value')

        async def goto(path, vp=(1366, 768), mobile=False, wait=4):
            await call('Emulation.setDeviceMetricsOverride', width=vp[0], height=vp[1], deviceScaleFactor=1, mobile=mobile)
            await call('Page.navigate', url=WEB + path)
            await asyncio.sleep(wait)

        await call('Page.enable')
        await call('Runtime.enable')
        # sesión: se inyecta el token del usuario administrador en localStorage
        await goto('/login')
        await ev(f"localStorage.setItem('token','{TOKEN}');localStorage.setItem('user',{json.dumps(json.dumps(USER))});localStorage.setItem('role','administrador');true", False)

        pages = ['/login', '/registro', '/home', '/clientes', '/contratos']

        # ------------------------------------------------ PT-USAB-001 (axe + tamaños)
        L = Case('PT-USAB-001', 'Accesibilidad para adultos mayores (WCAG 2.1 AA)', 'NFR-USAB-1; §3.1.1 ERS', 'Usabilidad / accesibilidad', 'axe_lighthouse')
        L.log('1) axe-core 4.x (WCAG 2.0/2.1 A y AA) sobre 5 URLs, viewport 1366x768, sesión de administrador')
        graves = 0
        contraste = 0
        fuente = []
        chicos = {}
        for p in pages:
            if p in ('/login', '/registro'):
                await ev("localStorage.removeItem('token');localStorage.removeItem('user');true", False)
            else:
                await ev(f"localStorage.setItem('token','{TOKEN}');localStorage.setItem('user',{json.dumps(json.dumps(USER))});localStorage.setItem('role','administrador');true", False)
            await goto(p, wait=5 if p in ('/clientes', '/contratos', '/home') else 3)
            await ev(AXE, False)
            r = await ev("""axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}).then(x=>JSON.stringify({v:x.violations.map(v=>({id:v.id,impact:v.impact,n:v.nodes.length,help:v.help})),url:location.pathname}))""")
            d = json.loads(r)
            fz = await ev("getComputedStyle(document.body).fontSize")
            peq = await ev("[...document.querySelectorAll('a,button,input,select,textarea,[role=button]')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&(r.width<44||r.height<44)}).length")
            tot = await ev("[...document.querySelectorAll('a,button,input,select,textarea,[role=button]')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0}).length")
            fuente.append(float(str(fz).replace('px', '')))
            chicos[p] = (peq, tot)
            crit = [v for v in d['v'] if v['impact'] in ('critical', 'serious')]
            graves += sum(v['n'] for v in crit)
            contraste += sum(v['n'] for v in d['v'] if v['id'] == 'color-contrast')
            L.log(f'  {p}  ->  url real: {d["url"]}  | violaciones: {len(d["v"])} (críticas/serias: {len(crit)}; nodos afectados {sum(v["n"] for v in crit)})  | fuente base {fz}  | objetivos < 44 px: {peq}/{tot}')
            for v in d['v']:
                L.log(f'      - [{v["impact"]}] {v["id"]} ({v["n"]} nodos): {v["help"]}')
        L.log('2) Lighthouse (categoría Accesibilidad, móvil por defecto) con la misma sesión')
        lh = {}
        for p in pages:
            out = EV / f'PT-USAB-001_lighthouse{p.strip("/").replace("/", "_") or "root"}.json'
            cmd = [f'{NODE_BIN}/node', str(QA / 'node_modules/.bin/lighthouse'), WEB + p, f'--port={PORT}', '--disable-storage-reset', '--only-categories=accessibility,performance',
                   '--output=json', f'--output-path={out}', '--quiet']
            r = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, 'PATH': NODE_BIN + ':' + os.environ['PATH']}, timeout=240)
            try:
                j = json.loads(out.read_text())
                acc = round(j['categories']['accessibility']['score'] * 100)
                perf = round(j['categories']['performance']['score'] * 100)
                lcp = j['audits']['largest-contentful-paint']['numericValue'] / 1000
                url_final = j['finalDisplayedUrl']
                lh[p] = (acc, perf, lcp, url_final)
                L.log(f'  {p}: accesibilidad {acc}/100, rendimiento {perf}/100, LCP {lcp:.2f} s (URL final: {url_final})')
            except Exception as e:  # noqa
                lh[p] = None
                L.log(f'  {p}: Lighthouse falló: {r.stderr[:200]} {e}')
        ok_lh = [v for v in lh.values() if v]
        L.chk('Lighthouse Accesibilidad ≥ 90 en las 5 URLs', bool(ok_lh) and all(v[0] >= 90 for v in ok_lh), ', '.join(f'{p}={v[0] if v else "s/d"}' for p, v in lh.items()))
        L.chk('0 incidencias critical/serious en axe', graves == 0, f'{graves} nodos con impacto crítico o serio')
        L.chk('Contraste de texto ≥ 4,5:1 (regla color-contrast de axe)', contraste == 0, f'{contraste} nodos con contraste insuficiente')
        L.chk('Tamaño de fuente base ≥ 12 px (mínimo del ERS)', all(f >= 12 for f in fuente), f'fuente base por página: {fuente} (el ERS pide mayor legibilidad para adultos mayores: se recomienda ≥ 16 px)')
        pq = sum(a for a, b in chicos.values())
        pt = sum(b for a, b in chicos.values())
        L.chk('Objetivos interactivos ≥ 44×44 px', pq == 0, f'{pq} de {pt} elementos interactivos miden menos de 44 px en alguna dimensión')
        L.chk('SUS promedio ≥ 70 y tareas sin bloqueos con adultos mayores', None, 'requiere participantes reales (no disponibles); se documenta como limitación')
        L.done()
        USAB_LH = lh

        # ------------------------------------------------ PT-PERF-002 (LCP móvil)
        L2 = Case('PT-PERF-002', 'Carga de la página principal en conexión móvil', 'NFR-PERF-2', 'Rendimiento (frontend)', 'lighthouse_lcp')
        L2.log('Lighthouse móvil con red 4G simulada sobre la página de ingreso y el inicio autenticado')
        vals = []
        for p in ('/login', '/home'):
            v = USAB_LH.get(p)
            if v:
                vals.append(v[2])
                L2.log(f'  {p}: LCP {v[2]:.2f} s, puntaje de rendimiento {v[1]}/100')
        L2.chk('LCP de la página principal < 2 s', bool(vals) and all(x < 2 for x in vals), ' · '.join(f'{x:.2f} s' for x in vals))
        L2.done()

        # ------------------------------------------------ PT-COMP-001 (responsividad)
        L3 = Case('PT-COMP-001', 'Responsividad en móviles y tablets', 'NFR-COMPAT-2', 'Compatibilidad (responsiva)', 'responsivo')
        vps = [('360x780', (360, 780), True), ('390x844', (390, 844), True), ('820x1180', (820, 1180), True), ('1366x768', (1366, 768), False)]
        pgs = ['/login', '/registro', '/home', '/clientes', '/clientes/nuevo', '/contratos', f'/contratos/{KID}']
        desb = 0
        peq_m = 0
        menu_fijo = []
        L3.log('Emulación de dispositivo en Chrome (DevTools). Medición: scrollWidth > innerWidth = desborde horizontal.')
        for nombre, vp, mob in vps:
            L3.log(f'Resolución {nombre}:')
            for p in pgs:
                if p in ('/login', '/registro'):
                    await ev("localStorage.removeItem('token');localStorage.removeItem('user');true", False)
                else:
                    await ev(f"localStorage.setItem('token','{TOKEN}');localStorage.setItem('user',{json.dumps(json.dumps(USER))});localStorage.setItem('role','administrador');true", False)
                await goto(p, vp, mob, wait=5 if p not in ('/login', '/registro') else 2.5)
                ov = await ev("document.documentElement.scrollWidth - window.innerWidth")
                peq = await ev("[...document.querySelectorAll('a,button,input,select,textarea,[role=button]')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&(r.width<44||r.height<44)}).length")
                fuera = await ev("[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&r.right>window.innerWidth+2}).length")
                side = await ev("(()=>{const e=[...document.querySelectorAll('button,a,div,span,p')].find(x=>x.children.length<3&&x.textContent.trim()==='Cerrar Sesión');if(!e)return 0;let a=e;while(a&&a.getBoundingClientRect().height<innerHeight*0.8)a=a.parentElement;return a?Math.round(a.getBoundingClientRect().width):0})()")
                if (ov and ov > 1) or (fuera and fuera > 0):
                    desb += 1
                if mob and p not in ('/login', '/registro') and side and side > 0.4 * vp[0]:
                    menu_fijo.append(f'{nombre} {p}: menú de {side} px sobre {vp[0]} px de ancho')
                if mob:
                    peq_m += peq or 0
                L3.log(f'  {p:22s} scroll horizontal: {max(ov or 0, 0)} px | elementos fuera del viewport (recortados): {fuera} | ancho del menú lateral: {side} px | objetivos < 44 px: {peq}')
                if p in ('/login', '/clientes', '/contratos') or p.startswith('/contratos/'):
                    shot = await call('Page.captureScreenshot', format='png')
                    nm = f'PT-COMP-001_{nombre}_{p.strip("/").replace("/", "-") or "root"}.png'
                    (EV / nm).write_bytes(base64.b64decode(shot['data']))
        L3.chk('0 desbordes horizontales ni contenido recortado en las 4 resoluciones', desb == 0, f'{desb} de {len(vps) * len(pgs)} combinaciones página/resolución con contenido fuera del viewport')
        L3.chk('El menú de navegación se adapta al ancho móvil (no ocupa más del 40 % del ancho)', not menu_fijo, f'{len(menu_fijo)} casos; p. ej. {menu_fijo[0] if menu_fijo else ""}')
        L3.chk('Elementos táctiles ≥ 44×44 px (resoluciones móviles)', peq_m == 0, f'{peq_m} elementos < 44 px sumados en las resoluciones móviles')
        L3.chk('Flujos críticos (login, crear cliente, ver contrato) completables en móvil', None, 'se verificó la presentación de las pantallas; la ejecución completa de los flujos con interacción táctil no se automatizó')
        L3.done()
    chrome.terminate()


asyncio.run(run())
(EV / 'resultados_ui.json').write_text(json.dumps(RESULTS, ensure_ascii=False, indent=2), encoding='utf-8')
