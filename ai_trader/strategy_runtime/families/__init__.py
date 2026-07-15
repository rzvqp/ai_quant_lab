"""Importing this package registers every implemented family evaluator (each module calls
``ai_trader.strategy_runtime.registry.register(strategy_id)`` at import time). Add a new
``import ai_trader.strategy_runtime.families.sNN_...`` line here for every strategy as its evaluator
is implemented -- this file is the single, auditable manifest of which strategies actually have real
runtime logic wired in.
"""

from __future__ import annotations

import ai_trader.strategy_runtime.families.s01_confirmed_liquidity_sweep_reversal  # noqa: F401
