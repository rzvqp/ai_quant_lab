"""Validation tests for the new Phase 2 types."""

from __future__ import annotations

import pytest

from ai_trader.risk_manager_live.tests._fixtures import make_account, make_instrument, make_proposal
from ai_trader.risk_manager_live.types import CalculationTraceStep, LiveRiskDecision
from ai_trader.signal_engine.types import Direction


def test_proposal_construction_happy_path() -> None:
    p = make_proposal()
    assert p.symbol == "XAUUSD"
    assert p.direction is Direction.LONG


def test_proposal_rejects_empty_proposal_id() -> None:
    with pytest.raises(ValueError, match="proposal_id"):
        make_proposal(proposal_id="")


def test_proposal_rejects_empty_correlation_id() -> None:
    with pytest.raises(ValueError, match="correlation_id"):
        make_proposal(correlation_id="")


def test_account_rejects_non_positive_leverage() -> None:
    with pytest.raises(ValueError, match="leverage"):
        make_account(leverage=0.0)


def test_account_rejects_negative_margin_used() -> None:
    with pytest.raises(ValueError, match="margin_used"):
        make_account(margin_used=-1.0)


def test_instrument_rejects_empty_symbol() -> None:
    with pytest.raises(ValueError, match="symbol"):
        make_instrument(symbol="")


def test_live_risk_decision_approved_requires_calculation_trace() -> None:
    with pytest.raises(ValueError, match="calculation_trace"):
        LiveRiskDecision(
            approved=True, reason_codes=(), requested_risk=0.005, approved_risk=0.005,
            calculated_volume=0.1, monetary_risk=10.0, stop_distance=10.0, margin_estimate=5.0,
            warnings=(), calculation_trace=(),
        )


def test_live_risk_decision_denied_requires_reason_codes() -> None:
    with pytest.raises(ValueError, match="reason code"):
        LiveRiskDecision(
            approved=False, reason_codes=(), requested_risk=None, approved_risk=None,
            calculated_volume=None, monetary_risk=None, stop_distance=None, margin_estimate=None,
            warnings=(), calculation_trace=(CalculationTraceStep(stage="X", passed=False),),
        )


def test_live_risk_decision_denied_with_reason_and_trace_is_valid() -> None:
    d = LiveRiskDecision(
        approved=False, reason_codes=("LOSS_DAILY",), requested_risk=None, approved_risk=None,
        calculated_volume=None, monetary_risk=None, stop_distance=None, margin_estimate=None,
        warnings=(), calculation_trace=(CalculationTraceStep(stage="LOSS_DAILY", passed=False),),
    )
    assert d.reason_codes == ("LOSS_DAILY",)
