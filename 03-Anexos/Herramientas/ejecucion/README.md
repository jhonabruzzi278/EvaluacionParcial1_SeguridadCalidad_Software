# Scripts de ejecución de pruebas

Ejecutaron los casos del plan contra el stack Docker de Atlas el 29-oct-2026. Los resultados quedan en `06-Evidencias/ejecucion/`.

| Script | Casos |
|---|---|
| `ejecutar_api.py [caso ...]` | PT-FUNC-001 a 011, PT-SEG-001 a 009, PT-PERF-004 (API y seguridad; sin argumentos ejecuta todos) |
| `ejecutar_ui.py` | PT-USAB-001, PT-PERF-002, PT-COMP-001 (Chrome headless, axe-core, Lighthouse). Requiere `QA_DIR` (node_modules con `axe-core` y `lighthouse`) y `NODE_BIN` |
| `ejecutar_dis.py` | PT-DIS-001 (reinicia contenedores; requiere `ATLAS_COMPOSE_DIR`) |
| `../k6/crud_latencia.js`, `../k6/crud_200vu.js` | PT-PERF-001, PT-PERF-003 |
| `consolidar.py` | Reúne todo en `resultados_ejecucion.json` y `resumen_ejecucion.md` |

**Levantar Atlas.** El Dockerfile del backend usa `npm ci` y el repositorio no versiona `package-lock.json`: se levantó desde una copia de `CodigoFuenteA` con el lockfile generado (`npm install --package-lock-only`) y la carpeta vacía `BACKEND/uploads/`, sin modificar el código original.

Las pruebas intrusivas se ejecutan solo contra el entorno local, con datos ficticios (Ley 21.459).
