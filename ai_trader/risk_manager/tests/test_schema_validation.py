"""Tests for :mod:`ai_trader.risk_manager.schema_validation`."""

from __future__ import annotations

from typing import Any

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import RiskManager
from ai_trader.risk_manager.schema_validation import validate_decision_dict
from ai_trader.risk_manager.tests.fixtures.fake_opportunity import (
    make_below_floor_opportunity,
    make_opportunity,
    make_portfolio,
    make_risk_context,
)
from ai_trader.risk_manager.validator import decision_to_dict


def _valid_allow_dict() -> dict[str, Any]:
    rm = RiskManager(RiskConfig())
    portfolio = make_portfolio()
    rm.configure(portfolio=portfolio)
    opp = make_opportunity()
    context = make_risk_context()
    rm._config.filters.reference_spread["XAUUSD"] = 0.1
    rm._config.filters.liquidity_floor["XAUUSD"] = 100.0
    decision = rm.allow_trade(opp, context, portfolio)
    assert decision.decision.value == "ALLOW"
    return decision_to_dict(decision)


def _valid_deny_dict() -> dict[str, Any]:
    rm = RiskManager(RiskConfig())
    portfolio = make_portfolio()
    rm.configure(portfolio=portfolio)
    opp = make_below_floor_opportunity()  # deterministic BELOW_FLOOR/SCORE_TOO_LOW DENY
    context = make_risk_context()
    decision = rm.allow_trade(opp, context, portfolio)
    assert decision.decision.value == "DENY"
    return decision_to_dict(decision)


class TestValidateDecisionDict:
    def test_valid_allow_produces_no_errors(self) -> None:
        assert validate_decision_dict(_valid_allow_dict()) == []

    def test_valid_deny_produces_no_errors(self) -> None:
        assert validate_decision_dict(_valid_deny_dict()) == []

    def test_missing_required_key_is_an_error(self) -> None:
        data = _valid_allow_dict()
        del data["decision"]
        assert validate_decision_dict(data) != []

    def test_wrong_type_is_an_error(self) -> None:
        data = _valid_allow_dict()
        data["as_of"] = "not an int"
        assert validate_decision_dict(data) != []

    def test_unknown_enum_value_is_an_error(self) -> None:
        data = _valid_allow_dict()
        data["decision"] = "MAYBE"
        assert validate_decision_dict(data) != []

    def test_deny_with_sizing_is_an_error(self) -> None:
        data = _valid_deny_dict()
        allow_sizing = _valid_allow_dict()["sizing"]
        data["sizing"] = allow_sizing
        assert validate_decision_dict(data) != []

    def test_allow_with_empty_applied_rules_is_still_valid_shape(self) -> None:
        # applied_rules is required but has no minItems constraint -- an empty list is schema-valid.
        data = _valid_allow_dict()
        data["applied_rules"] = []
        assert validate_decision_dict(data) == []

    def test_deny_without_reasons_is_an_error(self) -> None:
        data = _valid_deny_dict()
        data["denied_reasons"] = []
        assert validate_decision_dict(data) != []

    def test_cached_validator_is_reused_across_calls(self) -> None:
        data = _valid_allow_dict()
        for _ in range(5):
            assert validate_decision_dict(data) == []
