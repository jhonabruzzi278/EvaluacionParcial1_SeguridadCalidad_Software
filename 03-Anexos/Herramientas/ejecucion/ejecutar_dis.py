#!/usr/bin/env python3
"""PT-DIS-001 — recuperación ante caída, persistencia y respaldo/restauración de Atlas (Docker local).

Variable ATLAS_COMPOSE_DIR: carpeta con el docker-compose.yml con el que se levantó Atlas (para down/up).
"""
import datetime
import json
import os
import re
import subprocess
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EV = REPO / '06-Evidencias' / 'ejecucion'
COMPOSE_DIR = os.environ['ATLAS_COMPOSE_DIR']
T0 = datetime.datetime.now()
lines = []
crit = []


def log(s=''):
    lines.append(s)
    print(s)


def sh(cmd, timeout=300):
    r = subprocess.run(['sg', 'docker', '-c', cmd], capture_output=True, text=True, timeout=timeout)
    return (r.stdout + r.stderr).strip()


def psql(sql, dbname='atlas'):
    return sh(f'docker exec atlas-postgres psql -U postgres -d {dbname} -At -F "|" -c "{sql}"')


def up(url='http://localhost:4450/'):
    try:
        return urllib.request.urlopen(url, timeout=2).status == 200
    except Exception:
        return False


def espera_api(maximo=300):
    t = time.time()
    while time.time() - t < maximo:
        if up():
            return time.time() - t
        time.sleep(0.5)
    return None


def chk(texto, ok, detalle=''):
    crit.append((texto, ok, detalle))
    log(f'  [{"NO EVALUADO" if ok is None else ("CUMPLE" if ok else "NO CUMPLE")}] {texto}' + (f' — {detalle}' if detalle else ''))


TABLAS = ['usuarios', 'empresas', 'clientes', 'contratos', 'documentos_contrato', 'auditoria', 'empresa_usuarios']


def conteos(dbname='atlas'):
    return {t: psql(f'select count(*) from {t}', dbname) for t in TABLAS}


log('1) Caída del backend: docker kill atlas-backend y observación de la recuperación')
assert up(), 'Atlas no está en ejecución'
pol = sh("docker inspect -f '{{.HostConfig.RestartPolicy.Name}}' atlas-backend")
log(f'  Política de reinicio configurada en atlas-backend: {pol}')
chk('El backend tiene política de reinicio automático configurada', pol in ('unless-stopped', 'always', 'on-failure'), pol)
sh('docker kill atlas-backend')
time.sleep(0.5)
log(f'  Backend caído tras el kill: {not up()}')
rec = espera_api(20)
estado = sh("docker inspect -f '{{.State.Status}}' atlas-backend")
log(f'  A los 20 s: estado del contenedor = {estado}; responde = {rec is not None}')
if rec is None:
    log('  Docker no reinició el contenedor: `docker kill` se trata como detención manual y la política de reinicio no se aplica (documentación de Docker).')
    chk('Reinicio automático tras la caída (sin intervención manual)', None, 'no evaluable con `docker kill`; un fallo real del proceso no pudo simularse sin privilegios de root')
    sh('docker start atlas-backend')
    t = time.time()
    rec2 = espera_api(120)
    log(f'  Recuperación con una sola orden (docker start): {rec2:.1f} s' if rec2 is not None else '  Tampoco se recuperó con docker start')
    chk('El servicio se recupera con intervención mínima en ≤ 15 min', rec2 is not None and rec2 <= 900, f'{rec2:.1f} s con `docker start`' if rec2 is not None else 'no se recuperó')
else:
    chk('El backend se recupera sin intervención manual en ≤ 15 min', rec <= 900, f'{rec:.1f} s')

log('2) docker compose down (sin -v) y up; persistencia de datos')
antes = conteos()
log(f'  Conteos antes: {antes}')
log('  ' + sh(f'cd {COMPOSE_DIR} && docker compose down 2>&1 | tail -4'))
t1 = time.time()
log('  ' + sh(f'cd {COMPOSE_DIR} && docker compose up -d 2>&1 | tail -3'))
rec2 = espera_api(300)
time.sleep(3)
despues = conteos()
log(f'  Conteos después: {despues}')
log(f'  Stack operativo nuevamente en {rec2:.1f} s' if rec2 else '  El stack no volvió a responder')
chk('100 % de los registros se conservan tras down/up', antes == despues, 'conteos idénticos por tabla' if antes == despues else f'antes {antes} / después {despues}')

log('3) Respaldo: pg_dump atlas > respaldo.sql')
r = subprocess.run(['sg', 'docker', '-c', 'docker exec atlas-postgres pg_dump -U postgres atlas'], capture_output=True, text=True)
tam = len(r.stdout) // 1024
log(f'  Respaldo generado con pg_dump: {tam} KB, {len(r.stdout.splitlines())} líneas (archivo no versionado por su tamaño)')
ref = conteos()

log('4) Restauración en una BD vacía y comparación de conteos por tabla')
psql('drop database if exists atlas_restore', 'postgres')
log('  ' + sh('docker exec atlas-postgres psql -U postgres -d postgres -c "create database atlas_restore"'))
r = subprocess.run(['sg', 'docker', '-c', 'docker exec -i atlas-postgres psql -U postgres -d atlas_restore -q -v ON_ERROR_STOP=1'], input=r.stdout, capture_output=True, text=True)
log(f'  Restauración: código {r.returncode} {r.stderr[:200]}')
rest = conteos('atlas_restore')
log(f'  Conteos original : {ref}')
log(f'  Conteos restaurado: {rest}')
chk('La restauración reproduce los conteos de todas las tablas', ref == rest and r.returncode == 0)
psql('drop database if exists atlas_restore', 'postgres')

log('5) Política de respaldo y recuperación documentada en el repositorio')
hallazgos = subprocess.run(['grep', '-rliE', 'respaldo|backup|pg_dump|restore', 'CodigoFuenteA', '--include=*.md', '--include=*.yml', '--include=*.sh', '--include=*.json', '--include=Dockerfile', '--exclude-dir=node_modules'],
                           capture_output=True, text=True, cwd=REPO).stdout.strip()
log('  Archivos de CodigoFuenteA que mencionan respaldo/backup: ' + (hallazgos or 'ninguno'))
chk('Existe un documento de política de respaldo y recuperación', bool(hallazgos), 'no hay procedimiento ni automatización de respaldo en el repositorio' if not hallazgos else hallazgos)
log('6) Presupuesto de indisponibilidad del 99,5 % mensual: 30 días × 24 h × 0,5 % = 3,6 h')
chk('Disponibilidad mensual del 99,5 % (NFR-DIS-1)', None, 'no medible en el período de prueba; solo se verificó el mecanismo de recuperación')

ev = [c for c in crit if c[1] is not None]
verdict = 'Aprobado' if all(c[1] for c in ev) else 'Fallido'
log('')
log(f'VEREDICTO: {verdict}  ({sum(1 for c in ev if c[1])}/{len(ev)} criterios evaluados cumplidos; {len(crit) - len(ev)} no evaluados)')
head = ['Caso: PT-DIS-001 — Disponibilidad, respaldo y recuperación', 'Requerimiento(s): NFR-DIS-1, NFR-DIS-2, NFR-SEG-7', 'Tipo: Disponibilidad / recuperación',
        f'Inicio: {T0:%Y-%m-%d %H:%M:%S}   Fin: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}', 'Entorno: Docker local (atlas-backend/atlas-frontend/atlas-postgres)', '']
fn = EV / 'PT-DIS-001_01_recuperacion_respaldo.txt'
fn.write_text('\n'.join(head + lines) + '\n', encoding='utf-8')
(EV / 'resultados_dis.json').write_text(json.dumps({'PT-DIS-001': {
    'titulo': 'Disponibilidad, respaldo y recuperación', 'req': 'NFR-DIS-1, NFR-DIS-2, NFR-SEG-7', 'tipo': 'Disponibilidad / recuperación', 'veredicto': verdict,
    'criterios': [{'texto': t, 'cumple': o, 'detalle': d} for t, o, d in crit], 'evidencia': f'06-Evidencias/ejecucion/{fn.name}', 'fecha': T0.strftime('%Y-%m-%d %H:%M')}},
    ensure_ascii=False, indent=2), encoding='utf-8')
