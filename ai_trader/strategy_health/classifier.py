"""Overall Health Score -> :class:`HealthState` mapping.

**Bands** (fixed, disclosed, on the universal 0-100 percentile-built scale where 50 is, by
construction, the population's own median):

- ``score >= 65``  -> ACTIVE (clearly above the field's own median)
- ``45 <= score < 65`` -> WATCHLIST (at or near the median -- unremarkable, not proven either way)
- ``25 <= score < 45`` -> PROBATION (clearly below median, but not yet the worst)
- ``score < 25``   -> DISABLED (consistently in the bottom quartile of recent performance)

**Regime-adaptation trend adjustment** (the CEO's own stated purpose: "a strategy that was weak
historically may become excellent under the current market regime, and vice versa"): if the 3-month
score exceeds the 12-month score by `TREND_STRONG` (15 points) or more, the strategy is bumped UP one
tier from its band (capped at ACTIVE) -- strong recent improvement outweighs a merely-adequate
12-month baseline. Symmetrically, a 3-month score `TREND_STRONG` points BELOW the 12-month score bumps
the strategy DOWN one tier (floored at DISABLED) -- a strategy whose long-term number still looks fine
but whose most recent quarter has deteriorated sharply is exactly the case multi-year averages hide.

A strategy with NO trades in any window (no evidence either way) is placed on WATCHLIST -- available
to trade the moment it re-qualifies, neither trusted (ACTIVE) nor penalized (PROBATION/DISABLED) for
an absence of recent data that says nothing about its quality.
"""

from __future__ import annotations

from ai_trader.strategy_health.types import HealthState

TREND_STRONG = 15.0

_BANDS: tuple[tuple[float, HealthState], ...] = (
    (65.0, HealthState.ACTIVE),
    (45.0, HealthState.WATCHLIST),
    (25.0, HealthState.PROBATION),
    (float("-inf"), HealthState.DISABLED),
)
_TIER_ORDER: tuple[HealthState, ...] = (
    HealthState.DISABLED, HealthState.PROBATION, HealthState.WATCHLIST, HealthState.ACTIVE,
)


def _band_for(score: float) -> HealthState:
    for threshold, state in _BANDS:
        if score >= threshold:
            return state
    return HealthState.DISABLED  # unreachable (last band threshold is -inf), satisfies mypy


def classify(overall_score: float | None, trend_delta: float | None) -> tuple[HealthState, str]:
    """Returns ``(state, reason)`` -- ``reason`` is a plain-language explanation built from the
    actual numbers that decided it, not a static template."""
    if overall_score is None:
        return HealthState.WATCHLIST, "no trades in any rolling window (3m/6m/12m) -- no recent evidence either way"

    base = _band_for(overall_score)
    idx = _TIER_ORDER.index(base)
    reason = f"overall Health Score {overall_score:.1f} -> base tier {base.value}"

    if trend_delta is not None and trend_delta >= TREND_STRONG and idx < len(_TIER_ORDER) - 1:
        idx += 1
        reason += (
            f"; bumped up to {_TIER_ORDER[idx].value} -- 3-month score exceeds the 12-month "
            f"baseline by {trend_delta:.1f} points, a strong regime-adaptation signal"
        )
    elif trend_delta is not None and trend_delta <= -TREND_STRONG and idx > 0:
        idx -= 1
        reason += (
            f"; bumped down to {_TIER_ORDER[idx].value} -- 3-month score is {abs(trend_delta):.1f} "
            "points below the 12-month baseline, a sharp recent decline the longer-term number hides"
        )

    return _TIER_ORDER[idx], reason
