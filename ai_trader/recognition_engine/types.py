"""Data structures for Recognition Engine Phase 1A -- single-dimension conditional statistics
(`RECOGNITION_ENGINE_PHASE1_DESIGN.md`, CEO verdict CONDITIONAL GO, Phase 1A authorization). Every type
here is descriptive-evidence-only: counts, rates, dispersion, sufficiency, provenance. NONE of these types
may ever carry a BUY/SELL/LONG/SHORT/entry/stop/target/lot-size/confidence-to-trade/approve-or-reject
field -- that is the explicit, CEO-mandated output-contract boundary for this phase.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ContextDimension(str, Enum):
    """The single context dimension a caller conditions on for one call -- exactly one per call
    (Phase 1A's own explicit constraint: no multi-dimensional combination). Restricted to
    `ContextSnapshot`'s own already-stored CATEGORICAL fields only -- `context_confidence_score` (the one
    continuous field) is deliberately excluded, mirroring Checkpoint 8 design Sec3.2's own established
    "continuous fields are not a similarity/bucketing dimension" precedent."""

    SESSION = "SESSION"
    TREND_M15 = "TREND_M15"
    TREND_H1 = "TREND_H1"
    TREND_H4 = "TREND_H4"
    TREND_D1 = "TREND_D1"
    STRUCTURE_STATE = "STRUCTURE_STATE"
    MOMENTUM_M15 = "MOMENTUM_M15"
    MOMENTUM_H1 = "MOMENTUM_H1"
    MOMENTUM_H4 = "MOMENTUM_H4"
    MOMENTUM_D1 = "MOMENTUM_D1"
    VOLATILITY_REGIME = "VOLATILITY_REGIME"
    LIQUIDITY_STATE = "LIQUIDITY_STATE"
    EXPANSION_STATE = "EXPANSION_STATE"
    MULTI_TIMEFRAME_AGREEMENT = "MULTI_TIMEFRAME_AGREEMENT"
    DATA_QUALITY_STATE = "DATA_QUALITY_STATE"


class Sufficiency(str, Enum):
    """Whether a bucket's own sample size crosses the configured minimum. `INSUFFICIENT_EVIDENCE` is an
    explicit, first-class state -- never silently reinterpreted as NEUTRAL, FAVORABLE, or UNFAVORABLE
    (CEO's own explicit Phase 1A output-contract rule)."""

    SUFFICIENT = "SUFFICIENT"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass(frozen=True)
class ConditionalStatistics:
    """One bucket's own purely descriptive statistics -- `strategy_id`/`outcome_kind`-isolated (never
    blended, CEO decisions 3-4), conditioned on exactly one `context_dimension`/`context_bucket_value`
    pair. Every field here is DESCRIPTIVE EVIDENCE ONLY: no verdict, no classification label, no
    trading-related field of any kind (the CEO's own explicit output-contract prohibition) -- this type
    structurally cannot represent BUY/SELL/entry/stop/target/lot-size/confidence-to-trade/approval.

    `result` throughout means `PositionOutcome.total_net_pnl` -- NEVER the terminal, per-fill `Outcome`'s
    own `normalized_result` (Recognition Engine Phase 1 Design Sec1/CEO decision 5: `Outcome` alone is proven
    unsafe as a position's own truth by the dataset audit's own 4/688 sign-mismatch finding).
    """

    strategy_id: str
    outcome_kind: str  # OutcomeKind.value -- kept as a plain str here so this type has zero import
    # dependency on context_memory's own enums, mirroring decision_intelligence's own "local echo" precedent
    context_dimension: ContextDimension
    context_bucket_value: str  # e.g. "ny", "HIGH", "DOWN" -- the specific value of context_dimension

    n: int
    favorable_count: int
    unfavorable_count: int
    zero_count: int
    favorable_rate: float | None  # None when n == 0 -- never a fabricated 0.0
    unfavorable_rate: float | None

    mean_result: float | None
    median_result: float | None
    stdev_result: float | None  # dispersion; None when n < 2 (stdev undefined)
    min_result: float | None
    max_result: float | None

    sufficiency: Sufficiency
    min_observations_threshold: int
    data_provenance: str  # repository path + run_id, for full traceability back to the source dataset

    def __post_init__(self) -> None:
        if self.n < 0:
            raise ValueError(f"ConditionalStatistics.n must be >= 0, got {self.n!r}")
        if self.favorable_count + self.unfavorable_count + self.zero_count != self.n:
            raise ValueError(
                "ConditionalStatistics: favorable_count + unfavorable_count + zero_count must equal n, "
                f"got {self.favorable_count} + {self.unfavorable_count} + {self.zero_count} != {self.n}"
            )
        if self.n == 0 and self.sufficiency is not Sufficiency.INSUFFICIENT_EVIDENCE:
            raise ValueError("ConditionalStatistics: n == 0 must always be INSUFFICIENT_EVIDENCE")
