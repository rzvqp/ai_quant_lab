"""Pure P&L computation functions -- no MT5 dependency, no I/O, no wall-clock (`now`/`window_start`
always caller-supplied). Operates only on `DealRecord`/plain floats, projected once at the gateway
boundary (`source.py`) from real MT5 data."""

from __future__ import annotations

from collections.abc import Sequence

from ai_trader.mt5_pnl_source.types import DealRecord


def compute_realized_pnl_pct(
    deals: Sequence[DealRecord], window_start: int, denominator_equity: float,
) -> float:
    """Sum of `deals` whose `close_time` falls within `[window_start, +inf)`, as a fraction of
    `denominator_equity`. Deliberately conservative denominator choice: current equity, not equity at
    the START of the window (which MT5 does not expose directly) -- disclosed, not fabricated."""
    if denominator_equity <= 0:
        raise ValueError(f"denominator_equity must be > 0, got {denominator_equity!r}")
    total = sum(deal.profit for deal in deals if deal.close_time >= window_start)
    return total / denominator_equity


def compute_unrealized_pnl_pct(open_position_profits: Sequence[float], denominator_equity: float) -> float:
    """Sum of currently-open positions' own floating profit, as a fraction of `denominator_equity`."""
    if denominator_equity <= 0:
        raise ValueError(f"denominator_equity must be > 0, got {denominator_equity!r}")
    return sum(open_position_profits) / denominator_equity


def compute_consecutive_losses(deals_chronological: Sequence[DealRecord], now: int) -> tuple[int, float | None]:
    """`deals_chronological` oldest-first (MT5's own `history_deals_get` order). Counts the trailing
    losing streak ending at the MOST RECENT deal; a deal with `profit <= 0` counts as a loss (fail-safe:
    breakeven is not treated as a streak-resetting "win"). Returns `(0, None)` if the most recent deal
    was profitable, or there are no deals at all."""
    if not deals_chronological:
        return 0, None
    count = 0
    last_loss_close_time: int | None = None
    for deal in reversed(deals_chronological):
        if deal.profit > 0:
            break
        count += 1
        if last_loss_close_time is None:
            last_loss_close_time = deal.close_time
    if count == 0:
        return 0, None
    assert last_loss_close_time is not None
    minutes_since_last_loss = (now - last_loss_close_time) / 60.0
    return count, minutes_since_last_loss
