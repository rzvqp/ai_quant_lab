"""S38 -- Patient Pullback-into-Zone (Phase 6.8 Wave B, trailing-stop batch).

Implements EXACTLY the contract's own ``executable_default.params``
(``code/mstrat_ext.py::s38_setups``, read-only reference, never imported): ``htf=h1`` ·
``zone=ema20`` · ``stop=swing`` (the 20-bar rolling extreme, NOT atr-based) · ``exit=trailing``
(the frozen engine's own universal 1.5*ATR-at-entry trailing distance -- enforced generically by
``ai_trader.simulation.trailing_stop`` via :attr:`trailing_stop_atr_mult`).

Mechanism (v0 ``strategy.json``): "In an HTF trend, enter on a pullback INTO a discount zone
(EMA20) WITHOUT waiting for a confirmation close." Onset of price tagging EMA20 (an uptrend
pullback down, or a downtrend pullback up) -- no confirmation required, unlike S7's own
confirmed-pullback mechanism. EMA20's own value is approximated by the current bar's snapshot for
the onset comparison (it moves slowly bar to bar, the same convention S7 already established).
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

SPREAD_TICKS = 1.0
TRAILING_ATR_MULT = 1.5  # code/mstrat_ext.py::simulate -- the frozen engine's own universal trailing distance


@register("S38")
class S38PatientPullbackIntoZone(RuntimeEvaluator):
    trailing_stop_atr_mult = TRAILING_ATR_MULT

    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        prev = context_access.bar_n_ago(context, 1)
        if last is None or prev is None:
            return SetupResult.no_setup("insufficient M15 history")

        h1_trend_up = context_access.flag(context, "h1_trend_up")
        ema20 = context_access.feature(context, "m_ema20")
        rmax20 = context_access.feature(context, "rmax20")
        rmin20 = context_access.feature(context, "rmin20")
        atr = context_access.feature(context, "m_atr")
        if h1_trend_up is None or ema20 is None or rmax20 is None or rmin20 is None or atr is None or atr <= 0:
            return SetupResult.no_setup("h1_trend_up/m_ema20/rmax20/rmin20/atr unavailable")

        if h1_trend_up:
            touch_now, touch_before = last["low"] <= ema20, prev["low"] <= ema20
        else:
            touch_now, touch_before = last["high"] >= ema20, prev["high"] >= ema20
        onset = touch_now and not touch_before
        if not onset:
            return SetupResult.no_setup("no fresh onset of a pullback tagging EMA20")
        is_long = h1_trend_up

        entry = last["close"]
        raw_stop = rmin20 - 2 * risk.RESEARCH_ENGINE_TICK if is_long else rmax20 + 2 * risk.RESEARCH_ENGINE_TICK
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=None,
            strength=0.4, confidence="NEGATIVE", regime=None, risk_R=None,
            triggered_conditions=("PATIENT_PULLBACK_INTO_EMA20_ZONE",),
            headline="S38: patient pullback into the EMA20 zone",
        )
