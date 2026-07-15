"""S45 -- Consecutive-Bar Streak (Phase 6.8 Wave B, batch B5).

Implements EXACTLY the contract's own ``executable_default.params``
(``code/mstrat_ext.py::s45_setups``, read-only reference, never imported): ``k=6`` (exactly 6
consecutive close-to-close same-direction bars) · ``mode=reverse`` (fade AGAINST the streak
direction: ``dirn=-base``) · ``stop=atr`` (1.5*ATR, floored) · ``exit=time`` (frozen engine's own
24-bar timeout, no price target -- enforced generically by ``ai_trader.simulation.time_stop`` via
:attr:`time_stop_bars`).

Mechanism (v0 ``strategy.json``): "N consecutive same-direction closes -> reverse (overextension)."
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, patterns, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

STREAK_LENGTH = 6
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5
TIME_STOP_BARS = 24  # code/mstrat_ext.py::_exitmap -- exit_kind=='time' -> 24 bars (frozen engine convention)


@register("S45")
class S45ConsecutiveBarStreak(RuntimeEvaluator):
    time_stop_bars = TIME_STOP_BARS

    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context)
        atr = context_access.feature(context, "m_atr")
        if atr is None or atr <= 0:
            return SetupResult.no_setup("atr unavailable")

        streak_direction = patterns.exact_close_to_close_streak(recent, STREAK_LENGTH)
        if streak_direction is None:
            return SetupResult.no_setup(f"no exact {STREAK_LENGTH}-bar close-to-close streak")
        is_long = streak_direction < 0  # mode=reverse: fade AGAINST the streak direction

        last = recent[-1]
        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr if is_long else entry + ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=None,
            strength=0.4, confidence="VERY_LOW", regime=None, risk_R=None,
            triggered_conditions=(f"EXACT_{STREAK_LENGTH}_BAR_STREAK_REVERSAL",),
            headline=f"S45: exactly {STREAK_LENGTH}-bar streak reversal",
        )
