"""Timeframe Sync — lookahead-safe bar-window selection and ``MarketContext.timeframes`` assembly
(``MARKET_SCANNER_ARCHITECTURE.md`` §9, the correctness core).

A bar is usable at ``as_of`` if and only if ``available_at <= as_of`` (``available_at`` is defined
as the bar's own close). This module is the single place that enforces that rule when building the
per-timeframe window handed to strategies, so no other component needs to re-derive it.
"""

from __future__ import annotations

from typing import Any

from ai_trader.market_scanner.bar_store import TimeframeWindow
from ai_trader.market_scanner.types import RawBar


def select_lookahead_safe_bars(
    window: TimeframeWindow | None, as_of: int, lookback_bars: int
) -> list[RawBar]:
    """Return up to ``lookback_bars`` trailing bars from ``window``, all satisfying
    ``available_at <= as_of``, oldest first.

    This filter is applied even though ``window`` should, in the live case, never contain a bar
    ahead of ``as_of`` — it is the load-bearing safeguard against lookahead when a Data Source
    Adapter has pre-loaded history ahead of the replay clock (architecture §9, §11).
    """
    if window is None:
        return []
    safe = [b for b in window.bars() if b.available_at <= as_of]
    if lookback_bars > 0:
        safe = safe[-lookback_bars:]
    return safe


def latest_lookahead_safe_bar(window: TimeframeWindow | None, as_of: int) -> RawBar | None:
    """Return the single most recent bar in ``window`` with ``available_at <= as_of``, if any."""
    bars = select_lookahead_safe_bars(window, as_of, lookback_bars=1)
    return bars[-1] if bars else None


def bar_to_schema_dict(bar: RawBar) -> dict[str, Any]:
    """Render a :class:`RawBar` as the ``$defs/Bar`` shape from ``MARKET_CONTEXT_SCHEMA.json``."""
    return {
        "ts_open": bar.ts_open,
        "ts_close": bar.ts_close,
        "open": bar.open,
        "high": bar.high,
        "low": bar.low,
        "close": bar.close,
        "volume": bar.volume,
        "complete": bar.complete,
        "available_at": bar.available_at,
    }


def build_timeframe_context(
    timeframe: str,
    bars: list[RawBar],
    features: dict[str, Any],
    feature_history: list[dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    """Assemble one ``$defs/TimeframeContext`` entry. ``feature_history`` (Phase 6.8 Wave B
    addition, optional/additive) is the SAME standardized feature namespace computed at each of
    ``bars``' own closes, oldest->newest, index-aligned 1:1 with ``bars`` -- ``None`` entries mean
    that particular bar's own feature snapshot was not retained (never approximated or
    back-filled). Omitted entirely (not merely ``None``) when the caller has no history to offer,
    so existing consumers reading only ``features`` (the current snapshot) are unaffected."""
    context: dict[str, Any] = {
        "timeframe": timeframe,
        "bars": [bar_to_schema_dict(b) for b in bars],
        "features": features,
    }
    if feature_history is not None:
        context["feature_history"] = feature_history
    return context
