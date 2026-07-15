"""Shared, read-only helpers for pulling values out of a ``MarketContext`` dict
(``ai_trader.market_scanner``'s own schema shape -- see ``MARKET_CONTEXT_SCHEMA.json``). Every
strategy family evaluator reads context through these functions instead of indexing the dict
directly, so a context-shape change only needs fixing in one place.

**Lookahead safety**: every value here comes from ``context["timeframes"][tf]["bars"/"features"]``,
which the Market Scanner has ALREADY computed lookahead-safely (``select_lookahead_safe_bars``,
architecture §8/§9) for the context's own ``as_of``. These helpers never reach outside the passed-in
``context`` object, so any evaluator built purely from them inherits that guarantee automatically --
there is no way to "peek ahead" without bypassing this module entirely.
"""

from __future__ import annotations

from typing import Any

MarketContext = dict[str, Any]


def as_of(context: MarketContext) -> int:
    return int(context.get("meta", {}).get("as_of", 0))


def symbol(context: MarketContext) -> str:
    return str(context.get("meta", {}).get("symbol", ""))


def timeframe_block(context: MarketContext, timeframe: str) -> dict[str, Any] | None:
    result: dict[str, Any] | None = context.get("timeframes", {}).get(timeframe)
    return result


def features(context: MarketContext, timeframe: str = "M15") -> dict[str, Any]:
    block = timeframe_block(context, timeframe)
    return block.get("features", {}) if block is not None else {}


def feature(context: MarketContext, name: str, timeframe: str = "M15") -> float | None:
    value = features(context, timeframe).get(name)
    if value is None:
        return None
    if isinstance(value, bool):
        return None  # a boolean feature was requested as a number -- caller used the wrong accessor
    if isinstance(value, (int, float)):
        return float(value)
    return None


def flag(context: MarketContext, name: str, timeframe: str = "M15") -> bool | None:
    value = features(context, timeframe).get(name)
    return bool(value) if isinstance(value, bool) else None


def text_feature(context: MarketContext, name: str, timeframe: str = "M15") -> str | None:
    value = features(context, timeframe).get(name)
    return value if isinstance(value, str) else None


def bars(context: MarketContext, timeframe: str = "M15") -> list[dict[str, Any]]:
    """Complete bars for ``timeframe``, oldest first (``build_context``'s own ordering,
    ``select_lookahead_safe_bars``); the LAST element is the most recent CLOSED bar at this
    context's ``as_of`` -- never a still-forming bar (``RawBar.complete`` is always ``True`` here)."""
    block = timeframe_block(context, timeframe)
    if block is None:
        return []
    return list(block.get("bars", []))


def last_bar(context: MarketContext, timeframe: str = "M15") -> dict[str, Any] | None:
    b = bars(context, timeframe)
    return b[-1] if b else None


def bar_n_ago(context: MarketContext, n: int, timeframe: str = "M15") -> dict[str, Any] | None:
    """``n=0`` is the last closed bar, ``n=1`` the one before it, etc. ``None`` if not enough
    history is present (never fabricates a bar)."""
    b = bars(context, timeframe)
    idx = len(b) - 1 - n
    return b[idx] if 0 <= idx < len(b) else None


def session_name(context: MarketContext) -> str | None:
    return text_feature(context, "session")


def data_quality_level(context: MarketContext) -> str:
    dq = context.get("data_quality")
    if isinstance(dq, dict):
        level = dq.get("level")
        if isinstance(level, str):
            return level
    return "OK"
