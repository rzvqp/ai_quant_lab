"""S29 -- Day-of-Week Effect (Phase 6.8 Wave B, batch B1).

Implements EXACTLY the contract's own ``executable_default.params``
(``code/mstrat_ext.py::s29_setups``, read-only reference, never imported): ``dow=3`` (Thursday,
0=Monday, fired only at that UTC day's FIRST bar -- ``nd=_new_day(d)``) · ``side=up`` (LONG-only) ·
``exit=rr2`` (2R fixed target; no explicit ``stop`` grammar dimension for S29 -- the frozen engine's
own S29 setup always uses the universal ``o[ei]-dirn*1.5*atr[t]`` formula).

Mechanism (v0 ``strategy.json``): "A fixed weekday directional bias, entered at that day's first
bar." No scanner feature publishes UTC weekday directly; derived from the bar's own ``ts_open``,
the same convention the frozen engine's ``pd.to_datetime(...).dt.dayofweek`` applies.
"""

from __future__ import annotations

from datetime import UTC, datetime

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

TARGET_WEEKDAY = 3  # Monday=0 .. Sunday=6 (Python's datetime.weekday()); 3 = Thursday
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5


@register("S29")
class S29DayOfWeekEffect(RuntimeEvaluator):
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
        if not is_new_day or last_dt.weekday() != TARGET_WEEKDAY:
            return SetupResult.no_setup(f"not the first bar of a UTC weekday=={TARGET_WEEKDAY}")

        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=True, floor=floor)
        target = risk.rr_target(entry, stop, is_long=True, rr=2.0)
        return SetupResult.actionable(
            direction="LONG", entry=entry, stop=stop, target=target, strength=0.5, confidence="VERY_LOW",
            regime=None, risk_R=2.0, triggered_conditions=("DAY_OF_WEEK_EFFECT",),
            headline=f"S29: day-of-week={TARGET_WEEKDAY} first-bar effect",
        )
