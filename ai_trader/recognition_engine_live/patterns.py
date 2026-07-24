"""The authorized/versioned pattern catalog -- CEO: "only authorized/versioned pattern recognition,
never runtime-invented patterns." One entry per `ContextDimension`, all scoped to
`OutcomeKind.STRATEGY` (the per-strategy result unit `recognition_engine`'s own Phase 1A design
declared the primary unit of learning) -- a caller supplies a `pattern_id` from this closed set, never a
raw `(dimension, outcome_kind)` pair. Extending the catalog (a new dimension, or an `OutcomeKind.
PORTFOLIO`-scoped sibling) means adding one new entry here -- no engine code changes."""

from __future__ import annotations

from ai_trader.context_memory import OutcomeKind
from ai_trader.recognition_engine import ContextDimension
from ai_trader.recognition_engine_live.types import RecognitionPattern

AUTHORIZED_PATTERNS: tuple[RecognitionPattern, ...] = tuple(
    RecognitionPattern(
        pattern_id=f"REC-{dimension.value}-STRATEGY", pattern_version="v1", dimension=dimension,
        outcome_kind=OutcomeKind.STRATEGY,
        description=f"Per-strategy conditional statistics bucketed by {dimension.value}.",
    )
    for dimension in ContextDimension
)

_PATTERNS_BY_ID: dict[str, RecognitionPattern] = {p.pattern_id: p for p in AUTHORIZED_PATTERNS}


def pattern_for_id(pattern_id: str) -> RecognitionPattern | None:
    return _PATTERNS_BY_ID.get(pattern_id)
