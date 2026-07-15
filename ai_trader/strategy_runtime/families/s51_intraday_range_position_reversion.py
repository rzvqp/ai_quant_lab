"""S51 -- Intraday Range-Position Reversion (Phase 6.8 Wave B, batch B9).

Implements EXACTLY the contract's own ``executable_default.params``
(``code/mstrat_ext.py::s51_setups``, read-only reference, never imported): ``thr=0.85`` ·
``stop=edge`` (2 ticks past the session extreme, NOT atr-based) · ``exit=rr2`` (2R fixed target).

Mechanism (v0 ``strategy.json``): "Position within the developing SESSION range: near the
top/bottom -> revert toward the middle." Only active once the session range has formed
(``bar_in_sess >= 8``).
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

POSITION_THRESHOLD = 0.85
MIN_BAR_IN_SESSION = 8
SPREAD_TICKS = 1.0


@register("S51")
class S51IntradayRangePositionReversion(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        prev = context_access.bar_n_ago(context, 1)
        if last is None or prev is None:
            return SetupResult.no_setup("insufficient M15 history")

        bar_in_sess = context_access.feature(context, "bar_in_sess")
        sess_high = context_access.feature(context, "sess_high")
        sess_low = context_access.feature(context, "sess_low")
        atr = context_access.feature(context, "m_atr")
        if bar_in_sess is None or sess_high is None or sess_low is None or atr is None or atr <= 0:
            return SetupResult.no_setup("bar_in_sess/sess_high/sess_low/atr unavailable")
        if bar_in_sess < MIN_BAR_IN_SESSION:
            return SetupResult.no_setup("session range not yet formed")

        width = sess_high - sess_low
        if width <= 0:
            return SetupResult.no_setup("degenerate (zero-width) session range")
        position = (last["close"] - sess_low) / width
        position_prev = (prev["close"] - sess_low) / width if width > 0 else None

        high_now = position >= POSITION_THRESHOLD
        low_now = position <= (1.0 - POSITION_THRESHOLD)
        high_before = position_prev is not None and position_prev >= POSITION_THRESHOLD
        low_before = position_prev is not None and position_prev <= (1.0 - POSITION_THRESHOLD)
        onset_high = high_now and not high_before
        onset_low = low_now and not low_before
        if not onset_high and not onset_low:
            return SetupResult.no_setup("no fresh extreme-range-position onset")
        is_long = onset_low  # near the bottom -> revert LONG; near the top -> revert SHORT

        entry = last["close"]
        raw_stop = sess_low - 2 * risk.RESEARCH_ENGINE_TICK if is_long else sess_high + 2 * risk.RESEARCH_ENGINE_TICK
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        target = risk.rr_target(entry, stop, is_long=is_long, rr=2.0)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=target,
            strength=0.4, confidence="NEGATIVE", regime=None, risk_R=2.0,
            triggered_conditions=("INTRADAY_RANGE_POSITION_REVERSION",),
            headline=f"S51: intraday range-position ({position:.2f}) reversion",
        )
