# 9. Análisis Estático del Código Fuente — Hallazgos preliminares

**Alcance:** `CodigoFuenteA/` (BACKEND Express/PostgreSQL, FRONTEND React/Vite, `docker-compose.yml`, Dockerfiles, `nginx.conf`).
**Método aplicado hasta ahora:** revisión manual dirigida (lectura de `auth.js`, `users.js`, `clients.js`, `contracts.js`, `app.js`, `db.js`, `AuthContext.jsx`, configuración Docker) y búsqueda de patrones con `grep`.
**Estado:** **PRELIMINAR.** Cada hallazgo se cita con `archivo:línea` verificado. Falta (a) correr herramientas SAST (**SonarQube** como principal, más Semgrep, npm audit, Gitleaks, Trivy, Hadolint; guía en `03-Anexos/Herramientas/README.md`) y (b) **confirmar dinámicamente** cada hallazgo con el stack Docker. Hasta entonces el campo *Confirmado* permanece en "No".

Escala de severidad: ver `02-Informe/08-Ejecucion_Pruebas/registro_ejecucion.md` §1.

| ID | Hallazgo | Evidencia (`archivo:línea`) | Requerimiento incumplido | OWASP 2021 | Sev. prelim. | Caso que lo confirma | Confirmado |
|----|----------|------------------------------|--------------------------|-----------|--------------|----------------------|-----------|
| H-01 | Contraseñas **sin hash**: el login compara el valor almacenado con la contraseña recibida y las altas guardan lo que llega. `bcrypt` no figura en las dependencias. | `BACKEND/src/routes/auth.js:26`; inserciones en `users.js:26`, `empresas.js:30`, `empresa_usuarios.js:44`; `BACKEND/package.json`; **datos semilla** `sql/dump-atlas.sql:344-345` (`'admin'`/`'admin'`, `'editor'`/`'editor'` en la columna de hash) | NFR-SEG-2, restricción §2.4 | A02, A07 | Crítica | PT-SEG-001 | No |
| H-02 | **Sin control de rol en backend.** El token no incluye rol y los handlers de clientes, contratos y usuarios no consultan rol. El front toma el rol de `localStorage` con valor por defecto `"administrador"`. | `auth.js:42-51` (payload sin rol); sin referencias a rol en `clients.js`, `contracts.js`, `users.js`; `FRONTEND/src/context/AuthContext.jsx:14-15,52` | NFR-SEG-4, RF-3.2, RB-4, RB-5 | A01 | Crítica | PT-SEG-002 | No |
| H-03 | **Secreto JWT por defecto** `"inseguro"` repetido en 9 archivos; el `docker-compose.yml` define otro valor por defecto público. Si `JWT_SECRET` no se inyecta, cualquiera puede forjar tokens. | `const JWT_SECRET` en `auth.js:7` y 8 rutas más; `docker-compose.yml:35` | NFR-SEG-9 | A02, A05, A07 | Alta | PT-SEG-008 | No |
| H-04 | **No existe cierre de sesión ni revocación** en el backend (sin rutas `logout`/`refresh`). El logout del front solo borra `localStorage`; el JWT sigue válido hasta 2 h. | `auth.js` (única ruta: `/login`); `AuthContext.jsx:60-63`; `auth.js:50` | RF-1.2, §3.1.2 (refresh token) | A07 | Alta | PT-FUNC-003 | No |
| H-05 | **Latencia artificial de 4 s** en login y en un endpoint de contratos (comentada como "simular latencia"). Incumple el umbral aunque sea intencional. | `auth.js:17`; `contracts.js:75` | NFR-PERF-1 (< 300 ms), NFR-USAB-2 | — (calidad) | Alta | PT-PERF-001 | No |
| H-06 | **Eliminación física** (7 sentencias `DELETE FROM` en 6 rutas); el ERS exige eliminación lógica con confirmación. | `clients.js:341`; `contracts.js:437,441`; `users.js:126`; `empresas.js:164`; `empresa_usuarios.js:185`; `roles.js:84` | RF-4 (criterio de aceptación), RF-6.1 (trazabilidad) | A04 | Media | PT-FUNC-008 | No |
| H-07 | **Divulgación de errores internos**: 39 respuestas 500 devuelven `err.message` en el campo `glosa`. | `glosa: err.message` en todos los archivos de `routes/` (p. ej. `auth.js:64-67`) | NFR-SEG-6 | A05, A09 | Media | PT-SEG-006 | No |
| H-08 | **Carga de archivos sin validación**: `multer` sin `fileFilter` ni `limits`; el archivo se carga completo en memoria. Además el documento se guarda como `bytea` en la BD, no en storage interno referenciado. | `contracts.js:14-15`, `44-47` | RF-5.2, RF-5.3, NFR-SEG-5 | A04, A05 | Alta (SonarQube: "content length limit" no seguro) | PT-FUNC-001 / PT-SEG-005 / SonarQube | **Sí (preliminar)** — ver §2c |
| H-09 | **Sin TLS**: nginx escucha en el puerto 80 y el front se construye con `VITE_API_URL=http://…`. | `FRONTEND/nginx.conf:2`; `docker-compose.yml` (arg `VITE_API_URL`) | NFR-SEG-1, §2.4 | A02 | Alta | PT-SEG-003 | No |
| H-10 | **CORS abierto**, sin cabeceras de seguridad (`helmet`) ni limitación de intentos (login sin rate-limit → fuerza bruta). También se expone la versión del framework por defecto (`X-Powered-By`). | `app.js:20,22`; ausencia en `BACKEND/package.json` | NFR-SEG-5 | A05, A07 | Media (SonarQube confirma ambos puntos) | PT-SEG-005 / SonarQube | **Sí (preliminar)** — ver §2c |
| H-11 | **Credenciales por defecto en código e infraestructura** (`postgres:alone15`, `postgres/postgres`). | `db.js:6`; `docker-compose.yml:7,33` | NFR-SEG-8 (higiene de secretos) | A05, A07 | Alta (SonarQube lo marca **BLOCKER**) | revisión + Gitleaks + SonarQube | **Sí (preliminar)** — ver §2c del registro de ejecución |
| H-12 | **Endpoint sin autenticación ni verificación de pertenencia:** `POST /contratos` inserta con el `cliente_id` del cuerpo sin validar token ni empresa (riesgo IDOR). Aproximadamente 10 handlers más no muestran llamada a la verificación de token (a confirmar). | `contracts.js:29-58` | RB-2, RB-3, NFR-SEG-4 | A01 | Crítica | PT-SEG-009 | No |
| H-13 | **Datos bancarios sin cifrar en reposo** (`nombre_banco`, `numero_cuenta`) como `text`. | `BACKEND/sql/init.sql:45-46` | NFR-SEG-3, NFR-SEG-8 | A02 | Alta | PT-SEG-004 | No |
| H-14 | **Componentes desactualizados:** imagen `node:18-alpine` (fin de soporte), contenedor sin `USER` no-root; `multer 1.x` con avisos de seguridad conocidos (a confirmar con `npm audit`/OSV). | `BACKEND/Dockerfile:1`; `BACKEND/package.json` | NFR-SEG-5 (buenas prácticas) | A06 | Media | Trivy / npm audit | No |
| H-15 | **Sin política de contraseñas** en backend (mín. 12, mayúsc., minúsc., número y símbolo). | `users.js:22-36` (sin validación) | Restricción §2.4 | A07 | Media | PT-SEG-001 | No |
| H-16 | **Token JWT en `localStorage`**, expuesto a robo por XSS. | `AuthContext.jsx:8,32` | NFR-SEG-9 | A05, A07 | Media | PT-SEG-005 | No |
| H-17 | **Descarga de documentos sin autenticación ni verificación de empresa:** `GET /contratos/:id/file` devuelve el documento de cualquier contrato por ID secuencial. | `contracts.js:413-432` (sin llamada a verificación de token) | RB-2, NFR-SEG-4, NFR-SEG-8 | A01 | Crítica | PT-SEG-009 | No |
| H-18 | **RF-5.5 no implementado:** no existe código ni ruta para generar o revocar un enlace compartido (sin coincidencias de `compart`/`share`/`enlace` en `routes/` ni en `openapi.json`). | búsqueda en `BACKEND/src/routes/*.js` y `openapi.json` | RF-5.5 | A04 | Alta | PT-FUNC-009 | No |
| H-19 | **Auditoría expuesta y manipulable:** `GET /auditoria` lista **todos** los registros de todas las empresas sin autenticación; `POST /auditoria` permite escribir entradas arbitrarias a un usuario autenticado. | `audit.js:20-34` y `37-47` | RF-6.1, NFR-SEG-6, RB-2 | A01, A09 | Alta | PT-FUNC-010, PT-SEG-009 | No |

## Resumen preliminar

| Severidad | Cantidad |
|-----------|----------|
| Crítica | 4 (H-01, H-02, H-12, H-17) |
| Alta | 9 (H-03, H-04, H-05, H-08, H-09, H-11, H-13, H-18, H-19) |
| Media | 6 (H-06, H-07, H-10, H-14, H-15, H-16) |
| **Total** | **19** |

## Comparación con criterios normativos (insumo para EP4-IE6)

| Hallazgo(s) | Criterio legal / normativo | Lectura |
|-------------|----------------------------|---------|
| H-01, H-13, H-09, H-11 | Ley 19.628 art. 11 (deber de cuidado del banco de datos); Ley 21.719 (obligaciones de seguridad) | Contraseñas, datos bancarios y tránsito sin protección comprometen el deber de resguardo de datos personales. |
| H-02, H-12, H-17, H-19 | ISO/IEC 25010 *Seguridad → Confidencialidad/Autenticidad*; OWASP A01 | Un editor o un tercero puede operar sobre datos de otra empresa: incumple el aislamiento exigido por RB-2. |
| H-07, H-10 | OWASP A05/A09; NFR-SEG-6 | Configuración insegura y exposición de detalles internos. |
| H-05, H-04 | ISO/IEC 25010 *Eficiencia de desempeño / Fiabilidad* | Umbral de 300 ms vs. 4 s medidos en código. |

> **Importante para la defensa:** estos hallazgos provienen de lectura de código. No afirmar en el informe "se explotó" ni "se verificó en ejecución" hasta tener la evidencia en `06-Evidencias/`.
