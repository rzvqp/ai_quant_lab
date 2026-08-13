"""`DecisionProvenance`/`verify_decision_provenance` tests."""

from __future__ import annotations

import dataclasses

import pytest

from ai_trader.mandate2_readiness.decision_provenance import (
    NEW_BRAIN_SOURCE,
    DecisionProvenance,
    UntrustedDecisionSourceError,
    verify_decision_provenance,
)


def _valid_provenance(**overrides: str) -> DecisionProvenance:
    defaults = dict(
        source=NEW_BRAIN_SOURCE, trace_id="T1", catalog_hash="deadbeef", configuration_fingerprint="cfg-1",
    )
    defaults.update(overrides)
    return DecisionProvenance(**defaults)


def test_a_fully_valid_new_brain_provenance_passes_silently() -> None:
    verify_decision_provenance(_valid_provenance())  # no exception -- this IS the assertion


def test_any_source_other_than_new_brain_n6_is_rejected() -> None:
    for legacy_source in ("PdhPdlRecognitionRule", "LevelFvgConfluenceRecognitionRule", "", "new_brain_n6", "NEW_BRAIN_N6 "):
        with pytest.raises(UntrustedDecisionSourceError, match="UNTRUSTED_DECISION_SOURCE"):
            verify_decision_provenance(_valid_provenance(source=legacy_source))


def test_a_candidate_with_no_source_at_all_set_is_rejected_not_defaulted() -> None:
    """The realistic legacy case: `PdhPdlRecognitionRule`/`LevelFvgConfluenceRecognitionRule`/
    `DzLevelConfluenceRecognitionRule` never set `source` to anything -- confirmed by this codebase's own
    `LiveCandidate` having no such field at all today. A caller that forgets to attach provenance must
    hit this same rejection, not silently construct a "default" DecisionProvenance that happens to pass."""
    with pytest.raises(UntrustedDecisionSourceError):
        verify_decision_provenance(_valid_provenance(source=""))


@pytest.mark.parametrize("field", ["trace_id", "catalog_hash", "configuration_fingerprint"])
def test_each_required_identity_field_rejects_empty(field: str) -> None:
    with pytest.raises(UntrustedDecisionSourceError, match=field):
        verify_decision_provenance(_valid_provenance(**{field: ""}))


def test_multiple_missing_fields_are_all_reported_at_once() -> None:
    with pytest.raises(UntrustedDecisionSourceError) as exc_info:
        verify_decision_provenance(_valid_provenance(trace_id="", catalog_hash=""))
    assert "trace_id" in str(exc_info.value)
    assert "catalog_hash" in str(exc_info.value)


def test_source_check_happens_before_field_checks_but_both_are_reachable() -> None:
    """Not load-bearing on ordering per se, but confirms a wrong source is caught even when every other
    field also happens to be empty (the worst-case legacy candidate: no provenance attached at all)."""
    with pytest.raises(UntrustedDecisionSourceError, match="source"):
        verify_decision_provenance(DecisionProvenance(source="", trace_id="", catalog_hash="", configuration_fingerprint=""))


def test_provenance_is_frozen() -> None:
    provenance = _valid_provenance()
    with pytest.raises(dataclasses.FrozenInstanceError):
        provenance.source = "x"  # type: ignore[misc]
