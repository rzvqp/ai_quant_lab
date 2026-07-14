"""Builds the final ``RiskDecision`` from a :class:`~ai_trader.risk_manager.pipeline.PipelineOutcome`.

**Determinism note on ``timestamp``**: set to the opportunity's own ``as_of`` (never wall-clock) --
matching Signal/Scoring Engine's own precedent and ``RISK_MANAGER_ARCHITECTURE.md`` §9's "No ML, no
randomness, no wall-clock in the logic." There is no dedicated informational timing field in
``RISK_SCHEMA.json`` (unlike Signal Engine's ``evaluation_time_ms``), so this module contains no
``time`` import at all.
"""

from __future__ import annotations

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.pipeline import PipelineOutcome
from ai_trader.risk_manager.types import (
    Decision,
    EngineState,
    PortfolioImpact,
    PortfolioState,
    RiskDecision,
    RiskRefs,
)
from ai_trader.scoring_engine.types import OpportunityScore
from ai_trader.signal_engine.types import Direction


def assemble_decision(
    opportunity: OpportunityScore,
    outcome: PipelineOutcome,
    engine_state: EngineState,
    config: RiskConfig,
    portfolio_after: PortfolioState | None = None,
) -> RiskDecision:
    decision_id = f"{opportunity.strategy_id}|{opportunity.symbol}|{opportunity.as_of}"
    refs = RiskRefs(
        scoring_schema_version=opportunity.scoring_schema_version,
        interface_version=opportunity.refs.interface_version,
        account_equity=portfolio_after.equity if portfolio_after is not None else None,
        data_quality=opportunity.refs.data_quality,
    )

    if not outcome.allowed:
        return RiskDecision(
            risk_schema_version=config.risk_schema_version, risk_engine_version=config.risk_engine_version,
            risk_policy_version=config.risk_policy_version, decision_id=decision_id,
            score_id=opportunity.score_id, signal_id=opportunity.signal_id, strategy_id=opportunity.strategy_id,
            symbol=opportunity.symbol, timestamp=opportunity.as_of, as_of=opportunity.as_of,
            engine_state=engine_state, decision=Decision.DENY, direction=Direction.NONE,
            applied_rules=outcome.applied_rules, refs=refs, denied_reasons=outcome.denied_reasons,
            sizing=None, constraints=None, portfolio_impact=None,
        )

    portfolio_impact = None
    if portfolio_after is not None:
        portfolio_impact = PortfolioImpact(
            open_positions_after=len(portfolio_after.open_positions),
            portfolio_risk_pct_after=portfolio_after.portfolio_risk_pct,
            leverage_after=portfolio_after.leverage,
            correlation_group=config.correlation_group_for(opportunity.symbol),
        )

    return RiskDecision(
        risk_schema_version=config.risk_schema_version, risk_engine_version=config.risk_engine_version,
        risk_policy_version=config.risk_policy_version, decision_id=decision_id,
        score_id=opportunity.score_id, signal_id=opportunity.signal_id, strategy_id=opportunity.strategy_id,
        symbol=opportunity.symbol, timestamp=opportunity.as_of, as_of=opportunity.as_of,
        engine_state=EngineState.READY, decision=Decision.ALLOW, direction=opportunity.direction,
        applied_rules=outcome.applied_rules, refs=refs, denied_reasons=(),
        sizing=outcome.sizing, constraints=outcome.constraints, portfolio_impact=portfolio_impact,
    )


def assemble_invalid_decision(
    opportunity: object, config: RiskConfig, reason_code: str = "INTERNAL_VALIDATION_FAILED",
    detail: str | None = None, engine_state: EngineState = EngineState.READY,
) -> RiskDecision:
    """The fail-safe fallback for a decision that could not even be assembled from valid identity
    fields (an internal error, or a genuinely malformed input) -- architecture §6: "a validation
    failure -> a fail-safe DENY decision with reason INTERNAL_VALIDATION_FAILED, never a malformed
    ALLOW." ``opportunity`` is typed ``object`` deliberately: this is the one path reachable even when
    the caller passed something that is not a genuine :class:`OpportunityScore` at all.

    ``engine_state`` defaults to ``READY`` only for callers with no better information -- pass the
    ACTUAL global state when known (``_finalize_decision`` always does) so a fallback decision
    produced while the engine is SUSPENDED/EMERGENCY_STOP doesn't misreport itself as READY, which
    would make it inconsistent with the batch-level ``RiskDecisionBatch.engine_state``.
    """
    from ai_trader.risk_manager.types import DeniedReason

    if isinstance(opportunity, OpportunityScore):
        score_id, signal_id, strategy_id, symbol, as_of = (
            opportunity.score_id, opportunity.signal_id, opportunity.strategy_id, opportunity.symbol, opportunity.as_of,
        )
        scoring_schema_version = opportunity.scoring_schema_version
        interface_version = opportunity.refs.interface_version
        data_quality = opportunity.refs.data_quality
    else:
        score_id, signal_id, strategy_id, symbol, as_of = "", "", "S0", "", 0
        scoring_schema_version = "0.0.0"
        interface_version = "0.0.0"
        data_quality = None

    decision_id = f"{strategy_id}|{symbol}|{as_of}"
    refs = RiskRefs(
        scoring_schema_version=scoring_schema_version, interface_version=interface_version,
        account_equity=None, data_quality=data_quality,
    )
    return RiskDecision(
        risk_schema_version=config.risk_schema_version, risk_engine_version=config.risk_engine_version,
        risk_policy_version=config.risk_policy_version, decision_id=decision_id,
        score_id=score_id, signal_id=signal_id, strategy_id=strategy_id, symbol=symbol,
        timestamp=as_of, as_of=as_of, engine_state=engine_state, decision=Decision.DENY,
        direction=Direction.NONE, applied_rules=(),
        refs=refs, denied_reasons=(DeniedReason(code=reason_code, detail=detail),),
        sizing=None, constraints=None, portfolio_impact=None,
    )
