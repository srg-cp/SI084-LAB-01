# PT04 · Deficiencia de diseño frente a eficacia operativa

**Estado:** completado con la evidencia real obtenida el 9 de septiembre de 2026.

## Control seleccionado

- Control ISO/IEC 27001:2022: A.8.6 Gestión de la capacidad.
- Objetivo COBIT 2019: BAI04.01 — evaluar disponibilidad, desempeño y capacidad actuales.
- Evidencia técnica: reglas CIS Docker 5.10, 5.11, 5.26 y 5.28 en `docker-bench.log`, contrastadas con `entorno/docker-compose.yml`.

## Análisis en el plano de diseño

Existe una **deficiencia de diseño** cuando la organización no ha definido el control, su responsable, su frecuencia, el criterio de aceptación o la evidencia que debe conservarse. En ese caso, aunque una persona aplique endurecimiento de manera ocasional, no existe un control reproducible ni supervisable.

**Evaluación del caso:** Docker Bench informó que los siete contenedores del laboratorio operaban sin límites de memoria (regla 5.10), sin prioridad o límite de CPU (5.11) y sin límite de procesos (5.28). Seis de los siete tampoco tenían comprobación de salud en tiempo de ejecución (5.26). La revisión del archivo `entorno/docker-compose.yml` confirmó que no se declararon `mem_limit`, `cpus`, `pids_limit`, `healthcheck` ni restricciones equivalentes. El control, por tanto, no está diseñado en la infraestructura como código; no se trata solo de una ejecución fallida.

## Análisis en el plano de eficacia operativa

Existe una **deficiencia de eficacia operativa** cuando el control sí está diseñado y documentado, pero la evidencia demuestra que no se ejecutó, se ejecutó fuera de plazo o no produjo el resultado esperado.

**Contraste con el caso:** habría una deficiencia de eficacia operativa si Docker Compose declarara límites y comprobaciones de salud, pero `docker inspect` demostrara que no fueron aplicados a los contenedores en ejecución. Esa condición no se observó: la ausencia está tanto en el diseño versionado como en el estado operativo. Por ello, clasificarla como eficacia operativa ocultaría la causa real.

## Conclusión y recomendación

Se concluye que existe una **deficiencia de diseño** del control A.8.6. Se recomienda incorporar límites de memoria, CPU y PID y comprobaciones de salud apropiadas para cada servicio en `docker-compose.yml`; asignar como responsable a la Jefatura de Infraestructura; definir una revisión trimestral; y establecer como criterio de aceptación que ningún contenedor productivo opere con recursos ilimitados o sin una comprobación de salud documentada. Después de implementar el diseño debe repetirse Docker Bench y conservarse el log como prueba de eficacia operativa.
