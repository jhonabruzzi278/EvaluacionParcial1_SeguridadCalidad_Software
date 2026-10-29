# Análisis de rúbricas EP3 y EP4 — ISY1102

**Fuentes:** `01-Documentos_Base/Pauta_EP3_403028442.pdf` y `Pauta_EP4_403029208.pdf`
**Contraste con:** ERS Atlas (`SRS_Atlas_384735328.pdf`), código fuente (`CodigoFuenteA/`) y el informe EP1 efectivamente entregado (`04-Entrega/EP1_entregado/`).

---

## 0. Aclaración de numeración

Los PDF corresponden a **Evaluación Parcial Nº3** (informe grupal, 12 %) y **Nº4** (defensa individual, 28 %). Ambos PDF contienen en su texto la frase "La Evaluación Parcial 2 corresponde a…", que es un error de copia de la pauta y no indica otra evaluación. Lo que en el repo anterior se llamó "EVA2" fue el cuestionario teórico de EP1 (ya rendido el 24/09/2026) y se archivó.

| | EP3 | EP4 |
|---|---|---|
| Situación evaluativa | Encargo (informe) | Presentación / defensa |
| Modalidad | Grupal | **Individual** (se evalúa a cada estudiante) |
| Ponderación | 12 % | 28 % |
| Tiempo | 1 h pedagógica | 3 h pedagógicas de preparación; 10 min defensa + 5 min preguntas |
| Entrega | Informe Word/PDF en AVA el día de la evaluación | Informe **y** material de apoyo en AVA |

EP3 + EP4 = **40 %** de la nota de evaluaciones parciales. EP4 pesa más del doble que EP3 y se califica por lo que cada persona sepa explicar, no por lo que el grupo entregó.

Ambas miden los mismos indicadores de logro (IL 2.1–2.5). Esto significa que **el informe EP3 es la materia prima de la defensa EP4**: cada decisión del informe debe poder justificarse oralmente.

---

## 1. Qué exige cada indicador y dónde se cumple

### EP3 — Informe (12 %)

| IE | Peso | Qué pide el 100 % | Dónde se cubre | Riesgo principal |
|---|---|---|---|---|
| **IE1** Importancia de calidad, seguridad y cumplimiento legal | 20 % | Claridad y profundidad, **ejemplos pertinentes**, lenguaje técnico | `01-Introduccion`, `02-Criterios_Calidad`, `10-Analisis_Etico_Normativo` | Quedarse en definiciones genéricas. La diferencia con EP1 es que ahora hay **ejemplos reales del propio caso** (ver `09-Analisis_Estatico`). |
| **IE3** Clasifica tipos de prueba y su propósito | **38 %** | *Todos* los tipos (funcional, no funcional, seguridad, rendimiento, etc.), justificando propósito y aplicación | `04-Tipos_Pruebas` | Es el indicador más pesado. Un tipo omitido o sin justificar baja a "buen desempeño" (80 %). |
| **IE5** Casos de pruebas **no funcionales** | 15 % | Casos representativos de *distintos* tipos no funcionales, con criterios de aceptación y propósito coherentes con el contexto | `06-Casos_Prueba` (PT-SEG, PT-PERF, PT-USAB, PT-COMP, PT-DIS) | Casos con resultado esperado inalcanzable o sin relación con el código real. |
| **IE7** Elementos del plan de pruebas | 15 % | Introducción, **alcance, objetivos, estrategia, recursos y cronograma**, con vínculo a requerimientos y normativa | `01`, `03`, `05` | Las instrucciones listan *otros* apartados (estrategia, tipos, criterios de aceptación, herramientas); la rúbrica exige además alcance, objetivos, recursos y cronograma. **Hay que incluir ambas listas.** |
| **IE9** Cobertura, pertinencia y coherencia frente a estándares técnicos y legales | 12 % | Análisis **crítico** con justificación técnica | `07-Analisis_Cobertura`, matriz de trazabilidad | EP1 declaró 84 % de cobertura; EP3 exige 100 %. |

### EP4 — Defensa (28 %)

| IE | Peso | Qué pide el 100 % | Qué hay que preparar |
|---|---|---|---|
| **IE2** Estrategia de pruebas y justificación de seguridad/normativa | 20 % | Dominio y fluidez; justificar **por qué** se incluyó seguridad y normativa, con ejemplos concretos | Explicar el enfoque (riesgo, pirámide, SAST+DAST+manual) con 2–3 ejemplos del caso Atlas. |
| **IE4** Tipos de prueba aplicados: **origen e impacto** | **38 %** | Precisión, comprensión profunda, ejemplos | Para cada tipo ejecutado: de qué requerimiento/norma proviene (*origen*) y qué pasa si falla (*impacto*). Es la pregunta más probable en los 5 min de preguntas. |
| **IE6** Resultados del **análisis estático** comparados con criterios legales/normativos | 15 % | Resultados claros + comparación precisa con ley/norma | Exige *haber corrido* análisis estático (no solo revisión manual) y tener una tabla hallazgo → artículo/control incumplido. |
| **IE8** Proceso de ejecución con lógica, secuencia y **trazabilidad** | 15 % | Flujo ordenado con trazabilidad completa a requerimientos | Poder recorrer: requerimiento → caso → ejecución → evidencia → incidente. |
| **IE10** Recomendaciones basadas en evidencia técnica y principios éticos/normativos | 12 % | Argumentos con evidencia + referencias éticas y normativas | Cada recomendación debe citar el hallazgo (H-xx), el requerimiento y la norma/principio. |

### Contenido obligatorio de la defensa (EP4)
Enfoque estratégico · herramientas y justificación de su elección · ejecución de pruebas · clasificación de defectos · reflexiones de calidad, seguridad, normativa y legal.
Propuesta de reparto de los 10 minutos: estrategia 2 · herramientas 1,5 · ejecución 3 · defectos 1,5 · reflexión 2.

---

## 2. Lo que el informe EP3 debe contener (checklist normativo de la pauta)

1. Puntos de EP1 **con ajustes según el feedback del docente**.
2. Casos de prueba con **cobertura del 100 % del ERS** (necesidades, normativa, legal, seguridad).
3. Criterios de calidad, seguridad y cumplimiento normativo.
4. Plan de pruebas: estrategia, tipos y justificación, criterios de aceptación, herramientas.
5. **Mínimo 5** casos detallados con: ID, descripción, requerimiento (código ERS), datos de entrada (si aplica), resultado esperado, criterios de aceptación, tipo de prueba.
6. **Ejecución de pruebas:** resumen, detalle por caso, incidentes con criticidad.
7. Análisis ético y normativo de los resultados.
8. Formato: Word/PDF · títulos Arial 12 · cuerpo Arial 11 · interlineado 1,5 · justificado · portada (integrantes, carrera, sección, docente, fecha) · lenguaje formal técnico · capturas legibles.

**Novedad respecto de EP1:** los puntos 6 y 7 y el análisis estático (IL 2.3, IL 2.4) obligan a **ejecutar** el software, no solo planificar. La pauta lista como insumos: imágenes Docker, código fuente y los computadores del taller de proyectos.

---

## 3. Brechas del informe EP1 entregado (verificadas)

| # | Brecha | Evidencia | Impacto en EP3 |
|---|---|---|---|
| G1 | La cobertura se mide sobre 6 "RF" cuando el ERS define **17 requerimientos funcionales** (RF-1.1 … RF-6.1). Declara **26/31 = 84 %**. | EP1 §5.1; ERS §3.2 | EP3 exige 100 % → hay que re-contar sobre **42** ítems (ver matriz). |
| G2 | Solo **7 casos** de prueba. Cubren 7 de las ~30 áreas necesarias. | EP1 §4.8 | Faltan casos para RF-1.2, RF-2.x, RF-3.x, RF-5.4/5.5, RF-6.1, SEG-1/3/5/6/8/9, RB-1/2/3, PERF-2/3. |
| G3 | Los casos usan rutas inexistentes (`/api/auth/register`, `/api/empresas/1/clients`). El backend real expone `/autenticacion/login`, `/usuarios`, `/clientes`, `/contratos`, `/empresas`, `/roles`, `/empresa-usuarios`, `/auditoria`, `/metricas`. | `BACKEND/src/app.js:29-37` | Un caso con ruta falsa no es ejecutable ni defendible. |
| G4 | El borrador `.md` de la matriz describe requerimientos que **no coinciden con el ERS**: NFR-SEG-3 (es *cifrado en reposo*, no JWT), SEG-6 (*gestión de log*), SEG-7 (*respaldo*), SEG-9 (*JWT*), RB-1…RB-5, NFR-USAB-2…4. Además incluye "RUT módulo 11" como RB-5, que **no existe** en el ERS. | Borrador `matriz_trazabilidad.md` (v1) vs ERS §3.3–3.4 | Trazabilidad incorrecta = IE9 e IE8 comprometidos. **Corregido en la matriz v2.** |
| G5 | NFR-DIS-1/2 existían en el docx pero no en los borradores `.md`. | — | La matriz v2 los incluye. |
| G6 | No hay ejecución, análisis estático ni análisis ético-normativo. | — | Secciones 08, 09 y 10 nuevas. |
| G7 | Herramientas del plan (SonarQube, Cypress, JMeter, BrowserStack, TestRail) no se justifican contra lo realmente ejecutable en el taller. | EP1 §3.4 | EP4-IE2/IE4 piden *justificar la elección*. Se propone acotar (sección 5). |
| G8 | Borradores `.md` con marcas "Completar". | `02-Informe/*` | Limpiar antes de consolidar. |
| G9 | Feedback del docente a EP1 (86/100): **IE5 cobertura 6/20 "análisis confuso o con errores conceptuales"** y "índice no definido". | `01-Documentos_Base/Feedback_EP1_docente.md` | **Resuelto en diseño:** sección 7 reescrita, índice definido (ver §3b). |

---

## 3b. Diagnóstico del feedback de EP1

El comentario dice "demasiado breve", pero el **descriptor de la rúbrica** que recibió el indicador (nivel *incipiente*) dice "análisis confuso o con errores conceptuales". El nivel lo fija el descriptor, así que la corrección debe ser de **exactitud** además de extensión. Errores detectados en el EP1 entregado:

1. Contaba 6 RF; el ERS define 17 (cobertura mal medida).
2. Contradicción interna: tabla con "84 % – cumple parcialmente" y texto "todos los RF y NFR tienen casos".
3. Criterio de salida "cobertura de código ≥ 80 %" en un sistema sin una sola prueba ni script `test`.
4. Excluía respaldo/recuperación pese a NFR-SEG-7.
5. Afirmaba "Completa" en los IL sin evidencia ni métrica; en su análisis de cobertura citaba solo 2 de las 10 categorías OWASP.
6. Índice: texto de relleno de Word sin generar.

Esta rúbrica pesa 12 % en EP3 (IE9), no 20 %, pero el mismo contenido se evalúa de nuevo en EP4 (IE8, trazabilidad). Es el punto donde más se puede recuperar.

## 4. Hallazgo clave: el sistema probado es deliberadamente inseguro

`BACKEND/package.json` describe la API como *"intencionalmente vulnerable"*. Una primera revisión estática manual (detalle en `02-Informe/09-Analisis_Estatico/hallazgos_estaticos.md`) identificó **19 hallazgos** (4 críticos, 9 altos, 6 medios). Los más relevantes:

- **H-01** Contraseñas comparadas y almacenadas en texto plano (`auth.js:26`) → incumple NFR-SEG-2.
- **H-02** Sin control de rol en el backend → incumple NFR-SEG-4, RF-3.2, RB-4.
- **H-04** No existe logout/revocación de tokens → incumple RF-1.2.
- **H-05** `await delay(4000)` en login → incumple NFR-PERF-1 (< 300 ms).

**Consecuencia para el diseño de pruebas:** varios casos tendrán resultado real **FALLIDO**, y eso es el resultado correcto de una prueba bien hecha. El informe no debe "maquillar" resultados; debe registrarlos como incidentes con criticidad. Esto además es lo que da contenido a IE1 (ejemplos pertinentes), EP4-IE6 (estático vs. norma) y EP4-IE10 (recomendaciones).

> Estos hallazgos son de **revisión manual del código**. Para EP4-IE6 hay que complementarlos con una herramienta SAST ejecutada (Semgrep/ESLint-security) y para confirmarlos con pruebas dinámicas en el stack Docker. Ninguna prueba dinámica se ha ejecutado todavía.

---

## 5. Decisiones propuestas

1. **Renombrar y reorganizar el repositorio** para EP3/EP4 (hecho). Lo de EP1/EVA2 queda archivado en `99-Archivo_EP1_EVA2/`; los borradores de `02-Informe/01–07` se conservan como base.
2. **Re-trazar contra el ERS real:** 42 requerimientos + 2 criterios de interfaz → **30 casos de prueba** (matriz v2). Se conservan los 7 IDs de EP1 para no romper continuidad, corrigiendo sus requerimientos asociados.
3. **Detallar en el informe ≥ 8 casos completos** (uno por tipo: funcional, seguridad ×3, rendimiento, usabilidad, compatibilidad, disponibilidad); el resto queda en la matriz con ID, tipo, requerimiento y resultado esperado.
4. **Herramientas (acotar a lo ejecutable y justificar):**

| Propósito | Herramienta propuesta | Justificación | Reemplaza/ajusta (EP1) |
|---|---|---|---|
| SAST principal | **SonarQube Community** (Docker) | Herramienta del plan EP1 y estándar de la industria; entrega vulnerabilidades, *security hotspots* y calidad en un panel con capturas para evidencia. **Se mantiene.** Configuración lista en `03-Anexos/Herramientas/sonarqube/` | = (se conserva) |
| SAST complementario | Semgrep (reglas OWASP/Node) | La edición Community de SonarQube no incluye análisis de flujo contaminado (*taint*), según el proveedor (verificar en la versión instalada); Semgrep lo complementa | nuevo |
| Dependencias | `npm audit` / OSV-Scanner | Cubre A06 y es reproducible | — |
| Secretos | Gitleaks | Detecta credenciales embebidas (H-11) | nuevo |
| Imagen/IaC | Trivy + Hadolint | Imágenes Docker son insumo oficial de la pauta | nuevo |
| DAST | OWASP ZAP (baseline) | Ya estaba en EP1; funciona contra el stack local | = |
| API funcional | Postman/Newman sobre `openapi.json` | El ERS §3.1.2 pide colección Swagger con tests básicos | Cypress (solo si hay tiempo) |
| Rendimiento | k6 | Ya estaba en EP1; scripts en JS, mide p95 | JMeter |
| Accesibilidad | Lighthouse + axe DevTools + revisión manual de teclado | Cubre WCAG 2.1 AA | — |
| Compatibilidad | Navegadores locales + DevTools de emulación | BrowserStack es de pago | BrowserStack |

   SonarQube se mantiene por requerimiento del equipo; las demás herramientas se acotan a las ejecutables en el taller. BrowserStack, Cypress y JMeter se reemplazan según la tabla.
5. **Mantener esta línea de evidencia:** cada incidente debe tener ID → caso → requerimiento → evidencia (captura/log en `06-Evidencias/`) → norma. Eso responde directamente a EP4-IE8.
6. **Escala de criticidad de incidentes** definida una sola vez (en `08-Ejecucion_Pruebas`), alineada a OWASP/CVSS cualitativo, para que el informe y la defensa usen el mismo criterio.
7. **Tratar a EP4 como individual desde ya:** los tres integrantes deben poder defender el flujo completo. El reparto de redacción es solo logístico.

---

## 6. Marco legal y normativo a usar (validar con el docente)

| Norma | Uso en el informe | Nota |
|---|---|---|
| Ley 19.628 — Protección de la Vida Privada | Deber de cuidado de bancos de datos (art. 11), consentimiento (art. 4). Aplica a H-01, H-13, H-07. | Vigente. |
| Ley 21.719 — Protección de Datos Personales (2024) | Reemplaza a la 19.628; crea la Agencia de Protección de Datos. Eleva exigencias de seguridad y responsabilidad. | **Verificar fecha de entrada en vigor** (se entiende diferida a fines de 2026) antes de afirmarla en el informe. |
| Ley 20.422 — Inclusión de personas con discapacidad | NFR-USAB-1 y accesibilidad. | Vigente. |
| Ley 21.459 — Delitos informáticos | **Marco ético de las pruebas:** el acceso a sistemas sin autorización es delito; las pruebas intrusivas se limitan al entorno Docker local entregado por la asignatura. | Vigente. |
| Ley 19.799 — Documento y firma electrónica | Contexto de contratos y enlaces compartidos (RF-5.5). | Aplicación tangencial. |
| Ley 21.663 — Marco de Ciberseguridad | Referencia de buenas prácticas; probablemente no aplica directamente a una pyme. | Indicar como referencial. |
| ISO/IEC 25010 · ISO/IEC/IEEE 29119 · OWASP Top 10 (2021) · OWASP ASVS · WCAG 2.1 AA | Criterios técnicos de calidad, proceso de pruebas, seguridad y accesibilidad. | — |

---

## 7. Pendientes que requieren al equipo

| # | Pendiente | Quién |
|---|---|---|
| P1 | ~~Feedback del docente a EP1~~ — recibido | — |
| P2 | Fecha/hora de entrega EP3 y de la defensa EP4 | Equipo |
| P3 | Levantar el stack con `docker compose up` en el taller (esta máquina de desarrollo **no tiene** Docker ni Node, por lo que nada se ha ejecutado dinámicamente) | Equipo |
| P4 | Ejecutar herramientas (Semgrep, ZAP, k6, Lighthouse…) y guardar capturas en `06-Evidencias/` | Equipo |
| P5 | Confirmar con el docente la vigencia de la Ley 21.719 | Equipo |
| P6 | Completar portada: carrera *Ingeniería en Informática*, sección *003V*, docente *Cristian Eduardo Medina Cespedes* (datos tomados del informe EP1) | Equipo |
