"""Tests for :mod:`ai_trader.signal_engine.validator`."""

from __future__ import annotations

from dataclasses import replace

from ai_trader.signal_engine.assembler import assemble_signal
from ai_trader.signal_engine.config import EngineConfig
from ai_trader.signal_engine.pipeline import PipelineOutcome
from ai_trader.signal_engine.types import Direction, QualityFlag, SignalState, StrategySignal
from ai_trader.signal_engine.tests.fixtures.fake_strategy import make_context, make_fake_handle
from ai_trader.signal_engine.validator import explanation_to_dict, signal_to_dict, validate_signal


def _signal(state: SignalState = SignalState.NO_SIGNAL, direction: Direction = Direction.NONE) -> StrategySignal:
    handle, _ = make_fake_handle()
    context = make_context()
    outcome = PipelineOutcome(state=state, direction=direction)
    return assemble_signal(handle.id, handle.contract, outcome, context, 1.0, EngineConfig(), now_ts=context["meta"]["as_of"])


class TestValidateSignalHappyPath:
    def test_a_freshly_assembled_no_signal_is_valid(self) -> None:
        result = validate_signal(_signal())
        assert result.valid is True
        assert result.quality_flags == (QualityFlag.OK,)

    def test_a_freshly_assembled_buy_is_valid(self) -> None:
        result = validate_signal(_signal(state=SignalState.BUY, direction=Direction.LONG))
        assert result.valid is True

    def test_a_freshly_assembled_sell_is_valid(self) -> None:
        result = validate_signal(_signal(state=SignalState.SELL, direction=Direction.SHORT))
        assert result.valid is True


class TestDirectionStateConsistency:
    def test_buy_with_wrong_direction_is_invalid(self) -> None:
        result = validate_signal(_signal(state=SignalState.BUY, direction=Direction.SHORT))
        assert result.valid is False
        assert QualityFlag.INVALID_DIRECTION in result.quality_flags

    def test_sell_with_wrong_direction_is_invalid(self) -> None:
        result = validate_signal(_signal(state=SignalState.SELL, direction=Direction.LONG))
        assert result.valid is False
        assert QualityFlag.INVALID_DIRECTION in result.quality_flags

    def test_non_actionable_state_with_nonzero_direction_is_invalid(self) -> None:
        result = validate_signal(_signal(state=SignalState.NO_SIGNAL, direction=Direction.LONG))
        assert result.valid is False
        assert QualityFlag.INVALID_DIRECTION in result.quality_flags

    def test_blocked_with_direction_none_is_valid_on_this_rule(self) -> None:
        result = validate_signal(_signal(state=SignalState.BLOCKED, direction=Direction.NONE))
        assert QualityFlag.INVALID_DIRECTION not in result.quality_flags


class TestUnknownStrategyId:
    def test_known_id_passes(self) -> None:
        sig = _signal()
        result = validate_signal(sig, known_strategy_ids=frozenset({sig.strategy_id}))
        assert result.valid is True

    def test_unknown_id_flags_unknown_strategy(self) -> None:
        sig = _signal()
        result = validate_signal(sig, known_strategy_ids=frozenset({"SOME_OTHER_ID"}))
        assert result.valid is False
        assert QualityFlag.UNKNOWN_STRATEGY in result.quality_flags

    def test_none_known_ids_skips_the_check_entirely(self) -> None:
        sig = _signal()
        result = validate_signal(sig, known_strategy_ids=None)
        assert QualityFlag.UNKNOWN_STRATEGY not in result.quality_flags


class TestSignalStrengthRange:
    def test_out_of_range_strength_is_invalid(self) -> None:
        sig = replace(_signal(), signal_strength=1.5)
        result = validate_signal(sig)
        assert result.valid is False
        assert QualityFlag.INVALID_CONFIDENCE in result.quality_flags

    def test_negative_strength_is_invalid(self) -> None:
        sig = replace(_signal(), signal_strength=-0.1)
        result = validate_signal(sig)
        assert result.valid is False

    def test_boundary_values_are_valid(self) -> None:
        assert validate_signal(replace(_signal(), signal_strength=0.0)).valid is True
        assert validate_signal(replace(_signal(), signal_strength=1.0)).valid is True


class TestContextRefVersionFields:
    def test_missing_context_schema_version_is_invalid(self) -> None:
        sig = _signal()
        broken_ref = replace(sig.context_ref, context_schema_version="")
        sig = replace(sig, context_ref=broken_ref)
        result = validate_signal(sig)
        assert result.valid is False
        assert QualityFlag.MISSING_CONTEXT in result.quality_flags


class TestSchemaValidationIntegration:
    def test_schema_violating_signal_reports_schema_mismatch(self) -> None:
        sig = replace(_signal(), signal_strength=99.0)
        result = validate_signal(sig)
        assert QualityFlag.SCHEMA_MISMATCH in result.quality_flags or QualityFlag.INVALID_CONFIDENCE in result.quality_flags

    def test_reasons_are_non_empty_when_invalid(self) -> None:
        sig = replace(_signal(), signal_strength=1.5)
        result = validate_signal(sig)
        assert result.reasons != ()

    def test_explanation_only_schema_violation_is_still_caught(self) -> None:
        """SIGNAL_SCHEMA.json only requires ``explanation`` to be an object (it does NOT recursively
        validate it against SIGNAL_EXPLANATION_SCHEMA.json) -- a signal can be top-level valid while
        its nested explanation independently violates SIGNAL_EXPLANATION_SCHEMA.json's own
        ``strategy_ref.id`` pattern. Both checks run; this exercises the explanation-only path."""
        sig = _signal()
        broken_ref = replace(sig.explanation.strategy_ref, id="NOT_A_VALID_ID")
        sig = replace(sig, explanation=replace(sig.explanation, strategy_ref=broken_ref))
        result = validate_signal(sig)
        assert result.valid is False
        assert QualityFlag.SCHEMA_MISMATCH in result.quality_flags

    def test_as_of_none_is_flagged_missing_timestamp(self) -> None:
        sig = replace(_signal(), as_of=None)  # type: ignore[arg-type]
        result = validate_signal(sig)
        assert result.valid is False
        assert QualityFlag.MISSING_TIMESTAMP in result.quality_flags

    def test_as_of_zero_sentinel_is_flagged_missing_timestamp(self) -> None:
        """``StrategySignal.as_of`` is typed plain ``int`` -- the real "missing" representation
        (``assembler.assemble_signal``'s own ``meta.get("as_of", 0)`` fallback) is the sentinel 0,
        not None, which this check must actually catch."""
        sig = replace(_signal(), as_of=0)
        result = validate_signal(sig)
        assert result.valid is False
        assert QualityFlag.MISSING_TIMESTAMP in result.quality_flags


class TestSerializationRoundTrip:
    def test_signal_to_dict_has_correct_top_level_keys(self) -> None:
        data = signal_to_dict(_signal())
        for key in (
            "signal_schema_version", "signal_id", "strategy_id", "state", "direction",
            "signal_strength", "confidence", "mechanism", "context_ref", "explanation",
        ):
            assert key in data

    def test_trade_params_is_null_when_absent(self) -> None:
        data = signal_to_dict(_signal())
        assert data["trade_params"] is None

    def test_explanation_to_dict_has_correct_top_level_keys(self) -> None:
        sig = _signal()
        data = explanation_to_dict(sig.explanation)
        for key in (
            "explanation_schema_version", "strategy_ref", "state", "triggering_mechanism",
            "why_exists", "why_failed", "confirmations", "context_summary",
        ):
            assert key in data
