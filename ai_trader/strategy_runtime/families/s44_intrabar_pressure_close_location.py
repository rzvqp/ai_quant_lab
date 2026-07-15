"""S44 -- Intrabar Pressure / Close-Location (Phase 6.8 Wave B, batch B6).

Implements EXACTLY the contract's own ``executable_default.params``
(``code/mstrat_ext.py::s44_setups``, read-only reference, never imported): ``N=3`` (3-bar rolling
mean of the intrabar close-location-value, ``CLV=((C-L)-(H-C))/(H-L)``) · ``mode=continue``
(direction WITH the pressure -- data-dependent, both LONG and SHORT possible, matching
``"long_short": "both"``) · ``stop=atr`` (1.5*ATR, floored) · ``exit=rr2`` (2R fixed target).

Mechanism (v0 ``strategy.json``): "Intrabar buying/selling pressure via close-location-value ...
Persistent pressure -> continuation." Onset of the N-bar mean CLV crossing above +0.5 (buy
pressure, LONG) or below -0.5 (sell pressure, SHORT). CLV is computed purely from each bar's own
OHLC (no scanner feature publishes it), lookahead-safe by construction (only uses already-closed
bars, mirroring the frozen engine's own un-shifted ``rolling(N).mean()`` -- the current bar's own
CLV is included, which is safe here because it is computed AFTER that bar has closed).
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

WINDOW_BARS = 3
PRESSURE_THRESHOLD = 0.5
SPREAD_TICKS = 1.0
ATR_STOP_MULT = 1.5


def _clv(bar: dict) -> float | None:  # type: ignore[type-arg]
    rng = float(bar["high"]) - float(bar["low"])
    if rng <= 0:
        return None
    return (float(bar["close"]) - float(bar["low"]) - (float(bar["high"]) - float(bar["close"]))) / rng


def _mean_clv(bars: list[dict]) -> float | None:  # type: ignore[type-arg]
    values: list[float] = []
    for b in bars:
        v = _clv(b)
        if v is None:
            return None
        values.append(v)
    return sum(values) / len(values)


@register("S44")
class S44IntrabarPressureCloseLocation(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context)
        if len(recent) < WINDOW_BARS + 1:
            return SetupResult.no_setup("insufficient M15 history")

        atr = context_access.feature(context, "m_atr")
        if atr is None or atr <= 0:
            return SetupResult.no_setup("atr unavailable")

        mclv_now = _mean_clv(recent[-WINDOW_BARS:])
        mclv_before = _mean_clv(recent[-WINDOW_BARS - 1: -1])
        if mclv_now is None or mclv_before is None:
            return SetupResult.no_setup("a zero-range bar makes CLV undefined in this window")

        buy_now, buy_before = mclv_now > PRESSURE_THRESHOLD, mclv_before > PRESSURE_THRESHOLD
        sell_now, sell_before = mclv_now < -PRESSURE_THRESHOLD, mclv_before < -PRESSURE_THRESHOLD
        onset_buy = buy_now and not buy_before
        onset_sell = sell_now and not sell_before
        if not onset_buy and not onset_sell:
            return SetupResult.no_setup("no fresh intrabar-pressure onset")
        is_long = onset_buy  # mode=continue: trade WITH the pressure direction

        last = recent[-1]
        entry = last["close"]
        raw_stop = entry - ATR_STOP_MULT * atr if is_long else entry + ATR_STOP_MULT * atr
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        target = risk.rr_target(entry, stop, is_long=is_long, rr=2.0)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=target,
            strength=0.4, confidence="NEGATIVE", regime=None, risk_R=2.0,
            triggered_conditions=("INTRABAR_PRESSURE_CONTINUATION",),
            headline=f"S44: {WINDOW_BARS}-bar mean CLV pressure continuation",
        )
