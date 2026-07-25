"""Pure-function tests for the P&L computation logic -- no MT5 dependency at all, plain `DealRecord`
tuples and floats."""

from __future__ import annotations

import pytest

from ai_trader.mt5_pnl_source.computation import (
    compute_consecutive_losses,
    compute_realized_pnl_pct,
    compute_unrealized_pnl_pct,
)
from ai_trader.mt5_pnl_source.types import DealRecord

AS_OF = 1_700_000_000


def test_realized_pnl_sums_only_deals_within_the_window() -> None:
    deals = (
        DealRecord(profit=-500.0, close_time=AS_OF - 100_000),  # before window -- excluded
        DealRecord(profit=200.0, close_time=AS_OF - 1000),
        DealRecord(profit=-50.0, close_time=AS_OF - 500),
    )
    result = compute_realized_pnl_pct(deals, window_start=AS_OF - 10_000, denominator_equity=10_000.0)
    assert result == pytest.approx((200.0 - 50.0) / 10_000.0)


def test_realized_pnl_with_no_deals_in_window_is_zero() -> None:
    deals = (DealRecord(profit=-500.0, close_time=AS_OF - 100_000),)
    result = compute_realized_pnl_pct(deals, window_start=AS_OF - 10_000, denominator_equity=10_000.0)
    assert result == 0.0


def test_realized_pnl_rejects_non_positive_denominator() -> None:
    with pytest.raises(ValueError):
        compute_realized_pnl_pct((), window_start=AS_OF, denominator_equity=0.0)


def test_unrealized_pnl_sums_open_position_profits() -> None:
    result = compute_unrealized_pnl_pct((100.0, -30.0, 5.0), denominator_equity=1000.0)
    assert result == pytest.approx((100.0 - 30.0 + 5.0) / 1000.0)


def test_unrealized_pnl_with_no_open_positions_is_zero() -> None:
    assert compute_unrealized_pnl_pct((), denominator_equity=1000.0) == 0.0


def test_unrealized_pnl_rejects_non_positive_denominator() -> None:
    with pytest.raises(ValueError):
        compute_unrealized_pnl_pct((1.0,), denominator_equity=-1.0)


def test_consecutive_losses_zero_when_most_recent_deal_is_a_win() -> None:
    deals = (
        DealRecord(profit=-10.0, close_time=AS_OF - 300),
        DealRecord(profit=-20.0, close_time=AS_OF - 200),
        DealRecord(profit=15.0, close_time=AS_OF - 100),  # most recent -- a win
    )
    losses, minutes = compute_consecutive_losses(deals, now=AS_OF)
    assert losses == 0
    assert minutes is None


def test_consecutive_losses_counts_the_trailing_losing_streak() -> None:
    deals = (
        DealRecord(profit=50.0, close_time=AS_OF - 10_000),  # a win, well before the streak
        DealRecord(profit=-10.0, close_time=AS_OF - 300),
        DealRecord(profit=-20.0, close_time=AS_OF - 200),
        DealRecord(profit=-5.0, close_time=AS_OF - 120),  # most recent -- a loss
    )
    losses, minutes = compute_consecutive_losses(deals, now=AS_OF)
    assert losses == 3
    assert minutes == pytest.approx(120 / 60.0)


def test_consecutive_losses_with_no_deals_is_zero() -> None:
    losses, minutes = compute_consecutive_losses((), now=AS_OF)
    assert losses == 0
    assert minutes is None


def test_consecutive_losses_a_zero_profit_deal_counts_as_a_loss_not_a_win() -> None:
    """Fail-safe direction: breakeven is not a "win" that would reset the streak silently."""
    deals = (DealRecord(profit=0.0, close_time=AS_OF - 60),)
    losses, minutes = compute_consecutive_losses(deals, now=AS_OF)
    assert losses == 1
    assert minutes == pytest.approx(1.0)
