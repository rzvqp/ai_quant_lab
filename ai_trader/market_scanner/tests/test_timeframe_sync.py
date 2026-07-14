"""Unit tests for ai_trader.market_scanner.timeframe_sync — the lookahead-safety core."""

from ai_trader.market_scanner.bar_store import TimeframeWindow
from ai_trader.market_scanner.timeframe_sync import (
    bar_to_schema_dict,
    latest_lookahead_safe_bar,
    select_lookahead_safe_bars,
)
from ai_trader.market_scanner.types import RawBar

_M15 = 900


def _bar(ts_open: int) -> RawBar:
    return RawBar(symbol="X", timeframe="M15", ts_open=ts_open, ts_close=ts_open + _M15,
                  open=1.0, high=2.0, low=0.5, close=1.5, volume=1.0, complete=True)


def test_excludes_bars_closing_after_as_of_even_if_preloaded() -> None:
    """The critical lookahead-safety guarantee: a pre-loaded window that (e.g. via batch
    backfill) already contains bars closing AFTER as_of must never leak them into the selection."""
    w = TimeframeWindow("M15", max_len=20)
    for i in range(10):  # bars closing at M15, 2*M15, ..., 10*M15
        w.ingest_bar(_bar(i * _M15))
    as_of = 4 * _M15  # only the first 4 bars (closing at <=4*M15) should be visible
    safe = select_lookahead_safe_bars(w, as_of, lookback_bars=100)
    assert len(safe) == 4
    assert all(b.available_at <= as_of for b in safe)
    assert safe[-1].ts_close == as_of


def test_respects_lookback_limit() -> None:
    w = TimeframeWindow("M15", max_len=20)
    for i in range(10):
        w.ingest_bar(_bar(i * _M15))
    safe = select_lookahead_safe_bars(w, as_of=10 * _M15, lookback_bars=3)
    assert len(safe) == 3
    assert [b.ts_open for b in safe] == [7 * _M15, 8 * _M15, 9 * _M15]


def test_none_window_returns_empty() -> None:
    assert select_lookahead_safe_bars(None, as_of=1000, lookback_bars=10) == []


def test_latest_lookahead_safe_bar() -> None:
    w = TimeframeWindow("M15", max_len=20)
    for i in range(5):
        w.ingest_bar(_bar(i * _M15))
    latest = latest_lookahead_safe_bar(w, as_of=3 * _M15)
    assert latest is not None and latest.ts_close == 3 * _M15
    assert latest_lookahead_safe_bar(w, as_of=0) is None  # nothing closes at/before ts=0


def test_bar_to_schema_dict_shape() -> None:
    b = _bar(0)
    d = bar_to_schema_dict(b)
    assert d == {
        "ts_open": 0, "ts_close": 900, "open": 1.0, "high": 2.0, "low": 0.5,
        "close": 1.5, "volume": 1.0, "complete": True, "available_at": 900,
    }
