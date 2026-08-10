"""`LiveBarFeed` tests -- the required, CEO-specified proof that a forming bar can never be emitted,
plus fail-closed and dedup behavior."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from ai_trader.live_signal_source.bar_feed import LiveBarFeed, make_broker_offset
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


def test_a_real_shaped_numpy_structured_array_is_read_correctly() -> None:
    """Discovered against the real terminal (2026-07-30): `copy_rates_from`/`copy_rates_range` actually
    return a numpy STRUCTURED ARRAY -- fields reached via `rate["time"]` item access, not `rate.time`
    attribute access -- unlike every other MetaTrader5 call this codebase reads. Every prior test above
    uses an attribute-accessible fake (`RawRate`/`SimpleNamespace`), which never exercised this shape;
    `poll()` silently treated every field as missing and raised `BarFeedError` on a genuinely closed bar
    the real terminal actually returned. This test uses `numpy.array` with the exact real dtype."""
    numpy = pytest.importorskip("numpy")
    closed_open = NOW - 1_000  # close = NOW - 1000 + 900 = NOW - 100 -- already in the past
    real_shaped_rates = numpy.array(
        [(closed_open, 2000.0, 2001.0, 1999.0, 2000.5, 100, 5, 0)],
        dtype=[
            ("time", "<i8"), ("open", "<f8"), ("high", "<f8"), ("low", "<f8"), ("close", "<f8"),
            ("tick_volume", "<u8"), ("spread", "<i4"), ("real_volume", "<u8"),
        ],
    )
    gateway = FakeMT5Gateway(rates=real_shaped_rates)
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)

    bars = feed.poll()

    assert len(bars) == 1
    assert bars[0].ts_open == closed_open
    assert bars[0].open == 2000.0
    assert bars[0].high == 2001.0
    assert bars[0].low == 1999.0
    assert bars[0].close == 2000.5
    assert bars[0].volume == 100.0


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
    """Backfill note, 2026-08-10: a 3h gap exceeds the 2.5h normal-lookback threshold, so the second
    `poll()` now goes through `copy_rates_range` (the backfill path), not `copy_rates_from` -- `rates`
    is mirrored into `range_rates` so this pre-backfill test still exercises the same scenario."""
    first_open = _ts(2026, 7, 28, 10, 0)
    clock = _MutableClock(first_open + M15_SECONDS)
    gateway = FakeMT5Gateway(rates=[RawRate(time=first_open, open=1.0, high=2.0, low=0.5, close=1.5)])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=clock)
    feed.poll()
    assert feed.last_gaps() == ()

    second_open = first_open + 3 * 60 * 60
    gateway.rates = [RawRate(time=second_open, open=1.5, high=2.5, low=1.0, close=2.0)]
    gateway.range_rates = gateway.rates
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
    against, no special-casing needed.

    Backfill note, 2026-08-10: the 5h outage gap exceeds the 2.5h normal-lookback threshold, so the
    post-restart `poll()` now goes through `copy_rates_range` (the backfill path) -- `range_rates` is
    populated to match, same as `test_gap_detected_across_two_separate_poll_calls`."""
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
    gateway.range_rates = gateway.rates
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


# -- Backfill, 2026-08-10: "la reconectare, fiecare proces trage barele lipsa din watermark pana la
# prezent... maxim 30 de zile inapoi. Peste, raporteaza si nu umple." --


def test_first_ever_poll_uses_the_normal_lookback_fetch_not_backfill() -> None:
    """No prior watermark -- there is nothing to be "behind" on, so this must be the ordinary
    `copy_rates_from` steady-state path, never `copy_rates_range`."""
    first_open = _ts(2026, 7, 28, 10, 0)
    gateway = FakeMT5Gateway(rates=[RawRate(time=first_open, open=1.0, high=2.0, low=0.5, close=1.5)])
    feed = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: first_open + M15_SECONDS,
    )
    bars = feed.poll()

    assert len(bars) == 1
    assert bars[0].is_backfilled is False
    assert len(gateway.copy_rates_range_calls) == 0
    assert len(gateway.copy_rates_from_calls) == 1


def test_a_small_gap_within_normal_lookback_does_not_trigger_backfill() -> None:
    """`lookback_count=10` at M15 covers 2.5h -- a gap smaller than that is still handled by the
    ordinary `copy_rates_from` fetch, exactly as before this feature existed."""
    first_open = _ts(2026, 7, 28, 10, 0)
    clock = _MutableClock(first_open + M15_SECONDS)
    gateway = FakeMT5Gateway(rates=[RawRate(time=first_open, open=1.0, high=2.0, low=0.5, close=1.5)])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=clock)
    feed.poll()

    second_open = first_open + 3 * M15_SECONDS  # 45 minutes later -- well within the 2.5h lookback
    gateway.rates = [RawRate(time=second_open, open=1.5, high=2.5, low=1.0, close=2.0)]
    clock.now = second_open + M15_SECONDS
    bars = feed.poll()

    assert len(bars) == 1
    assert bars[0].is_backfilled is False
    assert len(gateway.copy_rates_range_calls) == 0


def test_a_gap_beyond_normal_lookback_triggers_a_full_range_backfill() -> None:
    """The exact scenario the CEO named: `lookback_count=10` only recovers 9-10 bars regardless of gap
    size via `copy_rates_from` -- a gap larger than that must switch to `copy_rates_range` for the ENTIRE
    missing window, and every recovered bar must be marked `is_backfilled=True`. This scenario has MT5
    history for every single missing 15-minute bar (an ordinary intra-day, non-weekend outage) -- once
    backfilled, the recovered sequence is perfectly contiguous, so there is genuinely no gap left to
    report: the market never actually stopped, only this process's own observation did."""
    first_open = _ts(2026, 7, 28, 10, 0)
    clock = _MutableClock(first_open + M15_SECONDS)
    gateway = FakeMT5Gateway(rates=[RawRate(time=first_open, open=1.0, high=2.0, low=0.5, close=1.5)])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=clock)
    feed.poll()

    next_expected = first_open + M15_SECONDS
    second_open = first_open + 5 * 60 * 60  # 5 hours later -- well beyond the 2.5h normal lookback
    now = second_open + M15_SECONDS
    clock.now = now
    gateway.range_rates = [
        RawRate(time=next_expected + i * M15_SECONDS, open=1.0, high=2.0, low=0.5, close=1.5)
        for i in range((second_open - next_expected) // M15_SECONDS)
    ] + [RawRate(time=second_open, open=1.5, high=2.5, low=1.0, close=2.0)]
    gateway.rates = []  # copy_rates_from must NOT be the source of these bars

    bars = feed.poll()

    assert len(gateway.copy_rates_range_calls) == 1
    assert gateway.copy_rates_range_calls[0] == (SYMBOL, 15, next_expected, now)
    assert len(bars) > 1
    assert all(b.is_backfilled for b in bars)
    assert feed.last_gaps() == ()  # fully contiguous recovery -- nothing left to report


def test_backfill_recovers_bars_across_a_real_internal_weekend_gap() -> None:
    """The realistic shape of the CEO's own restart scenario: MT5's own history has NO bars for the
    actual weekend closure (the market itself was shut, not just this process), so even a fully
    successful backfill still surfaces that one genuine internal gap -- classified normally, and now
    carrying `bars_backfilled`/`backfill_capped` so a restart's recovery is visible, not just the gap's
    own existence."""
    first_open = _ts(2026, 7, 24, 20, 45)  # Friday, just before the broker's Friday close
    clock = _MutableClock(first_open + M15_SECONDS)
    gateway = FakeMT5Gateway(rates=[RawRate(time=first_open, open=1.0, high=2.0, low=0.5, close=1.5)])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=clock)
    feed.poll()

    weekend_reopen = _ts(2026, 7, 26, 21, 0)  # Sunday reopen -- MT5 has no bars in between
    now = weekend_reopen + 2 * M15_SECONDS
    clock.now = now
    gateway.range_rates = [
        RawRate(time=weekend_reopen, open=1.5, high=2.5, low=1.0, close=2.0),
        RawRate(time=weekend_reopen + M15_SECONDS, open=2.0, high=2.5, low=1.5, close=2.2),
    ]
    gateway.rates = []

    bars = feed.poll()

    assert len(bars) == 2
    assert all(b.is_backfilled for b in bars)

    gaps = feed.last_gaps()
    assert len(gaps) == 1
    assert gaps[0].gap_start == first_open
    assert gaps[0].gap_end == weekend_reopen
    assert gaps[0].classification == GapClassification.WEEKEND
    assert gaps[0].backfill_capped is False
    assert gaps[0].bars_backfilled == 2


def test_a_gap_beyond_the_30_day_cap_falls_back_to_normal_lookback_uncapped() -> None:
    """CEO's own explicit limit: "maxim 30 de zile inapoi. Peste, raporteaza si nu umple." -- beyond the
    cap, `poll()` must NOT attempt a range backfill; it falls back to the ordinary small lookback fetch,
    the bars it does return are NOT marked backfilled, and the gap's own `backfill_capped` flag makes the
    omission visible rather than silent."""
    first_open = _ts(2026, 6, 1, 10, 0)
    clock = _MutableClock(first_open + M15_SECONDS)
    gateway = FakeMT5Gateway(rates=[RawRate(time=first_open, open=1.0, high=2.0, low=0.5, close=1.5)])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=clock)
    feed.poll()

    second_open = first_open + 40 * 86_400  # 40 days later -- beyond MAX_BACKFILL_SECONDS (30 days)
    now = second_open + M15_SECONDS
    clock.now = now
    gateway.rates = [RawRate(time=second_open, open=1.5, high=2.5, low=1.0, close=2.0)]

    bars = feed.poll()

    assert len(gateway.copy_rates_range_calls) == 0  # never attempted -- the cap is respected
    assert len(bars) == 1
    assert bars[0].is_backfilled is False

    gaps = feed.last_gaps()
    assert len(gaps) == 1
    assert gaps[0].backfill_capped is True
    assert gaps[0].bars_backfilled == 0
    assert gaps[0].classification == GapClassification.EXTENDED_PAUSE  # 40 days, spans many Saturdays


# -- Broker-to-UTC translation at the source, 2026-08-11, take 2 (CEO decision, "Optiunea A"): MT5
# reports every timestamp in the broker/terminal's own server time, not true UTC. Rather than injecting
# a broker-aware `clock=` (take 1, reverted -- it left every downstream consumer of `Bar.ts_open` still
# assuming true UTC), `LiveBarFeed` now converts every raw MT5 timestamp to true UTC itself, via
# `broker_offset=make_broker_offset(...)` -- `clock=` goes back to meaning true system UTC.
#
# `make_broker_offset` measures via a dedicated M1 probe (`copy_rates_from(symbol, M1, ...)`), NOT
# `symbol_info_tick` (take 1 of THIS fix, also reverted -- discovered empirically that a tick's `.time`
# is the time of the last PRICE TICK, not a live clock, and drifts by tens of minutes during quiet
# periods). `_m1_probe_rate(offset_seconds, system_now)` below builds exactly the raw M1 rate that makes
# `make_broker_offset`'s own arithmetic (`latest_ts_open + 60 - system_now`) land on a given offset. --


def _m1_probe_rate(offset_seconds: int, system_now: int) -> list[RawRate]:
    latest_closed_ts_open = system_now + offset_seconds - 60
    return [RawRate(time=latest_closed_ts_open, open=1.0, high=1.0, low=1.0, close=1.0)]


def test_make_broker_offset_computes_broker_minus_system() -> None:
    gateway = FakeMT5Gateway(m1_probe_rates=_m1_probe_rate(10_800, NOW))  # 3h offset
    offset = make_broker_offset(gateway, SYMBOL, system_clock=lambda: NOW)

    assert offset() == 10_800


def test_make_broker_offset_reads_fresh_on_every_call_not_memoized() -> None:
    """The DST question the CEO raised directly: the offset can shift twice a year, so it must be
    recomputed from the terminal every time, never cached after the first read."""
    gateway = FakeMT5Gateway(m1_probe_rates=_m1_probe_rate(0, NOW))
    offset = make_broker_offset(gateway, SYMBOL, system_clock=lambda: NOW)
    assert offset() == 0

    gateway.m1_probe_rates = _m1_probe_rate(3_600, NOW)  # simulates the terminal's clock having moved
    assert offset() == 3_600


def test_make_broker_offset_raises_when_the_probe_returns_nothing() -> None:
    """Fail-closed, matching this project's own established convention -- a silent fallback to a zero
    or stale offset would quietly reintroduce the broker/UTC mismatch this exists to eliminate."""
    gateway = FakeMT5Gateway(m1_probe_rates=None)
    offset = make_broker_offset(gateway, SYMBOL, system_clock=lambda: NOW)

    with pytest.raises(BarFeedError):
        offset()


def test_make_broker_offset_first_ever_call_is_never_validated_against_staleness() -> None:
    """Nothing to compare against yet -- this project's own restart discipline only starts a process
    when the market is already known to be open, so the very first probe is trusted unconditionally."""
    gateway = FakeMT5Gateway(m1_probe_rates=_m1_probe_rate(0, NOW))
    offset = make_broker_offset(gateway, SYMBOL, system_clock=lambda: NOW)

    assert offset() == 0  # no prior state to compare against -- never raises on the first call


def test_make_broker_offset_does_not_raise_for_ordinary_polling_jitter() -> None:
    """A normal, continuously-open market: consecutive polls a few seconds apart, the bar keeps
    advancing roughly in step -- must never spuriously raise."""
    clock = _MutableClock(NOW)
    gateway = FakeMT5Gateway(m1_probe_rates=_m1_probe_rate(0, NOW))
    offset = make_broker_offset(gateway, SYMBOL, system_clock=clock)
    offset()

    clock.now = NOW + 30  # one ordinary poll interval later
    gateway.m1_probe_rates = _m1_probe_rate(0, clock.now)  # market kept trading, bar advanced too

    assert offset() == 0  # no exception


def test_make_broker_offset_raises_when_the_probe_is_stale_relative_to_the_last_fresh_read() -> None:
    """The market-closed scenario the CEO asked about directly: once the M1 bar stops advancing while
    real time keeps moving, that's unambiguous evidence of a closure -- not measurement noise, per the
    DERIVED (not chosen) `_OFFSET_PROBE_MAX_STALE_LAG_SECONDS` threshold."""
    clock = _MutableClock(NOW)
    gateway = FakeMT5Gateway(m1_probe_rates=_m1_probe_rate(0, NOW))
    offset = make_broker_offset(gateway, SYMBOL, system_clock=clock)
    offset()  # first call, establishes the freshness reference

    clock.now = NOW + 200  # real time advances well past the 60s threshold
    # gateway.m1_probe_rates left UNCHANGED -- the bar never advanced

    with pytest.raises(BarFeedError):
        offset()


def test_make_broker_offset_staleness_accumulates_across_many_quiet_polls() -> None:
    """The exact bug caught during design: if the freshness reference refreshed on EVERY call, staleness
    would never accumulate -- each individual poll would only ever compare against one poll interval
    ago. It must only refresh when the bar genuinely moves, so staleness keeps growing across a closure
    that spans many polls, not resetting every call."""
    clock = _MutableClock(NOW)
    gateway = FakeMT5Gateway(m1_probe_rates=_m1_probe_rate(0, NOW))
    offset = make_broker_offset(gateway, SYMBOL, system_clock=clock)
    offset()

    # Two consecutive "polls" 20s apart, bar never advances -- neither individually reaches the 60s
    # threshold, but they must not silently reset the freshness reference either.
    for _ in range(2):
        clock.now += 20
        offset()  # 20s, 40s of accumulated lag -- neither raises yet

    clock.now += 20  # 60s of accumulated lag now -- the derived threshold itself
    with pytest.raises(BarFeedError):
        offset()


def test_make_broker_offset_self_heals_once_the_market_reopens() -> None:
    """After a stretch with no new bar, a genuinely fresh bar (reflecting the real gap) must be accepted
    immediately -- the check compares elapsed real time against elapsed bar time, and once both jump
    together (the market reopening), there is no more lag."""
    clock = _MutableClock(NOW)
    gateway = FakeMT5Gateway(m1_probe_rates=_m1_probe_rate(0, NOW))
    offset = make_broker_offset(gateway, SYMBOL, system_clock=clock)
    offset()

    clock.now = NOW + 2 * 86_400  # a 2-day closure -- gateway.m1_probe_rates still frozen
    with pytest.raises(BarFeedError):
        offset()

    # Market reopens: a genuinely fresh bar appears, reflecting the real 2-day gap.
    gateway.m1_probe_rates = _m1_probe_rate(0, clock.now)
    assert offset() == 0  # accepted immediately, no exception


def test_make_broker_offset_queries_m1_far_in_the_future_to_get_the_true_latest_bar() -> None:
    gateway = FakeMT5Gateway(m1_probe_rates=_m1_probe_rate(10_800, NOW))
    offset = make_broker_offset(gateway, SYMBOL, system_clock=lambda: NOW)

    offset()

    assert len(gateway.copy_rates_from_calls) == 1
    symbol, timeframe, date_from, count = gateway.copy_rates_from_calls[0]
    assert timeframe == 1  # M1, independent of whatever timeframe the feed itself tracks
    assert date_from > NOW  # deliberately in the future relative to true "now"
    assert count == 1


def test_broker_offset_wired_into_live_bar_feed_converts_raw_timestamps_to_true_utc() -> None:
    """The exact production fix, reproduced end to end: a raw MT5 rate carrying a broker-shifted
    timestamp must be emitted as a `Bar` with a TRUE UTC `ts_open` -- not the raw broker value."""
    offset_seconds = 10_800  # 3h, matching the measured real case
    broker_ts_open = NOW - 1_000 + offset_seconds  # broker-labeled raw value MT5 actually returns
    gateway = FakeMT5Gateway(
        rates=[RawRate(time=broker_ts_open, open=1.0, high=2.0, low=0.5, close=1.5)],
        m1_probe_rates=_m1_probe_rate(offset_seconds, NOW),
    )
    feed = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW,
        broker_offset=make_broker_offset(gateway, SYMBOL, system_clock=lambda: NOW),
    )

    bars = feed.poll()

    assert len(bars) == 1
    assert bars[0].ts_open == NOW - 1_000  # true UTC -- the offset has been removed


def test_watermark_survives_a_stale_offset_and_backfills_correctly_once_fresh(tmp_path: Path) -> None:
    """CEO's own "consecinta, de confirmat": if the process keeps running through a closure (or gets
    restarted after one), `poll()` raising on every stale-offset attempt must NEVER corrupt the
    persisted watermark -- and once the market genuinely reopens, the existing backfill mechanism
    (2026-08-10) must correctly recover the whole missing window in one shot, exactly as it already does
    for any other multi-day gap."""
    store = SqliteStateStore(tmp_path / "state.db")
    watermark_key = f"live_signal_source.bar_feed:{SYMBOL}:15"
    clock = _MutableClock(NOW)
    offset_seconds = 0
    friday_close = NOW - 1_000
    gateway = FakeMT5Gateway(
        rates=[RawRate(time=friday_close, open=1.0, high=2.0, low=0.5, close=1.5)],
        m1_probe_rates=_m1_probe_rate(offset_seconds, NOW),
    )
    feed = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=clock, state_store=store,
        broker_offset=make_broker_offset(gateway, SYMBOL, system_clock=clock),
    )

    # Friday: normal poll, succeeds, watermark saved.
    bars = feed.poll()
    assert len(bars) == 1
    assert store.get_value(watermark_key) == float(friday_close)

    # Weekend: the M1 probe never advances (market closed) -- every poll attempt raises, and the
    # watermark must stay frozen at Friday's value across all of them.
    for hours_elapsed in (1, 24, 49, 72):
        clock.now = NOW + hours_elapsed * 3600
        with pytest.raises(BarFeedError):
            feed.poll()
        assert store.get_value(watermark_key) == float(friday_close)  # never corrupted

    # Monday: the market reopens -- a genuinely fresh M1 bar appears, reflecting the real gap.
    monday_reopen_broker_now = NOW + 73 * 3600
    clock.now = monday_reopen_broker_now
    gateway.m1_probe_rates = _m1_probe_rate(offset_seconds, monday_reopen_broker_now)
    monday_bar_open = monday_reopen_broker_now - 1_000  # closed -- ts_close is safely before "now"
    gateway.rates = []
    gateway.range_rates = [
        RawRate(time=monday_bar_open, open=2.0, high=2.5, low=1.5, close=2.2),
    ]

    bars = feed.poll()  # backfill path: gap far exceeds lookback_count * bar_seconds

    assert len(bars) == 1
    assert bars[0].is_backfilled is True
    gaps = feed.last_gaps()
    assert len(gaps) == 1
    assert gaps[0].gap_start == friday_close
    assert gaps[0].gap_end == monday_bar_open
    assert store.get_value(watermark_key) == float(monday_bar_open)  # resumed correctly


def test_broker_offset_none_leaves_timestamps_unconverted() -> None:
    """Backward compatible by construction: no `broker_offset=` at all means every existing caller
    (every test in this file above this section, every caller that never knew about broker time) keeps
    working byte-for-byte unchanged."""
    closed_open = NOW - 1_000
    gateway = FakeMT5Gateway(rates=[RawRate(time=closed_open, open=1.0, high=2.0, low=0.5, close=1.5)])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)

    bars = feed.poll()

    assert len(bars) == 1
    assert bars[0].ts_open == closed_open


def test_broker_offset_applied_to_outgoing_mt5_query_timestamps_too() -> None:
    """MT5's own API still expects broker-epoch `date_from`/`date_to` -- the translation only happens
    at this file's own boundary, on the way in (raw rate -> `Bar`) and on the way out (true-UTC `now` ->
    the query MT5 actually receives)."""
    offset_seconds = 10_800
    gateway = FakeMT5Gateway(m1_probe_rates=_m1_probe_rate(offset_seconds, NOW))
    feed = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW,
        broker_offset=make_broker_offset(gateway, SYMBOL, system_clock=lambda: NOW),
    )

    feed.poll()

    m15_calls = [c for c in gateway.copy_rates_from_calls if c[1] == 15]
    assert len(m15_calls) == 1
    assert m15_calls[0][2] == NOW + offset_seconds  # date_from, broker-shifted


def test_clock_corrected_since_watermark_is_recorded_once(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    offset_seconds = 10_800
    gateway = FakeMT5Gateway(
        rates=[RawRate(time=NOW - 1_000 + offset_seconds, open=1.0, high=2.0, low=0.5, close=1.5)],
        m1_probe_rates=_m1_probe_rate(offset_seconds, NOW),
    )
    feed = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW, state_store=store,
        broker_offset=make_broker_offset(gateway, SYMBOL, system_clock=lambda: NOW),
    )

    feed.poll()

    key = "live_signal_source.bar_feed:XAUUSD:15.clock_corrected_since"
    assert store.get_value(key) == float(NOW)


def test_clock_corrected_since_watermark_is_never_overwritten(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    key = "live_signal_source.bar_feed:XAUUSD:15.clock_corrected_since"
    offset_seconds = 10_800
    clock = _MutableClock(NOW)
    gateway = FakeMT5Gateway(rates=[], m1_probe_rates=_m1_probe_rate(offset_seconds, NOW))
    feed = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=clock, state_store=store,
        broker_offset=make_broker_offset(gateway, SYMBOL, system_clock=clock),
    )
    feed.poll()
    assert store.get_value(key) == float(NOW)

    clock.now = NOW + 3_600
    gateway.m1_probe_rates = _m1_probe_rate(offset_seconds, NOW + 3_600)
    feed.poll()

    assert store.get_value(key) == float(NOW)  # unchanged -- the FIRST correction time, not the latest


def test_without_broker_offset_no_watermark_is_recorded(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    gateway = FakeMT5Gateway(rates=[RawRate(time=NOW - 1_000, open=1.0, high=2.0, low=0.5, close=1.5)])
    feed = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW, state_store=store,
    )

    feed.poll()

    key = "live_signal_source.bar_feed:XAUUSD:15.clock_corrected_since"
    assert store.get_value(key) is None
