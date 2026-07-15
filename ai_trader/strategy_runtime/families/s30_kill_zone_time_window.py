"""S30 -- Kill-Zone Time-Window (Phase 6.8 Wave B, batch B1).

Implements EXACTLY the contract's own ``executable_default.params``
(``code/mstrat_ext.py::s30_setups``, read-only reference, never imported): ``zone=ny_kz`` (12:00-
15:00 UTC) · ``mode=continuation`` (trade WITH the breakout direction, ``dirn=raw``) ·
``stop=atr`` (1.5*ATR, floored) · ``exit=rr2`` (2R fixed target). Onset of a close beyond the prior
4-bar (EXCLUDING the current bar) rolling high/low, inside the kill-zone window.

Mechanism (v0 ``strategy.json``): "Pre-registered UTC kill-zones; breakout of the prior 4-bar range
inside the window -> continuation or reversal." No scanner feature publishes a 4-bar rolling
extreme (only 20/50-bar windows exist); computed directly from the last 5 bars here, mirroring
``code/mstrat_ext.py``'s own ``rolling(4).max().shift(1)`` (strictly prior to the current bar).
"""

from __future__ import annotations

from datetime import UTC, datetime

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

KZ_START_HOUR_UTC = 12
KZ_END_HOUR_UTC = 15  # exclusive
LOOKBACK_BARS = 4
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5


@register("S30")
class S30KillZoneTimeWindow(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context)
        if len(recent) < LOOKBACK_BARS + 1:
            return SetupResult.no_setup("insufficient M15 history")

        atr = context_access.feature(context, "m_atr")
        if atr is None or atr <= 0:
            return SetupResult.no_setup("atr unavailable")

        last = recent[-1]
        opened_at = datetime.fromtimestamp(last["ts_open"], tz=UTC)
        if not (KZ_START_HOUR_UTC <= opened_at.hour < KZ_END_HOUR_UTC):
            return SetupResult.no_setup("outside the NY kill-zone window")

        prior_window = recent[-1 - LOOKBACK_BARS: -1]
        rolling_high = max(b["high"] for b in prior_window)
        rolling_low = min(b["low"] for b in prior_window)

        breaks_up = last["close"] > rolling_high
        breaks_down = last["close"] < rolling_low
        if not breaks_up and not breaks_down:
            return SetupResult.no_setup("no prior-4-bar range breakout this bar")
        is_long = breaks_up  # mode=continuation: trade WITH the breakout direction

        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr if is_long else entry + ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        target = risk.rr_target(entry, stop, is_long=is_long, rr=2.0)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=target,
            strength=0.4, confidence="NEGATIVE", regime=None, risk_R=2.0,
            triggered_conditions=("NY_KILL_ZONE_CONTINUATION",),
            headline="S30: NY kill-zone 4-bar range continuation breakout",
        )
