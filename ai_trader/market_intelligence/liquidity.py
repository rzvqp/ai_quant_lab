"""Liquidity-behaviour analysis -- Phase 7 Checkpoint 5. Reuses the SAME raw bar-volume signal
``ai_trader.simulation.harness::_build_risk_context`` already reads as its own ``liquidity_proxy`` --
extended here with a simple rolling-average comparison (computed directly from the M15 bars already
present in the context, no new feature) for a genuine "behavior" read rather than one bar's own raw
value.
"""

from __future__ import annotations

from ai_trader.market_intelligence.types import LiquidityReading, LiquidityState
from ai_trader.strategy_runtime import context_access
from ai_trader.strategy_runtime.context_access import MarketContext

#: IMPLEMENTATION CHOICE: a 20-bar trailing average (matching this codebase's own established
#: ``m_sma``/``m_std`` window, `market_scanner/config.py::SMA_WINDOW`) -- not re-derived
#: independently.
_ROLLING_WINDOW = 20

#: IMPLEMENTATION CHOICE: purely descriptive bands (never tuned against results) -- volume more than
#: 50% below/above its own trailing average is THIN/THICK, otherwise NORMAL.
_THIN_BELOW = 0.5
_THICK_ABOVE = 1.5


def _state_for_ratio(ratio: float | None) -> LiquidityState:
    if ratio is None:
        return LiquidityState.UNKNOWN
    if ratio < _THIN_BELOW:
        return LiquidityState.THIN
    if ratio > _THICK_ABOVE:
        return LiquidityState.THICK
    return LiquidityState.NORMAL


def analyze_liquidity(context: MarketContext) -> LiquidityReading:
    last_bar = context_access.last_bar(context, "M15")
    volume = None
    if last_bar is not None:
        raw_volume = last_bar.get("volume")
        volume = float(raw_volume) if isinstance(raw_volume, (int, float)) else None

    recent_bars = context_access.bars(context, "M15")[-_ROLLING_WINDOW:]
    volumes = [
        float(bar["volume"]) for bar in recent_bars
        if isinstance(bar.get("volume"), (int, float))
    ]
    avg_volume = (sum(volumes) / len(volumes)) if volumes else None

    ratio = (volume / avg_volume) if volume is not None and avg_volume is not None and avg_volume > 0 else None
    return LiquidityReading(volume=volume, avg_volume=avg_volume, volume_ratio=ratio, state=_state_for_ratio(ratio))
