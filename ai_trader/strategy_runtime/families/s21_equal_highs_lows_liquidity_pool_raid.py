"""S21 -- Equal-Highs/Lows Liquidity-Pool Raid (Phase 6.8 Wave B, batch B2).

Implements EXACTLY the contract's own ``executable_default.params``
(``code/mstrat_ext.py::s21_setups``, read-only reference, never imported): ``side=high`` (SHORT-
only) · ``lb=20`` (``rmax20``) · ``min_touches=2`` (in the prior 20 bars) · ``stop=beyond_raid``
(2 ticks past the raid extreme, NOT structural) · ``exit=rr2`` (2R fixed target).

Mechanism (v0 ``strategy.json``): "Stops/breakout orders pool at CLUSTERS of equal highs/lows (a
level tested >=2x). Large players raid the pool then price reverses." The raid itself (high breaches
``rmax20`` but the close stays back inside) is the SAME wick-vs-body shape as S1's own
``confirmations.swept_level`` -- reused directly. The "equal highs" multi-touch precondition (NEW
vs. S1) is computed inline: a bar "touches" the pool if its high comes within
``0.20*ATR`` of ``rmax20``; the level must have been touched at least ``min_touches`` times across
the prior 20 bars (STRICTLY before the raid bar itself).
"""

from __future__ import annotations

from ai_trader.strategy_runtime import confirmations, context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

TOUCH_WINDOW_BARS = 20
TOUCH_TOLERANCE_ATR_MULT = 0.20
MIN_TOUCHES = 2
SPREAD_TICKS = 1.0


@register("S21")
class S21EqualHighsLowsLiquidityPoolRaid(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context)
        if len(recent) < TOUCH_WINDOW_BARS + 1:
            return SetupResult.no_setup("insufficient M15 history")

        rmax20 = context_access.feature(context, "rmax20")
        atr = context_access.feature(context, "m_atr")
        if rmax20 is None or atr is None or atr <= 0:
            return SetupResult.no_setup("rmax20/atr unavailable")

        last = recent[-1]
        if not confirmations.swept_level(last, rmax20, is_high_sweep=True):
            return SetupResult.no_setup("no raid (wick-sweep-and-reject) of the pooled high this bar")

        tolerance = TOUCH_TOLERANCE_ATR_MULT * atr
        prior_window = recent[-1 - TOUCH_WINDOW_BARS: -1]
        touches = sum(
            1 for b in prior_window
            if confirmations.rolling_extreme_touch(b, rmax20, is_high=True, tolerance=tolerance)
        )
        if touches < MIN_TOUCHES:
            return SetupResult.no_setup(f"only {touches} prior touches of the pooled high, need {MIN_TOUCHES}")

        entry = last["close"]
        raw_stop = last["high"] + 2 * risk.RESEARCH_ENGINE_TICK  # stop='beyond_raid'
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=False, floor=floor)
        target = risk.rr_target(entry, stop, is_long=False, rr=2.0)
        return SetupResult.actionable(
            direction="SHORT", entry=entry, stop=stop, target=target, strength=0.5, confidence="NEGATIVE",
            regime=None, risk_R=2.0, triggered_conditions=("EQUAL_HIGHS_POOL", "RAID_REJECT"),
            headline=f"S21: liquidity-pool raid at {rmax20:.2f} ({touches} prior touches)",
        )
