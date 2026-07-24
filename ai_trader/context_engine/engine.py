"""`build_context_snapshot` -- Context Engine's single public entry point. Pure, read-only: reuses
`market_intelligence.build_market_intelligence` and `edge_intelligence.evaluate_edges` unmodified,
wraps their output with provenance/versioning/data-quality/staleness/calculation-trace. Never submits
an order, never computes a "final" confidence score, never reaches outside the passed-in `context`
(no wall-clock, no look-ahead -- inherited from the reused analyzers it calls)."""

from __future__ import annotations

from pathlib import Path

from ai_trader.context_engine.types import (
    CONTEXT_ENGINE_SCHEMA_VERSION,
    CalculationTraceStep,
    MarketContextSnapshot,
    Provenance,
)
from ai_trader.context_memory.contracts import EDGE_INTELLIGENCE_SCHEMA_VERSION, MARKET_INTELLIGENCE_SCHEMA_VERSION
from ai_trader.edge_intelligence.engine import evaluate_edges
from ai_trader.market_intelligence.engine import build_market_intelligence
from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.strategy_runtime import context_access
from ai_trader.strategy_runtime.context_access import MarketContext

_DATA_QUALITY_BY_LEVEL = {level.value: level for level in DataQualityLevel}


def build_context_snapshot(
    context: MarketContext, strategy_library_path: Path | None = None,
) -> MarketContextSnapshot:
    trace: list[CalculationTraceStep] = []
    symbol = context_access.symbol(context)
    as_of = context_access.as_of(context)

    market_intelligence = None
    try:
        market_intelligence = build_market_intelligence(context)
        trace.append(CalculationTraceStep("MARKET_INTELLIGENCE_BUILT", True))
    except Exception as exc:  # noqa: BLE001 -- fail-closed: a read-only query must never raise past
        # its own boundary; a build failure is recorded, not propagated.
        trace.append(CalculationTraceStep("MARKET_INTELLIGENCE_BUILT", False, detail=f"{type(exc).__name__}: {exc}"))

    edge_intelligence = None
    try:
        edge_intelligence = evaluate_edges(context, strategy_library_path)
        trace.append(CalculationTraceStep("EDGE_INTELLIGENCE_BUILT", True))
    except Exception as exc:  # noqa: BLE001 -- same fail-closed discipline as above.
        trace.append(CalculationTraceStep("EDGE_INTELLIGENCE_BUILT", False, detail=f"{type(exc).__name__}: {exc}"))

    raw_level = context_access.data_quality_level(context)
    data_quality = _DATA_QUALITY_BY_LEVEL.get(raw_level, DataQualityLevel.INSUFFICIENT)
    trace.append(CalculationTraceStep(
        "DATA_QUALITY_RESOLVED", data_quality is DataQualityLevel.OK, detail=f"level={raw_level}",
    ))
    if market_intelligence is None:
        data_quality = DataQualityLevel.INSUFFICIENT

    is_stale = data_quality is DataQualityLevel.STALE
    trace.append(CalculationTraceStep("STALE_CHECK", not is_stale, detail=f"data_quality={data_quality.value}"))

    provenance = Provenance(source_schema_versions={
        "market_intelligence": MARKET_INTELLIGENCE_SCHEMA_VERSION,
        "edge_intelligence": EDGE_INTELLIGENCE_SCHEMA_VERSION,
    })

    return MarketContextSnapshot(
        symbol=symbol, as_of=as_of, version=CONTEXT_ENGINE_SCHEMA_VERSION,
        market_intelligence=market_intelligence, edge_intelligence=edge_intelligence,
        data_quality=data_quality, is_stale=is_stale, provenance=provenance,
        calculation_trace=tuple(trace),
    )
