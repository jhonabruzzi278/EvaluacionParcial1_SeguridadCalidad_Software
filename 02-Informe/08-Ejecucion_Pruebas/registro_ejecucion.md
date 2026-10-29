# 8. Ejecución de Pruebas

> **Estado actual (29-oct-2026):** los 30 casos del plan completo se ejecutaron en el Docker local de Atlas (27 ejecutados: 7 aprobados, 20 fallidos; 3 no ejecutados). El informe final presenta 10 casos priorizados (1 aprobado, 9 fallidos, 12 incidentes). La evidencia por caso, `resultados_ejecucion.json` y `resumen_ejecucion.md` están en `06-Evidencias/ejecucion/`; el informe final (`04-Entrega/EP3/`) recoge los resultados. Las secciones 2 a 2c de este archivo son el registro histórico de las verificaciones previas.

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

*Plan completo de 30 casos. Detalle por caso en `06-Evidencias/ejecucion/resumen_ejecucion.md`.*

| Métrica | Valor |
|---|---|
| Casos diseñados | 30 |
| Casos ejecutados | 27 |
| Aprobados | 7 |
| Fallidos | 20 |
| Bloqueados | 0 |
| No ejecutados | 3 (PT-USAB-002, PT-USAB-003, PT-COMP-002) |
| Cobertura de diseño (requerimientos con caso) | 42/42 (100 %) |
| Cobertura de ejecución | 27/30 casos (90 %); 36 de 38 endpoints |
| Incidentes abiertos del plan completo (Crítica / Alta / Media / Baja) | 22 (4 / 8 / 9 / 1) |

**Entorno de ejecución:** equipo Linux Mint 22.3, Docker Compose (postgres:15-alpine, backend Node 18, frontend nginx), 29-oct-2026, frontend http://localhost:3350 y API http://localhost:4450, sobre una copia de `CodigoFuenteA` con `package-lock.json` generado.

## 2b. Verificaciones previas (entorno temporal; superadas por la ejecución en Docker)

> **Contexto.** Antes de levantar el stack con Docker se verificaron manualmente 8 puntos de alto riesgo en un entorno temporal (Node + PostgreSQL nativos). Esas verificaciones quedaron **superadas por la ejecución en Docker** del 29-oct-2026, cuya evidencia está en `06-Evidencias/ejecucion/`; se conservan como historial.

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

## 2c. Análisis estático con SonarQube (resultado real, entorno temporal)

> **Actualización (29-oct-2026):** el análisis se repitió con SonarQube en **Docker** (`sonarqube:community` 26.10.0.133078 + `sonar-scanner-cli`) sobre una copia del código con dependencias instaladas, con los mismos resultados (4 vulnerabilidades, 25 bugs, 9 code smells, Quality Gate OK) y evidencia guardada en `06-Evidencias/estatico/`. Sin dependencias instaladas SonarQube reporta solo 10 bugs (la regla S9383 necesita información de tipos). El texto siguiente se conserva como registro de la corrida inicial.

> Mismo tipo de advertencia que en §2b: SonarQube Community 26.10.0.133078 se ejecutó de forma **standalone** (Java, sin Docker) contra `CodigoFuenteA/BACKEND/src` y `CodigoFuenteA/FRONTEND/src` reales, sin modificarlos. Es la herramienta SAST oficial del plan (`03-Anexos/Herramientas/README.md` §1). El resultado es real y queda exportado como evidencia en `06-Evidencias/estatico/` (métricas, vulnerabilidades, bugs y code smells en JSON), pero debe **repetirse en el taller** con el Docker oficial para el informe final, dejando también capturas de pantalla del dashboard.

**Métricas generales** (`ncloc` = líneas de código no comentadas):

| Métrica | Valor |
|---|---|
| Líneas de código (ncloc) | 6 955 |
| Vulnerabilidades | 4 (1 Blocker, 2 Major, 1 Minor) |
| Bugs | 25 |
| Code smells | 9 |
| Security hotspots | 0 |
| Duplicación de líneas | 16,4 % |
| Quality Gate | **OK** (sin condiciones evaluadas: primer análisis del proyecto, sin línea base de código nuevo todavía) |

**Las 4 vulnerabilidades, con su severidad SonarQube:**

| Severidad | Archivo:línea | Mensaje de SonarQube | Hallazgo que confirma |
|---|---|---|---|
| **BLOCKER** | `BACKEND/src/db.js:6` | "Make sure this PostgreSQL password gets changed and removed from the code." | H-11 |
| MAJOR | `BACKEND/src/app.js:22` | "Make sure that enabling CORS is safe here." | H-10 |
| MAJOR | `BACKEND/src/routes/contracts.js:15` | "Make sure the content length limit is safe here." | H-08 |
| MINOR | `BACKEND/src/app.js:20` | "This framework implicitly discloses version information by default. Make sure it is safe here." | H-10 |

Los 25 bugs son mayoritariamente del frontend (promesas sin `await`/`.catch` en los componentes de React: `Layout.jsx`, `Home.jsx`, `Login.jsx`, `Register.jsx`, formularios de clientes/contratos, etc.) — no estaban catalogados como hallazgo de seguridad (H-xx) porque son defectos de calidad/mantenibilidad, no de seguridad; se incorporan a la sección 7 del informe como evidencia de calidad de código. Detalle completo en `06-Evidencias/estatico/sonarqube_bugs.json`.

**Lectura para el informe (IE6/EP4):** SonarQube confirma con una herramienta independiente 3 de los hallazgos obtenidos por revisión manual (H-08, H-10, H-11), y marca el de credenciales por defecto como **Blocker** — el nivel más alto de su escala, coherente con la criticidad "Crítica/Alta" que ya le habíamos asignado. Cero *security hotspots* detectados no significa ausencia de más vulnerabilidades: la edición Community no incluye *taint analysis* (ver `03-Anexos/Herramientas/README.md` §1), por lo que H-01, H-02, H-12, H-17, H-19 (todos de lógica de autorización) no son detectables por esta herramienta y siguen dependiendo de los casos de prueba dinámicos.

**Nota:** estos 8 puntos no guardaron evidencia; los mismos hallazgos se reconfirmaron con evidencia en la ejecución en Docker (PT-SEG-001, 002, 008, 009 y PT-FUNC-010, entre otros).

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
