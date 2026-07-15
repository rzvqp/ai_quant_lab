"""S3 -- Breakout Retest Continuation (Phase 6.8 Wave B, batch B7).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::s3_setups``,
read-only reference, never imported): ``ref=swing`` (``rmax50``/``rmin50``) · ``lb=50`` ·
``retest_within=8`` · ``stop=atr`` (1.5*ATR, floored) · ``exit=rr3`` (3R fixed target) ·
``side=up`` (LONG-only).

Mechanism (v0 ``strategy.json``): "A genuine breakout of a level, then a retest of that level as
new support/resistance, then continuation." Searches backward for the NEAREST prior breakout close
(within the retest window) with no intervening retest already having occurred, then confirms the
CURRENT bar is that first retest touch -- the same "nearest antecedent event, current bar
confirms" search shape S1's own evaluator already established.
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

RETEST_WINDOW_BARS = 8
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5


@register("S3")
class S03BreakoutRetestContinuation(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context)
        if len(recent) < RETEST_WINDOW_BARS + 2:
            return SetupResult.no_setup("insufficient M15 history")

        level = context_access.feature(context, "rmax50")
        atr = context_access.feature(context, "m_atr")
        if level is None or atr is None or atr <= 0:
            return SetupResult.no_setup("rmax50/atr unavailable")

        search_start = max(0, len(recent) - 1 - RETEST_WINDOW_BARS)
        breakout_idx: int | None = None
        for idx in range(len(recent) - 2, search_start - 1, -1):
            if recent[idx]["close"] > level:
                breakout_idx = idx
                break
        if breakout_idx is None:
            return SetupResult.no_setup("no breakout above the 50-bar rolling high within the window")

        for idx in range(breakout_idx + 1, len(recent) - 1):
            if recent[idx]["low"] <= level:
                return SetupResult.no_setup("an earlier retest already occurred since the breakout")

        last = recent[-1]
        if last["low"] > level:
            return SetupResult.no_setup("current bar has not retested the breakout level")

        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=True, floor=floor)
        target = risk.rr_target(entry, stop, is_long=True, rr=3.0)
        return SetupResult.actionable(
            direction="LONG", entry=entry, stop=stop, target=target, strength=0.5, confidence="VERY_LOW",
            regime=None, risk_R=3.0, triggered_conditions=("BREAKOUT_RETEST_CONTINUATION",),
            headline=f"S3: retest confirmed of the breakout above {level:.2f}",
        )
