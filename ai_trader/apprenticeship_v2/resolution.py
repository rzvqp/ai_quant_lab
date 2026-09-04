"""Mechanical outcome scoring (mandate Section 14-15). No subjective judgment anywhere in this
file -- every value here is pure arithmetic over a causally-revealed forward bar sequence. Horizon
definitions are frozen at episode-freeze time and never adjusted after seeing the path."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ai_trader.apprenticeship_v2.schemas import RESOLUTION_HORIZONS_M15, HorizonMetrics, S5StructuralResolution

if TYPE_CHECKING:
    from ai_trader.apprenticeship_v2.mt5_read_only_source import ReadOnlyBar
# `ReadOnlyBar` is used only as a type hint below (`list[ReadOnlyBar]`), never as a runtime value
# (no isinstance/construction) -- and `from __future__ import annotations` above already means these
# annotations are never evaluated at runtime. Moving the import behind TYPE_CHECKING removes this
# module's only hard dependency on `mt5_read_only_source` (which itself does `import MetaTrader5` at
# module scope) with zero behavior change in any environment where MetaTrader5 IS installed
# (production) -- General Observer V1.1's own `scorecard.py` needs to import and call
# `compute_horizon_metrics` in a test/dev environment that lacks that package, the same class of
# transitive-dependency problem already worked around this same way in `csv_causal_replay` and this
# package's own `primitives.py`/`snapshot.py` (see their docstrings for the precedent). Distinct from
# the separately-flagged `Direction.LONG` serialization defect (mandate Section 24): that is a real
# behavioral bug this delivery is instructed not to silently fix; this is a pure import-shape change
# that alters no function's computed output anywhere, in any environment.

# Same STOP > TARGET > MAX_HOLD precedence as the already-audited `q4_control_flow.check_trade_mechanics`
# (STOP checked first, then TARGET, then MAX_HOLD, on each forward bar in order) -- reused, not
# reinvented, to stay perfectly consistent with the rest of this project's own trade-mechanics logic.


def compute_s5_structural_resolution(
    *, entry: float, stop: float, target: float, entry_bar_ts: int, max_hold_bars: int,
    forward_bars: list[ReadOnlyBar],
) -> S5StructuralResolution | None:
    """`forward_bars` must be causally-closed bars strictly after `entry_bar_ts`, in ascending order.
    Returns `None` if none of STOP/TARGET/MAX_HOLD has been reached yet (still open)."""
    for i, bar in enumerate(forward_bars, start=1):
        if bar.low <= stop:
            return S5StructuralResolution(
                exit_bar_ts=bar.ts_close, exit_reason="STOP", exit_price=stop,
                r_multiple=round((stop - entry) / (entry - stop) * -1.0, 4),
            )
        if bar.high >= target:
            r = (target - entry) / (entry - stop)
            return S5StructuralResolution(exit_bar_ts=bar.ts_close, exit_reason="TARGET", exit_price=target, r_multiple=round(r, 4))
        if i >= max_hold_bars:
            r = (bar.close - entry) / (entry - stop)
            return S5StructuralResolution(exit_bar_ts=bar.ts_close, exit_reason="MAX_HOLD", exit_price=bar.close, r_multiple=round(r, 4))
    return None


def compute_horizon_metrics(
    *, entry_price: float, setup_direction: str | None, forward_bars: list[ReadOnlyBar], horizon_n: int,
    atr: float | None,
) -> HorizonMetrics:
    """`forward_bars` must contain at least `horizon_n` causally-closed bars strictly after the
    episode's freeze bar, in ascending order -- caller is responsible for only calling this once
    enough bars exist (never called with a partial/truncated horizon)."""
    window = forward_bars[:horizon_n]
    highs = [b.high for b in window]
    lows = [b.low for b in window]
    close_at_horizon = window[-1].close

    max_up = max(0.0, max(highs) - entry_price)
    max_down = max(0.0, entry_price - min(lows))
    forward_return = close_at_horizon - entry_price

    if setup_direction == "LONG":
        mfe, mae = max_up, max_down
    elif setup_direction == "SHORT":
        mfe, mae = max_down, max_up
    else:
        mfe, mae = max(max_up, max_down), min(max_up, max_down)

    horizon_high, horizon_low = max(highs), min(lows)
    close_location = (
        (close_at_horizon - horizon_low) / (horizon_high - horizon_low) if horizon_high > horizon_low else 0.5
    )

    directional_follow_through: bool | None = None
    if setup_direction == "LONG":
        directional_follow_through = forward_return > 0
    elif setup_direction == "SHORT":
        directional_follow_through = forward_return < 0

    # round_trip_magnitude: of the best favorable excursion reached (mfe), how much was given back by
    # horizon close -- 0.0 = none given back (closed at or beyond the best point), 1.0+ = fully round-tripped
    # and then some. Only meaningful when mfe > 0; 0.0 by convention when mfe == 0 (never moved favorably).
    if mfe > 0:
        favorable_close_progress = forward_return if setup_direction != "SHORT" else -forward_return
        round_trip_magnitude = max(0.0, (mfe - favorable_close_progress) / mfe)
    else:
        round_trip_magnitude = 0.0

    def _norm(x: float) -> float:
        return x / atr if atr else x

    return HorizonMetrics(
        forward_return=round(_norm(forward_return), 4), mfe=round(_norm(mfe), 4), mae=round(_norm(mae), 4),
        max_up_move=round(_norm(max_up), 4), max_down_move=round(_norm(max_down), 4),
        close_location=round(close_location, 4), directional_follow_through=directional_follow_through,
        round_trip_magnitude=round(round_trip_magnitude, 4),
    )


def all_horizons_available(forward_bars: list[ReadOnlyBar]) -> bool:
    return len(forward_bars) >= max(RESOLUTION_HORIZONS_M15)
