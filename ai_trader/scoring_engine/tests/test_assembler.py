"""Tests for :mod:`ai_trader.scoring_engine.assembler`."""

from __future__ import annotations

from ai_trader.scoring_engine import assembler
from ai_trader.scoring_engine.conflict import ConflictResult
from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.pipeline import score_signal_stage1
from ai_trader.scoring_engine.tests.fixtures.fake_strategy_manager import make_signal
from ai_trader.scoring_engine.types import Quality, ReasonCode, Recommendation, ScoreConfidence
from ai_trader.signal_engine.types import Direction, SignalState

CONFIG = ScoringConfig()


class TestAssembleInvalidScore:
    def test_non_signal_object_uses_placeholders(self) -> None:
        score = assembler.assemble_invalid_score(object(), CONFIG)
        assert score.strategy_id == "S0"
        assert score.symbol == ""
        assert score.as_of == 0
        assert score.total_score == 0
        assert score.recommendation is Recommendation.INVALID
        assert score.direction is Direction.NONE
        assert score.reason_codes == (ReasonCode(code="SIGNAL_INVALID"),)
        assert score.component_scores.signal_strength == 0.0
        assert score.base_quality is None
        assert score.penalty_factor is None

    def test_real_signal_carries_its_own_identity(self) -> None:
        signal = make_signal(strategy_id="S7", generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True,
        })
        score = assembler.assemble_invalid_score(signal, CONFIG)
        assert score.strategy_id == "S7"
        assert score.symbol == signal.symbol
        assert score.as_of == signal.as_of
        assert score.recommendation is Recommendation.INVALID


class TestAssembleSkippedScore:
    def test_forces_total_zero_and_skip(self) -> None:
        signal = make_signal(detect_response={"setup_forming": False})
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        score = assembler.assemble_skipped_score(partial, CONFIG)
        assert score.total_score == 0
        assert score.recommendation is Recommendation.SKIP
        assert score.direction is Direction.NONE
        assert score.confidence is ScoreConfidence.NONE
        assert score.quality is Quality.POOR
        assert score.base_quality is None
        assert score.penalty_factor is None

    def test_reason_codes_mirror_the_state(self) -> None:
        signal = make_signal(detect_response={"setup_forming": False})
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        score = assembler.assemble_skipped_score(partial, CONFIG)
        codes = [r.code for r in score.reason_codes]
        assert "NOT_ACTIONABLE" in codes
        assert "NO_SIGNAL" in codes

    def test_trade_context_is_none_for_skipped(self) -> None:
        signal = make_signal(detect_response={"setup_forming": False})
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        score = assembler.assemble_skipped_score(partial, CONFIG)
        assert score.trade_context is None


class TestAssembleScore:
    def test_normal_path_populates_base_quality_and_penalty_factor(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "entry": 100.0, "stop": 99.0, "target": 102.0,
            "strength": 0.8, "required_confirmations_met": True,
        })
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        score = assembler.assemble_score(partial, ConflictResult(0.0, ()), CONFIG)
        assert score.base_quality is not None
        assert score.penalty_factor is not None
        assert score.component_scores.conflict_penalty == 0.0

    def test_conflict_penalty_is_folded_into_component_scores(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True,
        })
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        score = assembler.assemble_score(partial, ConflictResult(0.5, ()), CONFIG)
        assert score.component_scores.conflict_penalty == 0.5

    def test_empty_reason_codes_falls_back_to_scored_clean(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "entry": 100.0, "stop": 99.0, "target": 102.0,
            "strength": 0.8, "required_confirmations_met": True, "regime": None,
        }, context_overrides={"data_quality": {"overall": "OK", "by_timeframe": {}}})
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        score = assembler.assemble_score(partial, ConflictResult(0.0, ()), CONFIG)
        assert len(score.reason_codes) >= 1  # schema requires non-empty; never silently empty

    def test_extra_reason_codes_are_appended(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True,
        })
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        extra = (ReasonCode(code="NO_BATCH_CONTEXT", component="conflict_penalty"),)
        score = assembler.assemble_score(partial, ConflictResult(0.0, ()), CONFIG, extra)
        assert any(r.code == "NO_BATCH_CONTEXT" for r in score.reason_codes)

    def test_trade_context_carries_through_from_trade_params(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "entry": 100.0, "stop": 99.0, "target": 102.0,
            "risk_R": 1.0, "required_confirmations_met": True,
        })
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        score = assembler.assemble_score(partial, ConflictResult(0.0, ()), CONFIG)
        assert score.trade_context is not None
        assert score.trade_context.entry == 100.0
        assert score.trade_context.risk_R == 1.0

    def test_direction_and_state_pass_through_from_signal(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "SHORT", "entry": 100.0, "stop": 101.0, "target": 98.0,
            "required_confirmations_met": True,
        })
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        score = assembler.assemble_score(partial, ConflictResult(0.0, ()), CONFIG)
        assert score.state is SignalState.SELL
        assert score.direction is Direction.SHORT

    def test_rank_is_a_placeholder_pending_ranker(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True,
        })
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        score = assembler.assemble_score(partial, ConflictResult(0.0, ()), CONFIG)
        assert score.rank == 1
