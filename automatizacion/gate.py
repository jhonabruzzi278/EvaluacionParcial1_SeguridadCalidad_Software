#!/usr/bin/env python3
"""Gate de liberación de Atlas (criterio de salida del plan de pruebas).

Lee resultados_ejecucion.json (generado por consolidar.py) y falla (exit 1) si algún caso
que cubre un riesgo crítico (P1) no está Aprobado. Imprime un resumen para el log del pipeline.

Uso: python3 gate.py 06-Evidencias/ejecucion/resultados_ejecucion.json
"""
import json
import sys
from pathlib import Path

# Casos P1: si fallan, el incidente asociado es CRÍTICO y bloquea la liberación.
P1 = {
    'PT-SEG-001': 'INC-02 contraseñas sin hash (NFR-SEG-2, Ley 19.628 art. 11)',
    'PT-SEG-002': 'INC-01 sin control de rol en el backend (NFR-SEG-4, RB-4, OWASP A01)',
    'PT-SEG-008': 'INC-04 secreto JWT por defecto (NFR-SEG-9, OWASP A07)',
    'PT-SEG-009': 'INC-03 sin aislamiento entre empresas (RB-2, OWASP A01)',
}


def main(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    casos = {k: v for k, v in data.items() if k.startswith('PT-')}
    total = len(casos)
    aprob = sum(1 for c in casos.values() if c.get('veredicto') == 'Aprobado')
    fall = sum(1 for c in casos.values() if c.get('veredicto') == 'Fallido')
    print(f'Casos: {total} · aprobados {aprob} · fallidos {fall}')

    bloqueantes = [(cid, desc) for cid, desc in P1.items()
                   if casos.get(cid, {}).get('veredicto') != 'Aprobado']
    for cid, desc in bloqueantes:
        print(f'  BLOQUEA  {cid}: {desc} -> {casos.get(cid, {}).get("veredicto", "sin resultado")}')
    if bloqueantes:
        print(f'GATE: RECHAZADO ({len(bloqueantes)} riesgo(s) crítico(s) abierto(s)). No liberar.')
        return 1
    print('GATE: APROBADO (sin riesgos críticos abiertos).')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '06-Evidencias/ejecucion/resultados_ejecucion.json'))
