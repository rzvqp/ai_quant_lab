"""`BrainArtifactPin`/`verify_artifact_pin` tests -- proves the fail-closed contract, and specifically
that the six not-yet-pinned fields refuse EVERY observed manifest, not just mismatched ones."""

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
    package_version="0.1.3", source_commit="fbc0f20", catalog_version="cat-1", catalog_hash="deadbeef",
    measurement_contract_version="mc-1", n1_contract_version="n1-1", router_version="rt-1", ev_engine_version="ev-1",
)


def test_current_pin_has_exactly_the_two_ceo_supplied_values() -> None:
    assert CURRENT_PIN.package_version == "0.1.3"
    assert CURRENT_PIN.source_commit == "fbc0f20"
    assert CURRENT_PIN.catalog_version is None
    assert CURRENT_PIN.catalog_hash is None
    assert CURRENT_PIN.measurement_contract_version is None
    assert CURRENT_PIN.n1_contract_version is None
    assert CURRENT_PIN.router_version is None
    assert CURRENT_PIN.ev_engine_version is None


def test_current_pin_refuses_even_a_manifest_that_matches_the_two_known_fields_exactly() -> None:
    """The central, easy-to-get-wrong property: matching the two KNOWN fields is not enough -- six
    fields have no reference value yet, so nothing can pass today."""
    with pytest.raises(BrainArtifactIncompatibleError) as exc_info:
        verify_artifact_pin(_FULLY_MATCHING_OBSERVED, pin=CURRENT_PIN)
    assert "6 of 8" in str(exc_info.value)


def test_a_fully_pinned_and_fully_matching_manifest_passes_silently() -> None:
    fully_pinned = BrainArtifactPin(
        package_version="0.1.3", source_commit="fbc0f20", catalog_version="cat-1", catalog_hash="deadbeef",
        measurement_contract_version="mc-1", n1_contract_version="n1-1", router_version="rt-1", ev_engine_version="ev-1",
    )
    verify_artifact_pin(_FULLY_MATCHING_OBSERVED, pin=fully_pinned)  # no exception -- this IS the assertion


def test_a_single_mismatched_field_still_refuses_even_if_fully_pinned() -> None:
    fully_pinned = BrainArtifactPin(
        package_version="0.1.3", source_commit="fbc0f20", catalog_version="cat-1", catalog_hash="deadbeef",
        measurement_contract_version="mc-1", n1_contract_version="n1-1", router_version="rt-1", ev_engine_version="ev-1",
    )
    wrong_commit = ObservedArtifactManifest(
        package_version="0.1.3", source_commit="DIFFERENT", catalog_version="cat-1", catalog_hash="deadbeef",
        measurement_contract_version="mc-1", n1_contract_version="n1-1", router_version="rt-1", ev_engine_version="ev-1",
    )
    with pytest.raises(BrainArtifactIncompatibleError, match="1 of 8"):
        verify_artifact_pin(wrong_commit, pin=fully_pinned)


def test_no_approximately_compatible_version_is_ever_accepted() -> None:
    """CEO's own explicit wording: 'NU poate continua pe alta versiune compatibila aproximativ' -- exact
    string equality only, no semver range/prefix logic anywhere in `verify_artifact_pin`."""
    fully_pinned = BrainArtifactPin(
        package_version="0.1.3", source_commit="fbc0f20", catalog_version="cat-1", catalog_hash="deadbeef",
        measurement_contract_version="mc-1", n1_contract_version="n1-1", router_version="rt-1", ev_engine_version="ev-1",
    )
    almost = ObservedArtifactManifest(
        package_version="0.1.4",  # one patch version ahead -- still refused
        source_commit="fbc0f20", catalog_version="cat-1", catalog_hash="deadbeef",
        measurement_contract_version="mc-1", n1_contract_version="n1-1", router_version="rt-1", ev_engine_version="ev-1",
    )
    with pytest.raises(BrainArtifactIncompatibleError):
        verify_artifact_pin(almost, pin=fully_pinned)


def test_pin_field_names_have_not_drifted_from_the_dataclass_definition() -> None:
    assert set(_all_pin_field_names()) == {
        "package_version", "source_commit", "catalog_version", "catalog_hash",
        "measurement_contract_version", "n1_contract_version", "router_version", "ev_engine_version",
    }


def test_pin_and_observed_manifest_are_both_frozen() -> None:
    import dataclasses

    pin = BrainArtifactPin()
    with pytest.raises(dataclasses.FrozenInstanceError):
        pin.package_version = "x"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        _FULLY_MATCHING_OBSERVED.package_version = "x"  # type: ignore[misc]
