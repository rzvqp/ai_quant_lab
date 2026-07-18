"""Unit tests for :mod:`ai_trader.market_intelligence.session_behavior`."""

from __future__ import annotations

from ai_trader.market_intelligence.session_behavior import analyze_session
from ai_trader.market_intelligence.tests._fixtures import make_context


def test_session_inside_opening_range_above_vwap() -> None:
    ctx = make_context(
        m15_features={"session": "LONDON", "bar_in_sess": 2, "or_high": 2010.0, "or_low": 1995.0, "vwap": 2000.0, "gap": 1.5},
        m15_bars=[{"ts_open": 0, "ts_close": 1, "open": 2000, "high": 2005, "low": 2000, "close": 2005.0, "volume": 100}],
    )
    reading = analyze_session(ctx)
    assert reading.session_name == "LONDON"
    assert reading.bar_in_session == 2
    assert reading.inside_opening_range is True
    assert reading.above_session_vwap is True
    assert reading.gap == 1.5


def test_session_outside_opening_range_below_vwap() -> None:
    ctx = make_context(
        m15_features={"session": "NY", "or_high": 2010.0, "or_low": 2005.0, "vwap": 2020.0},
        m15_bars=[{"ts_open": 0, "ts_close": 1, "open": 2000, "high": 2001, "low": 1990, "close": 1995.0, "volume": 100}],
    )
    reading = analyze_session(ctx)
    assert reading.inside_opening_range is False
    assert reading.above_session_vwap is False


def test_session_unknown_when_missing() -> None:
    reading = analyze_session(make_context(m15_features={}))
    assert reading.session_name is None
    assert reading.inside_opening_range is None
    assert reading.above_session_vwap is None


def test_session_is_deterministic() -> None:
    ctx = make_context(
        m15_features={"session": "ASIA", "or_high": 2010.0, "or_low": 1995.0, "vwap": 2000.0},
        m15_bars=[{"ts_open": 0, "ts_close": 1, "open": 2000, "high": 2005, "low": 2000, "close": 2005.0, "volume": 100}],
    )
    assert analyze_session(ctx) == analyze_session(ctx)
