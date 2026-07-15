"""S39 -- Trend-Efficiency-Gated Continuation (Phase 6.8 Wave B, batch B8).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat_ext.py::
s39_setups`` + ``_efficiency_ratio``, read-only reference, never imported): ``L=20`` ·
``er_thr=0.5`` (Kaufman efficiency ratio gate) · ``stop=swing`` (the 20-bar rolling extreme, NOT
atr-based) · ``exit=rr2`` (2R fixed target).

Mechanism (v0 ``strategy.json``): "Take continuation ONLY when the trend is CLEAN -- high Kaufman
efficiency ratio ... predicts persistence." An expansion bar (range > 1.5*ATR, matching close,
M15 trend-aligned) gated by ``|net L-bar move| / sum(|per-bar moves|) >= er_thr``. The efficiency
ratio is recomputed directly from closes (a fixed, bounded-window formula, exactly reproducible
from the bars already in the context window, unlike a long-memory recursive indicator).
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

ER_LOOKBACK_BARS = 20
ER_THRESHOLD = 0.5
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


@register("S39")
class S39TrendEfficiencyGatedContinuation(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context)
        m_trend_up = context_access.flag(context, "m_trend_up")
        rmax20 = context_access.feature(context, "rmax20")
        rmin20 = context_access.feature(context, "rmin20")
        atr = context_access.feature(context, "m_atr")
        if m_trend_up is None or rmax20 is None or rmin20 is None or atr is None or atr <= 0:
            return SetupResult.no_setup("m_trend_up/rmax20/rmin20/atr unavailable")

        last_idx = len(recent) - 1
        er_now = _efficiency_ratio(recent, last_idx, ER_LOOKBACK_BARS)
        if er_now is None or er_now < ER_THRESHOLD:
            return SetupResult.no_setup("efficiency ratio unavailable or below threshold")

        last = recent[-1]
        is_expansion = (last["high"] - last["low"]) > EXPANSION_ATR_MULT * atr
        if not is_expansion:
            return SetupResult.no_setup("no range-expansion bar this bar")

        is_long = m_trend_up and last["close"] > last["open"]
        is_short = (not m_trend_up) and last["close"] < last["open"]
        if not is_long and not is_short:
            return SetupResult.no_setup("expansion bar does not match the M15 trend direction")

        er_before = _efficiency_ratio(recent, last_idx - 1, ER_LOOKBACK_BARS)
        if er_before is not None and er_before >= ER_THRESHOLD:
            prev = recent[-2]
            prev_expansion = (prev["high"] - prev["low"]) > EXPANSION_ATR_MULT * atr
            prev_matches = (is_long and prev["close"] > prev["open"]) or (is_short and prev["close"] < prev["open"])
            if prev_expansion and prev_matches:
                return SetupResult.no_setup("already gated-and-expanding on the previous bar")

        entry = last["close"]
        raw_stop = rmin20 - 2 * risk.RESEARCH_ENGINE_TICK if is_long else rmax20 + 2 * risk.RESEARCH_ENGINE_TICK
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        target = risk.rr_target(entry, stop, is_long=is_long, rr=2.0)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=target,
            strength=0.5, confidence="LOW", regime=None, risk_R=2.0,
            triggered_conditions=("EFFICIENCY_GATED_TREND_CONTINUATION",),
            headline=f"S39: efficiency-gated (ER={er_now:.2f}) trend continuation",
        )
