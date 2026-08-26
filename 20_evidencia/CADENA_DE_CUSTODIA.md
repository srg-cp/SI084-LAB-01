# Cadena de custodia de la evidencia

| ID     | Archivo               | SHA-256                                                          | Fecha y hora (UTC)   | Obtenido por       | Método de obtención                                       | Sistema origen               |
| ------ | --------------------- | ---------------------------------------------------------------- | -------------------- | ------------------ | --------------------------------------------------------- | ---------------------------- |
| E01-01 | contenedores.json     | 078F1E729D38F7C67160019DCDEE83DFB582182E2FC4093D2B1C0C0D10466DE8 | 2026-08-26 21:20 UTC | srg-cp 			| `docker compose ps --format json`                         | Docker Desktop / Windows 11  |
| E01-02 | imagenes.tsv          | 88CBDA0440DD3AF795825FD8586F08DED1956E0A8D17E207661C2FBC1A17CB3B | 2026-08-26 21:20 UTC | srg-cp 			| `docker images --digests`                                 | Docker Desktop / Windows 11  |
| E01-03 | puertos.tsv           | 2065B1AA54E1DF243EEC48FE02EED36CCA69BA43E055DA036D40DF0EBB4A3323 | 2026-08-26 21:20 UTC | srg-cp 			| `docker ps --format`                                      | Docker Desktop / Windows 11  |
| E01-04 | compose_efectivo.yml  | DD8FA9584CDC592B409D86610E03460CBD69CB200CC13D5EFCD6E83A0D778C35 | 2026-08-26 21:20 UTC | srg-cp 			| `docker compose config`                                   | Docker Compose / Windows 11  |
| E01-05 | usuarios_postgres.txt | AF32B889FBAE13A312669FFA58B8881B9D6FE3176903E7FF2F8D5EEDBEFF5E02 | 2026-08-26 21:20 UTC | srg-cp 			| `docker exec si084_db psql -U erp_app -d erp -c "\du"`    | PostgreSQL 16 / Docker       |
| E01-06 | env_db.json           | 1F221C0EDD57BC23EAD3800F00170872D0B9F0D7AB4E32DC0904FD6EE3CB865F | 2026-08-26 21:20 UTC | srg-cp 			| `docker inspect si084_db --format '{{json .Config.Env}}'` | Contenedor si084_db / Docker |
