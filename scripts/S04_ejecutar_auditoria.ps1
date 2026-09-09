[CmdletBinding()]
param(
    [switch]$OmitirLynis,
    [switch]$OmitirOpenScap,
    [switch]$OmitirDockerBench,
    [switch]$OmitirTrivy
)

$ErrorActionPreference = 'Stop'
$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$EvidenceDir = Join-Path $ProjectDir '20_evidencia\E04_config'
$OutputDir = Join-Path $ProjectDir 'docs\evidencias\S04\salidas'
$MatrixScript = Join-Path $ProjectDir '30_papeles_trabajo\PT04_matriz_control.py'
$MatrixCsv = Join-Path $ProjectDir '40_hallazgos\PT04_matriz_control.csv'
$HashFile = Join-Path $ProjectDir '20_evidencia\SHA256SUMS_E04.txt'

New-Item -ItemType Directory -Force -Path $EvidenceDir, $OutputDir | Out-Null

function Invoke-DockerLogged {
    param(
        [Parameter(Mandatory)] [string]$Log,
        [Parameter(Mandatory)] [string[]]$Arguments,
        [switch]$AllowFailure
    )

    & docker @Arguments 2>&1 | Tee-Object -FilePath $Log
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0 -and -not $AllowFailure) {
        throw "Docker finalizo con codigo $exitCode. Revise: $Log"
    }
}

Write-Host '== Verificando Docker Desktop =='
docker version | Tee-Object -FilePath (Join-Path $OutputDir '00_versiones_docker.txt')
if ($LASTEXITCODE -ne 0) {
    throw 'Docker Desktop no esta accesible. Inicie Docker Desktop y vuelva a ejecutar.'
}

docker compose -f (Join-Path $ProjectDir 'entorno\docker-compose.yml') up -d
if ($LASTEXITCODE -ne 0) { throw 'No se pudo iniciar si084-lab.' }
docker compose -f (Join-Path $ProjectDir 'entorno\docker-compose.yml') ps |
    Set-Content -Encoding utf8 (Join-Path $OutputDir '01_docker_compose_ps.txt')

if (-not $OmitirLynis) {
    Write-Host '== Paso A: Lynis =='
    $lynisLog = Join-Path $EvidenceDir 'lynis-consola.txt'
    if ((Test-Path $lynisLog) -and (Select-String -LiteralPath $lynisLog -SimpleMatch 'cisofy/lynis' -Quiet)) {
        Move-Item -LiteralPath $lynisLog `
            -Destination (Join-Path $EvidenceDir 'lynis-intento-imagen-guia-error.txt') -Force
    }

    # La imagen citada en la guia (cisofy/lynis:latest) no esta publicada en
    # Docker Hub. Se construye la alternativa mantenida por CISOfy desde su
    # repositorio oficial https://github.com/CISOfy/lynis-docker.
    $lynisImage = 'si084/lynis:official'
    & docker image inspect $lynisImage *> $null
    if ($LASTEXITCODE -ne 0) {
        $buildArgs = @(
            'build', '--pull', '--tag', $lynisImage,
            'https://github.com/CISOfy/lynis-docker.git#master'
        )
        Invoke-DockerLogged -Log (Join-Path $EvidenceDir 'lynis-build.txt') -Arguments $buildArgs
    }

    $lynisCommand = @'
cd /root/lynis &&
./lynis audit system --forensics --root-dir /rootfs --quick --nocolors \
  --report-file /salida/lynis-report.dat \
  --log-file /salida/lynis.log
'@
    $args = @(
        'run', '--rm', '--pid', 'host', '--net', 'host',
        '--volume', '/:/rootfs:ro',
        '--volume', "${EvidenceDir}:/salida",
        $lynisImage, 'bash', '-lc', $lynisCommand
    )
    Invoke-DockerLogged -Log $lynisLog -Arguments $args
}

if (-not $OmitirOpenScap) {
    Write-Host '== Paso B: OpenSCAP =='
    $openScapCommand = @'
set -e
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq libopenscap8 ca-certificates curl unzip >/dev/null
curl --fail --location --silent --show-error \
  --output /tmp/scap-security-guide.zip \
  https://github.com/ComplianceAsCode/content/releases/download/v0.1.77/scap-security-guide-0.1.77.zip
mkdir -p /tmp/ssg
unzip -q /tmp/scap-security-guide.zip -d /tmp/ssg
DATASTREAM=$(find /tmp/ssg -name ssg-ubuntu2204-ds.xml -type f | head -1)
test -n "$DATASTREAM"
oscap --version > /salida/oscap-version.txt
oscap info "$DATASTREAM" > /salida/oscap-perfiles.txt
set +e
oscap xccdf eval \
  --profile xccdf_org.ssgproject.content_profile_cis_level1_server \
  --results /salida/oscap-resultados.xml \
  --report /salida/oscap-reporte.html \
  "$DATASTREAM"
rc=$?
echo "oscap_exit_code=$rc"
exit 0
'@
    $args = @(
        'run', '--rm',
        '--volume', "${EvidenceDir}:/salida",
        'ubuntu:22.04', 'bash', '-lc', $openScapCommand
    )
    Invoke-DockerLogged -Log (Join-Path $EvidenceDir 'oscap-consola.txt') -Arguments $args -AllowFailure
}

if (-not $OmitirDockerBench) {
    Write-Host '== Paso C: Docker Bench for Security =='
    $args = @(
        'run', '--rm', '--net', 'host', '--pid', 'host', '--userns', 'host',
        '--cap-add', 'audit_control',
        '--volume', '/etc:/etc:ro',
        '--volume', '/var/lib:/var/lib:ro',
        '--volume', '/var/run/docker.sock:/var/run/docker.sock:ro',
        '--volume', '/usr/lib/systemd:/usr/lib/systemd:ro',
        '--volume', '/etc/systemd:/etc/systemd:ro',
        '--label', 'docker_bench_security',
        'docker/docker-bench-security:latest'
    )
    Invoke-DockerLogged -Log (Join-Path $EvidenceDir 'docker-bench.log') -Arguments $args -AllowFailure
}

if (-not $OmitirTrivy) {
    Write-Host '== Paso D: Trivy =='
    $images = @(
        'bkimminich/juice-shop:latest',
        'postgres:16',
        'wordpress:latest',
        'mariadb:11'
    )

    $summary = Join-Path $EvidenceDir 'trivy_resumen.txt'
    if (Test-Path $summary) { Remove-Item -LiteralPath $summary }

    foreach ($imageName in $images) {
        $safeName = $imageName -replace '[/\:]', '_'
        $common = @(
            'run', '--rm',
            '--volume', '/var/run/docker.sock:/var/run/docker.sock',
            '--volume', 'si084-trivy-cache:/root/.cache/',
            '--volume', "${EvidenceDir}:/out",
            'aquasec/trivy:latest', 'image',
            '--severity', 'HIGH,CRITICAL', '--ignore-unfixed'
        )
        Invoke-DockerLogged -Log (Join-Path $OutputDir "trivy_${safeName}_json.log") `
            -Arguments ($common + @('--format', 'json', '--output', "/out/trivy_${safeName}.json", $imageName))
        $tableArgs = $common + @('--format', 'table', $imageName)
        & docker @tableArgs 2>&1 |
            Tee-Object -FilePath $summary -Append
        if ($LASTEXITCODE -ne 0) { throw "Trivy fallo al revisar $imageName" }
    }

    $trivyBase = @(
        'run', '--rm',
        '--volume', 'si084-trivy-cache:/root/.cache/',
        '--volume', "${ProjectDir}:/workspace:ro",
        '--volume', "${EvidenceDir}:/out",
        'aquasec/trivy:latest'
    )

    Invoke-DockerLogged -Log (Join-Path $OutputDir 'trivy_iac_json.log') `
        -Arguments ($trivyBase + @('config', '--severity', 'HIGH,CRITICAL', '--format', 'json',
            '--output', '/out/trivy_iac.json', '/workspace/entorno'))
    $iacTableArgs = $trivyBase + @('config', '--severity', 'HIGH,CRITICAL', '--format', 'table', '/workspace/entorno')
    & docker @iacTableArgs 2>&1 |
        Set-Content -Encoding utf8 (Join-Path $EvidenceDir 'trivy_iac.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Trivy config fallo.' }

    Invoke-DockerLogged -Log (Join-Path $OutputDir 'trivy_secretos_json.log') `
        -Arguments ($trivyBase + @('fs', '--scanners', 'secret', '--format', 'json',
            '--output', '/out/trivy_secretos.json', '--skip-dirs', '/workspace/.git',
            '--skip-dirs', '/workspace/20_evidencia', '/workspace'))
    $secretTableArgs = $trivyBase + @('fs', '--scanners', 'secret', '--format', 'table',
        '--skip-dirs', '/workspace/.git', '--skip-dirs', '/workspace/20_evidencia', '/workspace')
    & docker @secretTableArgs 2>&1 |
        Set-Content -Encoding utf8 (Join-Path $EvidenceDir 'trivy_secretos.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Trivy secret fallo.' }

    Invoke-DockerLogged -Log (Join-Path $OutputDir 'trivy_sbom.log') `
        -Arguments ($trivyBase + @('image', '--format', 'cyclonedx', '--output',
            '/out/sbom_juiceshop.json', 'bkimminich/juice-shop:latest'))
}

Write-Host '== Paso E/F: Consolidacion y validacion =='
py -3.11 $MatrixScript
if ($LASTEXITCODE -notin @(0, 2)) { throw 'No se pudo generar la matriz PT04.' }
if ($LASTEXITCODE -eq 2) {
    Write-Warning 'La matriz fue creada, pero requiere clasificacion manual para bajar de 20%.'
}

$hashTargets = @(
    Get-ChildItem -LiteralPath $EvidenceDir -File
    Get-Item -LiteralPath $MatrixCsv
)
$hashLines = foreach ($item in $hashTargets | Sort-Object FullName) {
    $relative = [IO.Path]::GetRelativePath($ProjectDir, $item.FullName).Replace('\', '/')
    $hash = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    "$hash  $relative"
}
$hashLines | Set-Content -Encoding utf8 $HashFile

Write-Host ''
Write-Host 'Auditoria automatizada terminada.' -ForegroundColor Green
Write-Host "Evidencia: $EvidenceDir"
Write-Host "Matriz:    $MatrixCsv"
Write-Host "Hashes:    $HashFile"
Write-Host 'IMPORTANTE: revise y redacte cualquier secreto real antes de hacer commit.' -ForegroundColor Yellow
