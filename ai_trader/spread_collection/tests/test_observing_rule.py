"""`SpreadCollectingNullRecognitionRule` tests -- mirrors `structural_observer`'s own
`ObservingNullRecognitionRule` test shape: always returns `None`, always forwards the bar."""

from __future__ import annotations

from ai_trader.live_signal_source.types import Bar
from ai_trader.pdh_pdl_demo.types import LiveTick
from ai_trader.spread_collection.journal import SpreadObservationLog
from ai_trader.spread_collection.observer import SpreadCollector
from ai_trader.spread_collection.observing_rule import SpreadCollectingNullRecognitionRule

SYMBOL = "XAUUSD"


class _FakeTickReader:
    def __init__(self, tick: LiveTick | None) -> None:
        self._tick = tick

    def read(self, symbol: str) -> LiveTick | None:
        return self._tick


def _bar(ts_open: int) -> Bar:
    return Bar(symbol=SYMBOL, ts_open=ts_open, ts_close=ts_open + 900, open=100.0, high=100.5, low=99.5, close=100.0, volume=10.0)


def test_evaluate_always_returns_none() -> None:
    journal = SpreadObservationLog()
    collector = SpreadCollector(SYMBOL, _FakeTickReader(LiveTick(bid=99.9, ask=100.1, as_of=1_705_356_000)), journal)
    rule = SpreadCollectingNullRecognitionRule(collector)

    result = rule.evaluate(_bar(1_705_356_000))

    assert result is None


def test_evaluate_forwards_the_bar_to_the_collector() -> None:
    journal = SpreadObservationLog()
    collector = SpreadCollector(SYMBOL, _FakeTickReader(LiveTick(bid=99.9, ask=100.1, as_of=1_705_356_000)), journal)
    rule = SpreadCollectingNullRecognitionRule(collector)

    rule.evaluate(_bar(1_705_356_000))

    assert collector.current_bar_count == 1
    assert len(journal.entries) == 1


def test_evaluate_still_returns_none_when_the_tick_is_unavailable() -> None:
    journal = SpreadObservationLog()
    collector = SpreadCollector(SYMBOL, _FakeTickReader(None), journal)
    rule = SpreadCollectingNullRecognitionRule(collector)

    result = rule.evaluate(_bar(1_705_356_000))

    assert result is None
    assert collector.current_bar_count == 1  # bar still accumulated for level-touch continuity
    assert journal.entries == ()  # but no observation recorded (no tick)
