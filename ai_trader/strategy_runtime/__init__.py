"""Strategy Runtime -- Phase 6.8: real, per-strategy Strategy API evaluators for the migrated
Strategy Library, composed into the live pipeline via ``ai_trader.signal_engine``'s own structural
``StrategyHandleLike``/``StrategyApiLike`` Protocols. Additive only: no file under
``ai_trader/strategy_manager/``, ``ai_trader/signal_engine/``, or any other frozen pipeline module is
modified by this package. See ``PHASE_6_8_IMPLEMENTATION_NOTES.md`` (repo root) for the full design.
"""

from __future__ import annotations
