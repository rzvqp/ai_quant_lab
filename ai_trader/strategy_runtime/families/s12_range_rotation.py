"""S12 -- Range Rotation (Phase 6.8 Wave B, batch B2).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::s12_setups``,
read-only reference, never imported): ``lb=20`` (``rmax20``) · ``side=down`` (SHORT-only) ·
``stop=ext`` (2 ticks beyond the rolling-high extreme, NOT atr -- a genuine, non-obvious detail:
S12's own ``stop=='atr'`` branch is the one NOT selected here) · ``target=center`` -- this OVERRIDES
whatever ``exit`` grammar value is set: ``if h['target']=='center': ek,ep=('rr',1.5) if
exit!='time' else ('time',24)``, so the executable_default's own literal ``"exit": "rr2"`` is
actually executed as a FIXED **1.5R** target, not 2R. Implemented exactly as the frozen engine
does, not as the v0 JSON's ``exit`` field alone would naively suggest.

Mechanism (v0 ``strategy.json``): "At a range extreme, a rejection rotates price back toward the
centre/opposite edge." Onset of the bar's high touching within 0.1% of the 20-bar rolling high.
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

TOUCH_TOLERANCE_FRACTION = 0.001  # code/mstrat.py::s12_setups -- `hi>=rmax*0.999`
RR_TARGET = 1.5  # target=='center' override -- NOT the executable_default's own literal "rr2"
SPREAD_TICKS = 1.0


@register("S12")
class S12RangeRotation(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        prev = context_access.bar_n_ago(context, 1)
        if last is None or prev is None:
            return SetupResult.no_setup("insufficient M15 history")

        rmax20 = context_access.feature(context, "rmax20")
        atr = context_access.feature(context, "m_atr")
        if rmax20 is None or atr is None or atr <= 0:
            return SetupResult.no_setup("rmax20/atr unavailable")

        threshold = rmax20 * (1.0 - TOUCH_TOLERANCE_FRACTION)
        at_ext_now = last["high"] >= threshold
        at_ext_before = prev["high"] >= threshold
        if not at_ext_now or at_ext_before:
            return SetupResult.no_setup("no fresh touch of the 20-bar rolling high")

        entry = last["close"]
        raw_stop = rmax20 + 2 * risk.RESEARCH_ENGINE_TICK  # stop='ext' -- NOT atr-based here
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=False, floor=floor)
        target = risk.rr_target(entry, stop, is_long=False, rr=RR_TARGET)
        return SetupResult.actionable(
            direction="SHORT", entry=entry, stop=stop, target=target, strength=0.4, confidence="NEGATIVE",
            regime=None, risk_R=RR_TARGET, triggered_conditions=("RANGE_HIGH_ROTATION",),
            headline=f"S12: rotation off the 20-bar rolling high {rmax20:.2f}",
        )
