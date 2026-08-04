"""`ZoneObservingNullRecognitionRule` tests -- mirrors `structural_observer`'s own
`ObservingNullRecognitionRule` test shape: always returns `None`, always forwards the bar."""

from __future__ import annotations

from ai_trader.live_signal_source.types import Bar
from ai_trader.zone_observer.journal import ZoneObservationLog
from ai_trader.zone_observer.observer import ZoneObserver
from ai_trader.zone_observer.observing_rule import ZoneObservingNullRecognitionRule

SYMBOL = "XAUUSD"


def _bar(ts_open: int) -> Bar:
    return Bar(symbol=SYMBOL, ts_open=ts_open, ts_close=ts_open + 900, open=100.0, high=100.5, low=99.5, close=100.0, volume=10.0)


def test_evaluate_always_returns_none() -> None:
    journal = ZoneObservationLog()
    observer = ZoneObserver(SYMBOL, journal)
    rule = ZoneObservingNullRecognitionRule(observer)

    result = rule.evaluate(_bar(1_705_356_000))

    assert result is None


def test_evaluate_forwards_the_bar_to_the_observer() -> None:
    journal = ZoneObservationLog()
    observer = ZoneObserver(SYMBOL, journal)
    rule = ZoneObservingNullRecognitionRule(observer)

    rule.evaluate(_bar(1_705_356_000))
    rule.evaluate(_bar(1_705_356_900))

    assert observer.current_bar_count == 2
