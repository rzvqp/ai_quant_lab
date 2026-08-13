"""MANIFESTUL ARTEFACTULUI — câmpurile de PIN, machine-readable, emise DIRECT din artefact, cu schemă VERSIONATĂ.

Cele TREI identități, care NU trebuie confundate într-un singur câmp:
  measurement source        = dc28e4a   (sursa contractului de măsurare; `version.SOURCE_COMMIT`)
  validated brain core       = fbc0f20   (nucleul verificat de Red Team, raport 46c462c)  → `validated_core_commit`
  delivered package          = <HEAD>    (commitul EXACT din care AI Trader instalează pachetul) → `source_commit`

`validated_core_commit` e o constantă STABILĂ, cunoscută, încorporată. `source_commit` (pachetul livrat) NU poate fi un
literal încorporat: un commit nu poate conține propriul hash. De aceea `artifact_manifest()` cere `delivery_commit`
EXPLICIT — îl furnizează cel care instalează (AI Trader citește `git rev-parse HEAD` din checkout-ul din care instalează;
nu îl inventează, îl citește din propria identitate git). Astfel `source_commit` e mereu EXACT commitul instalat, fără
auto-referință și fără placeholder. Lipsa lui ⇒ fail-closed (nu None).

`manifest_schema_version` fixează semantica acestor câmpuri ca IMUABILĂ și VERIFICABILĂ. Cele 8 valori derivate sunt
byte-identice cu fbc0f20 (demonstrat: `git diff fbc0f20` atinge doar fișiere de manifest).
"""

from __future__ import annotations

from .ev_engine import ENGINE_VERSION
from .version import (
    MEASUREMENT_CONTRACT_VERSION, N1_CONTRACT_VERSION, ROUTER_VERSION, VE_BRAIN_VERSION,
)
from ._canonical_catalog import CANONICAL_CATALOG_HASH, CANONICAL_CATALOG_VERSION

# versiunea schemei manifestului — pinează semantica celor 10 câmpuri (imuabilă + verificabilă)
MANIFEST_SCHEMA_VERSION: str = "1.0"

# nucleul brain VERIFICAT de Red Team (fbc0f20, raport 46c462c). Stabil, cunoscut, încorporat. ≠ pachetul livrat.
VALIDATED_CORE_COMMIT: str = "fbc0f20"

# ordinea + numele câmpurilor = contractul de pin cu AI Trader; toate 10 OBLIGATORII, niciunul None.
MANIFEST_FIELDS: tuple[str, ...] = (
    "manifest_schema_version", "package_version", "source_commit", "validated_core_commit",
    "catalog_version", "catalog_hash", "measurement_contract_version", "n1_contract_version",
    "router_version", "ev_engine_version",
)


class DeliveryCommitRequiredError(ValueError):
    """`source_commit` (pachetul livrat) trebuie furnizat EXPLICIT de instalator — fail-closed, niciun placeholder."""


def artifact_manifest(delivery_commit: str) -> dict[str, str]:
    """Cele 10 câmpuri de pin. `delivery_commit` = commitul EXACT din care se instalează pachetul (furnizat de
    instalator, ex. `git rev-parse HEAD`). Restul din constantele VII ale artefactului. Determinist, fără None."""
    if not isinstance(delivery_commit, str) or not delivery_commit.strip():
        raise DeliveryCommitRequiredError(
            "source_commit (delivery_commit) lipsă — furnizează commitul instalat; niciun placeholder/None")
    m: dict[str, str] = {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "package_version": VE_BRAIN_VERSION,
        "source_commit": delivery_commit.strip(),
        "validated_core_commit": VALIDATED_CORE_COMMIT,
        "catalog_version": CANONICAL_CATALOG_VERSION,
        "catalog_hash": CANONICAL_CATALOG_HASH,
        "measurement_contract_version": MEASUREMENT_CONTRACT_VERSION,
        "n1_contract_version": N1_CONTRACT_VERSION,
        "router_version": ROUTER_VERSION,
        "ev_engine_version": ENGINE_VERSION,
    }
    assert tuple(m.keys()) == MANIFEST_FIELDS, "manifest field set/order drift"
    assert all(isinstance(v, str) and v for v in m.values()), "manifest field gol/absent"
    return m
