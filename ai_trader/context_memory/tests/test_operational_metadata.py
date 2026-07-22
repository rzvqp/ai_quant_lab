"""Unit/integration tests for :class:`~ai_trader.context_memory.contracts.OperationalMetadata` --
Phase A of the Learning/Research Feedback implementation (``IMPLEMENTATION_DEFINITION_OF_DONE.md``).

Deliberately does NOT modify ``tests/_fixtures.py`` (Phase A's own explicit non-scope: "Any existing
test fixture") -- a local ``_make_operational_metadata`` helper is defined here instead, built on top of
the existing, unmodified ``make_observation``/``compute_observation_id``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.context_memory.contracts import OperationalMetadata, OperationalMetadataId
from ai_trader.context_memory.enums import ContextRiskDecision, OutcomeKind, SourceType
from ai_trader.context_memory.identities import compute_observation_id, compute_operational_metadata_id
from ai_trader.context_memory.repository import ContextMemoryRepository
from ai_trader.context_memory.validation import ContextMemoryValidationError
from ai_trader.context_memory.tests._fixtures import make_observation


def _make_operational_metadata(**overrides: object) -> OperationalMetadata:
    observation_id = overrides.pop("observation_id", None) or compute_observation_id(make_observation())
    kwargs: dict[str, object] = {
        "observation_id": observation_id,
        "strategy_id": "S1",
        "risk_decision": ContextRiskDecision.ALLOW,
        "denied_reason_code": None,
        "rejection_stage": None,
        "strategy_health_policy_state": "ACTIVE",
    }
    kwargs.update(overrides)
    return OperationalMetadata(**kwargs)  # type: ignore[arg-type]


# ------------------------------------------------------------------ new enums (OutcomeKind, SourceType)


def test_outcome_kind_values() -> None:
    assert {m.value for m in OutcomeKind} == {"STRATEGY", "PORTFOLIO"}


def test_source_type_gains_real_portfolio_ledger_member() -> None:
    assert {m.value for m in SourceType} == {
        "PRICE_ONLY", "SHADOW_EVIDENCE_ADAPTER", "REAL_PORTFOLIO_LEDGER",
    }


def test_context_risk_decision_values() -> None:
    assert {m.value for m in ContextRiskDecision} == {"ALLOW", "DENY"}


# ------------------------------------------------------------------ construction (unit)


def test_valid_allow_construction() -> None:
    metadata = _make_operational_metadata(risk_decision=ContextRiskDecision.ALLOW, denied_reason_code=None)
    assert metadata.risk_decision is ContextRiskDecision.ALLOW
    assert metadata.denied_reason_code is None


def test_valid_deny_construction() -> None:
    metadata = _make_operational_metadata(
        risk_decision=ContextRiskDecision.DENY,
        denied_reason_code="LIMIT_MAX_PER_SYMBOL",
        rejection_stage="portfolio_limit",
    )
    assert metadata.risk_decision is ContextRiskDecision.DENY
    assert metadata.denied_reason_code == "LIMIT_MAX_PER_SYMBOL"


def test_invalid_allow_with_reason_code_raises() -> None:
    with pytest.raises(ContextMemoryValidationError):
        _make_operational_metadata(
            risk_decision=ContextRiskDecision.ALLOW, denied_reason_code="SIZE_BELOW_MIN",
        )


def test_invalid_deny_without_reason_code_raises() -> None:
    with pytest.raises(ContextMemoryValidationError):
        _make_operational_metadata(risk_decision=ContextRiskDecision.DENY, denied_reason_code=None)


def test_wrong_type_observation_id_raises() -> None:
    with pytest.raises(ContextMemoryValidationError):
        _make_operational_metadata(observation_id="not-an-observation-id")


def test_wrong_type_risk_decision_raises() -> None:
    with pytest.raises(ContextMemoryValidationError):
        _make_operational_metadata(risk_decision="ALLOW")  # raw str, not the enum


def test_empty_strategy_id_raises() -> None:
    with pytest.raises(ContextMemoryValidationError):
        _make_operational_metadata(strategy_id="")


# ------------------------------------------------------------------ identity determinism


def test_identical_input_produces_identical_id() -> None:
    observation_id = compute_observation_id(make_observation())
    a = _make_operational_metadata(observation_id=observation_id)
    b = _make_operational_metadata(observation_id=observation_id)
    assert compute_operational_metadata_id(a) == compute_operational_metadata_id(b)


def test_different_input_produces_different_id() -> None:
    observation_id = compute_observation_id(make_observation())
    allow = _make_operational_metadata(observation_id=observation_id, strategy_id="S1")
    deny = _make_operational_metadata(
        observation_id=observation_id, strategy_id="S1",
        risk_decision=ContextRiskDecision.DENY, denied_reason_code="LIMIT_MAX_PER_SYMBOL",
    )
    assert compute_operational_metadata_id(allow) != compute_operational_metadata_id(deny)


# ------------------------------------------------------------------ repository round-trip (integration)


def _repo(tmp_path: Path) -> ContextMemoryRepository:
    return ContextMemoryRepository(tmp_path / "repo")


def test_append_and_retrieve_round_trip(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    metadata = _make_operational_metadata()
    record_id = repo.append_operational_metadata(metadata)
    assert record_id == compute_operational_metadata_id(metadata)
    assert repo.get_operational_metadata(record_id) == metadata
    assert repo.count_operational_metadata() == 1


def test_repeated_exact_append_is_idempotent(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    metadata = _make_operational_metadata()
    first = repo.append_operational_metadata(metadata)
    second = repo.append_operational_metadata(metadata)
    assert first == second
    assert repo.count_operational_metadata() == 1  # no second line written


def test_batch_append_preserves_order(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    observation_id = compute_observation_id(make_observation())
    items = [
        _make_operational_metadata(observation_id=observation_id, strategy_id=f"S{i}")
        for i in range(3)
    ]
    ids = repo.append_operational_metadatas(items)
    assert ids == tuple(compute_operational_metadata_id(m) for m in items)
    assert repo.count_operational_metadata() == 3
    assert list(repo.iter_operational_metadata()) == items


def test_survives_repository_rebuild(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    metadata = _make_operational_metadata()
    record_id = repo.append_operational_metadata(metadata)
    repo.rebuild()
    assert repo.get_operational_metadata(record_id) == metadata
    assert repo.count_operational_metadata() == 1


def test_operational_metadata_isolated_from_other_streams(tmp_path: Path) -> None:
    # OperationalMetadata is diagnostic-only -- appending it must never affect the other three streams.
    repo = _repo(tmp_path)
    repo.append_operational_metadata(_make_operational_metadata())
    assert repo.count_context_snapshots() == 0
    assert repo.count_observations() == 0
    assert repo.count_outcomes() == 0
