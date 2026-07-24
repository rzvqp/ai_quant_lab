"""Types owned by Confidence Engine (Phase 8). Reuses `scoring_engine.types.Quality` (values only, zero
engine coupling) and `context_engine.MarketContextSnapshot`/`recognition_engine_live.RecognitionResult`
(read-only inputs, unmodified) -- only the genuinely new grade infrastructure lives here."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ai_trader.scoring_engine.types import Quality


class Grade(str, Enum):
    """CEO's own explicit letter-grade scale -- no existing scale anywhere in this repo to reuse
    (confirmed by repo-wide search, `CONFIDENCE_ENGINE_PHASE8_DESIGN.md` §1)."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"


#: Disclosed, IMPLEMENTATION CHOICE mapping (never tuned against results) -- populates the exact
#: `TradeProposal.confidence_quality` field Phase 2 reserved for this phase.
GRADE_TO_QUALITY: dict[Grade, Quality] = {
    Grade.A: Quality.PREMIUM, Grade.B: Quality.STRONG, Grade.C: Quality.MODERATE, Grade.D: Quality.WEAK,
}


@dataclass(frozen=True, slots=True)
class GradeBands:
    """Explicit, versioned-by-value, never a hidden constant (mirrors `scoring_engine.config.
    QualityBands`'s own established convention for "configurable, not hardcoded" thresholds)."""

    a_threshold: float = 0.80
    b_threshold: float = 0.60
    c_threshold: float = 0.40

    def __post_init__(self) -> None:
        if not (0.0 <= self.c_threshold <= self.b_threshold <= self.a_threshold <= 1.0):
            raise ValueError(
                "GradeBands thresholds must satisfy 0 <= c_threshold <= b_threshold <= a_threshold <= 1"
            )


@dataclass(frozen=True, slots=True)
class ConfidenceEngineConfig:
    bands: GradeBands = field(default_factory=GradeBands)
    require_data_quality_ok: bool = True
    require_not_stale: bool = True
    require_pattern_authorized: bool = True


@dataclass(frozen=True, slots=True)
class ScoreComponents:
    """Every component individually inspectable -- nothing about "why" a grade is what it is is ever
    hidden inside one opaque number (same disclosure discipline as `market_intelligence.
    ContextConfidence`)."""

    context_confidence_component: float | None
    recognition_component: float | None
    #: ALWAYS None -- an explicit, disclosed, DISABLED placeholder. No authorized live strategy-health
    #: signal exists in this pipeline today (CEO: "undefined rules become explicit disabled
    #: placeholders"). Never fabricated, never silently omitted from the type either.
    strategy_health_component: None = None


@dataclass(frozen=True, slots=True)
class CalculationTraceStep:
    """Same shape as the identical type already established in `risk_manager_live`/
    `portfolio_manager_live`/`context_engine`/`recognition_engine_live` -- redeclared here (not
    imported) to keep this package free of any dependency on those sideways packages."""

    stage: str
    passed: bool
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class ConfidenceAssessment:
    """Confidence Engine's own public output. Purely descriptive -- never constructs or submits
    anything (CEO: "never automatically executable"); a caller decides whether/how to build a
    `TradeProposal` from an eligible assessment."""

    strategy_id: str
    symbol: str
    as_of: int
    correlation_id: str
    grade: Grade
    score: float
    components: ScoreComponents
    quality: Quality
    eligible_for_risk_evaluation: bool
    reason_codes: tuple[str, ...]
    calculation_trace: tuple[CalculationTraceStep, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"ConfidenceAssessment.score must be in [0, 1], got {self.score!r}")
        if not self.calculation_trace:
            raise ValueError("ConfidenceAssessment.calculation_trace must be non-empty -- every assessment is traced")
        if self.eligible_for_risk_evaluation and self.grade not in (Grade.A, Grade.B):
            raise ValueError("ConfidenceAssessment: only grade A or B may ever be eligible_for_risk_evaluation")
