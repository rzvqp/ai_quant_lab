"""Unit tests for ai_trader.market_scanner.timeframes."""

import pytest

from ai_trader.market_scanner.timeframes import snap_to_grid, timeframe_seconds


def test_timeframe_seconds_known() -> None:
    assert timeframe_seconds("M1") == 60
    assert timeframe_seconds("M15") == 900
    assert timeframe_seconds("H1") == 3600
    assert timeframe_seconds("H4") == 14400
    assert timeframe_seconds("D1") == 86400
    assert timeframe_seconds("W1") == 604800


def test_timeframe_seconds_unknown_raises() -> None:
    with pytest.raises(ValueError, match="unknown timeframe"):
        timeframe_seconds("M3")


def test_snap_to_grid_m15() -> None:
    # 1970-01-01T00:07:30Z is 450s -> should snap down to 0
    assert snap_to_grid(450, "M15") == 0
    assert snap_to_grid(900, "M15") == 900
    assert snap_to_grid(901, "M15") == 900
    assert snap_to_grid(1799, "M15") == 900


def test_snap_to_grid_d1_epoch_aligned() -> None:
    assert snap_to_grid(86400, "D1") == 86400
    assert snap_to_grid(86399, "D1") == 0


def test_snap_to_grid_w1_monday_anchored() -> None:
    # 1970-01-01 was a Thursday; the preceding Monday was 1969-12-29 = -259200
    monday = -4 * 24 * 60 * 60
    assert snap_to_grid(monday, "W1") == monday
    assert snap_to_grid(monday + 604800 - 1, "W1") == monday
    assert snap_to_grid(monday + 604800, "W1") == monday + 604800


def test_snap_to_grid_idempotent() -> None:
    for tf in ("M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1"):
        ts = snap_to_grid(1_700_123_456, tf)
        assert snap_to_grid(ts, tf) == ts
