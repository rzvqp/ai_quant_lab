"""Unit tests for the shared candlestick/bar-pattern helpers (Phase 6.8 Wave B batch B5)."""

from __future__ import annotations

from ai_trader.strategy_runtime.patterns import (
    close_to_close_direction,
    exact_close_to_close_streak,
    is_outside_bar,
    is_range_expansion,
)


def bar(o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"open": o, "high": h, "low": l, "close": c}


class TestIsOutsideBar:
    def test_engulfing_range_is_outside(self) -> None:
        prev = bar(100.0, 101.0, 99.0, 100.0)
        cur = bar(100.0, 102.0, 98.0, 101.0)
        assert is_outside_bar(cur, prev) is True

    def test_inside_range_is_not_outside(self) -> None:
        prev = bar(100.0, 101.0, 99.0, 100.0)
        cur = bar(100.0, 100.5, 99.5, 100.2)
        assert is_outside_bar(cur, prev) is False


class TestIsRangeExpansion:
    def test_range_over_atr_is_expansion(self) -> None:
        assert is_range_expansion(bar(100.0, 105.0, 95.0, 102.0), atr=5.0) is True

    def test_range_under_atr_is_not_expansion(self) -> None:
        assert is_range_expansion(bar(100.0, 101.0, 99.0, 100.5), atr=5.0) is False

    def test_none_atr_is_not_expansion(self) -> None:
        assert is_range_expansion(bar(100.0, 105.0, 95.0, 102.0), atr=None) is False


class TestCloseToCloseDirection:
    def test_higher_close_is_up(self) -> None:
        assert close_to_close_direction(bar(0, 0, 0, 101.0), bar(0, 0, 0, 100.0)) == 1

    def test_lower_close_is_down(self) -> None:
        assert close_to_close_direction(bar(0, 0, 0, 99.0), bar(0, 0, 0, 100.0)) == -1

    def test_unchanged_close_is_zero(self) -> None:
        assert close_to_close_direction(bar(0, 0, 0, 100.0), bar(0, 0, 0, 100.0)) == 0


def _closes(values: list[float]) -> list[dict]:  # type: ignore[type-arg]
    return [bar(0, 0, 0, v) for v in values]


class TestExactCloseToCloseStreak:
    def test_exactly_k_up_closes_is_up_streak(self) -> None:
        # bars: 100(base),101,102,103 -> 3 consecutive up closes, no predecessor to check.
        bars = _closes([100.0, 101.0, 102.0, 103.0])
        assert exact_close_to_close_streak(bars, k=3) == 1

    def test_streak_longer_than_k_is_not_an_exact_k_onset(self) -> None:
        # 4 consecutive up closes -- checking k=3 must reject since the streak is actually 4 long.
        bars = _closes([99.0, 100.0, 101.0, 102.0, 103.0])
        assert exact_close_to_close_streak(bars, k=3) is None

    def test_streak_broken_by_a_prior_opposite_bar_is_a_valid_exact_k_onset(self) -> None:
        bars = _closes([105.0, 99.0, 100.0, 101.0, 102.0])  # down, then exactly 3 up closes
        assert exact_close_to_close_streak(bars, k=3) == 1

    def test_mixed_direction_window_is_no_streak(self) -> None:
        bars = _closes([100.0, 101.0, 100.5, 102.0])
        assert exact_close_to_close_streak(bars, k=3) is None

    def test_insufficient_history_is_none(self) -> None:
        bars = _closes([100.0, 101.0])
        assert exact_close_to_close_streak(bars, k=3) is None
