"""Portfolio Architect (roadmap Flow B step 2/6, ``PORTFOLIO_ARCHITECT_DESIGN.md``, CEO-ACCEPTED
COMPLETE; this package's own Phase 1 authorization: PASSTHROUGH SCAFFOLD ONLY).

Sits between Strategy Health's real-eligibility filter and the Risk Manager's own decision, in the
per-symbol per-bar loop (:mod:`ai_trader.simulation.harness`): it receives the ALREADY-scored (Scoring
Engine), ALREADY-observed-by-Shadow-Evidence, ALREADY-eligibility-filtered (Strategy Health) opportunity
set for one bar and returns an opportunity sequence for the Risk Manager to evaluate. In this Phase 1
scaffold the ONLY supported mode is :class:`~ai_trader.portfolio_architect.types.ArchitectMode.PASSTHROUGH`
-- the output is always exactly the input, unchanged, with an accompanying diagnostics record that is
never read by anything else in the pipeline. No allocation, correlation, sizing, exclusion, or ranking
policy is implemented here yet -- those are separate, later, CEO-approved phases (see the design
document's own §14 open decisions).

Frozen modules consumed, never modified: Signal Engine, Scoring Engine, Risk Manager, Execution Engine,
Strategy Manager, Strategy Health's five frozen modules, and ``strategy_health/shadow_gate.py``.
"""

from __future__ import annotations
