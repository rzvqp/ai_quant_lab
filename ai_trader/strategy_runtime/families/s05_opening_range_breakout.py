"""S5 -- Opening-Range Breakout (Phase 6.8 Wave B, batch B7).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::s5_setups``,
read-only reference, never imported): ``session=ny`` · ``mode=breakout`` · ``stop=atr`` (1.5*ATR,
floored) · ``side=up`` (LONG-only) · ``exit=rr2`` (2R fixed target). No onset check needed (mirrors
S6's own precedent): the breakout condition can hold for many consecutive bars while trending, but
overlap suppression (``max_concurrent_positions=1``) prevents duplicate entries regardless, exactly
the ``ei<=last: continue`` convention the frozen engine's own shared backtester already applies.

Mechanism (v0 ``strategy.json``): "The first 4 M15 bars of a session define an opening range; a
break of that range signals the session directional bias."
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

TARGET_SESSION = "ny"
MIN_BAR_IN_SESSION = 4
MAX_BAR_IN_SESSION = 20
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5


@register("S5")
class S05OpeningRangeBreakout(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        if last is None:
            return SetupResult.no_setup("insufficient M15 history")

        session = context_access.session_name(context)
        if session != TARGET_SESSION:
            return SetupResult.no_setup(f"not in the {TARGET_SESSION} session")

        bar_in_sess = context_access.feature(context, "bar_in_sess")
        if bar_in_sess is None or not (MIN_BAR_IN_SESSION <= bar_in_sess <= MAX_BAR_IN_SESSION):
            return SetupResult.no_setup("opening range not yet formed, or session too far along")

        or_high = context_access.feature(context, "or_high")
        atr = context_access.feature(context, "m_atr")
        if or_high is None or atr is None or atr <= 0:
            return SetupResult.no_setup("or_high/atr unavailable")

        if last["close"] <= or_high:
            return SetupResult.no_setup("close has not broken above the opening-range high")

        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=True, floor=floor)
        target = risk.rr_target(entry, stop, is_long=True, rr=2.0)
        return SetupResult.actionable(
            direction="LONG", entry=entry, stop=stop, target=target, strength=0.5, confidence="LOW",
            regime=None, risk_R=2.0, triggered_conditions=("NY_OPENING_RANGE_BREAKOUT",),
            headline=f"S5: NY opening-range breakout above {or_high:.2f}",
        )
