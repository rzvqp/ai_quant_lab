"""CEO-required controls: incomplete data, inability to calculate risk -- every gap here must DENY,
never approve (fail-closed, CEO rule 11)."""

from __future__ import annotations

from ai_trader.risk_manager_live.engine import evaluate_trade_proposal
from ai_trader.risk_manager_live.reason_codes import PROPOSAL_DATA_INCOMPLETE, RISK_NOT_CALCULABLE
from ai_trader.risk_manager_live.tests._fixtures import (
    make_account,
    make_config,
    make_instrument,
    make_portfolio,
    make_proposal,
    make_risk_context,
)


def test_mismatched_symbol_is_data_incomplete() -> None:
    proposal = make_proposal(symbol="EURUSD")
    decision = evaluate_trade_proposal(
        proposal, make_account(), make_portfolio(), make_instrument(symbol="XAUUSD"),
        make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert PROPOSAL_DATA_INCOMPLETE in decision.reason_codes


def test_zero_stop_distance_is_not_calculable() -> None:
    proposal = make_proposal(entry=2000.0, stop=2000.0)
    decision = evaluate_trade_proposal(
        proposal, make_account(), make_portfolio(), make_instrument(), make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert RISK_NOT_CALCULABLE in decision.reason_codes


def test_zero_equity_is_not_calculable() -> None:
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(equity=0.0), make_portfolio(), make_instrument(),
        make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert RISK_NOT_CALCULABLE in decision.reason_codes


def test_zero_tick_size_is_not_calculable() -> None:
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(), make_portfolio(), make_instrument(tick_size=0.0),
        make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert RISK_NOT_CALCULABLE in decision.reason_codes


def test_zero_lot_step_is_not_calculable() -> None:
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(), make_portfolio(), make_instrument(lot_step=0.0),
        make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert RISK_NOT_CALCULABLE in decision.reason_codes


def test_zero_contract_size_is_not_calculable() -> None:
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(), make_portfolio(), make_instrument(contract_size=0.0),
        make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert RISK_NOT_CALCULABLE in decision.reason_codes


def test_missing_symbol_snapshot_fails_closed_via_data_quality_filter() -> None:
    """No RiskContext entry for the symbol at all -- RiskContext.for_symbol()'s own existing, unmodified
    fail-safe returns SymbolRiskSnapshot(data_quality=INSUFFICIENT), which the reused, frozen
    check_data_quality filter correctly denies."""
    from ai_trader.risk_manager.types import RiskContext

    empty_context = RiskContext(as_of=1_700_000_000)  # no per_symbol data at all
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(), make_portfolio(), make_instrument(), empty_context, make_config(),
    )
    assert decision.approved is False
    assert "DATA_DEGRADED" in decision.reason_codes


def test_denied_decision_never_carries_a_calculated_volume() -> None:
    decision = evaluate_trade_proposal(
        make_proposal(entry=2000.0, stop=2000.0), make_account(), make_portfolio(), make_instrument(),
        make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert decision.calculated_volume is None
    assert decision.monetary_risk is None
    assert decision.margin_estimate is None
