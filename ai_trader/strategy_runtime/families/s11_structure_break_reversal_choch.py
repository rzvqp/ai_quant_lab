"""S11 -- Structure-Break Reversal / CHoCH (Phase 6.8 Wave B, batch B2).

Implements EXACTLY the contract's own ``executable_default.params``
(``code/mstrat.py::s11_setups``, read-only reference, never imported): ``htf=h4`` · ``lb=20``
(``rmax20``/``rmin20``) · ``stop=atr`` (1.5*ATR, floored) · ``exit=rr2`` (2R fixed target).
Direction is data-dependent (both LONG and SHORT are possible), matching the v0 contract's own
``"long_short": "both"``.

Mechanism (v0 ``strategy.json``): "In an HTF trend, a break of the opposite recent swing (change-
of-character) signals a reversal." H4-uptrend + onset of a close below the 20-bar rolling low ->
SHORT reversal; H4-downtrend + onset of a close above the 20-bar rolling high -> LONG reversal.
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5


@register("S11")
class S11StructureBreakReversalChoch(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        prev = context_access.bar_n_ago(context, 1)
        if last is None or prev is None:
            return SetupResult.no_setup("insufficient M15 history")

        h4_trend_up = context_access.flag(context, "h4_trend_up")
        rmax20 = context_access.feature(context, "rmax20")
        rmin20 = context_access.feature(context, "rmin20")
        atr = context_access.feature(context, "m_atr")
        if h4_trend_up is None or rmax20 is None or rmin20 is None or atr is None or atr <= 0:
            return SetupResult.no_setup("h4_trend_up/rmax20/rmin20/atr unavailable")

        if h4_trend_up:
            breaks_now = last["close"] < rmin20
            breaks_before = prev["close"] < rmin20
            is_long = False
        else:
            breaks_now = last["close"] > rmax20
            breaks_before = prev["close"] > rmax20
            is_long = True
        if not breaks_now or breaks_before:
            return SetupResult.no_setup("no fresh CHoCH onset against the H4 trend")

        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr if is_long else entry + ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        target = risk.rr_target(entry, stop, is_long=is_long, rr=2.0)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=target,
            strength=0.4, confidence="NEGATIVE", regime=None, risk_R=2.0,
            triggered_conditions=("H4_CHOCH_REVERSAL",),
            headline="S11: H4-trend change-of-character reversal",
        )
