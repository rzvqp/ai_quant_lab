"""Integritatea repository-ului: nimic scris în afara directorului propriu de rulare.

Se calculează un instantaneu (hash per fișier) al arborelui `validation_engine/`,
EXCLUZÂND `runs/` (unde VE scrie legitim) și artefacte volatile. Comparând
instantaneul înainte/după o rulare, orice scriere externă devine detectabilă
(arhitectură §4.2, §11).

NU citește date de piață: `data/` este în afara arborelui scanat, iar garda de
acces (access_audit) rămâne activă. Se scanează doar .py/.json/.md/.txt.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from .. import paths

_EXCLUDE_DIRS = {"runs", "__pycache__", ".git", "clarifications"}
_INCLUDE_SUFFIXES = {".py", ".json", ".md", ".txt", ".yaml", ".yml"}
#: Artefacte append-only legitime din rădăcina VE — mutabile prin design, deci
#: excluse din instantaneul de integritate (nu sunt scrieri "externe").
_EXCLUDE_FILES = {"run_ledger.jsonl", "RUN_LEDGER.md"}


def _iter_tree(root: Path):
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if any(part in _EXCLUDE_DIRS for part in rel.parts):
            continue
        if p.name in _EXCLUDE_FILES:
            continue
        if p.suffix.lower() not in _INCLUDE_SUFFIXES:
            continue
        yield rel.as_posix(), p


def snapshot(root: Path | None = None) -> dict:
    """{cale relativă: sha256} pentru arborele VE, exceptând runs/ și volatile."""
    root = root or paths.VE_ROOT
    out = {}
    for rel, p in _iter_tree(root):
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        out[rel] = h.hexdigest()
    return out


def digest_of(snap: dict) -> str:
    """Hash agregat determinist al unui instantaneu."""
    manifest = "\n".join(f"{h}  {rel}" for rel, h in sorted(snap.items()))
    return hashlib.sha256(manifest.encode("utf-8")).hexdigest()


def compare(before: dict, after: dict) -> dict:
    """Diferența dintre două instantanee. external_writes = fișiere schimbate/adăugate/șterse."""
    changed = [rel for rel in before if rel in after and before[rel] != after[rel]]
    added = [rel for rel in after if rel not in before]
    removed = [rel for rel in before if rel not in after]
    external_writes = len(changed) + len(added) + len(removed)
    return {
        "hash_before": digest_of(before),
        "hash_after": digest_of(after),
        "external_writes": external_writes,
        "changed": changed,
        "added": added,
        "removed": removed,
    }
