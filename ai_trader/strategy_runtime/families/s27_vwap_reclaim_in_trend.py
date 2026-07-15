"""S27 -- VWAP Reclaim in Trend (Phase 6.8 Wave B, batch B3).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat_ext.py::
s27_setups``, read-only reference, never imported): ``htf=h4`` · ``band_k=1.0`` · ``stop=vwap``
(``vwap -/+ 0.25*std``, NOT atr-based) · ``exit=rr2`` -- a genuine, non-obvious detail: the frozen
engine's own code branches ONLY on ``exit=='time'`` vs. everything else (``if ex=='time': ...
else: ek,ep=('opp_struct', vwap[ei]+dirn*band_k*sd[ei])``), so the executable_default's own literal
``"exit": "rr2"`` is actually executed as a price target at the FAR VWAP band
(``vwap + direction*band_k*std``), never a computed R-multiple. Implemented exactly as the frozen
engine does.

Mechanism (v0 ``strategy.json``): "In the HTF trend, price reclaims session VWAP (mean-revert to
VWAP then continue with the trend)."
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

BAND_K = 1.0
STOP_STD_MULT = 0.25
SPREAD_TICKS = 1.0


@register("S27")
class S27VwapReclaimInTrend(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        prev = context_access.bar_n_ago(context, 1)
        if last is None or prev is None:
            return SetupResult.no_setup("insufficient M15 history")

        h4_trend_up = context_access.flag(context, "h4_trend_up")
        vwap = context_access.feature(context, "vwap")
        std = context_access.feature(context, "m_std")
        atr = context_access.feature(context, "m_atr")
        if h4_trend_up is None or vwap is None or std is None or std <= 0 or atr is None or atr <= 0:
            return SetupResult.no_setup("h4_trend_up/vwap/m_std/atr unavailable")

        if h4_trend_up:
            onset = last["close"] > vwap and not (prev["close"] > vwap)
            is_long = True
        else:
            onset = last["close"] < vwap and not (prev["close"] < vwap)
            is_long = False
        if not onset:
            return SetupResult.no_setup("no fresh VWAP reclaim onset aligned with the H4 trend")

        entry = last["close"]
        raw_stop = vwap - STOP_STD_MULT * std if is_long else vwap + STOP_STD_MULT * std
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        target = vwap + BAND_K * std if is_long else vwap - BAND_K * std
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=target,
            strength=0.4, confidence="NEGATIVE", regime=None, risk_R=None,
            triggered_conditions=("H4_TREND_VWAP_RECLAIM",),
            headline=f"S27: H4-trend VWAP reclaim, targeting the far VWAP band {target:.2f}",
        )
