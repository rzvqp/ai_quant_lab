"""Unit tests for ai_trader.market_scanner.data_quality."""

from ai_trader.market_scanner import data_quality
from ai_trader.market_scanner.bar_store import TimeframeWindow
from ai_trader.market_scanner.config import ScannerConfig
from ai_trader.market_scanner.types import Requirements
from ai_trader.market_scanner.types import RawBar

_M15 = 900


def _bar(ts_open: int) -> RawBar:
    return RawBar(symbol="X", timeframe="M15", ts_open=ts_open, ts_close=ts_open + _M15,
                  open=1.0, high=2.0, low=0.5, close=1.5, volume=1.0, complete=True)


def test_missing_timeframe_reports_insufficient() -> None:
    config = ScannerConfig()
    req = Requirements(timeframes=frozenset({"M15", "H1"}), fields_by_timeframe={}, lookback_by_timeframe={}, symbols=frozenset())
    dq, suff = data_quality.assess(as_of=10_000, config=config, windows={"M15": None, "H1": None},
                                    features_by_timeframe={}, requirements=req)
    assert dq["overall"] == "INSUFFICIENT"
    assert suff["overall"] == "INSUFFICIENT"
    assert "H1" in suff["missing_timeframes"]


def test_missing_required_field_marks_partial_when_data_otherwise_ok() -> None:
    config = ScannerConfig(history_buffer_bars=1)
    w = TimeframeWindow("M15", max_len=10)
    w.ingest_bar(_bar(0))
    req = Requirements(timeframes=frozenset({"M15"}), fields_by_timeframe={"M15": frozenset({"m_atr"})},
                        lookback_by_timeframe={"M15": 1}, symbols=frozenset())
    dq, suff = data_quality.assess(as_of=_M15, config=config, windows={"M15": w},
                                    features_by_timeframe={"M15": {"m_atr": None}}, requirements=req)
    assert dq["by_timeframe"]["M15"]["warmup_satisfied"] is False
    assert suff["overall"] in ("PARTIAL", "INSUFFICIENT")
    assert "M15.m_atr" in suff["missing_fields"]


def test_fully_satisfied_is_ok_and_sufficient() -> None:
    config = ScannerConfig(history_buffer_bars=1)
    w = TimeframeWindow("M15", max_len=10)
    w.ingest_bar(_bar(0))
    req = Requirements(timeframes=frozenset({"M15"}), fields_by_timeframe={"M15": frozenset({"m_atr"})},
                        lookback_by_timeframe={"M15": 1}, symbols=frozenset())
    dq, suff = data_quality.assess(as_of=_M15, config=config, windows={"M15": w},
                                    features_by_timeframe={"M15": {"m_atr": 1.23}}, requirements=req)
    assert dq["overall"] == "OK"
    assert suff["overall"] == "SUFFICIENT"
    assert suff["missing_fields"] is None
    assert suff["missing_timeframes"] is None


def test_stale_when_beyond_threshold() -> None:
    config = ScannerConfig(staleness_threshold_ms=1000, history_buffer_bars=1)
    w = TimeframeWindow("M15", max_len=10)
    w.ingest_bar(_bar(0))
    req = Requirements(timeframes=frozenset({"M15"}), fields_by_timeframe={}, lookback_by_timeframe={"M15": 1}, symbols=frozenset())
    as_of = _M15 + 10  # 10s = 10000ms staleness, way beyond the 1000ms threshold
    dq, _ = data_quality.assess(as_of=as_of, config=config, windows={"M15": w},
                                 features_by_timeframe={"M15": {}}, requirements=req)
    assert dq["by_timeframe"]["M15"]["staleness_ms"] == 10_000
    assert dq["overall"] == "STALE"


def test_unexplained_gap_marks_degraded_but_weekend_gap_does_not() -> None:
    config = ScannerConfig(max_gap_bars_before_degraded=1, history_buffer_bars=1)
    w = TimeframeWindow("M15", max_len=10)
    w.ingest_bar(_bar(0))
    w.ingest_bar(_bar(5 * _M15))  # unexplained gap of 4 bars (not a weekend/holiday span)
    req = Requirements(timeframes=frozenset({"M15"}), fields_by_timeframe={}, lookback_by_timeframe={"M15": 1}, symbols=frozenset())
    dq, _ = data_quality.assess(as_of=6 * _M15, config=config, windows={"M15": w},
                                 features_by_timeframe={"M15": {}}, requirements=req)
    assert dq["overall"] == "DEGRADED"
    assert dq["by_timeframe"]["M15"]["gaps"][0]["cause"] is None
