# 10. Análisis Ético y Normativo de los Resultados

> **Estado: BORRADOR ESTRUCTURAL.** Las conclusiones dependen de los resultados reales de la sección 8. Las columnas "Resultado" deben completarse con la evidencia de ejecución; hasta entonces solo se citan los hallazgos *preliminares* de la sección 9.

## 10.1 Marco aplicable

| Marco | Disposición relevante | Aplicación a Atlas |
|---|---|---|
| Ley 19.628 | Art. 4 (consentimiento), art. 11 (deber de cuidado de los datos) | Atlas almacena RUT, direcciones, correos y datos bancarios de clientes de las pymes. |
| Ley 21.719 | Principios de licitud, proporcionalidad y seguridad; Agencia de Protección de Datos | *Verificar entrada en vigor antes de citarla como exigible.* Orienta las recomendaciones a futuro. |
| Ley 20.422 | Accesibilidad universal | NFR-USAB-1 (adultos mayores). |
| Ley 21.459 | Acceso ilícito a sistemas informáticos | Define el límite ético de las pruebas: solo el entorno entregado. |
| ISO/IEC 25010 | Seguridad, fiabilidad, eficiencia, usabilidad, compatibilidad | Estructura el criterio de calidad. |
| OWASP Top 10 2021 / ASVS | A01–A10 | Clasificación de vulnerabilidades. |
| WCAG 2.1 AA | POUR | Criterios de accesibilidad. |

## 10.2 Análisis normativo de resultados

| Resultado / hallazgo | Requerimiento | Norma o principio comprometido | Gravedad ética-legal | Resultado real (completar) |
|---|---|---|---|---|
| H-01 Contraseñas sin hash | NFR-SEG-2 | Ley 19.628 art. 11; OWASP A02/A07 | Alta: un acceso a la BD expone credenciales reutilizables. | |
| H-13 Datos bancarios sin cifrar | NFR-SEG-3 | Ley 19.628 art. 11; minimización y seguridad (Ley 21.719) | Alta | |
| H-09 Sin TLS | NFR-SEG-1 | Ley 19.628 art. 11; OWASP A02 | Alta | |
| H-02 / H-12 Sin RBAC / sin aislamiento | NFR-SEG-4, RB-2, RB-4 | Confidencialidad entre empresas; OWASP A01 | Crítica: una empresa podría ver datos de otra. | |
| H-07 Errores con detalle interno | NFR-SEG-6 | OWASP A05/A09 | Media | |
| (Rendimiento) latencia 4 s | NFR-PERF-1 | ISO/IEC 25010 Eficiencia | Media (calidad) | |
| (Accesibilidad) | NFR-USAB-1 | Ley 20.422; WCAG 2.1 AA | Por medir | |

## 10.3 Análisis ético

Principios a desarrollar con ejemplos del caso (no repetir definiciones genéricas; EP4-IE10 exige argumentar con evidencia):

1. **Responsabilidad profesional y no maleficencia:** un defecto como H-01 no es solo técnico; sus consecuencias recaen en los clientes finales de las pymes. Reportarlo con criticidad real, sin minimizarlo.
2. **Honestidad de los resultados:** informar los casos fallidos tal cual; distinguir *hallazgo estático* de *vulnerabilidad confirmada*.
3. **Privacidad desde el diseño y minimización:** ¿Atlas necesita almacenar número de cuenta completo? ¿Cuánto tiempo se conservan los datos de clientes eliminados?
4. **Inclusión:** el requerimiento de adultos mayores es un compromiso de equidad, no solo un criterio de aceptación.
5. **Uso responsable de las pruebas:** autorización explícita, entorno aislado, datos ficticios, sin explotación fuera del alcance. Ley 21.459.
6. **Divulgación responsable:** los hallazgos se reportan al equipo dueño del sistema (la asignatura/docente) y no se publican con detalle explotable.

## 10.4 Recomendaciones (vinculadas a evidencia)

Cada recomendación debe llevar: hallazgo, requerimiento, norma/principio y esfuerzo estimado.

| # | Recomendación | Hallazgo | Requerimiento | Norma/principio | Prioridad |
|---|---|---|---|---|---|
| R1 | Hashear contraseñas con bcrypt (cost ≥ 10) o Argon2 y migrar las existentes | H-01 | NFR-SEG-2 | Ley 19.628 art. 11 | Inmediata |
| R2 | Incluir el rol en el JWT y aplicar un middleware de autorización en backend; no confiar en el rol del cliente | H-02 | NFR-SEG-4, RB-4 | OWASP A01 | Inmediata |
| R3 | Verificar token y pertenencia a la empresa en **todos** los endpoints (middleware global) | H-12 | RB-2 | OWASP A01 | Inmediata |
| R4 | Exigir `JWT_SECRET` por entorno (fallar al iniciar si falta); eliminar secretos por defecto del código y compose | H-03, H-11 | NFR-SEG-9 | OWASP A05 | Inmediata |
| R5 | Terminar TLS (reverse proxy), HSTS y redirección HTTP→HTTPS | H-09 | NFR-SEG-1 | Ley 19.628 art. 11 | Alta |
| R6 | Implementar logout con lista de revocación / refresh token rotativo | H-04 | RF-1.2 | OWASP A07 | Alta |
| R7 | Eliminar `delay(4000)` y medir con k6 hasta cumplir p95 < 300 ms | H-05 | NFR-PERF-1 | ISO/IEC 25010 | Alta |
| R8 | Validar tipo/tamaño de archivo y almacenar fuera de la BD con referencia | H-08 | RF-5.2, RF-5.3 | OWASP A04 | Alta |
| R9 | Cifrar columnas bancarias en reposo | H-13 | NFR-SEG-3 | Ley 19.628 | Alta |
| R10 | Eliminación lógica (`deleted_at`) con confirmación | H-06 | RF-4 | Trazabilidad/auditoría | Media |
| R11 | Respuestas de error genéricas; detalle solo en logs internos | H-07 | NFR-SEG-6 | OWASP A05 | Media |
| R12 | `helmet`, CORS por lista blanca, rate-limit en login | H-10 | NFR-SEG-5 | OWASP A05/A07 | Media |
| R13 | Actualizar imagen base y dependencias; usuario no-root; integrar `npm audit` y Trivy al pipeline | H-14 | — | OWASP A06 | Media |
| R14 | Política de contraseñas ≥ 12 caracteres validada en backend | H-15 | §2.4 | OWASP A07 | Media |

## 10.5 Conclusión (completar tras la ejecución)

*Redactar en 1–2 párrafos: nivel real de cumplimiento (casos aprobados/fallidos), riesgo legal asociado y decisión recomendada (liberar / no liberar), argumentada con los incidentes de criticidad Crítica y Alta confirmados.*
