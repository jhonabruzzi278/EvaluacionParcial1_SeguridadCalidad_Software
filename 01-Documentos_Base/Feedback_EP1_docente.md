# Feedback del docente — EP1 (transcrito literalmente)

**Calificación de rúbrica: 86 / 100**

**Comentario del docente:**
> "Obtuviste una Muy Buena Nota. El Índice del documento no lo veo definido (poca prolijidad), y en punto de Coberturas y Pertinencias del Plan de Pruebas lo veo demasiado breve."

| Indicador | Peso | Puntaje | Nivel | Descriptor |
|---|---|---|---|---|
| IE1 Importancia de calidad, seguridad y cumplimiento legal | 15 % | 15 | Muy buen desempeño | Claridad y profundidad, ejemplos pertinentes, lenguaje técnico adecuado |
| IE2 Clasifica tipos de pruebas y su propósito | 20 % | 20 | Muy buen desempeño | Clasifica y describe todos los tipos justificando propósito y aplicación |
| IE3 Pruebas no funcionales: propósito y contexto | 20 % | 20 | Muy buen desempeño | Casos representativos con criterios de aceptación y propósito coherentes |
| IE4 Elementos del plan de pruebas | 25 % | 25 | Muy buen desempeño | Todos los apartados con coherencia técnica y vínculo a requerimientos y normativas |
| **IE5 Cobertura, pertinencia y coherencia** | **20 %** | **6** | **Desempeño incipiente** | **"Presenta análisis confuso o con errores conceptuales."** |

**Total: 15 + 20 + 20 + 25 + 6 = 86.**

## Lectura

- El único indicador débil es IE5 (en EP3 es **IE9**, mismo contenido, 12 %). Perdió 14 de los 100 puntos.
- El comentario habla de "demasiado breve", pero el **descriptor de la rúbrica** dice "confuso o con errores conceptuales". El descriptor es lo que determina el nivel; hay que corregir **ambas** cosas: profundidad y exactitud.
- "Índice no definido": el docx entregado conserva el texto de relleno de Word (*"Haga clic derecho aquí y seleccione 'Actualizar campo'…"*). Nunca se generó.

## Ajustes comprometidos para EP3

| # | Observación | Ajuste | Dónde |
|---|---|---|---|
| F1 | Índice no definido | Índice automático real (estilos de título + "Actualizar tabla"), más índice de tablas; verificar en el PDF final | `02-Informe/00-Indice/` |
| F2 | Cobertura y pertinencia demasiado breve | Sección reescrita: cobertura en 6 dimensiones con datos, pertinencia basada en riesgo, coherencia con verificaciones y brechas reconocidas | `02-Informe/07-Analisis_Cobertura/` |
| F3 | Análisis confuso / errores conceptuales | Eliminar afirmaciones contradictorias (p. ej. "Cumple parcialmente 84 %" junto a "todos los RF/NFR tienen casos"); distinguir cobertura de **diseño** vs **ejecución** vs **código**; re-contar sobre los 42 requerimientos reales del ERS | Ídem + `03-Anexos/Matrices/` |
