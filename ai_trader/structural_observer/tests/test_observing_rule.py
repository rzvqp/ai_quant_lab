"""`ObservingNullRecognitionRule` -- proves the actual wiring point: a real `LiveBarFeed` +
`CandidateSignalProducer`, injected with this rule instead of a bare `NullRecognitionRule`, produces
zero candidates (identical to `NullRecognitionRule`'s own contract) while the `StructuralObserver`
behind it genuinely receives and records every bar."""

from __future__ import annotations

from ai_trader.live_signal_source.bar_feed import LiveBarFeed
from ai_trader.live_signal_source.journal import LiveSignalJournal
from ai_trader.live_signal_source.producer import CandidateSignalProducer
from ai_trader.live_signal_source.tests._fixtures import FakeMT5Gateway, RawRate
from ai_trader.live_signal_source.types import Bar, LiveCandidate
from ai_trader.structural_observer.journal import StructuralObservationLog
from ai_trader.structural_observer.observer import StructuralObserver
from ai_trader.structural_observer.observing_rule import ObservingNullRecognitionRule
from ai_trader.structural_observer.types import StructuralEventKind

SYMBOL = "XAUUSD"
M15_SECONDS = 15 * 60
NOW = 1_700_000_000


def _closed_bar_gateway(*ts_opens: int) -> FakeMT5Gateway:
    return FakeMT5Gateway(rates=[
        RawRate(time=ts, open=2000.0, high=2001.0, low=1999.0, close=2000.5) for ts in ts_opens
    ])


def test_observing_rule_never_produces_a_candidate() -> None:
    gateway = _closed_bar_gateway(NOW - 2_000, NOW - 1_000)
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)
    signal_journal = LiveSignalJournal()
    structural_journal = StructuralObservationLog()
    observer = StructuralObserver(SYMBOL, structural_journal)
    producer = CandidateSignalProducer(feed, ObservingNullRecognitionRule(observer), signal_journal)

    candidates = producer.run_once()

    assert candidates == ()


def test_observing_rule_forwards_every_bar_to_the_structural_observer() -> None:
    gateway = _closed_bar_gateway(NOW - 2_000, NOW - 1_000)
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)
    signal_journal = LiveSignalJournal()
    structural_journal = StructuralObservationLog()
    observer = StructuralObserver(SYMBOL, structural_journal)
    producer = CandidateSignalProducer(feed, ObservingNullRecognitionRule(observer), signal_journal)

    producer.run_once()

    regimes = [e for e in structural_journal.entries if e.kind is StructuralEventKind.REGIME]
    assert len(regimes) == 2  # one REGIME observation per bar the feed emitted this poll


def test_observing_rule_evaluate_returns_none_directly() -> None:
    structural_journal = StructuralObservationLog()
    observer = StructuralObserver(SYMBOL, structural_journal)
    rule = ObservingNullRecognitionRule(observer)
    bar = Bar(symbol=SYMBOL, ts_open=NOW, ts_close=NOW + M15_SECONDS,
              open=2000.0, high=2001.0, low=1999.0, close=2000.5, volume=None)

    result: LiveCandidate | None = rule.evaluate(bar)

    assert result is None
    assert len(structural_journal.entries) > 0
