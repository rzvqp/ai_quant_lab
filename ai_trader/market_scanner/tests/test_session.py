"""Unit tests for ai_trader.market_scanner.session."""

from ai_trader.market_scanner.config import OPENING_RANGE_BARS
from ai_trader.market_scanner.session import SessionEngine, session_name_for_hour
from ai_trader.market_scanner.types import SessionName

_M15 = 900
_DAY0 = 0  # 1970-01-01T00:00:00Z, a Thursday


def test_session_name_boundaries() -> None:
    assert session_name_for_hour(0) == SessionName.ASIA
    assert session_name_for_hour(7) == SessionName.ASIA
    assert session_name_for_hour(8) == SessionName.LONDON
    assert session_name_for_hour(12) == SessionName.LONDON
    assert session_name_for_hour(13) == SessionName.NY
    assert session_name_for_hour(20) == SessionName.NY
    assert session_name_for_hour(21) == SessionName.LATE
    assert session_name_for_hour(23) == SessionName.LATE


def test_block_id_increments_on_session_change() -> None:
    engine = SessionEngine()
    # hour 0 (asia) for the first 32 bars (0..7:45), then hour 8 (london)
    block_ids = []
    for i in range(40):
        ts_open = _DAY0 + i * _M15
        snap = engine.update(ts_open, high=101, low=99, close=100, volume=10)
        block_ids.append(snap.block_id)
    assert block_ids[0] == 0
    assert block_ids.count(0) == 32  # hours 0..7 inclusive = 32 M15 bars
    assert block_ids[32] == 1  # first london bar


def test_bar_in_session_resets_on_new_block() -> None:
    engine = SessionEngine()
    seq = [engine.update(_DAY0 + i * _M15, 101, 99, 100, 10).bar_in_session for i in range(34)]
    assert seq[:4] == [0, 1, 2, 3]
    assert seq[31] == 31  # last asia bar
    assert seq[32] == 0  # first london bar


def test_opening_range_forms_after_four_bars_and_freezes() -> None:
    engine = SessionEngine()
    highs = [101, 105, 103, 108, 110, 120]
    lows = [99, 100, 98, 97, 50, 5]
    last = None
    for i, (h, l) in enumerate(zip(highs, lows, strict=True)):
        last = engine.update(_DAY0 + i * _M15, h, l, (h + l) / 2, 10)
        if i < OPENING_RANGE_BARS - 1:
            assert last.opening_range.formed is False
    assert last.opening_range.formed is True
    assert last.opening_range.high == max(highs[:OPENING_RANGE_BARS])
    assert last.opening_range.low == min(lows[:OPENING_RANGE_BARS])
    # OR must not move after bars 5 and 6, even though bar 5's low (5) is far below bar0-3's lows
    assert last.opening_range.low == min(lows[:OPENING_RANGE_BARS])


def test_session_high_low_excludes_current_bar() -> None:
    engine = SessionEngine()
    s0 = engine.update(_DAY0, high=105, low=95, close=100, volume=10)
    assert s0.session_high is None and s0.session_low is None  # no prior bar in this block yet
    s1 = engine.update(_DAY0 + _M15, high=110, low=90, close=100, volume=10)
    assert s1.session_high == 105  # reflects bar0 only, not bar1's own 110
    assert s1.session_low == 95


def test_prev_session_values_available_at_new_block_start() -> None:
    engine = SessionEngine()
    # fill the whole asia block (32 bars), tracking its high/low/last-close
    highs = [100 + i for i in range(32)]
    lows = [90 + i for i in range(32)]
    closes = [95 + i for i in range(32)]
    for i in range(32):
        engine.update(_DAY0 + i * _M15, highs[i], lows[i], closes[i], 10)
    # first bar of the london block: prev_session_* must reflect the just-completed asia block
    snap = engine.update(_DAY0 + 32 * _M15, high=200, low=190, close=195, volume=10)
    assert snap.prev_session_high == max(highs)
    assert snap.prev_session_low == min(lows)
    assert snap.prev_session_close == closes[-1]


def test_vwap_resets_each_block() -> None:
    engine = SessionEngine()
    s0 = engine.update(_DAY0, high=101, low=99, close=100, volume=10)
    assert s0.vwap == 100.0  # single bar: vwap == its own typical price
    s1 = engine.update(_DAY0 + _M15, high=103, low=101, close=102, volume=10)
    typical0 = (101 + 99 + 100) / 3
    typical1 = (103 + 101 + 102) / 3
    expected = (typical0 * 10 + typical1 * 10) / 20
    assert abs(s1.vwap - expected) < 1e-9


def test_vwap_none_without_volume() -> None:
    engine = SessionEngine()
    snap = engine.update(_DAY0, high=101, low=99, close=100, volume=None)
    assert snap.vwap is None
