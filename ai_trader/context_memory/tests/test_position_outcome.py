"""Tests for PositionOutcome -- Learning/Research Feedback Sprint 2, Blocker 2 (CEO-ratified): the ONE
canonical, unambiguous, Level-1 accounting result for a complete economic position lifecycle.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.context_memory.contracts import (
    EdgeEvidenceId,
    InterimRealizationId,
    ObservationId,
    PositionOutcome,
    PositionOutcomeId,
)
from ai_trader.context_memory.enums import OutcomeKind, SourceType
from ai_trader.context_memory.identities import compute_position_outcome_id
from ai_trader.context_memory.repository import ContextMemoryRepository
from ai_trader.context_memory.validation import ContextMemoryValidationError

OBS_ID = ObservationId("x" * 64)
AS_OF = 1_700_000_000


def _position_outcome(**overrides: object) -> PositionOutcome:
    kwargs: dict[str, object] = {
        "observation_id": OBS_ID, "strategy_id": "S1", "position_key": "run-A:XAUUSD:1700000000:LONG",
        "outcome_kind": OutcomeKind.PORTFOLIO, "source_type": SourceType.REAL_PORTFOLIO_LEDGER,
        "opened_as_of": AS_OF, "terminal_as_of": AS_OF + 1200, "total_qty_closed": 7.0,
        "weighted_avg_exit_price": 2010.0, "total_gross_pnl": 70.0, "total_net_pnl": 65.0,
        "total_costs": 5.0, "cost_model_ref": "ref-1", "terminal_outcome_id": EdgeEvidenceId("y" * 64),
        "constituent_interim_realization_ids": (InterimRealizationId("z" * 64),),
    }
    kwargs.update(overrides)
    return PositionOutcome(**kwargs)  # type: ignore[arg-type]


# ------------------------------------------------------------------ construction validation


def test_construction_happy_path() -> None:
    po = _position_outcome()
    assert po.total_qty_closed == 7.0
    assert len(po.constituent_interim_realization_ids) == 1


def test_rejects_invalid_kind_source_pair() -> None:
    with pytest.raises(ContextMemoryValidationError):
        _position_outcome(outcome_kind=OutcomeKind.STRATEGY, source_type=SourceType.REAL_PORTFOLIO_LEDGER)


def test_rejects_terminal_before_opened() -> None:
    with pytest.raises(ContextMemoryValidationError):
        _position_outcome(terminal_as_of=AS_OF - 1)


def test_rejects_non_positive_total_qty_closed() -> None:
    with pytest.raises(ContextMemoryValidationError):
        _position_outcome(total_qty_closed=0.0)


def test_rejects_empty_position_key() -> None:
    with pytest.raises(ContextMemoryValidationError):
        _position_outcome(position_key="")


def test_weighted_avg_exit_price_may_be_none() -> None:
    po = _position_outcome(weighted_avg_exit_price=None)
    assert po.weighted_avg_exit_price is None


def test_constituent_ids_may_be_empty_single_partial_case() -> None:
    # A position closed by a SINGLE fill (no interim partials at all) has zero constituent
    # InterimRealizationIds -- the continuity/degenerate case, must not be rejected.
    po = _position_outcome(constituent_interim_realization_ids=())
    assert po.constituent_interim_realization_ids == ()


# ------------------------------------------------------------------ identity determinism


def test_identity_is_deterministic() -> None:
    a = compute_position_outcome_id(_position_outcome())
    b = compute_position_outcome_id(_position_outcome())
    assert a == b
    assert isinstance(a, PositionOutcomeId)


def test_identity_is_sensitive_to_total_net_pnl() -> None:
    a = compute_position_outcome_id(_position_outcome(total_net_pnl=65.0))
    b = compute_position_outcome_id(_position_outcome(total_net_pnl=66.0))
    assert a != b


def test_identity_is_sensitive_to_constituent_ids() -> None:
    a = compute_position_outcome_id(_position_outcome(constituent_interim_realization_ids=()))
    b = compute_position_outcome_id(
        _position_outcome(constituent_interim_realization_ids=(InterimRealizationId("z" * 64),))
    )
    assert a != b


# ------------------------------------------------------------------ repository round-trip


def test_repository_append_get_roundtrip(tmp_path: Path) -> None:
    repo = ContextMemoryRepository(tmp_path / "repo")
    position_outcome = _position_outcome()
    record_id = repo.append_position_outcome(position_outcome)
    fetched = repo.get_position_outcome(record_id)
    assert fetched == position_outcome
    assert repo.count_position_outcomes() == 1
    assert list(repo.iter_position_outcomes()) == [position_outcome]


def test_repository_append_is_idempotent(tmp_path: Path) -> None:
    repo = ContextMemoryRepository(tmp_path / "repo")
    position_outcome = _position_outcome()
    first = repo.append_position_outcome(position_outcome)
    second = repo.append_position_outcome(position_outcome)
    assert first == second
    assert repo.count_position_outcomes() == 1


def test_repository_survives_rebuild(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    repo1 = ContextMemoryRepository(root)
    position_outcome = _position_outcome()
    record_id = repo1.append_position_outcome(position_outcome)

    repo2 = ContextMemoryRepository(root)
    assert repo2.get_position_outcome(record_id) == position_outcome
    assert repo2.count_position_outcomes() == 1


def test_never_exported_from_evidence_or_retrieval_aggregation() -> None:
    # Structural proof, mirroring OperationalMetadata/InterimRealization's own precedent: neither
    # aggregation module references PositionOutcome at all -- it is never a learning target for the
    # existing evidence/retrieval pipeline (a future, separately-authorized phase may change this).
    import ai_trader.context_memory.evidence as evidence_module
    import ai_trader.context_memory.retrieval as retrieval_module

    assert "PositionOutcome" not in dir(evidence_module)
    assert "PositionOutcome" not in dir(retrieval_module)
