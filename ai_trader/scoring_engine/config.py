"""Configuration objects for the Scoring Engine.

A single :class:`ScoringConfig` instance is supplied to the :class:`~ai_trader.scoring_engine.engine.
ScoringEngine` constructor and never mutated afterwards — mirrors the Market Scanner/Strategy Manager/
Signal Engine ``*Config`` convention (immutable-by-convention configuration).

Every constant below is either transcribed verbatim from ``SCORING_MODEL.md`` (the quality-component
weights, the quality bands, the ``historical_confidence`` formula constants) or is an explicit,
documented value filling a genuine gap the model leaves to the implementer (marked "IMPLEMENTATION
CHOICE" below) — never an invented reinterpretation of anything the model DOES specify.
"""

from __future__ import annotations

from dataclasses import dataclass, field

#: The versions this build of the engine emits/targets (architecture §10). Bump deliberately.
SCORING_ENGINE_VERSION = "1.0.0"
SCORING_SCHEMA_VERSION = "1.0.0"
#: The component set, weights, and formula this build implements (``SCORING_MODEL.md`` §title).
SCORING_MODEL_VERSION = "1.0.0"

#: The Strategy Interface / Signal-schema MAJOR versions this build supports (architecture §10
#: "Compatibility"). A signal reporting a higher MAJOR degrades to a classified INVALID score rather
#: than being silently accepted.
DEFAULT_SUPPORTED_SIGNAL_SCHEMA_MAJOR = 1
DEFAULT_SUPPORTED_INTERFACE_MAJOR = 1


@dataclass(frozen=True, slots=True)
class ComponentWeights:
    """The seven quality-component weights (``SCORING_MODEL.md`` §5) — sum to 1.00 exactly, fixed
    per ``scoring_model_version``. Re-weighting is a versioned change, never live/learned."""

    signal_strength: float = 0.20
    historical_confidence: float = 0.20
    market_alignment: float = 0.12
    regime_alignment: float = 0.15
    confirmation_quality: float = 0.15
    data_quality: float = 0.10
    execution_readiness: float = 0.08

    def __post_init__(self) -> None:
        total = (
            self.signal_strength + self.historical_confidence + self.market_alignment
            + self.regime_alignment + self.confirmation_quality + self.data_quality
            + self.execution_readiness
        )
        if abs(total - 1.00) > 1e-9:
            raise ValueError(f"ComponentWeights must sum to 1.00, got {total!r}")


@dataclass(frozen=True, slots=True)
class QualityBands:
    """``total_score`` (0-100) → ``quality`` enum band thresholds (``SCORING_MODEL.md`` §6, exact:
    PREMIUM >=80, STRONG 65-79, MODERATE 45-64, WEAK 25-44, POOR <25)."""

    premium_min: int = 80
    strong_min: int = 65
    moderate_min: int = 45
    weak_min: int = 25


@dataclass(frozen=True, slots=True)
class RecommendationBands:
    """``total_score`` → the actionable-state ``recommendation`` tier thresholds (``SCORING_MODEL.md``
    §6: STRONG_OPPORTUNITY >=65, MODERATE_OPPORTUNITY 45-64, WEAK_OPPORTUNITY 25-44; below 25 an
    actionable signal still gets ``SKIP`` — a score too low to call an "opportunity", matching the
    architecture's own "non-actionable/low -> SKIP" wording)."""

    strong_min: int = 65
    moderate_min: int = 45
    weak_min: int = 25


@dataclass(frozen=True, slots=True)
class ConfidenceBands:
    """IMPLEMENTATION CHOICE: ``historical_confidence`` ([0,1]) -> ``confidence`` enum band
    thresholds. ``SCORING_MODEL.md`` §6 says only "mirrors the contract tiers" without giving exact
    cut points — the contract's own ``maturity_prior`` anchors (0.15/0.30/0.45/0.75/1.00, §3) are used
    as the band centers, since realistic ``historical_confidence`` values sit AT OR BELOW their
    strategy's own ``maturity_prior`` (the ``oos_factor``/validation multiplier is always <=1.0 pre-
    honesty-bonus-cap). Documented explicitly since the model does not fix these numbers."""

    high_min: float = 0.65
    medium_min: float = 0.40
    low_min: float = 0.20
    very_low_min: float = 0.0  # anything > 0 and < low_min; exactly 0.0 -> NONE


@dataclass(frozen=True, slots=True)
class RiskPenaltyWeights:
    """IMPLEMENTATION CHOICE: the ``w_dd``/``w_fr``/``w_n`` weights in ``risk_penalty``'s formula
    (``SCORING_MODEL.md`` §2 row 8: "clamp(w_dd*norm(drawdown_R) + w_fr*fragile + w_n*smallN, 0, 1)")
    — the model gives the formula SHAPE but not the exact weights. Chosen to sum to 1.00 so a
    strategy that is simultaneously maximally drawdown-risky, fragile, and tiny-sample reaches exactly
    the full [0,1] penalty range via ``clamp`` without any one factor alone dominating."""

    drawdown: float = 0.4
    fragile: float = 0.3
    small_sample: float = 0.3

    def __post_init__(self) -> None:
        total = self.drawdown + self.fragile + self.small_sample
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"RiskPenaltyWeights must sum to 1.00, got {total!r}")


@dataclass(frozen=True, slots=True)
class RiskPenaltyThresholds:
    """IMPLEMENTATION CHOICE: normalization constants for ``risk_penalty``'s three inputs, each
    filling a gap ``SCORING_MODEL.md`` §2 leaves unspecified (it names the inputs -- historical
    ``drawdown_R``, ``fragile``, tiny sample ``n`` -- but not their exact normalization). Missing
    evidence for any of these three is treated as the WORST case (maximal contribution), never the
    best -- consistent with the model's own honesty-preserving philosophy (§1.2: "the rubric cannot
    make an unvalidated... strategy look strong"; an undisclosed risk metric is not evidence of safety).
    """

    #: `norm(drawdown_R) = clamp(drawdown_R / cap, 0, 1)`; a strategy with a `drawdown_R` at or beyond
    #: this many R-multiples gets the full drawdown penalty contribution.
    drawdown_norm_cap_r: float = 10.0
    #: `fragile = top1_share > threshold` (fraction of total historical profit from a single trade).
    fragile_top1_share_threshold: float = 0.5
    #: `smallN = clamp(1 - n / full, 0, 1)`; a strategy with at least this many historical trades gets
    #: zero small-sample penalty contribution.
    small_sample_full_n: int = 100


@dataclass(slots=True)
class ScoringConfig:
    """Immutable-by-convention configuration for one :class:`ScoringEngine` instance.

    Attributes:
        weights: the seven fixed quality-component weights.
        quality_bands, recommendation_bands, confidence_bands: total_score/historical_confidence ->
            enum banding.
        risk_penalty_weights, risk_penalty_thresholds: the ``risk_penalty`` component's internal
            constants.
        supported_signal_schema_major, supported_interface_major: the MAJOR versions this build
            accepts from an incoming ``StrategySignal``.
        scoring_engine_version, scoring_schema_version, scoring_model_version: stamped on every
            emitted score (architecture §10).
    """

    weights: ComponentWeights = field(default_factory=ComponentWeights)
    quality_bands: QualityBands = field(default_factory=QualityBands)
    recommendation_bands: RecommendationBands = field(default_factory=RecommendationBands)
    confidence_bands: ConfidenceBands = field(default_factory=ConfidenceBands)
    risk_penalty_weights: RiskPenaltyWeights = field(default_factory=RiskPenaltyWeights)
    risk_penalty_thresholds: RiskPenaltyThresholds = field(default_factory=RiskPenaltyThresholds)
    supported_signal_schema_major: int = DEFAULT_SUPPORTED_SIGNAL_SCHEMA_MAJOR
    supported_interface_major: int = DEFAULT_SUPPORTED_INTERFACE_MAJOR
    scoring_engine_version: str = SCORING_ENGINE_VERSION
    scoring_schema_version: str = SCORING_SCHEMA_VERSION
    scoring_model_version: str = SCORING_MODEL_VERSION

    def __post_init__(self) -> None:
        if self.supported_signal_schema_major < 1:
            raise ValueError("ScoringConfig.supported_signal_schema_major must be >= 1")
        if self.supported_interface_major < 1:
            raise ValueError("ScoringConfig.supported_interface_major must be >= 1")
