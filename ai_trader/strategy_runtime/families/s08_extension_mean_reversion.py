"""S8 -- Extension Mean-Reversion (Phase 6.8 Wave B, batch B9).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::s8_setups``,
read-only reference, never imported): ``ref=vwap`` · ``k=3.0`` · ``side=up`` (LONG-only) ·
``stop=atr`` (1.5*ATR, floored) · ``exit=rr2`` (2R fixed target).

Mechanism (v0 ``strategy.json``): "Price extends k*ATR beyond a reference (session VWAP); the
onset of over-extension reverts toward the reference."
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

EXTENSION_ATR_MULT = 3.0
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5


@register("S8")
class S08ExtensionMeanReversion(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        prev = context_access.bar_n_ago(context, 1)
        if last is None or prev is None:
            return SetupResult.no_setup("insufficient M15 history")

        vwap = context_access.feature(context, "vwap")
        atr = context_access.feature(context, "m_atr")
        if vwap is None or atr is None or atr <= 0:
            return SetupResult.no_setup("vwap/atr unavailable")

        extended_now = (last["close"] - vwap) < -EXTENSION_ATR_MULT * atr
        extended_before = (prev["close"] - vwap) < -EXTENSION_ATR_MULT * atr
        if not extended_now or extended_before:
            return SetupResult.no_setup("no fresh over-extension below vwap")

        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=True, floor=floor)
        target = risk.rr_target(entry, stop, is_long=True, rr=2.0)
        return SetupResult.actionable(
            direction="LONG", entry=entry, stop=stop, target=target, strength=0.5, confidence="LOW",
            regime=None, risk_R=2.0, triggered_conditions=("VWAP_EXTENSION_MEAN_REVERSION",),
            headline=f"S8: fresh over-extension {EXTENSION_ATR_MULT}*ATR below vwap {vwap:.2f}",
        )
