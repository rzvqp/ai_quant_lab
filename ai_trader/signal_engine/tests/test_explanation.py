"""Tests for :mod:`ai_trader.signal_engine.explanation`."""

from __future__ import annotations

from ai_trader.signal_engine.explanation import build_explanation
from ai_trader.signal_engine.pipeline import PipelineOutcome, run_pipeline
from ai_trader.signal_engine.types import Confirmations, SignalState
from ai_trader.signal_engine.tests.fixtures.fake_strategy import make_context, make_fake_handle
from ai_trader.strategy_manager.contract import Regime


class TestBuildExplanation:
    def test_carries_mechanism_verbatim_from_contract(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context()
        outcome = PipelineOutcome(state=SignalState.NO_SIGNAL)
        explanation = build_explanation(outcome, handle.contract, context, "1.0.0")
        assert explanation.triggering_mechanism.mechanism_text == handle.contract.semantics.mechanism

    def test_strategy_ref_matches_contract_identity(self) -> None:
        handle, _ = make_fake_handle(strategy_id="S9")
        context = make_context()
        outcome = PipelineOutcome(state=SignalState.NO_SIGNAL)
        explanation = build_explanation(outcome, handle.contract, context, "1.0.0")
        assert explanation.strategy_ref.id == handle.contract.identity.id
        assert explanation.strategy_ref.version == handle.contract.identity.version

    def test_context_summary_reflects_context_meta_and_session(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context(symbol="XAUUSD", as_of=123, session_name="london")
        outcome = PipelineOutcome(state=SignalState.NO_SIGNAL)
        explanation = build_explanation(outcome, handle.contract, context, "1.0.0")
        assert explanation.context_summary.symbol == "XAUUSD"
        assert explanation.context_summary.as_of == 123
        assert explanation.context_summary.session == "london"

    def test_regime_is_none_when_outcome_has_no_regime(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context()
        outcome = PipelineOutcome(state=SignalState.NO_SIGNAL, regime=None)
        explanation = build_explanation(outcome, handle.contract, context, "1.0.0")
        assert explanation.context_summary.regime is None

    def test_regime_is_parsed_into_the_enum_when_present(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context()
        outcome = PipelineOutcome(state=SignalState.BUY, regime="TREND_UP")
        explanation = build_explanation(outcome, handle.contract, context, "1.0.0")
        assert explanation.context_summary.regime is Regime.TREND_UP

    def test_timeframes_used_is_sorted_tuple_of_context_timeframes(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context(features={"M15": {"m_atr": 1.0}, "H1": {"m_atr": 1.0}})
        outcome = PipelineOutcome(state=SignalState.NO_SIGNAL)
        explanation = build_explanation(outcome, handle.contract, context, "1.0.0")
        assert explanation.context_summary.timeframes_used == ("H1", "M15")

    def test_missing_and_invalid_conditions_are_wrapped_as_condition_records(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context()
        outcome = PipelineOutcome(
            state=SignalState.NEED_CONTEXT, missing_context=("H1",), invalid_conditions=("SPREAD",),
        )
        explanation = build_explanation(outcome, handle.contract, context, "1.0.0")
        assert explanation.missing_conditions == (
            __import__("ai_trader.signal_engine.types", fromlist=["ConditionRecord"]).ConditionRecord(
                code="H1", satisfied=False,
            ),
        )
        assert explanation.invalid_conditions[0].code == "SPREAD"

    def test_required_conditions_derived_from_confirmations_when_present(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context()
        outcome = PipelineOutcome(
            state=SignalState.WAIT_CONFIRMATION,
            confirmations_detail=Confirmations(required=("C1", "C2"), met=("C1",), pending=("C2",)),
        )
        explanation = build_explanation(outcome, handle.contract, context, "1.0.0")
        by_code = {r.code: r.satisfied for r in explanation.required_conditions}
        assert by_code == {"C1": True, "C2": False}

    def test_why_exists_and_why_failed_pass_through_unchanged(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context()
        from ai_trader.signal_engine.types import ConditionRecord

        outcome = PipelineOutcome(
            state=SignalState.BUY,
            why_exists=(ConditionRecord(code="A", satisfied=True),),
            why_failed=(ConditionRecord(code="B", satisfied=False),),
        )
        explanation = build_explanation(outcome, handle.contract, context, "1.0.0")
        assert explanation.why_exists == outcome.why_exists
        assert explanation.why_failed == outcome.why_failed

    def test_integrates_with_real_pipeline_outcome(self) -> None:
        handle, api = make_fake_handle()
        api.generate_signal_response = {
            "present": True, "direction": "LONG", "strength": 0.8, "required_confirmations_met": True,
        }
        context = make_context()
        outcome = run_pipeline(context, handle, trader_state=None)
        explanation = build_explanation(outcome, handle.contract, context, "1.0.0")
        assert explanation.state is SignalState.BUY
