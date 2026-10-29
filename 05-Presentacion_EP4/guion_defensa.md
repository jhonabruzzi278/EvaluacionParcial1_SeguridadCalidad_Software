# Guion de defensa EP4 (individual) — 10 min + 5 min de preguntas

Cada integrante debe poder presentar **todo** el flujo. Si no puede explicarlo con claridad, la pauta asume que no participó. Material de apoyo (diapositivas) se sube a AVA junto con el informe.

## Estructura (10 min)

| Min | Bloque | IE que puntúa | Qué decir (con ejemplo de Atlas) |
|---|---|---|---|
| 0:00–2:00 | **Enfoque estratégico** | IE2 (20 %) | Estrategia basada en riesgo: Atlas maneja datos personales y bancarios, por eso seguridad = prioridad P1. Combinación SAST + DAST + pruebas manuales. Ejemplo: se priorizó autenticación/autorización porque el ERS exige RBAC en backend (NFR-SEG-4). |
| 2:00–3:30 | **Herramientas y justificación** | IE2 | SonarQube (SAST principal: vulnerabilidades y *hotspots*) + Semgrep (complementa el análisis de flujo que la edición Community no cubre), ZAP (DAST), k6 (rendimiento), Lighthouse/axe (accesibilidad) y un cliente HTTP en Python sobre el OpenAPI (equivalente a la colección Newman que pide el ERS §3.1.2). Decir por qué se reemplazaron Cypress, JMeter y BrowserStack por lo ejecutable en el entorno local. |
| 3:30–6:30 | **Ejecución de pruebas** | IE8 (15 %), IE6 (15 %) | Recorrer una cadena completa: requerimiento → caso → ejecución → evidencia → incidente. Mostrar un caso Aprobado y uno Fallido. Presentar resultados del análisis estático y compararlos con la norma (Ley 19.628 art. 11, OWASP). |
| 6:30–8:00 | **Clasificación de defectos** | IE4 (38 %) | Tabla por criticidad y tipo; explicar el **origen** (de qué requerimiento/norma proviene la prueba) y el **impacto** (qué ocurre si falla) de cada tipo de prueba. |
| 8:00–10:00 | **Reflexión y recomendaciones** | IE10 (12 %) | 3 recomendaciones, cada una con hallazgo + requerimiento + norma/principio. Cerrar con límites éticos de las pruebas (Ley 21.459) y qué quedó fuera. |

## Preguntas probables (preparar respuesta de 30–45 s)

1. ¿Por qué se eligió una prueba de caja negra y no blanca para X? ¿Qué diferencia hay entre SAST y DAST?
2. ¿Qué tipo de prueba descubrió el defecto más grave y por qué las demás no lo habrían detectado? (*origen e impacto*)
3. ¿Cómo sabe que el 100 % de cobertura es real? (es el 100 % del **alcance**: 16 de los 42 requerimientos, elegidos por riesgo; frente al ERS completo es 38 %. Diferenciar cobertura de **diseño** y de **ejecución**; mostrar la matriz y lo que quedó fuera)
4. ¿Qué diferencia hay entre un hallazgo estático y una vulnerabilidad confirmada?
5. Un caso falló: ¿es un defecto del sistema o de la prueba? ¿Cómo lo descartó?
6. ¿Qué norma chilena aplica a los datos bancarios de los clientes y qué exige?
7. ¿Por qué un editor que puede borrar un cliente es un problema legal y no solo funcional? (RB-4, RB-2)
8. ¿Qué haría con los incidentes críticos antes de liberar? ¿Quién decide?
9. ¿Qué no se probó y por qué? (riesgos residuales)
10. ¿Qué cambió entre el plan de EP1 y lo ejecutado? (retroalimentación + hallazgos)

## Errores a evitar

- Decir "se probó/explotó" sobre algo que solo se leyó en el código.
- Presentar solo casos aprobados.
- Memorizar sin entender el origen de cada requerimiento.
- Citar la Ley 21.719 como vigente sin haber verificado su fecha de entrada en vigor.
