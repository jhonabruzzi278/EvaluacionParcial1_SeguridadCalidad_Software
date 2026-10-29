# Índice definido del informe EP3 (respuesta al feedback F1)

El feedback indicó que el índice "no está definido". En el informe EP1 el docx conservó el texto de relleno de Word y nunca se generó. Esta estructura numerada es la **fuente única**: las carpetas de `02-Informe/` usan la misma numeración que las secciones del informe.

## Estructura final

| N.º | Sección | Carpeta | Indicador (rúbrica EP3) |
|---|---|---|---|
| — | Portada, índice general, índice de tablas | — | Formato |
| 1 | Introducción: contexto, propósito, alcance, objetivos, referencias | `01-Introduccion` | IE7 |
| 2 | Importancia y criterios de calidad, seguridad y cumplimiento normativo | `02-Criterios_Calidad` | IE1 |
| 3 | Plan de pruebas: estrategia, criterios de entrada/salida y aceptación, priorización, herramientas, cronograma | `03-Estrategia_Pruebas` | IE7 |
| 4 | Tipos de prueba: clasificación, propósito y justificación | `04-Tipos_Pruebas` | IE3 (38 %) |
| 5 | Recursos: humanos, técnicos y de entorno | `05-Recursos` | IE7 |
| 6 | Diseño de casos de prueba (≥ 5; propuestos 8) | `06-Casos_Prueba` | IE5 |
| 7 | Análisis de cobertura, pertinencia y coherencia | `07-Analisis_Cobertura` | IE9 |
| 8 | Ejecución de pruebas: resumen, detalle, incidentes y criticidad | `08-Ejecucion_Pruebas` | IE5, IE9 |
| 9 | Análisis estático del código | `09-Analisis_Estatico` | IE1, IE9 |
| 10 | Análisis ético y normativo, recomendaciones y conclusión | `10-Analisis_Etico_Normativo` | IE1 |
| A | Anexo A — Matriz de trazabilidad completa | `03-Anexos/Matrices` | IE9 |
| B | Anexo B — Evidencias (capturas y logs) | `06-Evidencias` | — |
| C | Anexo C — Respuesta al feedback de EP1 | `01-Documentos_Base/Feedback_EP1_docente.md` | Exigido por la pauta |

> El plan de pruebas que pide la rúbrica (introducción, alcance, objetivos, estrategia, recursos, cronograma) se reparte entre las secciones 1, 3 y 5. Para que el evaluador lo encuentre, la **Sección 3 abre con una tabla** "Dónde está cada apartado del plan" que remite a esas secciones.

## Cómo generar el índice correctamente en Word

1. Aplicar los estilos **Título 1** (secciones) y **Título 2** (subsecciones) a todos los encabezados. No poner negrita manual. Configurar ambos estilos en Arial 12, negrita.
2. Insertar › Referencias › **Tabla de contenido** (automática, 2 niveles).
3. Numerar las tablas con **Insertar título** ("Tabla 1…") y generar el **índice de tablas**.
4. Antes de exportar: **Ctrl+A › F9 › "Actualizar toda la tabla"**. Confirmar que no queda ningún texto de relleno como "Haga clic derecho…".
5. Exportar a PDF y **abrir el PDF** para comprobar que el índice muestra títulos y números de página reales y que los enlaces funcionan.
6. Inserción de números de página en el pie; la portada sin número.

## Verificación previa a la entrega

- [ ] El índice lista las 10 secciones y los 3 anexos con página.
- [ ] La numeración del índice coincide con la del cuerpo.
- [ ] Ningún encabezado quedó fuera del índice (estilo mal aplicado).
- [ ] Búsqueda de "Completar", "[X]" y "Haga clic" devuelve 0 resultados.
- [ ] Formato: Arial 12 títulos · Arial 11 cuerpo · interlineado 1,5 · justificado.
