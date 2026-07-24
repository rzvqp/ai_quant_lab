"""Types owned by Recognition Engine (live wiring, Phase 7). Reuses `recognition_engine.types.
ConditionalStatistics`/`ContextDimension`/`Sufficiency` and `context_memory.OutcomeKind` unmodified --
only the genuinely missing pieces (the authorized pattern catalog, the live candidate/result envelope)
live here."""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_trader.context_memory import OutcomeKind
from ai_trader.recognition_engine import ConditionalStatistics, ContextDimension, Sufficiency


@dataclass(frozen=True, slots=True)
class RecognitionPattern:
    """One entry in the authorized/versioned pattern catalog. A live caller may only query a
    `pattern_id` that appears in `AUTHORIZED_PATTERNS` -- CEO: "only authorized/versioned pattern
    recognition, never runtime-invented patterns." `pattern_id` and `pattern_version` are both
    caller-declared and literal, never inferred (same discipline as `context_memory.SchemaVersion`)."""

    pattern_id: str
    pattern_version: str
    dimension: ContextDimension
    outcome_kind: OutcomeKind
    description: str

    def __post_init__(self) -> None:
        if not self.pattern_id:
            raise ValueError("RecognitionPattern.pattern_id must be non-empty")
        if not self.pattern_version:
            raise ValueError("RecognitionPattern.pattern_version must be non-empty")
        if not self.description:
            raise ValueError("RecognitionPattern.description must be non-empty")


@dataclass(frozen=True, slots=True)
class RecognitionCandidate:
    """The live query input -- one strategy, one authorized pattern, one point in time. Never carries
    a raw `(dimension, outcome_kind)` pair directly -- only a `pattern_id`, so an unauthorized
    combination is structurally unreachable, not merely discouraged."""

    strategy_id: str
    pattern_id: str
    as_of: int
    correlation_id: str

    def __post_init__(self) -> None:
        if not self.strategy_id:
            raise ValueError("RecognitionCandidate.strategy_id must be non-empty")
        if not self.pattern_id:
            raise ValueError("RecognitionCandidate.pattern_id must be non-empty")
        if not self.correlation_id:
            raise ValueError("RecognitionCandidate.correlation_id must be non-empty")


@dataclass(frozen=True, slots=True)
class CalculationTraceStep:
    """Same shape as the identical type already established in `risk_manager_live`/
    `portfolio_manager_live`/`context_engine` -- redeclared here (not imported) to keep this package
    free of any dependency on those downstream/sideways packages."""

    stage: str
    passed: bool
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class RecognitionResult:
    """The live query output -- ALWAYS descriptive statistics (or an explicit absence of them), NEVER a
    trading recommendation (the exact Phase 1A discipline, carried forward unchanged). No field here
    could be mistaken for a trade decision -- `pattern_authorized` is a catalog-membership fact, not an
    "approved to trade" signal."""

    strategy_id: str
    pattern_id: str
    pattern_version: str | None
    as_of: int
    correlation_id: str
    context_bucket_value: str | None
    statistics: ConditionalStatistics | None
    sufficiency: Sufficiency
    pattern_authorized: bool
    reason_codes: tuple[str, ...]
    calculation_trace: tuple[CalculationTraceStep, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.calculation_trace:
            raise ValueError("RecognitionResult.calculation_trace must be non-empty -- every query is traced")
