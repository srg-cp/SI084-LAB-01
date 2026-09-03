"""Convierte la salida JSONL de Nuclei a CSV y XML para el expediente E03."""

import csv
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse


SEVERITY_SCORE = {
    "info": 0.0,
    "unknown": 0.0,
    "low": 3.1,
    "medium": 5.5,
    "high": 8.0,
    "critical": 9.8,
}


def normalize_host(value: str) -> str:
    parsed = urlparse(value)
    return parsed.hostname or value.split(":", 1)[0]


source = Path(sys.argv[1])
output_dir = Path(sys.argv[2])
output_dir.mkdir(parents=True, exist_ok=True)

rows = []
with source.open(encoding="utf-8") as handle:
    for line in handle:
        if not line.strip():
            continue
        item = json.loads(line)
        info = item.get("info") or {}
        classification = info.get("classification") or {}
        cves = classification.get("cve-id") or classification.get("cve_id") or []
        if isinstance(cves, str):
            cves = [cves]
        severity_name = str(info.get("severity", "unknown")).lower()
        rows.append(
            {
                "Host": normalize_host(item.get("host") or item.get("matched-at", "")),
                "NVT Name": info.get("name") or item.get("template-id", "Sin nombre"),
                "CVEs": ", ".join(cves) if cves else "N/D",
                "Severity": SEVERITY_SCORE.get(severity_name, 0.0),
                "Severity label": severity_name,
                "Template ID": item.get("template-id", ""),
                "Matched at": item.get("matched-at", ""),
                "Timestamp": item.get("timestamp", ""),
                "Reference": "; ".join(info.get("reference") or []),
            }
        )

fieldnames = [
    "Host",
    "NVT Name",
    "CVEs",
    "Severity",
    "Severity label",
    "Template ID",
    "Matched at",
    "Timestamp",
    "Reference",
]

csv_path = output_dir / "reporte_nuclei.csv"
with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

xml_root = ET.Element("nuclei-report", findings=str(len(rows)))
for row in rows:
    finding = ET.SubElement(xml_root, "finding")
    for key, value in row.items():
        node = ET.SubElement(finding, key.lower().replace(" ", "-").replace("/", "-"))
        node.text = str(value)
ET.ElementTree(xml_root).write(
    output_dir / "reporte_nuclei.xml", encoding="utf-8", xml_declaration=True
)

print(f"Se convirtieron {len(rows)} hallazgos a {csv_path.name} y reporte_nuclei.xml")
