"""Tests for the Phase 6.8 Wave B historical-features window (``MarketScanner``'s own
``_base_feature_history`` + ``TimeframeContext.feature_history``): generic, deterministic,
per-bar feature retention any current or future strategy can reuse."""

from __future__ import annotations

from ai_trader.market_scanner import AdapterConfig, Mode, RawBar, SymbolMeta
from ai_trader.market_scanner.config import ScannerConfig
from ai_trader.market_scanner.scanner import MarketScanner

_M15 = 900


def _symbol(name: str = "XAUUSD") -> SymbolMeta:
    return SymbolMeta(symbol=name, tick_size=0.1, point_value=1.0, price_precision=2)


def _m15_bar(ts_open: int, close: float = 100.0) -> RawBar:
    return RawBar(symbol="XAUUSD", timeframe="M15", ts_open=ts_open, ts_close=ts_open + _M15,
                  open=close, high=close + 1, low=close - 1, close=close, volume=10.0, complete=True)


def _scanner(history_buffer_bars: int = 64) -> MarketScanner:
    scanner = MarketScanner(ScannerConfig(history_buffer_bars=history_buffer_bars))
    scanner.configure([_symbol()], AdapterConfig(mode=Mode.REPLAY, source_id="test"))
    return scanner


class TestFeatureHistoryPresenceAndAlignment:
    def test_feature_history_is_index_aligned_with_bars(self) -> None:
        scanner = _scanner()
        for i in range(5):
            scanner.ingest_bar(_m15_bar(i * _M15, close=100.0 + i))
        scanner.advance_clock(4 * _M15 + _M15)
        ctx = scanner.build_context("XAUUSD", 4 * _M15 + _M15)

        m15 = ctx["timeframes"]["M15"]
        assert "feature_history" in m15
        assert len(m15["feature_history"]) == len(m15["bars"])
        # the LAST entry of feature_history must equal the current `features` snapshot exactly --
        # both are computed from the same bar's own close.
        assert m15["feature_history"][-1] == m15["features"]

    def test_feature_history_reflects_real_per_bar_atr_progression(self) -> None:
        """A genuine, non-fabricated proof: ATR (Wilder-smoothed) differs bar to bar as more bars
        warm it up -- if feature_history merely repeated the current snapshot, every entry would
        be identical; real retention means they are NOT all the same once enough bars exist."""
        scanner = _scanner()
        # enough bars to get well past ATR's own Wilder warmup period (needs >= RSI_WINDOW deltas
        # before it first produces a non-null value).
        import random
        rng = random.Random(7)  # noqa: S311 -- deterministic test fixture, not security-sensitive
        closes = [100.0]
        for _ in range(29):
            closes.append(closes[-1] + rng.uniform(-3.0, 3.0))
        for i, c in enumerate(closes):
            scanner.ingest_bar(_m15_bar(i * _M15, close=c))
        last_ts = (len(closes) - 1) * _M15 + _M15
        scanner.advance_clock(last_ts)
        ctx = scanner.build_context("XAUUSD", last_ts)

        atr_series = [snap.get("m_atr") if snap is not None else None for snap in ctx["timeframes"]["M15"]["feature_history"]]
        non_null = [v for v in atr_series if v is not None]
        assert len(non_null) >= 2
        assert len(set(non_null)) > 1, "expected real ATR progression, not a repeated current snapshot"

    def test_no_bars_yet_gives_empty_history(self) -> None:
        scanner = _scanner()
        scanner.advance_clock(0)
        ctx = scanner.build_context("XAUUSD", 0)
        assert ctx["timeframes"]["M15"]["feature_history"] == []

    def test_history_bounded_like_the_bars_window(self) -> None:
        scanner = _scanner(history_buffer_bars=3)
        for i in range(10):
            scanner.ingest_bar(_m15_bar(i * _M15, close=100.0 + i))
        last_ts = 9 * _M15 + _M15
        scanner.advance_clock(last_ts)
        ctx = scanner.build_context("XAUUSD", last_ts)
        m15 = ctx["timeframes"]["M15"]
        assert len(m15["feature_history"]) == len(m15["bars"])
        assert len(m15["bars"]) <= 3


class TestContextAccessIntegration:
    def test_context_access_feature_n_ago_reads_the_real_scanner_output(self) -> None:
        from ai_trader.strategy_runtime import context_access

        scanner = _scanner()
        # enough bars to get past ATR's own Wilder warmup so m_atr is non-null both now and 1 bar ago.
        for i in range(30):
            scanner.ingest_bar(_m15_bar(i * _M15, close=100.0 + (i % 5)))
        last_ts = 29 * _M15 + _M15
        scanner.advance_clock(last_ts)
        ctx = scanner.build_context("XAUUSD", last_ts)

        now = context_access.feature_n_ago(ctx, "m_atr", 0)
        before = context_access.feature_n_ago(ctx, "m_atr", 1)
        assert now == context_access.feature(ctx, "m_atr")
        assert before is not None
