"""S13 -- Imbalance Fill (Phase 6.8 Wave B, batch B4).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::s13_setups``,
read-only reference, never imported): ``fvg=bull`` · ``mode=continue`` (LONG-only --
``dirn=base if mode=='continue' else -base`` with ``base=1`` for a bullish FVG) · ``stop=atr``
(1.5*ATR, floored) · ``exit=time`` (frozen engine's own 24-bar timeout, no price target -- enforced
generically by ``ai_trader.simulation.time_stop`` via :attr:`time_stop_bars`).

Mechanism (v0 ``strategy.json``): "A fair-value gap (imbalance) tends to be filled then produce a
reaction (revert) or act as continuation." Onset of the Market Scanner's own ``fvg_bull`` flag.
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5
TIME_STOP_BARS = 24  # code/mstrat.py::_exitmap -- exit_kind=='time' -> 24 bars (frozen engine convention)


@register("S13")
class S13ImbalanceFill(RuntimeEvaluator):
    time_stop_bars = TIME_STOP_BARS

    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        prev = context_access.bar_n_ago(context, 1)
        if last is None or prev is None:
            return SetupResult.no_setup("insufficient M15 history")

        fvg_bull_now = context_access.flag(context, "fvg_bull")
        atr = context_access.feature(context, "m_atr")
        if fvg_bull_now is None or atr is None or atr <= 0:
            return SetupResult.no_setup("fvg_bull/atr unavailable")

        # No onset check needed: unlike a fixed reference level (pd_close, pw_high), fvg_bull's own
        # comparison window shifts every bar (features.py: low > the high TWO bars back) -- the
        # SAME true value on consecutive bars would mean two genuinely different gaps, not a stale
        # repeat of the same one. Mirrors S6's own no-onset-needed precedent for the same reason.
        if not fvg_bull_now:
            return SetupResult.no_setup("no bullish FVG this bar")

        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=True, floor=floor)
        return SetupResult.actionable(
            direction="LONG", entry=entry, stop=stop, target=None, strength=0.4, confidence="VERY_LOW",
            regime=None, risk_R=None, triggered_conditions=("BULLISH_FVG_CONTINUATION",),
            headline="S13: bullish FVG continuation",
        )
