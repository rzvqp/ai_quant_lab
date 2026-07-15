"""S31 -- Month-End / Month-Start Effect (Phase 6.8 Wave B, batch B1).

Implements EXACTLY the contract's own ``executable_default.params``
(``code/mstrat_ext.py::s31_setups``, read-only reference, never imported): ``window=month_start``
(day-of-month <= 2) · ``side=down`` (SHORT-only) · ``exit=rr3`` (3R fixed target; the frozen
engine's own S31 setup always uses the universal ``o[ei]-dirn*1.5*atr[t]`` stop formula -- no
``stop`` grammar dimension exists for S31). Fired only at that UTC day's FIRST bar
(``nd=_new_day(d)``).

Mechanism (v0 ``strategy.json``): "Fixed windows around the month change ... entered at the day's
first bar."
"""

from __future__ import annotations

from datetime import UTC, datetime

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

MAX_DAY_OF_MONTH_FOR_MONTH_START = 2
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5


@register("S31")
class S31MonthEndMonthStartEffect(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        prev = context_access.bar_n_ago(context, 1)
        if last is None or prev is None:
            return SetupResult.no_setup("insufficient M15 history")

        atr = context_access.feature(context, "m_atr")
        if atr is None or atr <= 0:
            return SetupResult.no_setup("atr unavailable")

        last_dt = datetime.fromtimestamp(last["ts_open"], tz=UTC)
        prev_dt = datetime.fromtimestamp(prev["ts_open"], tz=UTC)
        is_new_day = last_dt.date() != prev_dt.date()
        in_window = last_dt.day <= MAX_DAY_OF_MONTH_FOR_MONTH_START
        if not is_new_day or not in_window:
            return SetupResult.no_setup("not the first bar of a month-start day")

        entry = last["close"]
        raw_stop = entry + ATR_STOP_MULT * atr  # SHORT
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=False, floor=floor)
        target = risk.rr_target(entry, stop, is_long=False, rr=3.0)
        return SetupResult.actionable(
            direction="SHORT", entry=entry, stop=stop, target=target, strength=0.5, confidence="VERY_LOW",
            regime=None, risk_R=3.0, triggered_conditions=("MONTH_START_EFFECT",),
            headline="S31: month-start first-bar effect",
        )
