"""`build_context_snapshot` -- translates a live `MarketIntelligenceSnapshot` (Phase 6's own embedded
field) into `context_memory`'s local `ContextSnapshot`, the shape `recognition_engine`'s bucket-value
logic actually reads. Field-for-field IDENTICAL to the existing, already-approved
`ai_trader.decision_intelligence_v2.adapters.build_context_snapshot` -- deliberately DUPLICATED, not
imported, to avoid creating a dependency edge onto `decision_intelligence_v2` (excluded from every live
phase's own allow-list this session, since it belongs to the old scoring-engine-coupled batch pipeline).
Pure, lossless, deterministic translation only -- invents no value, computes no statistic."""

from __future__ import annotations

from ai_trader.context_memory import (
    ContextAgreementLevel,
    ContextDataQualityState,
    ContextExpansionState,
    ContextLiquidityState,
    ContextMomentumState,
    ContextSnapshot,
    ContextStructureState,
    ContextTrendDirection,
    ContextVolatilityRegime,
)
from ai_trader.market_intelligence.types import MarketIntelligenceSnapshot

_TIMEFRAMES = ("M15", "H1", "H4", "D1")


def build_context_snapshot(mi_snapshot: MarketIntelligenceSnapshot) -> ContextSnapshot:
    trend = {tf: mi_snapshot.trend[tf].direction for tf in _TIMEFRAMES}
    momentum = {tf: mi_snapshot.momentum[tf].state for tf in _TIMEFRAMES}

    return ContextSnapshot(
        instrument=mi_snapshot.symbol,
        as_of=mi_snapshot.as_of,
        session_state=mi_snapshot.session.session_name,
        trend_m15=ContextTrendDirection(trend["M15"].value),
        trend_h1=ContextTrendDirection(trend["H1"].value),
        trend_h4=ContextTrendDirection(trend["H4"].value),
        trend_d1=ContextTrendDirection(trend["D1"].value),
        structure_state=ContextStructureState(mi_snapshot.structure.state.value),
        momentum_m15=ContextMomentumState(momentum["M15"].value),
        momentum_h1=ContextMomentumState(momentum["H1"].value),
        momentum_h4=ContextMomentumState(momentum["H4"].value),
        momentum_d1=ContextMomentumState(momentum["D1"].value),
        volatility_regime=ContextVolatilityRegime(mi_snapshot.volatility.regime.value),
        liquidity_state=ContextLiquidityState(mi_snapshot.liquidity.state.value),
        expansion_state=ContextExpansionState(mi_snapshot.expansion.state.value),
        multi_timeframe_agreement=ContextAgreementLevel(mi_snapshot.multi_timeframe_agreement.level.value),
        context_confidence_score=mi_snapshot.confidence.score,
        data_quality_state=(
            ContextDataQualityState.OK if mi_snapshot.confidence.data_quality_ok else ContextDataQualityState.DEGRADED
        ),
    )
