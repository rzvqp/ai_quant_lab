"""S6 -- Session-Transition (Phase 6.8 Wave B, batch B1).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::s6_setups``,
read-only reference, never imported): ``session=ny`` (target the NY session only) ·
``mode=breakout`` (trade WITH a cross of the prior session's high, not a fade) · ``side=up``
(LONG-only) · ``stop=atr`` (1.5*ATR, floored) · ``exit=rr2`` (2R fixed target).

Mechanism (v0 ``strategy.json``): "Early in London/NY, price interacts with the PRIOR session
high/low; breakout (continuation) or fade (reversion) of that level as the new session takes
control."
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

TARGET_SESSION = "ny"
MAX_BAR_IN_SESSION = 10
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5


@register("S6")
class S06SessionTransition(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        if last is None:
            return SetupResult.no_setup("insufficient M15 history")

        session = context_access.session_name(context)
        if session != TARGET_SESSION:
            return SetupResult.no_setup(f"not in the {TARGET_SESSION} session")

        bar_in_sess = context_access.feature(context, "bar_in_sess")
        if bar_in_sess is None or bar_in_sess > MAX_BAR_IN_SESSION:
            return SetupResult.no_setup("outside the first bars of the session")

        prev_sess_high = context_access.feature(context, "prev_sess_high")
        atr = context_access.feature(context, "m_atr")
        if prev_sess_high is None or atr is None or atr <= 0:
            return SetupResult.no_setup("prev_sess_high/atr unavailable")

        if last["close"] <= prev_sess_high:
            return SetupResult.no_setup("close has not broken above the prior session high")

        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=True, floor=floor)
        target = risk.rr_target(entry, stop, is_long=True, rr=2.0)
        return SetupResult.actionable(
            direction="LONG", entry=entry, stop=stop, target=target, strength=0.5, confidence="LOW",
            regime=None, risk_R=2.0, triggered_conditions=("NY_SESSION_TRANSITION_BREAKOUT",),
            headline=f"S6: NY session-transition breakout above prior session high {prev_sess_high:.2f}",
        )
