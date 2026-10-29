# 6. Diseño de Casos de Prueba

Se diseñaron **30 casos** que cubren los 42 requerimientos del ERS y los 2 criterios de interfaz (ver Anexo A). Se detallan completamente **8 casos representativos**, uno por cada tipo de prueba (§6.2–6.9); los 22 restantes se presentan en fichas resumidas (§6.10). Los 8 detallados superan el mínimo de 5 exigido.

## 6.1 Convenciones y entorno

| Elemento | Valor | Fuente |
|---|---|---|
| API | `http://localhost:4450` (variable `$API`) | `docker-compose.yml` (`PORT_BACKEND`) |
| Frontend | `http://localhost:3350` | `docker-compose.yml` (`PORT_FRONTEND`) |
| Documentación | `http://localhost:4450/docs` (Swagger) | `app.js:40` |
| Base de datos | contenedor `atlas-postgres`, usuario `postgres`, BD `atlas` | `docker-compose.yml` |
| Usuarios semilla | `admin` (rol administrador, empresa 1 «Altavia»); `editor` (rol editor) | `sql/dump-atlas.sql:344-355` |
| Autenticación | `Authorization: Bearer <token>` obtenido en `POST /autenticacion/login` | `auth.js` |

```bash
API=http://localhost:4450
TOKEN_ADMIN=$(curl -s -X POST $API/autenticacion/login -H 'Content-Type: application/json' \
  -d '{"nombre_usuario":"admin","password":"admin"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')
```

**Reglas de diseño.** (1) El resultado esperado se deriva **del ERS**, nunca del comportamiento actual del código. (2) Los criterios de aceptación son medibles. (3) Los datos son ficticios. (4) El apartado «Hipótesis previa» proviene del análisis estático (sección 9) y **no es un resultado**: la prueba debe confirmarla o refutarla.

Campos de cada caso (según pauta): ID · descripción · requerimiento asociado · datos de entrada · resultado esperado · criterios de aceptación · tipo de prueba. Se agregan procedimiento, herramienta y evidencia para que sea reproducible.

---

## 6.2 PT-FUNC-001 — Flujo completo de contrato con documento

| Campo | Contenido |
|---|---|
| **ID** | PT-FUNC-001 |
| **Descripción** | Verificar que un administrador crea un cliente y un contrato asociado a ese cliente, adjunta un documento de formato permitido, lo recupera y que la acción queda auditada; y que formatos no permitidos son rechazados. |
| **Requerimientos** | RF-5.1, RF-5.2, RF-5.3, RB-3 (apoyo: RF-6.1) |
| **Tipo de prueba** | Funcional — extremo a extremo (API + verificación en BD) |
| **Herramienta** | curl / Newman; `psql` en el contenedor |
| **Prioridad** | P1 |

**Datos de entrada**
- Cliente: `nombre="Cliente Prueba SpA"`, `correo="prueba@atlasfake.com"` (el correo del cliente es único en la BD).
- Contrato: `titulo="Servicios 2026"`, `descripcion="Contrato de prueba"`, `fecha_inicio=2026-01-01`, `fecha_fin=2026-12-31`, `cliente_id=<id del cliente>`.
- Archivos: `contrato.pdf` (< 1 MB), `foto.png`, `macro.exe` (no permitido), `grande.pdf` (≈ 30 MB).

**Procedimiento**
1. `POST /clientes` con `TOKEN_ADMIN` → obtener `cliente_id`.
2. `POST /contratos` (multipart: campos + `file=contrato.pdf`) → obtener `contrato_id`.
3. `GET /contratos/{contrato_id}` y `GET /contratos/{contrato_id}/file` (con token) → comparar bytes con el original (`sha256sum`).
4. `POST /contratos` con `file=macro.exe` y, por separado, con `file=grande.pdf`.
5. Consulta BD: `SELECT contract_id, length(document) FROM documentos_contrato WHERE contract_id=<id>;`
6. `GET /auditoria` y buscar `CONTRATOS_CREAR`.
7. Intentar un segundo `POST /contratos` con un `cliente_id` inexistente.

**Resultado esperado (según ERS)**
- Paso 2: HTTP 201; el contrato queda asociado a **un único** cliente (RB-3).
- Paso 3: el archivo descargado es idéntico al subido (hash igual).
- Paso 4: `.exe` rechazado con 4xx (RF-5.2 admite solo PDF, DOC, PPT, JPG, PNG); el archivo excesivo se rechaza con 413 o 400.
- Paso 5: el documento se almacena en el storage interno y la BD guarda la **referencia** (RF-5.3).
- Paso 6: existe un registro de auditoría de la creación y de la subida del documento (RF-6.1).
- Paso 7: error 4xx con mensaje controlado; no se crea contrato huérfano.

**Criterios de aceptación**
- [ ] Contrato creado con respuesta 201 y asociado a un solo cliente.
- [ ] Hash del archivo recuperado = hash del original.
- [ ] Solo los 5 formatos del ERS son aceptados; `.exe` devuelve 4xx.
- [ ] Existe límite de tamaño y se aplica.
- [ ] Subida y descarga ≤ 10 s (criterio de aceptación de RF-5).
- [ ] Registro de auditoría presente por cada acción crítica.

**Hipótesis previa (no resultado):** H-08 — `multer` sin `fileFilter` ni `limits` (`contracts.js:14-15`) y documento guardado como `bytea` en la BD (`contracts.js:44-47`) sugieren que `.exe` y el archivo grande serían aceptados y que RF-5.3 se incumple. H-12 — `POST /contratos` no valida token ni pertenencia.
**Evidencia:** `06-Evidencias/PT-FUNC-001_01…06`.

---

## 6.3 PT-SEG-001 — Hashing de contraseñas y política de contraseñas

| Campo | Contenido |
|---|---|
| **ID** | PT-SEG-001 |
| **Descripción** | Comprobar que las contraseñas se almacenan con hash bcrypt (con sal y costo adecuado), que el sistema impone la política de contraseñas del ERS y que el login funciona sin exponer el valor almacenado. |
| **Requerimientos** | NFR-SEG-2; restricción ERS §2.4 (política de contraseñas, bcrypt) |
| **Tipo de prueba** | Seguridad — confidencialidad (SAST + inspección de BD + prueba de API) |
| **Herramienta** | SonarQube / Semgrep (SAST), `psql`, curl |
| **Prioridad** | P1 (crítica) |

**Datos de entrada**
- Usuarios existentes: `admin`, `editor`.
- Contraseña débil: `abc` · contraseña sin símbolo: `Atlas2026Segura` · contraseña conforme: `Atlas#2026-Segura`.
- Payload de alta: `POST /usuarios {"nombre_usuario":"qa_hash","contrasena_hash":"<contraseña>","correo":"qa_hash@atlasfake.com"}`.

**Procedimiento**
1. SAST: buscar uso de `bcrypt`/`argon2` en `BACKEND/` y en `package.json`.
2. `docker exec atlas-postgres psql -U postgres -d atlas -c "SELECT nombre_usuario, contrasena_hash FROM usuarios;"`.
3. Registrar los usuarios con las tres contraseñas.
4. Consultar de nuevo la BD para el usuario recién creado.
5. Login correcto e incorrecto con `qa_hash`.

**Resultado esperado**
- Paso 1: dependencia y llamadas de hashing presentes.
- Paso 2 y 4: columna con formato bcrypt (`$2a$/$2b$/$2y$`), costo ≥ 10; **ninguna** contraseña legible.
- Paso 3: `abc` y `Atlas2026Segura` rechazadas (política: ≥ 12 caracteres con mayúscula, minúscula, número y símbolo); `Atlas#2026-Segura` aceptada.
- Paso 5: correcta → 200 con token; incorrecta → 401 con mensaje genérico.

**Criterios de aceptación**
- [ ] 100 % de los registros de `usuarios` tienen hash bcrypt con costo ≥ 10.
- [ ] Dos usuarios con la misma contraseña producen hashes distintos (sal).
- [ ] Contraseñas que incumplen la política son rechazadas por el **backend**.
- [ ] Ninguna respuesta ni log contiene la contraseña.

**Hipótesis previa:** H-01/H-15 — `auth.js:26` compara `contrasena_hash !== password` y el dump semilla guarda `'admin'` y `'editor'` en esa columna (`dump-atlas.sql:344-345`); sin `bcrypt` en dependencias. Se espera **fallo crítico**.
**Evidencia:** captura SAST, salida de `psql`, respuestas HTTP.

---

## 6.4 PT-SEG-002 — Control de acceso por rol en el backend (RBAC)

| Campo | Contenido |
|---|---|
| **ID** | PT-SEG-002 |
| **Descripción** | Verificar que el backend, y no solo la interfaz, impide que el rol *editor* cree, modifique o elimine datos, y que el *administrador* conserva acceso completo. |
| **Requerimientos** | NFR-SEG-4, RF-3.2, RB-4, RB-5 |
| **Tipo de prueba** | Seguridad — autorización (caja negra por API + inspección del token) |
| **Herramienta** | curl / Newman, decodificación de JWT, DevTools |
| **Prioridad** | P1 (crítica) |

**Datos de entrada**
- `TOKEN_ADMIN` (admin/admin) y `TOKEN_EDITOR` (editor/editor).
- Un cliente `C1` y un contrato `K1` creados por el administrador.
- Operaciones: `GET /clientes`, `POST /clientes`, `PUT /clientes/{C1}`, `DELETE /clientes/{C1}`, `POST /contratos`, `DELETE /contratos/{K1}`, `POST /empresa-usuarios`, `DELETE /usuarios/{id}`.

**Procedimiento**
1. Decodificar el payload de ambos JWT y comprobar si incluyen el rol.
2. Ejecutar la lista de operaciones con `TOKEN_EDITOR`.
3. Repetir con `TOKEN_ADMIN`.
4. En el frontend, iniciar sesión como `editor`, editar `localStorage.role = "administrador"`, recargar e intentar crear un cliente.

**Resultado esperado**
- Editor: `GET` → 200; todas las operaciones de escritura → **403**, con cuerpo genérico.
- Administrador: lectura y escritura permitidas (2xx).
- Paso 4: aunque se altere el rol en el navegador, el servidor rechaza la operación.
- El token contiene el rol y el servidor lo valida, o lo consulta en `empresa_usuarios`.

**Criterios de aceptación**
- [ ] 0 operaciones de escritura exitosas con rol editor (de 8 intentos).
- [ ] 100 % de operaciones permitidas para administrador.
- [ ] La autorización se decide en el servidor.
- [ ] Respuestas 403 sin detalles internos.

**Hipótesis previa:** H-02 — el token no incluye rol (`auth.js:42-51`), ni `clients.js`, `contracts.js` ni `users.js` consultan rol, y el front protege con `RequireAdmin` y un rol leído de `localStorage` con valor por defecto `"administrador"` (`AuthContext.jsx:15`; `App.jsx:39-45`). Se espera **fallo crítico**.

---

## 6.5 PT-SEG-005 — Inyección SQL, XSS, CSRF y validación de entrada

| Campo | Contenido |
|---|---|
| **ID** | PT-SEG-005 |
| **Descripción** | Verificar la resistencia a inyección SQL, XSS almacenado y CSRF, y la validación del lado del servidor, incluyendo cabeceras de seguridad y limitación de intentos de login. |
| **Requerimientos** | NFR-SEG-5; ERS §3.1.2 (validación server-side) |
| **Tipo de prueba** | Seguridad — DAST (OWASP ZAP baseline) + pruebas manuales |
| **Herramienta** | OWASP ZAP, curl, navegador, SonarQube |
| **Prioridad** | P1 |

**Datos de entrada**
- SQLi: `name=' OR '1'='1` en `GET /clientes/search`; login con `nombre_usuario = "admin' --"`.
- XSS: cliente con `nombre = <img src=x onerror=alert(1)>` y contrato con `descripcion = <script>alert(1)</script>`.
- Campos inválidos: `correo="no-es-correo"`, `fecha_fin < fecha_inicio`, `nombre` de 10 000 caracteres, cuerpo JSON mal formado.
- CSRF: comprobar el mecanismo de sesión (¿cookies o cabecera Bearer?).
- Fuerza bruta: 10 intentos de login fallidos consecutivos.

**Procedimiento**
1. Ejecutar ZAP baseline contra `$API` y el frontend; exportar el informe.
2. Enviar los payloads SQLi y XSS; abrir el front y observar si el script se ejecuta.
3. Enviar los campos inválidos a `POST /clientes` y `POST /contratos`.
4. `curl -I $API/` y revisar cabeceras (`Content-Security-Policy`, `X-Content-Type-Options`, `Strict-Transport-Security`, `Access-Control-Allow-Origin`).
5. Medir si el login se bloquea o retrasa tras intentos fallidos repetidos.

**Resultado esperado**
- SQLi: sin datos extra ni error SQL; consultas parametrizadas.
- XSS: ningún script se ejecuta; la entrada se sanea o se codifica en la salida.
- Entradas inválidas: 400 con mensaje controlado; no se persisten datos inválidos.
- CSRF: sesión por cabecera Bearer (sin cookies) o presencia de token anti-CSRF.
- Cabeceras de seguridad presentes; CORS restringido a orígenes autorizados; bloqueo o retardo creciente tras intentos fallidos.

**Criterios de aceptación**
- [ ] 0 alertas ZAP de riesgo Alto; alertas Medias justificadas.
- [ ] 0 ejecuciones de script en el navegador.
- [ ] 100 % de entradas inválidas rechazadas por el servidor.
- [ ] Cabeceras mínimas de seguridad presentes.
- [ ] Existe limitación de intentos de autenticación.

**Hipótesis previa:** las consultas leídas usan parámetros (`$1`), por lo que se espera **aprobar SQLi**; H-10 (CORS abierto `app.js:22`, sin `helmet` ni límite de intentos) y H-07 sugieren fallos en cabeceras y limitación de intentos; H-16 (token en `localStorage`) agrava el impacto de un XSS.

---

## 6.6 PT-PERF-001 — Tiempo de respuesta de operaciones CRUD

| Campo | Contenido |
|---|---|
| **ID** | PT-PERF-001 |
| **Descripción** | Medir la latencia de las operaciones CRUD simples bajo carga normal y compararla con el umbral del ERS. |
| **Requerimientos** | NFR-PERF-1 (apoyo: NFR-USAB-2) |
| **Tipo de prueba** | Rendimiento — carga |
| **Herramienta** | k6 (`03-Anexos/Herramientas/k6/crud_latencia.js`) |
| **Prioridad** | P2 |

**Datos de entrada**
- Carga normal definida para el caso: **20 usuarios virtuales durante 2 minutos**, con *think time* de 1 s.
- Endpoints: `GET /clientes`, `GET /clientes/{id}`, `POST /clientes`, `PUT /clientes/{id}`, `DELETE /clientes/{id}`, `GET /contratos`; y `POST /autenticacion/login` medido por separado.
- BD con los datos semilla más 1 000 clientes generados.

**Procedimiento**
1. Poblar la BD de prueba y obtener un token por usuario virtual.
2. Ejecutar k6 con los umbrales: `http_req_duration p(95) < 300` y `http_req_failed < 1 %`.
3. Registrar promedio, p(95), p(99) y tasa de error por endpoint.
4. Repetir `POST /autenticacion/login` 30 veces y medir latencia.

**Resultado esperado:** p(95) < 300 ms en cada endpoint CRUD; tasa de errores < 1 %.

**Criterios de aceptación**
- [ ] p(95) < 300 ms para todos los endpoints CRUD simples.
- [ ] Error 5xx < 1 %.
- [ ] El login también cumple el umbral (operación simple del ERS).

**Hipótesis previa:** H-05 — `await delay(4000)` en `auth.js:17` y `contracts.js:75` implica latencia ≈ 4 000 ms en login y `GET /contratos`. Se espera **fallo** en esos endpoints.
**Nota metodológica:** el entorno es local; las cifras no se extrapolan a producción y se reportan junto con las características del equipo.

---

## 6.7 PT-USAB-001 — Accesibilidad para adultos mayores (WCAG 2.1 AA)

| Campo | Contenido |
|---|---|
| **ID** | PT-USAB-001 |
| **Descripción** | Evaluar si el login, el registro y las pantallas principales son legibles y operables por adultos mayores, con criterios WCAG 2.1 AA. |
| **Requerimientos** | NFR-USAB-1; criterio ERS §3.1.1 |
| **Tipo de prueba** | Usabilidad / accesibilidad |
| **Herramienta** | Lighthouse, axe DevTools, revisión manual de teclado, cuestionario SUS |
| **Prioridad** | P2 |

**Datos de entrada**
- URLs: `/login`, `/registro`, `/home`, `/clientes`, `/contratos`.
- Participantes: hasta 5 adultos mayores (≥ 60 años). Si no es posible, 1–2 participantes más revisión heurística; la limitación se documenta.
- Tareas: iniciar sesión; crear un cliente; ubicar el contrato de ese cliente.

**Procedimiento**
1. Lighthouse (categoría Accesibilidad) y axe en cada URL.
2. Navegación completa solo con teclado (Tab/Shift+Tab/Enter/Esc); verificar foco visible y ausencia de trampas.
3. Medir contraste y tamaño de fuente base; ampliar el zoom al 200 %.
4. Tareas con usuarios: tiempo, errores, ayudas solicitadas; aplicar SUS.

**Resultado esperado:** puntaje Lighthouse accesibilidad ≥ 90; 0 incidencias axe críticas o serias; contraste ≥ 4,5:1; tarea completada sin bloqueos mayores.

**Criterios de aceptación**
- [ ] Lighthouse Accesibilidad ≥ 90 en las 5 URLs.
- [ ] 0 incidencias *critical/serious* en axe.
- [ ] Contraste de texto ≥ 4,5:1; tamaño de fuente base ≥ 12 px (mínimo del ERS), con observación si es < 16 px.
- [ ] Objetivos táctiles ≥ 44×44 px y campos con `label`/ARIA.
- [ ] SUS promedio ≥ 70 y sin bloqueos mayores.

---

## 6.8 PT-COMP-001 — Responsividad en móviles y tablets

| Campo | Contenido |
|---|---|
| **ID** | PT-COMP-001 |
| **Descripción** | Verificar que las pantallas principales se adaptan a móviles y tablets sin pérdida de funcionalidad. |
| **Requerimientos** | NFR-COMPAT-2 (apoyo: NFR-PERF-2) |
| **Tipo de prueba** | Compatibilidad — responsiva |
| **Herramienta** | DevTools (emulación de dispositivo), 1 dispositivo físico si está disponible, Lighthouse móvil |
| **Prioridad** | P3 |

**Datos de entrada**
- Resoluciones: 360×780, 390×844, 820×1180, 1366×768 (referencia).
- Páginas: `/login`, `/registro`, `/home`, `/clientes`, `/clientes/nuevo`, `/contratos`, `/contratos/{id}`.

**Procedimiento:** para cada resolución recorrer las páginas, crear un cliente y abrir un contrato; verificar desbordes, menú y legibilidad; ejecutar Lighthouse con perfil móvil.

**Resultado esperado:** diseño adaptable, sin scroll horizontal, menú accesible, formularios completables y tablas legibles.

**Criterios de aceptación**
- [ ] 0 desbordes horizontales en las 4 resoluciones.
- [ ] Flujos críticos (login, crear cliente, ver contrato) completables en móvil.
- [ ] Elementos táctiles ≥ 44×44 px sin solapamientos.

---

## 6.9 PT-DIS-001 — Disponibilidad, respaldo y recuperación

| Campo | Contenido |
|---|---|
| **ID** | PT-DIS-001 |
| **Descripción** | Verificar la recuperación ante caída de contenedores, la persistencia de datos y la existencia de un procedimiento de respaldo y restauración funcional. |
| **Requerimientos** | NFR-DIS-1, NFR-DIS-2, NFR-SEG-7 |
| **Tipo de prueba** | Disponibilidad / recuperación |
| **Herramienta** | Docker CLI, `pg_dump`/`psql` |
| **Prioridad** | P2 |

**Datos de entrada:** stack en ejecución con datos semilla; objetivos propuestos por el equipo (el ERS no los fija): **RTO ≤ 15 min** y **RPO = último respaldo**.

**Procedimiento**
1. `docker kill atlas-backend` y medir el tiempo hasta que `GET /` responda (política `restart: unless-stopped`).
2. `docker compose down` (sin `-v`) y `up`; comprobar que los datos persisten.
3. `docker exec atlas-postgres pg_dump -U postgres atlas > respaldo.sql`.
4. Eliminar un cliente de prueba; restaurar en una BD vacía y comparar conteos por tabla.
5. Revisar el repositorio en busca de política o procedimiento de respaldo documentado.
6. Calcular el presupuesto de indisponibilidad: 99,5 % mensual ≈ 3,6 h.

**Resultado esperado:** reinicio automático del backend; datos persistentes; respaldo restaurable con conteos idénticos; política de respaldo definida y documentada.

**Criterios de aceptación**
- [ ] El backend se recupera sin intervención manual en ≤ 15 min.
- [ ] 100 % de los registros se conservan tras `down`/`up`.
- [ ] La restauración reproduce los conteos de todas las tablas.
- [ ] Existe un documento de política de respaldo y recuperación.
- [ ] Se documenta la limitación: el 99,5 % mensual no puede medirse en el período de prueba.

**Hipótesis previa:** no se encontró en el repositorio ninguna mención a respaldos (búsqueda de `backup|respaldo|pg_dump`), por lo que el último criterio probablemente falle (NFR-SEG-7).

---

## 6.10 Fichas resumidas de los 22 casos restantes

Todas siguen la misma convención; el detalle completo se desarrolla al ejecutarlas (sección 8).

| Caso | Requerimiento | Procedimiento resumido | Resultado esperado (ERS) | Criterio de aceptación | Tipo |
|---|---|---|---|---|---|
| PT-FUNC-002 | RF-1.1 | `POST /autenticacion/login` con credenciales válidas, inválidas y vacías | Válidas → 200 con JWT; inválidas → 401 genérico | JWT con `exp` presente; 100 % de inválidas rechazadas | Funcional |
| PT-FUNC-003 | RF-1.2 | Cerrar sesión; reutilizar el mismo token en `GET /clientes` | Token revocado: 401 tras logout | 0 usos válidos del token posterior al logout | Funcional / Seguridad |
| PT-FUNC-004 | RF-2.1, RB-1 | `POST /usuarios` y `POST /empresas` con correo nuevo y repetido | Alta correcta; correo duplicado rechazado con 4xx | 0 correos principales duplicados entre empresas | Funcional |
| PT-FUNC-005 | RF-2.2, RF-2.3 | `POST /empresas` con `{usuario, empresa}`; consultar `empresa_usuarios` | Empresa creada; primer usuario con rol administrador (rol_id 1) | Rol = administrador; el usuario ve el dashboard | Funcional |
| PT-FUNC-006 | RF-3.1, RF-3.3 | Como admin: `POST /empresa-usuarios` (rol 1 y 2), `PUT`, `DELETE` | Usuarios creados con rol asignado; modificables y eliminables solo por admin | Roles correctos; operaciones registradas en auditoría | Funcional |
| PT-FUNC-007 | RF-4.1, RF-4.3 | `POST /clientes` con datos válidos e inválidos (RUT, correo, teléfono alfanumérico) | Válidos → 201; inválidos → 400 con mensaje | 100 % de inválidos rechazados; mensajes en español | Funcional |
| PT-FUNC-008 | RF-4.2 | Listar con paginación y filtro; editar; eliminar con confirmación y verificar en BD | Paginación y filtro correctos; **eliminación lógica**, registro conservado | El registro sigue en BD con marca de baja; UI pide confirmación | Funcional |
| PT-FUNC-009 | RF-5.4, RF-5.5 | Contratos con fechas pasadas, próximas y vigentes; `GET /contratos/estados`; intentar generar y revocar enlace compartido | Estado calculado (activo / por vencer / expirado); enlace generado y revocable | Estado coincide con fechas en 100 % de casos; existe función de enlace | Funcional / Seguridad |
| PT-FUNC-010 | RF-6.1 | Ejecutar crear/editar/eliminar sobre clientes, contratos y usuarios; subir y descargar documentos; leer `/auditoria` | Un registro por acción con usuario, acción y fecha | 100 % de acciones críticas auditadas | Funcional |
| PT-FUNC-011 | ERS §3.1.2 | Ejecutar `openapi.json` con Newman | Colección con pruebas básicas sobre endpoints críticos | ≥ 80 % de los 38 endpoints cubiertos; 0 fallos de contrato | Funcional (API) |
| PT-SEG-003 | NFR-SEG-1 | `curl -I http://…`, `testssl.sh`/ZAP sobre el endpoint, revisar nginx | HTTPS obligatorio; HTTP redirige; TLS ≥ 1.2 | 0 endpoints servidos en HTTP plano | Seguridad |
| PT-SEG-004 | NFR-SEG-3 | Inspeccionar columnas con datos bancarios en BD y volumen de disco | Datos sensibles cifrados en reposo | `numero_cuenta` no legible en la BD | Seguridad |
| PT-SEG-006 | NFR-SEG-6 | Forzar errores (JSON inválido, ID inexistente, caída de BD); revisar respuestas y logs | Respuestas genéricas; detalle solo en logs internos; logs sin secretos | 0 respuestas con `err.message` ni consultas SQL | Seguridad |
| PT-SEG-007 | NFR-SEG-8 | Revisar datos personales almacenados, acceso, retención, consentimiento, secretos en repositorio (Gitleaks) | Tratamiento conforme a Ley 19.628 (y 21.719 si aplica) | Lista de verificación legal completa; 0 secretos en código | Seguridad / Normativo |
| PT-SEG-008 | NFR-SEG-9 | Token expirado, firma alterada, `alg: none`, secreto por defecto (`inseguro`) | Token inválido rechazado; secreto robusto | 100 % de tokens manipulados rechazados | Seguridad |
| PT-SEG-009 | RB-2 | Con usuario de empresa B, acceder por ID a clientes/contratos/documentos y a `/auditoria` de la empresa A | 403/404; sin datos de otra empresa | 0 recursos de otra empresa accesibles | Seguridad |
| PT-PERF-002 | NFR-PERF-2 | Lighthouse (perfil móvil, 4G simulada) sobre la página principal | Carga < 2 s | LCP < 2 s | Rendimiento |
| PT-PERF-003 | NFR-PERF-3 | k6 con rampa a 200 usuarios concurrentes durante 5 min | Sistema estable | Error 5xx < 1 %; sin caída del servicio | Rendimiento (carga / estrés) |
| PT-PERF-004 | Criterio RF-5 | Subir y descargar un PDF de 5 MB, 10 repeticiones | Subida y descarga ≤ 10 s | 100 % de operaciones ≤ 10 s | Rendimiento |
| PT-USAB-002 | NFR-USAB-2, NFR-USAB-4 | Recorrer registro → crear empresa; acceder a cliente → ver sus contratos | Flujos claros y secuenciales | Tareas completadas sin ayuda; ruta cliente → contratos disponible | Usabilidad |
| PT-USAB-003 | NFR-USAB-3 | Provocar errores de formulario; buscar ayuda contextual | Mensajes amigables en español y ayuda disponible | 100 % de errores con causa y acción; ayuda contextual presente | Usabilidad |
| PT-COMP-002 | NFR-COMPAT-1 | Ejecutar los flujos críticos en Chrome, Firefox, Edge y Safari (últimas 2 versiones) | Funcionalidad idéntica | 0 fallos funcionales por navegador | Compatibilidad |

**Resultado esperado de las pruebas de seguridad (PT-SEG-003…009):** al estar el sistema declarado «intencionalmente vulnerable», se anticipa que varias fallarán; es resultado válido y se registra como incidente con su criticidad (sección 8).
