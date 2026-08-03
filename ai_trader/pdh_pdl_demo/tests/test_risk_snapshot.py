from __future__ import annotations

from ai_trader.live_signal_source.types import Bar, GapClassification, GapRecord
from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.pdh_pdl_demo.risk_snapshot import LiveRiskSnapshotBuilder

SYMBOL = "XAUUSD"
BAR_SECONDS = 900
NOW = 1_700_000_000


def _bar(i: int, h: float, l: float, c: float, volume: float = 100.0) -> Bar:
    ts = NOW + i * BAR_SECONDS
    return Bar(symbol=SYMBOL, ts_open=ts, ts_close=ts + BAR_SECONDS, open=c, high=h, low=l, close=c, volume=volume)


def test_atr_is_none_before_warmup_and_populated_after() -> None:
    builder = LiveRiskSnapshotBuilder()
    for i in range(13):
        builder.update(_bar(i, 101.0, 99.0, 100.0), gaps_this_poll=())
    assert builder.snapshot(current_spread=0.5).atr is None

    for i in range(13, 20):
        builder.update(_bar(i, 101.0, 99.0, 100.0), gaps_this_poll=())
    assert builder.snapshot(current_spread=0.5).atr is not None


def test_current_spread_passed_through_directly() -> None:
    builder = LiveRiskSnapshotBuilder()
    builder.update(_bar(0, 101.0, 99.0, 100.0), gaps_this_poll=())
    snap = builder.snapshot(current_spread=0.37)
    assert snap.current_spread == 0.37


def test_liquidity_proxy_reflects_volume_ratio() -> None:
    builder = LiveRiskSnapshotBuilder()
    for i in range(5):
        builder.update(_bar(i, 101.0, 99.0, 100.0, volume=100.0), gaps_this_poll=())
    builder.update(_bar(5, 101.0, 99.0, 100.0, volume=300.0), gaps_this_poll=())
    snap = builder.snapshot(current_spread=0.5)
    assert snap.liquidity_proxy is not None
    assert snap.liquidity_proxy > 1.0  # latest bar's volume is above the rolling average


def test_gap_this_poll_resets_bars_since_gap_and_records_classification() -> None:
    builder = LiveRiskSnapshotBuilder()
    builder.update(_bar(0, 101.0, 99.0, 100.0), gaps_this_poll=())
    assert builder.snapshot(current_spread=0.5).bars_since_gap is None  # no gap ever observed yet

    gap = GapRecord(symbol=SYMBOL, gap_start=NOW, gap_end=NOW + 10_000, duration_seconds=10_000,
                     classification=GapClassification.WEEKEND)
    builder.update(_bar(1, 101.0, 99.0, 100.0), gaps_this_poll=(gap,))
    snap = builder.snapshot(current_spread=0.5)
    assert snap.bars_since_gap == 0
    assert snap.is_weekend_gap is True

    builder.update(_bar(2, 101.0, 99.0, 100.0), gaps_this_poll=())
    snap2 = builder.snapshot(current_spread=0.5)
    assert snap2.bars_since_gap == 1
    assert snap2.is_weekend_gap is False  # only true on the bar the gap was actually observed


def test_disclosed_placeholders_match_phase10_precedent() -> None:
    builder = LiveRiskSnapshotBuilder()
    builder.update(_bar(0, 101.0, 99.0, 100.0), gaps_this_poll=())
    snap = builder.snapshot(current_spread=0.5)
    assert snap.is_past_friday_cutoff is False
    assert snap.is_near_session_close is False
    assert snap.minutes_to_high_impact_event == 999.0
    assert snap.data_quality is DataQualityLevel.OK
