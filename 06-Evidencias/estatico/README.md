# Evidencia SonarQube — EP3/EP4

Generado el 2026-10-29 con SonarQube Community 26.10.0.133078 en Docker (`03-Anexos/Herramientas/sonarqube/docker-compose.sonar.yml`,
imagen `sonarqube:community`) y `sonarsource/sonar-scanner-cli`, contra `BACKEND/src` y `FRONTEND/src` de `CodigoFuenteA/`.
Se analizó una **copia con las dependencias instaladas** (`npm install`) para no modificar el código entregado; sin dependencias
SonarQube reporta solo 10 bugs en lugar de 25 (la regla S9383 necesita información de tipos).

Archivos:
- `sonarqube_metricas.json` — ncloc, vulnerabilities, bugs, code_smells, security_hotspots, duplicacion
- `sonarqube_vulnerabilidades.json` — detalle de las 4 vulnerabilidades (incluye 1 BLOCKER)
- `sonarqube_bugs.json` — detalle de los 25 bugs
- `sonarqube_code_smells.json` — detalle de los 9 code smells
- `sonarqube_01_overview.png` — resumen del proyecto (Quality Gate, Security 4, Reliability 34, Maintainability 9)
- `sonarqube_02_vulnerabilidades.png` — las 4 vulnerabilidades (db.js:6 Blocker)
- `sonarqube_03_bugs.png` — bugs (25)
- `sonarqube_04_code_smells.png` — code smells (9)

Las capturas son del panel real (http://localhost:9000, proyecto `atlas-ep3`) del mismo análisis. `sonarqube_version.json` registra la versión del servidor.

Para repetir el análisis: `03-Anexos/Herramientas/README.md` §1.
