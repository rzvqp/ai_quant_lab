"""Expansion vs. compression analysis -- Phase 7 Checkpoint 5. Reuses `market_scanner/features.py`'s
own frozen ``compress`` (ATR below 0.8x its own moving average) and ``disp`` (bar range above 1.5x
ATR) flags verbatim -- this module only labels the combined state; it computes nothing new.
"""

from __future__ import annotations

from ai_trader.market_intelligence.types import ExpansionReading, ExpansionState
from ai_trader.strategy_runtime import context_access
from ai_trader.strategy_runtime.context_access import MarketContext


def _state_for(is_compressed: bool | None, is_displacement: bool | None) -> ExpansionState:
    if is_compressed is None and is_displacement is None:
        return ExpansionState.UNKNOWN
    # A displacement bar (large range) inside an otherwise-compressed regime is still the more
    # informative, more recent signal -- EXPANDING takes priority over COMPRESSED when both are
    # somehow true at once (compress reflects the last 14-50 bars; disp reflects THIS bar).
    if is_displacement:
        return ExpansionState.EXPANDING
    if is_compressed:
        return ExpansionState.COMPRESSED
    return ExpansionState.NORMAL


def analyze_expansion(context: MarketContext) -> ExpansionReading:
    is_compressed = context_access.flag(context, "compress", "M15")
    is_displacement = context_access.flag(context, "disp", "M15")
    return ExpansionReading(
        state=_state_for(is_compressed, is_displacement),
        is_compressed=is_compressed, is_displacement=is_displacement,
    )
