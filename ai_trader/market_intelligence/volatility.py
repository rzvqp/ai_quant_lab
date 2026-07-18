"""Volatility analysis -- Phase 7 Checkpoint 5. Reuses `market_scanner/features.py`'s own frozen
``m_atr``/``atr_ma`` (14-bar ATR / its own 50-bar moving average) and ``m_volrank`` (Parkinson-based
volatility percentile rank) verbatim -- no new indicator computed here. This module only classifies
the ALREADY-computed ratio into a descriptive regime label; it never gates or denies anything (that
remains ``risk_manager``'s own, unmodified, frozen responsibility -- see ``types.py``'s own
``VolatilityRegime`` docstring for the exact relationship to ``risk_manager``'s own filter bounds).
"""

from __future__ import annotations

from ai_trader.market_intelligence.types import VolatilityReading, VolatilityRegime
from ai_trader.strategy_runtime import context_access
from ai_trader.strategy_runtime.context_access import MarketContext

#: IMPLEMENTATION CHOICE: EXTREME's own outer bounds are reused verbatim from ``risk_manager``'s own
#: documented volatility filter (``RISK_POLICY.md`` §5: "deny if ATR/price is outside [0.25x, 4x] its
#: rolling median"). LOW/NORMAL/HIGH's own inner bounds are new, purely descriptive bands this module
#: adds (never tuned against results, disclosed here rather than silently assumed).
_EXTREME_LOW = 0.25
_EXTREME_HIGH = 4.0
_LOW_HIGH = 0.7
_HIGH_LOW = 1.3


def _regime_for_ratio(ratio: float | None) -> VolatilityRegime:
    if ratio is None:
        return VolatilityRegime.UNKNOWN
    if ratio < _EXTREME_LOW or ratio > _EXTREME_HIGH:
        return VolatilityRegime.EXTREME
    if ratio < _LOW_HIGH:
        return VolatilityRegime.LOW
    if ratio > _HIGH_LOW:
        return VolatilityRegime.HIGH
    return VolatilityRegime.NORMAL


def analyze_volatility(context: MarketContext) -> VolatilityReading:
    atr = context_access.feature(context, "m_atr", "M15")
    atr_ma = context_access.feature(context, "atr_ma", "M15")
    volatility_rank = context_access.feature(context, "m_volrank", "M15")
    ratio = (atr / atr_ma) if atr is not None and atr_ma is not None and atr_ma > 0 else None
    return VolatilityReading(
        atr=atr, atr_ma=atr_ma, atr_ratio=ratio, volatility_rank=volatility_rank,
        regime=_regime_for_ratio(ratio),
    )
