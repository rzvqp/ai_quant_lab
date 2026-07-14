"""Tests for :mod:`ai_trader.signal_engine.schema_validation`."""

from __future__ import annotations

from typing import Any

from ai_trader.signal_engine.schema_validation import (
    validate_explanation_dict,
    validate_signal_dict,
)
from ai_trader.signal_engine.tests.fixtures.fake_strategy import make_fake_handle, make_context
from ai_trader.signal_engine import assembler, pipeline


def _valid_signal_dict() -> dict[str, Any]:
    from ai_trader.signal_engine.config import EngineConfig
    from ai_trader.signal_engine.validator import signal_to_dict

    handle, _ = make_fake_handle()
    context = make_context()
    outcome = pipeline.run_pipeline(context, handle, trader_state=None)
    signal = assembler.assemble_signal(
        strategy_id=handle.id, contract=handle.contract, outcome=outcome, context=context,
        evaluation_time_ms=1.0, config=EngineConfig(), now_ts=context["meta"]["as_of"],
    )
    return signal_to_dict(signal)


class TestValidateSignalDict:
    def test_valid_signal_produces_no_errors(self) -> None:
        assert validate_signal_dict(_valid_signal_dict()) == []

    def test_missing_required_key_is_an_error(self) -> None:
        data = _valid_signal_dict()
        del data["state"]
        errors = validate_signal_dict(data)
        assert errors != []

    def test_wrong_type_is_an_error(self) -> None:
        data = _valid_signal_dict()
        data["signal_strength"] = "not a number"
        errors = validate_signal_dict(data)
        assert errors != []

    def test_unknown_enum_value_is_an_error(self) -> None:
        data = _valid_signal_dict()
        data["state"] = "NOT_A_REAL_STATE"
        errors = validate_signal_dict(data)
        assert errors != []


class TestValidateExplanationDict:
    def test_valid_explanation_produces_no_errors(self) -> None:
        data = _valid_signal_dict()
        assert validate_explanation_dict(data["explanation"]) == []

    def test_missing_required_key_is_an_error(self) -> None:
        data = _valid_signal_dict()
        expl = dict(data["explanation"])
        del expl["state"]
        errors = validate_explanation_dict(expl)
        assert errors != []

    def test_cached_validators_are_reused_across_calls(self) -> None:
        """``_signal_validator``/``_explanation_validator`` are ``lru_cache``d -- calling the public
        functions repeatedly must not error or recompile, and must remain correct."""
        data = _valid_signal_dict()
        for _ in range(5):
            assert validate_signal_dict(data) == []
            assert validate_explanation_dict(data["explanation"]) == []
