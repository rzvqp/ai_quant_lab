"""S48 -- Consolidation-Duration Breakout (Phase 6.8 Wave B, batch B7).

Implements EXACTLY the contract's own ``executable_default.params`` (``code/mstrat.py::
s48_setups``, read-only reference, never imported): ``D=6`` · ``stop=range`` (the opposite edge of
the D-bar consolidation band, NOT atr-based) · ``exit=trailing`` (the frozen engine's own universal
1.5*ATR-at-entry trailing distance -- enforced generically by ``ai_trader.simulation.trailing_stop``
via :attr:`trailing_stop_atr_mult`).

Mechanism (v0 ``strategy.json``): TIME spent compressed (run-length), not the compression level --
``D`` consecutive compressed bars immediately before the signal bar, then a close beyond that
D-bar high/low band; onset only (the frozen engine's own code recomputes the same "coil + band
break" condition one bar earlier and requires it to be fresh -- ``up = up & ~shift(up, 1)``).

Needs the Phase 6.8 Wave B historical-features window (``context_access.flag_n_ago``) for the
``compress`` flags up to ``D+1`` bars back (the onset check needs the whole condition re-evaluated
as of the PREVIOUS bar too); the consolidation band itself comes from ``context_access.bars`` (raw
OHLC needs no historical-feature access).
"""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

CONSOLIDATION_BARS = 6
SPREAD_TICKS = 1.0
TRAILING_ATR_MULT = 1.5  # code/mstrat.py::simulate -- the frozen engine's own universal trailing distance


def _coil_breakout_state(
    context: dict, recent: list[dict], offset: int, d: int  # type: ignore[type-arg]
) -> tuple[bool, bool, float, float] | None:
    """The frozen engine's own ``coil & (cl > band_hi)`` / ``coil & (cl < band_lo)`` state as of
    ``offset`` bars ago (``offset=0`` is the signal bar itself, ``offset=1`` the bar before it) --
    ``None`` if the required bar/flag history is not available (never fabricates)."""
    flags = [context_access.flag_n_ago(context, "compress", n) for n in range(offset + 1, offset + d + 1)]
    if any(f is None for f in flags):
        return None
    coil = all(flags)

    idx_close = len(recent) - 1 - offset
    band_start = len(recent) - 1 - (offset + d)
    band_end = len(recent) - 1 - (offset + 1)
    if idx_close < 0 or band_start < 0:
        return None

    window = recent[band_start: band_end + 1]
    band_hi = max(b["high"] for b in window)
    band_lo = min(b["low"] for b in window)
    close = recent[idx_close]["close"]
    up = coil and close > band_hi
    dn = coil and close < band_lo
    return up, dn, band_hi, band_lo


@register("S48")
class S48ConsolidationDurationBreakout(RuntimeEvaluator):
    trailing_stop_atr_mult = TRAILING_ATR_MULT

    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context)
        if len(recent) < CONSOLIDATION_BARS + 2:
            return SetupResult.no_setup("insufficient M15 history")

        atr = context_access.feature(context, "m_atr")
        if atr is None or atr <= 0:
            return SetupResult.no_setup("atr unavailable")

        now = _coil_breakout_state(context, recent, 0, CONSOLIDATION_BARS)
        before = _coil_breakout_state(context, recent, 1, CONSOLIDATION_BARS)
        if now is None or before is None:
            return SetupResult.no_setup("insufficient compress-flag/bar history")

        up_now, dn_now, band_hi, band_lo = now
        up_before, dn_before, _, _ = before
        fresh_up = up_now and not up_before
        fresh_dn = dn_now and not dn_before
        if not (fresh_up or fresh_dn):
            return SetupResult.no_setup("no fresh consolidation-duration breakout")

        is_long = fresh_up
        entry = recent[-1]["close"]
        raw_stop = (band_lo - 2 * risk.RESEARCH_ENGINE_TICK) if is_long else (band_hi + 2 * risk.RESEARCH_ENGINE_TICK)
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=is_long, floor=floor)
        return SetupResult.actionable(
            direction="LONG" if is_long else "SHORT", entry=entry, stop=stop, target=None,
            strength=0.3, confidence="NEGATIVE", regime=None, risk_R=None,
            triggered_conditions=("CONSOLIDATION_DURATION_BREAKOUT",),
            headline="S48: consolidation-duration breakout onset",
        )
