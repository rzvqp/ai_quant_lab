"""Tests for :mod:`ai_trader.signal_engine.pipeline` -- the fixed per-strategy evaluation pipeline.

Covers every stage short-circuit and all directly-reachable signal states via the controllable
:class:`~ai_trader.signal_engine.tests.fixtures.fake_strategy.FakeStrategyApi` double.
"""

from __future__ import annotations

import pytest

from ai_trader.signal_engine.pipeline import MalformedStrategyResponseError, run_pipeline
from ai_trader.signal_engine.types import Direction, SignalState
from ai_trader.signal_engine.tests.fixtures.fake_strategy import make_context, make_fake_handle


class TestHealthShortCircuit:
    def test_health_invalid_returns_invalid_without_calling_can_trade(self) -> None:
        handle, api = make_fake_handle()
        api.health_response = {"state": "INVALID"}
        outcome = run_pipeline(make_context(), handle, trader_state=None)
        assert outcome.state is SignalState.INVALID
        assert "can_trade" not in api.calls
        assert outcome.direction is Direction.NONE

    def test_health_disabled_returns_blocked(self) -> None:
        handle, api = make_fake_handle()
        api.health_response = {"state": "DISABLED"}
        outcome = run_pipeline(make_context(), handle, trader_state=None)
        assert outcome.state is SignalState.BLOCKED
        assert "health:DISABLED" in outcome.invalid_conditions

    def test_health_ok_proceeds_to_can_trade(self) -> None:
        handle, api = make_fake_handle()
        api.health_response = {"state": "OK"}
        run_pipeline(make_context(), handle, trader_state=None)
        assert "can_trade" in api.calls

    def test_health_missing_state_key_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.health_response = {}
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)

    def test_health_non_string_state_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.health_response = {"state": 123}
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)

    def test_health_non_dict_response_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.health_fn = lambda ctx, ts: "not a dict"
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)


class TestCanTradeShortCircuit:
    def test_not_allowed_returns_blocked_with_reasons(self) -> None:
        handle, api = make_fake_handle()
        api.can_trade_response = {"allowed": False, "reasons": ["SPREAD_TOO_WIDE", "NEWS_BLACKOUT"]}
        outcome = run_pipeline(make_context(), handle, trader_state=None)
        assert outcome.state is SignalState.BLOCKED
        assert outcome.invalid_conditions == ("SPREAD_TOO_WIDE", "NEWS_BLACKOUT")
        assert outcome.direction is Direction.NONE

    def test_not_allowed_with_no_reasons_still_blocks(self) -> None:
        handle, api = make_fake_handle()
        api.can_trade_response = {"allowed": False, "reasons": []}
        outcome = run_pipeline(make_context(), handle, trader_state=None)
        assert outcome.state is SignalState.BLOCKED
        assert outcome.why_failed[0].code == "CAN_TRADE_BLOCKED"

    def test_allowed_proceeds_to_required_context(self) -> None:
        handle, api = make_fake_handle()
        api.can_trade_response = {"allowed": True, "reasons": []}
        run_pipeline(make_context(), handle, trader_state=None)
        assert "required_context" in api.calls

    def test_missing_allowed_key_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.can_trade_response = {}
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)

    def test_non_bool_allowed_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.can_trade_response = {"allowed": "yes"}
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)

    def test_non_list_reasons_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.can_trade_response = {"allowed": False, "reasons": "not a list"}
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)


class TestContextValidation:
    def test_missing_context_returns_need_context(self) -> None:
        handle, api = make_fake_handle()
        api.timeframes = frozenset({"H1"})
        api.fields_by_timeframe = {"H1": frozenset({"m_atr"})}
        api.lookback_by_timeframe = {"H1": 5}
        context = make_context(features={"M15": {"m_atr": 1.0}})
        outcome = run_pipeline(context, handle, trader_state=None)
        assert outcome.state is SignalState.NEED_CONTEXT
        assert outcome.missing_context == ("H1",)
        assert outcome.direction is Direction.NONE

    def test_need_context_never_calls_detect(self) -> None:
        handle, api = make_fake_handle()
        api.timeframes = frozenset({"H1"})
        api.fields_by_timeframe = {"H1": frozenset()}
        api.lookback_by_timeframe = {}
        context = make_context(features={"M15": {"m_atr": 1.0}})
        run_pipeline(context, handle, trader_state=None)
        assert "detect" not in api.calls

    def test_need_context_never_calls_explain_signal(self) -> None:
        """Stage 5 (explain_signal) only follows Stage 4 (detect) -- NEED_CONTEXT never reaches it."""
        handle, api = make_fake_handle()
        api.timeframes = frozenset({"H1"})
        api.fields_by_timeframe = {"H1": frozenset()}
        api.lookback_by_timeframe = {}
        context = make_context(features={"M15": {"m_atr": 1.0}})
        run_pipeline(context, handle, trader_state=None)
        assert "explain_signal" not in api.calls

    def test_sufficient_context_proceeds_to_detect(self) -> None:
        handle, api = make_fake_handle()
        run_pipeline(make_context(), handle, trader_state=None)
        assert "detect" in api.calls

    def test_non_required_context_type_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.required_context_fn = lambda: {"not": "a RequiredContext"}  # type: ignore[assignment]
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)


class TestDetectStage:
    def test_setup_not_forming_returns_no_signal_with_explanation(self) -> None:
        handle, api = make_fake_handle()
        api.detect_response = {"active": False, "setup_forming": False, "reason": "flat market"}
        outcome = run_pipeline(make_context(), handle, trader_state=None)
        assert outcome.state is SignalState.NO_SIGNAL
        assert outcome.why_failed[0].code == "NO_SETUP"
        assert outcome.why_failed[0].observed == "flat market"
        assert outcome.direction is Direction.NONE
        assert "explain_signal" in api.calls

    def test_setup_not_forming_never_calls_generate_signal(self) -> None:
        handle, api = make_fake_handle()
        api.detect_response = {"setup_forming": False}
        run_pipeline(make_context(), handle, trader_state=None)
        assert "generate_signal" not in api.calls

    def test_missing_setup_forming_key_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.detect_response = {}
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)

    def test_non_bool_setup_forming_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.detect_response = {"setup_forming": "yes"}
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)

    def test_non_dict_detect_response_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.detect_fn = lambda ctx: None
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)


class TestGenerateSignalStage:
    def test_present_false_returns_no_signal(self) -> None:
        handle, api = make_fake_handle()
        api.generate_signal_response = {"present": False, "reason": "no edge"}
        outcome = run_pipeline(make_context(), handle, trader_state=None)
        assert outcome.state is SignalState.NO_SIGNAL
        assert outcome.why_failed[0].code == "NO_SIGNAL_PRESENT"
        assert outcome.why_failed[0].observed == "no edge"

    def test_missing_present_key_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.generate_signal_response = {}
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)

    def test_non_bool_present_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.generate_signal_response = {"present": 1}
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)

    def test_missing_direction_key_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.generate_signal_response = {"present": True}
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)

    def test_invalid_direction_value_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.generate_signal_response = {"present": True, "direction": "SIDEWAYS"}
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)

    def test_present_true_with_direction_none_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.generate_signal_response = {"present": True, "direction": "NONE"}
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)

    def test_strength_out_of_range_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.generate_signal_response = {
            "present": True, "direction": "LONG", "strength": 1.5, "required_confirmations_met": True,
        }
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)

    def test_non_numeric_strength_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.generate_signal_response = {
            "present": True, "direction": "LONG", "strength": "high", "required_confirmations_met": True,
        }
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)


class TestWaitConfirmation:
    def test_confirmations_not_met_returns_wait_confirmation(self) -> None:
        handle, api = make_fake_handle()
        api.generate_signal_response = {
            "present": True, "direction": "LONG", "strength": 0.5, "confidence": "LOW",
            "required_confirmations_met": False, "regime": "TREND_UP",
        }
        outcome = run_pipeline(make_context(), handle, trader_state=None)
        assert outcome.state is SignalState.WAIT_CONFIRMATION

    def test_wait_confirmation_direction_is_none_per_schema(self) -> None:
        """Regression guard: SIGNAL_SCHEMA.json's allOf rule requires direction=NONE for every
        non-actionable state, WAIT_CONFIRMATION included -- even though the strategy's own proposed
        direction was LONG/SHORT."""
        handle, api = make_fake_handle()
        api.generate_signal_response = {
            "present": True, "direction": "SHORT", "strength": 0.5, "required_confirmations_met": False,
        }
        outcome = run_pipeline(make_context(), handle, trader_state=None)
        assert outcome.direction is Direction.NONE

    def test_wait_confirmation_trade_params_is_none_per_schema(self) -> None:
        handle, api = make_fake_handle()
        api.generate_signal_response = {
            "present": True, "direction": "LONG", "entry": 100.0, "stop": 99.0, "target": 102.0,
            "strength": 0.5, "required_confirmations_met": False,
        }
        outcome = run_pipeline(make_context(), handle, trader_state=None)
        assert outcome.trade_params is None

    def test_wait_confirmation_preserves_strength_and_confidence(self) -> None:
        handle, api = make_fake_handle()
        api.generate_signal_response = {
            "present": True, "direction": "LONG", "strength": 0.42, "confidence": "HIGH",
            "required_confirmations_met": False,
        }
        outcome = run_pipeline(make_context(), handle, trader_state=None)
        assert outcome.signal_strength == 0.42
        assert outcome.confidence == "HIGH"

    def test_wait_confirmation_calls_explain_signal(self) -> None:
        handle, api = make_fake_handle()
        api.generate_signal_response = {"present": True, "direction": "LONG", "required_confirmations_met": False}
        run_pipeline(make_context(), handle, trader_state=None)
        assert "explain_signal" in api.calls


class TestActionableStates:
    def test_present_and_confirmed_long_returns_buy(self) -> None:
        handle, api = make_fake_handle()
        api.generate_signal_response = {
            "present": True, "direction": "LONG", "entry": 100.0, "stop": 99.0, "target": 102.0,
            "strength": 0.9, "confidence": "HIGH", "required_confirmations_met": True,
        }
        outcome = run_pipeline(make_context(), handle, trader_state=None)
        assert outcome.state is SignalState.BUY
        assert outcome.direction is Direction.LONG

    def test_present_and_confirmed_short_returns_sell(self) -> None:
        handle, api = make_fake_handle()
        api.generate_signal_response = {
            "present": True, "direction": "SHORT", "entry": 100.0, "stop": 101.0, "target": 98.0,
            "strength": 0.9, "confidence": "HIGH", "required_confirmations_met": True,
        }
        outcome = run_pipeline(make_context(), handle, trader_state=None)
        assert outcome.state is SignalState.SELL
        assert outcome.direction is Direction.SHORT

    def test_actionable_signal_carries_trade_params(self) -> None:
        handle, api = make_fake_handle()
        api.generate_signal_response = {
            "present": True, "direction": "LONG", "entry": 100.0, "stop": 99.0, "target": 102.0,
            "risk_R": 1.0, "strength": 0.9, "required_confirmations_met": True,
        }
        outcome = run_pipeline(make_context(), handle, trader_state=None)
        assert outcome.trade_params is not None
        assert outcome.trade_params.entry == 100.0
        assert outcome.trade_params.stop == 99.0
        assert outcome.trade_params.target == 102.0

    def test_actionable_signal_calls_explain_signal_and_folds_triggered_conditions(self) -> None:
        handle, api = make_fake_handle()
        api.generate_signal_response = {
            "present": True, "direction": "LONG", "strength": 0.9, "required_confirmations_met": True,
        }
        api.explain_signal_response = {
            "headline": "sweep + reclaim", "triggered_conditions": ["SWEEP_TAKEN", "CLOSE_BACK_INSIDE"],
        }
        outcome = run_pipeline(make_context(), handle, trader_state=None)
        codes = [r.code for r in outcome.why_exists]
        assert "SWEEP_TAKEN" in codes
        assert "CLOSE_BACK_INSIDE" in codes
        assert outcome.explain_headline == "sweep + reclaim"


class TestExplainSignalStage:
    def test_non_dict_explanation_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.explain_signal_fn = lambda ctx: "not a dict"
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)

    def test_non_string_headline_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.explain_signal_response = {"headline": 123, "triggered_conditions": []}
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)

    def test_non_list_triggered_conditions_raises_malformed(self) -> None:
        handle, api = make_fake_handle()
        api.explain_signal_response = {"headline": "x", "triggered_conditions": "not a list"}
        with pytest.raises(MalformedStrategyResponseError):
            run_pipeline(make_context(), handle, trader_state=None)

    def test_absent_headline_is_accepted(self) -> None:
        handle, api = make_fake_handle()
        api.explain_signal_response = {"triggered_conditions": []}
        outcome = run_pipeline(make_context(), handle, trader_state=None)
        assert outcome.explain_headline is None


class TestDeterminism:
    def test_identical_context_and_handle_yield_identical_outcome(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context()
        first = run_pipeline(context, handle, trader_state=None)
        second = run_pipeline(context, handle, trader_state=None)
        assert first == second

    def test_a_fresh_handle_with_same_config_yields_same_outcome(self) -> None:
        handle_a, _ = make_fake_handle()
        handle_b, _ = make_fake_handle()
        context = make_context()
        assert run_pipeline(context, handle_a, trader_state=None) == run_pipeline(context, handle_b, trader_state=None)


class TestRealStrategyRuntimeHandleIntegration:
    """The only concrete production ``StrategyHandle.api`` in the repository
    (``StrategyRuntimeHandle``) raises ``StrategyApiNotImplementedError`` for every method this
    pipeline calls except ``required_context()`` -- verifies the pipeline propagates that exception
    rather than swallowing or misclassifying it (the engine's outer boundary is what turns it into
    CORRUPTED_OUTPUT, tested separately in test_engine_unit.py)."""

    def test_real_handle_health_call_raises_not_swallowed(self) -> None:
        from ai_trader.strategy_manager.contract import parse_contract
        from ai_trader.strategy_manager.exceptions import StrategyApiNotImplementedError
        from ai_trader.strategy_manager.handle import StrategyHandle, StrategyRuntimeHandle
        from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict

        contract = parse_contract(make_contract_dict())
        api = StrategyRuntimeHandle("S1", contract, frozenset({"XAUUSD"}))
        handle = StrategyHandle(id="S1", contract=contract, api=api)
        with pytest.raises(StrategyApiNotImplementedError):
            run_pipeline(make_context(), handle, trader_state=None)
