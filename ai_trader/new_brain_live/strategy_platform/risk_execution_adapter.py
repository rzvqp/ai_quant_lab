"""Risk + Execution adapter (AI Trader New Brain Architecture mandate, sections 17-18). A thin,
additive translation from `TradeHypothesis`/`EVDecision` into the EXISTING, already-ratified Risk Engine
(`risk_manager_live.engine.evaluate_trade_proposal`) and Execution Adapter
(`new_brain_bridge.execution_shadow.attempt_shadow_execution` + `BrokerOrderSubmissionGate`) -- no risk
policy, sizing, or broker-gating logic is reimplemented here. `evaluate_trade_proposal` and
`attempt_shadow_execution` are ALREADY fully generic (neither imports anything `ve_brain`-specific),
so this module's only real job is the field-mapping `TradeHypothesis -> TradeProposal`.

A strategy may propose a stop (`TradeHypothesis.invalidation`); it may NOT override risk policy --
`evaluate_trade_proposal` independently recomputes sizing/limits/guards from `RiskContext`/`RiskConfig`,
never trusting anything the strategy itself calculated."""

from __future__ import annotations

import dataclasses

from ai_trader.mandate2_readiness.broker_gate import BrokerOrderSubmissionGate
from ai_trader.new_brain_bridge.execution_shadow import ShadowExecutionResult, attempt_shadow_execution
from ai_trader.new_brain_live.strategy_platform.ev_engine import TRADE_DECISION, EVDecision
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import PortfolioState, RiskContext
from ai_trader.risk_manager_live.engine import evaluate_trade_proposal
from ai_trader.risk_manager_live.types import AccountState, InstrumentSpecification, LiveRiskDecision, TradeProposal


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class RiskExecutionDeps:
    """Assembled upstream, never fetched here (same discipline `RiskContext` itself already documents)
    -- this module never reaches into MT5, a gateway, or any live source on its own."""

    account: AccountState
    portfolio: PortfolioState
    instrument: InstrumentSpecification
    risk_context: RiskContext
    risk_config: RiskConfig | None = None
    gate: BrokerOrderSubmissionGate = dataclasses.field(default_factory=BrokerOrderSubmissionGate)


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class RiskExecutionOutcome:
    risk_decision: LiveRiskDecision
    shadow_result: ShadowExecutionResult | None  # None when risk itself already denied -- never reached


def _proposal_id(ev_decision: EVDecision) -> str:
    h = ev_decision.hypothesis
    return f"{h.strategy_id}:{h.market_state_identity}"


def evaluate_and_attempt(ev_decision: EVDecision, *, deps: RiskExecutionDeps) -> RiskExecutionOutcome:
    """Only ever called for `decision == TRADE_DECISION` -- a NO_TRADE `EVDecision` never reaches Risk
    at all (`pipeline.py`'s own responsibility, asserted here as a defensive precondition, not silently
    tolerated)."""
    if ev_decision.decision != TRADE_DECISION:
        raise ValueError(
            f"evaluate_and_attempt: only TRADE_DECISION may reach Risk, got {ev_decision.decision!r}"
        )
    h = ev_decision.hypothesis
    proposal = TradeProposal(
        proposal_id=_proposal_id(ev_decision), correlation_id=h.market_state_identity,
        strategy_id=h.strategy_id, symbol=h.instrument, direction=h.direction, entry=h.intended_entry,
        stop=h.invalidation, target=None, as_of=h.signal_timestamp,
    )
    risk_decision = evaluate_trade_proposal(
        proposal, deps.account, deps.portfolio, deps.instrument, deps.risk_context, deps.risk_config,
    )
    if not risk_decision.approved:
        return RiskExecutionOutcome(risk_decision=risk_decision, shadow_result=None)

    shadow_result = attempt_shadow_execution(risk_decision, gate=deps.gate)
    return RiskExecutionOutcome(risk_decision=risk_decision, shadow_result=shadow_result)
