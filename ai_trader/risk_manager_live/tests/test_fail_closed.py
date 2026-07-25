"""CEO-required controls: incomplete data, inability to calculate risk -- every gap here must DENY,
never approve (fail-closed, CEO rule 11)."""

from __future__ import annotations

from ai_trader.risk_manager_live.engine import evaluate_trade_proposal
from ai_trader.risk_manager_live.reason_codes import (
    PROPOSAL_DATA_INCOMPLETE,
    RISK_NOT_CALCULABLE,
    STOP_WRONG_SIDE_OF_ENTRY,
)
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
    """Since the Decision Logic Audit #2 fix, `TradeProposal.__post_init__` itself now rejects
    entry==stop for either direction (a zero-distance stop is never on the STRICTLY correct side) --
    so this state can no longer arise through normal construction at all. `object.__setattr__` forces
    it onto an otherwise-valid, already-constructed proposal purely to prove `evaluate_trade_proposal`'s
    OWN `RISK_CALCULABLE` gate still independently denies it -- defense in depth, not a redundant test."""
    proposal = make_proposal(entry=2000.0, stop=1990.0)
    object.__setattr__(proposal, "stop", 2000.0)
    decision = evaluate_trade_proposal(
        proposal, make_account(), make_portfolio(), make_instrument(), make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert RISK_NOT_CALCULABLE in decision.reason_codes


def test_stop_on_wrong_side_of_entry_is_denied_by_the_risk_gate_too() -> None:
    """Decision Logic Audit #2, layer 3 (the risk gate's own independent check) -- construction
    (`TradeProposal.__post_init__`) already rejects this; `object.__setattr__` forces the state onto an
    otherwise-valid instance to prove `evaluate_trade_proposal` denies it too, not just relies on the
    type's own constructor. Never corrected to the "right" side -- denied, with its own reason code."""
    proposal = make_proposal(entry=2000.0, stop=1990.0)  # LONG, correctly sided at construction
    object.__setattr__(proposal, "stop", 2010.0)  # now on the WRONG side for a LONG
    decision = evaluate_trade_proposal(
        proposal, make_account(), make_portfolio(), make_instrument(), make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert STOP_WRONG_SIDE_OF_ENTRY in decision.reason_codes
    assert decision.calculated_volume is None


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
    # See test_zero_stop_distance_is_not_calculable: entry==stop can no longer be constructed
    # normally since the Decision Logic Audit #2 fix, so it's forced post-construction.
    proposal = make_proposal(entry=2000.0, stop=1990.0)
    object.__setattr__(proposal, "stop", 2000.0)
    decision = evaluate_trade_proposal(
        proposal, make_account(), make_portfolio(), make_instrument(), make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert decision.calculated_volume is None
    assert decision.monetary_risk is None
    assert decision.margin_estimate is None
