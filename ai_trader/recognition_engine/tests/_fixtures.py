"""Shared fixture builders for Recognition Engine Phase 1A tests. A local copy of Context Memory's own
established `make_snapshot`/`make_observation` pattern (`context_memory/tests/_fixtures.py`,
`decision_intelligence_v2/tests/_fixtures.py`) -- each package keeps its own local test fixtures, the
established precedent in this repository, rather than a cross-package test import.
"""

from __future__ import annotations

from pathlib import Path

from ai_trader.context_memory.contracts import (
    ContextSnapshot,
    EdgeEvidenceId,
    InterimRealizationId,
    Observation,
    ObservationId,
    Outcome,
    PositionOutcome,
    PresentEdgeReference,
    SchemaVersion,
)
from ai_trader.context_memory.enums import (
    ContextAgreementLevel,
    ContextDataQualityState,
    ContextEdgeStatus,
    ContextExpansionState,
    ContextLiquidityState,
    ContextMomentumState,
    ContextStructureState,
    ContextTrendDirection,
    ContextVolatilityRegime,
    HorizonUnit,
    OutcomeKind,
    OutcomeStatus,
    SourceType,
)
from ai_trader.context_memory.repository import ContextMemoryRepository

AS_OF = 1_700_000_000


def make_snapshot(**overrides: object) -> ContextSnapshot:
    kwargs: dict[str, object] = {
        "instrument": "XAUUSD", "as_of": AS_OF, "session_state": "LONDON",
        "trend_m15": ContextTrendDirection.UP, "trend_h1": ContextTrendDirection.UP,
        "trend_h4": ContextTrendDirection.UP, "trend_d1": ContextTrendDirection.UP,
        "structure_state": ContextStructureState.BULLISH_BOS,
        "momentum_m15": ContextMomentumState.NEUTRAL, "momentum_h1": ContextMomentumState.NEUTRAL,
        "momentum_h4": ContextMomentumState.NEUTRAL, "momentum_d1": ContextMomentumState.NEUTRAL,
        "volatility_regime": ContextVolatilityRegime.NORMAL, "liquidity_state": ContextLiquidityState.NORMAL,
        "expansion_state": ContextExpansionState.NORMAL,
        "multi_timeframe_agreement": ContextAgreementLevel.STRONG, "context_confidence_score": 0.85,
        "data_quality_state": ContextDataQualityState.OK,
    }
    kwargs.update(overrides)
    return ContextSnapshot(**kwargs)  # type: ignore[arg-type]


def make_edge_reference(strategy_id: str = "S1", **overrides: object) -> PresentEdgeReference:
    kwargs: dict[str, object] = {
        "strategy_id": strategy_id,
        "contract_version": SchemaVersion(namespace="strategy_contract", version="1.0.0"),
        "edge_intelligence_schema_version": SchemaVersion(namespace="edge_intelligence", version="ei-v1"),
        "declared_status": ContextEdgeStatus.PRESENT,
    }
    kwargs.update(overrides)
    return PresentEdgeReference(**kwargs)  # type: ignore[arg-type]


def make_observation(strategy_id: str = "S1", **overrides: object) -> Observation:
    kwargs: dict[str, object] = {
        "context_snapshot": make_snapshot(), "present_edges": (make_edge_reference(strategy_id),),
    }
    kwargs.update(overrides)
    return Observation(**kwargs)  # type: ignore[arg-type]


def make_outcome(observation_id: ObservationId, strategy_id: str = "S1", **overrides: object) -> Outcome:
    kwargs: dict[str, object] = {
        "observation_id": observation_id, "strategy_id": strategy_id, "horizon": 20,
        "horizon_unit": HorizonUnit.BARS,
        "outcome_definition_version": SchemaVersion(namespace="outcome_definition", version="od-v1"),
        "status": OutcomeStatus.RESOLVED, "observation_as_of": AS_OF, "normalized_result": 1.0,
        "resolution_as_of": AS_OF + 900, "cost_model_ref": "GROSS_NO_COSTS",
        "source_type": SourceType.SHADOW_EVIDENCE_ADAPTER, "outcome_kind": OutcomeKind.STRATEGY,
        "unavailable_reason": None,
    }
    kwargs.update(overrides)
    return Outcome(**kwargs)  # type: ignore[arg-type]


def make_position_outcome(
    observation_id: ObservationId, strategy_id: str = "S1", terminal_outcome_id: EdgeEvidenceId | None = None,
    **overrides: object,
) -> PositionOutcome:
    kwargs: dict[str, object] = {
        "observation_id": observation_id, "strategy_id": strategy_id,
        "position_key": f"TEST-RUN:XAUUSD:{AS_OF}:LONG", "outcome_kind": OutcomeKind.STRATEGY,
        "source_type": SourceType.SHADOW_EVIDENCE_ADAPTER, "opened_as_of": AS_OF,
        "terminal_as_of": AS_OF + 900, "total_qty_closed": 1.0, "weighted_avg_exit_price": 2000.0,
        "total_gross_pnl": 1.0, "total_net_pnl": 1.0, "total_costs": 0.0, "cost_model_ref": "GROSS_NO_COSTS",
        "terminal_outcome_id": terminal_outcome_id or EdgeEvidenceId("t" * 64),
        "constituent_interim_realization_ids": (),
    }
    kwargs.update(overrides)
    return PositionOutcome(**kwargs)  # type: ignore[arg-type]


def build_repository(
    tmp_path: Path, records: list[dict[str, object]],
) -> ContextMemoryRepository:
    """Builds a real, on-disk `ContextMemoryRepository` (tmp_path-scoped) from a list of record specs.
    Each dict may override any `make_snapshot`/`make_observation`/`make_outcome`/`make_position_outcome`
    keyword, plus `strategy_id`, `outcome_kind`, `result` (-> `total_net_pnl`/`total_gross_pnl`), and
    `snapshot_overrides` (a nested dict passed to `make_snapshot`). One full (Observation, Outcome,
    PositionOutcome) triple is appended per record spec, using the repository's own real, unmodified
    public write API -- exactly how production code populates it."""
    repo = ContextMemoryRepository(tmp_path / "repo")
    for i, spec in enumerate(records):
        strategy_id = str(spec.get("strategy_id", "S1"))
        outcome_kind_obj = spec.get("outcome_kind", OutcomeKind.STRATEGY)
        assert isinstance(outcome_kind_obj, OutcomeKind)
        outcome_kind = outcome_kind_obj
        source_type = (
            SourceType.SHADOW_EVIDENCE_ADAPTER if outcome_kind is OutcomeKind.STRATEGY
            else SourceType.REAL_PORTFOLIO_LEDGER
        )
        result = float(spec.get("result", 1.0))  # type: ignore[arg-type]
        as_of = AS_OF + i * 10_000
        raw_overrides = spec.get("snapshot_overrides", {})
        assert isinstance(raw_overrides, dict)
        snapshot_overrides: dict[str, object] = dict(raw_overrides)
        snapshot_overrides.setdefault("as_of", as_of)
        observation = make_observation(
            strategy_id=strategy_id, context_snapshot=make_snapshot(**snapshot_overrides),
            present_edges=(make_edge_reference(strategy_id),),
        )
        observation_id = repo.append_observation(observation)
        outcome = make_outcome(
            observation_id, strategy_id=strategy_id, outcome_kind=outcome_kind, source_type=source_type,
            observation_as_of=as_of, resolution_as_of=as_of + 900, normalized_result=result,
        )
        outcome_id = repo.append_outcome(outcome)
        position_outcome = make_position_outcome(
            observation_id, strategy_id=strategy_id, outcome_kind=outcome_kind, source_type=source_type,
            terminal_outcome_id=outcome_id, opened_as_of=as_of, terminal_as_of=as_of + 900,
            total_gross_pnl=result, total_net_pnl=result,
            position_key=f"TEST-RUN:XAUUSD:{as_of}:LONG",
        )
        repo.append_position_outcome(position_outcome)
    return repo
