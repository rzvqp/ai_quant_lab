"""S46 -- Volume-Confirmed Breakout (Phase 6.8 Wave B, batch B7).

Implements EXACTLY the contract's own ``executable_default.params``
(``code/mstrat_ext.py::s46_setups``, read-only reference, never imported): ``vthr=0.85`` ·
``lb=50`` (``rmax50``/``rmin50``) · ``stop=level`` (a genuine, non-obvious detail: the frozen
engine's own code places the stop at the OPPOSITE 50-bar extreme, not near the breakout level
itself -- ``stop = rmin50-2*TICK`` for a LONG breakout above ``rmax50``, a deliberately wide,
structural stop) · ``exit=rr3`` (3R fixed target).

Mechanism (v0 ``strategy.json``): "Breakout of a level ONLY when volume expands (conviction)."
Onset of a close beyond the 50-bar rolling extreme with the Market Scanner's own ``m_volrank``
feature at or above 0.85.
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

VOLRANK_THRESHOLD = 0.85
SPREAD_TICKS = 1.0


@register("S46")
class S46VolumeConfirmedBreakout(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        prev = context_access.bar_n_ago(context, 1)
        if last is None or prev is None:
            return SetupResult.no_setup("insufficient M15 history")

        rmax50 = context_access.feature(context, "rmax50")
        rmin50 = context_access.feature(context, "rmin50")
        volrank = context_access.feature(context, "m_volrank")
        atr = context_access.feature(context, "m_atr")
        if rmax50 is None or rmin50 is None or volrank is None or atr is None or atr <= 0:
            return SetupResult.no_setup("rmax50/rmin50/m_volrank/atr unavailable")
        if volrank < VOLRANK_THRESHOLD:
            return SetupResult.no_setup(f"volrank {volrank:.2f} below the {VOLRANK_THRESHOLD} threshold")

        up_now = last["close"] > rmax50
        up_before = prev["close"] > rmax50
        down_now = last["close"] < rmin50
        down_before = prev["close"] < rmin50
        onset_up = up_now and not up_before
        onset_down = down_now and not down_before
        if not onset_up and not onset_down:
            return SetupResult.no_setup("no fresh volume-confirmed breakout onset")
        is_long = onset_up

        entry = last["close"]
        # stop='level': the OPPOSITE 50-bar extreme, not the breakout level itself (a wide,
        # deliberately structural stop -- exactly what the frozen engine's own code computes).
        raw_stop = rmin50 - 2 * risk.RESEARCH_ENGINE_TICK if is_long else rmax50 + 2 * risk.RESEARCH_ENGINE_TICK
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        target = risk.rr_target(entry, stop, is_long=is_long, rr=3.0)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=target,
            strength=0.5, confidence="VERY_LOW", regime=None, risk_R=3.0,
            triggered_conditions=("VOLUME_CONFIRMED_BREAKOUT",),
            headline=f"S46: volume-confirmed ({volrank:.2f}) 50-bar breakout",
        )
