# Pautas para armar el Prezi — EP4 (defensa individual, 10 min + 5 min de preguntas)

Complementa a `guion_defensa.md` (qué decir) con **cómo armar la presentación** (qué mostrar). El Prezi debe contar el proceso de aseguramiento de calidad de Atlas de principio a fin: **planificación → estrategia → casos de prueba → ejecución → vulnerabilidades principales**.

## 1. Idea central

Un solo hilo narrativo: *"Atlas maneja datos personales de terceros; por eso planificamos las pruebas según el riesgo, las ejecutamos con evidencia y clasificamos lo que falló."* Cada tema del Prezi responde a un criterio de la pauta EP4:

| Tema del Prezi | Tiempo | Criterio que puntúa | Contenido mínimo |
|---|---|---|---|
| 1. Contexto y planificación | 0:00–1:00 | IE2 (20 %) | Qué es Atlas, 42 requerimientos del ERS, por qué la seguridad es prioridad P1, alcance. |
| 2. Estrategia y herramientas | 1:00–3:00 | IE2 (20 %) | Enfoque mixto basado en riesgo; SAST + DAST + manual; por qué cada herramienta (SonarQube, ZAP, k6, Lighthouse, Newman) y por qué se descartaron otras. |
| 3. Casos de prueba | 3:00–5:00 | IE4 (38 %) | 30 casos, cobertura 42/42; los 5 casos representativos (FUNC-001, SEG-001, SEG-002, PERF-001, USAB-001) con **origen** (de qué requerimiento nace) e **impacto** (qué pasa si falla). |
| 4. Ejecución y vulnerabilidades | 5:00–8:00 | IE8 y IE6 (15 % c/u) | Una cadena completa: requerimiento → caso → ejecución → evidencia → incidente. Un caso aprobado y uno fallido. Tabla de criticidad. Resultado de SonarQube. |
| 5. Reflexión normativa y ética | 8:00–10:00 | IE10 (12 %) | 3 recomendaciones (hallazgo + requerimiento + norma), límites éticos (Ley 21.459), qué quedó sin probar. |

> Los pesos salen de `00-Analisis_Rubricas/` y del guion; confírmalos contra `01-Documentos_Base/Pauta_EP4_403029208.pdf`.

## 2. Estructura del lienzo en Prezi

Prezi no es una secuencia de láminas: es **un lienzo grande con zoom**. Úsalo para que se vea el recorrido.

1. **Vista general (Overview):** un mapa con los **5 temas** como burbujas o estaciones dispuestas en una línea o círculo, en el orden del proceso de QA. Es la imagen que se ve al inicio y al final.
2. **Un tema = una zona del lienzo.** Dentro de cada una, 2–3 vistas (subtemas) como máximo. Total recomendado: **12–15 vistas** para 10 minutos (≈ 40–50 s por vista).
3. **Ruta lineal.** Define el camino con el orden de presentación (en Prezi Present: temas y subtemas ordenados en el panel izquierdo). Evita rutas que vuelvan atrás.
4. **Regla de zoom:** zoom *hacia adentro* para detalle (una captura, una tabla) y *hacia afuera* para volver al mapa entre temas. No hagas más de un salto grande por tema: marea.
5. **Cierre:** vuelve a la vista general y deja visible la frase final (conclusión: *"no liberar hasta corregir los críticos"*).

## 3. Qué poner en cada vista (sugerencia de 14 vistas)

| # | Vista | Qué mostrar |
|---|---|---|
| 1 | Portada / mapa | Título "Atlas: verificando calidad, seguridad y cumplimiento", integrantes, mapa de 5 temas. |
| 2 | Contexto | Diagrama simple: Front (React) → API (Express) → PostgreSQL, todo en Docker. Datos sensibles que maneja. |
| 3 | Planificación | Línea de tiempo EP1 → EP3 → EP4; el feedback de EP1 (cobertura 6/20) y lo que se corrigió (6 → 42 requerimientos). |
| 4 | Estrategia | Esquema SAST / DAST / manual y prioridades P1–P3. Una frase: *"seguridad primero porque hay datos personales"*. |
| 5 | Herramientas | Ícono + una línea por herramienta: qué prueba y por qué se eligió. |
| 6 | Cobertura | Gráfico o cifra grande: **30 casos → 42/42 requerimientos (100 %)**. Distinguir cobertura de *diseño* y de *ejecución*. |
| 7 | Casos representativos | Los 5 casos en tarjetas: ID, requerimiento, tipo y qué verifica. |
| 8 | Origen e impacto por tipo | Una tabla corta: tipo de prueba → de qué nace → qué pasa si falla (alimenta IE4, el criterio más pesado). |
| 9 | Ejecución: caso fallido | PT-SEG-002 (RBAC): captura del JWT sin rol + respuesta 201 del editor. |
| 10 | Ejecución: caso aprobado | Un control que funciona (p. ej. login válido/inválido) para mostrar que no solo hay fallos. |
| 11 | Criticidad | Semáforo CRÍTICO / GRAVE / MODERADO / LEVE con los 8 incidentes ubicados en él. |
| 12 | Análisis estático | Panel de SonarQube: 4 vulnerabilidades (1 Blocker), 25 bugs; qué confirma de la revisión manual (H-08, H-10, H-11) y qué **no** puede detectar. |
| 13 | Normativa y ética | Ley 19.628 art. 11, OWASP, Ley 21.459; 3 recomendaciones con hallazgo → requerimiento → norma. |
| 14 | Cierre | Qué quedó sin probar (riesgos residuales) y conclusión. |

## 4. Reglas de diseño

- **Pocas palabras por vista:** una idea, máximo 20–25 palabras. Lo demás lo dices tú.
- **Evidencia real, legible:** capturas recortadas al dato relevante (código de estado, línea de código, panel). Si no se lee a 2 metros, se recorta o se amplía. Nombra las capturas como en `06-Evidencias/` (PT-XXX-000_01.png).
- **Un solo color por significado:** rojo = crítico, naranja = grave, amarillo = moderado, verde = leve/aprobado. Los mismos del informe.
- **Tipografía grande y contraste alto** (se proyecta). Dos fuentes como máximo.
- **No abuses de animaciones ni de giros de lienzo:** el zoom ya es el efecto; rotar el lienzo resta claridad.
- **Cifras con fuente:** toda cifra viene del informe o de `06-Evidencias/` (30 casos, 42 requerimientos, 4 vulnerabilidades, 19 hallazgos). Si una cifra cambió tras el taller, actualízala en ambos.
- **No afirmar lo que no se ejecutó.** Un hallazgo leído en el código es una *hipótesis*; solo es *vulnerabilidad confirmada* si hay evidencia de ejecución. Rotula "preliminar" lo que viene del entorno temporal hasta reconfirmarlo en el Docker del taller.

## 5. Mecánica práctica en Prezi

1. Crea el Prezi desde una plantilla en blanco o de estilo sobrio (Prezi Present). Evita plantillas con muchos efectos.
2. Arma primero el **mapa** (Overview) y las 5 zonas; después rellena vistas.
3. Inserta imágenes (capturas) con *Insert → Image*; los diagramas simples (arquitectura, semáforo) se pueden dibujar con las formas de Prezi o importar desde una imagen.
4. Usa las **notas del presentador** de cada vista para tu guion; así el Prezi queda limpio.
5. Prueba el modo presentación completo **cronometrado** (objetivo: 9:30 para tener margen).
6. Revisa cómo se ve en el computador del taller (resolución, conexión). Ten un **respaldo sin Internet**: exporta a PDF o PowerPoint si tu plan lo permite (la descarga/exportación puede depender del plan de Prezi: verifícalo con tiempo) o guarda capturas de las vistas.
7. **Entrega en AVA:** la pauta pide subir el informe y el material de apoyo. Sube el PDF/exportación del Prezi y el enlace de visualización. Comparte el enlace con permiso de solo ver y comprueba que abra en una ventana de incógnito.

## 6. Defensa individual: cómo preparar el Prezi para que lo domines

- Los tres integrantes presentan **todo el flujo**, no solo su parte; la nota es individual y depende de lo que cada uno demuestre.
- Ensaya con la ruta del Prezi, pero memoriza **el hilo** (requerimiento → caso → evidencia → incidente → norma), no el texto.
- Prepara respuestas de 30–45 s a las preguntas de `guion_defensa.md` y deja en el lienzo, fuera de la ruta, una zona de **respaldo** (matriz de trazabilidad, tabla de 19 hallazgos, escala de criticidad) a la que puedas hacer zoom si te preguntan.
- Si algo falló en vivo, dilo y explica qué evidencia lo respalda; es preferible a improvisar.

## 7. Lista de verificación antes de entregar

- [ ] 5 temas en el mapa, en el orden del proceso de QA; 12–15 vistas en total.
- [ ] Hay un caso **aprobado** y uno **fallido** con captura real.
- [ ] Aparecen las cinco categorías de la pauta: enfoque estratégico, herramientas y justificación, ejecución, clasificación de defectos, reflexión normativa/ética.
- [ ] Cada tipo de prueba explica **origen** e **impacto**.
- [ ] Las cifras coinciden con el informe actualizado tras el taller.
- [ ] Lo "preliminar" está rotulado o ya fue reemplazado por resultados oficiales.
- [ ] Probado cronometrado (≤ 10 min) y con respaldo exportado.
- [ ] Subido a AVA junto con el informe.
