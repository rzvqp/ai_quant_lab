"""Edge Intelligence -- Phase 7 Checkpoint 6.

Answers: "Which validated statistical edges currently exist in the market?" -- for every
registered production strategy, independently. This is the recognition layer, not a decision
layer: it never chooses a trade, never scores, never ranks, never optimizes. See
:mod:`ai_trader.edge_intelligence.engine` for the single public entry point.
"""

from __future__ import annotations
