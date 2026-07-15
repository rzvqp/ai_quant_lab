"""S40 -- Regime Router (Phase 6.8 Wave B, batch B10 -- routes between other batches' now-
implemented mechanisms, implemented LAST per PHASE_6_8_WAVE_B_PLAN.md's own ordering).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat_ext.py::
s40_setups`` + ``_efficiency_ratio``, read-only reference, never imported): ``er_thr=0.5`` ·
``range_lb=20`` · ``stop=swing`` (the 20-bar rolling extreme, NOT atr-based) · ``exit=rr2``
(2R fixed target).

Mechanism (v0 ``strategy.json``): "Deploy each sub-edge only where its mechanism holds: TREND
regime (efficiency>=thr) -> efficient continuation (like S39); RANGE regime -> fade extremes back
to the middle (like S12)." Regime classification and its own onset detection are both recomputed
directly from closes/bars (the same fixed-window Kaufman efficiency ratio ``S39`` already
reimplements, plus already-accepted current-snapshot approximations for ``m_trend_up``/``m_atr``,
never a routing call into another strategy's own evaluator code -- no strategy-specific code, pure
composition of the same primitives).
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

ER_LOOKBACK_BARS = 20
ER_THRESHOLD = 0.5
RANGE_LOOKBACK_BARS = 20
EXPANSION_ATR_MULT = 1.5
SPREAD_TICKS = 1.0


def _efficiency_ratio(bars: list[dict], end_idx: int, lookback: int) -> float | None:  # type: ignore[type-arg]
    start_idx = end_idx - lookback
    if start_idx < 0:
        return None
    net = abs(float(bars[end_idx]["close"]) - float(bars[start_idx]["close"]))
    volume_of_moves = sum(
        abs(float(bars[i]["close"]) - float(bars[i - 1]["close"])) for i in range(start_idx + 1, end_idx + 1)
    )
    if volume_of_moves <= 0:
        return None
    return net / volume_of_moves


def _classify(
    bars: list[dict], idx: int, m_trend_up: bool, rmax20: float, rmin20: float, atr: float,  # type: ignore[type-arg]
) -> tuple[bool, bool] | None:
    """Returns ``(is_long, is_trend_regime)`` for the bar at ``idx``, or ``None`` if no signal."""
    er = _efficiency_ratio(bars, idx, ER_LOOKBACK_BARS)
    if er is None:
        return None
    bar = bars[idx]
    rng = bar["high"] - bar["low"]
    if er >= ER_THRESHOLD:
        # trend regime: efficient continuation (like S39) -- expansion bar in the trend direction.
        if m_trend_up and rng > EXPANSION_ATR_MULT * atr and bar["close"] > bar["open"]:
            return True, True
        if (not m_trend_up) and rng > EXPANSION_ATR_MULT * atr and bar["close"] < bar["open"]:
            return False, True
        return None
    # range regime: fade the rolling extreme back toward the middle (like S12).
    if bar["low"] < rmin20 and bar["close"] > rmin20:
        return True, False
    if bar["high"] > rmax20 and bar["close"] < rmax20:
        return False, False
    return None


@register("S40")
class S40RegimeRouter(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context)
        m_trend_up = context_access.flag(context, "m_trend_up")
        rmax20 = context_access.feature(context, "rmax20")
        rmin20 = context_access.feature(context, "rmin20")
        atr = context_access.feature(context, "m_atr")
        if m_trend_up is None or rmax20 is None or rmin20 is None or atr is None or atr <= 0:
            return SetupResult.no_setup("m_trend_up/rmax20/rmin20/atr unavailable")

        last_idx = len(recent) - 1
        now = _classify(recent, last_idx, m_trend_up, rmax20, rmin20, atr)
        if now is None:
            return SetupResult.no_setup("no regime-routed signal this bar")
        is_long, is_trend_regime = now

        before = _classify(recent, last_idx - 1, m_trend_up, rmax20, rmin20, atr) if last_idx >= 1 else None
        if before is not None and before == now:
            return SetupResult.no_setup("already signaling on the previous bar")

        last = recent[-1]
        entry = last["close"]
        raw_stop = rmin20 - 2 * risk.RESEARCH_ENGINE_TICK if is_long else rmax20 + 2 * risk.RESEARCH_ENGINE_TICK
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        target = risk.rr_target(entry, stop, is_long=is_long, rr=2.0)
        regime_label = "TREND_CONTINUATION" if is_trend_regime else "RANGE_FADE"
        regime = ("TREND_UP" if is_long else "TREND_DOWN") if is_trend_regime else "RANGE"
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=target,
            strength=0.4, confidence="NEGATIVE", regime=regime, risk_R=2.0,
            triggered_conditions=(f"REGIME_ROUTED_{regime_label}",),
            headline=f"S40: regime router ({regime_label.lower()})",
        )
