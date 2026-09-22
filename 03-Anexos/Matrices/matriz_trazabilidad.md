# Anexo: Matriz de Trazabilidad

## RF - Requerimientos Funcionales

| ID Requerimiento | Descripcion | Caso de Prueba | Tipo de Prueba | Resultado Esperado | Estado |
|------------------|-------------|----------------|----------------|-------------------|--------|
| RF-1 | Autenticacion de usuarios con JWT | PT-FUNC-001, PT-SEG-002 | Funcional, Seguridad | Login exitoso con credenciales validas; rechazo con credenciales invalidas | Pendiente |
| RF-2 | Registro de nuevos usuarios y asignacion de roles | PT-FUNC-001, PT-SEG-002 | Funcional, Seguridad | Usuario creado con rol correcto; validacion de campos obligatorios | Pendiente |
| RF-3 | Gestion de clientes (CRUD) | PT-FUNC-001, PT-SEG-002, PT-PERF-001 | Funcional, Seguridad, Rendimiento | CRUD completo funcionando; control de acceso por rol; tiempos < 300ms | Pendiente |
| RF-4 | Gestion de contratos (CRUD) | PT-FUNC-001 | Funcional | Contrato creado, actualizado, consultado y eliminado correctamente | Pendiente |
| RF-5 | Gestion de documentos asociados a contratos | PT-FUNC-001, PT-SEG-001 | Funcional, Seguridad | Documento subido, almacenado y descargable; sanitizacion de archivos | Pendiente |
| RF-6 | Auditoria y registro de acciones | PT-FUNC-001, PT-SEG-002 | Funcional, Seguridad | Logs generados para acciones sensibles; consulta de auditoria funciona | Pendiente |

## NFR-SEG - Requerimientos de Seguridad

| ID Requerimiento | Descripcion | Caso de Prueba | Tipo de Prueba | Resultado Esperado | Estado |
|------------------|-------------|----------------|----------------|-------------------|--------|
| NFR-SEG-1 | Comunicaciones cifradas con TLS | PT-SEG-001 | Seguridad | Certificado TLS valido; conexion HTTPS obligatoria; no se permite HTTP | Pendiente |
| NFR-SEG-2 | Hashing de contraseñas con bcrypt | PT-SEG-001 | Seguridad | Contraseñas almacenadas como hash bcrypt; nunca en texto plano | Pendiente |
| NFR-SEG-3 | Tokens JWT con expiracion | PT-SEG-002 | Seguridad | Token expira despues del tiempo configurado; refresh token funciona | Pendiente |
| NFR-SEG-4 | Control de acceso basado en roles (RBAC) | PT-SEG-002 | Seguridad | Admin tiene todos los permisos; Editor solo lectura; accesos no autorizados rechazados | Pendiente |
| NFR-SEG-5 | Proteccion contra CSRF, XSS, SQL Injection | PT-SEG-002 | Seguridad | Payloads maliciosos son sanitizados o rechazados; sin ejecucion de scripts | Pendiente |
| NFR-SEG-6 | Manejo seguro de errores | PT-FUNC-001 | Seguridad, Funcional | Errores no revelan informacion interna del sistema (stack traces, queries) | Pendiente |
| NFR-SEG-7 | Registro de auditoria de acciones sensibles | PT-FUNC-001, PT-SEG-002 | Seguridad, Funcional | Cada accion critica queda registrada con timestamp, usuario, IP | Pendiente |
| NFR-SEG-8 | Cumplimiento de normativas de proteccion de datos | PT-SEG-001, PT-USAB-001 | Seguridad, Usabilidad | Datos personales protegidos; politica de privacidad visible; consentimiento | Pendiente |
| NFR-SEG-9 | Sanitizacion de archivos subidos | PT-FUNC-001 | Seguridad, Funcional | Solo formatos permitidos (PDF, DOCX, JPG); sin ejecucion de archivos maliciosos | Pendiente |

## NFR-PERF - Requerimientos de Rendimiento

| ID Requerimiento | Descripcion | Caso de Prueba | Tipo de Prueba | Resultado Esperado | Estado |
|------------------|-------------|----------------|----------------|-------------------|--------|
| NFR-PERF-1 | Operaciones CRUD < 300ms | PT-PERF-001 | Rendimiento | 95% de peticiones responden en < 300ms bajo carga normal | Pendiente |
| NFR-PERF-2 | Carga de pagina < 2 segundos | PT-PERF-001 | Rendimiento | First Contentful Paint < 1.5s; Largest Contentful Paint < 2s | Pendiente |
| NFR-PERF-3 | Soporte a 200 usuarios concurrentes | PT-PERF-001 | Rendimiento | Sistema estable con 200 usuarios simultaneos; sin errores 5xx | Pendiente |

## NFR-USAB - Requerimientos de Usabilidad

| ID Requerimiento | Descripcion | Caso de Prueba | Tipo de Prueba | Resultado Esperado | Estado |
|------------------|-------------|----------------|----------------|-------------------|--------|
| NFR-USAB-1 | Accesibilidad para adultos mayores | PT-USAB-001 | Usabilidad | Cumplimiento WCAG 2.1 AA; navegacion por teclado; contraste >= 4.5:1 | Pendiente |
| NFR-USAB-2 | Tiempos de respuesta perceptibles | PT-PERF-001, PT-USAB-001 | Rendimiento, Usabilidad | Feedback visual en < 200ms para acciones del usuario | Pendiente |
| NFR-USAB-3 | Navegacion intuitiva | PT-USAB-001 | Usabilidad | Usuarios completan tareas core sin asistencia; SUS score >= 70 | Pendiente |
| NFR-USAB-4 | Mensajes de error claros | PT-USAB-001, PT-FUNC-001 | Usabilidad, Funcional | Mensajes en español; indican causa y solucion; sin codigos tecnicos crudos | Pendiente |

## NFR-COMPAT - Requerimientos de Compatibilidad

| ID Requerimiento | Descripcion | Caso de Prueba | Tipo de Prueba | Resultado Esperado | Estado |
|------------------|-------------|----------------|----------------|-------------------|--------|
| NFR-COMPAT-1 | Soporte Chrome, Firefox, Safari, Edge (ultimas 2 versiones) | PT-COMP-001 | Compatibilidad | Funcionalidades core operan correctamente en todos los navegadores listados | Pendiente |
| NFR-COMPAT-2 | Dispositivos moviles y tablets (responsive) | PT-COMP-001 | Compatibilidad | Layout adaptativo; sin scroll horizontal; botones tocables >= 44px | Pendiente |

## RB - Reglas de Negocio

| ID Regla | Descripcion | Caso de Prueba | Tipo de Prueba | Resultado Esperado | Estado |
|----------|-------------|----------------|----------------|-------------------|--------|
| RB-1 | Un usuario pertenece a una unica empresa | PT-FUNC-001 | Funcional | No se permite asignar un usuario a multiples empresas | Pendiente |
| RB-2 | Solo usuarios vinculados a una empresa pueden ver/editar sus datos | PT-SEG-002 | Seguridad, Funcional | Usuario de Empresa A no accede a datos de Empresa B | Pendiente |
| RB-3 | Solo usuarios con rol Admin pueden crear/editar/eliminar clientes y contratos | PT-SEG-002 | Seguridad, Funcional | Editor intenta crear cliente -> HTTP 403 | Pendiente |
| RB-4 | Los documentos solo son visibles para usuarios de la misma empresa | PT-SEG-002, PT-FUNC-001 | Seguridad, Funcional | Usuario externo no descarga documentos de otra empresa | Pendiente |
| RB-5 | El RUT chileno debe ser validado con algoritmo modulo 11 | PT-FUNC-001 | Funcional | RUT invalido es rechazado antes de guardar en BD | Pendiente |

## Resumen de Cobertura

| Categoria | Total | Cubiertos | % Cobertura |
|-----------|-------|-----------|-------------|
| RF | 6 | 6 | 100% |
| NFR-SEG | 9 | 9 | 100% |
| NFR-PERF | 3 | 3 | 100% |
| NFR-USAB | 4 | 4 | 100% |
| NFR-COMPAT | 2 | 2 | 100% |
| RB | 5 | 5 | 100% |
| **TOTAL** | **29** | **29** | **100%** |

---

**Nota:** Esta matriz debe actualizarse a medida que se ejecuten las pruebas, registrando el estado real (Aprobado / Fallido / Bloqueado) y los defectos encontrados.
