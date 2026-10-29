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
| Trazabilidad contra el ERS real (42 req. → plan completo de 30 casos) | ✅ `03-Anexos/Matrices/matriz_trazabilidad.md` (validada: 42/42). El informe presenta un **subconjunto priorizado de 10 casos** (alcance: 16 de los 42 requerimientos; ver `04-Entrega/EP3/`) |
| Revisión estática manual del código | ✅ 19 hallazgos con archivo:línea, todos contrastados con la ejecución — `02-Informe/09-Analisis_Estatico/` e informe §5.4 |
| SonarQube ejecutado en Docker | ✅ Resultado real (29-oct-2026, imagen `sonarqube:community` 26.10.0, copia con dependencias): 4 vulnerabilidades (1 Blocker), 25 bugs, 9 code smells — `06-Evidencias/estatico/`, `08-Ejecucion_Pruebas` §2c y Anexo B del informe. Confirma H-08, H-10, H-11 |
| Semgrep, Gitleaks, Trivy, OWASP ZAP, k6, Lighthouse/axe | ✅ Ejecutadas en Docker (29-oct-2026); resultados en `06-Evidencias/estatico/herramientas/` y `06-Evidencias/ejecucion/` |
| Ejecución de casos de prueba | ✅ **27 de los 30 casos del plan completo ejecutados** en el Docker local de Atlas (7 aprobados, 20 fallidos; 3 no ejecutados: USAB-002, USAB-003, COMP-002). **El informe presenta 10 casos priorizados** (FUNC-001, 002, 008, 010; SEG-001, 002, 008, 009; PERF-001; USAB-001): 1 aprobado y 9 fallidos, 12 incidentes (4 críticos). Evidencia por caso en `06-Evidencias/ejecucion/`, resumen en `resumen_ejecucion.md`; scripts en `03-Anexos/Herramientas/ejecucion/` |
| Feedback del docente a EP1 (86/100) | ✅ recibido: `01-Documentos_Base/Feedback_EP1_docente.md`. Debilidad: IE5 cobertura 6/20; índice no definido |
| Índice definido del informe | ✅ `02-Informe/00-Indice/indice_informe_EP3.md` |
| Sección 7 Cobertura, pertinencia y coherencia reescrita | ✅ `02-Informe/07-Analisis_Cobertura/` (plan completo de 30 casos; el informe final usa el análisis del alcance de 10 casos, §4.2) |
| Casos detallados del plan completo (8 completos + 22 fichas) con rutas reales | ✅ `02-Informe/06-Casos_Prueba/` (el informe detalla 10 casos priorizados) |
| Proyecto Atlas levantado con Docker Compose | ✅ atlas-frontend :3350, atlas-backend :4450, atlas-postgres y SonarQube :9000 en el equipo local (se construye desde una copia con `package-lock.json`; ver `03-Anexos/Herramientas/ejecucion/README.md`) |
| Guía de herramientas (todas ejecutadas) | ✅ `03-Anexos/Herramientas/` |
| Análisis ético-normativo | ✅ sección 6 del informe (resultados frente a normativa, ética, recomendaciones y conclusión) |
| Informe final Word sobre la **plantilla del docente** | ✅ Generado con resultados reales: `04-Entrega/EP3/EP3_ISY1102_Informe_Atlas.docx` (30 págs.; auditado contra la pauta en `00-Analisis_Rubricas/cumplimiento_informe_EP3.md`: alcance, objetivos, cronograma, 11 tipos de prueba clasificados, 10 casos detallados, análisis de cobertura/pertinencia/coherencia, ejecución con resultados reales, ético-normativo, matriz y capturas de SonarQube). Regenerable con `04-Entrega/generador_informe/make.sh`. Falta: confirmar la fecha de portada (29-oct-2026) y los apellidos completos |
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

## Levantar el sistema

```bash
cd CodigoFuenteA
docker compose up --build
# Front: http://localhost:3350   API: http://localhost:4450   Swagger: http://localhost:4450/docs
```

## Formato obligatorio del informe

Word o PDF · títulos Arial 12 · cuerpo Arial 11 · interlineado 1,5 · justificado · portada (integrantes, carrera, sección, docente, fecha) · lenguaje formal técnico · capturas legibles · subir a AVA el día de la evaluación.

El informe usa la **plantilla oficial del docente** (`04-Entrega/EP3_ISY1102_Estudiante_Formato_Informe.docx`: portada, índice, secciones 1–5, tabla de caso y escala de criticidad). Se agregaron lo que la pauta exige y la plantilla no trae: alcance, objetivos y cronograma (IE7), análisis de cobertura, pertinencia y coherencia (IE9), la sección 6 (análisis ético-normativo) y los anexos A (matriz) y B (SonarQube); si el docente no los quiere, se pueden eliminar. La escala de criticidad del informe usa los nombres de la plantilla (CRÍTICO/GRAVE/MODERADO/LEVE) y equivale a Crítica/Alta/Media/Baja del registro interno.

## Siguientes pasos

1. Completar en la portada del informe la **fecha de entrega** y los **apellidos completos** de los integrantes; abrir el .docx en Word y actualizar los índices (clic derecho → Actualizar campo).
2. Revisar el informe contra la evidencia (`06-Evidencias/ejecucion/`) y confirmar quién figura como ejecutor de las pruebas.
3. Armar el Prezi siguiendo `05-Presentacion_EP4/pautas_prezi.md` y ensayar la defensa individual (10 min + 5 min de preguntas).
4. Fuera del alcance del informe, para ampliarlo: pruebas con adultos mayores (PT-USAB-002/003) y compatibilidad en Firefox/Edge/Safari (PT-COMP-002), y los demás casos del plan completo.
5. Reproducir la ejecución: `docker compose up --build` en una copia de `CodigoFuenteA` con `package-lock.json` generado (ver `03-Anexos/Herramientas/ejecucion/README.md`) y regenerar el informe con `bash 04-Entrega/generador_informe/make.sh`.
