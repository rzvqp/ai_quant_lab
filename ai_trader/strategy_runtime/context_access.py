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


def feature_history(context: MarketContext, timeframe: str = "M15") -> list[dict[str, Any] | None]:
    """The per-bar feature snapshot history (Phase 6.8 Wave B addition,
    ``ai_trader.market_scanner.scanner``'s own ``_base_feature_history``), oldest-first, index
    -aligned 1:1 with :func:`bars` -- an entry is ``None`` where that specific bar's own snapshot
    was not retained. Empty list if the producing Market Scanner omitted this optional field
    entirely (a fixture/test scanner not carrying this Phase 6.8 addition, or a non-base
    timeframe that does not yet populate it)."""
    block = timeframe_block(context, timeframe)
    if block is None:
        return []
    raw = block.get("feature_history")
    return list(raw) if isinstance(raw, list) else []


def feature_n_ago(context: MarketContext, name: str, n: int, timeframe: str = "M15") -> float | None:
    """The numeric value of feature ``name`` as of the bar ``n`` bars ago (``n=0`` is the last
    closed bar, matching :func:`bar_n_ago`'s own convention) -- ``None`` if that bar's own
    snapshot was not retained, the feature is absent/non-numeric there, or ``n`` reaches before
    the retained history (never fabricates a value)."""
    history = feature_history(context, timeframe)
    idx = len(history) - 1 - n
    if not (0 <= idx < len(history)):
        return None
    snapshot = history[idx]
    if snapshot is None:
        return None
    value = snapshot.get(name)
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def flag_n_ago(context: MarketContext, name: str, n: int, timeframe: str = "M15") -> bool | None:
    """The boolean value of feature ``name`` as of the bar ``n`` bars ago -- see
    :func:`feature_n_ago` for the shared semantics."""
    history = feature_history(context, timeframe)
    idx = len(history) - 1 - n
    if not (0 <= idx < len(history)):
        return None
    snapshot = history[idx]
    if snapshot is None:
        return None
    value = snapshot.get(name)
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
