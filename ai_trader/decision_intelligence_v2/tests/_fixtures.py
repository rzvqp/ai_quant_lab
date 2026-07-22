"""Shared fixture builders for Decision Intelligence v2 unit tests."""

from __future__ import annotations

from ai_trader.context_memory import ContextMemoryRepository, EvidencePolicy, HistoricalIndex
from ai_trader.context_memory.contracts import Observation, Outcome, PresentEdgeReference, SchemaVersion
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
from ai_trader.context_memory.contracts import ContextSnapshot
from ai_trader.market_intelligence.types import (
    AgreementLevel,
    ContextConfidence,
    ExpansionReading,
    ExpansionState,
    LiquidityReading,
    LiquidityState,
    MarketIntelligenceSnapshot,
    MomentumReading,
    MomentumState,
    MultiTimeframeAgreement,
    SessionReading,
    StructureReading,
    StructureState,
    TrendDirection,
    TrendReading,
    VolatilityReading,
    VolatilityRegime,
)

AS_OF = 1_700_000_000


def make_mi_snapshot(symbol: str = "XAUUSD", as_of: int = AS_OF, **overrides: object) -> MarketIntelligenceSnapshot:
    trend = {
        tf: TrendReading(timeframe=tf, direction=TrendDirection.UP, strength=0.01 if tf == "M15" else None)
        for tf in ("M15", "H1", "H4", "D1")
    }
    momentum = {
        tf: MomentumReading(timeframe=tf, rsi=55.0, state=MomentumState.NEUTRAL, rate_of_change=0.001 if tf == "M15" else None)
        for tf in ("M15", "H1", "H4", "D1")
    }
    kwargs: dict[str, object] = {
        "symbol": symbol,
        "as_of": as_of,
        "trend": trend,
        "momentum": momentum,
        "structure": StructureReading(timeframe="M15", state=StructureState.BULLISH_BOS, last_swing_high=None, last_swing_low=None),
        "volatility": VolatilityReading(atr=1.0, atr_ma=1.0, atr_ratio=1.0, volatility_rank=0.5, regime=VolatilityRegime.NORMAL),
        "liquidity": LiquidityReading(volume=100.0, avg_volume=100.0, volume_ratio=1.0, state=LiquidityState.NORMAL),
        "expansion": ExpansionReading(state=ExpansionState.NORMAL, is_compressed=False, is_displacement=False),
        "session": SessionReading(session_name="LONDON", bar_in_session=5, inside_opening_range=False, above_session_vwap=True, gap=0.0),
        "multi_timeframe_agreement": MultiTimeframeAgreement(
            directions_by_timeframe={tf: TrendDirection.UP for tf in ("M15", "H1", "H4", "D1")},
            agreement_score=1.0, level=AgreementLevel.STRONG,
        ),
        "confidence": ContextConfidence(score=0.8, data_quality_ok=True, agreement_component=1.0, volatility_penalty=0.0),
    }
    kwargs.update(overrides)
    return MarketIntelligenceSnapshot(**kwargs)  # type: ignore[arg-type]


def make_cm_snapshot(**overrides: object) -> ContextSnapshot:
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
        "context_confidence_score": 0.8,
        "data_quality_state": ContextDataQualityState.OK,
    }
    kwargs.update(overrides)
    return ContextSnapshot(**kwargs)  # type: ignore[arg-type]


def build_populated_index(tmp_path, strategy_id: str = "S1", n_episodes: int = 30, result: float = 1.0) -> HistoricalIndex:
    """A small, synthetic, but real `ContextMemoryRepository` -- `n_episodes` distinct sessions (each
    its own episode, matching `make_cm_snapshot`'s own default dimensions at every relaxed-session tier)
    each with one strongly-signed RESOLVED outcome for `strategy_id`."""
    repo = ContextMemoryRepository(tmp_path / "cm_repo")
    ref = PresentEdgeReference(
        strategy_id=strategy_id, contract_version=SchemaVersion("strategy_contract", "1.0.0"),
        edge_intelligence_schema_version=SchemaVersion("edge_intelligence", "ei-v1"),
        declared_status=ContextEdgeStatus.PRESENT,
    )
    for i in range(n_episodes):
        snap = make_cm_snapshot(as_of=AS_OF - (n_episodes - i) * 1000, session_state=f"SESSION_{i}")
        obs = Observation(context_snapshot=snap, present_edges=(ref,))
        obs_id = repo.append_observation(obs)
        repo.append_outcome(
            Outcome(
                observation_id=obs_id, strategy_id=strategy_id, horizon=20, horizon_unit=HorizonUnit.BARS,
                outcome_definition_version=SchemaVersion("outcome_definition", "od-v1"), status=OutcomeStatus.RESOLVED,
                observation_as_of=snap.as_of, normalized_result=result, resolution_as_of=snap.as_of + 10,
                cost_model_ref="GROSS_NO_COSTS", source_type=SourceType.SHADOW_EVIDENCE_ADAPTER,
                outcome_kind=OutcomeKind.STRATEGY,
            )
        )
    return HistoricalIndex(repo)
