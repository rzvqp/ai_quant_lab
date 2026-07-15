"""S9 -- Multi-Timeframe Alignment (Phase 6.8 Wave B, batch B8).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::s9_setups``,
read-only reference, never imported): ``c4h=up`` (LONG-only) · ``conf1h=any`` (no additional H1
filter) · ``lb=10`` · ``stop=structural`` (the 20-bar rolling low, NOT atr-based) · ``exit=rr3``
(3R fixed target).

Mechanism (v0 ``strategy.json``): "4H trend context plus a fresh M15 breakout trigger." Onset of a
close above the prior 10-bar rolling max of CLOSE (excluding the current bar), while the H4 trend
is up. No scanner feature publishes a 10-bar close-based rolling max (only 20/50-bar HIGH-based
extremes); computed directly from the bars already in the context window.
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

LOOKBACK_BARS = 10
SPREAD_TICKS = 1.0


@register("S9")
class S09MultiTimeframeAlignment(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context)
        if len(recent) < LOOKBACK_BARS + 2:
            return SetupResult.no_setup("insufficient M15 history")

        h4_trend_up = context_access.flag(context, "h4_trend_up")
        rmin20 = context_access.feature(context, "rmin20")
        atr = context_access.feature(context, "m_atr")
        if h4_trend_up is None or rmin20 is None or atr is None or atr <= 0:
            return SetupResult.no_setup("h4_trend_up/rmin20/atr unavailable")
        if not h4_trend_up:
            return SetupResult.no_setup("H4 trend is not up")

        window_now = recent[-1 - LOOKBACK_BARS: -1]
        roll_now = max(b["close"] for b in window_now)
        last = recent[-1]
        onset_now = last["close"] > roll_now

        if len(recent) >= LOOKBACK_BARS + 3:
            window_before = recent[-2 - LOOKBACK_BARS: -2]
            roll_before = max(b["close"] for b in window_before)
            prev = recent[-2]
            if prev["close"] > roll_before:
                onset_now = False  # already broken out on the previous bar -- not fresh

        if not onset_now:
            return SetupResult.no_setup("no fresh 10-bar closing-high breakout onset")

        entry = last["close"]
        raw_stop = rmin20 - 2 * risk.RESEARCH_ENGINE_TICK
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=True, floor=floor)
        target = risk.rr_target(entry, stop, is_long=True, rr=3.0)
        return SetupResult.actionable(
            direction="LONG", entry=entry, stop=stop, target=target, strength=0.5, confidence="LOW",
            regime=None, risk_R=3.0, triggered_conditions=("H4_ALIGNED_10BAR_BREAKOUT",),
            headline="S9: H4-aligned 10-bar closing-high breakout",
        )
