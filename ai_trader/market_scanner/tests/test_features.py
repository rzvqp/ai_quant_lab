"""Unit tests for ai_trader.market_scanner.features.FeatureProvider."""

from ai_trader.market_scanner.features import M15_FEATURE_NAMES, FeatureProvider, TrailingExtreme, WeeklyAggregator
from ai_trader.market_scanner.types import RawBar

_M15 = 900
_D1 = 86400


def _m15_bar(ts_open: int, o: float, h: float, l: float, c: float) -> RawBar:
    return RawBar(symbol="X", timeframe="M15", ts_open=ts_open, ts_close=ts_open + _M15,
                  open=o, high=h, low=l, close=c, volume=10.0, complete=True)


def _d1_bar(ts_open: int, o: float, h: float, l: float, c: float) -> RawBar:
    return RawBar(symbol="X", timeframe="D1", ts_open=ts_open, ts_close=ts_open + _D1,
                  open=o, high=h, low=l, close=c, volume=100.0, complete=True)


class TestTrailingExtreme:
    def test_excludes_current_value(self) -> None:
        te = TrailingExtreme(window=2, is_max=True)
        assert te.update(10) is None  # window not full yet
        assert te.update(20) is None
        assert te.update(5) == 20  # max of the prior 2 values (10, 20), not including 5
        assert te.update(1) == 20  # max of the prior 2 values (20, 5), not including 1


class TestWeeklyAggregator:
    def test_prev_week_populates_only_after_a_week_boundary(self) -> None:
        agg = WeeklyAggregator()
        # 1970-01-01 (Thu) .. 1970-01-04 (Sun) is week 1; 1970-01-05 (Mon) starts week 2
        for i in range(4):
            agg.update(_d1_bar(i * _D1, 100, 100 + i, 100 - i, 100))
        assert agg.prev_week_high is None
        agg.update(_d1_bar(4 * _D1, 48, 50, 40, 45))  # first Monday bar -> new week
        assert agg.prev_week_high == 103  # max high from days 0..3
        assert agg.prev_week_low == 97


class TestFeatureProviderNamespace:
    def test_returns_complete_namespace_even_when_cold(self) -> None:
        fp = FeatureProvider(context_timeframes=frozenset({"H1", "H4", "D1"}), event_flag_window_seconds=1800)
        result = fp.on_base_close(_m15_bar(0, 100, 101, 99, 100.5), latest_d1_bar=None)
        assert set(result.features) == M15_FEATURE_NAMES
        # everything statistical is None on bar 1; structural bookkeeping is already populated
        assert result.features["m_atr"] is None
        assert result.features["session"] is not None
        assert result.features["blk"] == 0
        assert result.features["bar_in_sess"] == 0

    def test_pdh_pdl_wired_from_latest_d1_bar(self) -> None:
        fp = FeatureProvider(context_timeframes=frozenset({"D1"}), event_flag_window_seconds=1800)
        d1 = _d1_bar(0, o=100, h=110, l=90, c=105)
        result = fp.on_base_close(_m15_bar(_D1, 105, 106, 104, 105.5), latest_d1_bar=d1)
        assert result.features["pdh"] == 110
        assert result.features["pdl"] == 90
        assert result.features["pd_open"] == 100
        assert result.features["pd_close"] == 105
        assert result.features["pd_mid"] == 100.0

    def test_fvg_bull_detected_two_bars_back(self) -> None:
        fp = FeatureProvider(context_timeframes=frozenset(), event_flag_window_seconds=1800)
        fp.on_base_close(_m15_bar(0, 100, 101, 99, 100.5), None)          # bar0: high=101
        fp.on_base_close(_m15_bar(_M15, 100, 102, 99.5, 101), None)      # bar1
        r2 = fp.on_base_close(_m15_bar(2 * _M15, 103, 104, 102, 103.5), None)  # bar2: low=102 > bar0.high=101
        assert r2.features["fvg_bull"] is True
        assert r2.features["fvg_bear"] is False

    def test_roc3_and_disp_and_bull_bear_close(self) -> None:
        fp = FeatureProvider(context_timeframes=frozenset(), event_flag_window_seconds=1800)
        fp.on_base_close(_m15_bar(0, 100, 101, 99, 100), None)
        fp.on_base_close(_m15_bar(_M15, 100, 106, 99, 105), None)
        fp.on_base_close(_m15_bar(2 * _M15, 105, 109, 104, 108), None)
        r3 = fp.on_base_close(_m15_bar(3 * _M15, 108, 111, 107, 110), None)
        assert abs(r3.features["roc3"] - (110 / 100 - 1)) < 1e-9
        assert r3.features["bull_close"] is True
        assert r3.features["bear_close"] is False

    def test_gap_only_on_first_bar_of_new_session(self) -> None:
        fp = FeatureProvider(context_timeframes=frozenset(), event_flag_window_seconds=1800)
        # fill the whole asia block (32 M15 bars, hours 0-7) with close=100
        for i in range(32):
            fp.on_base_close(_m15_bar(i * _M15, 100, 101, 99, 100), None)
        # first london bar: open jumps to 110 -> gap = 110 - prev_sess_close(100)
        r = fp.on_base_close(_m15_bar(32 * _M15, 110, 111, 109, 110), None)
        assert r.features["gap"] == 10.0
        r2 = fp.on_base_close(_m15_bar(33 * _M15, 110, 111, 109, 110), None)
        assert r2.features["gap"] is None  # not the first bar of the block anymore

    def test_context_close_updates_htf_snapshot(self) -> None:
        fp = FeatureProvider(context_timeframes=frozenset({"H1"}), event_flag_window_seconds=1800)
        assert fp.htf_feature_snapshot("H1") == {"trend_up": None, "volrank": None, "rsi": None}
        h1_bar = RawBar(symbol="X", timeframe="H1", ts_open=0, ts_close=3600,
                         open=100, high=101, low=99, close=100.5, volume=10, complete=True)
        fp.on_context_close("H1", h1_bar)
        snap = fp.htf_feature_snapshot("H1")
        # a single H1 bar is not enough to warm up trend_up/volrank/rsi, but the call must not raise
        assert set(snap) == {"trend_up", "volrank", "rsi"}
