"""S42 -- Short-Term Return Reversal (Phase 6.8 Wave B, batch B9).

Implements EXACTLY the contract's own ``executable_default.params``
(``code/mstrat_ext.py::s42_setups``, read-only reference, never imported): ``L=6`` ·
``thr=0.012`` · ``stop=atr`` (1.5*ATR, floored) · ``exit=rr2`` (2R fixed target).

Mechanism (v0 ``strategy.json``): "The largest recent L-bar mover reverses (liquidity providers
absorb overreaction)." The L-bar return is recomputed directly from closes (the runtime context
only exposes the CURRENT bar's own feature snapshot, never a historical series).
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

RETURN_LOOKBACK_BARS = 6
RETURN_THRESHOLD = 0.012
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5


def _l_bar_return(bars: list[dict], end_idx: int, lookback: int) -> float | None:  # type: ignore[type-arg]
    start_idx = end_idx - lookback
    if start_idx < 0:
        return None
    base = float(bars[start_idx]["close"])
    if base == 0:
        return None
    return float(bars[end_idx]["close"]) / base - 1.0


@register("S42")
class S42ShortTermReturnReversal(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context)
        atr = context_access.feature(context, "m_atr")
        if atr is None or atr <= 0:
            return SetupResult.no_setup("atr unavailable")

        last_idx = len(recent) - 1
        return_now = _l_bar_return(recent, last_idx, RETURN_LOOKBACK_BARS)
        return_before = _l_bar_return(recent, last_idx - 1, RETURN_LOOKBACK_BARS)
        if return_now is None or return_before is None:
            return SetupResult.no_setup(f"insufficient M15 history for a {RETURN_LOOKBACK_BARS}-bar return")

        over_now, over_before = return_now > RETURN_THRESHOLD, return_before > RETURN_THRESHOLD
        under_now, under_before = return_now < -RETURN_THRESHOLD, return_before < -RETURN_THRESHOLD
        onset_over = over_now and not over_before
        onset_under = under_now and not under_before
        if not onset_over and not onset_under:
            return SetupResult.no_setup(f"no fresh {RETURN_LOOKBACK_BARS}-bar overreaction onset")
        is_long = onset_under  # oversold -> fade LONG; overbought -> fade SHORT

        last = recent[-1]
        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr if is_long else entry + ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        target = risk.rr_target(entry, stop, is_long=is_long, rr=2.0)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=target,
            strength=0.5, confidence="LOW", regime=None, risk_R=2.0,
            triggered_conditions=("SHORT_TERM_RETURN_REVERSAL",),
            headline=f"S42: {RETURN_LOOKBACK_BARS}-bar return overreaction fade",
        )
