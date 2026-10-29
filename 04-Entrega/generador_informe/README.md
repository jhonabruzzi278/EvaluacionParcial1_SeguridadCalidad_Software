# Generador del informe EP3

Reconstruye `04-Entrega/EP3/EP3_ISY1102_Informe_Atlas.docx` sobre la plantilla del docente
(`04-Entrega/EP3_ISY1102_Estudiante_Formato_Informe.docx`) con los datos del repositorio
(matriz de trazabilidad, exportaciones de SonarQube en `06-Evidencias/estatico/` y resultados de ejecución en `06-Evidencias/ejecucion/`).

```bash
bash 04-Entrega/generador_informe/make.sh
```

- El texto del informe está en `build_informe.py` (bloque `contenido`). La lista `KEEP` define los casos que presenta el informe (hoy 10); el alcance de requerimientos, la cobertura y la matriz se calculan a partir de ella y de `03-Anexos/Matrices/matriz_trazabilidad.md`.
- Los resultados de cada caso se leen de `06-Evidencias/ejecucion/resultados_ejecucion.json` (generado por `03-Anexos/Herramientas/ejecucion/consolidar.py`); los incidentes (`INC`) y los hallazgos H-xx se editan en `build_informe.py`.
- `make.sh` también deja `EP3_ISY1102_Informe_Atlas_vista_previa.pdf` junto al .docx: es una copia para revisar, renderizada con LibreOffice (Liberation Sans en lugar de Arial). Para entregar, usar el .docx o exportar a PDF desde Word.
- `make.sh` hace tres pasadas para que el índice y el índice de tablas tengan los números de página correctos.
- Alternativa: editar el .docx directamente en Word y actualizar los índices (clic derecho → Actualizar campo).
