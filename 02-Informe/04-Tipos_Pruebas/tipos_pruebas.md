# 4. Tipos de Pruebas y su Justificacion

## 4.1 Pruebas Funcionales

### Descripcion
Las pruebas funcionales validan que el sistema cumple con los requerimientos funcionales especificados en el ERS, verificando que cada funcionalidad produce el resultado esperado.

### Justificacion para Atlas
El sistema Atlas posee funcionalidades core que son criticas para la operacion de las pymes: autenticacion, gestion de clientes, gestion de contratos y auditoria. Un fallo en cualquiera de estas funcionalidades impacta directamente en la operacion del negocio y puede generar perdida de datos o incumplimiento contractual.

### Requerimientos Cubiertos
- **RF-1:** Autenticacion de usuarios (login con JWT)
- **RF-2:** Registro de nuevos usuarios y asignacion de roles
- **RF-3:** Gestion de clientes (CRUD completo)
- **RF-4:** Gestion de contratos (CRUD completo)
- **RF-5:** Gestion de documentos asociados a contratos
- **RF-6:** Auditoria y registro de acciones

### Tecnicas Aplicadas
- Pruebas de caja negra basadas en especificaciones
- Pruebas de caminos felices y alternativos
- Pruebas de limites y valores frontera
- Pruebas de flujo de datos

### Herramientas
- Cypress para pruebas E2E del frontend
- Jest + Supertest para pruebas de API
- Postman para pruebas manuales de endpoints

---

## 4.2 Pruebas de Seguridad

### Descripcion
Las pruebas de seguridad identifican vulnerabilidades, debilidades y riesgos en el sistema que podrian ser explotados para comprometer la confidencialidad, integridad o disponibilidad de la informacion.

### Justificacion para Atlas
Atlas maneja datos altamente sensibles: RUT, datos de contacto, informacion bancaria (para contratos) y documentos contractuales. El incumplimiento de seguridad no solo implica riesgo de fuga de datos, sino tambien sanciones legales bajo la Ley N° 19.628. Ademas, el control de acceso por roles es fundamental para evitar que usuarios no autorizados modifiquen o eliminen informacion critica.

### Requerimientos Cubiertos
- **NFR-SEG-1:** Comunicaciones cifradas con TLS
- **NFR-SEG-2:** Hashing de contraseñas con bcrypt
- **NFR-SEG-3:** Tokens JWT con expiracion
- **NFR-SEG-4:** Control de acceso basado en roles (RBAC)
- **NFR-SEG-5:** Proteccion contra CSRF, XSS, SQL Injection
- **NFR-SEG-6:** Manejo seguro de errores
- **NFR-SEG-7:** Registro de auditoria de acciones sensibles
- **NFR-SEG-8:** Cumplimiento de normativas de proteccion de datos
- **NFR-SEG-9:** Sanitizacion de archivos subidos

### Tecnicas Aplicadas
- Pruebas de penetracion (Pentesting)
- Analisis estatico de codigo (SAST)
- Analisis dinamico de aplicaciones (DAST)
- Pruebas de autenticacion y autorizacion
- Pruebas de validacion de entradas
- Revision de configuraciones de seguridad

### Herramientas
- OWASP ZAP (DAST)
- SonarQube (SAST)
- Burp Suite (Pentesting)
- JWT.io (validacion de tokens)

---

## 4.3 Pruebas de Rendimiento

### Descripcion
Las pruebas de rendimiento evaluan la velocidad, estabilidad, escalabilidad y consumo de recursos del sistema bajo diversas condiciones de carga.

### Justificacion para Atlas
El sistema esta dirigido a pymes que operan durante horarios laborales con picos de actividad. Si el sistema no responde en menos de 300ms o no soporta 200 usuarios concurrentes, se generaria perdida de productividad y frustracion en los usuarios, afectando la adopcion del producto.

### Requerimientos Cubiertos
- **NFR-PERF-1:** Tiempo de respuesta < 300ms para operaciones CRUD
- **NFR-PERF-2:** Carga de pagina < 2 segundos
- **NFR-PERF-3:** Soporte a 200 usuarios concurrentes

### Tecnicas Aplicadas
- Pruebas de carga (load testing)
- Pruebas de estres (stress testing)
- Pruebas de picos (spike testing)
- Pruebas de estabilidad (endurance testing)
- Pruebas de volumen

### Metricas Clave
- Tiempo de respuesta (promedio, percentil 95, percentil 99)
- Throughput (transacciones por segundo)
- Uso de CPU y memoria del servidor
- Tiempo de carga del DOM y recursos
- Numero de errores bajo carga

### Herramientas
- k6 (moderno, codigo JavaScript, ideal para APIs)
- JMeter (maduro, soporte amplio)
- Lighthouse (metricas de carga frontend)

---

## 4.4 Pruebas de Usabilidad

### Descripcion
Las pruebas de usabilidad evaluan que tan facil, intuitivo y eficiente es utilizar el sistema para los usuarios finales, incluyendo aspectos de accesibilidad.

### Justificacion para Atlas
El publico objetivo incluye adultos mayores y usuarios con poca experiencia tecnica. Si la interfaz no es accesible o intuitiva, se excluiria a un segmento importante de usuarios, incumpliendo la Ley N° 20.422 y limitando el mercado objetivo del producto.

### Requerimientos Cubiertos
- **NFR-USAB-1:** Accesibilidad para adultos mayores
- **NFR-USAB-2:** Tiempos de respuesta perceptibles (< 2s)
- **NFR-USAB-3:** Navegacion intuitiva
- **NFR-USAB-4:** Mensajes de error claros

### Tecnicas Aplicadas
- Testing con usuarios representativos (adultos mayores)
- Evaluacion heuristica (principios de Nielsen)
- Auditoria de accesibilidad automatizada (Lighthouse axe)
- Pruebas de navegacion por teclado
- Pruebas con lectores de pantalla

### Herramientas
- Lighthouse (auditoria automatizada)
- axe DevTools (accesibilidad)
- Hotjar / Clarity (mapas de calor, sesiones)
- Cuestionario SUS (System Usability Scale)

---

## 4.5 Pruebas de Integracion

### Descripcion
Las pruebas de integracion verifican que los diferentes modulos y componentes del sistema funcionan correctamente en conjunto.

### Justificacion para Atlas
Atlas es una arquitectura distribuida compuesta por Frontend (React), Backend (Express/Node.js), Base de Datos (PostgreSQL) y almacenamiento de archivos. Un fallo en la comunicacion entre cualquiera de estos componentes renderizaria el sistema inoperable.

### Componentes a Integrar
- Frontend React <-> Backend REST API
- Backend <-> PostgreSQL (persistencia de datos)
- Backend <-> Sistema de archivos (uploads de contratos)
- Backend <-> Servicio de autenticacion JWT
- Backend <-> Logs de auditoria

### Herramientas
- Jest + Supertest (pruebas de API)
- Postman / Newman (colecciones de integracion)
- Docker Compose (entorno de integracion consistente)

---

## 4.6 Pruebas de Compatibilidad

### Descripcion
Las pruebas de compatibilidad aseguran que el sistema funciona correctamente en diferentes navegadores, sistemas operativos, dispositivos y resoluciones de pantalla.

### Justificacion para Atlas
Los usuarios de pymes utilizan diversos dispositivos y navegadores. El sistema debe garantizar una experiencia consistente independientemente del entorno del usuario.

### Requerimientos Cubiertos
- **NFR-COMPAT-1:** Chrome, Firefox, Safari, Edge (ultimas 2 versiones)
- **NFR-COMPAT-2:** Dispositivos moviles y tablets (responsive)

### Matriz de Compatibilidad

| Navegador | Version | Escritorio | Tablet | Movil |
|-----------|---------|------------|--------|-------|
| Chrome | Ultimas 2 | Si | Si | Si |
| Firefox | Ultimas 2 | Si | Si | Si |
| Safari | Ultimas 2 | Si | Si | Si |
| Edge | Ultimas 2 | Si | Si | Si |

### Herramientas
- BrowserStack (pruebas en la nube)
- Chrome DevTools (emulacion de dispositivos)
- Responsive design testing tools

---

## 4.7 Resumen Comparativo de Tipos de Prueba

| Tipo | Proposito | Prioridad | Automatizable | Requerimientos |
|------|-----------|-----------|---------------|----------------|
| Funcionales | Validar comportamiento del sistema | Alta | Alta | RF-1 al RF-6 |
| Seguridad | Detectar vulnerabilidades | Muy Alta | Media | NFR-SEG |
| Rendimiento | Validar tiempos y escalabilidad | Alta | Alta | NFR-PERF |
| Usabilidad | Garantizar experiencia de usuario | Alta | Baja | NFR-USAB |
| Integracion | Validar comunicacion entre modulos | Alta | Alta | Arquitectura |
| Compatibilidad | Asegurar funcionamiento multi-entorno | Media | Media | NFR-COMPAT |

> **Completar:** Revisar que todos los tipos de prueba esten justificados con el contexto de Atlas y sus requerimientos especificos.
