"""Strategy Health System (CEO directive, 2026-07-16): a reusable, adaptive, rolling-window
performance evaluator for runtime strategies -- deliberately NOT part of the frozen six-module
pipeline, NOT a rewrite of any evaluator, and NOT a change to the Research Lab or to
``ai_trader.strategy_manager``'s own ``Health``/``Lifecycle`` concepts (those classify contract
schema-validity/compatibility and maturity-ladder progression; this module classifies TRADING
PERFORMANCE, a completely independent axis -- a strategy can be perfectly ``Lifecycle.PROMOTED`` and
schema-``Health.LOADED`` while this module rates it ``DISABLED`` for having traded badly recently,
or vice versa).

**Why this exists**: multi-year lifetime averages hide regime change -- a strategy strong in 2023 may
be weak now, and a strategy weak historically may fit the current regime well. This module scores
each strategy from its OWN recent trade history across three independent rolling windows (3/6/12
months), weighted toward the 12-month window as the primary signal (per explicit CEO direction) with
shorter windows supplying supporting/regime-adaptation evidence, and classifies it into one of four
states: ``ACTIVE``, ``WATCHLIST``, ``PROBATION``, ``DISABLED``. No strategy is ever deleted; states
are designed to be re-derived from scratch on every re-evaluation, so a strategy can move freely
between all four states as its own recent performance changes.

See ``types.py`` for the data model, ``metrics.py`` for the per-window statistics, ``scoring.py`` for
the (explicitly not-hardcoded-weight) composite Health Score derivation, ``classifier.py`` for the
score -> state mapping, and ``evaluator.py`` for the top-level orchestrator.
"""

from __future__ import annotations
