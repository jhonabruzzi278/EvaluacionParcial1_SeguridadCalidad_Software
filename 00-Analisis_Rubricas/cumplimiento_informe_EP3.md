# Cumplimiento del informe EP3 frente a la pauta

Auditoría interna del informe `04-Entrega/EP3/EP3_ISY1102_Informe_Atlas.docx` (28 págs.) contra `Pauta_EP3_403028442.pdf`. No forma parte del informe. Los números de sección son los del informe.

## 1. Indicadores de evaluación

| IE | Peso | Qué exige el 100 % | Dónde se cumple | Observación |
|---|---|---|---|---|
| IE1 Importancia de calidad, seguridad y cumplimiento legal | 20 % | Claridad, profundidad, ejemplos pertinentes, lenguaje técnico | §2.1 (importancia, con ejemplos reales de Atlas), §2.2–2.4, §6 | Cumple. |
| IE3 Clasifica tipos de prueba y su propósito | 38 % | Todos los tipos, con propósito y aplicación | §3.2: Tabla 4 (11 tipos: propósito, origen, impacto, casos y estado) y párrafo de técnica, modalidad y nivel | Cumple. Compatibilidad y disponibilidad se clasifican, pero figuran sin caso en el conjunto priorizado. |
| IE5 Casos de pruebas no funcionales | 15 % | Casos de **distintos** tipos no funcionales, con criterios de aceptación y propósito coherentes | §4.1: seguridad (PT-SEG-001, 002, 008, 009), rendimiento (PT-PERF-001) y usabilidad (PT-USAB-001); más 4 funcionales | 10 casos (la pauta pide ≥ 5), 6 de ellos no funcionales de 3 tipos distintos. Se quitaron los de compatibilidad y disponibilidad al reducir a 10 casos. |
| IE7 Elementos del plan de pruebas | 15 % | Introducción, alcance, objetivos, estrategia, recursos y cronograma, vinculados a requerimientos y normas | §1.1–1.3, §3.1 (estrategia), §3.5 (recursos), §3.6 (cronograma) | Cumple. El alcance declara que se verifican 16 de los 42 requerimientos. |
| IE9 Cobertura, pertinencia y coherencia | 12 % | Análisis crítico con justificación técnica | §4.2 (alcance y cobertura por categoría, estándares, pertinencia por riesgo, coherencia y brechas) y Anexo A | **Punto de atención:** la cobertura es del 100 % **del alcance** (16 de 16) y del 38 % del ERS completo (16 de 42). El informe lo declara en ambos términos; si el docente exige cobertura total del ERS, este indicador puede perder puntaje. |

## 2. Contenido obligatorio de las instrucciones

| Requisito de la pauta | Cumple | Dónde |
|---|---|---|
| Puntos de EP1 con ajustes por feedback | Sí | §1.4 |
| Casos con cobertura 100 % del ERS (necesidades, normativa, legal, seguridad) | **Parcial:** 100 % del alcance definido; 38 % del ERS completo | §1.2, §4.2, Anexo A |
| Criterios de calidad, seguridad y cumplimiento normativo | Sí | §2 |
| Plan: estrategia, tipos y justificación, criterios de aceptación, herramientas | Sí | §3.1–3.4 |
| ≥ 5 casos con ID, descripción, requerimiento, datos de entrada, resultado esperado, criterios de aceptación y tipo | Sí (10) | §4.1 |
| Ejecución: resumen, detalle, incidentes y criticidad | Sí, con resultados reales de la ejecución | §5.1–5.4 |
| Análisis ético y normativo de los resultados | Sí | §6 |
| Word o PDF; portada con integrantes, carrera, sección, docente y fecha | Sí, salvo apellidos | Fecha 29-oct-2026 (confirmar); faltan los apellidos completos |
| Arial 11 cuerpo, interlineado 1,5, justificado | Sí | Tablas en Arial 9–10, interlineado simple (habitual en tablas) |
| Títulos Arial 12 | Sí | Títulos y subtítulos en 12 pt (la plantilla traía 16 pt en nivel 1) |
| Lenguaje formal técnico y capturas legibles | Sí | Anexo B (capturas de SonarQube); la evidencia de cada caso está en 06-Evidencias/ejecucion/ |

## 3. Realismo: decisiones tomadas para que el informe sea defendible

1. **Solo se afirma lo ejecutado.** Los 10 casos del informe se ejecutaron en el Docker local de Atlas el 29-oct-2026 (1 aprobado, 9 fallidos). Cada resultado remite a un archivo de evidencia en `06-Evidencias/ejecucion/`.
2. **Alcance explícito.** El ERS (42 requerimientos) no se modificó: el informe acota el alcance por riesgo a 16 requerimientos y declara los 26 restantes como fuera de alcance y riesgo residual.
3. **Las verificaciones se corrigieron cuando la prueba era defectuosa** (URL sin codificar, consulta de auditoría incompleta, grep demasiado amplio, métrica de responsividad insuficiente); los fallos informados son del sistema, no de la prueba.
4. **Se retiró el criterio "cobertura de código ≥ 80 %"** (SonarQube mide 0,0 %: el sistema no tiene pruebas).
5. **Limitaciones declaradas:** sin adultos mayores reales (la usabilidad se mide con herramientas), pruebas de carga locales, alcance acotado, compatibilidad y disponibilidad fuera del conjunto priorizado.
6. **Herramientas acotadas a las ejecutables:** SonarQube, Semgrep, Gitleaks, Trivy, ZAP baseline, k6, Lighthouse y axe; cliente HTTP propio en lugar de Newman.
7. **Ley 21.719:** se cita como referencia con vigencia "a confirmar", no como exigible.
8. **Conclusión:** "no liberar", con 4 incidentes críticos confirmados por ejecución (12 incidentes en total).
9. **Hallazgos sin caso en el informe:** los de la revisión manual cuyo caso quedó fuera figuran como "Confirmado en prueba complementaria", con evidencia en el repositorio (el plan completo de 30 casos se ejecutó: 27 ejecutados, 7 aprobados, 20 fallidos).

## 4. Pendientes que el informe no puede resolver solo

- Confirmar la fecha de entrega y completar los apellidos de los integrantes en la portada.
- Abrir el .docx en Word y actualizar los índices (seleccionar todo + F9); la paginación se verificó solo con LibreOffice.
- Confirmar con el docente la vigencia de la Ley 21.719.
- Decidir si se amplía el alcance (más casos) en caso de que el docente exija cobertura total del ERS.

Para regenerar el informe: `bash 04-Entrega/generador_informe/make.sh`. Los casos que presenta se definen en la lista `KEEP` de `04-Entrega/generador_informe/build_informe.py`.
