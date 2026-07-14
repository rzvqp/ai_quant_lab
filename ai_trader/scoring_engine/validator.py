"""Output Collector's Validation (``SCORING_ENGINE_ARCHITECTURE.md`` §5, ``SCORING_API.md`` §2
``validate()``) — validates an assembled :class:`~ai_trader.scoring_engine.types.OpportunityScore`
against ``SCORING_SCHEMA.json`` and the semantic rules, before it is ever emitted. Also the dict
serialization used both for schema validation and for any external consumer that needs the canonical
JSON shape.
"""

from __future__ import annotations

from typing import Any

from ai_trader.scoring_engine.schema_validation import validate_score_dict
from ai_trader.scoring_engine.types import (
    NON_ACTIONABLE_STATES,
    OpportunityScore,
    Recommendation,
    ValidationResult,
)
from ai_trader.signal_engine.types import Direction

_VALID_NON_ACTIONABLE_RECOMMENDATIONS = frozenset({Recommendation.SKIP, Recommendation.INVALID})


def score_to_dict(score: OpportunityScore) -> dict[str, Any]:
    """Serialize an :class:`OpportunityScore` to the exact ``SCORING_SCHEMA.json`` shape."""
    cs = score.component_scores
    data: dict[str, Any] = {
        "scoring_schema_version": score.scoring_schema_version,
        "scoring_engine_version": score.scoring_engine_version,
        "scoring_model_version": score.scoring_model_version,
        "score_id": score.score_id,
        "signal_id": score.signal_id,
        "strategy_id": score.strategy_id,
        "symbol": score.symbol,
        "timestamp": score.timestamp,
        "as_of": score.as_of,
        "state": score.state.value,
        "direction": score.direction.value,
        "total_score": score.total_score,
        "component_scores": {
            "signal_strength": cs.signal_strength,
            "historical_confidence": cs.historical_confidence,
            "market_alignment": cs.market_alignment,
            "regime_alignment": cs.regime_alignment,
            "confirmation_quality": cs.confirmation_quality,
            "data_quality": cs.data_quality,
            "execution_readiness": cs.execution_readiness,
            "risk_penalty": cs.risk_penalty,
            "conflict_penalty": cs.conflict_penalty,
        },
        "confidence": score.confidence.value,
        "quality": score.quality.value,
        "recommendation": score.recommendation.value,
        "rank": score.rank,
        "reason_codes": [
            {"code": r.code, "component": r.component, "detail": r.detail} for r in score.reason_codes
        ],
        "refs": {
            "strategy_version": score.refs.strategy_version,
            "signal_schema_version": score.refs.signal_schema_version,
            "interface_version": score.refs.interface_version,
            "data_quality": score.refs.data_quality.value,
        },
    }
    if score.base_quality is not None:
        data["base_quality"] = score.base_quality
    if score.penalty_factor is not None:
        data["penalty_factor"] = score.penalty_factor
    if score.trade_context is not None:
        tc = score.trade_context
        data["trade_context"] = {"entry": tc.entry, "stop": tc.stop, "target": tc.target, "risk_R": tc.risk_R}
    return data


def validate_score(score: OpportunityScore) -> ValidationResult:
    """Validate ``score`` against ``SCORING_SCHEMA.json`` + the semantic rules (``SCORING_API.md``
    §2: "total in [0,100], components in [0,1], band <-> quality <-> recommendation consistency,
    non-actionable => SKIP/INVALID"). Pure; used internally before every emit and exposed via
    ``ScoringEngine.validate()``.
    """
    reasons: list[str] = []

    schema_errors = validate_score_dict(score_to_dict(score))
    reasons.extend(schema_errors)

    if not (0 <= score.total_score <= 100):
        reasons.append(f"total_score out of [0,100]: {score.total_score!r}")

    cs = score.component_scores
    for name, value in (
        ("signal_strength", cs.signal_strength), ("historical_confidence", cs.historical_confidence),
        ("market_alignment", cs.market_alignment), ("regime_alignment", cs.regime_alignment),
        ("confirmation_quality", cs.confirmation_quality), ("data_quality", cs.data_quality),
        ("execution_readiness", cs.execution_readiness), ("risk_penalty", cs.risk_penalty),
        ("conflict_penalty", cs.conflict_penalty),
    ):
        if not (0.0 <= value <= 1.0):
            reasons.append(f"component {name} out of [0,1]: {value!r}")

    if score.state in NON_ACTIONABLE_STATES:
        if score.direction is not Direction.NONE:
            reasons.append(f"non-actionable state {score.state.value} requires direction=NONE, got {score.direction.value}")
        if score.recommendation not in _VALID_NON_ACTIONABLE_RECOMMENDATIONS:
            reasons.append(
                f"non-actionable state {score.state.value} requires recommendation in "
                f"{{SKIP, INVALID}}, got {score.recommendation.value}",
            )

    if score.rank < 1:
        reasons.append(f"rank must be >= 1, got {score.rank!r}")

    if not score.reason_codes:
        reasons.append("reason_codes must be non-empty")

    return ValidationResult(valid=not reasons, reasons=tuple(reasons))


__all__ = ["validate_score", "score_to_dict"]
