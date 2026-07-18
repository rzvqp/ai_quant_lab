"""Trend analysis -- Phase 7 Checkpoint 5. A pure, deterministic function per timeframe, reusing
`market_scanner/features.py`'s own frozen, unmodified ``{tf}_trend_up`` boolean (EMA20 > EMA50) --
never recomputed, never a new indicator. M15 additionally exposes ``m_ema20``/``m_ema50`` as raw
values, letting this module compute a continuous strength and a ``FLAT`` band the other timeframes
cannot (disclosed in `types.py`'s own ``TrendDirection`` docstring).
"""

from __future__ import annotations

from ai_trader.market_intelligence.types import TrendDirection, TrendReading
from ai_trader.strategy_runtime import context_access
from ai_trader.strategy_runtime.context_access import MarketContext

#: IMPLEMENTATION CHOICE: an EMA20/EMA50 spread within +/-0.05% of price is treated as FLAT rather
#: than a directionless UP/DOWN -- a documented, conservative threshold (never tuned against
#: results), matching this codebase's own convention for undocumented numeric defaults
#: (`IMPLEMENTATION_CHOICES.md`'s own intro). M15 only -- see module docstring.
_FLAT_STRENGTH_THRESHOLD = 0.0005

#: Every timeframe `market_scanner` always assembles together in one MarketContext
#: (`market_scanner/config.py::DEFAULT_CONTEXT_TIMEFRAMES` + the base M15) that this module reads a
#: trend flag from.
TREND_TIMEFRAMES: tuple[str, ...] = ("M15", "H1", "H4", "D1")


def _direction_from_flag(trend_up: bool | None) -> TrendDirection:
    if trend_up is None:
        return TrendDirection.UNKNOWN
    return TrendDirection.UP if trend_up else TrendDirection.DOWN


def analyze_trend_m15(context: MarketContext) -> TrendReading:
    trend_up = context_access.flag(context, "m_trend_up", "M15")
    ema20 = context_access.feature(context, "m_ema20", "M15")
    ema50 = context_access.feature(context, "m_ema50", "M15")
    last_bar = context_access.last_bar(context, "M15")
    close = last_bar.get("close") if last_bar is not None else None

    strength: float | None = None
    if ema20 is not None and ema50 is not None and isinstance(close, (int, float)) and close != 0:
        strength = (ema20 - ema50) / float(close)

    direction = _direction_from_flag(trend_up)
    if direction is not TrendDirection.UNKNOWN and strength is not None and abs(strength) < _FLAT_STRENGTH_THRESHOLD:
        direction = TrendDirection.FLAT
    return TrendReading(timeframe="M15", direction=direction, strength=strength)


def analyze_trend_higher_timeframe(context: MarketContext, timeframe: str) -> TrendReading:
    """H1/H4/D1: only the boolean ``{tf}_trend_up`` flag is available -- ``strength`` is always
    ``None`` here (never fabricated from a boolean alone)."""
    feature_name = f"{timeframe.lower()}_trend_up"
    trend_up = context_access.flag(context, feature_name, "M15")  # h1_/h4_/d1_ features live on the M15 block
    return TrendReading(timeframe=timeframe, direction=_direction_from_flag(trend_up), strength=None)


def analyze_trend(context: MarketContext) -> dict[str, TrendReading]:
    """Every configured timeframe's own trend reading, keyed by timeframe name -- generic over
    :data:`TREND_TIMEFRAMES`, never hardcoded to fewer than what's actually available."""
    readings: dict[str, TrendReading] = {"M15": analyze_trend_m15(context)}
    for timeframe in TREND_TIMEFRAMES[1:]:
        readings[timeframe] = analyze_trend_higher_timeframe(context, timeframe)
    return readings
