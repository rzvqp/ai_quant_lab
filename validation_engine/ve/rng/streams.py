"""Semințe derivate determinist din hash-ul specificației (arhitectură §10).

`seed(test) = sha256(spec_sha256 || test_id)[:8]`. Aceeași specificație → aceleași
semințe, pe orice mașină. Nicio sămânță nu vine din ceas, entropie de sistem sau
ordinea de iterare. Acest modul NU rulează niciun generator aleator; doar derivă
valorile, ca ele să fie auditabile fără a executa nimic (relevant la F3).
"""

from __future__ import annotations

import hashlib


def _derive(spec_sha256: str, label: str) -> int:
    h = hashlib.sha256(f"{spec_sha256}||{label}".encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def root_seed(spec_sha256: str) -> int:
    return _derive(spec_sha256, "__root__")


def derive_seeds(spec_sha256: str, test_ids: list[str]) -> dict:
    """Semințele rădăcină + per-test, pur derivate. Fără execuție de RNG."""
    return {
        "root_seed": root_seed(spec_sha256),
        "derivation": "sha256(spec_sha256 || test_id)[:8]",
        "streams": {tid: _derive(spec_sha256, tid) for tid in test_ids},
    }
