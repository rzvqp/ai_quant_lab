"""Tests for confirmations.py's shared bar-pattern primitives."""

from __future__ import annotations

from ai_trader.strategy_runtime import confirmations


def bar(o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"open": o, "high": h, "low": l, "close": c}


def test_consecutive_same_direction_closes_bullish() -> None:
    bars = [bar(1, 2, 0.5, 1.5), bar(1.5, 2.5, 1.4, 2.0)]
    assert confirmations.consecutive_same_direction_closes(bars, 2, bullish=True) is True
    assert confirmations.consecutive_same_direction_closes(bars, 2, bullish=False) is False


def test_consecutive_same_direction_closes_needs_enough_bars() -> None:
    assert confirmations.consecutive_same_direction_closes([bar(1, 2, 0.5, 1.5)], 2, bullish=True) is False


def test_swept_level_low_sweep() -> None:
    level = 100.0
    swept = bar(101, 101.5, 99.0, 100.5)  # low < level, close > level
    not_swept_no_dip = bar(101, 101.5, 100.5, 100.8)  # never dipped below
    not_swept_no_reclaim = bar(101, 101.5, 99.0, 99.5)  # dipped but closed below
    assert confirmations.swept_level(swept, level, is_high_sweep=False) is True
    assert confirmations.swept_level(not_swept_no_dip, level, is_high_sweep=False) is False
    assert confirmations.swept_level(not_swept_no_reclaim, level, is_high_sweep=False) is False


def test_swept_level_high_sweep() -> None:
    level = 100.0
    swept = bar(99, 101.0, 98.5, 99.5)  # high > level, close < level
    assert confirmations.swept_level(swept, level, is_high_sweep=True) is True


def test_is_displacement_bar_requires_atr() -> None:
    b = bar(100, 105, 95, 102)  # range = 10
    assert confirmations.is_displacement_bar(b, atr=None) is False
    assert confirmations.is_displacement_bar(b, atr=5.0, min_atr_multiple=1.2) is True
    assert confirmations.is_displacement_bar(b, atr=100.0, min_atr_multiple=1.2) is False


def test_rolling_extreme_touch_none_extreme_never_matches() -> None:
    b = bar(100, 105, 95, 102)
    assert confirmations.rolling_extreme_touch(b, None, is_high=True) is False


def test_rolling_extreme_touch_high_and_low() -> None:
    b = bar(100, 105, 95, 102)
    assert confirmations.rolling_extreme_touch(b, 104.0, is_high=True) is True
    assert confirmations.rolling_extreme_touch(b, 106.0, is_high=True) is False
    assert confirmations.rolling_extreme_touch(b, 96.0, is_high=False) is True
