# 8. Ejecución de Pruebas

> **Regla de oro:** solo se registra lo que se ejecutó. Un caso no ejecutado figura como `No ejecutado`, nunca como `Aprobado`. Cada resultado debe tener evidencia en `06-Evidencias/` (captura legible o log) referenciada por nombre de archivo.

## 1. Escala de criticidad de incidentes

| Nivel | Definición | Ejemplo en Atlas | Plazo de corrección sugerido |
|---|---|---|---|
| **Crítica** | Compromete confidencialidad, integridad o autenticación de datos personales; explotable sin privilegios o con privilegios mínimos. | Contraseñas en texto plano; acceso a datos de otra empresa. | Inmediato; bloquea la liberación. |
| **Alta** | Incumple un requerimiento esencial del ERS o expone un vector de ataque relevante. | Sin TLS; sin revocación de sesión; umbral de rendimiento incumplido 10×. | Antes de la liberación. |
| **Media** | Debilita una defensa o degrada la calidad sin ruptura inmediata. | Mensajes de error con detalle interno; eliminación física. | Próxima iteración. |
| **Baja** | Desviación menor o de buenas prácticas. | Texto de ayuda incompleto. | Backlog. |

Cada incidente se clasifica además por **tipo de defecto** (funcional, seguridad, rendimiento, usabilidad, compatibilidad, disponibilidad) y por **categoría OWASP 2021** cuando aplique. Esta clasificación es el insumo de la defensa (EP4: "clasificación de los defectos").

## 2. Resumen de ejecución

*(Completar tras ejecutar. Cifras actuales: ninguna prueba dinámica ejecutada.)*

| Métrica | Valor |
|---|---|
| Casos diseñados | 30 |
| Casos ejecutados | 0 |
| Aprobados | — |
| Fallidos | — |
| Bloqueados | — |
| No ejecutados | 30 |
| Cobertura de diseño (requerimientos con caso) | 42/42 (100 %) |
| Cobertura de ejecución | 0/42 |
| Incidentes abiertos (Crítica / Alta / Media / Baja) | — |

**Entorno de ejecución oficial** *(completar en el taller):* equipo, SO, versión de Docker, comando, fecha, commit/versión del código, URL del front/back.

## 2b. Resultados preliminares (entorno temporal, fuera del taller)

> **Qué es esto y qué no es.** Antes de la sesión en el taller se verificaron manualmente 8 puntos de alto riesgo contra el mismo código fuente y el mismo `dump-atlas.sql`, levantados en un entorno temporal de desarrollo (Node + PostgreSQL nativos, **no el `docker compose` oficial**). Son datos reales, no simulados, pero **no reemplazan la ejecución oficial**: deben reconfirmarse en el stack Docker del taller y documentarse ahí con captura/log en `06-Evidencias/`. Se registran aquí para no perder el hallazgo y para orientar qué priorizar en el taller.

| # | Verificación | Comando (resumen) | Resultado real | Hallazgo que confirma |
|---|---|---|---|---|
| 1 | Payload del JWT emitido a un usuario con rol *editor* | `POST /autenticacion/login` (editor/editor) + decodificar el JWT | El payload **no contiene ningún campo de rol** | H-02 |
| 2 | Editor crea un cliente | `POST /clientes` con token de editor | HTTP **201** (debería ser 403) | H-02 |
| 3 | Editor elimina un cliente | `DELETE /clientes/{id}` con token de editor | HTTP **500** por restricción de clave foránea — falla por otra causa, no por control de rol (no hay 403) | H-02, H-06 |
| 4 | Auditoría sin autenticación | `GET /auditoria` sin cabecera `Authorization` | HTTP **200**, devuelve todos los registros de todas las empresas | H-19 |
| 5 | Listado de contratos sin autenticación | `GET /contratos` sin cabecera `Authorization` | HTTP 401 (este endpoint sí valida) | — (control, no incidente) |
| 6 | Alta de usuario con contraseña débil | `POST /usuarios` con `contrasena_hash="abc"` | HTTP **201** (sin política de contraseñas) | H-15 |
| 7 | Cierre de sesión | `POST /autenticacion/logout` | HTTP **404**, la ruta no existe | H-04 |
| 8 | Login correcto / incorrecto | `POST /autenticacion/login` con credenciales válidas e inválidas | 200 con token / 401, comportamiento correcto | — (control, no incidente) |

**Incidentes que estos resultados sustentan (a formalizar como INC-xxx tras la ejecución oficial):** ausencia de control de rol en el backend (puntos 1–3, criticidad propuesta: Crítica), exposición de auditoría sin autenticación (punto 4, Alta), ausencia de política de contraseñas (punto 6, Media), ausencia de cierre de sesión en el servidor (punto 7, Alta).

**Pendiente de esta ejecución preliminar:** no se guardó evidencia en `06-Evidencias/` porque el entorno era temporal y ya fue desmontado. Repetir los 8 puntos en el taller **con captura/log** antes de citarlos como resultado oficial en el informe.

## 3. Detalle de ejecución por caso

Copiar un bloque por caso ejecutado.

```
Caso: PT-XXX-000          Requerimiento(s): ________
Fecha/hora: ________      Ejecutor: ________
Herramienta: ________     Versión: ________
Datos de entrada: ________
Pasos reales: ________
Resultado obtenido: ________
Resultado esperado (ERS): ________
Veredicto: Aprobado | Fallido | Bloqueado
Evidencia: 06-Evidencias/PT-XXX-000_01.png
Incidente asociado: INC-___ (si Fallido)
```

## 4. Registro de incidentes

| ID | Caso | Requerimiento | Descripción | Tipo de defecto | OWASP | Criticidad | Hallazgo estático | Evidencia | Estado |
|---|---|---|---|---|---|---|---|---|---|
| INC-001 | | | | | | | | | Abierto |

## 5. Orden de ejecución sugerido

Priorizado por riesgo (EP4-IE8: secuencia lógica y trazable):

1. **Preparación:** `docker compose up`, verificar `/` y `/docs`, cargar datos de prueba (dos empresas, un admin y un editor por empresa).
2. **Análisis estático:** **SonarQube** (principal), Semgrep, npm audit, Gitleaks, Trivy, Hadolint → `06-Evidencias/estatico/` (guía: `03-Anexos/Herramientas/README.md`).
3. **Funcionales vía API** (Newman sobre `openapi.json`): PT-FUNC-002 → 011.
4. **Seguridad (autenticación/autorización):** PT-SEG-001, 002, 008, 009 (alto riesgo, ya con hipótesis H-01/H-02/H-12).
5. **Seguridad (DAST):** ZAP baseline → PT-SEG-005, 006, 003.
6. **Rendimiento:** k6 → PT-PERF-001 a 004.
7. **Usabilidad y compatibilidad:** Lighthouse/axe, teclado, navegadores → PT-USAB, PT-COMP.
8. **Disponibilidad/recuperación:** reinicio de contenedor, respaldo/restauración → PT-DIS-001.
9. **Consolidación:** actualizar la matriz (estado real), clasificar incidentes, redactar análisis ético-normativo.

## 6. Límites éticos de la ejecución

- Las pruebas intrusivas (inyección, fuerza bruta, manipulación de tokens) se ejecutan **únicamente** contra el entorno Docker local entregado por la asignatura. Ver §10 del informe y Ley 21.459.
- No se usan datos personales reales; los datos de prueba son ficticios.
- No se prueban sistemas de terceros ni la red del instituto.
