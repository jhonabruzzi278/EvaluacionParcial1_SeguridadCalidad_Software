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
| Herramientas SAST/DAST ejecutadas | ❌ pendiente (requiere el Docker oficial del taller; no disponible en la máquina de desarrollo) |
| Ejecución de casos de prueba | ❌ 0/30 ejecutados oficialmente · 🟡 8 verificaciones **preliminares** en entorno temporal — `08-Ejecucion_Pruebas/registro_ejecucion.md` §2b (pendientes de reconfirmar en Docker, con evidencia) |
| Feedback del docente a EP1 (86/100) | ✅ recibido: `01-Documentos_Base/Feedback_EP1_docente.md`. Debilidad: IE5 cobertura 6/20; índice no definido |
| Índice definido del informe | ✅ `02-Informe/00-Indice/indice_informe_EP3.md` |
| Sección 7 Cobertura, pertinencia y coherencia reescrita | ✅ `02-Informe/07-Analisis_Cobertura/` (pendiente completar valores de ejecución) |
| Casos detallados (8 completos + 22 fichas) con rutas reales | ✅ `02-Informe/06-Casos_Prueba/` |
| SonarQube + guía de herramientas (k6, ZAP, Semgrep, Gitleaks, Trivy) | ✅ `03-Anexos/Herramientas/` (sin ejecutar) |
| Análisis ético-normativo | 🟡 borrador estructural |
| Informe final Word/PDF (Arial 11, 1,5, justificado) | ❌ |
| Diapositivas EP4 | ❌ guion listo en `05-Presentacion_EP4/` |

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
├── 04-Entrega/                  EP1_entregado/ · EP3/ (informe final)
├── 05-Presentacion_EP4/         Guion de defensa y preguntas probables
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

## Siguientes pasos

1. Confirmar las **fechas** de EP3/EP4.
2. En el taller: `docker compose up --build` (guía: `03-Anexos/Herramientas/README.md` §0) y verificar que responde.
3. Levantar SonarQube y ejecutar el escaneo (`03-Anexos/Herramientas/README.md` §1), luego el resto de herramientas estáticas.
4. Ejecutar los 30 casos **uno a uno** en el orden de `08-Ejecucion_Pruebas/registro_ejecucion.md` §5, empezando por reconfirmar con evidencia las 8 verificaciones preliminares de §2b (PT-SEG-001, PT-SEG-002, PT-FUNC-003, PT-FUNC-010).
5. Completar el análisis ético-normativo y consolidar el informe en `04-Entrega/EP3/`.
6. Preparar diapositivas y ensayar la defensa individual.
