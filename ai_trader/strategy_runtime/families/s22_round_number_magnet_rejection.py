"""S22 -- Round-Number Magnet / Rejection (Phase 6.8 Wave B, batch B2).

Implements EXACTLY the contract's own ``executable_default.params``
(``code/mstrat_ext.py::s22_setups``, read-only reference, never imported): ``step=100`` ($100 bands
on XAUUSD) · ``mode=breakout`` (the integer band ``floor(close/step)`` changes between bars --
direction is data-dependent, both LONG and SHORT possible, matching ``"long_short": "both"``) ·
``stop=atr`` (1.5*ATR, floored) · ``exit=rr3`` (3R fixed target).

Mechanism (v0 ``strategy.json``): "Psychological $ levels attract limit orders and stops; price
rejects or cleanly breaks them." Band-cross onset: the bar's own $100 band differs from the
previous bar's band (an UP change is LONG, a DOWN change is SHORT).
"""

from __future__ import annotations

import math

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

STEP = 100.0
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5


@register("S22")
class S22RoundNumberMagnetRejection(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        prev = context_access.bar_n_ago(context, 1)
        if last is None or prev is None:
            return SetupResult.no_setup("insufficient M15 history")

        atr = context_access.feature(context, "m_atr")
        if atr is None or atr <= 0:
            return SetupResult.no_setup("atr unavailable")

        band_now = math.floor(last["close"] / STEP)
        band_before = math.floor(prev["close"] / STEP)
        if band_now == band_before:
            return SetupResult.no_setup("no round-number band change this bar")
        is_long = band_now > band_before

        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr if is_long else entry + ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        target = risk.rr_target(entry, stop, is_long=is_long, rr=3.0)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=target,
            strength=0.5, confidence="LOW", regime=None, risk_R=3.0,
            triggered_conditions=("ROUND_NUMBER_BAND_CROSS",),
            headline=f"S22: ${STEP:.0f} round-number band {'up' if is_long else 'down'}-cross",
        )
