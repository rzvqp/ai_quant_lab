"""S10 -- Displacement Continuation (Phase 6.8 Wave B, trailing-stop batch).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::
s10_setups``, read-only reference, never imported): ``disp_k=1.5`` · ``pb=4`` · ``side=down``
(SHORT-only) · ``stop=bar`` (2 ticks past the displacement bar's own extreme, NOT atr-based) ·
``exit=trailing`` (the frozen engine's own universal 1.5*ATR-at-entry trailing distance -- enforced
generically by ``ai_trader.simulation.trailing_stop`` via :attr:`trailing_stop_atr_mult`).

Mechanism (v0 ``strategy.json``): "A displacement bar ... marks strong intent; a controlled
pullback then continuation." Searches backward for the NEAREST prior bearish displacement bar
(range > 1.5*ATR, closing bearish) within the pullback window, then confirms the CURRENT bar pulls
back UP to touch that displacement bar's own close -- the same "nearest antecedent event, current
bar confirms" search shape S1's own evaluator established.
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

DISPLACEMENT_ATR_MULT = 1.5
PULLBACK_WINDOW_BARS = 4
SPREAD_TICKS = 1.0
TRAILING_ATR_MULT = 1.5  # code/mstrat.py::simulate -- the frozen engine's own universal trailing distance


@register("S10")
class S10DisplacementContinuation(RuntimeEvaluator):
    trailing_stop_atr_mult = TRAILING_ATR_MULT

    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context)
        if len(recent) < PULLBACK_WINDOW_BARS + 2:
            return SetupResult.no_setup("insufficient M15 history")

        atr = context_access.feature(context, "m_atr")
        if atr is None or atr <= 0:
            return SetupResult.no_setup("atr unavailable")

        search_start = max(0, len(recent) - 1 - PULLBACK_WINDOW_BARS)
        displacement_idx: int | None = None
        for idx in range(len(recent) - 2, search_start - 1, -1):
            bar = recent[idx]
            is_displacement = (bar["high"] - bar["low"]) > DISPLACEMENT_ATR_MULT * atr and bar["close"] < bar["open"]
            if is_displacement:
                displacement_idx = idx
                break

        if displacement_idx is None:
            return SetupResult.no_setup("no bearish displacement bar within the pullback window")

        displacement_close = recent[displacement_idx]["close"]
        for idx in range(displacement_idx + 1, len(recent) - 1):
            if recent[idx]["high"] >= displacement_close:
                return SetupResult.no_setup("an earlier pullback already occurred since the displacement bar")

        last = recent[-1]
        if last["high"] < displacement_close:
            return SetupResult.no_setup("current bar has not pulled back to the displacement bar's close")

        entry = last["close"]
        raw_stop = recent[displacement_idx]["high"] + 2 * risk.RESEARCH_ENGINE_TICK  # stop='bar', SHORT-only
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=False, floor=floor)
        return SetupResult.actionable(
            direction="SHORT", entry=entry, stop=stop, target=None, strength=0.4, confidence="NEGATIVE",
            regime=None, risk_R=None, triggered_conditions=("DISPLACEMENT_PULLBACK_CONTINUATION",),
            headline="S10: bearish displacement pullback continuation",
        )
