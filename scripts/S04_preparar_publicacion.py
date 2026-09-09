"""Archiva originales localmente y redacta valores sensibles de la evidencia S04."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
EVIDENCE = PROJECT / "20_evidencia" / "E04_config"
PRIVATE = PROJECT / ".private" / "S04_originales"
PRIVATE_MANIFEST = PROJECT / ".private" / "SHA256SUMS_S04_ORIGINALES.txt"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def redact_secret(secret: dict) -> int:
    changes = 0
    if secret.get("Match") and secret["Match"] != "[REDACTADO]":
        secret["Match"] = "[REDACTADO]"
        changes += 1
    code = secret.get("Code")
    if isinstance(code, dict):
        for line in code.get("Lines") or []:
            if isinstance(line, dict) and line.get("Content") not in (None, "[REDACTADO]"):
                line["Content"] = "[REDACTADO]"
                changes += 1
    return changes


def redact_json(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    changes = 0
    for result in data.get("Results") or []:
        for secret in result.get("Secrets") or []:
            if isinstance(secret, dict):
                changes += redact_secret(secret)
    if changes:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return changes


def redact_text(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    original = text
    text = re.sub(
        r"uptintranetapifinal\.azurecr\.io/upt-intranet-api:[^\s\]]+",
        "[IMAGEN_PRIVADA_REDACTADA]",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"(?m)^(hostname|domain_name)=.*$", r"\1=[REDACTADO]", text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return 1
    return 0


def main() -> int:
    if not EVIDENCE.is_dir():
        raise SystemExit(f"No existe la evidencia: {EVIDENCE}")

    if not PRIVATE.exists():
        PRIVATE.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(EVIDENCE, PRIVATE)
        manifest = [
            f"{sha256(path)}  {path.relative_to(PRIVATE).as_posix()}"
            for path in sorted(PRIVATE.rglob("*"))
            if path.is_file()
        ]
        PRIVATE_MANIFEST.write_text("\n".join(manifest) + "\n", encoding="utf-8")
        print(f"Originales archivados localmente en {PRIVATE}")
    else:
        print(f"Archivo privado existente; no se sobrescribe: {PRIVATE}")

    redactions = 0
    for path in sorted(EVIDENCE.glob("trivy_*.json")):
        redactions += redact_json(path)
    for name in ("docker-bench.log", "lynis-report.dat", "lynis.log", "lynis-consola.txt"):
        path = EVIDENCE / name
        if path.exists():
            redactions += redact_text(path)

    print(f"Elementos sensibles redactados: {redactions}")
    print("Los originales permanecen fuera del control de versiones en .private/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
