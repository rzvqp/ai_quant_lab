"""S14 -- Momentum Exhaustion (Phase 6.8 Wave B, batch B8).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::
s14_setups``, read-only reference, never imported): ``roc_k=0.004`` · ``side=down`` (a genuine,
non-obvious detail: this fixes SHORT-only, always fading an accelerating UP move that then stalls
-- ``up=(side=='up')=False`` forces ``dirn=-1`` regardless of which direction actually
accelerated) · ``stop=atr`` (1.5*ATR, floored) · ``exit=time`` (frozen engine's own 24-bar timeout,
no price target -- enforced generically by ``ai_trader.simulation.time_stop`` via
:attr:`time_stop_bars`).

Mechanism (v0 ``strategy.json``): "A sharp move (high |ROC|) that then STALLS (ROC magnitude
shrinks) signals exhaustion; fade it." 3-bar ROC values are recomputed directly from closes
(matching the Market Scanner's own ``roc3`` feature formula) since the runtime context only exposes
the CURRENT bar's own feature snapshot, never a historical series.
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

ROC_LOOKBACK_BARS = 3
ROC_THRESHOLD = 0.004
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5
TIME_STOP_BARS = 24  # code/mstrat.py::_exitmap -- exit_kind=='time' -> 24 bars (frozen engine convention)


def _roc3(bars: list[dict], end_idx: int) -> float | None:  # type: ignore[type-arg]
    start_idx = end_idx - ROC_LOOKBACK_BARS
    if start_idx < 0:
        return None
    base = float(bars[start_idx]["close"])
    if base == 0:
        return None
    return float(bars[end_idx]["close"]) / base - 1.0


@register("S14")
class S14MomentumExhaustion(RuntimeEvaluator):
    time_stop_bars = TIME_STOP_BARS

    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context)
        atr = context_access.feature(context, "m_atr")
        if atr is None or atr <= 0:
            return SetupResult.no_setup("atr unavailable")

        last_idx = len(recent) - 1
        roc_now = _roc3(recent, last_idx)
        roc_before = _roc3(recent, last_idx - 1)
        roc_before2 = _roc3(recent, last_idx - 2)
        if roc_now is None or roc_before is None:
            return SetupResult.no_setup("insufficient M15 history for 3-bar ROC")

        accel_now = roc_now > ROC_THRESHOLD
        stall_now = abs(roc_now) < abs(roc_before)
        ev_now = accel_now and stall_now

        ev_before = False
        if roc_before2 is not None:
            accel_before = roc_before > ROC_THRESHOLD
            stall_before = abs(roc_before) < abs(roc_before2)
            ev_before = accel_before and stall_before

        if not ev_now or ev_before:
            return SetupResult.no_setup("no fresh acceleration-then-stall onset")

        last = recent[-1]
        entry = last["close"]
        raw_stop = entry + ATR_STOP_MULT * atr  # SHORT (fading the up-move exhaustion)
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=False, floor=floor)
        return SetupResult.actionable(
            direction="SHORT", entry=entry, stop=stop, target=None, strength=0.4, confidence="VERY_LOW",
            regime=None, risk_R=None, triggered_conditions=("MOMENTUM_EXHAUSTION_STALL",),
            headline="S14: up-move acceleration-then-stall exhaustion",
        )
