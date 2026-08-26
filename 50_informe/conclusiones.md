# Conclusiones

1. La utilización de Docker Compose permitió desplegar un entorno de auditoría reproducible y controlado, facilitando que la configuración de los servicios pueda ser revisada y replicada posteriormente. Esto demuestra la importancia de mantener la infraestructura versionada para garantizar la trazabilidad de las pruebas realizadas.

2. La generación de hashes SHA-256 y el registro de los archivos en la cadena de custodia permitieron comprobar la integridad de la evidencia obtenida durante la auditoría. Al modificar deliberadamente uno de los archivos se evidenció que cualquier alteración produce un hash diferente, permitiendo detectar cambios en la evidencia original.

3. La captura de una línea base del entorno permitió registrar el estado inicial de los contenedores, imágenes, puertos, configuración y usuarios de la base de datos. Gracias a esta información fue posible identificar el hallazgo relacionado con el almacenamiento de credenciales en texto claro y contar con evidencia verificable que respalde dicho hallazgo.
