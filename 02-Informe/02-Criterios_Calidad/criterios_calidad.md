# 2. Criterios de Calidad, Seguridad y Cumplimiento Normativo

## 2.1 Criterios de Calidad del Software (ISO/IEC 25010)

El sistema Atlas sera evaluado conforme al modelo de calidad SQuaRE definido en la norma ISO/IEC 25010:2011. A continuacion se detallan las caracteristicas aplicables:

| Caracteristica | Subcaracteristica | Criterio de Aceptacion | Requerimiento ERS |
|----------------|-------------------|------------------------|-------------------|
| **Funcionalidad** | Completitud funcional | El sistema implementa todas las funcionalidades descritas en RF-1 a RF-6 | RF-1 al RF-6 |
| | Correccion funcional | Las funcionalidades producen resultados correctos y consistentes | RF-1 al RF-6 |
| **Fiabilidad** | Madurez | El sistema opera sin fallos criticos bajo condiciones normales | NFR-PERF |
| | Recuperabilidad | En caso de error, el sistema recupera el estado consistente sin perdida de datos | NFR-SEG-6 |
| **Usabilidad** | Capacidad de aprendizaje | Un usuario novel completa el registro y primer login sin asistencia en menos de 5 minutos | NFR-USAB-1 |
| | Accesibilidad | Cumplimiento WCAG 2.1 nivel AA para adultos mayores | NFR-USAB-1 al NFR-USAB-4 |
| **Eficiencia de Rendimiento** | Comportamiento temporal | 95% de operaciones CRUD responden en menos de 300ms | NFR-PERF-1 |
| | Utilizacion de recursos | Uso de CPU y memoria dentro de limites aceptables bajo carga | NFR-PERF-3 |
| **Mantenibilidad** | Modificabilidad | El codigo permite agregar nuevos modulos con impacto minimo en existentes | - |
| **Portabilidad** | Adaptabilidad | El sistema funciona correctamente en Chrome, Firefox, Safari, Edge (ultimas 2 versiones) | NFR-COMPAT-1 |
| | Instalabilidad | Despliegue mediante Docker Compose con un solo comando | Arquitectura 4.2 |

> **Completar:** Agregar mas subcaracteristicas si aplica. Justificar por que se seleccionaron estas.

## 2.2 Criterios de Seguridad

La seguridad del sistema Atlas se evaluara bajo los siguientes criterios, derivados de los requerimientos no funcionales de seguridad del ERS y mejores practicas de la industria:

### 2.2.1 Confidencialidad
- **Criterio:** Los datos sensibles (contraseñas, tokens, informacion personal) deben estar protegidos contra accesos no autorizados.
- **Medida:** Uso de hashing bcrypt para contraseñas (NFR-SEG-2), TLS 1.2+ para comunicaciones (NFR-SEG-1), control de acceso basado en roles (NFR-SEG-4).
- **Verificacion:** Pruebas de penetracion, revision de codigo, analisis de configuracion.

### 2.2.2 Integridad
- **Criterio:** Los datos no deben ser alterados de manera no autorizada.
- **Medida:** Validacion de entradas, proteccion contra CSRF (NFR-SEG-5), logs de auditoria (RF-6).
- **Verificacion:** Pruebas de inyeccion, manipulacion de requests, revision de logs.

### 2.2.3 Disponibilidad
- **Criterio:** El sistema debe estar disponible para usuarios autorizados cuando lo requieran.
- **Medida:** Tiempos de respuesta aceptables (NFR-PERF-1), manejo de errores graceful (NFR-SEG-6).
- **Verificacion:** Pruebas de carga, pruebas de recuperacion ante fallos.

### 2.2.4 Autenticidad y No Repudio
- **Criterio:** Las acciones de los usuarios deben ser atribuibles y verificables.
- **Medida:** Autenticacion JWT con expiracion (NFR-SEG-3), registro de auditoria (RF-6).
- **Verificacion:** Pruebas de expiracion de sesion, revision de logs de auditoria.

### 2.2.5 Cumplimiento OWASP Top 10
- **Criterio:** El sistema no debe presentar vulnerabilidades del OWASP Top 10.
- **Medida:** Revision de codigo, escaneos con OWASP ZAP.
- **Verificacion:** Reporte de vulnerabilidades sin hallazgos criticos.

> **Completar:** Expandir cada criterio con ejemplos concretos del caso Atlas.

## 2.3 Cumplimiento Normativo y Legal

El sistema Atlas debe cumplir con la siguiente normativa chilena e internacional:

### 2.3.1 Ley N° 19.628 - Proteccion de la Vida Privada
- **Aplicacion:** El sistema almacena datos personales (nombre, RUT, direccion, correo, telefono).
- **Obligaciones:**
  - Registrar la base de datos ante la autoridad correspondiente.
  - Obtener consentimiento informado para el tratamiento de datos.
  - Garantizar la seguridad de los datos personales.
  - Permitir el ejercicio de derechos de acceso, rectificacion, cancelacion y oposicion.
- **Vinculacion ERS:** NFR-SEG-8 (Cumplimiento de normativas de proteccion de datos personales).

### 2.3.2 Ley N° 20.422 - Igualdad de Oportunidades e Inclusion Social
- **Aplicacion:** El sistema debe ser accesible para personas con discapacidad, incluyendo adultos mayores.
- **Obligaciones:**
  - Cumplir con estandares de accesibilidad web (WCAG 2.1 nivel AA).
  - Garantizar navegacion por teclado.
  - Proveer alternativas textuales para contenido no textual.
- **Vinculacion ERS:** NFR-USAB-1 (Accesibilidad para adultos mayores).

### 2.3.3 Ley N° 19.799 - Documento Electronico, Firma Electronica y Servicios de Certificacion
- **Aplicacion:** El sistema gestiona contratos y documentos electronicos.
- **Obligaciones:**
  - Garantizar la integridad de los documentos almacenados.
  - Asegurar la autenticidad de los registros.
- **Vinculacion ERS:** RF-5 (Gestion de documentos de contratos), RF-6 (Auditoria).

### 2.3.4 ISO/IEC 25010:2011
- **Aplicacion:** Marco de referencia para la evaluacion de la calidad del producto software.
- **Uso en el proyecto:** Define las caracteristicas y subcaracteristicas de calidad a evaluar.

### 2.3.5 OWASP Testing Guide v4.2
- **Aplicacion:** Metodologia para pruebas de seguridad en aplicaciones web.
- **Uso en el proyecto:** Guia para disenar y ejecutar pruebas de seguridad.

> **Completar:** Ampliar el analisis de cada normativa. Explicar CONCRETAMENTE como Atlas se alinea o debe alinearse con cada una.

## 2.4 Clasificacion del Producto segun Elementos de Calidad, Seguridad y Cumplimiento

| Dimension | Clasificacion | Justificacion |
|-----------|--------------|---------------|
| **Calidad Funcional** | Alta criticidad | El sistema gestiona datos comerciales criticos para pymes |
| **Seguridad** | Muy alta criticidad | Maneja datos personales sensibles y documentos contractuales |
| **Cumplimiento Legal** | Obligatorio | Sujeto a Ley 19.628, Ley 20.422 y Ley 19.799 |
| **Rendimiento** | Alta criticidad | Debe soportar operacion diaria de multiples pymes |
| **Usabilidad** | Alta criticidad | Usuarios potencialmente no tecnicos (adultos mayores) |

> **Completar:** Justificar cada clasificacion con argumentos tecnicos y de negocio.
