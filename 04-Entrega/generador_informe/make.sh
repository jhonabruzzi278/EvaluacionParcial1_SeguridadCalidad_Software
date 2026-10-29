#!/usr/bin/env bash
# Regenera 04-Entrega/EP3/EP3_ISY1102_Informe_Atlas.docx (y una vista previa en PDF) desde la plantilla del docente y los datos del repo.
# Requiere: python3 + lxml, LibreOffice (soffice) y poppler (pdftotext, pdfinfo).
set -euo pipefail
cd "$(dirname "$0")"
TMP="${TMPDIR:-/tmp}/atlas_informe"; mkdir -p "$TMP"; echo '{}' > "$TMP/pages.json"
OUT=../EP3/EP3_ISY1102_Informe_Atlas.docx
for i in 1 2 3; do
  python3 build_informe.py "$(cat "$TMP/pages.json")" >/dev/null
  cp "$OUT" "$TMP/informe.docx"
  (cd "$TMP" && soffice --headless --convert-to pdf informe.docx >/dev/null 2>&1)
  python3 paginar.py "$TMP/informe.pdf"
done
cp "$TMP/informe.pdf" ../EP3/EP3_ISY1102_Informe_Atlas_vista_previa.pdf
echo "Listo: $OUT (y vista previa en PDF)"
