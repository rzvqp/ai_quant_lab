"""Context Validation (``SIGNAL_ENGINE_ARCHITECTURE.md`` §3 stage 3): "check MarketContext
sufficiency vs the strategy's ``required_context()``".

Deliberately does NOT just trust the Market Scanner's own aggregate ``context["sufficiency"]``
field: that aggregate is computed against the UNION of every active strategy's requirements
(Strategy Manager's Context Aggregator), so it can read ``PARTIAL``/``INSUFFICIENT`` even for a
strategy whose OWN, smaller requirement is fully satisfied (some OTHER strategy needs more). This
module checks THIS strategy's OWN ``required_context()`` against the actual context content instead
— per-timeframe presence, per-field non-``None`` values, and per-timeframe bar-count (warmup).
"""

from __future__ import annotations

from ai_trader.signal_engine.types import MarketContext
from ai_trader.strategy_manager.types import RequiredContext


def missing_context_items(context: MarketContext, required: RequiredContext) -> list[str]:
    """Every requirement THIS strategy's ``required_context()`` declares that the actual
    ``MarketContext`` does not satisfy, formatted as ``"<timeframe>"`` (the whole timeframe is
    absent), ``"<timeframe>.<field>"`` (a required field is ``None``/unavailable), or
    ``"<timeframe>.warmup"`` (fewer bars are present than the strategy's own lookback needs).
    Empty means the context is sufficient for this strategy. Deterministic (sorted) ordering.
    """
    missing: list[str] = []
    timeframes_block = context.get("timeframes", {})

    for timeframe in sorted(required.timeframes):
        tf_ctx = timeframes_block.get(timeframe)
        if tf_ctx is None:
            missing.append(timeframe)
            continue

        features = tf_ctx.get("features", {})
        for field_name in sorted(required.fields_by_timeframe.get(timeframe, frozenset())):
            if features.get(field_name) is None:
                missing.append(f"{timeframe}.{field_name}")

        lookback_needed = required.lookback_by_timeframe.get(timeframe, 0)
        if lookback_needed > 0:
            bars = tf_ctx.get("bars", [])
            if len(bars) < lookback_needed:
                missing.append(f"{timeframe}.warmup")

    return missing
