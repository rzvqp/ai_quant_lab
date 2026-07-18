"""Momentum analysis -- Phase 7 Checkpoint 5. Reuses `market_scanner/features.py`'s own frozen RSI(14)
(``{tf}_rsi``, Wilder's method) and M15's own 3-bar rate of change (``roc3``) verbatim -- no new
indicator computed here.
"""

from __future__ import annotations

from ai_trader.market_intelligence.trend import TREND_TIMEFRAMES
from ai_trader.market_intelligence.types import MomentumReading, MomentumState
from ai_trader.strategy_runtime import context_access
from ai_trader.strategy_runtime.context_access import MarketContext

#: IMPLEMENTATION CHOICE: the standard, well-established 70/30 RSI overbought/oversold convention
#: (never tuned against results) -- the same bands this project's own strategy families already
#: reference informally via raw `m_rsi`/`h1_rsi` reads.
_OVERBOUGHT_THRESHOLD = 70.0
_OVERSOLD_THRESHOLD = 30.0


def _momentum_state(rsi: float | None) -> MomentumState:
    if rsi is None:
        return MomentumState.UNKNOWN
    if rsi >= _OVERBOUGHT_THRESHOLD:
        return MomentumState.OVERBOUGHT
    if rsi <= _OVERSOLD_THRESHOLD:
        return MomentumState.OVERSOLD
    return MomentumState.NEUTRAL


def analyze_momentum_m15(context: MarketContext) -> MomentumReading:
    rsi = context_access.feature(context, "m_rsi", "M15")
    roc = context_access.feature(context, "roc3", "M15")
    return MomentumReading(timeframe="M15", rsi=rsi, state=_momentum_state(rsi), rate_of_change=roc)


def analyze_momentum_higher_timeframe(context: MarketContext, timeframe: str) -> MomentumReading:
    """H1/H4/D1: only ``{tf}_rsi`` is available -- ``rate_of_change`` is always ``None`` here (``roc3``
    is an M15-only feature, never fabricated for other timeframes)."""
    rsi = context_access.feature(context, f"{timeframe.lower()}_rsi", "M15")
    return MomentumReading(timeframe=timeframe, rsi=rsi, state=_momentum_state(rsi), rate_of_change=None)


def analyze_momentum(context: MarketContext) -> dict[str, MomentumReading]:
    readings: dict[str, MomentumReading] = {"M15": analyze_momentum_m15(context)}
    for timeframe in TREND_TIMEFRAMES[1:]:
        readings[timeframe] = analyze_momentum_higher_timeframe(context, timeframe)
    return readings
