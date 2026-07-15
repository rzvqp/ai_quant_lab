"""S43 -- Momentum Divergence (RSI/Price) (Phase 6.8 Wave B, batch B8, LAST of the 43).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::
s43_setups``, read-only reference, never imported): ``rsi_tf=m`` (M15-native RSI, ``m_rsi``) ·
``lb=14`` · ``stop=bar`` (2 ticks past the divergence bar's own extreme, NOT atr-based) ·
``exit=rr2`` (2R fixed target).

Mechanism (v0 ``strategy.json``): price makes a new ``lb``-bar extreme while RSI does NOT --
momentum weakening -> reversal. Bearish divergence: a fresh ``lb``-bar price HIGH while RSI sits
below its own prior ``lb``-bar high. Bullish divergence: a fresh ``lb``-bar price LOW while RSI
sits above its own prior ``lb``-bar low. Onset only (the frozen engine's own code recomputes the
same divergence condition one bar earlier and requires it to be fresh).

Needs the Phase 6.8 Wave B historical-features window (``context_access.feature_n_ago``) for the
``m_rsi`` values up to ``lb+1`` bars back -- RSI's own rolling extreme over that window, and the
onset check re-evaluating the whole condition one bar earlier, both require genuine per-bar RSI
history that no prior mechanism exposed (only the current ``m_rsi`` snapshot was ever available).
The price extremes come from ``context_access.bars`` (raw OHLC needs no historical-feature access).
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

LOOKBACK_BARS = 14
RSI_FEATURE = "m_rsi"
SPREAD_TICKS = 1.0
RR_TARGET = 2.0


def _divergence_state(
    context: dict, recent: list[dict], offset: int, lb: int  # type: ignore[type-arg]
) -> tuple[bool, bool] | None:
    """The frozen engine's own ``(hi > ph) & (rsi < rmaxv)`` bearish / ``(lo < pl) & (rsi > rminv)``
    bullish divergence state as of ``offset`` bars ago (``offset=0`` is the signal bar itself,
    ``offset=1`` the bar before it) -- ``None`` if the required bar/RSI history is not available
    (never fabricates)."""
    idx_now = len(recent) - 1 - offset
    win_start = len(recent) - 1 - (offset + lb)
    win_end = len(recent) - 1 - (offset + 1)
    if idx_now < 0 or win_start < 0:
        return None

    window = recent[win_start: win_end + 1]
    ph = max(b["high"] for b in window)
    pl = min(b["low"] for b in window)

    raw_rsi_window = [context_access.feature_n_ago(context, RSI_FEATURE, n) for n in range(offset + 1, offset + lb + 1)]
    if any(v is None for v in raw_rsi_window):
        return None
    rsi_window = [v for v in raw_rsi_window if v is not None]
    rmaxv = max(rsi_window)
    rminv = min(rsi_window)

    rsi_now = context_access.feature_n_ago(context, RSI_FEATURE, offset)
    if rsi_now is None:
        return None

    bar_now = recent[idx_now]
    bear = bar_now["high"] > ph and rsi_now < rmaxv
    bull = bar_now["low"] < pl and rsi_now > rminv
    return bear, bull


@register("S43")
class S43MomentumDivergenceRsiPrice(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context)
        if len(recent) < LOOKBACK_BARS + 3:
            return SetupResult.no_setup("insufficient M15 history")

        atr = context_access.feature(context, "m_atr")
        if atr is None or atr <= 0:
            return SetupResult.no_setup("atr unavailable")

        now = _divergence_state(context, recent, 0, LOOKBACK_BARS)
        before = _divergence_state(context, recent, 1, LOOKBACK_BARS)
        if now is None or before is None:
            return SetupResult.no_setup("insufficient RSI/bar history")

        bear_now, bull_now = now
        bear_before, bull_before = before
        fresh_bear = bear_now and not bear_before
        fresh_bull = bull_now and not bull_before
        if not (fresh_bear or fresh_bull):
            return SetupResult.no_setup("no fresh RSI/price divergence")

        is_long = fresh_bull
        last = recent[-1]
        entry = last["close"]
        raw_stop = (last["low"] - 2 * risk.RESEARCH_ENGINE_TICK) if is_long else (last["high"] + 2 * risk.RESEARCH_ENGINE_TICK)
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        target = risk.rr_target(entry, stop, is_long=is_long, rr=RR_TARGET)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=target,
            strength=0.3, confidence="NEGATIVE", regime=None, risk_R=RR_TARGET,
            triggered_conditions=("RSI_PRICE_DIVERGENCE",),
            headline="S43: fresh RSI/price divergence reversal",
        )
