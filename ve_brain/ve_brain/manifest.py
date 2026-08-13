"""MANIFESTUL ARTEFACTULUI — cele 8 câmpuri de PIN, machine-readable, emise DIRECT din artefact.

AI Trader NU copiază valorile din conversație și NU inventează placeholder-e: apelează `artifact_manifest()` pe
pachetul INSTALAT și obține cele 8 câmpuri din constantele vii ale artefactului. Verificarea de pin (`verify_artifact_pin`)
compară manifestul cu artefactul căruia Red Team i-a acordat VE_HANDOFF_PASS.

`source_commit` = identitatea GIT a artefactului PASS-uit (raport Red Team 46c462c). Constantele de mai jos (7 câmpuri
derivate) sunt citite din cod; commit-ul de release e înregistrat aici pentru că nu poate fi derivat din constante
Python. Comisul care adaugă acest emitent NU modifică niciuna dintre cele 8 valori (verificabil: `git diff fbc0f20 HEAD`
atinge doar fișiere de manifest) — deci manifestul corespunde EXACT release-ului fbc0f20.
"""

from __future__ import annotations

from .ev_engine import ENGINE_VERSION
from .version import (
    MEASUREMENT_CONTRACT_VERSION, N1_CONTRACT_VERSION, ROUTER_VERSION, VE_BRAIN_VERSION,
)
from ._canonical_catalog import CANONICAL_CATALOG_HASH, CANONICAL_CATALOG_VERSION

# identitatea git a artefactului PASS-uit de Red Team (fbc0f20, raport 46c462c). NU alt commit.
ARTIFACT_SOURCE_COMMIT: str = "fbc0f20"

# ordinea + numele câmpurilor sunt contractul de pin cu AI Trader; toate 8 sunt OBLIGATORII, niciunul None.
MANIFEST_FIELDS: tuple[str, ...] = (
    "package_version", "source_commit", "catalog_version", "catalog_hash",
    "measurement_contract_version", "n1_contract_version", "router_version", "ev_engine_version",
)


def artifact_manifest() -> dict[str, str]:
    """Cele 8 câmpuri de pin, din constantele VII ale artefactului. Determinist, fără None, fără placeholder."""
    m: dict[str, str] = {
        "package_version": VE_BRAIN_VERSION,
        "source_commit": ARTIFACT_SOURCE_COMMIT,
        "catalog_version": CANONICAL_CATALOG_VERSION,
        "catalog_hash": CANONICAL_CATALOG_HASH,
        "measurement_contract_version": MEASUREMENT_CONTRACT_VERSION,
        "n1_contract_version": N1_CONTRACT_VERSION,
        "router_version": ROUTER_VERSION,
        "ev_engine_version": ENGINE_VERSION,
    }
    # invariant: exact cele 8 câmpuri, toate ne-goale (fail-closed dacă o constantă ar lipsi)
    assert tuple(m.keys()) == MANIFEST_FIELDS, "manifest field set/order drift"
    assert all(isinstance(v, str) and v for v in m.values()), "manifest field gol/absent"
    return m
