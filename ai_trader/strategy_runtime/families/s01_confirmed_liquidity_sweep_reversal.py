"""S1 -- Confirmed Liquidity Sweep Reversal (Phase 6.8 reference slice).

Implements EXACTLY the contract's own ``executable_default.params`` -- the specific, evidence-backed
configuration the Research Lab's own performance numbers (``n=399, expectancy_R=0.032, ...``) were
measured on, not the full general grammar (implementing every ``liq_ref``/``confirm``/``exit``
combination would be a broader strategy than what was actually researched):

``side=low`` (LONG-only, low-sweep) · ``liq_ref=pdh_pdl`` (previous day low, via the Market Scanner's
own ``pdl`` feature) · ``confirm=consecutive2`` (two consecutive bullish closes) ·
``imb=none`` (no FVG filter) · ``stop=beyond_sweep`` (2 ticks past the sweep extreme, floored) ·
``exit=rr2`` (2R fixed target) · ``window=8`` (confirmation must complete within 8 bars of the sweep).

Mechanism (v0 ``strategy.json``): "Price sweeps a resting liquidity level ... trapping breakout
traders and triggering stops, then closes back inside the range."
"""

from __future__ import annotations

from ai_trader.strategy_runtime import confirmations, context_access, risk
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, SetupResult
from ai_trader.strategy_runtime.registry import register

WINDOW_BARS = 8
SPREAD_TICKS = 1.0


@register("S1")
class S01LiquiditySweepReversal(RuntimeEvaluator):
    def evaluate(self, context: dict) -> SetupResult:  # type: ignore[type-arg]
        recent = context_access.bars(context, "M15")
        if len(recent) < WINDOW_BARS + 3:
            return SetupResult.no_setup("insufficient M15 history")

        pdl = context_access.feature(context, "pdl")
        if pdl is None:
            return SetupResult.no_setup("pdl unavailable")
        atr = context_access.feature(context, "m_atr")

        last_two = recent[-2:]
        confirmed_now = confirmations.consecutive_same_direction_closes(last_two, 2, bullish=True)

        search_start = max(0, len(recent) - 2 - WINDOW_BARS)
        sweep_candidates_end = len(recent) - 2
        sweep_idx: int | None = None
        for idx in range(sweep_candidates_end - 1, search_start - 1, -1):  # nearest to confirmation first
            if confirmations.swept_level(recent[idx], pdl, is_high_sweep=False):
                sweep_idx = idx
                break

        if sweep_idx is None:
            return SetupResult.no_setup("no PDL low-sweep within the confirmation window")

        if not confirmed_now:
            return SetupResult.waiting(
                direction="LONG", strength=0.4, confidence="LOW", regime=None,
                triggered_conditions=("SWEEP_PDL",),
                headline=f"S1: PDL {pdl:.2f} swept, awaiting 2-bar bullish confirmation",
            )

        entry = recent[-1]["close"]
        # A real bug caught while proving Checkpoint 1: the stop must clear the LOWEST low reached
        # from the sweep bar THROUGH the confirmation bars (inclusive), not just the sweep bar's own
        # low -- price can (and did, in real XAUUSD data) make a NEW low after the nominal "sweep" bar
        # but before confirmation completes. Anchoring the stop to only the sweep bar's own low could
        # place it ABOVE the current entry price (already breached before the trade even opens) if a
        # later bar in the window traded lower. The true sequence extreme is always <= the current
        # bar's own low <= entry, so `stop = extreme_low - floor < entry` is guaranteed here.
        extreme_low = min(b["low"] for b in recent[sweep_idx: len(recent)])
        raw_stop = extreme_low - 2 * risk.RESEARCH_ENGINE_TICK
        floor = risk.executable_stop_floor(SPREAD_TICKS, risk.RESEARCH_ENGINE_TICK, atr)
        stop = risk.widen_stop_to_floor(entry, raw_stop, is_long=True, floor=floor)
        target = risk.rr_target(entry, stop, is_long=True, rr=2.0)
        return SetupResult.actionable(
            direction="LONG", entry=entry, stop=stop, target=target, strength=0.6, confidence="LOW",
            regime=None, risk_R=2.0, triggered_conditions=("SWEEP_PDL", "CONSECUTIVE2_CONFIRM"),
            headline=f"S1: PDL {pdl:.2f} sweep confirmed by 2 bullish closes",
        )
