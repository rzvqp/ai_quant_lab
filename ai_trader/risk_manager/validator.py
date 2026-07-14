"""Output Collector's Validation (``RISK_MANAGER_ARCHITECTURE.md`` §6, ``RISK_API.md`` §2
``validate()``) -- validates an assembled :class:`~ai_trader.risk_manager.types.RiskDecision`
against ``RISK_SCHEMA.json`` and the semantic rules before it is ever emitted. Also the dict
serialization used both for schema validation and for any external consumer needing the canonical
JSON shape.
"""

from __future__ import annotations

from typing import Any

from ai_trader.risk_manager.schema_validation import validate_decision_dict
from ai_trader.risk_manager.types import Decision, RiskDecision, ValidationResult
from ai_trader.signal_engine.types import Direction


def decision_to_dict(decision: RiskDecision) -> dict[str, Any]:
    """Serialize a :class:`RiskDecision` to the exact ``RISK_SCHEMA.json`` shape."""
    data: dict[str, Any] = {
        "risk_schema_version": decision.risk_schema_version,
        "risk_engine_version": decision.risk_engine_version,
        "risk_policy_version": decision.risk_policy_version,
        "decision_id": decision.decision_id,
        "score_id": decision.score_id,
        "signal_id": decision.signal_id,
        "strategy_id": decision.strategy_id,
        "symbol": decision.symbol,
        "timestamp": decision.timestamp,
        "as_of": decision.as_of,
        "engine_state": decision.engine_state.value,
        "decision": decision.decision.value,
        "direction": decision.direction.value,
        "denied_reasons": [
            {"code": r.code, "detail": r.detail, "observed": r.observed, "limit": r.limit}
            for r in decision.denied_reasons
        ],
        "applied_rules": [
            {"rule": r.rule, "passed": r.passed, "detail": r.detail} for r in decision.applied_rules
        ],
        "refs": {
            "scoring_schema_version": decision.refs.scoring_schema_version,
            "interface_version": decision.refs.interface_version,
            "account_equity": decision.refs.account_equity,
            "data_quality": decision.refs.data_quality.value if decision.refs.data_quality else None,
        },
    }

    if decision.sizing is None:
        data["sizing"] = None
    else:
        s = decision.sizing
        data["sizing"] = {
            "method": s.method.value, "risk_per_trade_pct": s.risk_per_trade_pct,
            "quality_factor": s.quality_factor, "risk_R": s.risk_R,
            "risk_budget_currency": s.risk_budget_currency, "stop_distance": s.stop_distance,
            "size_units": s.size_units, "size_lots": s.size_lots, "min_size": s.min_size,
            "max_size": s.max_size, "notional": s.notional, "leverage": s.leverage,
            "partial_exit_plan": (
                [{"at_R": e.at_R, "fraction": e.fraction} for e in s.partial_exit_plan]
                if s.partial_exit_plan is not None else None
            ),
        }

    if decision.constraints is None:
        data["constraints"] = None
    else:
        c = decision.constraints
        data["constraints"] = {
            "entry": c.entry, "stop": c.stop, "target": c.target, "max_hold_bars": c.max_hold_bars,
            "valid_until": c.valid_until, "max_slippage": c.max_slippage,
            "allowed_session": c.allowed_session, "reduce_only": c.reduce_only,
        }

    if decision.portfolio_impact is None:
        data["portfolio_impact"] = None
    else:
        pi = decision.portfolio_impact
        data["portfolio_impact"] = {
            "open_positions_after": pi.open_positions_after,
            "portfolio_risk_pct_after": pi.portfolio_risk_pct_after,
            "leverage_after": pi.leverage_after,
            "correlation_group": pi.correlation_group,
        }

    return data


def validate_decision(decision: RiskDecision) -> ValidationResult:
    """Validate ``decision`` against ``RISK_SCHEMA.json`` + the semantic rules (``RISK_API.md`` §2:
    "ALLOW => sizing>=min + valid stop + state READY; DENY => non-empty reasons"). Pure; used
    internally before every emit and exposed via ``RiskManager.validate()``.
    """
    reasons: list[str] = []

    schema_errors = validate_decision_dict(decision_to_dict(decision))
    reasons.extend(schema_errors)

    if decision.decision is Decision.DENY:
        if not decision.denied_reasons:
            reasons.append("DENY decision must carry at least one denied_reason")
        if decision.sizing is not None or decision.constraints is not None:
            reasons.append("DENY decision must not carry sizing/constraints")

    if decision.decision is Decision.ALLOW:
        if decision.sizing is None:
            reasons.append("ALLOW decision must carry sizing")
        elif decision.sizing.size_units < decision.sizing.min_size:
            reasons.append(
                f"ALLOW sizing.size_units {decision.sizing.size_units!r} below min_size "
                f"{decision.sizing.min_size!r}",
            )
        if decision.constraints is None:
            reasons.append("ALLOW decision must carry constraints")
        elif decision.constraints.stop is None:
            reasons.append("ALLOW decision must carry a valid stop")
        if decision.direction is Direction.NONE:
            reasons.append("ALLOW decision must carry a concrete direction")
        if decision.engine_state.value != "READY":
            reasons.append(f"ALLOW decision requires engine_state=READY, got {decision.engine_state.value}")

    return ValidationResult(valid=not reasons, reasons=tuple(reasons))


__all__ = ["validate_decision", "decision_to_dict"]
