"""The fixed, per-opportunity risk pipeline (``RISK_MANAGER_ARCHITECTURE.md`` §5, ``RISK_POLICY.md``
§1): Global State -> Opportunity Sanity -> Recommendation Floor -> Pre-Trade Filters -> Portfolio
Limits -> Loss/Drawdown Guards -> Cooldowns -> (ALLOW) Sizing -> Constraints. The FIRST failing gate
denies -- evaluation stops there; ``applied_rules`` records every rule actually run, in order,
including the one that failed (never rules that were never reached).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_trader.risk_manager import filters, guards, limits, sizing as sizing_mod
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.constraints import build_constraints
from ai_trader.risk_manager.types import (
    AppliedRule,
    Constraints,
    DeniedReason,
    EngineState,
    PortfolioState,
    RiskContext,
    Sizing,
)
from ai_trader.scoring_engine.types import ACTIONABLE_STATES, OpportunityScore
from ai_trader.signal_engine.types import Direction


@dataclass(slots=True)
class PipelineOutcome:
    allowed: bool
    applied_rules: tuple[AppliedRule, ...] = ()
    denied_reasons: tuple[DeniedReason, ...] = ()
    sizing: Sizing | None = None
    constraints: Constraints | None = None
    escalate_to: EngineState | None = None


def _valid_stop_side(opportunity: OpportunityScore) -> bool:
    tc = opportunity.trade_context
    if tc is None or tc.entry is None or tc.stop is None:
        return False
    if opportunity.direction is Direction.LONG:
        return tc.stop < tc.entry
    if opportunity.direction is Direction.SHORT:
        return tc.stop > tc.entry
    return False


def evaluate_opportunity(
    opportunity: OpportunityScore,
    context: RiskContext,
    portfolio: PortfolioState,
    config: RiskConfig,
    engine_state: EngineState,
    state_reason_code: str,
) -> PipelineOutcome:
    """Run the fixed gate chain for one opportunity against the (possibly already-updated-by-earlier-
    ALLOWs-in-this-batch) ``portfolio`` view. This function's own logic is pure arithmetic and
    comparisons against a well-formed ``OpportunityScore`` -- but Python dataclasses do not enforce
    field types at runtime, so a malformed upstream object (e.g. ``total_score=None``) CAN still raise
    here (a ``TypeError`` out of the ``>=`` comparison at stage 2, for instance). This function makes
    no attempt to guard against that itself; :mod:`ai_trader.risk_manager.engine` is the actual
    exception safety net (``_evaluate_one``), catching anything raised anywhere in this chain and
    degrading to a classified ``DENY(INTERNAL_ERROR)`` so one malformed opportunity never crashes the
    rest of the batch.
    """
    applied: list[AppliedRule] = []

    # 0. Global State Gate.
    applied.append(AppliedRule(rule="GLOBAL_STATE", passed=engine_state is EngineState.READY))
    if engine_state is not EngineState.READY:
        return PipelineOutcome(
            allowed=False, applied_rules=tuple(applied),
            denied_reasons=(DeniedReason(code=state_reason_code),),
        )

    # 1. Opportunity sanity.
    is_actionable = opportunity.state in ACTIONABLE_STATES
    applied.append(AppliedRule(rule="OPPORTUNITY_SANITY_ACTIONABLE", passed=is_actionable))
    if not is_actionable:
        return PipelineOutcome(
            allowed=False, applied_rules=tuple(applied),
            denied_reasons=(DeniedReason(code="NOT_ACTIONABLE", observed=opportunity.state.value),),
        )
    valid_context = _valid_stop_side(opportunity)
    applied.append(AppliedRule(rule="OPPORTUNITY_SANITY_TRADE_CONTEXT", passed=valid_context))
    if not valid_context:
        return PipelineOutcome(
            allowed=False, applied_rules=tuple(applied),
            denied_reasons=(DeniedReason(code="INVALID_INPUT", detail="missing/invalid trade_context"),),
        )

    # 2. Recommendation floor + minimum score.
    floor_ok = opportunity.recommendation.value in config.allowed_recommendations
    applied.append(AppliedRule(rule="RECOMMENDATION_FLOOR", passed=floor_ok))
    if not floor_ok:
        return PipelineOutcome(
            allowed=False, applied_rules=tuple(applied),
            denied_reasons=(DeniedReason(code="BELOW_FLOOR", observed=opportunity.recommendation.value),),
        )
    score_ok = opportunity.total_score >= config.min_total_score
    applied.append(AppliedRule(rule="MIN_SCORE", passed=score_ok))
    if not score_ok:
        return PipelineOutcome(
            allowed=False, applied_rules=tuple(applied),
            denied_reasons=(DeniedReason(
                code="SCORE_TOO_LOW", observed=opportunity.total_score, limit=config.min_total_score,
            ),),
        )

    # 3. Pre-trade filters.
    for rule_name, result in filters.run_pre_trade_filters(opportunity.symbol, context, config):
        applied.append(AppliedRule(rule=rule_name, passed=result.passed))
        if not result.passed:
            assert result.reason is not None
            return PipelineOutcome(allowed=False, applied_rules=tuple(applied), denied_reasons=(result.reason,))

    # 4. Portfolio limits.
    snapshot = context.for_symbol(opportunity.symbol)
    for rule_name, limit_result in limits.run_portfolio_limits(opportunity.symbol, snapshot, portfolio, config):
        applied.append(AppliedRule(rule=rule_name, passed=limit_result.passed))
        if not limit_result.passed:
            assert limit_result.reason is not None
            return PipelineOutcome(allowed=False, applied_rules=tuple(applied), denied_reasons=(limit_result.reason,))

    # 5. Loss & drawdown guards.
    for rule_name, guard_result in guards.run_loss_drawdown_guards(portfolio, config):
        applied.append(AppliedRule(rule=rule_name, passed=guard_result.passed))
        if not guard_result.passed:
            assert guard_result.reason is not None
            return PipelineOutcome(
                allowed=False, applied_rules=tuple(applied), denied_reasons=(guard_result.reason,),
                escalate_to=guard_result.escalate_to,
            )

    # 6. Cooldowns.
    for rule_name, cooldown_result in guards.run_cooldowns(
        opportunity.symbol, opportunity.strategy_id, portfolio, config,
    ):
        applied.append(AppliedRule(rule=rule_name, passed=cooldown_result.passed))
        if not cooldown_result.passed:
            assert cooldown_result.reason is not None
            return PipelineOutcome(allowed=False, applied_rules=tuple(applied), denied_reasons=(cooldown_result.reason,))

    # -> ALLOW. 7. Sizing.
    sizing_outcome = sizing_mod.compute_sizing(opportunity, portfolio, config)
    applied.append(AppliedRule(rule="POSITION_SIZING", passed=sizing_outcome.valid))
    if not sizing_outcome.valid:
        assert sizing_outcome.deny_reason is not None
        return PipelineOutcome(allowed=False, applied_rules=tuple(applied), denied_reasons=(sizing_outcome.deny_reason,))

    # 8. Constraints.
    constraints_obj = build_constraints(opportunity, config)
    applied.append(AppliedRule(rule="CONSTRAINT_BUILD", passed=True))

    return PipelineOutcome(
        allowed=True, applied_rules=tuple(applied), sizing=sizing_outcome.sizing, constraints=constraints_obj,
    )
