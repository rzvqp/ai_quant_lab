"""S2 -- Failed-Breakout Fade (Phase 6.8 Wave B, batch B2).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::s2_setups``,
read-only reference, never imported): ``ref=pdh_pdl`` (previous-day low, since ``side=low``) ·
``fail_within=4`` (bars) · ``stop=atr`` (1.5*ATR off the failure bar's own sweep bar, floored) ·
``exit=rr2`` (2R fixed target) · ``side=low`` (LONG-only -- ``dirn=1 if side=='low' else -1``).

Mechanism (v0 ``strategy.json``): "A close breaks beyond a reference level then FAILS (closes back
inside) within a few bars -- a false breakout. Fade back into the range." Unlike S1's own wick-sweep
(``confirmations.swept_level``), S2's breakdown/reclaim is CLOSE-based both ways
(``confirmations.close_beyond_level`` both legs), a deliberately different confirmation shape.
"""

from __future__ import annotations

from ai_trader.strategy_runtime import confirmations, context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

FAIL_WITHIN_BARS = 4
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5


@register("S2")
class S02FailedBreakoutFade(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context)
        if len(recent) < FAIL_WITHIN_BARS + 2:
            return SetupResult.no_setup("insufficient M15 history")

        pdl = context_access.feature(context, "pdl")
        atr = context_access.feature(context, "m_atr")
        if pdl is None or atr is None or atr <= 0:
            return SetupResult.no_setup("pdl/atr unavailable")

        last = recent[-1]
        if not confirmations.close_beyond_level(last, pdl, upward=True):
            return SetupResult.no_setup("no reclaim (close back above pdl) on the current bar")

        # Find the most recent close-beyond-pdl (breakdown) bar within the fail_within window,
        # strictly BEFORE the current (reclaim) bar -- the reclaim cannot confirm its own breakdown.
        search_start = max(0, len(recent) - 1 - FAIL_WITHIN_BARS)
        breakdown_idx: int | None = None
        for idx in range(len(recent) - 2, search_start - 1, -1):
            if confirmations.close_beyond_level(recent[idx], pdl, upward=False):
                breakdown_idx = idx
                break
        if breakdown_idx is None:
            return SetupResult.no_setup("no pdl breakdown within the fail_within window")

        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=True, floor=floor)
        target = risk.rr_target(entry, stop, is_long=True, rr=2.0)
        return SetupResult.actionable(
            direction="LONG", entry=entry, stop=stop, target=target, strength=0.5, confidence="VERY_LOW",
            regime=None, risk_R=2.0, triggered_conditions=("PDL_BREAKDOWN", "RECLAIM_CONFIRM"),
            headline=f"S2: pdl {pdl:.2f} breakdown failed, reclaimed",
        )
