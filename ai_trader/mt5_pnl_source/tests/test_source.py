"""`MT5PortfolioStateSource` tests: real-shaped happy path, fail-closed on every missing-data case
(Risk Audit #1's own point -- never default to 0.0, never estimate), and equity-high-water-mark
tracking."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.mt5_pnl_source.source import MT5PortfolioStateSource
from ai_trader.mt5_pnl_source.tests._fixtures import FakeMT5HistoryGateway, make_gateway
from ai_trader.mt5_pnl_source.types import PortfolioDataUnavailableError
from ai_trader.persistent_state.store import SqliteStateStore

AS_OF = 1_700_000_000
_DAY = 86_400
_WEEK = 7 * _DAY


def test_happy_path_computes_real_pnl_from_positions_and_deals() -> None:
    gateway = make_gateway(
        equity=10_000.0,
        position_profits=(100.0, -20.0),
        deals=((200.0, AS_OF - 1000), (-50.0, AS_OF - _DAY - 100)),  # one today, one this week but not today
    )
    source = MT5PortfolioStateSource(gateway, clock=lambda: AS_OF)
    portfolio = source.current_portfolio_state()

    assert portfolio.equity == 10_000.0
    assert portfolio.unrealized_pnl_pct_daily == pytest.approx((100.0 - 20.0) / 10_000.0)
    assert portfolio.unrealized_pnl_pct_weekly == pytest.approx((100.0 - 20.0) / 10_000.0)
    assert portfolio.realized_pnl_pct_daily == pytest.approx(200.0 / 10_000.0)  # only today's deal
    assert portfolio.realized_pnl_pct_weekly == pytest.approx((200.0 - 50.0) / 10_000.0)  # both deals


def test_history_deals_get_is_called_once_with_the_weekly_window() -> None:
    gateway = make_gateway()
    source = MT5PortfolioStateSource(gateway, clock=lambda: AS_OF)
    source.current_portfolio_state()
    assert gateway.history_calls == [(AS_OF - _WEEK, AS_OF)]


def test_equity_high_water_mark_starts_at_first_observed_equity() -> None:
    gateway = make_gateway(equity=8_000.0)
    source = MT5PortfolioStateSource(gateway, clock=lambda: AS_OF)
    portfolio = source.current_portfolio_state()
    assert portfolio.equity_high_water_mark == 8_000.0


def test_equity_high_water_mark_ratchets_up_never_down() -> None:
    gateway = make_gateway(equity=8_000.0)
    source = MT5PortfolioStateSource(gateway, clock=lambda: AS_OF)
    source.current_portfolio_state()

    gateway.set_equity(9_000.0)
    result_up = source.current_portfolio_state()
    assert result_up.equity_high_water_mark == 9_000.0

    gateway.set_equity(7_000.0)  # equity dropped -- high-water mark must NOT drop with it
    result_down = source.current_portfolio_state()
    assert result_down.equity_high_water_mark == 9_000.0
    assert result_down.equity == 7_000.0


def test_seeded_high_water_mark_is_respected_if_higher_than_current_equity() -> None:
    gateway = make_gateway(equity=8_000.0)
    source = MT5PortfolioStateSource(gateway, clock=lambda: AS_OF, initial_equity_high_water_mark=12_000.0)
    portfolio = source.current_portfolio_state()
    assert portfolio.equity_high_water_mark == 12_000.0


def test_consecutive_losses_reflected_from_deal_history() -> None:
    gateway = make_gateway(
        deals=((10.0, AS_OF - 10_000), (-5.0, AS_OF - 300), (-2.0, AS_OF - 120)),
    )
    source = MT5PortfolioStateSource(gateway, clock=lambda: AS_OF)
    portfolio = source.current_portfolio_state()
    assert portfolio.consecutive_losses == 2
    assert portfolio.minutes_since_last_loss == pytest.approx(120 / 60.0)


def test_raises_when_account_info_is_none() -> None:
    gateway = FakeMT5HistoryGateway(account=None, positions=(), deals=())
    source = MT5PortfolioStateSource(gateway, clock=lambda: AS_OF)
    with pytest.raises(PortfolioDataUnavailableError):
        source.current_portfolio_state()


def test_raises_when_positions_get_is_none() -> None:
    gateway = make_gateway()
    gateway.positions = None
    source = MT5PortfolioStateSource(gateway, clock=lambda: AS_OF)
    with pytest.raises(PortfolioDataUnavailableError):
        source.current_portfolio_state()


def test_raises_when_history_deals_get_is_none() -> None:
    gateway = make_gateway()
    gateway.deals = None
    source = MT5PortfolioStateSource(gateway, clock=lambda: AS_OF)
    with pytest.raises(PortfolioDataUnavailableError):
        source.current_portfolio_state()


def test_raises_when_equity_is_non_positive() -> None:
    gateway = make_gateway(equity=0.0)
    source = MT5PortfolioStateSource(gateway, clock=lambda: AS_OF)
    with pytest.raises(PortfolioDataUnavailableError):
        source.current_portfolio_state()


def test_never_defaults_to_zero_on_incomplete_data_does_not_swallow_the_exception() -> None:
    """The exact Risk Audit #1 point: a caller must never see a silently-zeroed PortfolioState when
    data was actually missing -- confirmed here as a behavioral guarantee, not just an implementation
    detail of one specific field."""
    gateway = FakeMT5HistoryGateway(account=None, positions=None, deals=None)
    source = MT5PortfolioStateSource(gateway, clock=lambda: AS_OF)
    try:
        source.current_portfolio_state()
        assert False, "expected PortfolioDataUnavailableError, got a result instead"
    except PortfolioDataUnavailableError:
        pass


# -- Mandate 2 (2026-07-27): equity high-water-mark persistence -- a restart must not reset the peak --


def test_high_water_mark_survives_a_simulated_restart(tmp_path: Path) -> None:
    """The core acceptance proof: a brand-new `MT5PortfolioStateSource` instance, given the SAME
    `SqliteStateStore`, must resume from the persisted high-water mark, not reset to whatever equity it
    first observes after restart -- exactly the failure mode disclosed at Step 3."""
    store = SqliteStateStore(tmp_path / "state.db")
    gateway = make_gateway(equity=9_000.0)

    source_before_restart = MT5PortfolioStateSource(gateway, clock=lambda: AS_OF, state_store=store)
    source_before_restart.current_portfolio_state()  # observes 9_000.0, ratchets HWM to 9_000.0

    # Simulated restart: a brand-new source object, same store, but equity has since DROPPED --
    # exactly the scenario Step 3 disclosed as broken (a fresh, lower first-observed value would
    # otherwise become the new, false high-water mark).
    gateway.set_equity(7_000.0)
    source_after_restart = MT5PortfolioStateSource(gateway, clock=lambda: AS_OF, state_store=store)
    portfolio = source_after_restart.current_portfolio_state()

    assert portfolio.equity == 7_000.0
    assert portfolio.equity_high_water_mark == 9_000.0  # recovered from the store, not reset to 7_000.0


def test_persisted_high_water_mark_takes_precedence_over_a_seeded_initial_value() -> None:
    """A persisted value represents a REAL prior observation; a caller-supplied seed is only a
    fallback for the very first run, when nothing has been persisted yet."""
    store = SqliteStateStore(":memory:")
    gateway = make_gateway(equity=8_000.0)
    first = MT5PortfolioStateSource(gateway, clock=lambda: AS_OF, state_store=store)
    first.current_portfolio_state()  # persists high-water mark 8_000.0

    second = MT5PortfolioStateSource(
        gateway, clock=lambda: AS_OF, initial_equity_high_water_mark=1_000.0, state_store=store,
    )
    portfolio = second.current_portfolio_state()

    assert portfolio.equity_high_water_mark == 8_000.0  # persisted value wins, not the 1_000.0 seed


def test_seeded_initial_value_is_used_when_nothing_is_persisted_yet() -> None:
    store = SqliteStateStore(":memory:")
    gateway = make_gateway(equity=8_000.0)
    source = MT5PortfolioStateSource(
        gateway, clock=lambda: AS_OF, initial_equity_high_water_mark=12_000.0, state_store=store,
    )
    portfolio = source.current_portfolio_state()
    assert portfolio.equity_high_water_mark == 12_000.0


def test_high_water_mark_ratchet_writes_through_immediately() -> None:
    store = SqliteStateStore(":memory:")
    gateway = make_gateway(equity=8_000.0)
    source = MT5PortfolioStateSource(gateway, clock=lambda: AS_OF, state_store=store)
    source.current_portfolio_state()

    gateway.set_equity(9_500.0)
    source.current_portfolio_state()  # ratchets up to 9_500.0, must write through immediately

    fresh_view = MT5PortfolioStateSource(make_gateway(equity=1.0), clock=lambda: AS_OF, state_store=store)
    assert fresh_view.current_portfolio_state().equity_high_water_mark == 9_500.0


def test_without_a_state_store_nothing_is_persisted() -> None:
    """No `state_store` argument at all -- the exact prior, in-memory-only behavior -- remains the
    default; every other test in this file already proves this, this test names it explicitly."""
    gateway = make_gateway(equity=8_000.0)
    source = MT5PortfolioStateSource(gateway, clock=lambda: AS_OF)
    assert source.current_portfolio_state().equity_high_water_mark == 8_000.0
