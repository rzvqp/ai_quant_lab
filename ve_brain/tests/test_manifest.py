"""Manifestul de PIN: cele 8 câmpuri, emise din constantele VII ale artefactului, fără None/placeholder, și
JSON-ul livrat corespunde EXACT emitentului (machine-readable + imuabil)."""

from __future__ import annotations

import json
import os
import sys

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

import ve_brain  # noqa: E402
from ve_brain.ev_engine import ENGINE_VERSION  # noqa: E402

_EXPECTED_FIELDS = (
    "package_version", "source_commit", "catalog_version", "catalog_hash",
    "measurement_contract_version", "n1_contract_version", "router_version", "ev_engine_version",
)


def test_manifest_has_exactly_eight_non_none_fields() -> None:
    m = ve_brain.artifact_manifest()
    assert tuple(m.keys()) == _EXPECTED_FIELDS
    assert all(isinstance(v, str) and v for v in m.values()), m   # niciun None, niciun gol


def test_manifest_values_come_from_live_constants() -> None:
    m = ve_brain.artifact_manifest()
    assert m["package_version"] == ve_brain.VE_BRAIN_VERSION
    assert m["source_commit"] == ve_brain.ARTIFACT_SOURCE_COMMIT == "fbc0f20"
    assert m["catalog_version"] == ve_brain.CANONICAL_CATALOG_VERSION
    assert m["catalog_hash"] == ve_brain.CANONICAL_CATALOG_HASH
    assert m["measurement_contract_version"] == ve_brain.MEASUREMENT_CONTRACT_VERSION
    assert m["n1_contract_version"] == ve_brain.N1_CONTRACT_VERSION
    assert m["router_version"] == ve_brain.ROUTER_VERSION
    assert m["ev_engine_version"] == ENGINE_VERSION


def test_delivered_json_matches_emitter() -> None:
    path = os.path.join(_PKG, "ARTIFACT_MANIFEST.json")
    with open(path, encoding="utf-8") as f:
        delivered = json.load(f)
    assert delivered == ve_brain.artifact_manifest()   # JSON livrat == emitent viu (nereconstruit manual)
