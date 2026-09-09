# INFORME DE LABORATORIO N.º 04

## Auditoría de configuración segura con Lynis, OpenSCAP, Docker Bench y Trivy

**Curso:** SI-084 · Auditoría de Sistemas  
**Semana:** 04 · **Unidad:** I · **Grupo:** COLQUE  
**Estudiante:** Sergio Colque Ponce  
**Código universitario:** 2022073503  
**Fecha:** 9 de septiembre de 2026  
**Docente:** Dr. Oscar Juan Jimenez Flores

## 1. Información sobre el evento práctico

### 1.1 Título del evento práctico

Evaluación automatizada de controles generales de TI mediante herramientas libres de auditoría de configuración, contrastando la evidencia técnica con CIS Benchmarks, ISO/IEC 27001:2022 y COBIT 2019.

### 1.2 Objetivos

- Auditar el endurecimiento del sistema mediante Lynis.
- Evaluar un perfil normativo CIS Level 1 Server mediante OpenSCAP.
- revisar la seguridad del plano de contenedores mediante Docker Bench for Security.
- Identificar vulnerabilidades, configuraciones IaC, posibles secretos y componentes mediante Trivy.
- Consolidar los resultados en una matriz única mapeada a ISO/IEC 27001:2022 y COBIT 2019.
- Diferenciar una deficiencia de diseño de una deficiencia de eficacia operativa sobre evidencia real.

### 1.3 Tiempo de duración

100 minutos de laboratorio guiado y tiempo adicional de descarga, consolidación, revisión y documentación.

### 1.4 Resultados de aprendizaje

- RA1: analiza e interpreta conceptos y terminología de Auditoría de Sistemas.
- RA2: evalúa la seguridad de la información en Auditoría de Sistemas.

### 1.5 Recursos

| Recurso | Versión o detalle | Propósito |
|---|---|---|
| Docker Desktop | 4.40.0; cliente y motor 28.0.4 | Ejecutar el entorno local y las herramientas aisladas |
| Lynis | Imagen construida desde `CISOfy/lynis-docker` | Auditoría de endurecimiento del sistema |
| OpenSCAP y ComplianceAsCode | OpenSCAP en Ubuntu 22.04; contenido 0.1.77 | Evaluación del perfil CIS Level 1 Server |
| Docker Bench for Security | Imagen `docker/docker-bench-security` | Verificación contra CIS Docker Benchmark |
| Trivy | Imagen `aquasec/trivy:latest` | Vulnerabilidades, IaC, secretos y SBOM |
| Python | 3.11 | Consolidación y validación de la matriz |

### 1.6 Seguridad y alcance

La ejecución se limitó al equipo propio y al entorno Docker local `si084-lab`. No se analizaron sistemas institucionales, direcciones públicas ni equipos de terceros. Los reportes se trataron como confidenciales: antes de versionarlos se redactaron valores de secretos, líneas de código sensibles, nombres privados de registro y datos identificadores del anfitrión. Las copias originales permanecen fuera de Git en `.private/S04_originales/`.

## 2. Procedimiento o metodología

### Paso A — Auditoría del sistema con Lynis

Se intentó primero la imagen indicada por la guía. Al no existir `cisofy/lynis:latest` en el registro, se documentó el error y se construyó una imagen desde el repositorio oficial `CISOfy/lynis-docker`. Lynis auditó el sistema montado en modo de solo lectura y produjo el reporte, el log y la salida de consola.

### Paso B — Evaluación formal con OpenSCAP

Se ejecutó el perfil `xccdf_org.ssgproject.content_profile_cis_level1_server` sobre Ubuntu 22.04. Como el paquete `ssg-debderived` no estaba disponible, se descargó el *data stream* precompilado de Ubuntu 22.04 de ComplianceAsCode 0.1.77. El código de salida 2 fue conservado porque OpenSCAP lo utiliza cuando existen reglas que no cumplen.

### Paso C — Revisión CIS de Docker

Docker Bench for Security inspeccionó el *daemon*, las imágenes y los siete contenedores operativos del laboratorio. Se conservaron el log completo y la salida reproducible, con especial atención a las secciones 4 y 5.

### Paso D — Escaneo con Trivy

Se analizaron las imágenes `bkimminich/juice-shop:latest`, `postgres:16`, `wordpress:latest` y `mariadb:11`; la infraestructura como código de `entorno/`; los posibles secretos del repositorio; y el SBOM CycloneDX de Juice Shop. Los valores sensibles de las detecciones de secretos fueron omitidos de la versión publicable.

### Paso E — Consolidación, validación y sellado

El script `PT04_matriz_control.py` convirtió las salidas a un esquema común, asignó un identificador `S04-NNNN`, mapeó cada registro a ISO/IEC 27001:2022 y COBIT 2019 y marcó su estado de revisión. Se comprobó el porcentaje sin clasificar, se documentó un control en los planos de diseño y eficacia operativa y se calcularon hashes SHA-256.

## 3. Resultados y evidencias

### 3.1 Resultados principales evaluados

| Resultado | Estado y resultado real | Evidencia verificable |
|---|---|---|
| Matriz única de control | Logrado: 294 hallazgos de las cuatro herramientas, mapeados a ISO/IEC 27001 y COBIT 2019 | [PT04_matriz_control.csv](https://github.com/srg-cp/SI084-LAB-01/blob/taller-04/40_hallazgos/PT04_matriz_control.csv) |
| Clasificación completada | Logrado: 0 hallazgos sin clasificar, equivalente a 0,0 % | [Script de consolidación](https://github.com/srg-cp/SI084-LAB-01/blob/taller-04/30_papeles_trabajo/PT04_matriz_control.py) y [captura 06](https://github.com/srg-cp/SI084-LAB-01/blob/taller-04/docs/evidencias/S04/06_matriz_validacion.png) |
| Diseño frente a eficacia operativa | Logrado: A.8.6 se concluyó como deficiencia de diseño por ausencia de límites de recursos y `HEALTHCHECK` en la IaC | [PT04_diseno_vs_eficacia.md](https://github.com/srg-cp/SI084-LAB-01/blob/taller-04/30_papeles_trabajo/PT04_diseno_vs_eficacia.md) |

### 3.2 Resultados técnicos

1. **Lynis.** Se obtuvo un índice de endurecimiento de 53/100 y 28 sugerencias. Se priorizaron `AUTH-9262`, `FIRE-4590` y `ACCT-9628`. Evidencia: [lynis-report.dat](https://github.com/srg-cp/SI084-LAB-01/blob/taller-04/20_evidencia/E04_config/lynis-report.dat) y [captura 02](https://github.com/srg-cp/SI084-LAB-01/blob/taller-04/docs/evidencias/S04/02_lynis_indice_y_sugerencias.png).
2. **OpenSCAP.** Se registraron 15 reglas XCCDF fallidas, todas de severidad Media. La ejecución no produjo fallos de severidad Alta, por lo que se documentó esta limitación sin alterar la evidencia. Evidencia: [resultados XML](https://github.com/srg-cp/SI084-LAB-01/blob/taller-04/20_evidencia/E04_config/oscap-resultados.xml), [reporte HTML](https://github.com/srg-cp/SI084-LAB-01/blob/taller-04/20_evidencia/E04_config/oscap-reporte.html) y [captura 03](https://github.com/srg-cp/SI084-LAB-01/blob/taller-04/docs/evidencias/S04/03_openscap_reglas_fallidas.png).
3. **Docker Bench.** Se consolidaron 105 advertencias. Las secciones 4 y 5 mostraron ejecución como `root`, sistemas raíz escribibles y ausencia de controles de capacidad y salud. Evidencia: [docker-bench.log](https://github.com/srg-cp/SI084-LAB-01/blob/taller-04/20_evidencia/E04_config/docker-bench.log) y [captura 04](https://github.com/srg-cp/SI084-LAB-01/blob/taller-04/docs/evidencias/S04/04_docker_bench_advertencias.png).
4. **Trivy.** Se identificaron 141 vulnerabilidades de imagen —8 críticas y 133 altas— y 5 detecciones de secretos cuyos valores fueron redactados. También se ejecutó el análisis IaC y se generó el SBOM CycloneDX. Evidencia: [directorio E04_config](https://github.com/srg-cp/SI084-LAB-01/tree/taller-04/20_evidencia/E04_config), [captura 05](https://github.com/srg-cp/SI084-LAB-01/blob/taller-04/docs/evidencias/S04/05_trivy_resumen.png) y [SBOM](https://github.com/srg-cp/SI084-LAB-01/blob/taller-04/20_evidencia/E04_config/sbom_juiceshop.json).
5. **Integridad.** Se calcularon hashes SHA-256 para las evidencias publicables y la matriz. Evidencia: [SHA256SUMS_E04.txt](https://github.com/srg-cp/SI084-LAB-01/blob/taller-04/20_evidencia/SHA256SUMS_E04.txt) y [cadena de custodia](https://github.com/srg-cp/SI084-LAB-01/blob/taller-04/20_evidencia/CADENA_DE_CUSTODIA.md).

### 3.3 Análisis de diseño y eficacia operativa

El control A.8.6 Gestión de la capacidad no está incorporado en el archivo `docker-compose.yml`: faltan límites de memoria, CPU y PID y comprobaciones de salud adecuadas. La misma ausencia fue observada por Docker Bench en los contenedores operativos. Por ello se trata de una **deficiencia de diseño**, no solo de eficacia operativa. Si las restricciones existieran en la definición pero no se aplicaran al ejecutar los contenedores, correspondería clasificar el problema como eficacia operativa.

### 3.4 URL de entrega

- Versión etiquetada: <https://github.com/srg-cp/SI084-LAB-01/tree/taller-04>
- Pull Request hacia `develop`: `[COMPLETAR DESPUÉS DE PUBLICAR]`
- Índice de evidencias: <https://github.com/srg-cp/SI084-LAB-01/blob/taller-04/docs/evidencias/S04/README.md>

### 3.5 Riesgo de transferencia

Una organización que confíe en las salidas automáticas sin consolidarlas podría remediar síntomas duplicados y dejar sin tratar controles ausentes. Si además publica los reportes sin saneamiento, expondría inventario, rutas y secretos aprovechables por un atacante.

### 3.6 Problemas y mejoras

- La imagen de Lynis indicada en la guía no estaba disponible. Se reemplazó por una compilación reproducible desde el repositorio oficial y se conservó el intento fallido.
- Ubuntu 22.04 no ofreció `ssg-debderived`. Se usó el contenido oficial precompilado de ComplianceAsCode 0.1.77.
- OpenSCAP produjo 15 fallos Medios y cero Altos. La guía pedía cinco Altos, pero se reportó el resultado real y cinco identificadores Medios representativos.
- La primera salida de Trivy contenía valores potencialmente sensibles. Antes de versionar se archivaron los originales fuera de Git, se redactaron 51 elementos sensibles y se recalcularon los hashes.
- La ejecución final de la matriz y la captura 06 verifican 0 de 294 hallazgos sin clasificar (0,0 %).

## 4. Conclusiones

1. Las cuatro herramientas generaron hallazgos técnicos heterogéneos; la matriz única permitió convertir 294 registros en evidencia de auditoría trazable contra ISO/IEC 27001:2022 y COBIT 2019.
2. La validación manual fue indispensable: el mapeo inicial basado solo en palabras clave podía producir asociaciones falsas, mientras que la revisión final redujo los hallazgos sin clasificar a 0,0 % y conservó el criterio aplicado.
3. La ausencia simultánea de límites de recursos en la infraestructura como código y en los contenedores demuestra una deficiencia de diseño de A.8.6. La recomendación correcta es diseñar e incorporar el control antes de evaluar su eficacia operativa.
4. La evidencia automatizada también crea riesgo de divulgación. Redactar secretos y datos del anfitrión antes de publicar, sin perder los originales ni sus hashes, es parte del trabajo de auditoría y no una tarea administrativa secundaria.
5. Una limitación documentada —como la inexistencia de fallos OpenSCAP Altos— conserva más valor probatorio que modificar la severidad para aparentar cumplimiento de una lista de cotejo.

## 5. Cuestionario

La guía del Taller 04 no presenta un cuestionario independiente. La pregunta de transferencia se respondió en la sección 3.5.

## 6. Referencias bibliográficas

- Aqua Security. (2026). *Trivy Documentation*. <https://trivy.dev/>
- Center for Internet Security. (2026). *CIS Benchmarks*. <https://www.cisecurity.org/cis-benchmarks>
- CISOfy. (2026). *Lynis — Security auditing tool*. <https://cisofy.com/lynis/>
- ComplianceAsCode. (2025). *SCAP Security Guide 0.1.77*. <https://github.com/ComplianceAsCode/content>
- ISACA. (2018). *COBIT 2019 Framework: Governance and Management Objectives*. <https://www.isaca.org/resources/cobit>
- ISO. (2022). *ISO/IEC 27001:2022 Information security management systems — Requirements*. <https://www.iso.org/standard/27001>
- ISO. (2022). *ISO/IEC 27002:2022 Information security controls*. <https://www.iso.org/standard/75652.html>
- OpenSCAP Project. (2026). *OpenSCAP*. <https://www.open-scap.org/>

## 7. Anexos

- Anexo A — `oscap-reporte.html`, reporte completo del perfil CIS Level 1 Server.
- Anexo B — `PT04_matriz_control.csv`, matriz consolidada de 294 hallazgos.
- Anexo C — `sbom_juiceshop.json`, SBOM CycloneDX.
- Anexo D — `PT04_diseno_vs_eficacia.md`, análisis del control A.8.6.
- Anexo E — Capturas numeradas 01 a 06 en `docs/evidencias/S04/`.
- Anexo F — `SHA256SUMS_E04.txt` y `CADENA_DE_CUSTODIA.md`.
