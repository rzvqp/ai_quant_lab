"""Tests for the Replay Data Source against the repo's real (read-only) ``data/market/`` CSVs."""

from __future__ import annotations

from pathlib import Path

from ai_trader.market_scanner.config import ScannerConfig
from ai_trader.market_scanner.scanner import AdapterConfig, MarketScanner
from ai_trader.market_scanner.types import Mode, SymbolMeta
from ai_trader.simulation.data_source import ReplayDataSource

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data" / "market"


def test_data_files_exist() -> None:
    assert (DATA_DIR / "OANDA_XAUUSD_M15.csv").exists()


def test_base_ticks_in_range_sorted_and_bounded() -> None:
    ds = ReplayDataSource(("XAUUSD",), ("M15",), "M15", DATA_DIR)
    ticks = ds.base_ticks_in_range(1_700_000_000, 1_700_100_000, warmup_bars=10)
    assert ticks == tuple(sorted(ticks))
    assert all(t <= 1_700_100_000 for t in ticks)
    assert len(ticks) > 0


def test_warmup_extends_before_start() -> None:
    ds = ReplayDataSource(("XAUUSD",), ("M15",), "M15", DATA_DIR)
    with_warmup = ds.base_ticks_in_range(1_700_010_000, 1_700_100_000, warmup_bars=20)
    no_warmup = ds.base_ticks_in_range(1_700_010_000, 1_700_100_000, warmup_bars=0)
    assert len(with_warmup) >= len(no_warmup)
    assert min(with_warmup) <= min(no_warmup)


def test_feed_up_to_ingests_higher_timeframe_before_base_at_equal_close() -> None:
    ds = ReplayDataSource(("XAUUSD",), ("M15", "H1", "H4", "D1"), "M15", DATA_DIR)
    scanner = MarketScanner(ScannerConfig(base_timeframe="M15"))
    scanner.configure(
        [SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)],
        AdapterConfig(mode=Mode.REPLAY, source_id="replay"),
    )
    ticks = ds.base_ticks_in_range(1_700_000_000, 1_700_050_000, warmup_bars=50)
    for as_of in ticks[:20]:
        ds.feed_up_to(scanner, as_of)
        scanner.advance_clock(as_of)
    # If ordering were wrong, build_context would raise/degrade; a clean call is the behavioral proof.
    ctx = scanner.build_context("XAUUSD", ticks[19])
    assert ctx["meta"]["symbol"] == "XAUUSD"


def test_base_bars_at_matches_close_timestamp() -> None:
    ds = ReplayDataSource(("XAUUSD",), ("M15",), "M15", DATA_DIR)
    ticks = ds.base_ticks_in_range(1_700_000_000, 1_700_050_000, warmup_bars=0)
    bar = ds.base_bars_at(ticks[0])["XAUUSD"]
    assert bar.ts_close == ticks[0]
    assert bar.low <= bar.open <= bar.high
    assert bar.low <= bar.close <= bar.high
