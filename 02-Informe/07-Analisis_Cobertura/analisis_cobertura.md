# 7. Analisis de Cobertura, Pertinencia y Coherencia

## 7.1 Matriz de Trazabilidad

La matriz de trazabilidad vincula cada requerimiento del ERS con los casos de prueba diseñados, garantizando que todos los aspectos criticos del sistema son validados.

> **Nota:** La matriz detallada completa se encuentra en el Anexo: `03-Anexos/Matrices/matriz_trazabilidad.md`

### Resumen de Cobertura por Tipo de Requerimiento

| Categoria | Total Requerimientos | Requerimientos Cubiertos | Cobertura | Estado |
|-----------|---------------------|-------------------------|-----------|--------|
| Requerimientos Funcionales (RF) | 6 | 6 | 100% | Cumple |
| Requerimientos de Seguridad (NFR-SEG) | 9 | 9 | 100% | Cumple |
| Requerimientos de Rendimiento (NFR-PERF) | 3 | 3 | 100% | Cumple |
| Requerimientos de Usabilidad (NFR-USAB) | 4 | 4 | 100% | Cumple |
| Requerimientos de Disponibilidad (NFR-DIS) | [X] | [X] | [X]% | [Estado] |
| Requerimientos de Compatibilidad (NFR-COMPAT) | 2 | 2 | 100% | Cumple |
| Reglas de Negocio (RB) | 5 | 5 | 100% | Cumple |
| **TOTAL** | **29+** | **29+** | **100%** | **Cumple** |

> **Completar:** Ajustar los numeros segun el conteo exacto del ERS.

---

## 7.2 Analisis de Cobertura por Indicador de Logro (IL)

| IL | Descripcion | Cobertura en el Plan | Evidencia |
|----|-------------|----------------------|-----------|
| **IL 1.1** | Rol de la calidad, seguridad y cumplimiento legal | Completa | Secciones 1, 2 y 7 del informe. Se identifican normativas Ley 19.628, Ley 20.422, ISO/IEC 25010 |
| **IL 1.2** | Diferencias entre pruebas funcionales y no funcionales | Completa | Seccion 4 (Tipos de Pruebas). Se distinguen y justifican ambas categorias con ejemplos del caso Atlas |
| **IL 1.3** | Pruebas de usabilidad, rendimiento y compatibilidad | Completa | Casos PT-USAB-001, PT-PERF-001, PT-COMP-001. Se reconoce impacto en calidad, seguridad y etica |
| **IL 1.4** | Diseno de plan de pruebas con estrategia, objetivos, recursos y cronograma | Completa | Secciones 3 (Estrategia), 5 (Recursos). Coherencia con requerimientos y normativas |
| **IL 1.5** | Evaluacion de consistencia y cobertura del plan | Completa | Seccion 7 (Analisis). Matriz de trazabilidad, alineacion con estandares y marcos legales |

---

## 7.3 Analisis de Coherencia del Plan

### 7.3.1 Coherencia Interna
- **Estrategia vs Casos de Prueba:** La estrategia define pruebas de seguridad como prioridad critica, y los casos PT-SEG-001 y PT-SEG-002 validan especificamente los controles de seguridad del sistema.
- **Recursos vs Pruebas:** Las herramientas seleccionadas (OWASP ZAP, k6, Cypress) permiten ejecutar todos los casos de prueba definidos.
- **Criterios de Aceptacion vs Requerimientos:** Cada criterio de aceptacion es medible y directamente trazable a un requerimiento del ERS.
- **Cronograma vs Complejidad:** El tiempo asignado a cada fase es proporcional a la criticidad y complejidad de las pruebas.

### 7.3.2 Coherencia con Requerimientos del Proyecto
- Todos los RF (funcionales) tienen al menos un caso de prueba funcional o E2E asociado.
- Todos los NFR (no funcionales) tienen casos de prueba especificos que los validan.
- Las reglas de negocio (RB) son verificadas dentro de los casos funcionales y de seguridad.

### 7.3.3 Coherencia con Normativas y Estandares
- **ISO/IEC 25010:** Las caracteristicas de calidad seleccionadas (funcionalidad, fiabilidad, usabilidad, eficiencia, mantenibilidad, portabilidad) cubren las dimensiones principales del modelo SQuaRE.
- **OWASP Top 10:** Los casos de seguridad PT-SEG-001 y PT-SEG-002 abordan directamente A02:2021 (Criptografica Fallida) y A01:2021 (Control de Acceso Roto).
- **WCAG 2.1:** El caso PT-USAB-001 valida explicitamente el cumplimiento de nivel AA.
- **Ley 19.628:** Los criterios de confidencialidad e integridad aseguran el tratamiento seguro de datos personales.
- **Ley 20.422:** Las pruebas de usabilidad garantizan la accesibilidad para personas con discapacidad, incluyendo adultos mayores.

---

## 7.4 Analisis Critico y Justificacion Tecnica

### 7.4.1 Por que se probaron ciertos escenarios y no otros

**Escenarios Priorizados:**
1. **Seguridad de autenticacion y autorizacion:** Porque Atlas maneja datos personales sensibles (RUT, direcciones, documentos contractuales). Una brecha de seguridad implicaria responsabilidad legal bajo la Ley 19.628.
2. **Rendimiento de operaciones CRUD:** Porque las pymes dependen de la agilidad del sistema para su operacion diaria. Un sistema lento genera perdida de productividad.
3. **Usabilidad para adultos mayores:** Porque es un requerimiento explicito del caso (NFR-USAB-1) y un mandato legal (Ley 20.422).

**Escenarios No Priorizados (pero mencionados):**
- Pruebas de interoperabilidad con sistemas legacy: Fuera del alcance del caso semestral.
- Pruebas de instalacion: El sistema utiliza Docker Compose, simplificando el despliegue.
- Pruebas de localizacion: El sistema esta dirigido exclusivamente al mercado chileno.

### 7.4.2 Riesgos Identificados y Mitigacion

| Riesgo | Probabilidad | Impacto | Mitigacion mediante Pruebas |
|--------|-------------|---------|----------------------------|
| Fuga de datos personales | Media | Critico | PT-SEG-001 (hashing), PT-SEG-002 (RBAC), auditoria continua |
| Acceso no autorizado a contratos | Media | Alto | PT-SEG-002 (control de roles), pruebas de penetracion |
| Degradacion del servicio bajo carga | Baja | Alto | PT-PERF-001 (rendimiento), pruebas de estres |
| Exclusion de usuarios adultos mayores | Baja | Medio | PT-USAB-001 (accesibilidad), testing con usuarios reales |
| Incompatibilidad con navegadores | Baja | Medio | PT-COMP-001 (compatibilidad), matriz de navegadores |

### 7.4.3 Brechas y Limitaciones del Plan

| Brecha | Descripcion | Justificacion |
|--------|-------------|---------------|
| Pruebas de recuperacion ante desastres | No se incluyen pruebas de backup/restore | Fuera del alcance del caso semestral; requiere infraestructura de produccion |
| Pruebas de escalabilidad horizontal | No se prueba auto-scaling | El sistema esta disenado para pymes; 200 usuarios concurrentes es el limite definido |
| Pruebas de compliance legal formal | No se realiza auditoria legal formal | Se verifica cumplimiento tecnico; auditoria legal requiere abogado especializado |

---

## 7.5 Revision de Consistencia entre Componentes del Plan

| Componente | Consistente con Estrategia | Consistente con Recursos | Criterios Medibles | Estado |
|------------|---------------------------|-------------------------|-------------------|--------|
| Introduccion / Alcance | Si | Si | Si | Aprobado |
| Criterios de Calidad | Si | Si | Si | Aprobado |
| Estrategia de Pruebas | Si | Si | Si | Aprobado |
| Tipos de Prueba | Si | Si | Si | Aprobado |
| Recursos | Si | Si | Si | Aprobado |
| Casos de Prueba | Si | Si | Si | Aprobado |
| Matriz de Trazabilidad | Si | N/A | Si | Aprobado |

---

## 7.6 Conclusion del Analisis

El plan de pruebas disenado para el sistema Atlas presenta una cobertura completa de los requerimientos funcionales y no funcionales establecidos en el ERS. La estrategia definida es coherente con los objetivos del proyecto, los recursos asignados son suficientes para su ejecucion, y los criterios de aceptacion son medibles y trazables.

La priorizacion de pruebas de seguridad y usabilidad refleja adecuadamente el contexto del sistema —una plataforma que maneja datos personales y contractuales de pymes chilenas— y garantiza el cumplimiento de las normativas legales aplicables (Ley 19.628 y Ley 20.422).

Se recomienda la ejecucion del plan en los entornos definidos y la actualizacion continua de la matriz de trazabilidad a medida que se identifiquen nuevos riesgos o requerimientos.

> **Completar:** Personalizar la conclusion con reflexiones del grupo.
