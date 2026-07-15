"""S50 -- Outside-Bar / Engulfing Reversal (Phase 6.8 Wave B, batch B5).

Implements EXACTLY the contract's own ``executable_default.params``
(``code/mstrat_ext.py::s50_setups``, read-only reference, never imported): ``mode=reversal`` (fade
AGAINST the engulfing candle's own direction: ``dirn=-base``) · ``stop=bar`` (2 ticks past the
engulfing bar's own extreme, NOT atr-based) · ``exit=rr2`` (2R fixed target).

Mechanism (v0 ``strategy.json``): "An engulfing (outside) candle that is also a genuine range
expansion (>ATR) = a control shift; reversal or continuation." An outside bar (``high > prev.high``
AND ``low < prev.low``) whose own range exceeds ATR, closing bullish (engulfing up) or bearish
(engulfing down); this strategy fades that direction.
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, patterns, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

SPREAD_TICKS = 1.0


@register("S50")
class S50OutsideBarEngulfingReversal(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        prev = context_access.bar_n_ago(context, 1)
        if last is None or prev is None:
            return SetupResult.no_setup("insufficient M15 history")

        atr = context_access.feature(context, "m_atr")
        if atr is None or atr <= 0:
            return SetupResult.no_setup("atr unavailable")

        if not patterns.is_outside_bar(last, prev) or not patterns.is_range_expansion(last, atr):
            return SetupResult.no_setup("no genuine range-expansion outside bar")

        bullish_engulf = last["close"] > last["open"]
        bearish_engulf = last["close"] < last["open"]
        if not bullish_engulf and not bearish_engulf:
            return SetupResult.no_setup("outside bar closed flat")
        is_long = bearish_engulf  # mode=reversal: fade AGAINST the engulfing candle's own direction

        entry = last["close"]
        raw_stop = last["low"] - 2 * risk.RESEARCH_ENGINE_TICK if is_long else last["high"] + 2 * risk.RESEARCH_ENGINE_TICK
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        target = risk.rr_target(entry, stop, is_long=is_long, rr=2.0)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=target,
            strength=0.4, confidence="NEGATIVE", regime=None, risk_R=2.0,
            triggered_conditions=("OUTSIDE_BAR_ENGULFING_REVERSAL",),
            headline="S50: range-expansion engulfing reversal",
        )
