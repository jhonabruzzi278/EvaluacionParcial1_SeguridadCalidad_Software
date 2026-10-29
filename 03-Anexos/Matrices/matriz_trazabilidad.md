# Anexo: Matriz de Trazabilidad v2 (reconstruida contra el ERS)

**Fuente de verdad:** `01-Documentos_Base/SRS_Atlas_384735328.pdf` v1.1 (§3.2 RF, §3.3 NFR, §3.4 RB).
**Cambio respecto de v1:** la v1 contaba 6 "RF" y describía varios NFR/RB de forma distinta al ERS. Esta versión usa los **42 requerimientos reales** (17 RF + 20 NFR + 5 RB) más los 2 criterios de aceptación de interfaz (§3.1.1 y §3.1.2). Cobertura objetivo exigida por EP3: **100 %**.

**Estado:** `Pendiente` = diseñado, aún no ejecutado. No se ha ejecutado ninguna prueba dinámica; los resultados reales deben registrarse en `02-Informe/08-Ejecucion_Pruebas/registro_ejecucion.md`.
**Columna "Hallazgo estático":** señala un incumplimiento *probable* según `09-Analisis_Estatico`; es una hipótesis que la prueba debe confirmar o refutar, no un resultado.

## 1. Requerimientos funcionales (17)

| ID ERS | Requerimiento (resumen del ERS) | Caso(s) | Tipo | Hallazgo estático | Estado |
|---|---|---|---|---|---|
| RF-1.1 | Autenticación con nombre_usuario y contraseña; login genera JWT | PT-FUNC-002 | Funcional | H-05 | Pendiente |
| RF-1.2 | Cierre de sesión y revocación de tokens | PT-FUNC-003 | Funcional / Seguridad | H-04 | Pendiente |
| RF-2.1 | Registro con usuario, contraseña y correo | PT-FUNC-004 | Funcional | H-15 | Pendiente |
| RF-2.2 | Usuario registrado crea empresa (nombre, dirección, teléfono, correo) | PT-FUNC-005 | Funcional | — | Pendiente |
| RF-2.3 | Primer usuario de la empresa obtiene rol administrador | PT-FUNC-005 | Funcional | — | Pendiente |
| RF-3.1 | Administrador crea/invita usuarios y asigna rol | PT-FUNC-006 | Funcional | H-02 | Pendiente |
| RF-3.2 | Rol editor solo visualiza | PT-SEG-002 | Seguridad (autorización) | H-02 | Pendiente |
| RF-3.3 | Administrador modifica o elimina usuarios | PT-FUNC-006 | Funcional | H-06 | Pendiente |
| RF-4.1 | Crear clientes (nombre, descripción, dirección, contacto) | PT-FUNC-007 | Funcional | — | Pendiente |
| RF-4.2 | Editar, eliminar y listar clientes (paginación, filtro por nombre) | PT-FUNC-008 | Funcional | H-06 | Pendiente |
| RF-4.3 | Validaciones de campos y formato | PT-FUNC-007 | Funcional | — | Pendiente |
| RF-5.1 | Crear contratos asociados a cliente (título, descripción, fechas) | PT-FUNC-001 | Funcional (E2E) | H-12 | Pendiente |
| RF-5.2 | Adjuntar un documento por contrato (PDF, DOC, PPT, JPG, PNG) | PT-FUNC-001 | Funcional | H-08 | Pendiente |
| RF-5.3 | Documentos en storage interno referenciado en BD | PT-FUNC-001 | Funcional | H-08 | Pendiente |
| RF-5.4 | Estado del contrato (activo / vence / expirado) por fechas | PT-FUNC-009 | Funcional | — | Pendiente |
| RF-5.5 | Generar enlace para compartir el documento y gestionar su acceso | PT-FUNC-009 | Funcional / Seguridad | H-18 | Pendiente |
| RF-6.1 | Auditar acciones críticas (crear/editar/eliminar; subir/descargar documentos) | PT-FUNC-010 | Funcional | H-19 | Pendiente |

## 2. Seguridad (9)

| ID ERS | Requerimiento | Caso(s) | Tipo | Hallazgo estático | Estado |
|---|---|---|---|---|---|
| NFR-SEG-1 | TLS obligatorio en todas las comunicaciones | PT-SEG-003 | Seguridad (DAST/config.) | H-09 | Pendiente |
| NFR-SEG-2 | Contraseñas con hashing seguro (bcrypt) | PT-SEG-001 | Seguridad (SAST + BD) | H-01, H-15 | Pendiente |
| NFR-SEG-3 | Encriptación de datos sensibles en reposo | PT-SEG-004 | Seguridad (BD) | H-13 | Pendiente |
| NFR-SEG-4 | Control de acceso por rol en backend | PT-SEG-002 | Seguridad (autorización) | H-02 | Pendiente |
| NFR-SEG-5 | Protección CSRF, XSS, SQL Injection; validación y saneamiento de entrada | PT-SEG-005 | Seguridad (DAST) | H-08, H-10, H-16 | Pendiente |
| NFR-SEG-6 | Gestión de log segura | PT-SEG-006 | Seguridad | H-07 | Pendiente |
| NFR-SEG-7 | Políticas de respaldo y recuperación | PT-DIS-001 | Disponibilidad / Recuperación | — | Pendiente |
| NFR-SEG-8 | Cumplimiento de protección de datos personales | PT-SEG-007 | Seguridad / Normativo | H-01, H-11, H-13 | Pendiente |
| NFR-SEG-9 | Manejo de sesión con JWT | PT-SEG-008 | Seguridad (sesión) | H-03, H-16 | Pendiente |

## 3. Rendimiento (3 + criterio RF-5)

| ID ERS | Requerimiento | Caso(s) | Tipo | Hallazgo estático | Estado |
|---|---|---|---|---|---|
| NFR-PERF-1 | CRUD simples < 300 ms bajo carga normal | PT-PERF-001 | Rendimiento (carga) | H-05 | Pendiente |
| NFR-PERF-2 | Página principal < 2 s en conexión móvil promedio | PT-PERF-002 | Rendimiento (frontend) | — | Pendiente |
| NFR-PERF-3 | 200 usuarios concurrentes (por defecto) | PT-PERF-003 | Rendimiento (carga/estrés) | H-05 | Pendiente |
| Criterio RF-5 | Subida y descarga ≤ 10 s | PT-PERF-004 | Rendimiento | H-08 | Pendiente |

## 4. Usabilidad y accesibilidad (4)

| ID ERS | Requerimiento | Caso(s) | Tipo | Estado |
|---|---|---|---|---|
| NFR-USAB-1 | Tipografía legible, contraste y controles grandes (mayores) | PT-USAB-001 | Usabilidad / Accesibilidad | Pendiente |
| NFR-USAB-2 | Flujos claros de registro y creación de empresa | PT-USAB-002 | Usabilidad | Pendiente |
| NFR-USAB-3 | Ayuda contextual y mensajes de error amigables | PT-USAB-003 | Usabilidad | Pendiente |
| NFR-USAB-4 | Flujo cliente → contratos del cliente | PT-USAB-002 | Usabilidad | Pendiente |

## 5. Disponibilidad y mantenimiento (2)

| ID ERS | Requerimiento | Caso(s) | Tipo | Estado |
|---|---|---|---|---|
| NFR-DIS-1 | Disponibilidad objetivo 99,5 % mensual | PT-DIS-001 | Disponibilidad | Pendiente |
| NFR-DIS-2 | Ventana de mantenimiento y migración segura | PT-DIS-001 | Disponibilidad / Mantenibilidad | Pendiente |

## 6. Compatibilidad (2)

| ID ERS | Requerimiento | Caso(s) | Tipo | Estado |
|---|---|---|---|---|
| NFR-COMPAT-1 | Últimas 2 versiones de Chrome, Firefox, Safari, Edge | PT-COMP-002 | Compatibilidad | Pendiente |
| NFR-COMPAT-2 | Responsivo para móviles y tablets | PT-COMP-001 | Compatibilidad | Pendiente |

## 7. Reglas de negocio (5)

| ID ERS | Regla (literal del ERS) | Caso(s) | Tipo | Hallazgo estático | Estado |
|---|---|---|---|---|---|
| RB-1 | Un mismo correo no puede existir en dos empresas como correo principal (si la política lo decide) | PT-FUNC-004 | Funcional | — | Pendiente |
| RB-2 | Solo usuarios con relación en `empresa_usuarios` ven o editan datos de la empresa | PT-SEG-009 | Seguridad (aislamiento) | H-12, H-17, H-19 | Pendiente |
| RB-3 | Un contrato se asocia únicamente a un cliente | PT-FUNC-001 | Funcional | — | Pendiente |
| RB-4 | Un editor solo tiene permisos de lectura | PT-SEG-002 | Seguridad (autorización) | H-02 | Pendiente |
| RB-5 | Un administrador tiene acceso completo (escritura, lectura, actualización, eliminación) | PT-SEG-002 | Seguridad / Funcional | — | Pendiente |

## 8. Criterios de aceptación de interfaz (ERS §3.1)

| Ref. | Criterio | Caso | Tipo | Estado |
|---|---|---|---|---|
| §3.1.1 | Pruebas con 5 usuarios mayores sin bloqueos mayores; accesibilidad básica | PT-USAB-001 | Usabilidad | Pendiente |
| §3.1.2 | Colección Swagger con tests básicos y cobertura de endpoints críticos | PT-FUNC-011 | Funcional (API) | Pendiente |

## 9. Catálogo de casos de prueba (30)

IDs en **negrita** = existían en EP1 (se conservan, con requerimientos corregidos). **★** = caso a detallar completo en el informe (ID, descripción, requerimiento, datos de entrada, resultado esperado, criterios de aceptación, tipo).

| Caso | Título | Tipo | Requerimientos | Detalle en informe |
|---|---|---|---|---|
| **PT-FUNC-001** | Flujo completo de contrato con documento | Funcional E2E | RF-5.1, RF-5.2, RF-5.3, RB-3 | ★ |
| PT-FUNC-002 | Autenticación y emisión de JWT | Funcional | RF-1.1 | |
| PT-FUNC-003 | Cierre de sesión y revocación de token | Funcional | RF-1.2 | |
| PT-FUNC-004 | Registro de usuario y unicidad de correo | Funcional | RF-2.1, RB-1 | |
| PT-FUNC-005 | Creación de empresa y rol admin por defecto | Funcional | RF-2.2, RF-2.3 | |
| PT-FUNC-006 | Alta, edición y baja de usuarios con rol | Funcional | RF-3.1, RF-3.3 | |
| PT-FUNC-007 | Creación de cliente y validaciones | Funcional | RF-4.1, RF-4.3 | |
| PT-FUNC-008 | Listar, filtrar, editar y eliminar (lógico) clientes | Funcional | RF-4.2 | |
| PT-FUNC-009 | Estado del contrato y enlace compartido | Funcional | RF-5.4, RF-5.5 | |
| PT-FUNC-010 | Registro de auditoría de acciones críticas | Funcional | RF-6.1 | |
| PT-FUNC-011 | Colección OpenAPI/Swagger ejecutable | Funcional (API) | §3.1.2 | |
| **PT-SEG-001** | Hashing de contraseñas y política de contraseñas | Seguridad | NFR-SEG-2 | ★ |
| **PT-SEG-002** | RBAC admin vs editor en backend | Seguridad | NFR-SEG-4, RF-3.2, RB-4, RB-5 | ★ |
| PT-SEG-003 | TLS y redirección HTTP→HTTPS | Seguridad | NFR-SEG-1 | |
| PT-SEG-004 | Cifrado de datos sensibles en reposo | Seguridad | NFR-SEG-3 | |
| PT-SEG-005 | Inyección SQL, XSS, CSRF, validación de entrada | Seguridad (DAST) | NFR-SEG-5 | ★ |
| PT-SEG-006 | Gestión segura de logs y errores | Seguridad | NFR-SEG-6 | |
| PT-SEG-007 | Cumplimiento de protección de datos personales | Seguridad / Normativo | NFR-SEG-8 | |
| PT-SEG-008 | Sesión JWT: expiración, firma, manipulación | Seguridad | NFR-SEG-9 | |
| PT-SEG-009 | Aislamiento entre empresas (IDOR) | Seguridad | RB-2 | |
| **PT-PERF-001** | Tiempo de respuesta CRUD < 300 ms | Rendimiento | NFR-PERF-1 | ★ |
| PT-PERF-002 | Carga de página principal < 2 s | Rendimiento | NFR-PERF-2 | |
| PT-PERF-003 | 200 usuarios concurrentes | Rendimiento (carga/estrés) | NFR-PERF-3 | |
| PT-PERF-004 | Subida/descarga de documento ≤ 10 s | Rendimiento | criterio RF-5 | |
| **PT-USAB-001** | Accesibilidad para adultos mayores (WCAG 2.1 AA) | Usabilidad | NFR-USAB-1, §3.1.1 | ★ |
| PT-USAB-002 | Flujo de registro/empresa y cliente→contratos | Usabilidad | NFR-USAB-2, NFR-USAB-4 | |
| PT-USAB-003 | Ayuda contextual y mensajes de error | Usabilidad | NFR-USAB-3 | |
| **PT-DIS-001** | Disponibilidad, respaldo y recuperación | Disponibilidad | NFR-DIS-1, NFR-DIS-2, NFR-SEG-7 | ★ |
| **PT-COMP-001** | Responsividad en móviles y tablets | Compatibilidad | NFR-COMPAT-2 | ★ |
| PT-COMP-002 | Compatibilidad entre navegadores | Compatibilidad | NFR-COMPAT-1 | |

★ = 8 casos detallados (uno por tipo de prueba), superando el mínimo de 5 exigido por la pauta.

## 10. Resumen de cobertura (verificable)

| Categoría | Total ERS | Con ≥1 caso | % |
|---|---|---|---|
| Requerimientos funcionales (RF) | 17 | 17 | 100 % |
| Seguridad (NFR-SEG) | 9 | 9 | 100 % |
| Rendimiento (NFR-PERF) | 3 | 3 | 100 % |
| Usabilidad (NFR-USAB) | 4 | 4 | 100 % |
| Disponibilidad (NFR-DIS) | 2 | 2 | 100 % |
| Compatibilidad (NFR-COMPAT) | 2 | 2 | 100 % |
| Reglas de negocio (RB) | 5 | 5 | 100 % |
| **TOTAL** | **42** | **42** | **100 %** |
| Criterios de interfaz §3.1 | 2 | 2 | 100 % |

> **Aclaración metodológica para la defensa (IE9/IE8):** "100 % de cobertura" significa que **cada requerimiento tiene al menos un caso diseñado** (cobertura de diseño). No significa que todos los casos pasen. La cobertura de *ejecución* y los resultados reales se informan por separado en la sección 8 del informe.
