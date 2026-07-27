"""`LiveBarFeed` tests -- the required, CEO-specified proof that a forming bar can never be emitted,
plus fail-closed and dedup behavior."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from ai_trader.live_signal_source.bar_feed import LiveBarFeed
from ai_trader.live_signal_source.tests._fixtures import FakeMT5Gateway, RawRate
from ai_trader.live_signal_source.types import BarFeedError

SYMBOL = "XAUUSD"
M15_SECONDS = 15 * 60
NOW = 1_700_000_000


def test_a_forming_bar_can_never_be_emitted() -> None:
    """The exact scenario the CEO named, 2026-07-26: a bar whose close time has not yet passed must
    never be returned -- filtered out silently, not an error."""
    forming_open = NOW - 100  # close = NOW - 100 + 900 = NOW + 800 -- still 800s in the future
    gateway = FakeMT5Gateway(rates=[RawRate(time=forming_open, open=2000.0, high=2001.0, low=1999.0, close=2000.5)])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)

    bars = feed.poll()

    assert bars == ()


def test_a_genuinely_closed_bar_is_emitted() -> None:
    closed_open = NOW - 1_000  # close = NOW - 1000 + 900 = NOW - 100 -- already in the past
    gateway = FakeMT5Gateway(rates=[RawRate(time=closed_open, open=2000.0, high=2001.0, low=1999.0, close=2000.5)])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)

    bars = feed.poll()

    assert len(bars) == 1
    assert bars[0].symbol == SYMBOL
    assert bars[0].ts_open == closed_open
    assert bars[0].ts_close == closed_open + M15_SECONDS
    assert bars[0].close == 2000.5


def test_a_bar_exactly_at_its_close_boundary_is_emitted() -> None:
    """ts_close == now is closed, not forming -- the boundary belongs to "closed" (`>` not `>=` in the
    forming check), matching the docstring's own "close time has not yet passed" wording."""
    boundary_open = NOW - M15_SECONDS  # close == NOW exactly
    gateway = FakeMT5Gateway(rates=[RawRate(time=boundary_open, open=1.0, high=2.0, low=0.5, close=1.5)])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)

    bars = feed.poll()

    assert len(bars) == 1


def test_already_emitted_bar_is_not_returned_again() -> None:
    closed_open = NOW - 1_000
    gateway = FakeMT5Gateway(rates=[RawRate(time=closed_open, open=1.0, high=2.0, low=0.5, close=1.5)])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)

    first = feed.poll()
    second = feed.poll()

    assert len(first) == 1
    assert second == ()


def test_a_newer_closed_bar_is_emitted_after_dedup_of_the_older_one() -> None:
    older_open = NOW - 2_000
    newer_open = NOW - 1_000
    gateway = FakeMT5Gateway(rates=[
        RawRate(time=older_open, open=1.0, high=2.0, low=0.5, close=1.5),
        RawRate(time=newer_open, open=1.5, high=2.5, low=1.0, close=2.0),
    ])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)

    first = feed.poll()
    assert [b.ts_open for b in first] == [older_open, newer_open]

    gateway.rates = [RawRate(time=newer_open, open=1.5, high=2.5, low=1.0, close=2.0)]
    second = feed.poll()
    assert second == ()


def test_raises_when_gateway_returns_none() -> None:
    gateway = FakeMT5Gateway(rates=None)
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)

    with pytest.raises(BarFeedError):
        feed.poll()


def test_raises_when_a_rate_is_missing_a_required_field() -> None:
    incomplete = SimpleNamespace(time=NOW - 1_000, open=1.0, high=2.0)  # missing low/close
    gateway = FakeMT5Gateway(rates=[incomplete])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)

    with pytest.raises(BarFeedError):
        feed.poll()


def test_bar_seconds_must_be_positive() -> None:
    with pytest.raises(ValueError):
        LiveBarFeed(FakeMT5Gateway(), SYMBOL, mt5_timeframe=15, bar_seconds=0)


def test_lookback_count_must_be_positive() -> None:
    with pytest.raises(ValueError):
        LiveBarFeed(FakeMT5Gateway(), SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, lookback_count=0)
