"""Unit tests for :class:`ai_trader.context_memory.contracts.Outcome`."""

from __future__ import annotations

import dataclasses

import pytest

from ai_trader.context_memory.contracts import ObservationId
from ai_trader.context_memory.enums import OutcomeKind, OutcomeStatus, SourceType
from ai_trader.context_memory.identities import compute_edge_evidence_id
from ai_trader.context_memory.tests._fixtures import AS_OF, make_pending_outcome
from ai_trader.context_memory.validation import ContextMemoryValidationError

OBS_ID = ObservationId("fake-observation-id-for-outcome-tests")


def test_valid_pending_construction() -> None:
    out = make_pending_outcome(OBS_ID)
    assert out.status is OutcomeStatus.PENDING
    assert out.normalized_result is None
    assert out.resolution_as_of is None


def test_immutable() -> None:
    out = make_pending_outcome(OBS_ID)
    with pytest.raises(dataclasses.FrozenInstanceError):
        out.status = OutcomeStatus.RESOLVED  # type: ignore[misc]


def test_valid_resolved_construction() -> None:
    out = make_pending_outcome(
        OBS_ID, status=OutcomeStatus.RESOLVED, normalized_result=0.42, resolution_as_of=AS_OF + 20,
    )
    assert out.status is OutcomeStatus.RESOLVED
    assert out.normalized_result == 0.42
    assert out.resolution_as_of == AS_OF + 20


def test_pending_with_numerical_result_is_rejected() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(OBS_ID, status=OutcomeStatus.PENDING, normalized_result=0.1)


def test_pending_with_resolution_timestamp_is_rejected() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(OBS_ID, status=OutcomeStatus.PENDING, resolution_as_of=AS_OF + 20)


def test_resolved_without_numerical_result_is_rejected() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(OBS_ID, status=OutcomeStatus.RESOLVED, resolution_as_of=AS_OF + 20)


def test_resolved_without_resolution_timestamp_is_rejected() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(OBS_ID, status=OutcomeStatus.RESOLVED, normalized_result=0.1)


def test_resolution_before_observation_is_rejected() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(
            OBS_ID, status=OutcomeStatus.RESOLVED, normalized_result=0.1, resolution_as_of=AS_OF - 1,
        )


def test_invalid_status_with_numerical_result_is_rejected() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(OBS_ID, status=OutcomeStatus.INVALID, normalized_result=0.1)


def test_unavailable_status_with_numerical_result_is_rejected() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(OBS_ID, status=OutcomeStatus.UNAVAILABLE, normalized_result=0.1)


def test_invalid_status_without_result_is_accepted() -> None:
    out = make_pending_outcome(OBS_ID, status=OutcomeStatus.INVALID)
    assert out.status is OutcomeStatus.INVALID
    assert out.normalized_result is None


def test_invalid_status_may_carry_a_resolution_timestamp() -> None:
    out = make_pending_outcome(OBS_ID, status=OutcomeStatus.INVALID, resolution_as_of=AS_OF + 20)
    assert out.resolution_as_of == AS_OF + 20


def test_rejects_non_finite_normalized_result() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(
            OBS_ID, status=OutcomeStatus.RESOLVED, normalized_result=float("nan"), resolution_as_of=AS_OF + 20,
        )


def test_rejects_non_positive_horizon() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(OBS_ID, horizon=0)
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(OBS_ID, horizon=-5)


def test_rejects_wrong_observation_id_type() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome("not-an-observation-id")  # type: ignore[arg-type]


def test_rejects_wrong_source_type() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(OBS_ID, source_type="PRICE_ONLY")  # a raw string


def test_rejects_wrong_horizon_unit_type() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(OBS_ID, horizon_unit="BARS")  # a raw string


def test_rejects_wrong_outcome_definition_version_type() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(OBS_ID, outcome_definition_version="od-v1")  # a raw string


def test_rejects_wrong_status_type() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(OBS_ID, status="PENDING")  # a raw string


def test_invalid_status_resolution_before_observation_is_rejected() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(OBS_ID, status=OutcomeStatus.INVALID, resolution_as_of=AS_OF - 1)


def test_id_is_deterministic() -> None:
    a = make_pending_outcome(OBS_ID)
    b = make_pending_outcome(OBS_ID)
    assert compute_edge_evidence_id(a) == compute_edge_evidence_id(b)


def test_id_differs_on_status() -> None:
    pending = make_pending_outcome(OBS_ID)
    resolved = make_pending_outcome(
        OBS_ID, status=OutcomeStatus.RESOLVED, normalized_result=0.1, resolution_as_of=AS_OF + 20,
    )
    assert compute_edge_evidence_id(pending) != compute_edge_evidence_id(resolved)


def test_id_fixed_expected_value() -> None:
    real_observation_id = ObservationId("d0e6e3a9ac874f9e5cfc760dcb4fb3e60dfac8f5eb9b5113ebff9f2ca312f370")
    out = make_pending_outcome(
        real_observation_id, strategy_id="S1",
        source_type=SourceType.SHADOW_EVIDENCE_ADAPTER, outcome_kind=OutcomeKind.STRATEGY,
    )
    result = compute_edge_evidence_id(out)
    assert result.value == "d165fd9e17a2eef51eef798f55187cf41fb948b79a4071fcdd830edf0c33ca7d"


# ------------------------------------------------------------------ outcome_kind / source_type pairing


def test_valid_strategy_shadow_pair_constructs() -> None:
    out = make_pending_outcome(
        OBS_ID, source_type=SourceType.SHADOW_EVIDENCE_ADAPTER, outcome_kind=OutcomeKind.STRATEGY,
    )
    assert out.outcome_kind is OutcomeKind.STRATEGY
    assert out.source_type is SourceType.SHADOW_EVIDENCE_ADAPTER


def test_valid_portfolio_real_ledger_pair_constructs() -> None:
    out = make_pending_outcome(
        OBS_ID, source_type=SourceType.REAL_PORTFOLIO_LEDGER, outcome_kind=OutcomeKind.PORTFOLIO,
    )
    assert out.outcome_kind is OutcomeKind.PORTFOLIO
    assert out.source_type is SourceType.REAL_PORTFOLIO_LEDGER


def test_portfolio_kind_with_shadow_adapter_source_is_rejected() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(
            OBS_ID, source_type=SourceType.SHADOW_EVIDENCE_ADAPTER, outcome_kind=OutcomeKind.PORTFOLIO,
        )


def test_strategy_kind_with_real_ledger_source_is_rejected() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(
            OBS_ID, source_type=SourceType.REAL_PORTFOLIO_LEDGER, outcome_kind=OutcomeKind.STRATEGY,
        )


def test_rejects_wrong_outcome_kind_type() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_pending_outcome(OBS_ID, outcome_kind="STRATEGY")  # a raw string
