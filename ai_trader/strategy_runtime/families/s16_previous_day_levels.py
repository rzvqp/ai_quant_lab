"""S16 -- Previous-Day Levels (Phase 6.8 Wave B, batch B1).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::s16_setups``,
read-only reference, never imported): ``level=pd_close`` (previous day's closing price) ·
``mode=breakout`` (LONG-only in this grammar -- ``dirn=1 if mode=='breakout' else -1``, independent
of which level) · ``stop=atr`` (1.5*ATR, floored) · ``exit=time`` (the frozen engine's own
``_exitmap``: ``exit_kind=='time' -> 24`` bars, no price target -- enforced generically by
``ai_trader.simulation.time_stop`` via :attr:`time_stop_bars`, never a substitute rr exit).

Mechanism (v0 ``strategy.json``): "Prior-day high/low/open/close/mid act as magnets/decision points
-- breakout or rejection."
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5
TIME_STOP_BARS = 24  # code/mstrat.py::_exitmap -- exit_kind=='time' -> 24 bars (frozen engine convention)


@register("S16")
class S16PreviousDayLevels(RuntimeEvaluator):
    time_stop_bars = TIME_STOP_BARS

    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        prev = context_access.bar_n_ago(context, 1)
        if last is None or prev is None:
            return SetupResult.no_setup("insufficient M15 history")

        pd_close = context_access.feature(context, "pd_close")
        atr = context_access.feature(context, "m_atr")
        if pd_close is None or atr is None or atr <= 0:
            return SetupResult.no_setup("pd_close/atr unavailable")

        crossed_now = last["close"] > pd_close
        crossed_before = prev["close"] > pd_close
        if not crossed_now or crossed_before:
            return SetupResult.no_setup("no fresh close-onset above pd_close")

        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=True, floor=floor)
        return SetupResult.actionable(
            direction="LONG", entry=entry, stop=stop, target=None, strength=0.5, confidence="LOW",
            regime=None, risk_R=None, triggered_conditions=("PD_CLOSE_BREAKOUT_ONSET",),
            headline=f"S16: fresh close above pd_close {pd_close:.2f}",
        )
