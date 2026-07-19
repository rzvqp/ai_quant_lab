"""Shared fixture builders for Context Memory unit tests."""

from __future__ import annotations

from ai_trader.context_memory.contracts import (
    ContextSnapshot,
    Observation,
    Outcome,
    ObservationId,
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
    OutcomeStatus,
    SourceType,
)

AS_OF = 1_700_000_000


def make_snapshot(**overrides: object) -> ContextSnapshot:
    kwargs: dict[str, object] = {
        "instrument": "XAUUSD",
        "as_of": AS_OF,
        "session_state": "LONDON",
        "trend_m15": ContextTrendDirection.UP,
        "trend_h1": ContextTrendDirection.UP,
        "trend_h4": ContextTrendDirection.UP,
        "trend_d1": ContextTrendDirection.UP,
        "structure_state": ContextStructureState.BULLISH_BOS,
        "momentum_m15": ContextMomentumState.NEUTRAL,
        "momentum_h1": ContextMomentumState.NEUTRAL,
        "momentum_h4": ContextMomentumState.NEUTRAL,
        "momentum_d1": ContextMomentumState.NEUTRAL,
        "volatility_regime": ContextVolatilityRegime.NORMAL,
        "liquidity_state": ContextLiquidityState.NORMAL,
        "expansion_state": ContextExpansionState.NORMAL,
        "multi_timeframe_agreement": ContextAgreementLevel.STRONG,
        "context_confidence_score": 0.85,
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


def make_observation(**overrides: object) -> Observation:
    kwargs: dict[str, object] = {
        "context_snapshot": make_snapshot(),
        "present_edges": (make_edge_reference("S1"),),
    }
    kwargs.update(overrides)
    return Observation(**kwargs)  # type: ignore[arg-type]


def make_pending_outcome(observation_id: ObservationId, **overrides: object) -> Outcome:
    kwargs: dict[str, object] = {
        "observation_id": observation_id,
        "strategy_id": "S1",
        "horizon": 20,
        "horizon_unit": HorizonUnit.BARS,
        "outcome_definition_version": SchemaVersion(namespace="outcome_definition", version="od-v1"),
        "status": OutcomeStatus.PENDING,
        "observation_as_of": AS_OF,
        "normalized_result": None,
        "resolution_as_of": None,
        "cost_model_ref": "GROSS_NO_COSTS",
        "source_type": SourceType.PRICE_ONLY,
    }
    kwargs.update(overrides)
    return Outcome(**kwargs)  # type: ignore[arg-type]
