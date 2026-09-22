# Guia de Preparacion: EVA2 - Evaluacion Teorica Individual (8%)

**Asignatura:** ISY1102 - Seguridad y Calidad en el Desarrollo de Software  
**Fecha:** 24/09/2026 - 19:00 hrs  
**Duracion:** 60 minutos  
**Modalidad:** Individual via AVA  
**Ponderacion:** 8% de la nota de Evaluaciones Parciales

---

## Contenidos a Estudiar (IL 1.1 al IL 1.5)

### IL 1.1 - Rol de la Calidad del Software
**Conceptos clave:**
- Calidad de software: grado en que un sistema satisface las necesidades explicitas e implicitas
- Factores de calidad: funcionalidad, fiabilidad, usabilidad, eficiencia, mantenibilidad, portabilidad (ISO/IEC 25010)
- Costo de la calidad: prevencion, evaluacion, fallas internas, fallas externas
- Cumplimiento legal y normativo:
  - Ley N° 19.628 de Proteccion de Datos Personales (Chile)
  - Ley N° 19.799 sobre Documento Electronico, Firma Electronica y Servicios de Certificacion de dicha Firma
  - Ley del Consumidor (N° 19.496)
  - Reglamento General de Proteccion de Datos (RGPD) de la UE (referencia internacional)
- Importancia del cumplimiento: evita sanciones legales, genera confianza, protege datos sensibles

**Tips para la evaluacion:**
- Saber diferenciar entre calidad del producto vs calidad del proceso
- Conocer al menos 3 normativas legales chilenas aplicables al software
- Entender que el cumplimiento normativo no es opcional, es un requisito

---

### IL 1.2 - Pruebas Funcionales vs No Funcionales
**Conceptos clave:**

| Caracteristica | Pruebas Funcionales | Pruebas No Funcionales |
|----------------|---------------------|------------------------|
| **Que prueban** | Que el sistema hace lo que debe hacer (requerimientos funcionales) | Como el sistema se comporta (rendimiento, seguridad, usabilidad) |
| **Ejemplos** | Unitarias, integracion, sistema, aceptacion, regression | Rendimiento, carga, estres, seguridad, usabilidad, compatibilidad |
| **Basadas en** | Especificaciones funcionales, historias de usuario | Requerimientos no funcionales (NFR), estandares, normativas |
| **Herramientas** | Jest, JUnit, Selenium, Cypress | JMeter, k6, OWASP ZAP, Lighthouse |
| **Legal/Normativo** | Validan cumplimiento de funcionalidades contractuales | Validan cumplimiento de normativas de seguridad, accesibilidad, rendimiento |

- **Pruebas de caja negra:** Se prueban entradas/salidas sin conocer la estructura interna
- **Pruebas de caja blanca:** Se prueba la estructura interna del codigo (cobertura, caminos)
- **Pruebas de caja gris:** Combinacion de ambas

**Tips para la evaluacion:**
- Saber dar ejemplos concretos de cada tipo de prueba
- Entender la diferencia entre prueba unitaria, de integracion y de sistema
- Conocer la piramide de pruebas (unitarias > integracion > E2E)

---

### IL 1.3 - Pruebas de Usabilidad, Rendimiento y Compatibilidad
**Conceptos clave:**

#### Pruebas de Usabilidad
- **Objetivo:** Evaluar que tan facil es usar el sistema
- **Aspectos:** Aprendizaje, eficiencia, memorabilidad, errores, satisfaccion
- **Normativa:** WCAG 2.1 (Web Content Accessibility Guidelines)
- **Relacion con legales:** Ley N° 20.422 de Inclusion Social (accesibilidad en Chile)
- **Herramientas:** Test de usuario, cuestionarios SUS, eye-tracking, Lighthouse

#### Pruebas de Rendimiento
- **Tipos:**
  - **Carga (Load):** Comportamiento bajo carga esperada
  - **Estres (Stress):** Comportamiento bajo carga extrema
  - **Volumen (Volume):** Gran cantidad de datos
  - **Escalabilidad:** Capacidad de crecer
- **Metricas:** Tiempo de respuesta, throughput, uso de CPU/memoria, concurrencia
- **Herramientas:** JMeter, k6, Gatling, Loader.io

#### Pruebas de Compatibilidad
- **Objetivo:** Verificar funcionamiento en distintos entornos
- **Aspectos:** Navegadores, SO, dispositivos, resoluciones, versiones
- **Herramientas:** BrowserStack, Sauce Labs, emuladores

#### Impacto en Calidad, Seguridad y Etica
- Usabilidad deficiente -> exclusion de usuarios (etica)
- Rendimiento deficiente -> perdida de negocio, frustracion
- Compatibilidad deficiente -> barreras de acceso
- Todas afectan la confiabilidad y la seguridad percibida

**Tips para la evaluacion:**
- Saber definir cada tipo de prueba no funcional
- Conocer las metricas clave de rendimiento
- Relacionar con normativas de accesibilidad

---

### IL 1.4 - Diseno de un Plan de Pruebas
**Conceptos clave:**
- **Estructura estandar de un plan de pruebas (IEEE 829 / ISO/IEC/IEEE 29119):**
  1. Identificador del plan
  2. Introduccion (alcance, objetivos)
  3. Elementos a probar (requerimientos, caracteristicas)
  4. Caracteristicas a no probar
  5. Enfoque (estrategia, tecnicas, criterios de entrada/salida)
  6. Criterios de suspension y reanudacion
  7. Entregables (documentos, reportes)
  8. Tareas de pruebas (actividades)
  9. Necesidades ambientales (hardware, software, red)
  10. Responsabilidades (roles)
  11. Necesidades de personal y capacitacion
  12. Cronograma
  13. Riesgos y contingencias
  14. Aprobaciones

- **Estrategia de pruebas:** Enfoque general para alcanzar los objetivos de prueba
- **Criterios de aceptacion:** Condiciones que debe cumplir el sistema para ser aceptado
- **Coherencia con requerimientos:** Cada prueba debe trazarse a un requerimiento
- **Normativas vigentes:** El plan debe considerar leyes y estandares aplicables

**Tips para la evaluacion:**
- Conocer la estructura basica de un plan de pruebas
- Saber diferenciar entre estrategia, plan y caso de prueba
- Entender que es un criterio de aceptacion

---

### IL 1.5 - Evaluacion de Consistencia y Cobertura
**Conceptos clave:**
- **Cobertura de requerimientos:** % de requerimientos que tienen al menos un caso de prueba
- **Cobertura de codigo:** % de lineas/caminos/condiciones ejecutados por las pruebas
- **Matriz de trazabilidad:** Tabla que vincula requerimientos -> casos de prueba -> resultados
- **Consistencia:** El plan no tiene contradicciones internas
- **Alineacion con estandares:** ISO/IEC 25010, ISO/IEC 29119, OWASP, WCAG
- **Marcos legales:** Ley 19.628, Ley 20.422, Ley del Consumidor
- **Analisis critico:** No solo verificar que existen pruebas, sino que son las correctas

**Tips para la evaluacion:**
- Saber que es una matriz de trazabilidad y para que sirve
- Conocer los estandares ISO mencionados
- Entender la diferencia entre cobertura funcional y cobertura de codigo

---

## Temas Transversales Importantes

### Seguridad en Pruebas de Software
- OWASP Top 10: Inyeccion, autenticacion rota, exposicion de datos sensibles, XXE, control de acceso roto, configuracion de seguridad incorrecta, XSS, deserializacion insegura, componentes vulnerables, registro y monitoreo insuficientes
- Pruebas de seguridad: Pentesting, analisis estatico (SAST), analisis dinamico (DAST)
- Cifrado: En transito (TLS/SSL) y en reposo (AES)
- Hashing de contraseñas: bcrypt, Argon2, PBKDF2 (NO usar MD5 ni SHA1 para contraseñas)

### Accesibilidad (a11y)
- WCAG 2.1 niveles: A, AA, AAA
- Principios: Perceptible, Operable, Comprensible, Robusto (POUR)
- Pautas clave: Texto alternativo, contraste minimo 4.5:1, navegacion por teclado, etiquetas correctas
- Ley 20.422 (Chile): Obliga accesibilidad en sitios publicos y servicios digitales

### Etica en el Desarrollo de Software
- Privacidad por diseno (Privacy by Design)
- Minimizacion de datos
- Consentimiento informado
- Transparencia algoritmica
- Impacto social del software

---

## Estrategia de Estudio para EVA2

1. **Revisa la Evaluacion Formativa** compartida en AVA. Repite las preguntas que te costaron.
2. **Estudia en grupo** pero recuerda que la evaluacion es individual.
3. **Crea tarjetas de estudio** con las definiciones clave de cada IL.
4. **Practica con el caso Atlas:** Aplica cada concepto al sistema Atlas para entenderlos en contexto.
5. **Revisa las normativas chilenas:** Memoriza los numeros de ley y sus objetivos principales.
6. **Conoce las siglas:** ISO/IEC 25010, ISO/IEC 29119, OWASP, WCAG, SAST, DAST.
7. **Descansa bien** el dia anterior. La evaluacion es a las 19:00 hrs.

---

## Recordatorio Importante

- **EVA1 (Informe grupal):** Entrega a las 19:00 hrs del 24/09/2026. Debe estar listo antes de la EVA2.
- **EVA2 (Teorica individual):** Inicia a las 19:00 hrs del 24/09/2026. Duracion: 60 minutos.
- **Organizate:** El mismo dia debes entregar el informe Y rendir la evaluacion teorica. Planifica tu tiempo.

---

**Exitos en la preparacion!**
