# EP3 + EP4 — ISY1102 Seguridad y Calidad en el Desarrollo de Software

## Verificando la calidad, seguridad y cumplimiento normativo — Sistema Atlas

| | |
|---|---|
| **Asignatura** | ISY1102 — Seguridad y Calidad en el Desarrollo de Software (Duoc UC) |
| **Caso semestral** | Atlas — plataforma web de gestión de clientes y contratos para pymes |
| **EP3** | Encargo grupal — informe (12 %) |
| **EP4** | Presentación **individual** — defensa de 10 min + 5 min de preguntas (28 %) |
| **Integrantes** | Victor Silva · Jonathan Guerra · Darlette Morales |
| **Carrera / Sección** | Ingeniería en Informática · 003V |
| **Docente** | Cristian Eduardo Medina Cespedes |

> Este repositorio continúa el trabajo de EP1 (plan de pruebas). Los archivos de EP1 y del cuestionario EVA2 están en `99-Archivo_EP1_EVA2/`.

## Estado actual

| Frente | Estado |
|---|---|
| Análisis de rúbricas EP3/EP4 | ✅ `00-Analisis_Rubricas/analisis_rubricas_EP3_EP4.md` |
| Trazabilidad contra el ERS real (42 req. → 30 casos) | ✅ `03-Anexos/Matrices/matriz_trazabilidad.md` (validada: 42/42) |
| Revisión estática manual del código | 🟡 19 hallazgos **preliminares** — `02-Informe/09-Analisis_Estatico/` |
| SonarQube ejecutado (preliminar) | 🟡 SÍ, resultado real: 4 vulnerabilidades (1 Blocker), 25 bugs, 9 code smells — `06-Evidencias/estatico/` y `08-Ejecucion_Pruebas` §2c. Confirma H-08, H-10, H-11. Repetir en Docker del taller |
| Resto de herramientas SAST/DAST (ZAP, Semgrep, k6, Gitleaks, Trivy) | ❌ pendiente (requiere el Docker oficial del taller; no disponible en la máquina de desarrollo) |
| Ejecución de casos de prueba | ❌ 0/30 ejecutados oficialmente · 🟡 8 verificaciones **preliminares** en entorno temporal — `08-Ejecucion_Pruebas/registro_ejecucion.md` §2b (pendientes de reconfirmar en Docker, con evidencia) |
| Feedback del docente a EP1 (86/100) | ✅ recibido: `01-Documentos_Base/Feedback_EP1_docente.md`. Debilidad: IE5 cobertura 6/20; índice no definido |
| Índice definido del informe | ✅ `02-Informe/00-Indice/indice_informe_EP3.md` |
| Sección 7 Cobertura, pertinencia y coherencia reescrita | ✅ `02-Informe/07-Analisis_Cobertura/` (pendiente completar valores de ejecución) |
| Casos detallados (8 completos + 22 fichas) con rutas reales | ✅ `02-Informe/06-Casos_Prueba/` |
| Proyecto Atlas levantado (entorno temporal, sin Docker) | ✅ backend+frontend+BD funcionando con login real; no reemplaza el Docker oficial |
| Guía de herramientas (SonarQube ejecutado; k6, ZAP, Semgrep, Gitleaks, Trivy pendientes) | ✅ `03-Anexos/Herramientas/` |
| Análisis ético-normativo | 🟡 borrador estructural |
| Informe final Word sobre la **plantilla del docente** | 🟡 Generado: `04-Entrega/EP3/EP3_ISY1102_Informe_Atlas.docx` (18 págs.: 5 casos detallados de 30, ejecución preliminar rotulada, análisis estático, ético-normativo y matriz de trazabilidad). Faltan: fecha en portada, nombres completos, ejecución oficial con evidencias y actualizar §5 |
| Diapositivas EP4 | 🟡 guion y **pautas para armar el Prezi** listos en `05-Presentacion_EP4/` (`guion_defensa.md`, `pautas_prezi.md`); presentación sin crear |

## Estructura

```
.
├── 00-Analisis_Rubricas/        Análisis profundo de las pautas EP3 y EP4, brechas y plan
├── 01-Documentos_Base/          ERS, pautas EP1/EP3/EP4 (solo lectura)
├── 02-Informe/                  Secciones del informe
│   ├── 00-Indice/               Índice definido del informe y guía para generarlo
│   ├── 01-Introduccion … 07-Analisis_Cobertura   (base EP1, a ajustar)
│   ├── 08-Ejecucion_Pruebas/    Escala de criticidad + registro de ejecución e incidentes
│   ├── 09-Analisis_Estatico/    Hallazgos H-01…H-19 con archivo:línea
│   └── 10-Analisis_Etico_Normativo/
├── 03-Anexos/Matrices/          Matriz de trazabilidad v2
├── 04-Entrega/                  Plantilla del docente EP3 · EP1_entregado/ · EP3/ (informe final .docx)
├── 05-Presentacion_EP4/         Guion de defensa, preguntas probables y pautas del Prezi
├── 06-Evidencias/               Capturas y logs (nombrar: PT-XXX-000_01.png)
├── 99-Archivo_EP1_EVA2/         README y guía del ciclo anterior
└── CodigoFuenteA/               Código del sistema Atlas (no modificar)
```

## Reglas de trabajo

1. **No modificar** `01-Documentos_Base/` ni `CodigoFuenteA/`.
2. **Solo se registra lo ejecutado.** Un caso sin evidencia está "No ejecutado".
3. Pruebas intrusivas **solo** contra el entorno Docker local de la asignatura, con datos ficticios.
4. Cada incidente: `INC → caso → requerimiento → evidencia → norma`.
5. La defensa es individual: los tres deben dominar todo el flujo.

## Levantar el sistema (en el taller de proyectos)

```bash
cd CodigoFuenteA
docker compose up --build
# Front: http://localhost:3350   API: http://localhost:4450   Swagger: http://localhost:4450/docs
```

## Formato obligatorio del informe

Word o PDF · títulos Arial 12 · cuerpo Arial 11 · interlineado 1,5 · justificado · portada (integrantes, carrera, sección, docente, fecha) · lenguaje formal técnico · capturas legibles · subir a AVA el día de la evaluación.

El informe usa la **plantilla oficial del docente** (`04-Entrega/EP3_ISY1102_Estudiante_Formato_Informe.docx`: portada, índice, secciones 1–5, tabla de caso y escala de criticidad). Se agregaron la sección 6 (análisis ético-normativo, exigido por la pauta EP3) y el Anexo A (matriz de trazabilidad); si el docente no los quiere, se pueden eliminar. La escala de criticidad del informe usa los nombres de la plantilla (CRÍTICO/GRAVE/MODERADO/LEVE) y equivale a Crítica/Alta/Media/Baja del registro interno.

## Siguientes pasos

1. Confirmar las **fechas** de EP3/EP4.
2. En el taller: `docker compose up --build` (guía: `03-Anexos/Herramientas/README.md` §0) y verificar que responde.
3. Repetir el escaneo de SonarQube en el Docker del taller (ya corrió en preliminar, ver `08-Ejecucion_Pruebas` §2c) y capturar su dashboard; luego el resto de herramientas estáticas (ZAP, Semgrep, k6, Gitleaks, Trivy).
4. Ejecutar los 30 casos **uno a uno** en el orden de `08-Ejecucion_Pruebas/registro_ejecucion.md` §5, empezando por reconfirmar con evidencia las 8 verificaciones preliminares de §2b (PT-SEG-001, PT-SEG-002, PT-FUNC-003, PT-FUNC-010) y el SAST de §2c.
5. Con los resultados del taller, actualizar en el informe: §5.1 (resumen), §5.2 (detalle con evidencia, fecha y ejecutor), §5.3 (incidentes), §6.4 (conclusión) y la fecha de la portada; completar nombres completos con ambos apellidos; reemplazar los textos "preliminar" por resultados oficiales; refrescar el índice en Word (clic derecho → Actualizar campo).
6. Armar el Prezi siguiendo `05-Presentacion_EP4/pautas_prezi.md` y ensayar la defensa individual (10 min + 5 min de preguntas).
