"""Checksums SHA-256 peste fișierele unui bundle (arhitectură §7, §11).

Fișierul CHECKSUMS.sha256 conține câte o linie `<hex>  <cale relativă>` pentru
fiecare fișier din bundle (cu excepția lui însuși). Formatul e cel clasic
`sha256sum`, verificabil și extern.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

CHECKSUMS_NAME = "CHECKSUMS.sha256"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _iter_files(bundle_dir: Path):
    for p in sorted(bundle_dir.rglob("*")):
        if p.is_file() and p.name != CHECKSUMS_NAME:
            yield p


def write_checksums(bundle_dir: Path) -> Path:
    """Scrie CHECKSUMS.sha256 peste toate fișierele bundle-ului. Întoarce calea."""
    lines = []
    for p in _iter_files(bundle_dir):
        rel = p.relative_to(bundle_dir).as_posix()
        lines.append(f"{sha256_file(p)}  {rel}")
    target = bundle_dir / CHECKSUMS_NAME
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def bundle_sha256(bundle_dir: Path) -> str:
    """Hash agregat determinist al bundle-ului (peste manifestul de checksums)."""
    manifest = "\n".join(
        f"{sha256_file(p)}  {p.relative_to(bundle_dir).as_posix()}"
        for p in _iter_files(bundle_dir)
    )
    return hashlib.sha256(manifest.encode("utf-8")).hexdigest()


def verify_checksums(bundle_dir: Path) -> dict:
    """Re-calculează și compară cu CHECKSUMS.sha256. Întoarce un raport."""
    checkfile = bundle_dir / CHECKSUMS_NAME
    if not checkfile.exists():
        return {"status": "MISMATCH", "reason": "CHECKSUMS.sha256 absent", "mismatches": []}
    declared = {}
    for line in checkfile.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split("  ", 1)
        declared[rel] = digest

    actual = {p.relative_to(bundle_dir).as_posix(): sha256_file(p) for p in _iter_files(bundle_dir)}

    mismatches = []
    for rel, digest in declared.items():
        if rel not in actual:
            mismatches.append({"file": rel, "issue": "missing"})
        elif actual[rel] != digest:
            mismatches.append({"file": rel, "issue": "altered"})
    for rel in actual:
        if rel not in declared:
            mismatches.append({"file": rel, "issue": "unexpected"})

    return {
        "status": "EXACT" if not mismatches else "MISMATCH",
        "files_checked": len(declared),
        "mismatches": mismatches,
    }
