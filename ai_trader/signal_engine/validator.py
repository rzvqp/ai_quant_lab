"""Output Collector's Signal Validation (``SIGNAL_ENGINE_ARCHITECTURE.md`` §7) — validates an
assembled :class:`~ai_trader.signal_engine.types.StrategySignal` against ``SIGNAL_SCHEMA.json`` and
the semantic rules, before it is ever emitted. Also the dict serialization used both for schema
validation and for any external consumer that needs the canonical JSON shape.
"""

from __future__ import annotations

from typing import Any

from ai_trader.signal_engine.schema_validation import validate_explanation_dict, validate_signal_dict
from ai_trader.signal_engine.types import (
    ACTIONABLE_STATES,
    NON_ACTIONABLE_STATES,
    READY_STATES,
    ConditionRecord,
    Confirmations,
    ContextSummary,
    Direction,
    Explanation,
    QualityFlag,
    SignalState,
    StrategySignal,
    TriggeringMechanism,
    ValidationResult,
)

_LONG_STATES = frozenset({SignalState.BUY, SignalState.LONG_READY})
_SHORT_STATES = frozenset({SignalState.SELL, SignalState.SHORT_READY})


def _condition_record_to_dict(rec: ConditionRecord) -> dict[str, Any]:
    return {
        "code": rec.code, "satisfied": rec.satisfied, "label": rec.label,
        "observed": rec.observed, "expected": rec.expected,
    }


def _confirmations_to_dict(c: Confirmations) -> dict[str, Any]:
    return {"required": list(c.required), "met": list(c.met), "pending": list(c.pending)}


def _context_summary_to_dict(cs: ContextSummary) -> dict[str, Any]:
    return {
        "symbol": cs.symbol, "as_of": cs.as_of, "session": cs.session,
        "regime": cs.regime.value if cs.regime else None,
        "data_quality": cs.data_quality.value,
        "timeframes_used": list(cs.timeframes_used) if cs.timeframes_used else None,
    }


def _triggering_mechanism_to_dict(tm: TriggeringMechanism) -> dict[str, Any]:
    return {"mechanism_code": tm.mechanism_code, "mechanism_text": tm.mechanism_text}


def explanation_to_dict(explanation: Explanation) -> dict[str, Any]:
    """Serialize an :class:`Explanation` to the exact ``SIGNAL_EXPLANATION_SCHEMA.json`` shape."""
    return {
        "explanation_schema_version": explanation.explanation_schema_version,
        "strategy_ref": {"id": explanation.strategy_ref.id, "version": explanation.strategy_ref.version},
        "state": explanation.state.value,
        "triggering_mechanism": _triggering_mechanism_to_dict(explanation.triggering_mechanism),
        "why_exists": [_condition_record_to_dict(r) for r in explanation.why_exists],
        "why_failed": [_condition_record_to_dict(r) for r in explanation.why_failed],
        "required_conditions": [_condition_record_to_dict(r) for r in explanation.required_conditions],
        "missing_conditions": [_condition_record_to_dict(r) for r in explanation.missing_conditions],
        "invalid_conditions": [_condition_record_to_dict(r) for r in explanation.invalid_conditions],
        "confirmations": _confirmations_to_dict(explanation.confirmations),
        "context_summary": _context_summary_to_dict(explanation.context_summary),
    }


def signal_to_dict(signal: StrategySignal) -> dict[str, Any]:
    """Serialize a :class:`StrategySignal` to the exact ``SIGNAL_SCHEMA.json`` shape."""
    data: dict[str, Any] = {
        "signal_schema_version": signal.signal_schema_version,
        "signal_engine_version": signal.signal_engine_version,
        "signal_id": signal.signal_id,
        "strategy_id": signal.strategy_id,
        "strategy_version": signal.strategy_version,
        "timestamp": signal.timestamp,
        "as_of": signal.as_of,
        "symbol": signal.symbol,
        "timeframe": signal.timeframe,
        "state": signal.state.value,
        "direction": signal.direction.value,
        "signal_strength": signal.signal_strength,
        "confidence": signal.confidence.value,
        "mechanism": signal.mechanism,
        "required_confirmations": list(signal.required_confirmations),
        "confirmations_met": signal.confirmations_met,
        "missing_context": list(signal.missing_context),
        "invalid_conditions": list(signal.invalid_conditions),
        "quality_flags": [f.value for f in signal.quality_flags],
        "context_ref": {
            "context_schema_version": signal.context_ref.context_schema_version,
            "feature_dictionary_version": signal.context_ref.feature_dictionary_version,
            "interface_version": signal.context_ref.interface_version,
            "data_quality": signal.context_ref.data_quality.value,
            "context_hash": signal.context_ref.context_hash,
        },
        "explanation": explanation_to_dict(signal.explanation),
        "evaluation_time_ms": signal.evaluation_time_ms,
    }
    if signal.trade_params is not None:
        tp = signal.trade_params
        data["trade_params"] = {
            "entry": tp.entry, "stop": tp.stop, "target": tp.target,
            "risk_R": tp.risk_R, "valid_until": tp.valid_until,
        }
    else:
        data["trade_params"] = None
    data["regime"] = signal.regime.value if signal.regime else None
    data["session"] = signal.session
    return data


def validate_signal(
    signal: StrategySignal, known_strategy_ids: frozenset[str] | None = None,
) -> ValidationResult:
    """Validate ``signal`` against ``SIGNAL_SCHEMA.json`` + the semantic rules
    (``SIGNAL_ENGINE_ARCHITECTURE.md`` §7). Pure; used internally before every emit and exposed to
    external callers via ``SignalEngine.validate_signal()``.
    """
    reasons: list[str] = []
    flags: list[QualityFlag] = []

    schema_errors = validate_signal_dict(signal_to_dict(signal))
    if schema_errors:
        reasons.extend(schema_errors)
        flags.append(QualityFlag.SCHEMA_MISMATCH)

    explanation_errors = validate_explanation_dict(explanation_to_dict(signal.explanation))
    if explanation_errors:
        reasons.extend(explanation_errors)
        if QualityFlag.SCHEMA_MISMATCH not in flags:
            flags.append(QualityFlag.SCHEMA_MISMATCH)

    if signal.state in _LONG_STATES and signal.direction is not Direction.LONG:
        reasons.append(f"state {signal.state.value} requires direction=LONG, got {signal.direction.value}")
        flags.append(QualityFlag.INVALID_DIRECTION)
    elif signal.state in _SHORT_STATES and signal.direction is not Direction.SHORT:
        reasons.append(f"state {signal.state.value} requires direction=SHORT, got {signal.direction.value}")
        flags.append(QualityFlag.INVALID_DIRECTION)
    elif signal.state in NON_ACTIONABLE_STATES and signal.direction is not Direction.NONE:
        reasons.append(f"non-actionable state {signal.state.value} requires direction=NONE, got {signal.direction.value}")
        flags.append(QualityFlag.INVALID_DIRECTION)

    if not signal.as_of:
        # StrategySignal.as_of is typed plain `int` (never Optional) -- assembler.assemble_signal's
        # own missing-as_of fallback is `meta.get("as_of", 0)`, so "missing" is represented as the
        # sentinel 0, not None. An `is None` check here would be permanently unreachable dead code;
        # a falsy check catches the real sentinel (and would also catch a stray None if the field's
        # type were ever loosened later -- defense in depth, not just today's exact representation).
        reasons.append("as_of is missing")
        flags.append(QualityFlag.MISSING_TIMESTAMP)

    if known_strategy_ids is not None and signal.strategy_id not in known_strategy_ids:
        reasons.append(f"unknown/inactive strategy id: {signal.strategy_id!r}")
        flags.append(QualityFlag.UNKNOWN_STRATEGY)

    if not signal.context_ref.context_schema_version or not signal.context_ref.feature_dictionary_version:
        reasons.append("context_ref is missing required version fields")
        flags.append(QualityFlag.MISSING_CONTEXT)

    if not (0.0 <= signal.signal_strength <= 1.0):
        reasons.append(f"signal_strength out of [0,1]: {signal.signal_strength!r}")
        flags.append(QualityFlag.INVALID_CONFIDENCE)

    valid = not reasons
    return ValidationResult(valid=valid, reasons=tuple(reasons), quality_flags=tuple(flags) or (QualityFlag.OK,))


__all__ = ["validate_signal", "signal_to_dict", "explanation_to_dict", "ACTIONABLE_STATES", "READY_STATES"]
