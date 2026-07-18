"""Unit tests for :mod:`ai_trader.market_intelligence.liquidity`."""

from __future__ import annotations

from ai_trader.market_intelligence.liquidity import analyze_liquidity
from ai_trader.market_intelligence.types import LiquidityState
from ai_trader.market_intelligence.tests._fixtures import make_flat_bars, AS_OF, BAR_SECONDS


def _bars_with_last_volume(last_volume: float, n: int = 20, base_volume: float = 1000.0) -> list[dict[str, object]]:
    bars = make_flat_bars(n, AS_OF - n * BAR_SECONDS, volume=base_volume)
    bars[-1] = {**bars[-1], "volume": last_volume}
    return bars


def _context(bars: list[dict[str, object]]) -> dict[str, object]:
    return {
        "meta": {"as_of": AS_OF, "symbol": "XAUUSD"},
        "timeframes": {"M15": {"bars": bars, "features": {}, "feature_history": []}},
        "data_quality": {"level": "OK"},
    }


def test_liquidity_normal() -> None:
    reading = analyze_liquidity(_context(_bars_with_last_volume(1000.0)))
    assert reading.volume_ratio == 1.0
    assert reading.state is LiquidityState.NORMAL


def test_liquidity_thin() -> None:
    reading = analyze_liquidity(_context(_bars_with_last_volume(100.0)))
    assert reading.state is LiquidityState.THIN


def test_liquidity_thick() -> None:
    reading = analyze_liquidity(_context(_bars_with_last_volume(3000.0)))
    assert reading.state is LiquidityState.THICK


def test_liquidity_unknown_with_no_bars() -> None:
    reading = analyze_liquidity(_context([]))
    assert reading.state is LiquidityState.UNKNOWN
    assert reading.volume is None
    assert reading.avg_volume is None


def test_liquidity_is_deterministic() -> None:
    ctx = _context(_bars_with_last_volume(1200.0))
    assert analyze_liquidity(ctx) == analyze_liquidity(ctx)
