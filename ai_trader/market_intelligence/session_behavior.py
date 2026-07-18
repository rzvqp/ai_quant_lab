"""Session-behaviour analysis -- Phase 7 Checkpoint 5. Reuses `market_scanner/session.py`'s own
frozen ``SessionEngine`` output verbatim (session name, developing opening range, session VWAP, gap
vs. prior session close) -- this module only describes the CURRENT bar's own relationship to those
already-computed levels (inside/outside the opening range, above/below session VWAP); it computes no
new session logic.
"""

from __future__ import annotations

from ai_trader.market_intelligence.types import SessionReading
from ai_trader.strategy_runtime import context_access
from ai_trader.strategy_runtime.context_access import MarketContext


def analyze_session(context: MarketContext) -> SessionReading:
    name = context_access.session_name(context)
    bar_in_session = context_access.feature(context, "bar_in_sess", "M15")
    or_high = context_access.feature(context, "or_high", "M15")
    or_low = context_access.feature(context, "or_low", "M15")
    vwap = context_access.feature(context, "vwap", "M15")
    gap = context_access.feature(context, "gap", "M15")
    last_bar = context_access.last_bar(context, "M15")
    close = last_bar.get("close") if last_bar is not None else None
    close_value = float(close) if isinstance(close, (int, float)) else None

    inside_opening_range: bool | None = None
    if close_value is not None and or_high is not None and or_low is not None:
        inside_opening_range = or_low <= close_value <= or_high

    above_session_vwap: bool | None = None
    if close_value is not None and vwap is not None:
        above_session_vwap = close_value > vwap

    return SessionReading(
        session_name=name,
        bar_in_session=int(bar_in_session) if bar_in_session is not None else None,
        inside_opening_range=inside_opening_range,
        above_session_vwap=above_session_vwap,
        gap=gap,
    )
