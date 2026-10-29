# 7. Análisis de Cobertura, Pertinencia y Coherencia del Plan de Pruebas

> **Respuesta al feedback EP1 (F2, F3).** La versión anterior de esta sección fue calificada "demasiado breve" y con "análisis confuso o con errores conceptuales". Los principales defectos eran: (a) contar 6 requerimientos funcionales cuando el ERS define 17; (b) afirmar a la vez "84 % – cumple parcialmente" y "todos los requerimientos tienen casos"; (c) exigir "cobertura de código ≥ 80 %" en un sistema que no tiene pruebas automatizadas; (d) excluir la recuperación ante desastres pese a que NFR-SEG-7 la exige. Esta versión separa los tipos de cobertura, usa cifras verificables y reconoce explícitamente las brechas.

## 7.1 Conceptos y definiciones utilizadas

Para evitar la ambigüedad de la versión anterior, "cobertura" se emplea con tres significados distintos y se mide por separado:

| Tipo de cobertura | Pregunta que responde | Fórmula | Cuándo se puede medir |
|---|---|---|---|
| **De diseño (de requerimientos)** | ¿Cada requerimiento del ERS tiene al menos un caso que lo verifique? | requerimientos con ≥ 1 caso ÷ requerimientos del ERS | Ahora (es una propiedad del plan) |
| **De ejecución** | ¿Cuántos de esos casos se ejecutaron y con qué resultado? | casos ejecutados ÷ casos diseñados; aprobados ÷ ejecutados | Tras la sección 8 |
| **De código / de endpoints** | ¿Cuánto del sistema ejercitan las pruebas? | endpoints probados ÷ 38 endpoints del backend | Tras la sección 8 |

Una cobertura de diseño del 100 % **no implica** que el sistema cumpla: indica que el plan no deja requerimientos sin verificar. El cumplimiento se determina con la cobertura de ejecución y los incidentes (sección 8).

## 7.2 Cobertura de requerimientos (diseño)

Fuente: `03-Anexos/Matrices/matriz_trazabilidad.md` (v2), validada contra el ERS v1.1.

| Categoría del ERS | Requerimientos | Con ≥ 1 caso | Cobertura | Casos que la verifican |
|---|---|---|---|---|
| Funcionales (RF-1.1 … RF-6.1) | 17 | 17 | 100 % | PT-FUNC-001…011, PT-SEG-002 |
| Seguridad (NFR-SEG-1…9) | 9 | 9 | 100 % | PT-SEG-001…009, PT-DIS-001 |
| Rendimiento (NFR-PERF-1…3) | 3 | 3 | 100 % | PT-PERF-001…003 (+ PERF-004 por criterio RF-5) |
| Usabilidad (NFR-USAB-1…4) | 4 | 4 | 100 % | PT-USAB-001…003 |
| Disponibilidad (NFR-DIS-1…2) | 2 | 2 | 100 % | PT-DIS-001 |
| Compatibilidad (NFR-COMPAT-1…2) | 2 | 2 | 100 % | PT-COMP-001…002 |
| Reglas de negocio (RB-1…5) | 5 | 5 | 100 % | PT-FUNC-001, 004; PT-SEG-002, 009 |
| **Total ERS** | **42** | **42** | **100 %** | **30 casos** |
| Criterios de interfaz (§3.1.1 y §3.1.2) | 2 | 2 | 100 % | PT-USAB-001, PT-FUNC-011 |

**Distribución y profundidad.** Con 30 casos para 42 requerimientos, la relación es 1,4 requerimientos por caso. Ningún caso concentra más de 4 requerimientos (PT-SEG-002 y PT-FUNC-001 verifican 4 cada uno), de modo que un fallo es atribuible a un conjunto acotado. Los requerimientos de mayor riesgo se verifican por **más de una técnica** (triangulación): p. ej. NFR-SEG-2 (hashing) se comprueba por inspección de código (SAST), por consulta a la base de datos y por comportamiento del login; NFR-SEG-4 (RBAC) se comprueba por API con tokens de distinto rol y por revisión del código de las rutas.

**Cobertura por tipo de prueba (30 casos):**

| Tipo | Casos | % | Orientación |
|---|---|---|---|
| Funcional (incl. API/E2E) | 11 | 37 % | ¿Hace lo que el ERS dice? |
| Seguridad | 9 | 30 % | ¿Resiste abuso y protege datos? |
| Rendimiento | 4 | 13 % | ¿Cumple umbrales de tiempo y carga? |
| Usabilidad / accesibilidad | 3 | 10 % | ¿Lo pueden usar los destinatarios, incl. adultos mayores? |
| Compatibilidad | 2 | 7 % | ¿Funciona en navegadores y dispositivos definidos? |
| Disponibilidad / recuperación | 1 | 3 % | ¿Se recupera y se mantiene? |

La concentración en funcional y seguridad (67 %) es deliberada y se justifica en 7.5: son los tipos que cubren los requerimientos de mayor riesgo para datos personales.

## 7.3 Cobertura frente a estándares técnicos

### 7.3.1 ISO/IEC 25010 (modelo de calidad del producto)

| Característica | Cubierta por | Observación |
|---|---|---|
| Idoneidad funcional | PT-FUNC-001…011 | Completa. |
| Eficiencia de desempeño | PT-PERF-001…004 | Completa respecto del ERS. |
| Compatibilidad | PT-COMP-001…002 | Completa. |
| Usabilidad (incl. accesibilidad) | PT-USAB-001…003 | Accesibilidad con WCAG 2.1 AA (7.3.3). |
| Fiabilidad | PT-DIS-001, PT-FUNC-003 | Parcial: una sola prueba de recuperación; no se mide el 99,5 % mensual (requiere observación prolongada; se verifica el mecanismo, no el período). |
| Seguridad | PT-SEG-001…009 | Completa respecto del ERS; mapeo OWASP en 7.3.2. |
| Mantenibilidad | PT-DIS-001 (migración), análisis estático | Parcial: sin métricas de complejidad ni pruebas unitarias existentes. |
| Portabilidad | — | **No cubierta** de forma directa; se asume contenedorización Docker como único entorno. Se declara como brecha (7.6). |

### 7.3.2 OWASP Top 10 (2021)

| Categoría | Caso(s) / técnica | Cobertura |
|---|---|---|
| A01 Control de acceso roto | PT-SEG-002, PT-SEG-009 | Directa |
| A02 Fallos criptográficos | PT-SEG-001, 003, 004 | Directa |
| A03 Inyección | PT-SEG-005 (SQL y XSS), SAST | Directa |
| A04 Diseño inseguro | PT-FUNC-001 (carga de archivos), PT-FUNC-008 (eliminación lógica), revisión de diseño | Parcial |
| A05 Configuración de seguridad incorrecta | PT-SEG-005, 006; escaneo de imagen/Dockerfile | Directa |
| A06 Componentes vulnerables y desactualizados | Análisis de dependencias (`npm audit`/OSV) e imágenes (Trivy) | Por herramienta; **sin caso PT dedicado** |
| A07 Fallos de identificación y autenticación | PT-SEG-001, 008, PT-FUNC-002, 003 | Directa |
| A08 Fallos de integridad de software y datos | — | **No cubierta**; se declara como brecha |
| A09 Fallos de registro y monitoreo | PT-SEG-006, PT-FUNC-010 | Directa |
| A10 SSRF | — | No aplica, salvo que el enlace compartido (RF-5.5) realice solicitudes salientes; se verifica en PT-FUNC-009 |

Resultado: 7 de 10 categorías con cobertura directa o parcial mediante casos; 1 (A06) cubierta por herramienta; 2 (A08, A10) sin cobertura o no aplicables, justificado.

### 7.3.3 WCAG 2.1 (principios POUR) — verificados en PT-USAB-001

| Principio | Verificación | Criterio medible |
|---|---|---|
| Perceptible | Contraste, texto alternativo, tamaño de fuente | Contraste ≥ 4,5:1 (AA); fuente base ≥ 16 px |
| Operable | Navegación por teclado, tamaño de objetivos táctiles, ausencia de trampas de foco | Todo operable con teclado; objetivos ≥ 44×44 px |
| Comprensible | Etiquetas de formulario, mensajes de error claros | Cada campo con `label`; error indica causa y acción |
| Robusto | Semántica y atributos ARIA | Sin errores críticos en axe / Lighthouse ≥ 90 |

### 7.3.4 Marco legal

| Norma | Qué exige (en lo que afecta a Atlas) | Casos que la verifican |
|---|---|---|
| Ley 19.628 (art. 11, deber de cuidado) | Resguardo de bases de datos personales | PT-SEG-001, 003, 004, 007 |
| Ley 21.719 | Mayor exigencia de seguridad y licitud (*vigencia por confirmar*) | PT-SEG-007 (criterios prospectivos) |
| Ley 20.422 | Accesibilidad para personas con discapacidad | PT-USAB-001 |
| Ley 21.459 | Límite ético de las pruebas (solo entorno autorizado) | Restricción transversal (sección 8, §6) |

## 7.4 Cobertura de ejecución y de endpoints (a completar tras la sección 8)

| Indicador | Meta | Valor real |
|---|---|---|
| Casos ejecutados / diseñados | 30 / 30 | — |
| Casos aprobados / ejecutados | informar sin meta (un fallo es un hallazgo válido) | — |
| Endpoints del backend probados | ≥ 80 % de 38 | — |
| Requerimientos con resultado verificado | 42 / 42 | — |

**Corrección del criterio de salida de EP1.** EP1 fijaba "cobertura de código ≥ 80 %". El repositorio no contiene pruebas unitarias ni script `test`, por lo que ese criterio no es alcanzable ni medible. Se reemplaza por **cobertura de endpoints** (38 manejadores HTTP identificados en `routes/`), medible con la colección OpenAPI/Newman que el propio ERS (§3.1.2) exige.

## 7.5 Pertinencia: por qué estas pruebas y no otras

La pertinencia se justifica por **riesgo** (probabilidad × impacto) sobre las características de Atlas, no por preferencia. La probabilidad se apoya en evidencia de la revisión estática (sección 9), no solo en estimación.

| Riesgo | Prob. | Impacto | Evidencia que sustenta la probabilidad | Pruebas asignadas | Prioridad |
|---|---|---|---|---|---|
| Fuga o robo de credenciales | Alta | Crítico | Contraseñas sin hash (H-01), secreto JWT por defecto (H-03) | PT-SEG-001, 008 | P1 |
| Acceso a datos de otra empresa o escalada de rol | Alta | Crítico | Sin control de rol (H-02), endpoints sin verificación de pertenencia (H-12, H-17, H-19) | PT-SEG-002, 009 | P1 |
| Exposición de datos bancarios | Media | Alto | Sin TLS (H-09), sin cifrado en reposo (H-13) | PT-SEG-003, 004, 007 | P1 |
| Operaciones lentas que inutilizan el sistema | Alta | Medio | Latencia de 4 s en login (H-05) | PT-PERF-001…003 | P2 |
| Pérdida de trazabilidad de acciones | Media | Alto | Eliminación física (H-06), auditoría por verificar | PT-FUNC-008, 010 | P2 |
| Exclusión de adultos mayores | Media | Medio | Requisito explícito (NFR-USAB-1) | PT-USAB-001 | P2 |
| Falla en navegadores/dispositivos | Baja | Medio | Stack React/MUI estándar | PT-COMP-001, 002 | P3 |
| Pérdida de datos sin recuperación | Media | Alto | Sin evidencia de política de respaldo | PT-DIS-001 | P2 |

**Por qué seguridad y funcionales concentran el esfuerzo:** Atlas almacena RUT, direcciones, contactos y datos bancarios de clientes de pymes; un incidente produce responsabilidad bajo la Ley 19.628 y daño a terceros ajenos al sistema. Los requerimientos de seguridad son 9 de los 20 NFR y su criterio de aceptación (ERS §3.3.1) exige "pruebas de penetración sin hallazgos críticos".

**Por qué rendimiento tiene casos de carga y de estrés:** NFR-PERF-3 define 200 usuarios concurrentes y un umbral CRUD de 300 ms; ambos son verificables con k6 y la evidencia estática ya sugiere un incumplimiento.

**Qué se descarta y por qué** (decisiones explícitas, no omisiones):

| Alternativa | Decisión | Justificación |
|---|---|---|
| Pruebas unitarias del backend | No incluidas como caso | El código no las tiene y el ERS no las exige; el equivalente es la prueba de API sobre los 38 endpoints. |
| Auditoría legal formal | Fuera de alcance | Requiere especialista jurídico; se verifica el cumplimiento **técnico** de los deberes de seguridad. |
| Escalabilidad horizontal | Fuera de alcance | El ERS define 200 concurrentes en un único despliegue. |
| Pruebas de instalación | Fuera de alcance | Docker Compose es el mecanismo de despliegue entregado; se valida levantando el stack. |
| **Recuperación ante desastres** | **Incluida** (PT-DIS-001) | *Corrige EP1:* NFR-SEG-7 exige políticas de respaldo y recuperación; se prueba un ciclo básico de respaldo y restauración. |

## 7.6 Coherencia interna del plan

Cada verificación indica el resultado del análisis, no una afirmación general.

| # | Verificación | Resultado | Acción |
|---|---|---|---|
| C1 | Todo requerimiento del ERS tiene caso | **Cumple** (42/42, verificado con script sobre la matriz) | — |
| C2 | Todo caso apunta a un requerimiento existente | **Cumple** (30 casos, ninguno huérfano) | — |
| C3 | Los resultados esperados coinciden con el texto del ERS | **Cumple tras corrección**: la v1 de la matriz definía mal NFR-SEG-3/6/7/9 y RB-1…5 | Matriz v2 |
| C4 | Los casos usan rutas reales | **Cumple tras corrección**: EP1 usaba `/api/auth/register`; el backend expone `/autenticacion`, `/usuarios`, `/clientes`… | Reescribir sección 6 con rutas reales |
| C5 | Las herramientas permiten ejecutar los casos | **Parcial**: EP1 listaba SonarQube, Cypress, JMeter, BrowserStack, TestRail, no todos disponibles en el taller | Herramientas acotadas (Semgrep, ZAP, k6, Newman, Lighthouse/axe) |
| C6 | Criterios de salida medibles | **Corregido**: "cobertura de código ≥ 80 %" no medible | Cobertura de endpoints (7.4) |
| C7 | Criterio de salida "sin defectos críticos ni altos" | **Se anticipa su incumplimiento** por los hallazgos H-01/H-02/H-12; es un resultado válido, no una incoherencia | Recomendación de no liberar (sección 10) |
| C8 | Cronograma vs. complejidad | **Por validar**: la proporcionalidad se verificará comparando horas reales con las estimadas | Registrar horas en sección 8 |

## 7.7 Brechas y riesgos residuales

| Brecha | Efecto | Tratamiento |
|---|---|---|
| Portabilidad (ISO 25010) sin caso directo | No se demuestra operación fuera de Docker | Declarada; fuera del alcance del ERS |
| OWASP A08 sin cobertura | Integridad de software/datos no verificada | Declarada; se recomienda firma de artefactos y control de dependencias |
| A06 cubierta solo por herramienta | Sin caso PT con criterios de aceptación propios | Se registra como evidencia de análisis estático (sección 9) |
| Disponibilidad 99,5 % no medible en el plazo | Solo se verifica el mecanismo de recuperación | Declarada |
| Usabilidad con 5 adultos mayores reales puede no ser factible | Resultado menos representativo | Alternativa: revisión heurística + Lighthouse/axe + prueba con al menos 1–2 usuarios; documentar la limitación |
| Pruebas de carga contra un entorno local | Resultados no extrapolables a producción | Reportar con las especificaciones del equipo usado |

## 7.8 Conclusión del análisis

1. **El plan es completo en diseño**: los 42 requerimientos y 2 criterios de interfaz están cubiertos por 30 casos trazables.
2. **El plan es pertinente**: el esfuerzo se concentra en seguridad y funcionalidad, respaldado por evidencia estática de riesgo, y las exclusiones están justificadas.
3. **El plan es coherente tras las correcciones C3–C6**; C7 anticipa, con fundamento, un resultado de no liberación.
4. **La cobertura real aún no está demostrada**: depende de la ejecución (sección 8). Hasta entonces ningún porcentaje de ejecución debe presentarse como logrado.
