# 3. Estrategia de Pruebas

## 3.1 Enfoque General

La estrategia de pruebas para el sistema Atlas adopta un **enfoque mixto** que combina pruebas manuales y automatizadas, distribuidas a lo largo del ciclo de desarrollo segun el modelo de piramide de pruebas. Se prioriza la ejecucion de pruebas unitarias y de integracion en etapas tempranas, complementadas con pruebas de sistema, seguridad y usabilidad en etapas posteriores.

> **Completar:** Justificar el enfoque mixto. Mencionar por que no se opta solo por manual o solo por automatizado.

## 3.2 Niveles de Pruebas

| Nivel | Descripcion | Momento | Responsable |
|-------|-------------|---------|-------------|
| **Unitarias** | Pruebas de funciones, componentes y modulos individuales | Durante el desarrollo | Desarrolladores |
| **Integracion** | Pruebas de interfaces entre modulos (Frontend-Backend, Backend-DB) | Post-desarrollo de modulos | QA / Desarrolladores |
| **Sistema** | Pruebas end-to-end de flujos completos de usuario | Pre-release | QA |
| **Aceptacion** | Validacion con usuarios representativos | Pre-lanzamiento | Usuarios clave / Product Owner |
| **Seguridad** | Pruebas de vulnerabilidades y controles de seguridad | Continuo / Pre-release | Especialista en Seguridad |
| **Rendimiento** | Pruebas de carga, estres y volumen | Pre-release | QA / DevOps |
| **Usabilidad** | Evaluacion de experiencia de usuario y accesibilidad | Pre-release | UX / QA |

## 3.3 Estrategia por Tipo de Prueba

### 3.3.1 Pruebas Funcionales
- **Tecnica:** Caja negra basada en especificaciones
- **Cobertura:** Todos los RF del ERS
- **Prioridad:** Alta
- **Automatizacion:** Si, con Cypress para flujos criticos (login, CRUD)

### 3.3.2 Pruebas de Seguridad
- **Tecnica:** Caja negra (DAST) + Caja blanca (SAST)
- **Cobertura:** Todos los NFR-SEG
- **Prioridad:** Muy Alta (manejo de datos sensibles)
- **Automatizacion:** Parcial, con OWASP ZAP y SonarQube

### 3.3.3 Pruebas de Rendimiento
- **Tecnica:** Pruebas de carga y estres
- **Cobertura:** NFR-PERF-1, NFR-PERF-2, NFR-PERF-3
- **Prioridad:** Alta
- **Automatizacion:** Si, con k6 o JMeter

### 3.3.4 Pruebas de Usabilidad
- **Tecnica:** Testing con usuarios + Heuristicas + Lighthouse
- **Cobertura:** NFR-USAB-1 al NFR-USAB-4
- **Prioridad:** Alta (adultos mayores)
- **Automatizacion:** Parcial (Lighthouse), principalmente manual

### 3.3.5 Pruebas de Compatibilidad
- **Tecnica:** Pruebas en multiples navegadores y dispositivos
- **Cobertura:** NFR-COMPAT-1, NFR-COMPAT-2
- **Prioridad:** Media-Alta
- **Automatizacion:** Parcial (BrowserStack)

## 3.4 Criterios de Entrada y Salida

### Criterios de Entrada (Para iniciar pruebas)
- [ ] El codigo fuente esta versionado en el repositorio Git
- [ ] Los modulos a probar han pasado revision de codigo (code review)
- [ ] El entorno de pruebas esta configurado y disponible
- [ ] Los datos de prueba han sido preparados y validados
- [ ] Los casos de prueba han sido revisados y aprobados

### Criterios de Salida (Para dar por terminadas las pruebas)
- [ ] 100% de casos de prueba funcionales ejecutados
- [ ] Cobertura de codigo >= 80%
- [ ] Sin defectos criticos ni altos abiertos
- [ ] Todos los requerimientos de seguridad verificados
- [ ] Informe de pruebas aprobado por el equipo de QA
- [ ] Matriz de trazabilidad actualizada y completa

## 3.5 Priorizacion de Pruebas

Las pruebas se priorizan segun el riesgo y la criticidad para el negocio:

| Prioridad | Area | Justificacion |
|-----------|------|---------------|
| P1 - Critica | Seguridad (autenticacion, autorizacion, datos) | Manejo de informacion sensible y legalmente protegida |
| P1 - Critica | Funcionalidades core (login, CRUD clientes/contratos) | Operaciones esenciales del negocio |
| P2 - Alta | Rendimiento (tiempos de respuesta, concurrencia) | Experiencia de usuario y escalabilidad |
| P2 - Alta | Usabilidad y accesibilidad | Cumplimiento Ley 20.422 y publico objetivo |
| P3 - Media | Compatibilidad multi-navegador | Alcance de mercado |
| P3 - Media | Regresion | Estabilidad en iteraciones futuras |

## 3.6 Herramientas de Prueba

| Categoria | Herramienta | Proposito | Tipo de Prueba |
|-----------|-------------|-----------|----------------|
| Automatizacion Frontend | Cypress / Playwright | Pruebas E2E de flujos de usuario | Funcional, Regresion |
| Automatizacion Backend | Jest / Mocha | Pruebas unitarias e integracion API | Funcional, Integracion |
| Rendimiento | k6 / JMeter | Pruebas de carga y estres | Rendimiento |
| Seguridad | OWASP ZAP | Escaneo de vulnerabilidades web | Seguridad (DAST) |
| Seguridad | SonarQube | Analisis estatico de codigo | Seguridad (SAST) |
| Usabilidad | Lighthouse | Auditoria de rendimiento y accesibilidad | Usabilidad, Rendimiento |
| Gestion de Pruebas | TestRail / Excel | Gestion de casos de prueba y resultados | Todas |
| Versionado | Git + GitHub | Control de versiones del codigo y pruebas | Todas |

> **Completar:** Justificar la seleccion de cada herramienta. Mencionar alternativas consideradas.

## 3.7 Cronograma Estimado de Pruebas

| Fase | Actividad | Duracion | Responsable |
|------|-----------|----------|-------------|
| Semana 1 | Preparacion: entornos, datos, casos de prueba | 3 dias | QA + Dev |
| Semana 1-2 | Pruebas Unitarias y de Integracion | 5 dias | Desarrolladores |
| Semana 2 | Pruebas Funcionales de Sistema | 4 dias | QA |
| Semana 2-3 | Pruebas de Seguridad | 4 dias | Especialista Seguridad |
| Semana 3 | Pruebas de Rendimiento | 3 dias | QA / DevOps |
| Semana 3 | Pruebas de Usabilidad | 3 dias | UX / QA |
| Semana 3-4 | Pruebas de Compatibilidad | 2 dias | QA |
| Semana 4 | Regresion y validacion final | 2 dias | QA |
| Semana 4 | Entrega de informe de pruebas | 1 dia | QA Lead |

> **Completar:** Ajustar duraciones segun sea realista para el proyecto.
