"""Context Engine (Phase 6 -- `CONTEXT_ENGINE_PHASE6_DESIGN.md`). A thin, read-only wrapper over the
already-built `market_intelligence`/`edge_intelligence` engines: reuses their output unmodified, adds
provenance/versioning/data-quality/staleness/calculation-trace. Never submits an order, never computes a
"final" confidence score, never imports the MT5 terminal API or any execution/order/risk/portfolio
package (verified by dedicated static tests)."""

from __future__ import annotations

from ai_trader.context_engine.engine import build_context_snapshot
from ai_trader.context_engine.types import (
    CONTEXT_ENGINE_SCHEMA_VERSION,
    CalculationTraceStep,
    MarketContextSnapshot,
    Provenance,
)

__all__ = [
    "build_context_snapshot",
    "MarketContextSnapshot",
    "Provenance",
    "CalculationTraceStep",
    "CONTEXT_ENGINE_SCHEMA_VERSION",
]
