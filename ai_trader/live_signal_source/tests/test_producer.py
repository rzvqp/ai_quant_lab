"""`CandidateSignalProducer` tests -- including the CEO's own acceptance test for #6: the system runs
end-to-end, through `NullRecognitionRule`, and produces zero candidates."""

from __future__ import annotations

from ai_trader.live_signal_source.bar_feed import LiveBarFeed
from ai_trader.live_signal_source.journal import LiveSignalJournal
from ai_trader.live_signal_source.producer import CandidateSignalProducer
from ai_trader.live_signal_source.tests._fixtures import FakeMT5Gateway, RawRate
from ai_trader.live_signal_source.types import Bar, LiveCandidate, NullRecognitionRule
from ai_trader.signal_engine.types import Direction

SYMBOL = "XAUUSD"
M15_SECONDS = 15 * 60
NOW = 1_700_000_000


class _AlwaysLongRule:
    """Test-only `RecognitionRule` -- NOT shipped, exists only to prove the producer correctly passes
    through whatever a real rule (someday) would return."""

    def evaluate(self, bar: Bar) -> LiveCandidate | None:
        return LiveCandidate(
            strategy_id="TEST_STRATEGY", symbol=bar.symbol, direction=Direction.LONG,
            entry=bar.close, stop=bar.close - 1.0, target=None, session="LONDON",
            magic_number=1, comment="test", as_of=bar.ts_close,
        )


def _closed_bar_gateway(*ts_opens: int) -> FakeMT5Gateway:
    return FakeMT5Gateway(rates=[
        RawRate(time=ts, open=2000.0, high=2001.0, low=1999.0, close=2000.5) for ts in ts_opens
    ])


def test_null_rule_produces_zero_candidates_end_to_end() -> None:
    """The CEO's own acceptance test for #6, verbatim: the system runs cap-coada (end to end) and
    produces zero candidates."""
    gateway = _closed_bar_gateway(NOW - 2_000, NOW - 1_000)
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)
    journal = LiveSignalJournal()
    producer = CandidateSignalProducer(feed, NullRecognitionRule(), journal)

    candidates = producer.run_once()

    assert candidates == ()


def test_null_rule_still_journals_every_observed_bar() -> None:
    """The "eyes" the CEO described: even with zero candidates, the journal proves bars were observed."""
    gateway = _closed_bar_gateway(NOW - 2_000, NOW - 1_000)
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)
    journal = LiveSignalJournal()
    producer = CandidateSignalProducer(feed, NullRecognitionRule(), journal)

    producer.run_once()

    assert len(journal.entries) == 2
    assert all(entry.candidate is None for entry in journal.entries)
    assert all(entry.symbol == SYMBOL for entry in journal.entries)


def test_a_rule_that_returns_a_candidate_is_passed_through_and_journaled() -> None:
    gateway = _closed_bar_gateway(NOW - 1_000)
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)
    journal = LiveSignalJournal()
    producer = CandidateSignalProducer(feed, _AlwaysLongRule(), journal)

    candidates = producer.run_once()

    assert len(candidates) == 1
    assert candidates[0].direction is Direction.LONG
    assert len(journal.entries) == 1
    assert journal.entries[0].candidate is candidates[0]


def test_no_new_bars_produces_nothing_and_journals_nothing() -> None:
    gateway = FakeMT5Gateway(rates=[])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)
    journal = LiveSignalJournal()
    producer = CandidateSignalProducer(feed, NullRecognitionRule(), journal)

    candidates = producer.run_once()

    assert candidates == ()
    assert journal.entries == ()


def test_a_gap_detected_by_the_feed_is_journaled_by_the_producer() -> None:
    """Mandate 3, Element 1 (2026-07-27): the producer is what connects `LiveBarFeed.last_gaps()` to
    the journal -- the feed only detects, it never journals on its own."""
    first_open = NOW - 5 * 60 * 60
    second_open = NOW - 1_000
    gateway = _closed_bar_gateway(first_open, second_open)
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)
    journal = LiveSignalJournal()
    producer = CandidateSignalProducer(feed, NullRecognitionRule(), journal)

    producer.run_once()

    assert len(journal.gaps) == 1
    assert journal.gaps[0].gap_start == first_open
    assert journal.gaps[0].gap_end == second_open


class _MutableClock:
    def __init__(self, now: int) -> None:
        self.now = now

    def __call__(self) -> int:
        return self.now


def test_a_backfilled_bar_is_journaled_with_is_backfilled_true() -> None:
    """Backfill, 2026-08-10: the journal entry must carry through whatever `Bar.is_backfilled` the feed
    marked the bar with -- this is the producer's own propagation responsibility, not the feed's."""
    first_open = NOW - 10 * M15_SECONDS
    clock = _MutableClock(first_open + M15_SECONDS)
    gateway = _closed_bar_gateway(first_open)
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=clock)
    journal = LiveSignalJournal()
    producer = CandidateSignalProducer(feed, NullRecognitionRule(), journal)
    producer.run_once()
    assert journal.entries[0].is_backfilled is False  # ordinary steady-state fetch, not a backfill

    second_open = first_open + 5 * 60 * 60  # well beyond the 2.5h normal lookback -- triggers backfill
    clock.now = second_open + M15_SECONDS
    gateway.range_rates = [RawRate(time=second_open, open=2000.0, high=2001.0, low=1999.0, close=2000.5)]
    gateway.rates = []

    producer.run_once()

    assert journal.entries[1].is_backfilled is True


def test_no_gap_is_journaled_when_bars_are_contiguous() -> None:
    first_open = NOW - 2 * M15_SECONDS
    gateway = _closed_bar_gateway(first_open, first_open + M15_SECONDS)
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)
    journal = LiveSignalJournal()
    producer = CandidateSignalProducer(feed, NullRecognitionRule(), journal)

    producer.run_once()

    assert journal.gaps == ()
