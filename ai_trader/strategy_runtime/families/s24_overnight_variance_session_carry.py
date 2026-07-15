"""S24 -- Overnight Variance / Session Carry (Phase 6.8 Wave B, batch B1).

Implements EXACTLY the contract's own ``executable_default.params``
(``code/mstrat_ext.py::s24_setups``, read-only reference, never imported): ``sess=ny`` ·
``mode=fade`` (trade AGAINST the prior session's own closing bias: ``dirn=(-1 if bu else 1) if
mode=='fade'``) · ``entry_bar=1`` (the SECOND bar, index 1, of the session) · ``exit=time`` (frozen
engine's own 24-bar timeout, no price target -- enforced generically by
``ai_trader.simulation.time_stop`` via :attr:`time_stop_bars`). Direction is data-dependent (both
LONG and SHORT are possible outputs), matching the v0 contract's own ``"long_short": "both"``.

Mechanism (v0 ``strategy.json``): "The prior session's close position in its range conditions the
next session; carry (same bias) or fade at the target session's early bar."
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

TARGET_SESSION = "ny"
TARGET_ENTRY_BAR = 1
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5
TIME_STOP_BARS = 24  # code/mstrat_ext.py::_exitmap -- exit_kind=='time' -> 24 bars (frozen engine convention)


@register("S24")
class S24OvernightVarianceSessionCarry(RuntimeEvaluator):
    time_stop_bars = TIME_STOP_BARS

    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        if last is None:
            return SetupResult.no_setup("insufficient M15 history")

        session = context_access.session_name(context)
        if session != TARGET_SESSION:
            return SetupResult.no_setup(f"not in the {TARGET_SESSION} session")

        bar_in_sess = context_access.feature(context, "bar_in_sess")
        if bar_in_sess != TARGET_ENTRY_BAR:
            return SetupResult.no_setup(f"not the session's own bar index {TARGET_ENTRY_BAR}")

        prev_sess_high = context_access.feature(context, "prev_sess_high")
        prev_sess_low = context_access.feature(context, "prev_sess_low")
        prev_sess_close = context_access.feature(context, "prev_sess_close")
        atr = context_access.feature(context, "m_atr")
        if prev_sess_high is None or prev_sess_low is None or prev_sess_close is None or atr is None or atr <= 0:
            return SetupResult.no_setup("prior-session range/atr unavailable")

        mid = (prev_sess_high + prev_sess_low) / 2.0
        bias_up = prev_sess_close > mid
        is_long = not bias_up  # mode=fade: trade AGAINST the prior session's own closing bias

        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr if is_long else entry + ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=None,
            strength=0.4, confidence="VERY_LOW", regime=None, risk_R=None,
            triggered_conditions=("SESSION_CARRY_FADE",),
            headline=f"S24: NY session-carry fade of prior session's {'upper' if bias_up else 'lower'}-half close",
        )
