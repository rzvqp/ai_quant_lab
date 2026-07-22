"""Market snapshot orchestration -- Learning/Research Feedback Phase F, Architectural Decision Package
Decision 4 (Option C, resolving Finding A): a small, single-purpose seam that calls REAL, unmodified
Market Intelligence / Edge Intelligence exactly once per ``(symbol, as_of)`` and hands the result to
:mod:`ai_trader.learning_feedback.observation_builder`. Never fabricates, never degrades -- both
``build_market_intelligence``/``evaluate_edges`` are confirmed pure, stateless, deterministic functions of
the SAME ``MarketContext`` dict ``harness.py`` already has in hand per symbol per bar (Architectural
Decision Package §1: ``market_intelligence/engine.py``'s own docstring -- "Deliberately not wired into any
live per-bar loop... calling it changes nothing about how the market context was produced or how any other
module behaves").

**This is genuinely new wiring, disclosed**: nothing in this repository previously called Market
Intelligence or Edge Intelligence from a live per-bar loop -- both were, until now, standalone libraries
reachable only from ``decision_intelligence_v2`` (a read-only, execution-independent explain-a-decision
tool with no production caller). This module is the first real production consumer; it does not modify
``market_intelligence``/``edge_intelligence`` themselves, and it feeds ONLY ``learning_feedback`` (never
Signal Engine, Scoring Engine, Risk Manager, Shadow Evidence, or Execution Engine) -- Context Memory's
evidence never feeds back into eligibility, ranking, scoring, sizing, or execution, exactly the same
guarantee ``decision_intelligence_v2`` itself already makes.

**Disclosed, deliberately accepted inefficiency**: ``evaluate_edges`` (``edge_intelligence/engine.py``)
already calls ``build_market_intelligence`` internally and does not expose the snapshot it computed --
calling both functions here computes Market Intelligence TWICE per ``(symbol, as_of)``. The alternative --
reimplementing ``evaluate_edges``'s own internal composition here to reuse a single snapshot -- would
duplicate business logic that must then be kept in permanent lockstep with ``edge_intelligence/engine.py``'s
own recipe, exactly the class of maintenance-coupling risk the Architectural Decision Package already
rejected for Decision 1's Option B. Given both functions are confirmed pure/stateless/CPU-only (no I/O,
no network), this is a bounded, disclosed performance cost, never a correctness risk.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_trader.edge_intelligence.engine import evaluate_edges
from ai_trader.edge_intelligence.types import EdgeIntelligenceSnapshot
from ai_trader.market_intelligence.engine import build_market_intelligence
from ai_trader.market_intelligence.types import MarketIntelligenceSnapshot
from ai_trader.strategy_runtime.context_access import MarketContext


@dataclass(frozen=True)
class MarketSnapshotBundle:
    """One ``(symbol, as_of)``'s worth of real, non-degraded Market Intelligence + Edge Intelligence
    output -- the sole input :mod:`ai_trader.learning_feedback.observation_builder` accepts."""

    mi_snapshot: MarketIntelligenceSnapshot
    ei_snapshot: EdgeIntelligenceSnapshot


def build_market_snapshot(context: MarketContext, library_path: Path | None = None) -> MarketSnapshotBundle:
    """The one, single call site for producing a real ``(MarketIntelligenceSnapshot,
    EdgeIntelligenceSnapshot)`` pair for one ``(symbol, as_of)`` -- never a fabricated, empty, or
    degraded substitute (CEO's own explicit instruction, Architectural Decision Package Decision 4).

    Both calls are pure functions of ``context`` alone. This function is deliberately NOT defense-in-depth
    wrapped, unlike ``capture.py``'s own public functions -- a genuine failure here (e.g. a malformed
    ``MarketContext``) indicates a real upstream data problem the caller needs to see, not a routine
    "nothing to correlate" case."""
    mi_snapshot = build_market_intelligence(context)
    ei_snapshot = evaluate_edges(context, library_path)
    return MarketSnapshotBundle(mi_snapshot=mi_snapshot, ei_snapshot=ei_snapshot)
