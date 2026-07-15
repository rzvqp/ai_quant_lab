"""S7 -- Trend Pullback Continuation (Phase 6.8 Wave B, batch B8).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::s7_setups``,
read-only reference, never imported): ``htf=h4`` · ``stop=ema`` (2 ticks past EMA20, NOT atr-based)
· ``exit=rr2`` (2R fixed target) · ``pb_within=8``.

Mechanism (v0 ``strategy.json``): "In an established HTF trend, a pullback to the M15 EMA20 then a
confirmation close back in the trend direction resumes the move." Searches backward for the
NEAREST prior bar on the "wrong side" of EMA20 (a pullback), verifying no earlier confirmation
already occurred since then, then confirms the CURRENT bar closes back on the trend side -- the
same "nearest antecedent event, current bar confirms" search shape S1's own evaluator established.
EMA20's own value is approximated by the current bar's snapshot throughout the search window (it
moves slowly bar to bar, the same convention already used for rmax20/rmin20/pw_high elsewhere).
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

PULLBACK_WINDOW_BARS = 8
SPREAD_TICKS = 1.0


@register("S7")
class S07TrendPullbackContinuation(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context)
        if len(recent) < PULLBACK_WINDOW_BARS + 2:
            return SetupResult.no_setup("insufficient M15 history")

        h4_trend_up = context_access.flag(context, "h4_trend_up")
        ema20 = context_access.feature(context, "m_ema20")
        atr = context_access.feature(context, "m_atr")
        if h4_trend_up is None or ema20 is None or atr is None or atr <= 0:
            return SetupResult.no_setup("h4_trend_up/m_ema20/atr unavailable")
        is_long = h4_trend_up

        search_start = max(0, len(recent) - 1 - PULLBACK_WINDOW_BARS)
        pullback_idx: int | None = None
        for idx in range(len(recent) - 2, search_start - 1, -1):
            on_wrong_side = recent[idx]["close"] < ema20 if is_long else recent[idx]["close"] > ema20
            if on_wrong_side:
                pullback_idx = idx
                break
            on_trend_side = recent[idx]["close"] > ema20 if is_long else recent[idx]["close"] < ema20
            if on_trend_side:
                return SetupResult.no_setup("an earlier confirmation already occurred since the pullback")
        if pullback_idx is None:
            return SetupResult.no_setup("no pullback to the wrong side of EMA20 within the window")

        last = recent[-1]
        confirms = last["close"] > ema20 if is_long else last["close"] < ema20
        if not confirms:
            return SetupResult.no_setup("current bar has not confirmed back through EMA20")

        entry = last["close"]
        raw_stop = ema20 - 2 * risk.RESEARCH_ENGINE_TICK if is_long else ema20 + 2 * risk.RESEARCH_ENGINE_TICK
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        target = risk.rr_target(entry, stop, is_long=is_long, rr=2.0)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=target,
            strength=0.4, confidence="NEGATIVE", regime=None, risk_R=2.0,
            triggered_conditions=("H4_TREND_EMA20_PULLBACK_CONFIRMED",),
            headline="S7: H4-trend EMA20 pullback confirmation",
        )
