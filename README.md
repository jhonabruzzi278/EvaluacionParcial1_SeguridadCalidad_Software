# EP1 - ISY1102: Seguridad y Calidad en el Desarrollo de Software

## Proyecto: Plan de Pruebas - Sistema Atlas

**Asignatura:** ISY1102 - Seguridad y Calidad en el Desarrollo de Software  
**Evaluacion:** Parcial N°1 - Diseñando un plan de pruebas seguro, legal y normativo  
**Ponderacion:** 17% de la nota final  
**Modalidad:** Grupal (maximo 3 integrantes)  
**Caso Base:** Sistema "Atlas" - Plataforma web de gestion de clientes y contratos para pymes

---

## Integrantes del Grupo

| Nombre Completo | Carrera | Seccion |
|-----------------|---------|---------|
| [Integrante 1]  | [Carrera] | [Seccion] |
| [Integrante 2]  | [Carrera] | [Seccion] |
| [Integrante 3]  | [Carrera] | [Seccion] |

**Docente:** [Nombre del docente]  
**Fecha de entrega:** [Fecha]

---

## Estructura del Repositorio

```
EvaluacionParcial1_SeguridadCalidad_Software/
|
|-- 01-Documentos_Base/           # Documentos originales de la evaluacion
|   |-- SRS_Atlas_384735328.pdf        # Especificacion de Requerimientos de Software
|   |-- Pauta_Evaluacion_403028603.pdf # Pauta de evaluacion y rubrica
|   |-- Pauta_Evaluacion_403028603.txt # Texto extraido de la pauta
|   |-- EP1_ISY1102_Formato_Informe.docx # Formato oficial del informe
|
|-- 02-Informe/                   # Secciones del informe (archivos .md o .docx)
|   |-- 01-Introduccion/
|   |-- 02-Criterios_Calidad/
|   |-- 03-Estrategia_Pruebas/
|   |-- 04-Tipos_Pruebas/
|   |-- 05-Recursos/
|   |-- 06-Casos_Prueba/
|   |-- 07-Analisis_Cobertura/
|
|-- 03-Anexos/                    # Material complementario
|   |-- Diagramas/
|   |-- Matrices/
|
|-- 04-Entrega/                   # Documento final consolidado (PDF o DOCX)
|
|-- CodigoFuenteA/                # Codigo fuente del sistema Atlas (Original)
```

---

## Rubrica de Evaluacion (Fuente de Verdad)

| Indicador | Ponderacion | Muy Buen Desempeno (100%) |
|-----------|-------------|---------------------------|
| **IE1** - Importancia de calidad, seguridad y cumplimiento legal | 15% | Identifica con claridad y profundidad la importancia de calidad, seguridad y cumplimiento legal, integrando ejemplos pertinentes y lenguaje tecnico adecuado |
| **IE2** - Clasificacion de tipos de pruebas | 20% | Clasifica y describe correctamente todos los tipos de prueba (funcionales, no funcionales, seguridad, rendimiento, etc.), justificando su proposito y aplicacion |
| **IE3** - Pruebas no funcionales: diseno de casos | 20% | Disena y documenta casos representativos de distintos tipos de pruebas no funcionales, definiendo criterios de aceptacion y proposito de manera coherente con el contexto |
| **IE4** - Elementos del plan de pruebas | 25% | El plan presenta todos los apartados solicitados (introduccion, alcance, objetivos, estrategia, recursos y cronograma) con coherencia tecnica, vinculacion a requerimientos y normativas vigentes |
| **IE5** - Cobertura, pertinencia y coherencia | 20% | Evalua la coherencia y cobertura del plan de pruebas con respecto a los requerimientos y estandares, demostrando analisis critico y justificacion tecnica |

### Niveles de Logro

| Nivel | Porcentaje |
|-------|------------|
| Muy buen desempeno | 100% |
| Buen desempeno | 80% |
| Desempeno aceptable | 60% |
| Desempeno incipiente | 30% |
| Desempeno no logrado | 0% |

---

## Plan de Accion para Lograr el Maximo Puntaje

### IE1 - Calidad, Seguridad y Cumplimiento Legal (15%)
**Objetivo:** Demostrar que se entiende POR QUE es importante todo esto.

**Acciones:**
1. Definir el contexto del sistema Atlas: plataforma que maneja datos personales, contratos y documentos sensibles de pymes chilenas.
2. Justificar la **calidad**: errores pueden causar perdida de contratos, datos bancarios de clientes o informacion empresarial critica.
3. Justificar la **seguridad** citando ejemplos concretos del caso:
   - Hashing de contraseñas con bcrypt (NFR-SEG-2)
   - TLS obligatorio en comunicaciones (NFR-SEG-1)
   - Proteccion contra CSRF, XSS, SQL Injection (NFR-SEG-5)
   - Control de acceso por roles (NFR-SEG-4)
4. Justificar el **cumplimiento legal** mencionando:
   - Ley de Proteccion de Datos Personales en Chile (Ley N° 19.628)
   - NFR-SEG-8: Cumplimiento de normativas de proteccion de datos personales
   - RB-2: Solo usuarios con relacion en empresa_usuarios pueden ver/editar datos
5. Usar lenguaje tecnico formal.

### IE2 - Clasificacion de Tipos de Pruebas (20%)
**Objetivo:** Demostrar que se saben QUE tipos de pruebas existen y PARA QUE sirven.

**Debes incluir:**

| Tipo de Prueba | Justificacion basada en Atlas | Requerimientos asociados |
|----------------|-------------------------------|--------------------------|
| Pruebas Funcionales | Validar login, registro, CRUD de clientes/contratos, gestion de roles | RF-1, RF-2, RF-3, RF-4, RF-5, RF-6 |
| Pruebas de Seguridad | Verificar autenticacion JWT, control de acceso por rol, proteccion contra inyeccion SQL, XSS, CSRF | NFR-SEG-1 al NFR-SEG-9 |
| Pruebas de Rendimiento | Confirmar operaciones CRUD < 300ms, carga de pagina < 2s, 200 usuarios concurrentes | NFR-PERF-1, NFR-PERF-2, NFR-PERF-3 |
| Pruebas de Usabilidad | Validar accesibilidad para adultos mayores, contraste, tamanos de fuente, navegacion por teclado | NFR-USAB-1, NFR-USAB-2, NFR-USAB-3, NFR-USAB-4 |
| Pruebas de Integracion | Verificar Frontend (React) + Backend (Express) + PostgreSQL + Storage de documentos | Arquitectura 4.1 y 4.2 |
| Pruebas de Compatibilidad | Probar en Chrome, Firefox, Safari, Edge ultimas 2 versiones, y dispositivos moviles/tablets | NFR-COMPAT-1, NFR-COMPAT-2 |

### IE3 - Pruebas No Funcionales: Diseno de Casos (20%)
**Objetivo:** Disenar al menos 5 casos de prueba NO FUNCIONALES concretos para Atlas.

**Ejemplos de casos obligatorios:**

1. **PT-SEG-001** - Hashing de contraseñas con bcrypt (NFR-SEG-2)
2. **PT-SEG-002** - Control de acceso por rol Editor vs Admin (RF-3.2 + RB-4)
3. **PT-PERF-001** - Tiempo de respuesta CRUD < 300ms (NFR-PERF-1)
4. **PT-USAB-001** - Accesibilidad para adultos mayores (NFR-USAB-1)
5. **PT-COMP-001** - Responsividad en moviles y tablets (NFR-COMPAT-2)

Cada caso debe contener: ID, Descripcion, Requerimiento asociado, Datos de entrada, Resultado esperado, Criterios de aceptacion, Tipo de prueba.

### IE4 - Elementos del Plan de Pruebas (25%)
**Objetivo:** Presentar un plan COMPLETO y coherente.

**Apartados obligatorios:**
1. Introduccion (contexto Atlas + proposito del plan)
2. Criterios de Calidad (usabilidad, rendimiento, estabilidad, confiabilidad, mantenibilidad, seguridad, normativas)
3. Estrategia de Pruebas (enfoque mixto manual + automatizado, etapas, herramientas, priorizacion, criterios de entrada/salida)
4. Tipos de Prueba (lista completa con justificacion)
5. Recursos Necesarios (humanos, tecnicos, entornos)
6. Diseno de Casos de Prueba (minimo 5 casos representativos)
7. Criterios de Aceptacion (transversales)

**Ademas:** Alcance, Objetivos especificos, Cronograma estimado.

### IE5 - Cobertura, Pertinencia y Coherencia (20%)
**Objetivo:** Demostrar que el plan realmente cubre lo que necesita Atlas.

**Debes demostrar analisis critico mediante:**
1. **Matriz de trazabilidad:** Requerimiento del ERS -> Caso de prueba -> Tipo de prueba -> Resultado esperado
2. **Analisis de cobertura:** Cuantos RF y NFR estan cubiertos (objetivo: todos)
3. **Justificacion tecnica:** Por que se probaron ciertos escenarios y no otros. Mencionar riesgos.
4. **Relacion con estandares:** ISO/IEC 25010, OWASP Top 10, WCAG 2.1
5. **Revision de consistencia:** Casos coherentes con estrategia, recursos permiten ejecucion, criterios medibles.

---

## Division de Tareas Sugerida (3 Integrantes)

### Integrante A - Lider Tecnico y Seguridad
**Responsable de:**
- Seccion 1: Introduccion
- Seccion 2: Criterios de Calidad, Seguridad y Cumplimiento Normativo
- IE1 (15%) + IE5 parcial
- Coordinar la matriz de trazabilidad

**Entregables:**
- `02-Informe/01-Introduccion/introduccion.md`
- `02-Informe/02-Criterios_Calidad/criterios_calidad.md`

### Integrante B - Estrategia y Tipos de Prueba
**Responsable de:**
- Seccion 3: Estrategia de Pruebas
- Seccion 4: Tipos de Pruebas
- Seccion 5: Recursos Necesarios
- IE2 (20%) + IE4 parcial

**Entregables:**
- `02-Informe/03-Estrategia_Pruebas/estrategia.md`
- `02-Informe/04-Tipos_Pruebas/tipos_pruebas.md`
- `02-Informe/05-Recursos/recursos.md`

### Integrante C - Casos de Prueba y Analisis
**Responsable de:**
- Seccion 6: Diseno de Casos de Prueba (minimo 5 casos)
- Seccion 7: Analisis de Cobertura y Matriz de Trazabilidad
- IE3 (20%) + IE5 parcial

**Entregables:**
- `02-Informe/06-Casos_Prueba/casos_prueba.md`
- `02-Informe/07-Analisis_Cobertura/analisis_cobertura.md`
- `03-Anexos/Matrices/matriz_trazabilidad.md`

### Tareas Conjuntas (Todos)
- Revision cruzada de secciones
- Consolidacion del informe final en `04-Entrega/`
- Verificacion de aspectos formales (formato, fuentes, interlineado)

---

## Aspectos Formales Obligatorios

Para no perder puntos por formato:

- [ ] **Portada:** Nombre completo de cada integrante, carrera, seccion, docente, fecha
- [ ] **Formato:** Word o PDF
- [ ] **Titulos:** Arial 12, negrita
- [ ] **Cuerpo:** Arial 11
- [ ] **Interlineado:** 1,5
- [ ] **Alineacion:** Texto justificado
- [ ] **Lenguaje:** Formal tecnico (evitar "nosotros pensamos", usar "se recomienda", "es imperativo", "el analisis evidencia")
- [ ] **Entrega:** Subir a plataforma AVA en el plazo indicado

---

## Checklist de Entrega Final

Antes de subir el informe, verifica:

- [ ] El informe incluye los 7 apartados principales
- [ ] Hay al menos 5 casos de prueba detallados con ID, descripcion, requerimiento, datos de entrada, resultado esperado, criterios de aceptacion y tipo
- [ ] Los casos de prueba estan vinculados a codigos de requerimiento del ERS (RF-1, NFR-SEG-1, etc.)
- [ ] Se menciona la Ley N° 19.628 de Proteccion de Datos Personales
- [ ] Se citan estandares tecnicos (ISO/IEC 25010, OWASP, WCAG)
- [ ] La matriz de trazabilidad esta completa
- [ ] El analisis de cobertura demuestra que todos los requerimientos estan cubiertos
- [ ] El formato cumple con los aspectos formales (Arial 11/12, interlineado 1.5, justificado)
- [ ] La portada tiene todos los datos del grupo
- [ ] Se ha revisado la redaccion y no hay faltas de ortografia

---

## Comandos Git Utiles para el Trabajo Colaborativo

```bash
# Clonar el repositorio (cada integrante)
git clone <URL_DEL_REPOSITORIO>

# Antes de empezar a trabajar
git pull origin main

# Crear una rama para tu seccion
git checkout -b feature/seccion-casos-prueba

# Despues de hacer cambios
git add .
git commit -m "feat: agrega casos de prueba PT-SEG-001 y PT-PERF-001"

# Subir tu rama
git push origin feature/seccion-casos-prueba

# Para integrar cambios (una vez revisados)
git checkout main
git merge feature/seccion-casos-prueba

# Ver estado actual
git status

# Ver historial de cambios
git log --oneline
```

---

## Notas Importantes

1. **Trabajar en ramas:** Cada integrante debe trabajar en su propia rama para evitar conflictos.
2. **Commits frecuentes:** Hacer commits pequenos y descriptivos.
3. **Reuniones de sincronizacion:** Acordar reuniones para revisar avances antes de consolidar.
4. **No modificar CodigoFuenteA:** El codigo fuente es solo referencia para entender el sistema. No modificar a menos que sea necesario para pruebas.
5. **Documentos base son solo lectura:** Los archivos en `01-Documentos_Base/` son la fuente de verdad. No modificarlos.

---

**Exito en la evaluacion!**
