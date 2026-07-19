"""Data structures for the Edge Intelligence layer -- Phase 7 Checkpoint 6. Determines, per
registered strategy, whether its statistical edge is currently PRESENT / POSSIBLE / ABSENT in the
market -- never a health score, never a trade decision. Every reading is explainable via a tuple
of :class:`EdgeEvidenceItem`: concrete, disclosed, deterministic checks against the strategy's own
declared :class:`~ai_trader.strategy_manager.contract.Contract` and the current
:class:`~ai_trader.market_intelligence.types.MarketIntelligenceSnapshot`, never a hidden or
probabilistic judgment. No field here is a scoring/classification output -- there is zero overlap
with :mod:`ai_trader.strategy_health`'s own ``HealthState``/``WindowScore``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EvidenceContribution(str, Enum):
    """How one evidence item weighs on the overall edge verdict -- see
    :func:`ai_trader.edge_intelligence.verdict.determine_edge_state` for the combination rule."""

    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class EdgeState(str, Enum):
    """Whether a strategy's statistical edge is currently recognizable in the market. Never a
    trade decision -- PRESENT does not mean "take this trade", it means "no disclosed evidence
    dimension currently contradicts this strategy's own declared requirements"."""

    PRESENT = "PRESENT"
    POSSIBLE = "POSSIBLE"
    ABSENT = "ABSENT"


@dataclass(frozen=True)
class EdgeEvidenceItem:
    """One concrete, explainable check. ``explanation`` always names the actual observed values
    (never a vague phrase) so a human can verify the verdict without re-deriving it -- "No hidden
    reasoning" (CEO Checkpoint 6 directive)."""

    dimension: str
    contribution: EvidenceContribution
    explanation: str


@dataclass(frozen=True)
class StrategyEdgeReading:
    """One strategy's edge verdict plus every evidence item that produced it."""

    strategy_id: str
    as_of: int
    state: EdgeState
    evidence: tuple[EdgeEvidenceItem, ...]

    def __post_init__(self) -> None:
        if not self.evidence:
            raise ValueError(
                "StrategyEdgeReading requires at least one evidence item -- a verdict with no "
                "disclosed reasoning is exactly what this layer must never produce"
            )


@dataclass(frozen=True)
class EdgeIntelligenceSnapshot:
    """One point-in-time view across every strategy this layer could evaluate -- keyed by
    strategy id, always covering every registered strategy with a readable contract (never a
    silently-truncated subset): "if twenty strategies are present, report twenty; if zero are
    present, report zero" (CEO Checkpoint 6 directive)."""

    symbol: str
    as_of: int
    readings: dict[str, StrategyEdgeReading]
