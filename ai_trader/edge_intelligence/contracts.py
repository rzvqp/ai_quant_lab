"""Read-only strategy contract loading -- Phase 7 Checkpoint 6. A thin wrapper reusing
:func:`ai_trader.strategy_manager.loader.load_all` directly -- never :class:`StrategyManager`
itself, since Edge Intelligence needs no Market Scanner handshake and none of the Manager's
lifecycle/health/admission machinery, only the already-parsed, already schema-validated
:class:`~ai_trader.strategy_manager.contract.Contract` each ``strategy.json`` declares. Nothing in
the Strategy Library is ever written to (the Loader's own read-only invariant, unchanged here).
"""

from __future__ import annotations

from pathlib import Path

from ai_trader.strategy_manager import loader
from ai_trader.strategy_manager.config import DEFAULT_LIBRARY_PATH
from ai_trader.strategy_manager.contract import Contract


def load_strategy_contracts(library_path: Path | None = None) -> dict[str, Contract]:
    """Every successfully-parsed, schema-valid Contract in the Strategy Library, keyed by strategy
    id. A ``strategy.json`` that fails to parse/validate is silently excluded here -- the Loader's
    own classified failure reasons are Strategy Manager's concern, not this read-only layer's;
    Edge Intelligence simply has no evidence for a strategy it cannot read (never a fabricated
    reading)."""
    path = library_path if library_path is not None else DEFAULT_LIBRARY_PATH
    outcomes = loader.load_all(path)
    return {
        outcome.id: outcome.contract
        for outcome in outcomes
        if outcome.ok and outcome.id is not None and outcome.contract is not None
    }
