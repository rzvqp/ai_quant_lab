"""`LiveBarFeed` tests -- the required, CEO-specified proof that a forming bar can never be emitted,
plus fail-closed and dedup behavior."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from ai_trader.live_signal_source.bar_feed import LiveBarFeed
from ai_trader.live_signal_source.tests._fixtures import FakeMT5Gateway, RawRate
from ai_trader.live_signal_source.types import BarFeedError, GapClassification
from ai_trader.persistent_state.store import SqliteStateStore

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


# -- Mandate 2 (2026-07-27): watermark persistence -- restart must be deterministic, never duplicate --


def test_watermark_survives_a_simulated_restart(tmp_path: Path) -> None:
    """The core acceptance proof: a brand-new `LiveBarFeed` instance, given the SAME `SqliteStateStore`
    (simulating a process restart, not just a fresh object), must not re-emit a bar the prior instance
    already emitted and persisted."""
    store = SqliteStateStore(tmp_path / "state.db")
    closed_open = NOW - 1_000
    gateway = FakeMT5Gateway(rates=[RawRate(time=closed_open, open=1.0, high=2.0, low=0.5, close=1.5)])

    feed_before_restart = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW, state_store=store,
    )
    first = feed_before_restart.poll()
    assert len(first) == 1

    # Simulated restart: a brand-new LiveBarFeed object, same store, same symbol/timeframe, same
    # underlying (unchanged) gateway data -- exactly what a real restart would see.
    feed_after_restart = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW, state_store=store,
    )
    second = feed_after_restart.poll()

    assert second == ()  # NOT re-emitted -- watermark was loaded from the store, not reset to None


def test_watermark_is_scoped_per_symbol_and_timeframe(tmp_path: Path) -> None:
    """Two different symbols must not share a watermark -- a bar closed for XAUUSD must never suppress
    an equally-timed bar for a different symbol."""
    store = SqliteStateStore(tmp_path / "state.db")
    closed_open = NOW - 1_000
    gateway_a = FakeMT5Gateway(rates=[RawRate(time=closed_open, open=1.0, high=2.0, low=0.5, close=1.5)])
    gateway_b = FakeMT5Gateway(rates=[RawRate(time=closed_open, open=1.0, high=2.0, low=0.5, close=1.5)])

    feed_a = LiveBarFeed(
        gateway_a, "XAUUSD", mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW, state_store=store,
    )
    feed_a.poll()

    feed_b = LiveBarFeed(
        gateway_b, "EURUSD", mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW, state_store=store,
    )
    assert len(feed_b.poll()) == 1  # a fresh symbol -- not suppressed by XAUUSD's own watermark


def test_without_a_state_store_nothing_is_persisted() -> None:
    """No `state_store` argument at all -- the exact prior, in-memory-only behavior -- is still the
    default; every other test in this file already proves this, this test names it explicitly."""
    closed_open = NOW - 1_000
    gateway = FakeMT5Gateway(rates=[RawRate(time=closed_open, open=1.0, high=2.0, low=0.5, close=1.5)])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)

    assert len(feed.poll()) == 1
    assert feed.poll() == ()  # in-memory dedup still works without any store at all


# -- Mandate 3, Element 1 (2026-07-27): gap continuity detection -- reported, never filled --


def _ts(year: int, month: int, day: int, hour: int, minute: int = 0) -> int:
    import datetime

    return int(datetime.datetime(year, month, day, hour, minute, tzinfo=datetime.timezone.utc).timestamp())


def test_no_gap_when_consecutive_bars_are_exactly_one_bar_apart() -> None:
    first_open = _ts(2026, 7, 28, 10, 0)  # Tuesday, ordinary mid-session hour
    gateway = FakeMT5Gateway(rates=[
        RawRate(time=first_open, open=1.0, high=2.0, low=0.5, close=1.5),
        RawRate(time=first_open + M15_SECONDS, open=1.5, high=2.5, low=1.0, close=2.0),
    ])
    feed = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS,
        clock=lambda: first_open + 2 * M15_SECONDS,
    )
    feed.poll()
    assert feed.last_gaps() == ()


def test_no_gap_flagged_for_the_very_first_bar_ever_seen() -> None:
    """No prior watermark exists yet -- there is nothing to compare against, so this must never be
    reported as a gap (a brand-new symbol/feed startup is not a continuity break)."""
    first_open = _ts(2026, 7, 28, 10, 0)
    gateway = FakeMT5Gateway(rates=[RawRate(time=first_open, open=1.0, high=2.0, low=0.5, close=1.5)])
    feed = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: first_open + M15_SECONDS,
    )
    feed.poll()
    assert feed.last_gaps() == ()


def test_unexpected_gap_within_a_single_poll_batch() -> None:
    first_open = _ts(2026, 7, 28, 10, 0)  # Tuesday
    second_open = first_open + 4 * 60 * 60  # 4 hours later -- not maintenance, not weekend
    gateway = FakeMT5Gateway(rates=[
        RawRate(time=first_open, open=1.0, high=2.0, low=0.5, close=1.5),
        RawRate(time=second_open, open=1.5, high=2.5, low=1.0, close=2.0),
    ])
    feed = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS,
        clock=lambda: second_open + M15_SECONDS,
    )
    feed.poll()

    gaps = feed.last_gaps()
    assert len(gaps) == 1
    assert gaps[0].symbol == SYMBOL
    assert gaps[0].gap_start == first_open
    assert gaps[0].gap_end == second_open
    assert gaps[0].duration_seconds == second_open - first_open
    assert gaps[0].classification == GapClassification.UNEXPECTED


class _MutableClock:
    def __init__(self, now: int) -> None:
        self.now = now

    def __call__(self) -> int:
        return self.now


def test_gap_detected_across_two_separate_poll_calls() -> None:
    first_open = _ts(2026, 7, 28, 10, 0)
    clock = _MutableClock(first_open + M15_SECONDS)
    gateway = FakeMT5Gateway(rates=[RawRate(time=first_open, open=1.0, high=2.0, low=0.5, close=1.5)])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=clock)
    feed.poll()
    assert feed.last_gaps() == ()

    second_open = first_open + 3 * 60 * 60
    gateway.rates = [RawRate(time=second_open, open=1.5, high=2.5, low=1.0, close=2.0)]
    clock.now = second_open + M15_SECONDS
    feed.poll()

    gaps = feed.last_gaps()
    assert len(gaps) == 1
    assert gaps[0].gap_start == first_open
    assert gaps[0].gap_end == second_open


def test_last_gaps_only_reflects_the_most_recent_poll() -> None:
    first_open = _ts(2026, 7, 28, 10, 0)
    second_open = first_open + 4 * 60 * 60
    gateway = FakeMT5Gateway(rates=[
        RawRate(time=first_open, open=1.0, high=2.0, low=0.5, close=1.5),
        RawRate(time=second_open, open=1.5, high=2.5, low=1.0, close=2.0),
    ])
    feed = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS,
        clock=lambda: second_open + M15_SECONDS,
    )
    feed.poll()
    assert len(feed.last_gaps()) == 1

    gateway.rates = []
    feed.poll()
    assert feed.last_gaps() == ()  # no NEW gap this poll -- not still reporting the old one


def test_maintenance_gap_is_classified_correctly() -> None:
    first_open = _ts(2026, 7, 28, 20, 0)  # Tuesday 20:00 UTC -- the documented daily break window
    second_open = first_open + 60 * 60  # 60 minutes later -- within the 75-minute allowance
    gateway = FakeMT5Gateway(rates=[
        RawRate(time=first_open, open=1.0, high=2.0, low=0.5, close=1.5),
        RawRate(time=second_open, open=1.5, high=2.5, low=1.0, close=2.0),
    ])
    feed = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS,
        clock=lambda: second_open + M15_SECONDS,
    )
    feed.poll()
    assert feed.last_gaps()[0].classification == GapClassification.MAINTENANCE


def test_weekend_gap_is_classified_correctly() -> None:
    first_open = _ts(2026, 7, 24, 21, 0)  # Friday close
    second_open = _ts(2026, 7, 26, 21, 0)  # Sunday reopen
    gateway = FakeMT5Gateway(rates=[
        RawRate(time=first_open, open=1.0, high=2.0, low=0.5, close=1.5),
        RawRate(time=second_open, open=1.5, high=2.5, low=1.0, close=2.0),
    ])
    feed = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS,
        clock=lambda: second_open + M15_SECONDS,
    )
    feed.poll()
    assert feed.last_gaps()[0].classification == GapClassification.WEEKEND


def test_gap_detection_uses_the_persisted_watermark_after_a_simulated_restart(tmp_path: Path) -> None:
    """A gap that occurred WHILE the process was down must still be detected after restart -- the
    watermark loaded from `SqliteStateStore` (Mandate 2) is exactly what continuity is checked
    against, no special-casing needed."""
    store = SqliteStateStore(tmp_path / "state.db")
    first_open = _ts(2026, 7, 28, 10, 0)
    gateway = FakeMT5Gateway(rates=[RawRate(time=first_open, open=1.0, high=2.0, low=0.5, close=1.5)])
    feed_before_restart = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS,
        clock=lambda: first_open + M15_SECONDS, state_store=store,
    )
    feed_before_restart.poll()

    second_open = first_open + 5 * 60 * 60  # a gap that happened during the "outage"
    gateway.rates = [RawRate(time=second_open, open=1.5, high=2.5, low=1.0, close=2.0)]
    feed_after_restart = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS,
        clock=lambda: second_open + M15_SECONDS, state_store=store,
    )
    feed_after_restart.poll()

    gaps = feed_after_restart.last_gaps()
    assert len(gaps) == 1
    assert gaps[0].gap_start == first_open
    assert gaps[0].gap_end == second_open
    assert gaps[0].classification == GapClassification.UNEXPECTED
