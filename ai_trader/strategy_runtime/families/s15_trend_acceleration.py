"""S15 -- Trend Acceleration (Phase 6.8 Wave B, trailing-stop batch).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::
s15_setups``, read-only reference, never imported): ``htf=h1`` · ``exp_k=1.5`` · ``stop=atr``
(1.5*ATR, floored) · ``exit=trailing`` (the frozen engine's own universal 1.5*ATR-at-entry trailing
distance -- enforced generically by ``ai_trader.simulation.trailing_stop`` via
:attr:`trailing_stop_atr_mult`).

Mechanism (v0 ``strategy.json``): "A trend plus a fresh range/momentum expansion bar continues."
Onset of an expansion bar (range > 1.5*ATR) matching the H1 trend direction.
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

EXPANSION_ATR_MULT = 1.5
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5
TRAILING_ATR_MULT = 1.5  # code/mstrat.py::simulate -- the frozen engine's own universal trailing distance


@register("S15")
class S15TrendAcceleration(RuntimeEvaluator):
    trailing_stop_atr_mult = TRAILING_ATR_MULT

    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        prev = context_access.bar_n_ago(context, 1)
        if last is None or prev is None:
            return SetupResult.no_setup("insufficient M15 history")

        h1_trend_up = context_access.flag(context, "h1_trend_up")
        atr = context_access.feature(context, "m_atr")
        if h1_trend_up is None or atr is None or atr <= 0:
            return SetupResult.no_setup("h1_trend_up/atr unavailable")

        def is_expansion_matching_trend(bar: dict) -> bool:  # type: ignore[type-arg]
            expansion = (bar["high"] - bar["low"]) > EXPANSION_ATR_MULT * atr
            matches = bar["close"] > bar["open"] if h1_trend_up else bar["close"] < bar["open"]
            return bool(expansion and matches)

        onset = is_expansion_matching_trend(last) and not is_expansion_matching_trend(prev)
        if not onset:
            return SetupResult.no_setup("no fresh H1-trend-aligned expansion onset")
        is_long = h1_trend_up

        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr if is_long else entry + ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=None,
            strength=0.4, confidence="NEGATIVE", regime=None, risk_R=None,
            triggered_conditions=("H1_TREND_EXPANSION_ACCELERATION",),
            headline="S15: H1-trend-aligned expansion acceleration",
        )
