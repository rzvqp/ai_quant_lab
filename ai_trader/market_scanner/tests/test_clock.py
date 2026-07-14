"""Unit tests for ai_trader.market_scanner.clock.ClockController."""

import pytest

from ai_trader.market_scanner.bar_store import SymbolBarStore
from ai_trader.market_scanner.clock import ClockController
from ai_trader.market_scanner.types import RawBar

_M15 = 900


def _bar(symbol: str, tf: str, ts_open: int) -> RawBar:
    secs = {"M15": 900, "H1": 3600}[tf]
    return RawBar(symbol=symbol, timeframe=tf, ts_open=ts_open, ts_close=ts_open + secs,
                  open=1.0, high=2.0, low=0.5, close=1.5, volume=1.0, complete=True)


def test_advance_reports_newly_closed_bars_only_once() -> None:
    store = SymbolBarStore("XAUUSD")
    w = store.ensure_timeframe("M15", 10)
    w.ingest_bar(_bar("XAUUSD", "M15", 0))
    clock = ClockController()
    closes1 = clock.advance(_M15, {"XAUUSD": store})
    assert len(closes1) == 1 and closes1[0].ts_close == _M15
    closes2 = clock.advance(_M15, {"XAUUSD": store})  # same as_of again: nothing new
    assert closes2 == []


def test_advance_reports_backlog_in_order() -> None:
    store = SymbolBarStore("XAUUSD")
    w = store.ensure_timeframe("M15", 10)
    for i in range(3):
        w.ingest_bar(_bar("XAUUSD", "M15", i * _M15))
    clock = ClockController()
    closes = clock.advance(3 * _M15, {"XAUUSD": store})
    assert [c.ts_close for c in closes] == [_M15, 2 * _M15, 3 * _M15]


def test_advance_cannot_move_backward() -> None:
    clock = ClockController()
    clock.advance(1000, {})
    with pytest.raises(ValueError, match="backward"):
        clock.advance(999, {})


def test_advance_multi_symbol_multi_timeframe_ordering() -> None:
    store_a = SymbolBarStore("A")
    store_a.ensure_timeframe("M15", 10).ingest_bar(_bar("A", "M15", 0))
    store_b = SymbolBarStore("B")
    store_b.ensure_timeframe("H1", 10).ingest_bar(_bar("B", "H1", 0))
    clock = ClockController()
    closes = clock.advance(3600, {"A": store_a, "B": store_b})
    keys = [(c.symbol, c.timeframe, c.ts_close) for c in closes]
    assert ("A", "M15", 900) in keys
    assert ("B", "H1", 3600) in keys
    # deterministic ordering: sorted by (ts_close, symbol, timeframe)
    assert keys == sorted(keys)
