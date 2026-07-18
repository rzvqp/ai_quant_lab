"""Shared ``MarketContext`` fixture builder for Market Intelligence unit tests -- the same
"reusable fixture module" convention already established by
``ai_trader.scoring_engine.tests.fixtures.fake_strategy_manager``. Builds a schema-shaped dict by
hand (``MARKET_CONTEXT_SCHEMA.json``), not a real ``MarketScanner`` run -- fast, isolated, no market
data needed for unit-level tests. See ``test_engine.py`` for a real-data integration test.
"""

from __future__ import annotations

from typing import Any

AS_OF = 1_700_000_000
BAR_SECONDS = 900  # M15


def make_bar(ts_close: int, open_: float, high: float, low: float, close: float, volume: float = 1000.0) -> dict[str, Any]:
    return {
        "ts_open": ts_close - BAR_SECONDS, "ts_close": ts_close,
        "open": open_, "high": high, "low": low, "close": close, "volume": volume,
    }


def make_flat_bars(n: int, start_as_of: int, price: float = 2000.0, volume: float = 1000.0) -> list[dict[str, Any]]:
    """``n`` identical, featureless bars -- a neutral baseline other tests perturb."""
    return [
        make_bar(start_as_of + i * BAR_SECONDS, price, price, price, price, volume)
        for i in range(n)
    ]


def make_context(
    as_of: int = AS_OF,
    symbol: str = "XAUUSD",
    m15_features: dict[str, Any] | None = None,
    m15_bars: list[dict[str, Any]] | None = None,
    data_quality_level: str = "OK",
    other_timeframes: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """A minimal, schema-shaped ``MarketContext``. ``m15_features``/``m15_bars`` default to empty --
    every analyzer must handle that honestly (``UNKNOWN``/``None``, never fabricated), exercised
    directly by the "missing data" tests in each analyzer's own test file."""
    timeframes: dict[str, dict[str, Any]] = {
        "M15": {"bars": m15_bars or [], "features": m15_features or {}, "feature_history": []},
    }
    if other_timeframes:
        timeframes.update(other_timeframes)
    return {
        "meta": {"as_of": as_of, "symbol": symbol},
        "timeframes": timeframes,
        "data_quality": {"level": data_quality_level},
    }
