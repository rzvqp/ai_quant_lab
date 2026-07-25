"""Verificarea integrității surselor (F4, E4). Fail-closed pe orice nepotrivire.

Recalculează SHA-256 al fișierului întreg și îl compară cu hash-ul declarat în
specificație ȘI cu cel înregistrat în registru. Citirea octeților pentru hash este
o operație de integritate — niciun rând sigilat nu e parsat ca dată aici.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from ..spec import registry_validator


class DataIntegrityError(RuntimeError):
    """Nepotrivire de hash, sursă inexistentă sau fișier absent."""


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_and_verify(source_id: str, declared_sha256: str) -> tuple[Path, str]:
    """Localizează sursa, verifică hash-ul vs. declarat + registru. Întoarce (cale, hash)."""
    reg = registry_validator.load_registry()
    src = reg["data_sources"].get(source_id)
    if src is None:
        raise DataIntegrityError(f"sursa '{source_id}' nu există în registru")

    root = registry_validator.load_registry  # placeholder to avoid unused import warning
    from .. import paths as _paths
    path = _paths.LAB_ROOT / src["path"]
    if not path.exists():
        raise DataIntegrityError(f"fișierul sursei '{source_id}' nu există: {path}")

    actual = _sha256(path)
    if actual != declared_sha256:
        raise DataIntegrityError(
            f"hash-ul declarat pentru '{source_id}' nu corespunde fișierului "
            f"(declarat {declared_sha256[:12]}…, real {actual[:12]}…)"
        )
    if actual != src["sha256"]:
        raise DataIntegrityError(
            f"hash-ul fișierului '{source_id}' nu corespunde celui înregistrat în registru"
        )
    return path, actual
