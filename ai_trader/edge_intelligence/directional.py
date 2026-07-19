"""Directional trend alignment evidence -- Phase 7 Checkpoint 6. Compares a strategy's own
DECLARED directional scope (``Contract.execution.long_short``) against the Market Intelligence
Trend reading on that strategy's own declared execution timeframe. Uses ONLY declared contract
fields -- never infers a directional bias from free-text ``mechanism``/``klass`` descriptions,
since that would be an undisclosed guess, not evidence.
"""

from __future__ import annotations

from ai_trader.edge_intelligence.types import EdgeEvidenceItem, EvidenceContribution
from ai_trader.market_intelligence.types import MarketIntelligenceSnapshot, TrendDirection
from ai_trader.strategy_manager.contract import Contract, LongShort

DIMENSION = "directional_trend_alignment"


def evaluate_directional_alignment(contract: Contract, snapshot: MarketIntelligenceSnapshot) -> EdgeEvidenceItem:
    long_short = contract.execution.long_short
    timeframe = contract.execution.timeframe

    if long_short is LongShort.BOTH:
        return EdgeEvidenceItem(
            DIMENSION, EvidenceContribution.NEUTRAL,
            "strategy declares long_short=BOTH -- no directional constraint to evaluate",
        )

    reading = snapshot.trend.get(timeframe)
    if reading is None:
        return EdgeEvidenceItem(
            DIMENSION, EvidenceContribution.UNKNOWN,
            f"Market Intelligence has no trend reading for the strategy's own execution timeframe {timeframe!r}",
        )

    direction = reading.direction
    if direction in (TrendDirection.FLAT, TrendDirection.UNKNOWN):
        return EdgeEvidenceItem(
            DIMENSION, EvidenceContribution.UNKNOWN,
            f"{timeframe} trend direction is {direction.value} -- not clear enough to confirm or "
            f"contradict a {long_short.value} bias",
        )

    wants_up = long_short is LongShort.LONG
    matches = (direction is TrendDirection.UP) == wants_up
    contribution = EvidenceContribution.SUPPORTS if matches else EvidenceContribution.CONTRADICTS
    return EdgeEvidenceItem(
        DIMENSION, contribution,
        f"strategy declares long_short={long_short.value}; {timeframe} trend direction is "
        f"{direction.value} (strength={reading.strength})",
    )
