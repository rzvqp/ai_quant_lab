"""Unit tests for :mod:`ai_trader.market_intelligence.trend`."""

from __future__ import annotations

from ai_trader.market_intelligence.trend import analyze_trend, analyze_trend_m15
from ai_trader.market_intelligence.types import TrendDirection
from ai_trader.market_intelligence.tests._fixtures import make_context


def test_trend_m15_up_with_strength() -> None:
    ctx = make_context(m15_features={"m_trend_up": True, "m_ema20": 2010.0, "m_ema50": 2000.0}, m15_bars=[
        {"ts_open": 0, "ts_close": 1, "open": 2000, "high": 2010, "low": 1995, "close": 2010, "volume": 100},
    ])
    reading = analyze_trend_m15(ctx)
    assert reading.direction is TrendDirection.UP
    assert reading.strength == (2010.0 - 2000.0) / 2010.0


def test_trend_m15_down() -> None:
    ctx = make_context(m15_features={"m_trend_up": False, "m_ema20": 1990.0, "m_ema50": 2000.0}, m15_bars=[
        {"ts_open": 0, "ts_close": 1, "open": 2000, "high": 2005, "low": 1985, "close": 1990, "volume": 100},
    ])
    reading = analyze_trend_m15(ctx)
    assert reading.direction is TrendDirection.DOWN


def test_trend_m15_flat_when_spread_is_negligible() -> None:
    ctx = make_context(m15_features={"m_trend_up": True, "m_ema20": 2000.1, "m_ema50": 2000.0}, m15_bars=[
        {"ts_open": 0, "ts_close": 1, "open": 2000, "high": 2001, "low": 1999, "close": 2000.1, "volume": 100},
    ])
    reading = analyze_trend_m15(ctx)
    assert reading.direction is TrendDirection.FLAT


def test_trend_m15_unknown_when_flag_missing() -> None:
    ctx = make_context(m15_features={})
    reading = analyze_trend_m15(ctx)
    assert reading.direction is TrendDirection.UNKNOWN
    assert reading.strength is None


def test_trend_higher_timeframes_have_no_strength() -> None:
    ctx = make_context(m15_features={"m_trend_up": True, "h1_trend_up": True, "h4_trend_up": False, "d1_trend_up": True})
    readings = analyze_trend(ctx)
    assert set(readings) == {"M15", "H1", "H4", "D1"}
    assert readings["H1"].direction is TrendDirection.UP
    assert readings["H1"].strength is None
    assert readings["H4"].direction is TrendDirection.DOWN
    assert readings["D1"].direction is TrendDirection.UP


def test_analyze_trend_is_deterministic() -> None:
    ctx = make_context(m15_features={"m_trend_up": True, "m_ema20": 2010.0, "m_ema50": 2000.0, "h1_trend_up": False})
    assert analyze_trend(ctx) == analyze_trend(ctx)
