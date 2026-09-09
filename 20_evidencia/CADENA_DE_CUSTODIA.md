# Cadena de custodia de la evidencia

| ID     | Archivo               | SHA-256                                                          | Fecha y hora (UTC)   | Obtenido por       | Método de obtención                                       | Sistema origen               |
| ------ | --------------------- | ---------------------------------------------------------------- | -------------------- | ------------------ | --------------------------------------------------------- | ---------------------------- |
| E01-01 | contenedores.json     | 078F1E729D38F7C67160019DCDEE83DFB582182E2FC4093D2B1C0C0D10466DE8 | 2026-08-26 21:20 UTC | srg-cp 			| `docker compose ps --format json`                         | Docker Desktop / Windows 11  |
| E01-02 | imagenes.tsv          | 88CBDA0440DD3AF795825FD8586F08DED1956E0A8D17E207661C2FBC1A17CB3B | 2026-08-26 21:20 UTC | srg-cp 			| `docker images --digests`                                 | Docker Desktop / Windows 11  |
| E01-03 | puertos.tsv           | 2065B1AA54E1DF243EEC48FE02EED36CCA69BA43E055DA036D40DF0EBB4A3323 | 2026-08-26 21:20 UTC | srg-cp 			| `docker ps --format`                                      | Docker Desktop / Windows 11  |
| E01-04 | compose_efectivo.yml  | DD8FA9584CDC592B409D86610E03460CBD69CB200CC13D5EFCD6E83A0D778C35 | 2026-08-26 21:20 UTC | srg-cp 			| `docker compose config`                                   | Docker Compose / Windows 11  |
| E01-05 | usuarios_postgres.txt | AF32B889FBAE13A312669FFA58B8881B9D6FE3176903E7FF2F8D5EEDBEFF5E02 | 2026-08-26 21:20 UTC | srg-cp 			| `docker exec si084_db psql -U erp_app -d erp -c "\du"`    | PostgreSQL 16 / Docker       |
| E01-06 | env_db.json           | 1F221C0EDD57BC23EAD3800F00170872D0B9F0D7AB4E32DC0904FD6EE3CB865F | 2026-08-26 21:20 UTC | srg-cp 			| `docker inspect si084_db --format '{{json .Config.Env}}'` | Contenedor si084_db / Docker |
| E04-01 | E04_config/lynis-report.dat | B7CEE97752E0BF5889FB409A1D242330D1B7F04CA1DABE4DCD140133B2C22404 | 2026-09-09 21:30 UTC | srg-cp | Lynis `audit system --forensics` sobre montaje de solo lectura | Lynis / Docker Desktop |
| E04-02 | E04_config/oscap-resultados.xml | 5595D0E1EACC37D50D22CEC59FCC6A134243F28913F78CCD37114A236ECF57AC | 2026-09-09 21:37 UTC | srg-cp | `oscap xccdf eval` con perfil CIS Level 1 Server | OpenSCAP / Ubuntu 22.04 |
| E04-03 | E04_config/oscap-reporte.html | BF1F5FCFD355EC5138769A59EF4C22907C93436C529C6410F014B28C48486D8F | 2026-09-09 21:37 UTC | srg-cp | Reporte HTML generado por `oscap xccdf eval` | OpenSCAP / Ubuntu 22.04 |
| E04-04 | E04_config/docker-bench.log | 564C858E5D8C4EF264DDEE191B1C59A02F388BF012284626119227C2611C9506 | 2026-09-09 21:29 UTC | srg-cp | Docker Bench for Security con acceso de lectura al host Docker | Docker Desktop / Windows 11 |
| E04-05 | E04_config/trivy_bkimminich_juice-shop_latest.json | 3BBC34E86AF0B091F7B31A1AE694628918C8F88CA84229C03366DBBF632259D4 | 2026-09-09 21:32 UTC | srg-cp | `trivy image --severity HIGH,CRITICAL --format json` | Trivy / Docker Desktop |
| E04-06 | E04_config/trivy_iac.json | F67BF99B27B54FEE920B544319C66F5B3ED0B27CB52A13186A577322AA96980F | 2026-09-09 21:33 UTC | srg-cp | `trivy config --severity HIGH,CRITICAL --format json` | Trivy / repositorio local |
| E04-07 | E04_config/trivy_secretos.json | 81DD515D41036EB0A45C70A3D6831E9B5C3CC06C392833E884A458ED3F053549 | 2026-09-09 21:33 UTC | srg-cp | `trivy fs --scanners secret`; versión publicable saneada | Trivy / repositorio local |
| E04-08 | E04_config/sbom_juiceshop.json | 050CACC26A31A96F66E7CE43922B741E75FE91F728FC10B69A52A78CF642E919 | 2026-09-09 21:33 UTC | srg-cp | `trivy image --format cyclonedx` | Trivy / Docker Desktop |
| E04-09 | PT04_matriz_control.csv | CCEAC3DFFB2FA80C7594CD3715FB1988DC6ABE3EAE81DBE95F5BA94C5A875337 | 2026-09-09 22:28 UTC | srg-cp | Consolidación y revisión con `PT04_matriz_control.py` | Evidencias E04 / Python 3.11 |

> Los hashes E04 corresponden a las copias publicables después del saneamiento. Los originales confidenciales se conservaron fuera de Git en `.private/S04_originales/`, con un manifiesto independiente en `.private/SHA256SUMS_S04_ORIGINALES.txt`.
