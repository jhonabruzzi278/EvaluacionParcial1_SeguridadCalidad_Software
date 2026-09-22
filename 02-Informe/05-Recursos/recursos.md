# 5. Recursos Necesarios

## 5.1 Recursos Humanos

| Rol | Cantidad | Responsabilidades | Perfil Requerido |
|-----|----------|-------------------|------------------|
| **QA Lead / Lider de Pruebas** | 1 | Planificar, coordinar y supervisar el plan de pruebas. Garantizar la calidad del proceso. Generar informes. | Conocimiento en metodologias de prueba, gestion de proyectos, herramientas de automatizacion. |
| **QA Engineer (Funcional)** | 1 | Disenar y ejecutar pruebas funcionales, de integracion y regresion. Documentar defectos. | Experiencia en pruebas de aplicaciones web, Cypress/Playwright, APIs REST. |
| **QA Engineer (Seguridad)** | 1 | Disenar y ejecutar pruebas de seguridad. Realizar pentesting y revision de codigo. | Conocimiento en OWASP Top 10, herramientas DAST/SAST, criptografia basica. |
| **QA Engineer (Rendimiento)** | 1 | Disenar y ejecutar pruebas de carga, estres y rendimiento. Analizar metricas. | Experiencia con JMeter, k6, monitoreo de infraestructura. |
| **Desarrollador Backend** | 1 | Soporte en pruebas unitarias, revision de logs, correccion de defectos criticos. | Node.js, Express, PostgreSQL. |
| **Desarrollador Frontend** | 1 | Soporte en pruebas de usabilidad, compatibilidad y accesibilidad. | React, HTML5, CSS3, a11y. |
| **UX / Especialista en Accesibilidad** | 1 (parcial) | Disenar y supervisar pruebas de usabilidad. Validar cumplimiento WCAG 2.1. | Conocimiento en diseno centrado en usuario, accesibilidad web, testing con usuarios. |

> **Completar:** Justificar por que se requiere cada rol. Considerar que en un proyecto real de pymes, algunos roles pueden combinarse.

## 5.2 Recursos Tecnicos (Hardware y Software)

### 5.2.1 Hardware

| Recurso | Especificacion Minima | Cantidad | Proposito |
|---------|----------------------|----------|-----------|
| Servidor de aplicaciones | 4 vCPU, 8 GB RAM, 100 GB SSD | 2 | Backend y frontend en entornos QA y Staging |
| Servidor de base de datos | 2 vCPU, 4 GB RAM, 50 GB SSD | 2 | PostgreSQL en entornos QA y Staging |
| Estaciones de trabajo QA | Intel i5 / AMD Ryzen 5, 16 GB RAM, SSD 256 GB | 3 | Ejecucion de pruebas manuales y automatizadas |
| Dispositivos moviles | iPhone (iOS 16+), Android (API 30+) | 2 c/u | Pruebas de compatibilidad y usabilidad |
| Tablet | iPad / Android Tablet | 1 | Pruebas de compatibilidad responsive |

### 5.2.2 Software

| Categoria | Herramienta | Version | Licencia | Proposito |
|-----------|-------------|---------|----------|-----------|
| Gestion de pruebas | TestRail / XRay | Cloud / Latest | Pago | Gestion de casos de prueba, ejecucion y reportes |
| Automatizacion E2E | Cypress | 13.x | Open Source | Pruebas funcionales end-to-end |
| Automatizacion API | Jest + Supertest | 29.x | Open Source | Pruebas unitarias e integracion de backend |
| Rendimiento | k6 | 0.47+ | Open Source | Pruebas de carga y estres |
| Seguridad DAST | OWASP ZAP | 2.14+ | Open Source | Escaneo de vulnerabilidades web |
| Seguridad SAST | SonarQube Community | 10.x | Open Source | Analisis estatico de codigo |
| Usabilidad | Lighthouse | Chrome DevTools | Gratuito | Auditoria de accesibilidad y rendimiento |
| Compatibilidad | BrowserStack | Latest | Pago | Pruebas en navegadores y dispositivos reales en la nube |
| Gestion de defectos | Jira / GitHub Issues | Cloud | Pago / Gratis | Registro y seguimiento de bugs |
| Versionado | Git + GitHub | Latest | Gratis | Control de versiones y colaboracion |
| Contenedores | Docker + Docker Compose | 24.x | Open Source | Entornos consistentes y reproducibles |
| IDE / Editor | VS Code | Latest | Gratuito | Desarrollo y ejecucion de pruebas |

> **Completar:** Ajustar herramientas segun presupuesto y disponibilidad real.

## 5.3 Entornos de Prueba

| Entorno | Proposito | Configuracion | Datos |
|---------|-----------|---------------|-------|
| **Desarrollo (Dev)** | Desarrollo y pruebas unitarias por desarrolladores | Local / Docker Compose | Datos sinteticos minimos |
| **QA / Integracion** | Pruebas funcionales, integracion y regresion automatizadas | Servidor dedicado | Datos de prueba representativos (anonimizados) |
| **Staging / Pre-produccion** | Pruebas de rendimiento, seguridad, usabilidad y aceptacion | Replica de produccion | Subconjunto de datos de produccion (ofuscados) |
| **Produccion** | Monitoreo continuo y pruebas de humo post-despliegue | Infraestructura real | Datos reales |

### Requisitos de Red
- Acceso a Internet para herramientas cloud (BrowserStack, GitHub)
- Red aislada para pruebas de seguridad (pentesting sin afectar sistemas externos)
- VPN para acceso remoto seguro a entornos QA y Staging

## 5.4 Datos de Prueba

### 5.4.1 Datos Funcionales
- Usuarios con distintos roles (admin, editor, viewer)
- Empresas de prueba con RUT valido
- Clientes con datos completos y parciales
- Contratos con distintos estados (borrador, activo, finalizado)
- Documentos en formatos permitidos (PDF, DOCX, JPG)

### 5.4.2 Datos de Seguridad
- Contraseñas validas e invalidas (fuerza bruta)
- Tokens JWT expirados y manipulados
- Payloads de inyeccion SQL, XSS, CSRF
- Archivos maliciosos (ejecutables, scripts)

### 5.4.3 Datos de Rendimiento
- 1000+ registros de clientes
- 500+ contratos con documentos asociados
- Scripts de carga con 200 usuarios concurrentes

> **Completar:** Detallar mas ejemplos de datos de prueba especificos.

## 5.5 Capacitacion Requerida

| Tema | Dirigido a | Duracion | Formato |
|------|------------|----------|---------|
| Arquitectura del sistema Atlas | Todo el equipo QA | 2 horas | Sesion interna con desarrolladores |
| Uso de herramientas de automatizacion | QA Engineers | 4 horas | Workshop practico |
| OWASP Top 10 y pruebas de seguridad | QA Seguridad + Dev | 4 horas | Curso + practica guiada |
| Accesibilidad web (WCAG 2.1) | QA + UX + Frontend | 3 horas | Taller practico |
| Normativa Ley 19.628 y 20.422 | Todo el equipo | 2 horas | Charla con asesor legal / compliance |

> **Completar:** Ajustar segun nivel actual del equipo.
