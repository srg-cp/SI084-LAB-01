"""Consolida evidencia de Lynis, OpenSCAP, Docker Bench y Trivy para el PT04."""

from __future__ import annotations

import csv
import glob
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
EVIDENCE = PROJECT / "20_evidencia" / "E04_config"
OUTPUT = PROJECT / "40_hallazgos" / "PT04_matriz_control.csv"

FIELDS = [
    "id",
    "herramienta",
    "severidad",
    "identificador_tecnico",
    "hallazgo",
    "control_iso27001",
    "objetivo_cobit",
    "tipo_deficiencia",
    "evidencia",
    "estado_revision",
]

MAPPING = [
    (r"NSWG-ECO-", "A.8.8 Management of technical vulnerabilities", "DSS05.07"),
    (r"private-key|asymmetric private key", "A.8.24 Use of cryptography", "DSS05.03"),
    (r"ACCT-9622|ACCT-9626|process accounting|sysstat", "A.8.16 Monitoring activities", "DSS01.03"),
    (r"FINT-4350|file integrity", "A.8.16 Monitoring activities", "DSS05.07"),
    (r"KRNL-5820|KRNL-6000|core.?dump|sysctl", "A.8.9 Configuration management", "BAI10.02"),
    (r"NETW-3200|protocol '(dccp|rds|sctp|tipc)'", "A.8.20 Networks security", "DSS05.02"),
    (r"PKGS-7370|PKGS-7420|debsums|apply upgrades", "A.8.8 Management of technical vulnerabilities", "DSS05.07"),
    (r"STRG-1846|USB-1000|firewire storage|USB storage", "A.7.10 Storage media", "DSS05.03"),
    (r"TOOL-5002|automation tools", "A.8.9 Configuration management", "BAI10.02"),
    (r"account_disable_post_pw_expiration", "A.5.18 Access rights", "DSS05.04"),
    (r"pam_wheel|wheel_group", "A.8.2 Privileged access rights", "DSS05.04"),
    (r"pam_pwquality", "A.5.17 Authentication information", "DSS05.04"),
    (r"accounts?_(maximum|minimum)_age|password age", "A.5.17 Authentication information", "DSS05.04"),
    (r"\bumask\b|accounts_umask", "A.8.9 Configuration management", "BAI10.02"),
    (r"root|privileg|capabilit|setuid|sudo|user namespace|userns", "A.8.2 Privileged access rights", "DSS05.04"),
    (r"password|credential|secret|authentication|passwd|shadow", "A.5.17 Authentication information", "DSS05.04"),
    (r"CVE-|vulnerab|outdated|security update|patch|package manager", "A.8.8 Management of technical vulnerabilities", "DSS05.07"),
    (r"\blog(?:ging)?\b|audit|journal|rsyslog|syslog", "A.8.15 Logging", "DSS01.03"),
    (r"tls|ssl|cipher|encrypt|certificate|crypto", "A.8.24 Use of cryptography", "DSS05.03"),
    (r"firewall|port|network|expose|forward|iptables|nftables", "A.8.20 Networks security", "DSS05.02"),
    (r"backup|restore|recovery", "A.8.13 Information backup", "DSS04.07"),
    (r"malware|antivirus", "A.8.7 Protection against malware", "DSS05.01"),
    (r"time sync|ntp|chrony|timesync", "A.8.17 Clock synchronization", "DSS01.03"),
    (r"docker socket|/var/run/docker.sock", "A.8.2 Privileged access rights", "DSS05.04"),
    (r"healthcheck|resource limit|memory limit|cpu limit|restart policy", "A.8.6 Capacity management", "BAI04.01"),
    (r"permission|ownership|mount|partition|filesystem|file system", "A.8.9 Configuration management", "BAI10.02"),
    (r"config|default|hardening|daemon|service|kernel|docker", "A.8.9 Configuration management", "BAI10.02"),
]


def clean(value: object, limit: int = 500) -> str:
    text = re.sub(r"\x1b\[[0-9;]*m", "", str(value or ""))
    return re.sub(r"\s+", " ", text).strip()[:limit]


def map_control(text: str) -> tuple[str, str]:
    for pattern, iso, cobit in MAPPING:
        if re.search(pattern, text, re.IGNORECASE):
            return iso, cobit
    return "Sin clasificar", "Sin clasificar"


def add_row(rows: list[dict[str, str]], *, tool: str, severity: str,
            technical_id: str, finding: str, evidence: str) -> None:
    finding = clean(finding)
    iso, cobit = map_control(f"{technical_id} {finding}")
    rows.append(
        {
            "id": "",
            "herramienta": tool,
            "severidad": clean(severity).capitalize() or "Informativa",
            "identificador_tecnico": clean(technical_id, 250),
            "hallazgo": finding,
            "control_iso27001": iso,
            "objetivo_cobit": cobit,
            "tipo_deficiencia": (
                "Diseño"
                if tool == "Docker Bench" and re.search(
                    r"CIS Docker 5\.(10|11|26|28)$", technical_id
                )
                else "No seleccionado; ver PT04_diseno_vs_eficacia.md"
            ),
            "evidencia": evidence,
            "estado_revision": (
                "Revisado contra criterio PT04"
                if iso != "Sin clasificar"
                else "Requiere revision manual"
            ),
        }
    )


def parse_lynis(rows: list[dict[str, str]]) -> None:
    path = EVIDENCE / "lynis-report.dat"
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"^(warning|suggestion)\[\]=(.*)$", raw)
        if not match:
            continue
        kind, detail = match.groups()
        parts = detail.split("|")
        technical_id = parts[0] if parts and re.match(r"^[A-Z]+-\d+", parts[0]) else kind
        add_row(
            rows,
            tool="Lynis",
            severity="Alta" if kind == "warning" else "Media",
            technical_id=technical_id,
            finding=detail.replace("|", " · "),
            evidence="20_evidencia/E04_config/lynis-report.dat",
        )


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_openscap(rows: list[dict[str, str]]) -> None:
    path = EVIDENCE / "oscap-resultados.xml"
    if not path.exists():
        return
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        print(f"ADVERTENCIA: XML OpenSCAP invalido: {exc}", file=sys.stderr)
        return
    for node in root.iter():
        if local_name(node.tag) != "rule-result":
            continue
        result = next((clean(c.text) for c in node if local_name(c.tag) == "result"), "")
        if result.lower() not in {"fail", "error", "unknown"}:
            continue
        identifier = node.attrib.get("idref", "Regla XCCDF sin ID")
        severity = node.attrib.get("severity", "unknown")
        add_row(
            rows,
            tool="OpenSCAP",
            severity={"high": "Alta", "medium": "Media", "low": "Baja"}.get(severity.lower(), severity),
            technical_id=identifier,
            finding=f"Regla XCCDF con resultado {result}: {identifier}",
            evidence="20_evidencia/E04_config/oscap-resultados.xml",
        )


def parse_docker_bench(rows: list[dict[str, str]]) -> None:
    path = EVIDENCE / "docker-bench.log"
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = clean(raw)
        match = re.search(r"\[WARN\]\s*(.*)", line)
        if not match:
            continue
        finding = match.group(1)
        id_match = re.match(r"(\d+(?:\.\d+)+)\s*-?\s*(.*)", finding)
        technical_id = f"CIS Docker {id_match.group(1)}" if id_match else "CIS Docker"
        add_row(
            rows,
            tool="Docker Bench",
            severity="Alta",
            technical_id=technical_id,
            finding=finding,
            evidence="20_evidencia/E04_config/docker-bench.log",
        )


def parse_trivy(rows: list[dict[str, str]]) -> None:
    for file_name in sorted(glob.glob(str(EVIDENCE / "trivy_*.json"))):
        path = Path(file_name)
        if path.name == "trivy_secretos.json":
            # No se copia el valor detectado; solo regla, archivo y categoria.
            secret_mode = True
        else:
            secret_mode = False
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"ADVERTENCIA: no se pudo leer {path.name}: {exc}", file=sys.stderr)
            continue
        for result in data.get("Results") or []:
            target = clean(result.get("Target"), 200)
            for vuln in result.get("Vulnerabilities") or []:
                vuln_id = clean(vuln.get("VulnerabilityID"), 100)
                package = clean(vuln.get("PkgName"), 120)
                installed = clean(vuln.get("InstalledVersion"), 120)
                add_row(
                    rows,
                    tool="Trivy",
                    severity=vuln.get("Severity", "unknown"),
                    technical_id=vuln_id,
                    finding=f"{vuln_id} en {package} {installed} · objetivo {target}",
                    evidence=f"20_evidencia/E04_config/{path.name}",
                )
            for misconfig in result.get("Misconfigurations") or []:
                check_id = clean(misconfig.get("ID") or misconfig.get("AVDID"), 100)
                title = clean(misconfig.get("Title") or misconfig.get("Message"))
                add_row(
                    rows,
                    tool="Trivy IaC",
                    severity=misconfig.get("Severity", "unknown"),
                    technical_id=check_id,
                    finding=f"{title} · objetivo {target}",
                    evidence=f"20_evidencia/E04_config/{path.name}",
                )
            for secret in result.get("Secrets") or []:
                rule_id = clean(secret.get("RuleID") or secret.get("Category"), 100)
                title = clean(secret.get("Title") or secret.get("Category") or "Posible secreto")
                add_row(
                    rows,
                    tool="Trivy Secret",
                    severity=secret.get("Severity", "high"),
                    technical_id=rule_id,
                    finding=f"{title} en {target} (valor omitido)",
                    evidence=f"20_evidencia/E04_config/{path.name}",
                )
        if secret_mode:
            print("AVISO: revise trivy_secretos.json antes de versionarlo; puede contener datos sensibles.")


def main() -> int:
    rows: list[dict[str, str]] = []
    parse_lynis(rows)
    parse_openscap(rows)
    parse_docker_bench(rows)
    parse_trivy(rows)

    if not rows:
        print(f"ERROR: no hay reportes analizables en {EVIDENCE}", file=sys.stderr)
        return 1

    order = {"Critica": 0, "Critical": 0, "Alta": 1, "High": 1, "Media": 2, "Medium": 2, "Baja": 3, "Low": 3}
    rows.sort(key=lambda r: (order.get(r["severidad"], 9), r["herramienta"], r["hallazgo"]))
    for number, row in enumerate(rows, 1):
        row["id"] = f"S04-{number:04d}"

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    unclassified = sum(row["control_iso27001"] == "Sin clasificar" for row in rows)
    percent = unclassified / len(rows)
    print(f"Matriz generada: {OUTPUT}")
    print(f"Hallazgos totales: {len(rows)}")
    for tool in sorted({row["herramienta"] for row in rows}):
        print(f"  {tool}: {sum(row['herramienta'] == tool for row in rows)}")
    print(f"Sin clasificar: {unclassified} ({percent:.1%})")
    if percent >= 0.20:
        print("VALIDACION PENDIENTE: se requiere clasificacion manual para quedar por debajo de 20%.")
        return 2
    print("VALIDACION OK: porcentaje sin clasificar menor a 20%.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
