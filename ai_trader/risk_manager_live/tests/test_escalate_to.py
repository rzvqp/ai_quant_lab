"""Proof that `guards.py`'s `GuardResult.escalate_to` -- previously computed and silently discarded by
the loop in `evaluate_trade_proposal` (Risk Audit #1) -- now reaches `LiveRiskDecision.escalate_to`."""

from __future__ import annotations

from ai_trader.risk_manager.types import EngineState
from ai_trader.risk_manager_live.engine import evaluate_trade_proposal
from ai_trader.risk_manager_live.tests._fixtures import (
    make_account,
    make_config,
    make_instrument,
    make_portfolio,
    make_proposal,
    make_risk_context,
)


def test_daily_loss_breach_surfaces_escalate_to() -> None:
    portfolio = make_portfolio(realized_pnl_pct_daily=-0.10)
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(), portfolio, make_instrument(), make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert decision.escalate_to is EngineState.SUSPENDED


def test_drawdown_breach_surfaces_escalate_to() -> None:
    portfolio = make_portfolio(equity=80_000.0, equity_high_water_mark=200_000.0)
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(), portfolio, make_instrument(), make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert decision.escalate_to is EngineState.SUSPENDED


def test_non_escalating_denial_leaves_escalate_to_none() -> None:
    """A denial with no `escalate_to` signal (e.g. a position-count limit) must not be misreported as
    an escalation -- `guards.py` only ever escalates on loss/drawdown, never on portfolio limits."""
    portfolio = make_portfolio(consecutive_losses=5)
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(), portfolio, make_instrument(), make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert decision.escalate_to is None


def test_approved_decision_has_no_escalation() -> None:
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(), make_portfolio(), make_instrument(), make_risk_context(), make_config(),
    )
    assert decision.approved is True
    assert decision.escalate_to is None
