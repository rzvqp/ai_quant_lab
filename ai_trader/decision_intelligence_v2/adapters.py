"""Live-snapshot -> Context Memory adapters -- Phase 7 Checkpoint 14.

Context Memory (`ai_trader.context_memory`) deliberately has ZERO import dependency on
`market_intelligence`/`edge_intelligence` (Checkpoint 9's own design choice -- every controlled
vocabulary it needs is a LOCAL, canonically-serialized mirror). Something has to bridge a REAL,
already-computed `MarketIntelligenceSnapshot`/`EdgeIntelligenceSnapshot` into Context Memory's own local
`ContextSnapshot`/`PresentEdgeReference` types -- `PresentEdgeReference`'s own docstring names this
exact responsibility: "a future adapter that DOES have access to a real Contract is responsible for
supplying its version identity here." This module IS that adapter, and it lives here (in the consuming
`decision_intelligence_v2` package), never inside `context_memory` itself, preserving Context Memory's
own zero-import independence.

This module performs pure, lossless, deterministic translation only -- it invents no value, computes no
statistic, and makes no decision. Every field copied from a live snapshot maps to the SAME named field on
the Context Memory side; every enum value maps by its own `.value` string (both sides are `str`-valued
enums with identical member values, verified byte-exact at Checkpoint 9's own close).
"""

from __future__ import annotations

from ai_trader.context_memory import (
    EDGE_INTELLIGENCE_SCHEMA_VERSION,
    ContextAgreementLevel,
    ContextDataQualityState,
    ContextEdgeStatus,
    ContextExpansionState,
    ContextLiquidityState,
    ContextMomentumState,
    ContextSnapshot,
    ContextStructureState,
    ContextTrendDirection,
    ContextVolatilityRegime,
    PresentEdgeReference,
    SchemaVersion,
)
from ai_trader.edge_intelligence.types import EdgeState
from ai_trader.market_intelligence.types import MarketIntelligenceSnapshot
from ai_trader.strategy_manager.contract import Contract

_TIMEFRAMES = ("M15", "H1", "H4", "D1")


def build_context_snapshot(mi_snapshot: MarketIntelligenceSnapshot) -> ContextSnapshot:
    """Translate a real `MarketIntelligenceSnapshot` into a Context Memory `ContextSnapshot`. Every
    categorical dimension is copied verbatim by enum value; `data_quality_state` is derived from
    `ContextConfidence.data_quality_ok` (a bool is all Market Intelligence exposes at this layer -- the
    only two states reachable from it are OK/DEGRADED, never STALE/INSUFFICIENT, a disclosed narrowing,
    not a fabrication)."""
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


def build_present_edge_reference(strategy_id: str, contract: Contract) -> PresentEdgeReference:
    """One `PresentEdgeReference` for a strategy Edge Intelligence classified PRESENT. `contract_version`
    is sourced from the strategy's own already-declared `Contract.interface_version` -- never invented."""
    return PresentEdgeReference(
        strategy_id=strategy_id,
        contract_version=SchemaVersion("strategy_contract", contract.interface_version),
        edge_intelligence_schema_version=EDGE_INTELLIGENCE_SCHEMA_VERSION,
        declared_status=ContextEdgeStatus(EdgeState.PRESENT.value),
    )
