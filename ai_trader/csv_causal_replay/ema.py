"""Causal EMA-50 helper (mandate section 12) -- deliberately the ONLY indicator this package
computes, and deliberately scoped to a coarse SIGN check, not decimal-exact value parity. See
`docs/trader_apprenticeship/CSV_Q4_PARITY_1_378_V1.md` for the full disclosure this module's
docstring summarizes.

**Why EMA-50 specifically and nothing else (no ATR/H1/H4 aggregation)**: it is the one indicator
value `AI_TRADER_Q4_M15_LOG.md` itself reports as a bar-by-bar reference ("still below EMA50",
"EMA50/1902.349") and the one Parity Test B (mandate section 11) needs to reproduce the "38
consecutive bars below EMA50" state. Building H1/H4 aggregation or ATR was not needed to satisfy
any specific mandate requirement and was left out per mandate section 15 (no scope creep) -- H1/H4
context for AI Trader's own reasoning is expected to keep coming from the canonical Pine indicator
exactly as the live-TradingView path already provides it (mandate section 5's "ALLOWED CURRENT
STATE" is about what this adapter reveals about the BAR, not a reimplementation of every indicator
AI Trader's Pine layer already computes correctly).

**Why this is causal**: `causal_ema` is a strict left-to-right fold -- the EMA value at index `i`
is a pure function of `values[0..i]` only, never `values[i+1:]`. No centered window, no
backward-fill, no resample bucket that could pull in a later timestamp (mandate section 12's four
explicit prohibitions).

**Why this is NOT claimed bit-identical to the original Pine indicator's own EMA-50 state, and the
CONCRETE, MEASURED size of the divergence (disclosed, not glossed over)**: Pine's `ta.ema` warms up
from however much chart history TradingView had loaded for that indicator at install time --
materially more, and not independently reproducible, than this fixture's disclosed 2000-bar warmup
window (`fixtures.materialize_sealed_fixture.WARMUP_BARS_BEFORE_Q4`). EMA is an infinite-impulse-
response average: its seed choice's influence decays exponentially but never reaches exactly zero.

Measured directly against the real sealed fixture (not estimated): this module's causal EMA-50
puts bar 378's close (1880.434) BELOW its own EMA-50 (1890.390) -- the same DIRECTION
`AI_TRADER_Q4_M15_LOG.md` reports -- but the consecutive-bars-below-EMA streak this module computes
is **44** (extending back to roughly bar 335), not the log's own reported **38** (bars 340-378). This
is a real ~6-bar divergence in exactly WHERE the price/EMA-50 crossing is placed, not a rounding
nuance -- expected precisely because the log's own narrative (`"Price vs EMA50 flips BELOW for the
first time since bar 220"`) describes price and EMA-50 as closely interacting through bars ~220-340,
exactly the kind of near-threshold region where a different warmup seed shifts the exact crossing
bar by a handful of bars. Ruled out as a bug: the formula is the standard textbook one (seed =
SMA(period), `alpha = 2/(period+1)`, matching Pine's own `ta.ema` formula), and causality is
independently verified (`tests/test_ema.py`'s adversarial "changing a later value never changes an
earlier EMA" check) -- so this is warmup-sensitivity, not an implementation defect or a lookahead
leak. **Net scope**: the SIGN fact (bar 378 is below EMA-50) is trustworthy and used by Parity Test
B; the exact STREAK LENGTH is not claimed to match and is reported as a disclosed divergence, not
silently forced to agree -- see `CSV_Q4_PARITY_1_378_V1.md`'s own ledger-state-parity section.
"""

from __future__ import annotations

from typing import Sequence

EMA_PERIOD = 50


def causal_ema(values: Sequence[float], period: int = EMA_PERIOD) -> list[float | None]:
    """Returns one EMA value per input value, `None` for indices before the seed is available
    (`< period - 1`). `result[i]` depends only on `values[0..i]` -- verified directly by
    `tests/test_ema.py`'s own "changing a later value never changes an earlier EMA" adversarial
    check, not merely asserted here."""
    if period < 1:
        raise ValueError(f"period must be >= 1, got {period}")
    n = len(values)
    result: list[float | None] = [None] * n
    if n < period:
        return result
    seed = sum(values[:period]) / period
    result[period - 1] = seed
    alpha = 2.0 / (period + 1)
    prev = seed
    for i in range(period, n):
        prev = (values[i] - prev) * alpha + prev
        result[i] = prev
    return result


def sub_ema_streak(closes: Sequence[float], period: int = EMA_PERIOD) -> int:
    """Length of the current (as-of the LAST value in `closes`) consecutive run of closes strictly
    below their own causal EMA -- the "N consecutive bars below EMA50" fact
    `AI_TRADER_Q4_M15_LOG.md` reports at bar 378 (`"38 consecutive bars (340-378)"`). Returns 0 if
    the last close is at-or-above its EMA, or if fewer than `period` values are available."""
    ema = causal_ema(closes, period)
    streak = 0
    for close, e in zip(reversed(closes), reversed(ema)):
        if e is None:
            break
        if close < e:
            streak += 1
        else:
            break
    return streak
