# 6. Diseno de Casos de Prueba

## 6.1 Caso de Prueba PT-SEG-001: Hashing de Contraseñas con bcrypt

| Campo | Descripcion |
|-------|-------------|
| **ID del Caso** | PT-SEG-001 |
| **Descripcion** | Verificar que las contraseñas de los usuarios se almacenan utilizando el algoritmo de hashing bcrypt y nunca en texto plano |
| **Requerimiento Asociado** | NFR-SEG-2 |
| **Tipo de Prueba** | Seguridad (Confidencialidad) |
| **Nivel** | Unitario / Integracion |

### Datos de Entrada
- Contraseña en texto plano: `Atlas2024!Segura`
- Contraseña en texto plano: `Password123`
- Contraseña vacia: `` (debe ser rechazada)

### Procedimiento
1. Registrar un nuevo usuario con la contraseña proporcionada
2. Consultar directamente la tabla `usuarios` en la base de datos PostgreSQL
3. Verificar el valor almacenado en el campo `contraseña`
4. Intentar autenticar al usuario con la contraseña original

### Resultado Esperado
- El campo `contraseña` en la BD NO contiene el texto plano `Atlas2024!Segura`
- El campo contiene un hash en formato bcrypt (prefijo `$2a$`, `$2b$` o `$2y$`)
- La autenticacion con la contraseña original es exitosa
- La autenticacion con cualquier otra contraseña falla

### Criterios de Aceptacion
- [ ] El hash almacenado sigue el formato estandar de bcrypt
- [ ] El cost factor (work factor) es >= 10
- [ ] No existe ninguna columna o log que almacene la contraseña en texto plano
- [ ] La verificacion de contraseña utiliza `bcrypt.compare()` o equivalente

---

## 6.2 Caso de Prueba PT-SEG-002: Control de Acceso Basado en Roles (RBAC)

| Campo | Descripcion |
|-------|-------------|
| **ID del Caso** | PT-SEG-002 |
| **Descripcion** | Verificar que un usuario con rol "Editor" NO puede crear, editar ni eliminar clientes, mientras que un "Admin" SI puede |
| **Requerimiento Asociado** | RF-3.2, RB-4, NFR-SEG-4 |
| **Tipo de Prueba** | Seguridad (Autorizacion) |
| **Nivel** | Integracion / Sistema |

### Datos de Entrada
- Usuario A: rol "Admin" (token JWT valido)
- Usuario B: rol "Editor" (token JWT valido)
- Endpoint: `POST /api/empresas/1/clients` (crear cliente)
- Endpoint: `PUT /api/empresas/1/clients/123` (editar cliente)
- Endpoint: `DELETE /api/empresas/1/clients/123` (eliminar cliente)

### Procedimiento
1. Autenticar como Usuario A (Admin) y ejecutar POST, PUT, DELETE sobre clientes
2. Autenticar como Usuario B (Editor) y ejecutar las mismas operaciones
3. Verificar los codigos de respuesta HTTP y los registros de auditoria

### Resultado Esperado
- Usuario A (Admin): HTTP 201 / 200 para todas las operaciones
- Usuario B (Editor): HTTP 403 Forbidden para POST, PUT, DELETE
- Usuario B (Editor): HTTP 200 para GET (lectura permitida)
- El intento de acceso no autorizado del Editor queda registrado en la auditoria

### Criterios de Aceptacion
- [ ] El backend verifica el rol del usuario antes de ejecutar operaciones sensibles
- [ ] Las respuestas 403 no revelan informacion interna del sistema
- [ ] Cada intento de acceso no autorizado se registra con: timestamp, usuario, recurso, accion, IP
- [ ] La validacion ocurre en el servidor, no solo en el frontend

---

## 6.3 Caso de Prueba PT-PERF-001: Tiempo de Respuesta de Operaciones CRUD

| Campo | Descripcion |
|-------|-------------|
| **ID del Caso** | PT-PERF-001 |
| **Descripcion** | Medir el tiempo de respuesta de la operacion de listado de clientes con 1000 registros en la base de datos |
| **Requerimiento Asociado** | NFR-PERF-1 |
| **Tipo de Prueba** | Rendimiento (Carga) |
| **Nivel** | Sistema |

### Datos de Entrada
- Base de datos con 1000 registros de clientes para la empresa ID=1
- Usuario autenticado con rol Admin
- Request: `GET /api/empresas/1/clients?page=1&limit=50`

### Procedimiento
1. Preparar la base de datos con 1000 clientes de prueba
2. Ejecutar 100 solicitudes GET al endpoint de listado
3. Medir el tiempo de respuesta de cada solicitud
4. Calcular el promedio, percentil 95 y percentil 99

### Resultado Esperado
- Promedio de respuesta: < 300ms
- Percentil 95: < 300ms
- Percentil 99: < 500ms
- Sin errores HTTP 5xx

### Criterios de Aceptacion
- [ ] El 95% de las solicitudes responde en menos de 300ms
- [ ] El 99% de las solicitudes responde en menos de 500ms
- [ ] No hay degradacion visible en la interfaz de usuario
- [ ] El uso de CPU del servidor backend no supera el 70% en carga normal

---

## 6.4 Caso de Prueba PT-USAB-001: Accesibilidad para Adultos Mayores

| Campo | Descripcion |
|-------|-------------|
| **ID del Caso** | PT-USAB-001 |
| **Descripcion** | Verificar que la interfaz de login es accesible y usable por adultos mayores, cumpliendo con WCAG 2.1 nivel AA |
| **Requerimiento Asociado** | NFR-USAB-1, NFR-USAB-3, NFR-USAB-4 |
| **Tipo de Prueba** | Usabilidad / Accesibilidad |
| **Nivel** | Sistema |

### Datos de Entrada
- Usuarios de prueba: 5 adultos mayores de 65 años (perfil no tecnico)
- Dispositivo: Computador de escritorio con navegador Chrome
- Resolucion: 1920x1080 (ajustada a 125% de escala)

### Procedimiento
1. Solicitar a cada usuario que complete el flujo de login sin asistencia
2. Medir el tiempo que tardan en completar la tarea
3. Registrar errores, confusiones o solicitudes de ayuda
4. Ejecutar auditoria automatizada con Lighthouse (accesibilidad)
5. Verificar navegacion completa por teclado (Tab, Enter, Esc)

### Resultado Esperado
- Todos los usuarios completan el login sin asistencia en menos de 3 minutos
- Los campos de email y contraseña tienen labels asociados correctamente (`<label for="...">`)
- El contraste entre texto y fondo cumple ratio minimo 4.5:1
- Los mensajes de error son claros y sugieren la accion correctiva
- Lighthouse Accessibility Score >= 90
- Navegacion por teclado funciona sin trampas (keyboard traps)

### Criterios de Aceptacion
- [ ] Cumplimiento WCAG 2.1 nivel AA verificado con herramienta automatizada
- [ ] Tamano de fuente base >= 16px (o escalable sin perdida de funcionalidad)
- [ ] Los elementos interactivos tienen area de click/tap >= 44x44px
- [ ] No hay dependencia exclusiva del color para transmitir informacion
- [ ] El foco del teclado es visible en todos los elementos interactivos

---

## 6.5 Caso de Prueba PT-COMP-001: Responsividad en Dispositivos Moviles

| Campo | Descripcion |
|-------|-------------|
| **ID del Caso** | PT-COMP-001 |
| **Descripcion** | Verificar que el Dashboard y las funcionalidades principales se visualizan y operan correctamente en dispositivos moviles y tablets |
| **Requerimiento Asociado** | NFR-COMPAT-2 |
| **Tipo de Prueba** | Compatibilidad (Responsive) |
| **Nivel** | Sistema |

### Datos de Entrada
- Dispositivos de prueba:
  - iPhone 14 (iOS 17, Safari, resolucion 390x844)
  - Samsung Galaxy S23 (Android 14, Chrome, resolucion 360x780)
  - iPad Air (iOS 17, Safari, resolucion 820x1180)
- Navegadores: Safari, Chrome

### Procedimiento
1. Acceder al sistema Atlas desde cada dispositivo/navegador
2. Realizar login con credenciales validas
3. Navegar por: Dashboard, Lista de Clientes, Formulario de Cliente, Lista de Contratos
4. Intentar crear un cliente nuevo y subir un documento
5. Verificar que no hay scroll horizontal no deseado
6. Verificar que los botones y campos son facilmente tocables

### Resultado Esperado
- El layout se adapta a cada resolucion sin scroll horizontal
- El menu de navegacion es accesible (hamburger menu en moviles)
- Los formularios son completables en pantallas pequeñas
- Las tablas de datos se visualizan correctamente (scroll vertical o cards)
- Los botones y enlaces tienen area de toque minima de 44x44px
- Las imagenes y documentos se previsualizan correctamente

### Criterios de Aceptacion
- [ ] Visualizacion correcta en todas las resoluciones de prueba
- [ ] Sin scroll horizontal en ninguna vista
- [ ] Tiempo de carga inicial < 3 segundos en conexion 4G simulada
- [ ] Todos los flujos criticos son completables en dispositivos moviles
- [ ] Sin elementos superpuestos o cortados

---

## 6.6 Caso de Prueba PT-FUNC-001: Flujo Completo de Creacion de Contrato

| Campo | Descripcion |
|-------|-------------|
| **ID del Caso** | PT-FUNC-001 |
| **Descripcion** | Verificar el flujo end-to-end de creacion de un contrato, incluyendo asignacion de cliente, carga de documento y verificacion en la lista |
| **Requerimiento Asociado** | RF-4, RF-5, RB-3 |
| **Tipo de Prueba** | Funcional (End-to-End) |
| **Nivel** | Sistema |

### Datos de Entrada
- Usuario autenticado con rol Admin
- Cliente previamente creado: "Empresa ABC SpA", RUT 76.123.456-7
- Archivo de prueba: contrato_servicios_2024.pdf (tamaño < 5MB)
- Datos del contrato: tipo "Servicios", monto $1.500.000, fecha inicio 01/10/2024, fecha termino 01/10/2025

### Procedimiento
1. Iniciar sesion como Admin
2. Navegar a "Contratos" > "Nuevo Contrato"
3. Seleccionar el cliente "Empresa ABC SpA"
4. Completar los campos obligatorios del contrato
5. Subir el archivo PDF del contrato
6. Guardar el contrato
7. Verificar que aparece en la lista de contratos
8. Verificar que el documento se puede descargar

### Resultado Esperado
- El contrato se crea con estado "Activo"
- El archivo PDF se almacena y es accesible para descarga
- La lista de contratos muestra el nuevo registro con datos correctos
- Se genera un registro en la auditoria indicando: usuario, accion "CREAR_CONTRATO", timestamp, detalles

### Criterios de Aceptacion
- [ ] Todos los campos obligatorios son validados antes del envio
- [ ] El archivo PDF se almacena correctamente y es descargable
- [ ] El contrato aparece inmediatamente en la lista
- [ ] El registro de auditoria se genera automaticamente
- [ ] Sin errores de consola ni en la red (HTTP 4xx/5xx)

> **Completar:** Agregar mas casos de prueba si se considera necesario (minimo 5, pero pueden ser mas).

---

## 6.7 Resumen de Casos de Prueba

| ID | Tipo | Requerimiento | Prioridad | Responsable |
|----|------|--------------|-----------|-------------|
| PT-SEG-001 | Seguridad | NFR-SEG-2 | Critica | QA Seguridad |
| PT-SEG-002 | Seguridad | RF-3.2, RB-4, NFR-SEG-4 | Critica | QA Seguridad |
| PT-PERF-001 | Rendimiento | NFR-PERF-1 | Alta | QA Rendimiento |
| PT-USAB-001 | Usabilidad | NFR-USAB-1 | Alta | QA / UX |
| PT-COMP-001 | Compatibilidad | NFR-COMPAT-2 | Media | QA |
| PT-FUNC-001 | Funcional | RF-4, RF-5 | Alta | QA Funcional |

> **Completar:** Asegurar que la matriz de trazabilidad vincule cada caso con los requerimientos.
