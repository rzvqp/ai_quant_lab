"""S17 -- Weekly Levels (Phase 6.8 Wave B, batch B1).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::s17_setups``,
read-only reference, never imported): ``level=pw_high`` (previous week's high) · ``mode=reject``
(SHORT-only -- ``dirn=1 if mode=='breakout' else -1``) · ``stop=atr`` (1.5*ATR, floored) ·
``exit=time`` (frozen engine's own 24-bar timeout, no price target -- enforced generically by
``ai_trader.simulation.time_stop`` via :attr:`time_stop_bars`).

Mechanism (v0 ``strategy.json``): "Prior-week high/low as higher-timeframe decision levels --
breakout or rejection." Reject: a wick tags/exceeds ``pw_high`` but the close stays back inside --
the SAME wick-vs-body shape as ``confirmations.swept_level``.
"""

from __future__ import annotations

from ai_trader.strategy_runtime import confirmations, context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5
TIME_STOP_BARS = 24  # code/mstrat.py::_exitmap -- exit_kind=='time' -> 24 bars (frozen engine convention)


@register("S17")
class S17WeeklyLevels(RuntimeEvaluator):
    time_stop_bars = TIME_STOP_BARS

    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        prev = context_access.bar_n_ago(context, 1)
        if last is None or prev is None:
            return SetupResult.no_setup("insufficient M15 history")

        pw_high = context_access.feature(context, "pw_high")
        atr = context_access.feature(context, "m_atr")
        if pw_high is None or atr is None or atr <= 0:
            return SetupResult.no_setup("pw_high/atr unavailable")

        rejects_now = confirmations.swept_level(last, pw_high, is_high_sweep=True)
        rejects_before = confirmations.swept_level(prev, pw_high, is_high_sweep=True)
        if not rejects_now or rejects_before:
            return SetupResult.no_setup("no fresh pw_high rejection onset")

        entry = last["close"]
        raw_stop = entry + ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=False, floor=floor)
        return SetupResult.actionable(
            direction="SHORT", entry=entry, stop=stop, target=None, strength=0.5, confidence="LOW",
            regime=None, risk_R=None, triggered_conditions=("PW_HIGH_REJECTION_ONSET",),
            headline=f"S17: fresh rejection at pw_high {pw_high:.2f}",
        )
