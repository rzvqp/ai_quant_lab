"""S4 -- Volatility Compression Expansion (Phase 6.8 Wave B, batch B7).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::
s4_setups``, read-only reference, never imported): ``exp_k=1.5`` · ``min_compress=1`` ·
``stop=bar`` (2 ticks past the expansion bar's own extreme, NOT atr-based) · ``exit=trailing``
(the frozen engine's own universal 1.5*ATR-at-entry trailing distance -- enforced generically by
``ai_trader.simulation.trailing_stop`` via :attr:`trailing_stop_atr_mult`).

Mechanism (v0 ``strategy.json``): "After a compression regime (ATR below its mean), a
range-expansion bar (>k*ATR) signals a volatility breakout; trade its direction." v0 itself notes
S4 was found NEGATIVE (expansion direction is near-random without a trend filter -- the fix is
S23) -- migrated as-is regardless, per the frozen-semantics mandate (report, never invent/improve).

Needs the Phase 6.8 Wave B historical-features window (``context_access.flag_n_ago``): the frozen
engine's own prior-compression check is ``comp[t-1-mc:t].sum() < mc`` -- for ``mc=1`` this is the
TWO bars immediately before the signal bar (indices ``t-2`` and ``t-1``), requiring at least one of
them to have been compressed. Only the CURRENT ``compress`` flag was ever exposed before this
window existed; the flags one and two bars back are genuine per-bar history.
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

EXPANSION_ATR_MULT = 1.5
MIN_COMPRESS_BARS = 1
SPREAD_TICKS = 1.0
TRAILING_ATR_MULT = 1.5  # code/mstrat.py::simulate -- the frozen engine's own universal trailing distance


@register("S4")
class S04VolatilityCompressionExpansion(RuntimeEvaluator):
    trailing_stop_atr_mult = TRAILING_ATR_MULT

    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        if last is None:
            return SetupResult.no_setup("insufficient M15 history")

        atr = context_access.feature(context, "m_atr")
        if atr is None or atr <= 0:
            return SetupResult.no_setup("atr unavailable")

        prior_flags = [
            context_access.flag_n_ago(context, "compress", n)
            for n in range(1, MIN_COMPRESS_BARS + 2)
        ]
        if any(f is None for f in prior_flags):
            return SetupResult.no_setup("insufficient compress-flag history")
        if sum(1 for f in prior_flags if f) < MIN_COMPRESS_BARS:
            return SetupResult.no_setup("no sustained prior compression")

        bar_range = last["high"] - last["low"]
        if bar_range <= EXPANSION_ATR_MULT * atr:
            return SetupResult.no_setup("no range-expansion bar")

        is_long = last["close"] > last["open"]
        entry = last["close"]
        raw_stop = (last["low"] - 2 * risk.RESEARCH_ENGINE_TICK) if is_long else (last["high"] + 2 * risk.RESEARCH_ENGINE_TICK)
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=None,
            strength=0.3, confidence="NEGATIVE", regime=None, risk_R=None,
            triggered_conditions=("COMPRESSION_EXPANSION_BREAKOUT",),
            headline="S4: post-compression range-expansion breakout",
        )
