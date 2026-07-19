"""Edge Intelligence public API -- Phase 7 Checkpoint 6. Answers: "which of the registered
strategies' statistical edges currently exist in the market?" Pure and read-only: composes the
already-built Market Intelligence snapshot with each strategy's own declared Contract -- never
strategy logic, never Signal/Scoring/Risk/Shadow/Research, never a trade decision.
"""

from __future__ import annotations

from pathlib import Path

from ai_trader.edge_intelligence.context import (
    evaluate_context_confidence,
    evaluate_multi_timeframe_agreement,
    evaluate_volatility_regime,
)
from ai_trader.edge_intelligence.contracts import load_strategy_contracts
from ai_trader.edge_intelligence.data_availability import evaluate_data_availability
from ai_trader.edge_intelligence.directional import evaluate_directional_alignment
from ai_trader.edge_intelligence.session import evaluate_session_suitability
from ai_trader.edge_intelligence.types import EdgeIntelligenceSnapshot, EdgeState, StrategyEdgeReading
from ai_trader.edge_intelligence.verdict import determine_edge_state
from ai_trader.market_intelligence.engine import build_market_intelligence
from ai_trader.strategy_runtime.context_access import MarketContext, as_of, symbol


def _registered_strategy_ids() -> frozenset[str]:
    """The full set of currently-registered production strategies (Strategy Runtime's own
    registry) -- no new strategy invented, no subset hand-picked. Imported inline (mirroring
    :func:`ai_trader.shadow_evidence.config.all_registered_strategies`'s own lazy-import pattern)
    so this module never depends on the ``shadow_evidence`` package at all."""
    import ai_trader.strategy_runtime.families  # noqa: F401 -- trigger every family's own @register(...)
    from ai_trader.strategy_runtime.registry import registered_strategy_ids

    return registered_strategy_ids()


def evaluate_edges(context: MarketContext, library_path: Path | None = None) -> EdgeIntelligenceSnapshot:
    """The single public entry point: "what edges are currently available?" -- one
    :class:`~ai_trader.edge_intelligence.types.StrategyEdgeReading` per strategy id both
    registered in the runtime and present in the Strategy Library with a valid Contract. A
    registered strategy whose contract cannot be read produces no reading at all -- never a
    fabricated one. "If twenty strategies are present, report twenty; if zero are present, report
    zero" applies to each reading's own :class:`~ai_trader.edge_intelligence.types.EdgeState`, not
    to how many strategies are evaluated -- every readable, registered strategy always gets a
    reading."""
    snapshot = build_market_intelligence(context)
    contracts = load_strategy_contracts(library_path)
    registered = _registered_strategy_ids()

    readings: dict[str, StrategyEdgeReading] = {}
    for strategy_id in sorted(registered & contracts.keys()):
        contract = contracts[strategy_id]
        evidence = (
            evaluate_data_availability(contract, context),
            evaluate_directional_alignment(contract, snapshot),
            evaluate_session_suitability(contract.execution.sessions, snapshot.session.session_name),
            evaluate_context_confidence(snapshot),
            evaluate_multi_timeframe_agreement(snapshot),
            evaluate_volatility_regime(snapshot),
        )
        readings[strategy_id] = StrategyEdgeReading(
            strategy_id=strategy_id, as_of=as_of(context), state=determine_edge_state(evidence), evidence=evidence,
        )

    return EdgeIntelligenceSnapshot(symbol=symbol(context), as_of=as_of(context), readings=readings)


def present_strategy_ids(snapshot: EdgeIntelligenceSnapshot) -> tuple[str, ...]:
    """Every strategy id whose edge is currently PRESENT, sorted -- the clean, execution-decoupled
    query surface future modules (Decision AI) are meant to call instead of inspecting
    ``snapshot.readings`` themselves."""
    return tuple(sorted(sid for sid, reading in snapshot.readings.items() if reading.state is EdgeState.PRESENT))
