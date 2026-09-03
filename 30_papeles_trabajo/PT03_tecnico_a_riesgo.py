"""Convierte los hallazgos técnicos de Nuclei en un registro de riesgos E03."""

import csv
import sys
from pathlib import Path


ACTIVOS = {
    "db": {
        "nombre": "Base de datos ERP",
        "dueno": "Gerencia de Finanzas",
        "clasificacion": "Restringida",
        "expuesto": False,
        "criticidad": 5,
    },
    "juiceshop": {
        "nombre": "Portal de clientes",
        "dueno": "Gerencia Comercial",
        "clasificacion": "Confidencial",
        "expuesto": True,
        "criticidad": 4,
    },
    "wordpress": {
        "nombre": "Portal corporativo",
        "dueno": "Gerencia Comercial",
        "clasificacion": "Pública",
        "expuesto": True,
        "criticidad": 2,
    },
    "dvwa": {
        "nombre": "Aplicación legada interna",
        "dueno": "Gerencia de Operaciones",
        "clasificacion": "Interna",
        "expuesto": False,
        "criticidad": 3,
    },
}


RIESGOS_LINEA_BASE = [
    {
        "id_riesgo": "R-004",
        "activo": "Base de datos ERP",
        "dueno_del_riesgo": "Gerencia de Finanzas",
        "clasificacion": "Restringida",
        "amenaza": "Acceso no autorizado mediante credenciales expuestas",
        "vulnerabilidad": "Credenciales débiles almacenadas en variables de entorno",
        "cve": "N/A",
        "cvss": "N/A",
        "probabilidad": 3,
        "impacto": 5,
        "riesgo_inherente": 15,
        "nivel": "Alto",
        "evidencia": "E01/env_db.json; H-001",
    },
    {
        "id_riesgo": "R-005",
        "activo": "Base de datos ERP",
        "dueno_del_riesgo": "Gerencia de Finanzas",
        "clasificacion": "Restringida",
        "amenaza": "Abuso de privilegios de la cuenta de aplicación",
        "vulnerabilidad": "La cuenta erp_app posee privilegios de superusuario, creación de roles, replicación y bypass de RLS",
        "cve": "N/A",
        "cvss": "N/A",
        "probabilidad": 3,
        "impacto": 5,
        "riesgo_inherente": 15,
        "nivel": "Alto",
        "evidencia": "E01/usuarios_postgres.txt",
    },
    {
        "id_riesgo": "R-006",
        "activo": "Base de datos del portal WordPress",
        "dueno_del_riesgo": "Gerencia Comercial",
        "clasificacion": "Confidencial",
        "amenaza": "Compromiso de la base de datos mediante credenciales predecibles",
        "vulnerabilidad": "Credenciales wp/wp y contraseña root débil definidas en Docker Compose",
        "cve": "N/A",
        "cvss": "N/A",
        "probabilidad": 4,
        "impacto": 3,
        "riesgo_inherente": 12,
        "nivel": "Alto",
        "evidencia": "E01/compose_efectivo.yml",
    },
    {
        "id_riesgo": "R-007",
        "activo": "Plataforma de contenedores",
        "dueno_del_riesgo": "Jefatura de Infraestructura",
        "clasificacion": "Interna",
        "amenaza": "Cambio no controlado o incorporación de componentes vulnerables",
        "vulnerabilidad": "Uso de imágenes con etiqueta latest sin fijar versión o digest",
        "cve": "N/A",
        "cvss": "N/A",
        "probabilidad": 3,
        "impacto": 4,
        "riesgo_inherente": 12,
        "nivel": "Alto",
        "evidencia": "E01/compose_efectivo.yml; E01/imagenes.tsv",
    },
    {
        "id_riesgo": "R-008",
        "activo": "Servicios web del laboratorio",
        "dueno_del_riesgo": "Jefatura de Infraestructura",
        "clasificacion": "Interna",
        "amenaza": "Intercepción o alteración del tráfico de aplicación",
        "vulnerabilidad": "Servicios publicados mediante HTTP sin protección TLS",
        "cve": "N/A",
        "cvss": "N/A",
        "probabilidad": 2,
        "impacto": 3,
        "riesgo_inherente": 6,
        "nivel": "Medio",
        "evidencia": "E01/puertos.tsv; PT03_soa_extracto.md",
    },
    {
        "id_riesgo": "R-009",
        "activo": "Red de contenedores audit_net",
        "dueno_del_riesgo": "Jefatura de Infraestructura",
        "clasificacion": "Interna",
        "amenaza": "Movimiento lateral desde un contenedor comprometido",
        "vulnerabilidad": "Todos los servicios comparten una única red bridge sin segmentación por función",
        "cve": "N/A",
        "cvss": "N/A",
        "probabilidad": 2,
        "impacto": 4,
        "riesgo_inherente": 8,
        "nivel": "Medio",
        "evidencia": "E01/compose_efectivo.yml",
    },
    {
        "id_riesgo": "R-010",
        "activo": "Datos persistentes de ERP y WordPress",
        "dueno_del_riesgo": "Jefatura de Infraestructura",
        "clasificacion": "Restringida",
        "amenaza": "Pérdida o corrupción de datos persistentes",
        "vulnerabilidad": "La línea base no evidencia copias de seguridad ni pruebas de restauración de los volúmenes",
        "cve": "N/A",
        "cvss": "N/A",
        "probabilidad": 2,
        "impacto": 5,
        "riesgo_inherente": 10,
        "nivel": "Medio",
        "evidencia": "E01/compose_efectivo.yml",
    },
]


def probabilidad(cvss: float, expuesto: bool) -> int:
    base = 1 if cvss < 4 else 2 if cvss < 7 else 3 if cvss < 9 else 4
    return min(5, base + (1 if expuesto else 0))


def impacto(criticidad: int, clasificacion: str) -> int:
    extra = {"Restringida": 1, "Confidencial": 0, "Interna": 0, "Pública": -1}
    return max(1, min(5, criticidad + extra.get(clasificacion, 0)))


def nivel(valor: int) -> str:
    if valor >= 20:
        return "Crítico"
    if valor >= 12:
        return "Alto"
    if valor >= 6:
        return "Medio"
    return "Bajo"


input_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])
rows = []

with input_path.open(encoding="utf-8-sig") as handle:
    for finding in csv.DictReader(handle):
        asset = ACTIVOS.get(finding["Host"].strip().lower())
        if not asset:
            continue
        score = float(finding["Severity"] or 0)
        likelihood = probabilidad(score, asset["expuesto"])
        impact = impacto(asset["criticidad"], asset["clasificacion"])
        inherent = likelihood * impact
        rows.append(
            {
                "id_riesgo": "",
                "activo": asset["nombre"],
                "dueno_del_riesgo": asset["dueno"],
                "clasificacion": asset["clasificacion"],
                "amenaza": "Explotación de vulnerabilidad conocida",
                "vulnerabilidad": finding["NVT Name"],
                "cve": finding["CVEs"],
                "cvss": score,
                "probabilidad": likelihood,
                "impacto": impact,
                "riesgo_inherente": inherent,
                "nivel": nivel(inherent),
                "evidencia": finding["Template ID"],
            }
        )

rows.sort(key=lambda row: row["riesgo_inherente"], reverse=True)
for index, row in enumerate(rows, start=1):
    row["id_riesgo"] = f"R-{index:03d}"

rows.extend(RIESGOS_LINEA_BASE)

fieldnames = [
    "id_riesgo",
    "activo",
    "dueno_del_riesgo",
    "clasificacion",
    "amenaza",
    "vulnerabilidad",
    "cve",
    "cvss",
    "probabilidad",
    "impacto",
    "riesgo_inherente",
    "nivel",
    "evidencia",
]
output_path.parent.mkdir(parents=True, exist_ok=True)
with output_path.open("w", newline="", encoding="utf-8-sig") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Registro generado: {output_path} ({len(rows)} riesgos)")
if len(rows) < 10:
    print("ADVERTENCIA: la guía exige al menos 10 riesgos; no declare el resultado como logrado.")
