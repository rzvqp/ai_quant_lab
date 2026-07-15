"""S20 -- Hybrid Sweep + MTF (Phase 6.8 Wave B, batch B10 -- composes S1/S9's own proven mechanisms,
implemented LAST per PHASE_6_8_WAVE_B_PLAN.md's own ordering).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::
s20_setups``, read-only reference, never imported): ``ctx=h4up`` (LONG-only) · ``trig=breakout`` ·
``lb=20`` (``rmax20``) · ``stop=struct`` (the 20-bar rolling low, NOT atr-based) · ``exit=rr2``
(2R fixed target).

Mechanism (v0 ``strategy.json``): "Combines S9 MTF-trend context with an S1-style sweep or
breakout trigger." Onset of a close above the 20-bar rolling high while the H4 trend is up.
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

SPREAD_TICKS = 1.0


@register("S20")
class S20HybridSweepMtf(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        prev = context_access.bar_n_ago(context, 1)
        if last is None or prev is None:
            return SetupResult.no_setup("insufficient M15 history")

        h4_trend_up = context_access.flag(context, "h4_trend_up")
        rmax20 = context_access.feature(context, "rmax20")
        rmin20 = context_access.feature(context, "rmin20")
        atr = context_access.feature(context, "m_atr")
        if h4_trend_up is None or rmax20 is None or rmin20 is None or atr is None or atr <= 0:
            return SetupResult.no_setup("h4_trend_up/rmax20/rmin20/atr unavailable")
        if not h4_trend_up:
            return SetupResult.no_setup("H4 trend is not up")

        onset = last["close"] > rmax20 and not (prev["close"] > rmax20)
        if not onset:
            return SetupResult.no_setup("no fresh 20-bar rolling-high breakout onset")

        entry = last["close"]
        raw_stop = rmin20 - 2 * risk.RESEARCH_ENGINE_TICK
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=True, floor=floor)
        target = risk.rr_target(entry, stop, is_long=True, rr=2.0)
        return SetupResult.actionable(
            direction="LONG", entry=entry, stop=stop, target=target, strength=0.5, confidence="LOW",
            regime=None, risk_R=2.0, triggered_conditions=("H4_MTF_BREAKOUT",),
            headline="S20: H4-aligned 20-bar breakout (hybrid sweep+MTF)",
        )
