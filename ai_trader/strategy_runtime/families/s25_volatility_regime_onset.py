"""S25 -- Volatility-Regime Onset (Phase 6.8 Wave B, batch B10).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::
s25_setups``, read-only reference, never imported): ``mode=contract`` (SHORT-only entry logic
mirrored -- direction is chosen by the mean-reversion rule below, not fixed) · ``stop=swing`` (the
20-bar rolling extreme, NOT atr-based) · ``exit=time`` (the frozen engine's own ``_exitmap``:
``exit_kind=='time' -> 24`` bars, no price target -- enforced generically by
``ai_trader.simulation.time_stop`` via :attr:`time_stop_bars`).

Mechanism (v0 ``strategy.json``): trades the TRANSITION of ATR across its own moving average, not
a squeeze breakout (distinct from S23). ``contract`` mode is the onset of ATR crossing back BELOW
its moving average (``high_vol`` true one bar ago, false now); direction reverts toward the mean
(SHORT if price is above its own SMA, LONG if below).

Needs the Phase 6.8 Wave B historical-features window (``context_access.feature_n_ago``): the
frozen engine's own onset check compares the CURRENT bar's ``atr > atr_ma`` state against the SAME
comparison one bar ago -- only the current snapshot of ``m_atr``/``atr_ma`` was ever exposed before
this window existed.
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

SPREAD_TICKS = 1.0
TIME_STOP_BARS = 24  # code/mstrat.py::_exitmap -- exit_kind=='time' -> 24 bars (frozen engine convention)


@register("S25")
class S25VolatilityRegimeOnset(RuntimeEvaluator):
    time_stop_bars = TIME_STOP_BARS

    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        last = context_access.last_bar(context)
        if last is None:
            return SetupResult.no_setup("insufficient M15 history")

        atr = context_access.feature(context, "m_atr")
        atr_ma = context_access.feature(context, "atr_ma")
        sma = context_access.feature(context, "m_sma")
        if atr is None or atr <= 0 or atr_ma is None or sma is None:
            return SetupResult.no_setup("atr/atr_ma/m_sma unavailable")

        prev_atr = context_access.feature_n_ago(context, "m_atr", 1)
        prev_atr_ma = context_access.feature_n_ago(context, "atr_ma", 1)
        if prev_atr is None or prev_atr_ma is None:
            return SetupResult.no_setup("insufficient atr/atr_ma history")

        high_vol_now = atr > atr_ma
        high_vol_before = prev_atr > prev_atr_ma
        contract_onset = (not high_vol_now) and high_vol_before
        if not contract_onset:
            return SetupResult.no_setup("no volatility-contraction onset")

        is_long = not (last["close"] > sma)  # revert toward the mean as volatility calms
        rmin20 = context_access.feature(context, "rmin20")
        rmax20 = context_access.feature(context, "rmax20")
        if rmin20 is None or rmax20 is None:
            return SetupResult.no_setup("rmin20/rmax20 unavailable")

        entry = last["close"]
        raw_stop = (rmin20 - 2 * risk.RESEARCH_ENGINE_TICK) if is_long else (rmax20 + 2 * risk.RESEARCH_ENGINE_TICK)
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=None,
            strength=0.3, confidence="NEGATIVE", regime=None, risk_R=None,
            triggered_conditions=("VOLATILITY_CONTRACTION_ONSET",),
            headline="S25: volatility-contraction onset mean-reversion",
        )
