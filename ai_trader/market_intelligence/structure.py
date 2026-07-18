"""Market structure analysis -- Phase 7 Checkpoint 5. The one Market Intelligence dimension with no
existing centralized detector in this repository -- confirmed by direct search: strategy families
either read `market_scanner`'s own trailing-extreme features (``rmax20``/``rmin20``) directly, or (one
family, ``s11_structure_break_reversal_choch.py``) implement their own inline, non-shared
break-of-structure/change-of-character logic. This module is the first GENERIC, standalone version of
that concept, built fresh -- a deterministic fractal swing-point detector plus a break classifier --
never reusing or modifying `s11`'s own strategy-specific implementation.

**Algorithm (disclosed, IMPLEMENTATION CHOICE, standard and simple by design)**:
1. A bar is a confirmed swing high/low if its own high/low is the strict extreme among
   ``fractal_bars`` bars on each side (a classic "fractal" swing definition -- ties are skipped, never
   arbitrarily broken, for determinism).
2. "Prevailing structure" is read from the last TWO confirmed swing highs and the last TWO confirmed
   swing lows: higher-high AND higher-low = bullish; lower-high AND lower-low = bearish; anything else
   = no clear prevailing structure (a genuine market state, not a gap in this detector).
3. If the current close breaks beyond the most recent swing extreme in the SAME direction as the
   prevailing structure, that is a Break of Structure (BOS, continuation). In the OPPOSITE direction,
   that is a Change of Character (CHoCH, the first signal a trend may be reversing). No break at all is
   RANGING.
"""

from __future__ import annotations

from ai_trader.market_intelligence.types import StructureReading, StructureState, SwingPoint
from ai_trader.strategy_runtime import context_access
from ai_trader.strategy_runtime.context_access import MarketContext

#: IMPLEMENTATION CHOICE: 3 bars on each side (a standard, simple "fractal" window -- never tuned
#: against results). Larger values find fewer, more significant swings; smaller values find more,
#: noisier ones.
_DEFAULT_FRACTAL_BARS = 3

#: How many confirmed swings of each kind to look for -- 2 is the minimum needed to establish
#: "higher-high/higher-low" vs "lower-high/lower-low" prevailing structure.
_SWINGS_NEEDED = 2


def _find_recent_swings(bars: list[dict[str, object]], kind: str, fractal_bars: int, count: int) -> list[SwingPoint]:
    """The most recent ``count`` confirmed swing points of ``kind`` ("HIGH" or "LOW"), most-recent
    first. Scans backward from the newest confirmable bar for efficiency (never needs the FULL bar
    history if recent swings already satisfy ``count``)."""
    key = "high" if kind == "HIGH" else "low"
    found: list[SwingPoint] = []
    n = len(bars)
    last_confirmable = n - 1 - fractal_bars  # the newest index with fractal_bars bars available after it
    for i in range(last_confirmable, fractal_bars - 1, -1):
        window = bars[i - fractal_bars: i + fractal_bars + 1]
        values = [float(bar[key]) for bar in window]  # type: ignore[arg-type]
        candidate_value = float(bars[i][key])  # type: ignore[arg-type]
        is_extreme = candidate_value == (max(values) if kind == "HIGH" else min(values))
        is_unique = values.count(candidate_value) == 1
        if is_extreme and is_unique:
            ts_close = bars[i].get("ts_close")
            found.append(SwingPoint(kind=kind, price=candidate_value, as_of=int(ts_close) if isinstance(ts_close, (int, float)) else 0))
            if len(found) >= count:
                break
    return found


def _prevailing_structure(recent_highs: list[SwingPoint], recent_lows: list[SwingPoint]) -> str:
    """"BULLISH" / "BEARISH" / "UNCLEAR" -- from the last two swing highs and last two swing lows,
    oldest-vs-newest. ``UNCLEAR`` when fewer than two of either kind exist, or highs and lows disagree
    (a higher-high with a lower-low, or vice versa) -- an honest description of a genuinely
    directionless or transitional market, never forced into BULLISH/BEARISH."""
    if len(recent_highs) < _SWINGS_NEEDED or len(recent_lows) < _SWINGS_NEEDED:
        return "UNCLEAR"
    higher_high = recent_highs[0].price > recent_highs[1].price
    higher_low = recent_lows[0].price > recent_lows[1].price
    lower_high = recent_highs[0].price < recent_highs[1].price
    lower_low = recent_lows[0].price < recent_lows[1].price
    if higher_high and higher_low:
        return "BULLISH"
    if lower_high and lower_low:
        return "BEARISH"
    return "UNCLEAR"


def analyze_structure(context: MarketContext, fractal_bars: int = _DEFAULT_FRACTAL_BARS) -> StructureReading:
    bars = context_access.bars(context, "M15")
    last_bar = context_access.last_bar(context, "M15")
    close = last_bar.get("close") if last_bar is not None else None
    close_value = float(close) if isinstance(close, (int, float)) else None

    recent_highs = _find_recent_swings(bars, "HIGH", fractal_bars, _SWINGS_NEEDED)
    recent_lows = _find_recent_swings(bars, "LOW", fractal_bars, _SWINGS_NEEDED)
    last_swing_high = recent_highs[0] if recent_highs else None
    last_swing_low = recent_lows[0] if recent_lows else None

    if close_value is None or last_swing_high is None or last_swing_low is None:
        return StructureReading(
            timeframe="M15", state=StructureState.UNKNOWN,
            last_swing_high=last_swing_high, last_swing_low=last_swing_low,
        )

    prevailing = _prevailing_structure(recent_highs, recent_lows)
    broke_up = close_value > last_swing_high.price
    broke_down = close_value < last_swing_low.price

    if broke_up and not broke_down:
        state = StructureState.BULLISH_BOS if prevailing == "BULLISH" else StructureState.BULLISH_CHOCH
    elif broke_down and not broke_up:
        state = StructureState.BEARISH_BOS if prevailing == "BEARISH" else StructureState.BEARISH_CHOCH
    else:
        # Neither broke, or (a data pathology, e.g. last_swing_high < last_swing_low) both broke --
        # RANGING is the honest default rather than guessing.
        state = StructureState.RANGING

    return StructureReading(
        timeframe="M15", state=state, last_swing_high=last_swing_high, last_swing_low=last_swing_low,
    )
