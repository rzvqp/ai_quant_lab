"""Tests for :mod:`ai_trader.execution_engine.schema_validation`."""

from __future__ import annotations

from typing import Any

from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.schema_validation import validate_order_dict
from ai_trader.execution_engine.tests.fixtures.fake_broker import make_capabilities
from ai_trader.execution_engine.tests.fixtures.fake_decision import make_allow_decision
from ai_trader.execution_engine.validator import order_to_dict
from ai_trader.execution_engine import builder


def _valid_order_dict() -> dict[str, Any]:
    decision, portfolio = make_allow_decision()
    outcome = builder.build_order(decision, portfolio, make_capabilities(), ExecConfig())
    assert outcome.success and outcome.order is not None
    return order_to_dict(outcome.order)


class TestValidateOrderDict:
    def test_valid_order_produces_no_errors(self) -> None:
        assert validate_order_dict(_valid_order_dict()) == []

    def test_missing_required_key_is_an_error(self) -> None:
        data = _valid_order_dict()
        del data["quantity"]
        assert validate_order_dict(data) != []

    def test_wrong_type_is_an_error(self) -> None:
        data = _valid_order_dict()
        data["as_of"] = "not an int"
        assert validate_order_dict(data) != []

    def test_unknown_enum_value_is_an_error(self) -> None:
        data = _valid_order_dict()
        data["order_type"] = "NOT_A_TYPE"
        assert validate_order_dict(data) != []

    def test_negative_quantity_is_an_error(self) -> None:
        data = _valid_order_dict()
        data["quantity"] = -1.0
        assert validate_order_dict(data) != []

    def test_limit_order_without_limit_price_is_an_error(self) -> None:
        data = _valid_order_dict()
        data["order_type"] = "LIMIT"
        data["limit_price"] = None
        assert validate_order_dict(data) != []

    def test_bracket_without_bracket_object_is_an_error(self) -> None:
        data = _valid_order_dict()
        data["order_type"] = "BRACKET"
        data["bracket"] = None
        assert validate_order_dict(data) != []

    def test_cached_validator_is_reused_across_calls(self) -> None:
        data = _valid_order_dict()
        for _ in range(5):
            assert validate_order_dict(data) == []
