# Herramientas de prueba — guía de uso

> Estas herramientas se ejecutaron el 29-oct-2026 sobre el stack Docker de Atlas (SonarQube, Semgrep, Gitleaks, Trivy, ZAP baseline, k6, Lighthouse y axe). Los scripts de las pruebas están en `ejecucion/` y la evidencia en `06-Evidencias/ejecucion/` y `06-Evidencias/estatico/`. Si un comando de esta guía falla al repetirlo, registrar el ajuste en `02-Informe/08-Ejecucion_Pruebas/registro_ejecucion.md`.

## 0. Preparación y reinicio del entorno

```bash
cd CodigoFuenteA
docker compose up --build -d
docker compose logs -f atlas-backend   # esperar "Atlas API escuchando en puerto 4000"
curl -s http://localhost:4450/ ; echo          # {"name":"Atlas","status":"ok"}
curl -s -X POST http://localhost:4450/autenticacion/login -H 'Content-Type: application/json' \
  -d '{"nombre_usuario":"admin","password":"admin"}'    # debe devolver un token
```

**Reiniciar al estado semilla entre tandas de prueba** (varios casos de `06-Casos_Prueba` dan por hecho que la BD parte en el estado de `dump-atlas.sql`):

```bash
docker compose down -v        # -v elimina el volumen de datos
docker compose up --build -d  # init-db.sh vuelve a cargar el dump
```

Si solo se necesita limpiar lo creado por las pruebas sin perder el volumen, usar `docker exec atlas-postgres psql -U postgres -d atlas` y truncar las tablas creadas durante la sesión en lugar de `down -v`.

## 1. SonarQube (SAST principal)

```bash
sudo sysctl -w vm.max_map_count=262144                         # una vez por sesión (Linux)
cd 03-Anexos/Herramientas/sonarqube
docker compose -f docker-compose.sonar.yml up -d               # esperar ~2 min
# Abrir http://localhost:9000  (usuario admin / clave admin → pedirá cambiarla)
# Mi cuenta › Seguridad › Generar token  →  export SONAR_TOKEN=<token>

docker run --rm --network host \
  -e SONAR_HOST_URL=http://localhost:9000 -e SONAR_TOKEN=$SONAR_TOKEN \
  -v "$(realpath ../../../CodigoFuenteA):/usr/src" \
  -v "$(pwd):/opt/sonar:ro" \
  sonarsource/sonar-scanner-cli -Dproject.settings=/opt/sonar/sonar-project.properties
```

Resultados en `http://localhost:9000/dashboard?id=atlas-ep3`. Capturar: *Overview*, *Issues* filtrado por *Vulnerability* y *Security Hotspot*, *Quality Gate*.

**Importante: analizar con las dependencias instaladas.** La regla de promesas sin manejar (S9383) necesita información de tipos. Sobre el código sin `node_modules`, SonarQube 26.10 reporta 10 bugs; con las dependencias instaladas reporta 25 (comprobado). Para no modificar `CodigoFuenteA`, analizar una copia:

```bash
mkdir -p /tmp/cfa && cp -r CodigoFuenteA/BACKEND CodigoFuenteA/FRONTEND /tmp/cfa/
(cd /tmp/cfa/FRONTEND && npm install) && (cd /tmp/cfa/BACKEND && npm install)
# y montar /tmp/cfa en lugar de CodigoFuenteA en el comando de sonar-scanner-cli (-v /tmp/cfa:/usr/src)
```

**Cómo leer el resultado**
- **Vulnerabilidades / Hotspots** → insumo de EP4-IE6; mapear cada una a OWASP, requerimiento y norma (tabla en sección 9).
- **Quality Gate:** en la ejecución preliminar (26.10.0, primer análisis del proyecto) el Quality Gate dio **OK sin condiciones evaluadas** — la condición de cobertura en código nuevo de "Sonar way" no se activó por no existir todavía una línea base de código nuevo (comparación entre análisis). Esto puede diferir en el taller según la versión de la imagen Docker y si ya existe un historial de análisis previo; si en esa ejecución el Quality Gate sí falla por cobertura, es consecuencia directa de la ausencia de pruebas automatizadas en el proyecto (criterio C6, sección 7), no un error de la herramienta. Registrar el resultado real obtenido, sea cual sea.
- **Alcance de la edición Community:** según la documentación del proveedor, el análisis de flujo de datos contaminados (*taint analysis*, que detecta inyecciones rastreando la entrada hasta su uso) se ofrece en ediciones de pago. Verificar en la versión instalada. Por ello se complementa con Semgrep.

## 2. Semgrep (SAST complementario)

```bash
docker run --rm -v "$(realpath CodigoFuenteA):/src:ro" -v "$(pwd)/06-Evidencias:/out" semgrep/semgrep \
  semgrep --config p/owasp-top-ten --config p/nodejs --config p/jwt /src --json -o /out/semgrep.json
```

## 3. Dependencias, secretos e imágenes

```bash
cd CodigoFuenteA/BACKEND  && npm audit --omit=dev
cd ../FRONTEND            && npm audit --omit=dev
docker run --rm -v "$(realpath ../..):/repo" zricethezav/gitleaks detect --source /repo --no-git
trivy image <imagen-backend>       # tras docker compose build
docker run --rm -i hadolint/hadolint < CodigoFuenteA/BACKEND/Dockerfile
```

## 4. OWASP ZAP (DAST, solo contra localhost)

```bash
docker run --rm --network host -v "$(pwd):/zap/wrk" ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://localhost:4450 -r zap_api.html
docker run --rm --network host -v "$(pwd):/zap/wrk" ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://localhost:3350 -r zap_front.html
```

## 5. k6 (rendimiento)

```bash
k6 run -e API=http://localhost:4450 03-Anexos/Herramientas/k6/crud_latencia.js
# O con Docker:  docker run --rm -i --network host grafana/k6 run -e API=http://localhost:4450 - < crud_latencia.js
```

## 6. Newman (API desde OpenAPI)

Importar `http://localhost:4450/openapi.json` en Postman, generar la colección, agregar pruebas básicas de estado y esquema, exportar y ejecutar con `newman run coleccion.json`.

## 7. Casos de API caso por caso

Cada uno de los 30 casos de `02-Informe/06-Casos_Prueba/casos_prueba.md` trae su propio procedimiento y, en los 8 casos detallados, los comandos `curl` ya escritos (sección 6.2 a 6.9 de ese documento: flujo de contrato, hashing de contraseñas, RBAC, inyección/XSS/cabeceras, latencia CRUD, accesibilidad, responsividad y disponibilidad). Ejecutarlos **uno a la vez**, registrando cada resultado en `02-Informe/08-Ejecucion_Pruebas/registro_ejecucion.md` §3 antes de pasar al siguiente, en el orden de prioridad de ese documento §5. No encadenar varios casos de seguridad en un único script: cada verificación debe quedar documentada por separado, con su propia evidencia.

## 8. Límite ético

Todo se ejecuta **solo** contra el stack local de la asignatura (Ley 21.459). Nunca contra redes o sistemas de terceros.
