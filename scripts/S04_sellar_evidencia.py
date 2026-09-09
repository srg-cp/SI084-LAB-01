"""Genera o verifica el manifiesto SHA-256 de la evidencia publicable S04."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
EVIDENCE = PROJECT / "20_evidencia" / "E04_config"
MATRIX = PROJECT / "40_hallazgos" / "PT04_matriz_control.csv"
MANIFEST = PROJECT / "20_evidencia" / "SHA256SUMS_E04.txt"


def digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def targets() -> list[Path]:
    files = sorted(path for path in EVIDENCE.iterdir() if path.is_file())
    if MATRIX.exists():
        files.append(MATRIX)
    return files


def generate() -> int:
    files = targets()
    if not files:
        print("ERROR: no se encontraron evidencias para sellar.")
        return 1
    lines = [f"{digest(path)}  {path.relative_to(PROJECT).as_posix()}" for path in files]
    MANIFEST.write_text("\n".join(sorted(lines)) + "\n", encoding="utf-8", newline="\n")
    print(f"HASHES_GENERADOS={len(lines)}")
    print(MANIFEST)
    return 0


def verify() -> int:
    if not MANIFEST.exists():
        print(f"ERROR: no existe {MANIFEST}")
        return 1
    failures = 0
    checked = 0
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(None, 1)
        path = PROJECT / relative.strip()
        current = digest(path) if path.exists() else "NO_EXISTE"
        status = "OK" if current == expected else "FALLO"
        print(f"{status}  {relative.strip()}")
        checked += 1
        failures += status != "OK"
    print(f"VERIFICADOS={checked}; FALLOS={failures}")
    return 1 if failures else 0


parser = argparse.ArgumentParser()
parser.add_argument("--verificar", action="store_true")
args = parser.parse_args()
raise SystemExit(verify() if args.verificar else generate())
