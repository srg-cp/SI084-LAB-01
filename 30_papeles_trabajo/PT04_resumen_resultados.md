# PT04 · Resumen y trazabilidad de resultados

**Fecha de ejecución:** 9 de septiembre de 2026  
**Alcance:** equipo propio con Windows 11, Docker Desktop y el entorno local `si084-lab`  
**Responsable:** Sergio Colque Ponce (`srg-cp`)

## Lynis

- Índice de endurecimiento: **53/100**.
- Resultado consolidado: **28 sugerencias** y ninguna advertencia formal en el reporte.
- Observaciones priorizadas:
  1. `AUTH-9262`: falta un módulo PAM para comprobar la robustez de contraseñas. Se relaciona con ISO/IEC 27001:2022 A.5.17 y COBIT DSS05.04.
  2. `FIRE-4590`: no se comprobó un cortafuegos o filtro de paquetes que controle tráfico entrante y saliente. Se relaciona con A.8.20 y DSS05.02.
  3. `ACCT-9628`: se recomienda habilitar `auditd` para recopilar información de auditoría. Se relaciona con A.8.15 y DSS01.03.
- Evidencia primaria: `20_evidencia/E04_config/lynis-report.dat`.

La imagen `cisofy/lynis:latest` indicada por la guía no se encontraba publicada. Para no sustituir la herramienta, se construyó la imagen `si084/lynis:official` desde el repositorio oficial `CISOfy/lynis-docker`. El intento fallido se conservó como evidencia de la incidencia.

## OpenSCAP

- Perfil: `xccdf_org.ssgproject.content_profile_cis_level1_server` para Ubuntu 22.04.
- Resultado: **15 reglas fallidas**, todas de severidad **Media**; no hubo reglas fallidas de severidad Alta.
- Entre los identificadores completos se encuentran:
  - `xccdf_org.ssgproject.content_rule_package_pam_pwquality_installed`
  - `xccdf_org.ssgproject.content_rule_accounts_passwords_pam_faillock_deny`
  - `xccdf_org.ssgproject.content_rule_accounts_passwords_pam_faillock_interval`
  - `xccdf_org.ssgproject.content_rule_accounts_passwords_pam_faillock_unlock_time`
  - `xccdf_org.ssgproject.content_rule_set_password_hashing_algorithm_logindefs`
- Evidencia primaria: `oscap-resultados.xml` y `oscap-reporte.html`.

La guía solicitaba extraer cinco fallos de severidad Alta, pero la ejecución real no produjo ninguno. Se presentan cinco reglas Medias representativas y se mantiene la limitación de forma expresa; no se eleva artificialmente su severidad. Ubuntu 22.04 tampoco ofreció el paquete `ssg-debderived`, por lo que se utilizó el *data stream* oficial de ComplianceAsCode 0.1.77.

## Docker Bench for Security

- Resultado consolidado: **105 registros `[WARN]`**.
- En las secciones 4 y 5 se observaron, entre otros, contenedores ejecutados como `root`, sistemas de archivos raíz de escritura, ausencia de restricciones de CPU, memoria y PID, y ausencia de `HEALTHCHECK` en seis de siete contenedores.
- Las reglas 5.10, 5.11, 5.26 y 5.28 sustentan el análisis de deficiencia de diseño del control A.8.6.
- Evidencia primaria: `20_evidencia/E04_config/docker-bench.log`.

## Trivy

- Vulnerabilidades de imágenes: **141**, de las cuales **8 son críticas** y **133 altas**.
- IaC: análisis ejecutado sobre `entorno/`, sin hallazgos adicionales incorporados a la matriz.
- Secretos: **5 detecciones**. Los valores y líneas de código se redactaron antes de versionar; se conservaron únicamente regla, categoría y ubicación para mantener la trazabilidad sin exponer material sensible.
- SBOM: generado para `bkimminich/juice-shop:latest` en formato CycloneDX.
- Evidencia primaria: los archivos `trivy_*.json`, `trivy_iac.*`, `trivy_secretos.*` y `sbom_juiceshop.json` de `20_evidencia/E04_config/`.

## Consolidación y validación

- Hallazgos totales: **294**.
- Origen: Docker Bench 105, Lynis 28, OpenSCAP 15, Trivy 141 y Trivy Secret 5.
- Hallazgos sin clasificar: **0 (0,0 %)**.
- Criterios: ISO/IEC 27001:2022 y objetivos COBIT 2019 de los dominios BAI y DSS.
- Papel de trabajo principal: `40_hallazgos/PT04_matriz_control.csv`.

La clasificación automática se revisó y amplió con reglas explícitas para controles de autenticación, privilegios, registro, vulnerabilidades, criptografía, red, capacidad, configuración y medios de almacenamiento. La columna `estado_revision` deja constancia de la revisión contra el criterio PT04.

## Pregunta de transferencia

Si una organización real ejecutara estas herramientas sin consolidar ni validar sus resultados, podría priorizar conteos duplicados o severidades técnicas fuera de contexto mientras deja sin tratar controles realmente ausentes. Además, publicar las salidas sin saneamiento expondría inventario, rutas y secretos que facilitarían ataques posteriores.

