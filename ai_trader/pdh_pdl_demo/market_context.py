"""`build_market_context` -- a real `MarketContext` (`ai_trader.strategy_runtime.context_access`,
`dict[str, Any]`, `MARKET_CONTEXT_SCHEMA.json`-shaped) built from the SAME accumulated bars the
recognition rule already holds -- no separate data source, no fabrication. `m15_features` is left
empty: `OrchestratorConfig(recognition_pattern_id=None)` (the SAME config every `mt5_demo_execution`
gating test already uses) means the pipeline never reads a recognition-pattern feature off this
context for PDH-PDL -- Part A's own trigger already lives entirely in `recognition_rule.py`, reusing
ratified primitives, not the generic feature-confidence path."""

from __future__ import annotations

from typing import Any

from ai_trader.live_signal_source.types import Bar
from ai_trader.market_scanner.types import DataQualityLevel


def build_market_context(
    symbol: str, as_of: int, bars: list[Bar], data_quality: DataQualityLevel = DataQualityLevel.OK,
) -> dict[str, Any]:
    m15_bars = [
        {"ts_open": b.ts_open, "ts_close": b.ts_close, "open": b.open, "high": b.high, "low": b.low,
         "close": b.close, "volume": b.volume if b.volume is not None else 0.0}
        for b in bars
    ]
    return {
        "meta": {"as_of": as_of, "symbol": symbol},
        "timeframes": {"M15": {"bars": m15_bars, "features": {}, "feature_history": []}},
        "data_quality": {"level": data_quality.value},
    }
