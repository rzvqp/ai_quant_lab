"""Unit tests for ai_trader.market_scanner.indicators.StreamingIndicatorEngine."""

import math

from ai_trader.market_scanner.config import ATR_WINDOW, EMA_SLOW_SPAN, SMA_WINDOW, VOLRANK_WINDOW
from ai_trader.market_scanner.indicators import StreamingIndicatorEngine


def _feed_constant(engine: StreamingIndicatorEngine, price: float, n: int) -> None:
    for _ in range(n):
        engine.update(high=price + 0.5, low=price - 0.5, close=price)


class TestWarmupGating:
    def test_atr_none_before_window(self) -> None:
        engine = StreamingIndicatorEngine()
        snap = None
        for _ in range(ATR_WINDOW):
            snap = engine.update(high=101, low=99, close=100)
            assert snap.atr is None
        # the (ATR_WINDOW+1)-th bar is the first with a full non-null TR window
        snap = engine.update(high=101, low=99, close=100)
        assert snap.atr is not None

    def test_sma_std_none_before_window(self) -> None:
        engine = StreamingIndicatorEngine()
        for i in range(SMA_WINDOW - 1):
            snap = engine.update(high=101, low=99, close=100 + i)
        assert snap.sma is None and snap.std is None
        snap = engine.update(high=101, low=99, close=100)
        assert snap.sma is not None and snap.std is not None

    def test_ema_gated_by_span(self) -> None:
        engine = StreamingIndicatorEngine()
        snap = None
        for i in range(EMA_SLOW_SPAN - 1):
            snap = engine.update(high=101, low=99, close=100)
        assert snap.ema_slow is None
        snap = engine.update(high=101, low=99, close=100)
        assert snap.ema_slow is not None

    def test_volrank_none_before_full_history(self) -> None:
        engine = StreamingIndicatorEngine()
        snap = None
        # volrank needs ATR_WINDOW bars for the first Parkinson value, then VOLRANK_WINDOW pv values
        for _ in range(ATR_WINDOW + VOLRANK_WINDOW - 2):
            snap = engine.update(high=101, low=99, close=100)
        assert snap.volrank is None
        snap = engine.update(high=101, low=99, close=100)
        assert snap.volrank is not None


class TestDeterminism:
    def test_identical_input_identical_output(self) -> None:
        prices = [100 + math.sin(i / 5) * 3 for i in range(150)]
        e1, e2 = StreamingIndicatorEngine(), StreamingIndicatorEngine()
        snaps1 = [e1.update(high=p + 1, low=p - 1, close=p) for p in prices]
        snaps2 = [e2.update(high=p + 1, low=p - 1, close=p) for p in prices]
        assert snaps1 == snaps2


class TestBehaviour:
    def test_trend_up_true_in_rising_market(self) -> None:
        engine = StreamingIndicatorEngine()
        snap = None
        for i in range(EMA_SLOW_SPAN + 20):
            price = 100 + i * 2.0
            snap = engine.update(high=price + 0.5, low=price - 0.5, close=price)
        assert snap.trend_up is True
        assert snap.ema_fast > snap.ema_slow

    def test_rsi_high_in_strongly_rising_market(self) -> None:
        engine = StreamingIndicatorEngine()
        snap = None
        for i in range(60):
            price = 100 + i * 1.0
            snap = engine.update(high=price + 0.1, low=price - 0.1, close=price)
        assert snap.rsi is not None
        assert snap.rsi > 90

    def test_atr_zero_for_flat_series(self) -> None:
        engine = StreamingIndicatorEngine()
        snap = None
        for _ in range(ATR_WINDOW + 2):
            snap = engine.update(high=100.0, low=100.0, close=100.0)
        assert snap.atr == 0.0

    def test_compress_flag_matches_atr_vs_atr_ma(self) -> None:
        engine = StreamingIndicatorEngine()
        snap = None
        for i in range(80):
            price = 100 + (i % 3) * 0.01  # tiny, flattening range
            snap = engine.update(high=price + 0.02, low=price - 0.02, close=price)
        if snap.atr is not None and snap.atr_ma is not None:
            assert snap.compress == (snap.atr < 0.8 * snap.atr_ma)
