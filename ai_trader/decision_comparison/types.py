"""Data structures for the Decision Intelligence v1-vs-v2 falsification study -- Phase 7 Checkpoint 15.

The CEO's own explicit framing: the goal is FALSIFICATION, not confirmation -- "nu presupune ca v2 este
mai bun" (do not assume v2 is better). `FalsificationVerdict` therefore has exactly two members:
`V1_REMAINS_ACTIVE` (the default, safe conclusion whenever no measured evidence of a v2 benefit exists)
and `V2_SUPERIOR_CONFIRMED` (reachable only if a real, disclosed, statistically supported benefit is
measured on real trade-outcome data -- never inferred from explanation richness or evidence attachment
alone, since neither of those changes what actually gets traded).
"""

from __future__ import annotations

import enum
from dataclasses import dataclass


class FalsificationVerdict(str, enum.Enum):
    V1_REMAINS_ACTIVE = "V1_REMAINS_ACTIVE"
    V2_SUPERIOR_CONFIRMED = "V2_SUPERIOR_CONFIRMED"


@dataclass(frozen=True)
class RecommendationComparison:
    """Covers the CEO's own "final recommendation / NO TRADE frequency / edge selection" dimensions --
    computed directly from paired `(v1_report, v2_report)` observations, never assumed."""

    n_compared: int
    divergences: int
    divergence_rate: float
    no_trade_count_v1: int
    no_trade_count_v2: int
    no_trade_frequency_v1: float
    no_trade_frequency_v2: float
    edge_selection_counts_v1: dict[str, int]
    edge_selection_counts_v2: dict[str, int]
    edge_selection_agreement_rate: float
    divergent_as_of: tuple[int, ...]


@dataclass(frozen=True)
class TradeOutcomeEquivalenceProof:
    """Covers the CEO's own "expectancy / win rate / drawdown / false positives / false negatives /
    stability / regime robustness" dimensions. These are all downstream FUNCTIONS of "which
    strategy_id (if any) was recommended on a given bar" -- nothing else about a v1 vs. v2 recommendation
    differs (Checkpoint 14's own structural guarantee: `DecisionReportV2.recommended_strategy_id` is
    construction-time-enforced to equal `v1_report.recommended_strategy_id`). When
    `RecommendationComparison.divergences == 0` over the compared sample, every trade-outcome metric
    computed from that recommendation stream (expectancy, win rate, drawdown, false-positive/-negative
    rate, and recommendation stability across the sampled contexts, i.e. regime robustness AS MEASURED
    BY the recommendation stream itself) is PROVABLY identical between v1 and v2 -- not re-simulated
    here, since re-running an identical backtest twice to confirm a mathematical identity would be a
    purposeless, disclosed-as-such waste rather than genuine falsification work."""

    n_compared: int
    divergences: int
    equivalence_holds: bool
    rationale: str


@dataclass(frozen=True)
class ExplanationQualityResult:
    """A deterministic completeness checklist, never a subjective "quality" score. v1's own
    `comparison_notes` narration is compared against v2's own per-candidate Context Memory attachment
    for whether it discloses all four categories the CEO's own Checkpoint 14 directive requires: why the
    context was found, what evidence exists, what limitations apply, why the evidence status is what it
    is."""

    n_v2_reports: int
    n_candidates_with_context_evidence: int
    n_candidates_disclosing_why_found: int
    n_candidates_disclosing_evidence: int
    n_candidates_disclosing_limitations_when_present: int
    n_candidates_disclosing_status_reason: int
    v2_strictly_more_explanatory_content: bool


@dataclass(frozen=True)
class CalibrationSample:
    """One (Context Memory prediction, realized outcome) pair -- the unit `evaluate_calibration`
    consumes. `predicted_mean` is `ContextualEvidenceReport.mean_normalized_result` at decision time;
    `realized_result` is the ACTUAL normalized outcome once known. Never fabricated -- a caller supplies
    real paired data, or none at all."""

    predicted_mean: float | None
    predicted_status: str
    realized_result: float


@dataclass(frozen=True)
class CalibrationResult:
    """Whether Context Memory's own point estimate carries any measured predictive skill against real
    realized outcomes. `n_samples == 0` is a first-class, honest result ("no real historical outcome
    data available yet"), never silently skipped or defaulted to a fabricated correlation."""

    n_samples: int
    sign_agreement_rate: float | None
    pearson_correlation: float | None
    rationale: str


@dataclass(frozen=True)
class FalsificationReport:
    """The complete Checkpoint 15 study result."""

    recommendation_comparison: RecommendationComparison
    trade_outcome_equivalence: TradeOutcomeEquivalenceProof
    explanation_quality: ExplanationQualityResult
    calibration: CalibrationResult
    verdict: FalsificationVerdict
    rationale: str
