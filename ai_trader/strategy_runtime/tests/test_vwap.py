"""Unit tests for the shared VWAP/value-area helpers (Phase 6.8 Wave B batch B3)."""

from __future__ import annotations

from ai_trader.strategy_runtime.vwap import anchored_vwap, distance_in_atr, value_area_edges, week_bucket


def bar(ts_open: int, h: float, l: float, c: float, vol: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts_open, "high": h, "low": l, "close": c, "volume": vol}


class TestValueAreaEdges:
    def test_edges_are_symmetric_around_vwap(self) -> None:
        hi, lo = value_area_edges(vwap=2000.0, std=5.0, k=2.0)
        assert hi == 2010.0
        assert lo == 1990.0


class TestWeekBucket:
    def test_same_week_maps_to_same_bucket(self) -> None:
        monday = 1_704_067_200  # 2024-01-01 00:00 UTC (a Monday)
        wednesday_same_week = monday + 2 * 86400
        assert week_bucket(monday) == week_bucket(wednesday_same_week)

    def test_next_week_maps_to_a_different_bucket(self) -> None:
        monday = 1_704_067_200
        next_monday = monday + 7 * 86400
        assert week_bucket(monday) != week_bucket(next_monday)


class TestAnchoredVwap:
    def test_only_bars_in_the_last_bars_own_bucket_are_used(self) -> None:
        w1 = 1_704_067_200
        w2 = w1 + 7 * 86400
        bars = [
            bar(w1, 100.0, 98.0, 99.0, 10.0),  # different week -- must be excluded
            bar(w2, 10.0, 8.0, 9.0, 1.0),
            bar(w2 + 900, 20.0, 18.0, 19.0, 1.0),
        ]
        result = anchored_vwap(bars, week_bucket)
        # typical prices for the w2 bars: (10+8+9)/3=9, (20+18+19)/3=19; equal volume -> mean=14
        assert result is not None
        assert abs(result - 14.0) < 1e-9

    def test_no_volume_in_bucket_returns_none(self) -> None:
        bars = [bar(1_704_067_200, 10.0, 8.0, 9.0, 0.0)]
        assert anchored_vwap(bars, week_bucket) is None

    def test_empty_bars_returns_none(self) -> None:
        assert anchored_vwap([], week_bucket) is None


class TestDistanceInAtr:
    def test_computes_absolute_distance_over_atr(self) -> None:
        assert distance_in_atr(price=110.0, anchor=100.0, atr=5.0) == 2.0

    def test_none_atr_returns_none(self) -> None:
        assert distance_in_atr(price=110.0, anchor=100.0, atr=None) is None

    def test_non_positive_atr_returns_none(self) -> None:
        assert distance_in_atr(price=110.0, anchor=100.0, atr=0.0) is None
