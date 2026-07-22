"""Tests for InterimRealization -- Learning/Research Feedback Phase F, Architectural Decision Package
Decision 3 (Option C): a diagnostic-only companion type, never a learning target, mirroring
OperationalMetadata's own established precedent exactly.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.context_memory.contracts import InterimRealization, InterimRealizationId, ObservationId
from ai_trader.context_memory.enums import HorizonUnit, OutcomeKind, OutcomeUnavailableReason, SourceType
from ai_trader.context_memory.identities import compute_interim_realization_id
from ai_trader.context_memory.repository import ContextMemoryRepository
from ai_trader.context_memory.validation import ContextMemoryValidationError

OBS_ID = ObservationId("x" * 64)
AS_OF = 1_700_000_000


def _realization(**overrides: object) -> InterimRealization:
    kwargs: dict[str, object] = {
        "observation_id": OBS_ID, "strategy_id": "S1", "position_key": "run-A:XAUUSD:1700000000:LONG",
        "outcome_kind": OutcomeKind.PORTFOLIO, "source_type": SourceType.REAL_PORTFOLIO_LEDGER,
        "horizon": 4, "horizon_unit": HorizonUnit.BARS, "observation_as_of": AS_OF,
        "realization_as_of": AS_OF + 400, "normalized_result": 0.6, "cost_model_ref": "ref-1",
        "unavailable_reason": None,
    }
    kwargs.update(overrides)
    return InterimRealization(**kwargs)  # type: ignore[arg-type]


# ------------------------------------------------------------------ construction validation


def test_construction_happy_path() -> None:
    r = _realization()
    assert r.normalized_result == 0.6
    assert r.unavailable_reason is None


def test_requires_exactly_one_of_normalized_result_or_unavailable_reason() -> None:
    with pytest.raises(ContextMemoryValidationError):
        _realization(normalized_result=None, unavailable_reason=None)
    with pytest.raises(ContextMemoryValidationError):
        _realization(normalized_result=0.5, unavailable_reason=OutcomeUnavailableReason.NO_VALID_RISK_DENOMINATOR)


def test_unavailable_reason_path() -> None:
    r = _realization(normalized_result=None, unavailable_reason=OutcomeUnavailableReason.NO_VALID_RISK_DENOMINATOR)
    assert r.normalized_result is None
    assert r.unavailable_reason is OutcomeUnavailableReason.NO_VALID_RISK_DENOMINATOR


def test_rejects_invalid_kind_source_pair() -> None:
    with pytest.raises(ContextMemoryValidationError):
        _realization(outcome_kind=OutcomeKind.STRATEGY, source_type=SourceType.REAL_PORTFOLIO_LEDGER)


def test_rejects_realization_before_observation() -> None:
    with pytest.raises(ContextMemoryValidationError):
        _realization(realization_as_of=AS_OF - 1)


def test_rejects_empty_position_key() -> None:
    with pytest.raises(ContextMemoryValidationError):
        _realization(position_key="")


def test_rejects_non_positive_horizon() -> None:
    with pytest.raises(ContextMemoryValidationError):
        _realization(horizon=0)


# ------------------------------------------------------------------ identity determinism


def test_identity_is_deterministic() -> None:
    a = compute_interim_realization_id(_realization())
    b = compute_interim_realization_id(_realization())
    assert a == b
    assert isinstance(a, InterimRealizationId)


def test_identity_is_sensitive_to_position_key() -> None:
    a = compute_interim_realization_id(_realization())
    b = compute_interim_realization_id(_realization(position_key="run-A:XAUUSD:1700000400:LONG"))
    assert a != b


def test_identity_is_sensitive_to_normalized_result() -> None:
    a = compute_interim_realization_id(_realization(normalized_result=0.6))
    b = compute_interim_realization_id(_realization(normalized_result=0.7))
    assert a != b


# ------------------------------------------------------------------ repository round-trip


def test_repository_append_get_roundtrip(tmp_path: Path) -> None:
    repo = ContextMemoryRepository(tmp_path / "repo")
    realization = _realization()
    record_id = repo.append_interim_realization(realization)
    fetched = repo.get_interim_realization(record_id)
    assert fetched == realization
    assert repo.count_interim_realizations() == 1
    assert list(repo.iter_interim_realizations()) == [realization]


def test_repository_append_is_idempotent(tmp_path: Path) -> None:
    repo = ContextMemoryRepository(tmp_path / "repo")
    realization = _realization()
    first = repo.append_interim_realization(realization)
    second = repo.append_interim_realization(realization)
    assert first == second
    assert repo.count_interim_realizations() == 1


def test_repository_unavailable_roundtrip(tmp_path: Path) -> None:
    repo = ContextMemoryRepository(tmp_path / "repo")
    realization = _realization(normalized_result=None, unavailable_reason=OutcomeUnavailableReason.NO_VALID_RISK_DENOMINATOR)
    record_id = repo.append_interim_realization(realization)
    fetched = repo.get_interim_realization(record_id)
    assert fetched == realization


def test_repository_survives_rebuild(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    repo1 = ContextMemoryRepository(root)
    realization = _realization()
    record_id = repo1.append_interim_realization(realization)

    repo2 = ContextMemoryRepository(root)
    assert repo2.get_interim_realization(record_id) == realization
    assert repo2.count_interim_realizations() == 1


def test_never_exported_from_evidence_or_retrieval_aggregation() -> None:
    # Structural proof (mirrors OperationalMetadata's own precedent): neither aggregation module
    # references InterimRealization at all -- it is never a learning target.
    import ai_trader.context_memory.evidence as evidence_module
    import ai_trader.context_memory.retrieval as retrieval_module

    assert "InterimRealization" not in dir(evidence_module)
    assert "InterimRealization" not in dir(retrieval_module)
