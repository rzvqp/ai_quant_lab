"""Manifestul de PIN (schema v1.0): cele 10 câmpuri, emise din constantele VII ale artefactului, cu cele trei
identități SEPARATE (delivered package ≠ validated core ≠ measurement source), fără None/placeholder, iar JSON-ul
livrat corespunde EXACT emitentului pentru commitul de livrare declarat."""

from __future__ import annotations

import json
import os
import sys

import pytest

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

import ve_brain  # noqa: E402
from ve_brain.ev_engine import ENGINE_VERSION  # noqa: E402
from ve_brain.version import SOURCE_COMMIT as MEASUREMENT_SOURCE_COMMIT  # noqa: E402

_EXPECTED_FIELDS = (
    "manifest_schema_version", "package_version", "source_commit", "validated_core_commit",
    "catalog_version", "catalog_hash", "measurement_contract_version", "n1_contract_version",
    "router_version", "ev_engine_version",
)
_DELIVERY = "296e3ac"   # exemplu de commit de livrare (furnizat de instalator)


def test_manifest_has_exactly_ten_non_none_fields() -> None:
    m = ve_brain.artifact_manifest(_DELIVERY)
    assert tuple(m.keys()) == _EXPECTED_FIELDS
    assert all(isinstance(v, str) and v for v in m.values()), m   # niciun None, niciun gol


def test_three_identities_are_separate() -> None:
    m = ve_brain.artifact_manifest(_DELIVERY)
    assert m["source_commit"] == _DELIVERY                    # delivered package (furnizat de instalator)
    assert m["validated_core_commit"] == "fbc0f20"            # validated brain core (Red Team)
    assert MEASUREMENT_SOURCE_COMMIT == "dc28e4a"             # measurement source (câmp diferit, în version.py)
    assert len({m["source_commit"], m["validated_core_commit"], MEASUREMENT_SOURCE_COMMIT}) == 3


def test_delivery_commit_required_fail_closed() -> None:
    for bad in ("", "   "):
        with pytest.raises(ve_brain.DeliveryCommitRequiredError):
            ve_brain.artifact_manifest(bad)


def test_manifest_values_come_from_live_constants() -> None:
    m = ve_brain.artifact_manifest(_DELIVERY)
    assert m["manifest_schema_version"] == ve_brain.MANIFEST_SCHEMA_VERSION == "1.0"
    assert m["package_version"] == ve_brain.VE_BRAIN_VERSION
    assert m["validated_core_commit"] == ve_brain.VALIDATED_CORE_COMMIT
    assert m["catalog_version"] == ve_brain.CANONICAL_CATALOG_VERSION
    assert m["catalog_hash"] == ve_brain.CANONICAL_CATALOG_HASH
    assert m["measurement_contract_version"] == ve_brain.MEASUREMENT_CONTRACT_VERSION
    assert m["n1_contract_version"] == ve_brain.N1_CONTRACT_VERSION
    assert m["router_version"] == ve_brain.ROUTER_VERSION
    assert m["ev_engine_version"] == ENGINE_VERSION


def test_delivered_json_matches_emitter_for_its_delivery_commit() -> None:
    path = os.path.join(_PKG, "ARTIFACT_MANIFEST.json")
    with open(path, encoding="utf-8") as f:
        delivered = json.load(f)
    # JSON livrat == emitent viu pentru commitul de livrare pe care îl declară el însuși (nereconstruit manual)
    assert delivered == ve_brain.artifact_manifest(delivered["source_commit"])
