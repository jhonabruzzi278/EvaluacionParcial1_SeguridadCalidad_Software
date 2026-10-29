# Resumen de ejecución de casos de prueba — Atlas (Docker local)

Generado el 2026-10-29. Entorno: Docker Compose de Atlas (atlas-frontend, atlas-backend, atlas-postgres) en el equipo del equipo.

**30 casos: 7 aprobado · 20 fallido · 3 no ejecutado**

| Caso | Título | Veredicto | Criterios cumplidos | Evidencia |
|---|---|---|---|---|
| PT-FUNC-001 | Flujo completo de contrato con documento adjunto | Fallido | 4/8 | 06-Evidencias/ejecucion/PT-FUNC-001_01_flujo_contrato.txt |
| PT-FUNC-002 | Autenticación y emisión de JWT | Aprobado | 3/3 | 06-Evidencias/ejecucion/PT-FUNC-002_01_login.txt |
| PT-FUNC-003 | Cierre de sesión y revocación de token | Fallido | 0/2 | 06-Evidencias/ejecucion/PT-FUNC-003_01_logout.txt |
| PT-FUNC-004 | Registro de usuario y unicidad de correo | Aprobado | 3/3 | 06-Evidencias/ejecucion/PT-FUNC-004_01_registro_correo.txt |
| PT-FUNC-005 | Creación de empresa y rol administrador por defecto | Aprobado | 3/3 | 06-Evidencias/ejecucion/PT-FUNC-005_01_empresa_rol.txt |
| PT-FUNC-006 | Alta, edición y baja de usuarios con rol | Aprobado | 4/4 | 06-Evidencias/ejecucion/PT-FUNC-006_01_usuarios_rol.txt |
| PT-FUNC-007 | Creación de cliente y validaciones | Fallido | 1/2 | 06-Evidencias/ejecucion/PT-FUNC-007_01_cliente_validaciones.txt |
| PT-FUNC-008 | Listar, filtrar, editar y eliminar clientes | Fallido | 2/4 | 06-Evidencias/ejecucion/PT-FUNC-008_01_clientes_crud.txt |
| PT-FUNC-009 | Estado del contrato y enlace compartido | Fallido | 1/2 | 06-Evidencias/ejecucion/PT-FUNC-009_01_estado_enlace.txt |
| PT-FUNC-010 | Registro de auditoría de acciones críticas | Fallido | 4/6 | 06-Evidencias/ejecucion/PT-FUNC-010_01_auditoria.txt |
| PT-FUNC-011 | Colección OpenAPI: cobertura de endpoints | Aprobado | 1/1 | 06-Evidencias/ejecucion/PT-FUNC-011_01_openapi.txt |
| PT-SEG-001 | Hashing de contraseñas y política de contraseñas | Fallido | 0/4 | 06-Evidencias/ejecucion/PT-SEG-001_01_hash_politica.txt |
| PT-SEG-002 | Control de acceso por rol en el backend (RBAC) | Fallido | 1/4 | 06-Evidencias/ejecucion/PT-SEG-002_01_rbac.txt |
| PT-SEG-003 | TLS y redirección HTTP→HTTPS | Fallido | 0/3 | 06-Evidencias/ejecucion/PT-SEG-003_01_tls.txt |
| PT-SEG-004 | Cifrado de datos sensibles en reposo | Fallido | 0/1 | 06-Evidencias/ejecucion/PT-SEG-004_01_cifrado_reposo.txt |
| PT-SEG-005 | Inyección SQL, XSS, CSRF y validación de entrada | Fallido | 2/9 | 06-Evidencias/ejecucion/PT-SEG-005_01_inyeccion_xss.txt |
| PT-SEG-006 | Gestión segura de errores y logs | Fallido | 1/2 | 06-Evidencias/ejecucion/PT-SEG-006_01_errores_logs.txt |
| PT-SEG-007 | Cumplimiento técnico de protección de datos personales | Fallido | 0/3 | 06-Evidencias/ejecucion/PT-SEG-007_01_datos_personales.txt |
| PT-SEG-008 | Sesión JWT: expiración, firma y secreto | Fallido | 4/6 | 06-Evidencias/ejecucion/PT-SEG-008_01_jwt.txt |
| PT-SEG-009 | Aislamiento entre empresas (IDOR) | Fallido | 0/1 | 06-Evidencias/ejecucion/PT-SEG-009_01_aislamiento.txt |
| PT-PERF-001 | Tiempo de respuesta de operaciones CRUD | Fallido | 4/6 | 06-Evidencias/ejecucion/PT-PERF-001_01_k6.txt |
| PT-PERF-002 | Carga de la página principal en conexión móvil | Fallido | 0/1 | 06-Evidencias/ejecucion/PT-PERF-002_01_lighthouse_lcp.txt |
| PT-PERF-003 | 200 usuarios concurrentes | Aprobado | 2/2 | 06-Evidencias/ejecucion/PT-PERF-003_01_k6.txt |
| PT-PERF-004 | Subida y descarga de documentos ≤ 10 s | Aprobado | 1/1 | 06-Evidencias/ejecucion/PT-PERF-004_01_documentos.txt |
| PT-USAB-001 | Accesibilidad para adultos mayores (WCAG 2.1 AA) | Fallido | 1/5 | 06-Evidencias/ejecucion/PT-USAB-001_01_axe_lighthouse.txt |
| PT-USAB-002 | Flujos claros de registro, creación de empresa y cliente → contratos | No ejecutado | 0/0 | — |
| PT-USAB-003 | Ayuda contextual y mensajes de error amigables | No ejecutado | 0/0 | — |
| PT-COMP-001 | Responsividad en móviles y tablets | Fallido | 0/3 | 06-Evidencias/ejecucion/PT-COMP-001_01_responsivo.txt |
| PT-COMP-002 | Compatibilidad en Chrome, Firefox, Edge y Safari | No ejecutado | 0/0 | — |
| PT-DIS-001 | Disponibilidad, respaldo y recuperación | Fallido | 4/5 | 06-Evidencias/ejecucion/PT-DIS-001_01_recuperacion_respaldo.txt |
