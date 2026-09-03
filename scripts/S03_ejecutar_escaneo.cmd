@echo off
setlocal

set "PROJECT_DIR=%~dp0.."
set "EVIDENCE_DIR=%PROJECT_DIR%\20_evidencia\E03_scan"

if not exist "%EVIDENCE_DIR%" mkdir "%EVIDENCE_DIR%"

docker compose -f "%PROJECT_DIR%\entorno\docker-compose.yml" up -d
if errorlevel 1 exit /b 1

docker compose -f "%PROJECT_DIR%\entorno\docker-compose.yml" ps > "%EVIDENCE_DIR%\docker_compose_ps.txt"
docker ps --format "{{.Names}}	{{.Ports}}	{{.Status}}" > "%EVIDENCE_DIR%\objetivos.txt"

docker run --rm --network si084-lab_audit_net ^
  --volume "%EVIDENCE_DIR%:/output" ^
  projectdiscovery/nuclei:latest ^
  -u http://juiceshop:3000 ^
  -u http://dvwa:80 ^
  -u http://wordpress:80 ^
  -severity low,medium,high,critical ^
  -jsonl-export /output/reporte_nuclei.jsonl

if errorlevel 1 exit /b 1

py -3.11 "%PROJECT_DIR%\scripts\S03_nuclei_a_reportes.py" ^
  "%EVIDENCE_DIR%\reporte_nuclei.jsonl" "%EVIDENCE_DIR%"

py -3.11 "%PROJECT_DIR%\30_papeles_trabajo\PT03_tecnico_a_riesgo.py" ^
  "%EVIDENCE_DIR%\reporte_nuclei.csv" ^
  "%PROJECT_DIR%\40_hallazgos\PT03_registro_riesgos.csv"

echo.
echo Escaneo terminado. Revise %EVIDENCE_DIR% y el registro de riesgos.
endlocal
