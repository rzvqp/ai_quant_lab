"""S18 -- Time-of-Day Edge (Phase 6.8 Wave B, batch B1).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::s18_setups``,
read-only reference, never imported): ``hour=0`` (fires only at 00:00 UTC -- ``(hh==hour)&(mm==0)``)
· ``side=up`` (LONG-only) · ``stop=atr`` (1.5*ATR, floored) · ``exit=time`` (frozen engine's own
24-bar timeout, no price target -- enforced generically by ``ai_trader.simulation.time_stop`` via
:attr:`time_stop_bars`).

Mechanism (v0 ``strategy.json``): "A fixed intraday hour with a directional bias (session-open
flows). Pure clock effect." No scanner feature publishes UTC hour/minute directly; both are derived
from the bar's own ``ts_open`` (the same convention the frozen engine's own
``pd.to_datetime(d['time'],unit='s',utc=True)`` applies), never a fabricated clock.
"""

from __future__ import annotations

from datetime import UTC, datetime

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

TARGET_HOUR_UTC = 0
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5
TIME_STOP_BARS = 24  # code/mstrat.py::_exitmap -- exit_kind=='time' -> 24 bars (frozen engine convention)


@register("S18")
class S18TimeOfDayEdge(RuntimeEvaluator):
    time_stop_bars = TIME_STOP_BARS

    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        if last is None:
            return SetupResult.no_setup("insufficient M15 history")

        atr = context_access.feature(context, "m_atr")
        if atr is None or atr <= 0:
            return SetupResult.no_setup("atr unavailable")

        opened_at = datetime.fromtimestamp(last["ts_open"], tz=UTC)
        if opened_at.hour != TARGET_HOUR_UTC or opened_at.minute != 0:
            return SetupResult.no_setup(f"bar does not open exactly at {TARGET_HOUR_UTC:02d}:00 UTC")

        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=True, floor=floor)
        return SetupResult.actionable(
            direction="LONG", entry=entry, stop=stop, target=None, strength=0.4, confidence="VERY_LOW",
            regime=None, risk_R=None, triggered_conditions=("TIME_OF_DAY_EDGE",),
            headline=f"S18: {TARGET_HOUR_UTC:02d}:00 UTC time-of-day edge",
        )
