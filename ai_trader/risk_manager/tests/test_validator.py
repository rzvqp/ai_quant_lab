"""Tests for :mod:`ai_trader.risk_manager.validator`."""

from __future__ import annotations

from dataclasses import replace

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import RiskManager
from ai_trader.risk_manager.tests.fixtures.fake_opportunity import (
    make_below_floor_opportunity,
    make_opportunity,
    make_portfolio,
    make_risk_context,
)
from ai_trader.risk_manager.types import EngineState, RiskDecision, Sizing, SizingMethod
from ai_trader.risk_manager.validator import decision_to_dict, validate_decision
from ai_trader.signal_engine.types import Direction


def _allow_decision() -> RiskDecision:
    rm = RiskManager(RiskConfig())
    portfolio = make_portfolio()
    rm.configure(portfolio=portfolio)
    rm._config.filters.reference_spread["XAUUSD"] = 0.1
    rm._config.filters.liquidity_floor["XAUUSD"] = 100.0
    opp = make_opportunity(strength=0.95)
    decision = rm.allow_trade(opp, make_risk_context(), portfolio)
    assert decision.decision.value == "ALLOW"
    return decision


def _deny_decision() -> RiskDecision:
    """Denied specifically via RECOMMENDATION_FLOOR -- filters are configured (matching
    ``_allow_decision``) so this deterministically exercises the floor gate, not an incidental
    unconfigured-filter DENY."""
    rm = RiskManager(RiskConfig())
    portfolio = make_portfolio()
    rm.configure(portfolio=portfolio)
    rm._config.filters.reference_spread["XAUUSD"] = 0.1
    rm._config.filters.liquidity_floor["XAUUSD"] = 100.0
    opp = make_below_floor_opportunity()
    decision = rm.allow_trade(opp, make_risk_context(), portfolio)
    assert decision.decision.value == "DENY"
    assert decision.denied_reasons[0].code in ("BELOW_FLOOR", "SCORE_TOO_LOW")
    return decision


class TestValidateDecisionHappyPath:
    def test_allow_is_valid(self) -> None:
        result = validate_decision(_allow_decision())
        assert result.valid is True

    def test_deny_is_valid(self) -> None:
        result = validate_decision(_deny_decision())
        assert result.valid is True


class TestDenySemantics:
    def test_deny_with_no_reasons_is_invalid(self) -> None:
        broken = replace(_deny_decision(), denied_reasons=())
        result = validate_decision(broken)
        assert result.valid is False

    def test_deny_with_sizing_is_invalid(self) -> None:
        sizing = Sizing(method=SizingMethod.FIXED_FRACTIONAL, risk_per_trade_pct=0.005, risk_R=1.0, size_units=1.0, min_size=0.1, max_size=10.0)
        broken = replace(_deny_decision(), sizing=sizing)
        result = validate_decision(broken)
        assert result.valid is False


class TestAllowSemantics:
    def test_allow_without_sizing_is_invalid(self) -> None:
        broken = replace(_allow_decision(), sizing=None)
        result = validate_decision(broken)
        assert result.valid is False

    def test_allow_without_constraints_is_invalid(self) -> None:
        broken = replace(_allow_decision(), constraints=None)
        result = validate_decision(broken)
        assert result.valid is False

    def test_allow_with_size_below_min_is_invalid(self) -> None:
        decision = _allow_decision()
        assert decision.sizing is not None
        broken_sizing = replace(decision.sizing, size_units=decision.sizing.min_size - 1.0) if decision.sizing.min_size > 0 else replace(decision.sizing, min_size=decision.sizing.size_units + 1.0)
        broken = replace(decision, sizing=broken_sizing)
        result = validate_decision(broken)
        assert result.valid is False

    def test_allow_with_direction_none_is_invalid(self) -> None:
        broken = replace(_allow_decision(), direction=Direction.NONE)
        result = validate_decision(broken)
        assert result.valid is False

    def test_allow_with_non_ready_state_is_invalid(self) -> None:
        broken = replace(_allow_decision(), engine_state=EngineState.SUSPENDED)
        result = validate_decision(broken)
        assert result.valid is False

    def test_allow_without_stop_is_invalid(self) -> None:
        decision = _allow_decision()
        assert decision.constraints is not None
        broken_constraints = replace(decision.constraints, stop=None)
        broken = replace(decision, constraints=broken_constraints)
        result = validate_decision(broken)
        assert result.valid is False


class TestSchemaIntegration:
    def test_schema_violation_is_caught(self) -> None:
        broken = replace(_allow_decision(), timestamp="not an int")  # type: ignore[arg-type]
        result = validate_decision(broken)
        assert result.valid is False
        assert result.reasons != ()


class TestDecisionToDict:
    def test_has_correct_top_level_keys(self) -> None:
        data = decision_to_dict(_allow_decision())
        for key in (
            "risk_schema_version", "decision_id", "score_id", "strategy_id", "symbol", "decision",
            "engine_state", "direction", "applied_rules", "refs",
        ):
            assert key in data

    def test_deny_sizing_and_constraints_are_null(self) -> None:
        data = decision_to_dict(_deny_decision())
        assert data["sizing"] is None
        assert data["constraints"] is None

    def test_allow_sizing_reflects_computed_size(self) -> None:
        decision = _allow_decision()
        assert decision.sizing is not None
        data = decision_to_dict(decision)
        assert data["sizing"]["size_units"] == decision.sizing.size_units
