"""S19 -- Session Gap (Phase 6.8 Wave B, batch B1).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::s19_setups``,
read-only reference, never imported): ``gap_dir=down`` (only a DOWN gap qualifies) ·
``mode=fill`` (trade back toward the prior session close -- LONG, since a down-gap fills upward:
``dirn=(-1 if gu else 1) if mode=='fill' else ...`` with ``gu=False``) · ``stop=atr`` (1.5*ATR,
floored) · ``exit=time`` (frozen engine's own 24-bar timeout -- note the ``opp_liq``/prior-close
target ONLY applies when ``exit=='opp_liq'``, not here, so this is a plain time-stop with no price
target, enforced generically by ``ai_trader.simulation.time_stop`` via :attr:`time_stop_bars`).

Mechanism (v0 ``strategy.json``): "A session-open gap either fills (revert to prior close) or
continues." The ``gap`` feature is only ever published on the first bar of a session
(``features.py``: ``gap = open - prev_session_close if bar_in_session==0``), so no extra onset
check is needed -- it naturally fires at most once per session.
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

GAP_ATR_MULT = 0.5
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5
TIME_STOP_BARS = 24  # code/mstrat.py::_exitmap -- exit_kind=='time' -> 24 bars (frozen engine convention)


@register("S19")
class S19SessionGap(RuntimeEvaluator):
    time_stop_bars = TIME_STOP_BARS

    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        if last is None:
            return SetupResult.no_setup("insufficient M15 history")

        gap = context_access.feature(context, "gap")
        atr = context_access.feature(context, "m_atr")
        if gap is None or atr is None or atr <= 0:
            return SetupResult.no_setup("gap/atr unavailable (not the first bar of a session, or ATR not ready)")

        if gap >= -GAP_ATR_MULT * atr:
            return SetupResult.no_setup("no qualifying down-gap this session")

        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr  # LONG (fill of a down-gap)
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=True, floor=floor)
        return SetupResult.actionable(
            direction="LONG", entry=entry, stop=stop, target=None, strength=0.4, confidence="VERY_LOW",
            regime=None, risk_R=None, triggered_conditions=("SESSION_GAP_DOWN_FILL",),
            headline=f"S19: down-gap {gap:.2f} fill",
        )
