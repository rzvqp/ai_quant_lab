"""Tests for context_access.py's MarketContext readers."""

from __future__ import annotations

from ai_trader.strategy_runtime import context_access


def make_context(as_of: int = 1000, symbol: str = "XAUUSD", **feature_overrides: object) -> dict:  # type: ignore[type-arg]
    features = {"pdl": 100.0, "m_atr": 2.5, "session": "ny"}
    features.update(feature_overrides)
    return {
        "meta": {"as_of": as_of, "symbol": symbol},
        "data_quality": {"level": "OK"},
        "timeframes": {
            "M15": {
                "features": features,
                "bars": [
                    {"ts_open": 100, "ts_close": 1000, "open": 10.0, "high": 12.0, "low": 9.0, "close": 11.0},
                    {"ts_open": 1000, "ts_close": 1900, "open": 11.0, "high": 13.0, "low": 10.5, "close": 12.5},
                ],
            },
        },
    }


def test_as_of_and_symbol() -> None:
    ctx = make_context(as_of=123, symbol="EURUSD")
    assert context_access.as_of(ctx) == 123
    assert context_access.symbol(ctx) == "EURUSD"


def test_feature_reads_numeric() -> None:
    ctx = make_context()
    assert context_access.feature(ctx, "pdl") == 100.0
    assert context_access.feature(ctx, "missing") is None


def test_flag_reads_boolean_only() -> None:
    ctx = make_context(compress=True)
    assert context_access.flag(ctx, "compress") is True
    assert context_access.flag(ctx, "pdl") is None  # pdl is numeric, not boolean


def test_bars_ordered_oldest_first() -> None:
    ctx = make_context()
    bars = context_access.bars(ctx)
    assert bars[0]["close"] == 11.0
    assert bars[-1]["close"] == 12.5


def test_last_bar_and_bar_n_ago() -> None:
    ctx = make_context()
    assert context_access.last_bar(ctx)["close"] == 12.5
    assert context_access.bar_n_ago(ctx, 0)["close"] == 12.5
    assert context_access.bar_n_ago(ctx, 1)["close"] == 11.0
    assert context_access.bar_n_ago(ctx, 5) is None  # not enough history -- never fabricates


def test_missing_timeframe_returns_empty() -> None:
    ctx = make_context()
    assert context_access.bars(ctx, "H4") == []
    assert context_access.features(ctx, "H4") == {}


def test_data_quality_level_defaults_ok() -> None:
    ctx = {"meta": {}}
    assert context_access.data_quality_level(ctx) == "OK"
