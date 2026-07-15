"""S28 -- Anchored-VWAP Reaction (Phase 6.8 Wave B, batch B3).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat_ext.py::
s28_setups`` + ``_anchored_vwap``, read-only reference, never imported): ``anchor=week`` (Monday-
aligned week bucket -- ``ai_trader.strategy_runtime.vwap.week_bucket``, the exact same bucketing
formula) · ``mode=bounce`` (tag-and-hold at the anchor, not a clean cross) · ``exit=time`` (frozen
engine's own 24-bar timeout, no price target -- enforced generically by
``ai_trader.simulation.time_stop`` via :attr:`time_stop_bars`). No scanner feature publishes a
week-anchored VWAP (only the session ``vwap`` resets per session); computed directly from the
bars already in the (lookahead-safe) context window, which is why this strategy declares a large
``lookback_bars`` (>= one week of M15 bars) in its own contract.

Mechanism (v0 ``strategy.json``): "Reactions at a WEEK ... anchored VWAP ... after a genuine
departure." Requires the prior 8 bars to have departed >= 0.75*ATR from the anchor (the frozen
engine's own per-bar ATR array approximated here by the CURRENT bar's own ATR, the same convention
every other cross-bar computation in this package already uses).
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime import vwap as vwap_mod
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

DEPARTURE_WINDOW_BARS = 8
DEPARTURE_ATR_MULT = 0.75
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5
TIME_STOP_BARS = 24  # code/mstrat_ext.py::_exitmap -- exit_kind=='time' -> 24 bars (frozen engine convention)


@register("S28")
class S28AnchoredVwapReaction(RuntimeEvaluator):
    time_stop_bars = TIME_STOP_BARS

    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context)
        if len(recent) < DEPARTURE_WINDOW_BARS + 2:
            return SetupResult.no_setup("insufficient M15 history")

        atr = context_access.feature(context, "m_atr")
        if atr is None or atr <= 0:
            return SetupResult.no_setup("atr unavailable")

        anchor = vwap_mod.anchored_vwap(recent, vwap_mod.week_bucket)
        if anchor is None:
            return SetupResult.no_setup("week-anchored vwap unavailable (no volume in this bucket yet)")

        prior_window = recent[-1 - DEPARTURE_WINDOW_BARS: -1]
        max_distance = max(
            (vwap_mod.distance_in_atr(b["close"], anchor, atr) or 0.0) for b in prior_window
        )
        if max_distance < DEPARTURE_ATR_MULT:
            return SetupResult.no_setup("no genuine prior departure from the anchor")

        last, prev = recent[-1], recent[-2]
        long_now = last["low"] <= anchor and last["close"] > anchor
        long_before = prev["low"] <= anchor and prev["close"] > anchor
        short_now = last["high"] >= anchor and last["close"] < anchor
        short_before = prev["high"] >= anchor and prev["close"] < anchor
        onset_long = long_now and not long_before
        onset_short = short_now and not short_before
        if not onset_long and not onset_short:
            return SetupResult.no_setup("no fresh bounce onset at the anchored vwap")
        is_long = onset_long

        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr if is_long else entry + ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=None,
            strength=0.4, confidence="NEGATIVE", regime=None, risk_R=None,
            triggered_conditions=("WEEK_ANCHORED_VWAP_BOUNCE",),
            headline=f"S28: bounce at the week-anchored vwap {anchor:.2f}",
        )
