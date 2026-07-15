"""S26 -- Value-Area Rejection / Acceptance (Phase 6.8 Wave B, batch B3).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat_ext.py::
s26_setups``, read-only reference, never imported): ``mode=reject`` (fade an excursion beyond the
value-area edge that closes back inside) · ``k=2.0`` (value-area edge = ``vwap +/- 2*std``) ·
``stop=edge`` (2 ticks past the excursion bar's own extreme, NOT atr-based) · ``exit=vwap`` -- a
genuine, non-obvious detail: for ``mode=='reject'`` this does NOT mean a fixed R:R; the frozen
engine's own code (``if ex=='vwap' and mode=='reject': ek,ep=('opp_struct', vwap[ei])``) targets
the session VWAP price directly (revert to value), never a computed R-multiple.

Mechanism (v0 ``strategy.json``): "Excursions beyond the value-area edge ... are rejected (revert)."
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime import vwap as vwap_mod
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

VALUE_AREA_K = 2.0
SPREAD_TICKS = 1.0


@register("S26")
class S26ValueAreaRejectionAcceptance(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        prev = context_access.bar_n_ago(context, 1)
        if last is None or prev is None:
            return SetupResult.no_setup("insufficient M15 history")

        vwap = context_access.feature(context, "vwap")
        std = context_access.feature(context, "m_std")
        atr = context_access.feature(context, "m_atr")
        if vwap is None or std is None or std <= 0 or atr is None or atr <= 0:
            return SetupResult.no_setup("vwap/m_std/atr unavailable")

        va_hi, va_lo = vwap_mod.value_area_edges(vwap, std, VALUE_AREA_K)

        long_now = last["low"] < va_lo and last["close"] > va_lo
        long_before = prev["low"] < va_lo and prev["close"] > va_lo
        short_now = last["high"] > va_hi and last["close"] < va_hi
        short_before = prev["high"] > va_hi and prev["close"] < va_hi
        onset_long = long_now and not long_before
        onset_short = short_now and not short_before
        if not onset_long and not onset_short:
            return SetupResult.no_setup("no fresh value-area-edge rejection onset")
        is_long = onset_long

        entry = last["close"]
        raw_stop = last["low"] - 2 * risk.RESEARCH_ENGINE_TICK if is_long else last["high"] + 2 * risk.RESEARCH_ENGINE_TICK
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=vwap,
            strength=0.4, confidence="NEGATIVE", regime=None, risk_R=None,
            triggered_conditions=("VALUE_AREA_EDGE_REJECTION",),
            headline=f"S26: value-area edge rejection, reverting to vwap {vwap:.2f}",
        )
