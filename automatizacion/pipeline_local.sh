#!/usr/bin/env bash
# Ejecuta el pipeline DevSecOps de Atlas en el equipo local y MIDE el tiempo de cada etapa.
# Salida: automatizacion/salida/tiempos_pipeline.csv y reporte_pipeline.md (evidencia para IE5/IE6).
#
# Uso (desde la raíz del repo, con Docker corriendo y Atlas levantado en :3350/:4450):
#   bash automatizacion/pipeline_local.sh
# Solo ataca el entorno local con datos ficticios (Ley 21.459).
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$REPO/automatizacion/salida"; mkdir -p "$OUT"
CSV="$OUT/tiempos_pipeline.csv"; echo "etapa,control,norma,segundos,codigo_salida" > "$CSV"
API="${API:-http://localhost:4450}"; WEB="${WEB:-http://localhost:3350}"
PY="${PY:-python}"   # en Linux: PY=python3
# En Git Bash (Windows) evita que Docker reciba rutas convertidas
export MSYS_NO_PATHCONV=1
# Ruta nativa para Python en Windows (Git Bash); en Linux queda igual
PYREPO="$REPO"; command -v cygpath >/dev/null && PYREPO="$(cygpath -w "$REPO")"

etapa () {  # etapa "<nombre>" "<control>" "<norma>" comando...
  local nombre="$1" control="$2" norma="$3"; shift 3
  echo "==> $nombre"
  local t0=$(date +%s)
  "$@" > "$OUT/${nombre// /_}.log" 2>&1; local rc=$?
  local dt=$(( $(date +%s) - t0 ))
  echo "$nombre,$control,$norma,$dt,$rc" >> "$CSV"
  echo "    $dt s (código $rc)"
}

curl -sf "$API/" >/dev/null || { echo "Atlas no responde en $API. Levantarlo con: cd CodigoFuenteA && docker compose up -d"; exit 1; }

etapa "1 Secretos"  "Gitleaks"            "OWASP A05; Ley 19.628 art.11" \
  docker run --rm -v "$REPO:/repo" zricethezav/gitleaks:latest detect --source /repo/CodigoFuenteA --no-git \
  --report-format json --report-path /repo/automatizacion/salida/gitleaks.json
etapa "2 SAST"      "Semgrep"             "OWASP Top 10; ISO 27001 A.8.28" \
  docker run --rm -v "$REPO:/src" semgrep/semgrep semgrep --config p/owasp-top-ten --config p/nodejs --config p/jwt \
  --json -o /src/automatizacion/salida/semgrep.json /src/CodigoFuenteA
etapa "3 SCA"       "Trivy"               "OWASP A06; ISO 27001 A.8.8" \
  docker run --rm -v "$REPO:/src" aquasec/trivy:latest fs --scanners vuln,misconfig --severity HIGH,CRITICAL \
  --format json -o /src/automatizacion/salida/trivy_fs.json /src/CodigoFuenteA
etapa "4 API"       "ejecutar_api.py"     "Ley 19.628; OWASP A01/A02/A07" \
  "$PY" "$PYREPO/03-Anexos/Herramientas/ejecucion/ejecutar_api.py"
etapa "5 DAST"      "OWASP ZAP baseline"  "OWASP A05" \
  docker run --rm --network host -v "$OUT:/zap/wrk" zaproxy/zap-stable zap-baseline.py -t "$WEB" \
  -J zap_frontend.json -r zap_frontend.html -I
etapa "6 Carga"     "k6"                  "ISO 25010 eficiencia; NFR-PERF-1" \
  docker run --rm --network host -v "$REPO/03-Anexos/Herramientas/k6:/k6" grafana/k6 run -e API="$API" \
  --summary-export /k6/k6_summary.json /k6/crud_latencia.js
etapa "7 Consolidar" "consolidar.py"      "ISO 27001 A.8.15 (registros)" \
  "$PY" "$PYREPO/03-Anexos/Herramientas/ejecucion/consolidar.py"
etapa "8 Gate"      "gate.py"             "Criterio de salida: sin críticos abiertos" \
  "$PY" "$PYREPO/automatizacion/gate.py" "$PYREPO/06-Evidencias/ejecucion/resultados_ejecucion.json"

TOTAL=$(awk -F, 'NR>1{s+=$4} END{print s}' "$CSV")
{
  echo "# Reporte del pipeline local — $(date '+%Y-%m-%d %H:%M')"
  echo; echo "| Etapa | Control | Norma | Segundos | Código |"; echo "|---|---|---|---|---|"
  awk -F, 'NR>1{printf "| %s | %s | %s | %s | %s |\n",$1,$2,$3,$4,$5}' "$CSV"
  echo; echo "**Tiempo total: ${TOTAL} s (≈ $((TOTAL/60)) min).** Código ≠ 0 en un escáner = encontró hallazgos (esperado en Atlas)."
  echo; echo '## Gate'; echo '```'; cat "$OUT/8_Gate.log"; echo '```'
} > "$OUT/reporte_pipeline.md"
echo; echo "Listo: $OUT/reporte_pipeline.md  (total ${TOTAL} s)"
