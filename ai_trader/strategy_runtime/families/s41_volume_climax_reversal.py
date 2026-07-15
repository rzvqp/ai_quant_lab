"""S41 -- Volume-Climax Reversal (Phase 6.8 Wave B, batch B9).

Implements EXACTLY the contract's own ``executable_default.params``
(``code/mstrat_ext.py::s41_setups``, read-only reference, never imported): ``vthr=0.90`` ·
``stop=bar`` (2 ticks past the climax bar's own extreme, NOT atr-based) · ``exit=rr2``
(2R fixed target).

Mechanism (v0 ``strategy.json``): "A participation spike (high volume rank) at a 20-bar price
extreme = capitulation/blow-off; forced flow exhausts -> reversal."
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

VOLRANK_THRESHOLD = 0.90
SPREAD_TICKS = 1.0


@register("S41")
class S41VolumeClimaxReversal(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        prev = context_access.bar_n_ago(context, 1)
        if last is None or prev is None:
            return SetupResult.no_setup("insufficient M15 history")

        rmax20 = context_access.feature(context, "rmax20")
        rmin20 = context_access.feature(context, "rmin20")
        volrank = context_access.feature(context, "m_volrank")
        atr = context_access.feature(context, "m_atr")
        if rmax20 is None or rmin20 is None or volrank is None or atr is None or atr <= 0:
            return SetupResult.no_setup("rmax20/rmin20/m_volrank/atr unavailable")
        if volrank < VOLRANK_THRESHOLD:
            return SetupResult.no_setup(f"volrank {volrank:.2f} below the {VOLRANK_THRESHOLD} threshold")

        top_now = last["high"] >= rmax20
        top_before = prev["high"] >= rmax20
        bottom_now = last["low"] <= rmin20
        bottom_before = prev["low"] <= rmin20
        onset_top = top_now and not top_before
        onset_bottom = bottom_now and not bottom_before
        if not onset_top and not onset_bottom:
            return SetupResult.no_setup("no fresh volume-climax onset at a 20-bar extreme")
        is_long = onset_bottom  # capitulation at the low -> LONG; blow-off at the high -> SHORT

        entry = last["close"]
        raw_stop = last["low"] - 2 * risk.RESEARCH_ENGINE_TICK if is_long else last["high"] + 2 * risk.RESEARCH_ENGINE_TICK
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        target = risk.rr_target(entry, stop, is_long=is_long, rr=2.0)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=target,
            strength=0.4, confidence="NEGATIVE", regime=None, risk_R=2.0,
            triggered_conditions=("VOLUME_CLIMAX_REVERSAL",),
            headline=f"S41: volume-climax ({volrank:.2f}) reversal",
        )
