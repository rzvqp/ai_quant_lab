"""Tests for :mod:`ai_trader.signal_engine.assembler`."""

from __future__ import annotations

from ai_trader.signal_engine.assembler import assemble_signal
from ai_trader.signal_engine.config import EngineConfig
from ai_trader.signal_engine.pipeline import PipelineOutcome
from ai_trader.signal_engine.types import ConditionRecord, Direction, QualityFlag, SignalState, TradeParams
from ai_trader.signal_engine.tests.fixtures.fake_strategy import make_context, make_fake_handle
from ai_trader.strategy_manager.contract import ConfidenceLevel, Regime


class TestAssembleSignalWithContract:
    def test_stamps_versions_from_config(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context()
        config = EngineConfig(signal_engine_version="9.9.9", signal_schema_version="8.8.8")
        outcome = PipelineOutcome(state=SignalState.NO_SIGNAL)
        signal = assemble_signal(handle.id, handle.contract, outcome, context, 1.0, config, now_ts=context["meta"]["as_of"])
        assert signal.signal_engine_version == "9.9.9"
        assert signal.signal_schema_version == "8.8.8"

    def test_timestamp_and_as_of_both_use_now_ts_never_wallclock(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context(as_of=555)
        outcome = PipelineOutcome(state=SignalState.NO_SIGNAL)
        signal = assemble_signal(handle.id, handle.contract, outcome, context, 1.0, EngineConfig(), now_ts=555)
        assert signal.timestamp == 555
        assert signal.as_of == 555

    def test_signal_id_is_composed_of_strategy_symbol_as_of(self) -> None:
        handle, _ = make_fake_handle(strategy_id="S3")
        context = make_context(symbol="XAUUSD", as_of=42)
        outcome = PipelineOutcome(state=SignalState.NO_SIGNAL)
        signal = assemble_signal("S3", handle.contract, outcome, context, 1.0, EngineConfig(), now_ts=42)
        assert signal.signal_id == "S3|XAUUSD|42"

    def test_mechanism_and_strategy_version_come_from_contract(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context()
        outcome = PipelineOutcome(state=SignalState.NO_SIGNAL)
        signal = assemble_signal(handle.id, handle.contract, outcome, context, 1.0, EngineConfig(), now_ts=context["meta"]["as_of"])
        assert signal.mechanism == handle.contract.semantics.mechanism
        assert signal.strategy_version == handle.contract.identity.version

    def test_default_quality_flags_is_ok_when_no_extra_flags(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context()
        outcome = PipelineOutcome(state=SignalState.NO_SIGNAL)
        signal = assemble_signal(handle.id, handle.contract, outcome, context, 1.0, EngineConfig(), now_ts=context["meta"]["as_of"])
        assert signal.quality_flags == (QualityFlag.OK,)

    def test_extra_quality_flags_override_ok(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context()
        outcome = PipelineOutcome(state=SignalState.INVALID)
        signal = assemble_signal(
            handle.id, handle.contract, outcome, context, 1.0, EngineConfig(), now_ts=context["meta"]["as_of"],
            extra_quality_flags=(QualityFlag.CORRUPTED_OUTPUT,),
        )
        assert signal.quality_flags == (QualityFlag.CORRUPTED_OUTPUT,)

    def test_invalid_confidence_string_falls_back_to_none(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context()
        outcome = PipelineOutcome(state=SignalState.NO_SIGNAL, confidence="NOT_A_LEVEL")
        signal = assemble_signal(handle.id, handle.contract, outcome, context, 1.0, EngineConfig(), now_ts=context["meta"]["as_of"])
        assert signal.confidence is ConfidenceLevel.NONE

    def test_valid_confidence_string_is_parsed(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context()
        outcome = PipelineOutcome(state=SignalState.NO_SIGNAL, confidence="HIGH")
        signal = assemble_signal(handle.id, handle.contract, outcome, context, 1.0, EngineConfig(), now_ts=context["meta"]["as_of"])
        assert signal.confidence is ConfidenceLevel.HIGH

    def test_invalid_regime_string_falls_back_to_none(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context()
        outcome = PipelineOutcome(state=SignalState.NO_SIGNAL, regime="NOT_A_REGIME")
        signal = assemble_signal(handle.id, handle.contract, outcome, context, 1.0, EngineConfig(), now_ts=context["meta"]["as_of"])
        assert signal.regime is None

    def test_valid_regime_string_is_parsed(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context()
        outcome = PipelineOutcome(state=SignalState.BUY, regime="RANGE")
        signal = assemble_signal(handle.id, handle.contract, outcome, context, 1.0, EngineConfig(), now_ts=context["meta"]["as_of"])
        assert signal.regime is Regime.RANGE

    def test_session_comes_from_context_session_block(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context(session_name="asia")
        outcome = PipelineOutcome(state=SignalState.NO_SIGNAL)
        signal = assemble_signal(handle.id, handle.contract, outcome, context, 1.0, EngineConfig(), now_ts=context["meta"]["as_of"])
        assert signal.session == "asia"

    def test_trade_params_pass_through_from_outcome(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context()
        tp = TradeParams(entry=1.0, stop=0.9, target=1.2, risk_R=1.0)
        outcome = PipelineOutcome(state=SignalState.BUY, direction=Direction.LONG, trade_params=tp)
        signal = assemble_signal(handle.id, handle.contract, outcome, context, 1.0, EngineConfig(), now_ts=context["meta"]["as_of"])
        assert signal.trade_params is tp

    def test_context_ref_reflects_context_meta_and_data_quality(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context(data_quality="DEGRADED")
        outcome = PipelineOutcome(state=SignalState.NO_SIGNAL)
        signal = assemble_signal(handle.id, handle.contract, outcome, context, 1.0, EngineConfig(), now_ts=context["meta"]["as_of"])
        assert signal.context_ref.data_quality.value == "DEGRADED"
        assert signal.context_ref.context_schema_version == context["meta"]["context_schema_version"]


class TestAssembleSignalWithoutContract:
    """``contract=None`` is the CORRUPTED_OUTPUT/EVAL_TIMEOUT fallback path -- every field must
    default to the safest possible value, never fabricate strategy-specific data."""

    def test_mechanism_is_the_unavailable_placeholder(self) -> None:
        context = make_context()
        outcome = PipelineOutcome(state=SignalState.INVALID)
        signal = assemble_signal(
            "S1", None, outcome, context, 1.0, EngineConfig(), now_ts=context["meta"]["as_of"],
            extra_quality_flags=(QualityFlag.CORRUPTED_OUTPUT,),
        )
        assert signal.mechanism == "unavailable: strategy output could not be read"
        assert signal.strategy_version is None

    def test_explanation_folds_extra_quality_flags_into_why_failed(self) -> None:
        context = make_context()
        outcome = PipelineOutcome(state=SignalState.INVALID)
        signal = assemble_signal(
            "S1", None, outcome, context, 1.0, EngineConfig(), now_ts=context["meta"]["as_of"],
            extra_quality_flags=(QualityFlag.EVAL_TIMEOUT,),
        )
        assert signal.explanation.why_failed == (ConditionRecord(code="EVAL_TIMEOUT", satisfied=False),)

    def test_explanation_has_no_confirmations_or_conditions(self) -> None:
        context = make_context()
        outcome = PipelineOutcome(state=SignalState.INVALID)
        signal = assemble_signal(
            "S1", None, outcome, context, 1.0, EngineConfig(), now_ts=context["meta"]["as_of"],
            extra_quality_flags=(QualityFlag.CORRUPTED_OUTPUT,),
        )
        assert signal.explanation.why_exists == ()
        assert signal.explanation.required_conditions == ()
        assert signal.explanation.confirmations.required == ()

    def test_strategy_ref_still_carries_the_strategy_id(self) -> None:
        context = make_context()
        outcome = PipelineOutcome(state=SignalState.INVALID)
        signal = assemble_signal(
            "S42", None, outcome, context, 1.0, EngineConfig(), now_ts=context["meta"]["as_of"],
            extra_quality_flags=(QualityFlag.CORRUPTED_OUTPUT,),
        )
        assert signal.explanation.strategy_ref.id == "S42"
        assert signal.explanation.strategy_ref.version is None
