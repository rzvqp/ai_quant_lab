"""Verifies `causal_h1.CausalH1EmaTracker` against 4 independently-established real anchor points
(RT-Q4-P007-004-RETRO-DETECTION-INTEGRITY-001 / E107's own dual calibration) -- not merely a
self-consistency check, an exact reproduction of numbers this mandate's own code never computed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.csv_causal_replay.causal_h1 import CausalH1EmaTracker, replay_causal_h1_ema
from ai_trader.csv_causal_replay.identity import M15_BAR_INTERVAL_SECONDS, Q4_START_TS, XAUUSD_M15_SYMBOL
from ai_trader.csv_causal_replay.sealed_reader import SealedReader, SealedReaderConfig
from ai_trader.csv_causal_replay.types import Bar

REAL_FIXTURE = Path(__file__).parent.parent / "fixtures" / "data" / "Q4_SEALED_1_1304.csv"

# bar_index -> independently-established causal H1 EMA50, from a document this code never read.
ANCHOR_POINTS = {378: 1901.160, 487: 1891.748, 787: 1918.200, 878: 1904.592}


@pytest.mark.skipif(not REAL_FIXTURE.exists(), reason="real Q4_SEALED_1_1304.csv fixture not present")
def test_causal_h1_ema_reproduces_all_four_known_anchor_points_exactly():
    config = SealedReaderConfig(
        symbol=XAUUSD_M15_SYMBOL, bar_interval_seconds=M15_BAR_INTERVAL_SECONDS,
        q4_start_ts=Q4_START_TS, max_q4_bar_index=1304,
    )
    tracker = CausalH1EmaTracker()
    results: dict[int, float] = {}
    with SealedReader(REAL_FIXTURE, config=config) as reader:
        for row in reader.iter_rows():
            tracker.feed(row.bar)  # includes the pre-Q4 warm-up section, required for the seed to converge
            if row.q4_bar_index is not None and row.q4_bar_index in ANCHOR_POINTS:
                results[row.q4_bar_index] = tracker.current_ema

    for bar_index, expected in ANCHOR_POINTS.items():
        actual = results[bar_index]
        assert actual == pytest.approx(expected, abs=0.001), f"bar {bar_index}: expected {expected}, got {actual}"


def test_current_ema_is_none_before_period_h1_candles_close():
    tracker = CausalH1EmaTracker(period=3)
    for hour in range(2):  # 2 closed H1 candles, one short of period=3
        for minute in (0, 15, 30, 45):
            ts = 1_600_000_000 + hour * 3600 + minute * 60
            tracker.feed(Bar(symbol="TEST", ts_open=ts, ts_close=ts + 900, open=1, high=1, low=1, close=100.0 + hour, volume=1))
    assert tracker.current_ema is None


def test_ema_never_includes_the_current_still_open_hour():
    """Feeding only PART of an hour (e.g. just the :00 sub-bar) must not close that hour's bucket --
    `current_ema` must stay exactly what it was before those partial bars were fed."""
    tracker = CausalH1EmaTracker(period=2)
    base = 1_600_000_000
    for hour in range(2):
        for minute in (0, 15, 30, 45):
            ts = base + hour * 3600 + minute * 60
            tracker.feed(Bar(symbol="TEST", ts_open=ts, ts_close=ts + 900, open=1, high=1, low=1, close=100.0 + hour, volume=1))
    ema_after_two_closed_hours = tracker.current_ema
    assert ema_after_two_closed_hours is not None
    # Feed only the :00 sub-bar of a third hour -- must not change current_ema (that hour is not closed).
    ts = base + 2 * 3600
    tracker.feed(Bar(symbol="TEST", ts_open=ts, ts_close=ts + 900, open=1, high=1, low=1, close=999.0, volume=1))
    assert tracker.current_ema == ema_after_two_closed_hours


def test_replay_causal_h1_ema_convenience_matches_manual_feed_loop():
    base = 1_600_000_000
    bars = [
        Bar(symbol="TEST", ts_open=base + i * 900, ts_close=base + i * 900 + 900, open=1, high=1, low=1, close=100.0 + i, volume=1)
        for i in range(20)
    ]
    manual = CausalH1EmaTracker(period=2)
    for b in bars:
        manual.feed(b)
    via_helper = replay_causal_h1_ema(bars, period=2)
    assert via_helper.current_ema == manual.current_ema
