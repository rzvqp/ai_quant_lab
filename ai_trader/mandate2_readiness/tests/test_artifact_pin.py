"""`BrainArtifactPin`/`verify_artifact_pin` tests -- proves the fail-closed contract on the corrected
ten-field schema (2026-08-14), and specifically that `source_commit`/`validated_core_commit` are
distinct fields that must each match independently."""

from __future__ import annotations

import pytest

from ai_trader.mandate2_readiness.artifact_pin import (
    CURRENT_PIN,
    BrainArtifactIncompatibleError,
    BrainArtifactPin,
    ObservedArtifactManifest,
    _all_pin_field_names,
    verify_artifact_pin,
)

_FULLY_MATCHING_OBSERVED = ObservedArtifactManifest(
    package_version="0.1.3", source_commit="296e3ac", validated_core_commit="fbc0f20",
    catalog_version="ve-canonical-catalog-v1", catalog_hash="37b95393df85dc2b",
    measurement_contract_version="canonical-evaluator-v2.7.66-A2", n1_contract_version="n1-additive-raw-axes-v1",
    router_version="router-v1", ev_engine_version="ev-core@bdd15e5+ev-adapter-v1",
    manifest_schema_version="schema-v1",
)


def test_current_pin_has_exactly_the_nine_ceo_supplied_values() -> None:
    assert CURRENT_PIN.package_version == "0.1.3"
    assert CURRENT_PIN.source_commit == "296e3ac"
    assert CURRENT_PIN.validated_core_commit == "fbc0f20"
    assert CURRENT_PIN.catalog_version == "ve-canonical-catalog-v1"
    assert CURRENT_PIN.catalog_hash == "37b95393df85dc2b"
    assert CURRENT_PIN.measurement_contract_version == "canonical-evaluator-v2.7.66-A2"
    assert CURRENT_PIN.n1_contract_version == "n1-additive-raw-axes-v1"
    assert CURRENT_PIN.router_version == "router-v1"
    assert CURRENT_PIN.ev_engine_version == "ev-core@bdd15e5+ev-adapter-v1"


def test_manifest_schema_version_is_the_one_deferred_field() -> None:
    assert CURRENT_PIN.manifest_schema_version is None


def test_current_pin_refuses_even_a_manifest_that_matches_all_nine_known_fields_exactly() -> None:
    """The central, easy-to-get-wrong property: matching the nine KNOWN fields is not enough -- one
    field (manifest_schema_version) has no reference value yet, so nothing can pass today."""
    with pytest.raises(BrainArtifactIncompatibleError) as exc_info:
        verify_artifact_pin(_FULLY_MATCHING_OBSERVED, pin=CURRENT_PIN)
    assert "1 of 10" in str(exc_info.value)
    assert "manifest_schema_version" in str(exc_info.value)


def _fully_pinned() -> BrainArtifactPin:
    return BrainArtifactPin(
        package_version="0.1.3", source_commit="296e3ac", validated_core_commit="fbc0f20",
        catalog_version="ve-canonical-catalog-v1", catalog_hash="37b95393df85dc2b",
        measurement_contract_version="canonical-evaluator-v2.7.66-A2", n1_contract_version="n1-additive-raw-axes-v1",
        router_version="router-v1", ev_engine_version="ev-core@bdd15e5+ev-adapter-v1",
        manifest_schema_version="schema-v1",
    )


def test_a_fully_pinned_and_fully_matching_manifest_passes_silently() -> None:
    verify_artifact_pin(_FULLY_MATCHING_OBSERVED, pin=_fully_pinned())  # no exception -- the assertion


def test_source_commit_and_validated_core_commit_are_checked_independently() -> None:
    """The exact defect this schema correction fixed: a delivered package commit that matches
    `source_commit` but whose CONTAINED core doesn't match `validated_core_commit` (or vice versa) must
    still be refused -- they are two separate facts, not one field wearing two hats."""
    wrong_core = ObservedArtifactManifest(
        package_version="0.1.3", source_commit="296e3ac", validated_core_commit="DIFFERENT_CORE",
        catalog_version="ve-canonical-catalog-v1", catalog_hash="37b95393df85dc2b",
        measurement_contract_version="canonical-evaluator-v2.7.66-A2", n1_contract_version="n1-additive-raw-axes-v1",
        router_version="router-v1", ev_engine_version="ev-core@bdd15e5+ev-adapter-v1",
        manifest_schema_version="schema-v1",
    )
    with pytest.raises(BrainArtifactIncompatibleError, match="validated_core_commit"):
        verify_artifact_pin(wrong_core, pin=_fully_pinned())

    wrong_package = ObservedArtifactManifest(
        package_version="0.1.3", source_commit="DIFFERENT_PACKAGE", validated_core_commit="fbc0f20",
        catalog_version="ve-canonical-catalog-v1", catalog_hash="37b95393df85dc2b",
        measurement_contract_version="canonical-evaluator-v2.7.66-A2", n1_contract_version="n1-additive-raw-axes-v1",
        router_version="router-v1", ev_engine_version="ev-core@bdd15e5+ev-adapter-v1",
        manifest_schema_version="schema-v1",
    )
    with pytest.raises(BrainArtifactIncompatibleError, match="source_commit"):
        verify_artifact_pin(wrong_package, pin=_fully_pinned())


def test_no_approximately_compatible_version_is_ever_accepted() -> None:
    """CEO's own explicit wording: 'NU poate continua pe alta versiune compatibila aproximativ' -- exact
    string equality only, no semver range/prefix logic anywhere in `verify_artifact_pin`."""
    almost = ObservedArtifactManifest(
        package_version="0.1.4",  # one patch version ahead -- still refused
        source_commit="296e3ac", validated_core_commit="fbc0f20", catalog_version="ve-canonical-catalog-v1",
        catalog_hash="37b95393df85dc2b", measurement_contract_version="canonical-evaluator-v2.7.66-A2",
        n1_contract_version="n1-additive-raw-axes-v1", router_version="router-v1",
        ev_engine_version="ev-core@bdd15e5+ev-adapter-v1", manifest_schema_version="schema-v1",
    )
    with pytest.raises(BrainArtifactIncompatibleError):
        verify_artifact_pin(almost, pin=_fully_pinned())


def test_pin_field_names_have_not_drifted_from_the_dataclass_definition() -> None:
    assert set(_all_pin_field_names()) == {
        "package_version", "source_commit", "validated_core_commit", "catalog_version", "catalog_hash",
        "measurement_contract_version", "n1_contract_version", "router_version", "ev_engine_version",
        "manifest_schema_version",
    }


def test_pin_and_observed_manifest_are_both_frozen() -> None:
    import dataclasses

    pin = BrainArtifactPin()
    with pytest.raises(dataclasses.FrozenInstanceError):
        pin.package_version = "x"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        _FULLY_MATCHING_OBSERVED.package_version = "x"  # type: ignore[misc]
