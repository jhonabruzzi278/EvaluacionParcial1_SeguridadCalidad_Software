# Automatización DevSecOps de Atlas

| Archivo | Para qué |
|---|---|
| `.github/workflows/devsecops.yml` | Pipeline en GitHub Actions: secretos → SAST → SCA → entorno efímero → API → DAST → k6 → gate. Cada job tiene su norma en el comentario. |
| `pipeline_local.sh` | El mismo pipeline en el equipo local, **midiendo el tiempo de cada etapa** (evidencia de IE5/IE6). |
| `gate.py` | Criterio de salida: falla si algún caso P1 (los 4 críticos) no está aprobado. |

## Cómo instalarlo en el repo

```bash
REPO="C:/jonathan/seguridad y calidad/repo"
cp -r "C:/jonathan/seguridad y calidad de software/EP5-EP6/automatizacion" "$REPO/"
mkdir -p "$REPO/.github/workflows"
cp "$REPO/automatizacion/.github/workflows/devsecops.yml" "$REPO/.github/workflows/"
```

## Ejecutar localmente (Git Bash, Docker Desktop encendido)

```bash
cd "C:/jonathan/seguridad y calidad/repo/CodigoFuenteA" && docker compose up --build -d
cd .. && bash automatizacion/pipeline_local.sh
# Resultado: automatizacion/salida/reporte_pipeline.md y tiempos_pipeline.csv
```

Notas:
- Si el backend no compila por falta de `package-lock.json`, levantar desde una copia como en EP3 (`03-Anexos/Herramientas/ejecucion/README.md`).
- Que Gitleaks, Semgrep o Trivy terminen con código ≠ 0 **es lo esperado**: significa que encontraron hallazgos. El gate final debe salir **RECHAZADO** mientras existan los 4 críticos.
- Los casos de interfaz (`ejecutar_ui.py`, Lighthouse/axe) y de recuperación (`ejecutar_dis.py`) se corren aparte porque necesitan Chrome y reinician contenedores.

## Qué capturar para el informe y la defensa

1. `reporte_pipeline.md` (tabla de tiempos por etapa) → Tabla de tiempos del informe §5 y lámina 8.
2. La corrida en GitHub Actions con los jobs (captura de pantalla) → Figura del informe §5 y lámina 7.
3. El log del gate con `GATE: RECHAZADO` → evidencia de que el control automático bloquea la liberación.

## CI/CD (`.github/workflows/ci-cd.yml`)

Complementa al pipeline de seguridad (`devsecops.yml`). Corre en cada push/PR a `main`.

| Job | Qué hace |
|---|---|
| `frontend` | `npm ci`, ESLint (informativo: hay 8 errores previos en el código evaluado) y `vite build`. |
| `backend` | `npm ci`, `node --check` de todos los `.js` y validación de `openapi.json`. |
| `imagenes` | Construye las imágenes Docker. **CD:** en push a `main` o tag `v*` las publica en `ghcr.io/<owner>/<repo>-backend` y `-frontend` (tags `sha`, `latest`, versión). En PR solo construye. |
| `humo` | `docker compose up`, espera `:4450/docs` y `:3350`, y apaga. |

Preparación hecha en el repo: lockfiles `package-lock.json` versionados (ya no están en `.gitignore`) para
`npm ci` reproducible; `BACKEND/uploads/.gitkeep` (el Dockerfile hace `COPY uploads/`); Dockerfile del backend
con `--omit=dev` y `EXPOSE 4000`; `.github/dependabot.yml`.

Pendiente de configurar en GitHub: variable `VITE_API_URL` (Settings → Variables) con la URL pública de la API,
y permisos de Actions en modo lectura/escritura de paquetes. El despliegue a un servidor no está incluido
(no hay destino definido). Ojo: la publicación no espera al gate de `devsecops.yml`, que rechaza mientras
existan los 4 críticos intencionales.

## Secretos y rama corregida
El `docker-compose.yml` ya **no trae secretos por defecto**: exige `JWT_SECRET` y `POSTGRES_PASSWORD`.
En local copie `CodigoFuenteA/.env.example` a `.env` y complete ambos (`openssl rand -hex 32`).
Los workflows generan secretos efímeros en cada corrida. La rama `ci-cd/pipeline-corregido` corrige los 4 críticos
(INC-01 a INC-04) y los hallazgos de Gitleaks, Semgrep y Trivy; `ci-cd/pipeline` conserva la versión con los hallazgos.
