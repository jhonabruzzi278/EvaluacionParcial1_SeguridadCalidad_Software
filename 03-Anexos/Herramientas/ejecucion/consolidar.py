#!/usr/bin/env python3
"""Consolida los resultados de ejecución (API, UI, k6, ZAP, DIS) en resultados_ejecucion.json y resumen_ejecucion.md."""
import datetime
import json
import re
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EV = REPO / '06-Evidencias' / 'ejecucion'
R = {}
for f in ('resultados_api.json', 'resultados_ui.json', 'resultados_dis.json'):
    p = EV / f
    if p.exists():
        R.update({k: v for k, v in json.loads(p.read_text(encoding='utf-8')).items() if not k.startswith('_')})
COB = json.loads((EV / 'resultados_api.json').read_text(encoding='utf-8')).get('_cobertura_endpoints')


def limpia_k6(fn):
    t = fn.read_text(encoding='utf-8', errors='replace')
    t = t.replace('\r', '\n')
    i = t.find('█ THRESHOLDS')
    if i < 0:
        i = t.find('THRESHOLDS')
    return t[i:] if i >= 0 else t


def k6(summary, name):
    return json.loads((EV / summary).read_text())['metrics'].get(name, {})


def rec(cid, titulo, req, tipo, slug, crit, notas=None, fecha=None):
    ev = [c for c in crit if c['cumple'] is not None]
    v = 'Aprobado' if ev and all(c['cumple'] for c in ev) else 'Fallido'
    R[cid] = {'titulo': titulo, 'req': req, 'tipo': tipo, 'veredicto': v, 'criterios': crit, 'observaciones': notas or [],
              'evidencia': f'06-Evidencias/ejecucion/{slug}', 'fecha': fecha or datetime.date.today().isoformat()}


# ---------------- PT-PERF-001 (k6 20 VU)
s = 'PT-PERF-001_k6_summary.json'
nom = {'GET /clientes': 'GET /clientes', 'POST /clientes': 'POST /clientes', 'PUT /clientes': 'PUT /clientes', 'DELETE /clientes': 'DELETE /clientes', 'POST /login': 'POST /autenticacion/login'}
crit = []
lineas = []
for k, etq in nom.items():
    m = k6(s, f'http_req_duration{{name:{k}}}')
    p95 = m.get('p(95)')
    crit.append({'texto': f'p(95) < 300 ms en {etq}', 'cumple': p95 is not None and p95 < 300, 'detalle': f'p(95) = {p95:.0f} ms (promedio {m.get("avg", 0):.0f} ms, máx {m.get("max", 0):.0f} ms)'})
    lineas.append(f'{etq:28s} p95 = {p95:8.1f} ms   avg = {m.get("avg", 0):8.1f} ms   max = {m.get("max", 0):8.1f} ms')
fail = k6(s, 'http_req_failed').get('value', 1)
crit.append({'texto': 'Tasa de errores < 1 %', 'cumple': fail < 0.01, 'detalle': f'{fail * 100:.2f} %'})
txt = limpia_k6(EV / 'PT-PERF-001_01_k6.txt')
(EV / 'PT-PERF-001_01_k6.txt').write_text(
    'Caso: PT-PERF-001 — Tiempo de respuesta de operaciones CRUD (NFR-PERF-1)\nHerramienta: k6 v2.3.0, script 03-Anexos/Herramientas/k6/crud_latencia.js\n'
    'Carga: 20 usuarios virtuales durante 2 min (CRUD) + 30 logins secuenciales. Entorno: Docker local.\n\nRESUMEN POR ENDPOINT (p95 frente al umbral de 300 ms):\n  ' + '\n  '.join(lineas) + '\n\nSALIDA DE k6:\n' + txt, encoding='utf-8')
rec('PT-PERF-001', 'Tiempo de respuesta de operaciones CRUD', 'NFR-PERF-1', 'Rendimiento (carga)', 'PT-PERF-001_01_k6.txt', crit,
    ['GET /clientes y el login incluyen un retardo artificial de 4 s en el código (auth.js:17, clients.js); POST, PUT y DELETE cumplen el umbral.'])

# ---------------- PT-PERF-003 (k6 200 VU)
sp = EV / 'PT-PERF-003_k6_summary.json'
if sp.exists():
    s3 = 'PT-PERF-003_k6_summary.json'
    fail = k6(s3, 'http_req_failed').get('value', 1)
    dur = k6(s3, 'http_req_duration')
    reqs = k6(s3, 'http_reqs').get('count', 0)
    try:
        vivo = urllib.request.urlopen('http://localhost:4450/', timeout=5).status == 200
    except Exception:
        vivo = False
    crit = [{'texto': 'Error 5xx / fallos HTTP < 1 %', 'cumple': fail < 0.01, 'detalle': f'{fail * 100:.2f} % de {reqs} peticiones'},
            {'texto': 'El servicio sigue disponible al terminar la prueba (sin caída)', 'cumple': vivo, 'detalle': 'GET / responde 200' if vivo else 'la API no respondió'}]
    txt = limpia_k6(EV / 'PT-PERF-003_01_k6.txt')
    (EV / 'PT-PERF-003_01_k6.txt').write_text(
        'Caso: PT-PERF-003 — 200 usuarios concurrentes (NFR-PERF-3)\nHerramienta: k6 v2.3.0, script 03-Anexos/Herramientas/k6/crud_200vu.js\nCarga: rampa a 200 VUs en 1 min y 4 min sostenidos (5 min). Entorno: Docker local.\n\n'
        f'Peticiones: {reqs}; fallos HTTP: {fail * 100:.2f} %; duración p95 = {dur.get("p(95)", 0):.0f} ms, máx = {dur.get("max", 0):.0f} ms\n\nSALIDA DE k6:\n' + txt, encoding='utf-8')
    rec('PT-PERF-003', '200 usuarios concurrentes', 'NFR-PERF-3', 'Rendimiento (carga / estrés)', 'PT-PERF-003_01_k6.txt', crit,
        [f'Latencia p95 bajo carga: {dur.get("p(95)", 0):.0f} ms (incluye el retardo artificial de 4 s de GET /clientes).'])

# ---------------- ZAP → PT-SEG-005
zap = {}
for nm, f in (('frontend', 'zap/zap_frontend.json'), ('API', 'zap/zap_api.json')):
    p = EV / f
    if p.exists():
        d = json.loads(p.read_text())
        al = [a for site in d.get('site', []) for a in site.get('alerts', [])]
        zap[nm] = [(a['name'], re.sub(r'\D', '', a['riskcode']) or a['riskcode'], a['riskdesc'].split(' ')[0], len(a.get('instances', []))) for a in al]
if zap and 'PT-SEG-005' in R:
    altos = sum(1 for v in zap.values() for a in v if a[2].lower() in ('high', 'alto'))
    medios = [(k, a[0]) for k, v in zap.items() for a in v if a[2].lower() in ('medium', 'medio')]
    tot = sum(len(v) for v in zap.values())
    R['PT-SEG-005']['criterios'].append({'texto': '0 alertas ZAP de riesgo Alto (alertas Medias justificadas)', 'cumple': altos == 0 and not medios,
                                         'detalle': f'ZAP baseline: {altos} alertas altas, {len(medios)} medias, {tot} en total; medias: ' + '; '.join(f'{k}: {n}' for k, n in medios)})
    R['PT-SEG-005']['observaciones'] = [o for o in R['PT-SEG-005']['observaciones'] if 'ZAP' not in o]
    R['PT-SEG-005']['observaciones'].append('OWASP ZAP baseline (zaproxy:stable en Docker) ejecutado contra el frontend (http://localhost:3350) y la API (http://localhost:4450): informes en 06-Evidencias/ejecucion/zap/.')
    # reflejar en el archivo de evidencia
    fn = REPO / R['PT-SEG-005']['evidencia']
    add = ['', 'ZAP baseline (OWASP ZAP stable, Docker) — alertas:'] + [f'  [{k}] {a[0]} (riesgo {a[2]}, {a[3]} instancias)' for k, v in zap.items() for a in v]
    add += [f'  [{"NO CUMPLE" if (altos or medios) else "CUMPLE"}] 0 alertas ZAP de riesgo Alto (alertas Medias justificadas) — {altos} altas, {len(medios)} medias']
    t = fn.read_text(encoding='utf-8')
    if 'ZAP baseline' not in t:
        fn.write_text(t.rstrip('\n') + '\n' + '\n'.join(add) + '\n', encoding='utf-8')
    ev = [c for c in R['PT-SEG-005']['criterios'] if c['cumple'] is not None]
    R['PT-SEG-005']['veredicto'] = 'Aprobado' if all(c['cumple'] for c in ev) else 'Fallido'

# ---------------- No ejecutados
PEND = {
    'PT-USAB-002': ('Flujos claros de registro, creación de empresa y cliente → contratos', 'NFR-USAB-2, NFR-USAB-4', 'Usabilidad', 'requiere tareas con usuarios y observación de tiempos y errores; no se contó con participantes'),
    'PT-USAB-003': ('Ayuda contextual y mensajes de error amigables', 'NFR-USAB-3', 'Usabilidad', 'requiere evaluación heurística con usuarios; solo se observó que la API devuelve mensajes técnicos (ver PT-SEG-006)'),
    'PT-COMP-002': ('Compatibilidad en Chrome, Firefox, Edge y Safari', 'NFR-COMPAT-1', 'Compatibilidad', 'solo Chrome está instalado y Safari no existe en Linux; no se verificó la funcionalidad por navegador'),
}
for cid, (t, rq, tp, motivo) in PEND.items():
    R[cid] = {'titulo': t, 'req': rq, 'tipo': tp, 'veredicto': 'No ejecutado', 'criterios': [], 'observaciones': [motivo], 'evidencia': '—', 'fecha': ''}

ORDEN = ['PT-FUNC-%03d' % i for i in range(1, 12)] + ['PT-SEG-%03d' % i for i in range(1, 10)] + ['PT-PERF-%03d' % i for i in range(1, 5)] + \
        ['PT-USAB-%03d' % i for i in range(1, 4)] + ['PT-COMP-001', 'PT-COMP-002', 'PT-DIS-001']
faltan = [c for c in ORDEN if c not in R]
for c in faltan:
    R[c] = {'titulo': c, 'veredicto': 'No ejecutado', 'criterios': [], 'observaciones': ['no ejecutado'], 'evidencia': '—'}
final = {c: R[c] for c in ORDEN}
final['_cobertura_endpoints'] = COB
(EV / 'resultados_ejecucion.json').write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding='utf-8')

cnt = {}
for c in ORDEN:
    cnt[final[c]['veredicto']] = cnt.get(final[c]['veredicto'], 0) + 1
md = ['# Resumen de ejecución de casos de prueba — Atlas (Docker local)', '',
      f'Generado el {datetime.date.today():%Y-%m-%d}. Entorno: Docker Compose de Atlas (atlas-frontend, atlas-backend, atlas-postgres) en el equipo del equipo.', '',
      f'**{len(ORDEN)} casos: ' + ' · '.join(f'{v} {k.lower()}' for k, v in sorted(cnt.items())) + '**', '',
      '| Caso | Título | Veredicto | Criterios cumplidos | Evidencia |', '|---|---|---|---|---|']
for c in ORDEN:
    r = final[c]
    ev = [x for x in r['criterios'] if x['cumple'] is not None]
    md.append(f'| {c} | {r["titulo"]} | {r["veredicto"]} | {sum(1 for x in ev if x["cumple"])}/{len(ev)} | {r["evidencia"]} |')
(EV / 'resumen_ejecucion.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
print('\n'.join(md[4:6]))
print(cnt, COB)
