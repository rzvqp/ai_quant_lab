"""Tests for :mod:`ai_trader.scoring_engine.validator`."""

from __future__ import annotations

from dataclasses import replace

from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.conflict import ConflictResult
from ai_trader.scoring_engine import assembler
from ai_trader.scoring_engine.pipeline import score_signal_stage1
from ai_trader.scoring_engine.tests.fixtures.fake_strategy_manager import make_signal
from ai_trader.scoring_engine.types import OpportunityScore, Recommendation
from ai_trader.scoring_engine.validator import score_to_dict, validate_score
from ai_trader.signal_engine.types import Direction

CONFIG = ScoringConfig()


def _score(**generate_kwargs: object) -> OpportunityScore:
    defaults: dict[str, object] = {
        "present": True, "direction": "LONG", "entry": 100.0, "stop": 99.0, "target": 102.0,
        "strength": 0.8, "required_confirmations_met": True,
    }
    defaults.update(generate_kwargs)
    signal = make_signal(generate_signal_response=defaults)
    partial = score_signal_stage1(signal, None, {}, CONFIG)
    return assembler.assemble_score(partial, ConflictResult(0.0, ()), CONFIG)


class TestValidateScoreHappyPath:
    def test_a_freshly_assembled_score_is_valid(self) -> None:
        result = validate_score(_score())
        assert result.valid is True
        assert result.reasons == ()

    def test_a_skipped_score_is_valid(self) -> None:
        signal = make_signal(detect_response={"setup_forming": False})
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        score = assembler.assemble_skipped_score(partial, CONFIG)
        assert validate_score(score).valid is True


class TestDirectionStateConsistency:
    def test_non_actionable_with_nonzero_direction_is_invalid(self) -> None:
        signal = make_signal(detect_response={"setup_forming": False})
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        score = assembler.assemble_skipped_score(partial, CONFIG)
        broken = replace(score, direction=Direction.LONG)
        result = validate_score(broken)
        assert result.valid is False
        assert any("direction=NONE" in r for r in result.reasons)

    def test_non_actionable_with_wrong_recommendation_is_invalid(self) -> None:
        signal = make_signal(detect_response={"setup_forming": False})
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        score = assembler.assemble_skipped_score(partial, CONFIG)
        broken = replace(score, recommendation=Recommendation.STRONG_OPPORTUNITY)
        result = validate_score(broken)
        assert result.valid is False


class TestComponentRange:
    def test_out_of_range_component_is_invalid(self) -> None:
        score = _score()
        broken = replace(score, component_scores=replace(score.component_scores, signal_strength=1.5))
        result = validate_score(broken)
        assert result.valid is False
        assert any("signal_strength" in r for r in result.reasons)

    def test_negative_component_is_invalid(self) -> None:
        score = _score()
        broken = replace(score, component_scores=replace(score.component_scores, data_quality=-0.1))
        result = validate_score(broken)
        assert result.valid is False


class TestTotalScoreRange:
    def test_out_of_range_total_is_invalid(self) -> None:
        score = _score()
        broken = replace(score, total_score=150)
        result = validate_score(broken)
        assert result.valid is False


class TestRankAndReasonCodes:
    def test_rank_below_one_is_invalid(self) -> None:
        score = _score()
        broken = replace(score, rank=0)
        result = validate_score(broken)
        assert result.valid is False

    def test_empty_reason_codes_is_invalid(self) -> None:
        score = _score()
        broken = replace(score, reason_codes=())
        result = validate_score(broken)
        assert result.valid is False


class TestSchemaIntegration:
    def test_schema_violation_is_caught(self) -> None:
        score = _score()
        broken = replace(score, total_score=999)
        result = validate_score(broken)
        assert result.valid is False
        assert result.reasons != ()


class TestScoreToDict:
    def test_has_correct_top_level_keys(self) -> None:
        data = score_to_dict(_score())
        for key in (
            "scoring_schema_version", "score_id", "signal_id", "strategy_id", "symbol", "state",
            "direction", "total_score", "component_scores", "confidence", "quality",
            "recommendation", "rank", "reason_codes", "refs",
        ):
            assert key in data

    def test_optional_fields_omitted_when_none(self) -> None:
        signal = make_signal(detect_response={"setup_forming": False})
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        score = assembler.assemble_skipped_score(partial, CONFIG)
        data = score_to_dict(score)
        assert "base_quality" not in data
        assert "penalty_factor" not in data
        assert "trade_context" not in data

    def test_trade_context_included_when_present(self) -> None:
        data = score_to_dict(_score())
        assert "trade_context" in data
        assert data["trade_context"]["entry"] == 100.0
