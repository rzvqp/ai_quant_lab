"""S23 -- Squeeze Breakout + HTF Filter (Phase 6.8 Wave B, batch B7).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::
s23_setups``, read-only reference, never imported): ``htf=h4`` · ``min_sq=3`` ·
``stop=range_opp`` (the opposite edge of the squeeze range, NOT atr-based) · ``exit=trailing``
(the frozen engine's own universal 1.5*ATR-at-entry trailing distance -- enforced generically by
``ai_trader.simulation.trailing_stop`` via :attr:`trailing_stop_atr_mult`).

Mechanism (v0 ``strategy.json``): redesign of the failed S4 -- take the squeeze breakout ONLY in
the H4 trend direction. ``min_sq`` consecutive compressed bars immediately before the signal bar
(``pd.Series(comp).rolling(min_sq).sum().shift(1) >= min_sq`` -- ALL of them, not merely most,
since the window size equals ``min_sq`` itself); the squeeze range is the prior ``min_sq``-bar
high/low. No onset filter in the frozen engine's own code -- overlap suppression (one position at a
time) is what prevents repeat entries while the condition persists, so this evaluator does not add
one either.

Needs the Phase 6.8 Wave B historical-features window (``context_access.flag_n_ago``) for the
``compress`` flags 1..``min_sq`` bars back; the squeeze range itself comes straight from
``context_access.bars`` (raw OHLC needs no historical-feature access).
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

MIN_SQUEEZE_BARS = 3
SPREAD_TICKS = 1.0
TRAILING_ATR_MULT = 1.5  # code/mstrat.py::simulate -- the frozen engine's own universal trailing distance


@register("S23")
class S23SqueezeBreakoutHtfFilter(RuntimeEvaluator):
    trailing_stop_atr_mult = TRAILING_ATR_MULT

    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context)
        if len(recent) < MIN_SQUEEZE_BARS + 1:
            return SetupResult.no_setup("insufficient M15 history")

        atr = context_access.feature(context, "m_atr")
        if atr is None or atr <= 0:
            return SetupResult.no_setup("atr unavailable")

        h4_trend_up = context_access.flag(context, "h4_trend_up")
        if h4_trend_up is None:
            return SetupResult.no_setup("h4_trend_up unavailable")

        prior_flags = [
            context_access.flag_n_ago(context, "compress", n)
            for n in range(1, MIN_SQUEEZE_BARS + 1)
        ]
        if any(f is None for f in prior_flags):
            return SetupResult.no_setup("insufficient compress-flag history")
        if not all(prior_flags):
            return SetupResult.no_setup("squeeze not sustained through the full window")

        squeeze_window = recent[-1 - MIN_SQUEEZE_BARS: -1]
        sq_hi = max(b["high"] for b in squeeze_window)
        sq_lo = min(b["low"] for b in squeeze_window)

        last = recent[-1]
        if h4_trend_up:
            if last["close"] <= sq_hi:
                return SetupResult.no_setup("no upside squeeze breakout")
            is_long = True
        else:
            if last["close"] >= sq_lo:
                return SetupResult.no_setup("no downside squeeze breakout")
            is_long = False

        entry = last["close"]
        raw_stop = (sq_lo - 2 * risk.RESEARCH_ENGINE_TICK) if is_long else (sq_hi + 2 * risk.RESEARCH_ENGINE_TICK)
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=None,
            strength=0.3, confidence="NEGATIVE", regime=None, risk_R=None,
            triggered_conditions=("SQUEEZE_BREAKOUT_HTF_ALIGNED",),
            headline="S23: H4-aligned squeeze breakout",
        )
