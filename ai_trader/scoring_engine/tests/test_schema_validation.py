"""Tests for :mod:`ai_trader.scoring_engine.schema_validation`."""

from __future__ import annotations

from typing import Any

from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.engine import ScoringEngine
from ai_trader.scoring_engine.schema_validation import validate_score_dict
from ai_trader.scoring_engine.validator import score_to_dict
from ai_trader.scoring_engine.tests.fixtures.fake_strategy_manager import make_signal


def _valid_score_dict() -> dict[str, Any]:
    engine = ScoringEngine(ScoringConfig())
    engine.configure(manager=None)
    signal = make_signal(generate_signal_response={
        "present": True, "direction": "LONG", "entry": 100.0, "stop": 99.0, "target": 102.0,
        "strength": 0.8, "confidence": "HIGH", "required_confirmations_met": True, "regime": "TREND_UP",
    })
    score = engine.score_signal(signal)
    return score_to_dict(score)


class TestValidateScoreDict:
    def test_valid_score_produces_no_errors(self) -> None:
        assert validate_score_dict(_valid_score_dict()) == []

    def test_missing_required_key_is_an_error(self) -> None:
        data = _valid_score_dict()
        del data["state"]
        assert validate_score_dict(data) != []

    def test_wrong_type_is_an_error(self) -> None:
        data = _valid_score_dict()
        data["total_score"] = "not a number"
        assert validate_score_dict(data) != []

    def test_unknown_enum_value_is_an_error(self) -> None:
        data = _valid_score_dict()
        data["recommendation"] = "NOT_A_REAL_RECOMMENDATION"
        assert validate_score_dict(data) != []

    def test_out_of_range_total_score_is_an_error(self) -> None:
        data = _valid_score_dict()
        data["total_score"] = 150
        assert validate_score_dict(data) != []

    def test_out_of_range_component_score_is_an_error(self) -> None:
        data = _valid_score_dict()
        data["component_scores"]["signal_strength"] = 1.5
        assert validate_score_dict(data) != []

    def test_empty_reason_codes_is_an_error(self) -> None:
        data = _valid_score_dict()
        data["reason_codes"] = []
        assert validate_score_dict(data) != []

    def test_non_actionable_state_with_wrong_recommendation_is_an_error(self) -> None:
        data = _valid_score_dict()
        data["state"] = "NEED_CONTEXT"
        data["direction"] = "NONE"
        data["recommendation"] = "STRONG_OPPORTUNITY"
        assert validate_score_dict(data) != []

    def test_cached_validator_is_reused_across_calls(self) -> None:
        data = _valid_score_dict()
        for _ in range(5):
            assert validate_score_dict(data) == []
