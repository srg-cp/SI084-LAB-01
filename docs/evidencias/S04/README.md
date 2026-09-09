# Evidencias · Taller 04

Esta carpeta contiene el índice versionable de evidencias del Taller 04. Los reportes técnicos completos se conservan en `20_evidencia/E04_config/` y se tratan como **Confidenciales** hasta revisar que no expongan secretos ni información sensible del anfitrión.

## Resultados esperados

| # | Resultado | Artefacto | Estado |
|---|---|---|---|
| 1 | Lynis, índice de endurecimiento y tres observaciones priorizadas | [`lynis-report.dat`](../../../20_evidencia/E04_config/lynis-report.dat) | Logrado: índice 53; el escaneo produjo sugerencias, no advertencias formales |
| 2 | OpenSCAP y reglas XCCDF fallidas | [`oscap-resultados.xml`](../../../20_evidencia/E04_config/oscap-resultados.xml) y [`oscap-reporte.html`](../../../20_evidencia/E04_config/oscap-reporte.html) | Logrado con limitación: 15 fallos medios y ningún fallo alto |
| 3 | Docker Bench, conteo de WARN y secciones 4 y 5 | [`docker-bench.log`](../../../20_evidencia/E04_config/docker-bench.log) | Logrado: 105 advertencias consolidadas |
| 4 | Trivy: imágenes, IaC, secretos y SBOM CycloneDX | [`E04_config`](../../../20_evidencia/E04_config/) | Logrado: 141 vulnerabilidades y 5 detecciones de secretos con valores redactados |
| 5 | Matriz única ISO/IEC 27001 y COBIT 2019 | [`PT04_matriz_control.csv`](../../../40_hallazgos/PT04_matriz_control.csv) | Logrado: 294 registros |
| 6 | Menos de 20 % sin clasificar | [`06_matriz_validacion.png`](06_matriz_validacion.png) | Logrado: 0 de 294 (0,0 %); la captura debe actualizarse tras la última ejecución |
| 7 | Diseño frente a eficacia operativa | [`PT04_diseno_vs_eficacia.md`](../../../30_papeles_trabajo/PT04_diseno_vs_eficacia.md) | Logrado: A.8.6 clasificado como deficiencia de diseño |
| 8 | Integridad SHA-256 | [`SHA256SUMS_E04.txt`](../../../20_evidencia/SHA256SUMS_E04.txt) | Logrado: 22 artefactos verificados |

## Capturas numeradas

1. [`01_entorno_docker_operativo.png`](01_entorno_docker_operativo.png)
2. [`02_lynis_indice_y_sugerencias.png`](02_lynis_indice_y_sugerencias.png)
3. [`03_openscap_reglas_fallidas.png`](03_openscap_reglas_fallidas.png)
4. [`04_docker_bench_advertencias.png`](04_docker_bench_advertencias.png)
5. [`05_trivy_resumen.png`](05_trivy_resumen.png)
6. [`06_matriz_validacion.png`](06_matriz_validacion.png)

## Ejecución

Desde PowerShell, en la raíz de `auditoria-si084`:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\S04_ejecutar_auditoria.ps1
```

La imagen `cisofy/lynis:latest` citada por la guía no se encuentra publicada en Docker Hub. El ejecutor construye `si084/lynis:official` desde `CISOfy/lynis-docker`, repositorio oficial del proyecto, y conserva el intento fallido en `lynis-intento-imagen-guia-error.txt` como parte de «Problemas y mejoras».

Ubuntu 22.04 tampoco distribuye `ssg-debderived` en sus repositorios. Para mantener el perfil exigido, el ejecutor instala OpenSCAP y descarga el *data stream* precompilado de Ubuntu 22.04 desde la versión 0.1.77 publicada por `ComplianceAsCode/content`.

Los reportes publicables fueron saneados con `scripts/S04_preparar_publicacion.py`. Las copias originales se conservan en `.private/S04_originales/`, fuera de Git. Si se repite el laboratorio, se debe volver a revisar `trivy_secretos.json` antes del siguiente `commit` o `push`.
