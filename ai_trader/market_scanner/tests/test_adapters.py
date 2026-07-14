"""Unit tests for ai_trader.market_scanner.adapters."""

import pytest

from ai_trader.market_scanner.adapters import DataSourceAdapter, ReplayAdapter
from ai_trader.market_scanner.types import CalendarEvent, ImpactLevel, Mode, RawBar, RawTick


def _bar(ts_open: int) -> RawBar:
    return RawBar(symbol="X", timeframe="M15", ts_open=ts_open, ts_close=ts_open + 900,
                  open=1.0, high=2.0, low=0.5, close=1.5, volume=1.0, complete=True)


def test_replay_adapter_yields_bars_in_given_order() -> None:
    bars = [_bar(0), _bar(900), _bar(1800)]
    adapter = ReplayAdapter(bars, source_id="unit-test")
    assert list(adapter.bars()) == bars
    assert adapter.mode == Mode.REPLAY
    assert adapter.source_id == "unit-test"


def test_replay_adapter_default_ticks_and_events_are_empty() -> None:
    adapter = ReplayAdapter([_bar(0)])
    assert list(adapter.ticks()) == []
    assert list(adapter.calendar_events()) == []


def test_replay_adapter_with_ticks_and_events() -> None:
    tick = RawTick(symbol="X", ts=100, bid=1.0, ask=1.1)
    event = CalendarEvent(ts=200, impact=ImpactLevel.HIGH, kind="nfp")
    adapter = ReplayAdapter([_bar(0)], ticks=[tick], calendar_events=[event])
    assert list(adapter.ticks()) == [tick]
    assert list(adapter.calendar_events()) == [event]


def test_replay_adapter_lab_parity_mode() -> None:
    adapter = ReplayAdapter([_bar(0)], mode=Mode.LAB_PARITY, source_id="research-csv")
    assert adapter.mode == Mode.LAB_PARITY


def test_data_source_adapter_is_abstract() -> None:
    with pytest.raises(TypeError):
        DataSourceAdapter()  # type: ignore[abstract]
