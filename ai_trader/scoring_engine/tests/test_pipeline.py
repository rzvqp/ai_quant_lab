"""Tests for :mod:`ai_trader.scoring_engine.pipeline`."""

from __future__ import annotations

from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.evidence import EvidenceCache
from ai_trader.scoring_engine.pipeline import score_signal_stage1
from ai_trader.scoring_engine.tests.fixtures.fake_strategy_manager import FakeStrategyManager, make_signal
from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict
from ai_trader.strategy_manager.types import Lifecycle

CONFIG = ScoringConfig()


class TestMalformedSignal:
    def test_non_strategy_signal_object_is_score_invalid(self) -> None:
        partial = score_signal_stage1(object(), None, {}, CONFIG)  # type: ignore[arg-type]
        assert partial.is_terminal
        assert partial.terminal_state == "SCORE_INVALID"
        assert partial.terminal_recommendation == "INVALID"

    def test_none_is_score_invalid(self) -> None:
        partial = score_signal_stage1(None, None, {}, CONFIG)  # type: ignore[arg-type]
        assert partial.terminal_state == "SCORE_INVALID"

    def test_missing_context_ref_is_score_invalid_not_a_crash(self) -> None:
        """Regression guard: a StrategySignal with context_ref=None (a caller bypassing the type
        system, e.g. via dataclasses.replace) used to slip past the malformed check and crash later
        with AttributeError inside assembler/component code that reads signal.context_ref.*."""
        from dataclasses import replace as dc_replace

        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True,
        })
        broken = dc_replace(signal, context_ref=None)  # type: ignore[arg-type]
        partial = score_signal_stage1(broken, None, {}, CONFIG)
        assert partial.terminal_state == "SCORE_INVALID"

    def test_missing_explanation_is_score_invalid_not_a_crash(self) -> None:
        from dataclasses import replace as dc_replace

        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True,
        })
        broken = dc_replace(signal, explanation=None)  # type: ignore[arg-type]
        partial = score_signal_stage1(broken, None, {}, CONFIG)
        assert partial.terminal_state == "SCORE_INVALID"

    def test_as_of_zero_with_invalid_state_is_skipped_not_score_invalid(self) -> None:
        """Regression guard: as_of==0 is the Signal Engine's OWN documented sentinel for "context
        missing meta.as_of" (its _missing_as_of_signal fallback), always paired with
        state=SignalState.INVALID -- a legitimately-typed signal reporting an upstream failure, which
        must be routed through the ordinary non-actionable-state path (SKIPPED), not rejected here as
        if the object itself were malformed."""
        from dataclasses import replace as dc_replace

        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True,
        })
        from ai_trader.signal_engine.types import SignalState
        upstream_failure = dc_replace(signal, as_of=0, state=SignalState.INVALID)
        partial = score_signal_stage1(upstream_failure, None, {}, CONFIG)
        assert partial.terminal_state == "SKIPPED"


class TestNonActionableIsSkipped:
    def test_need_context_is_skipped(self) -> None:
        signal = make_signal(required_timeframes=frozenset({"H1"}))
        assert signal.state.value == "NEED_CONTEXT"
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        assert partial.terminal_state == "SKIPPED"
        assert partial.terminal_recommendation == "SKIP"
        assert partial.components.signal_strength == 0.0  # never computed

    def test_no_signal_is_skipped(self) -> None:
        signal = make_signal(detect_response={"setup_forming": False})
        assert signal.state.value == "NO_SIGNAL"
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        assert partial.terminal_state == "SKIPPED"

    def test_blocked_is_skipped(self) -> None:
        signal = make_signal(can_trade_response={"allowed": False, "reasons": ["SPREAD"]})
        assert signal.state.value == "BLOCKED"
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        assert partial.terminal_state == "SKIPPED"

    def test_invalid_is_skipped(self) -> None:
        signal = make_signal(health_response={"state": "INVALID"})
        assert signal.state.value == "INVALID"
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        assert partial.terminal_state == "SKIPPED"

    def test_skipped_never_binds_evidence(self) -> None:
        calls: list[str] = []

        class _TrackingManager:
            def find_strategy(self, strategy_id: str) -> object:
                calls.append(strategy_id)
                from ai_trader.strategy_manager.types import NotFound
                return NotFound(strategy_id)

            def get_contract(self, strategy_id: str) -> object:
                calls.append(strategy_id)
                from ai_trader.strategy_manager.types import NotFound
                return NotFound(strategy_id)

        signal = make_signal(detect_response={"setup_forming": False})
        score_signal_stage1(signal, _TrackingManager(), {}, CONFIG)  # type: ignore[arg-type]
        assert calls == []


class TestActionableComputesComponents:
    def test_buy_produces_non_terminal_partial_with_all_components(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "entry": 100.0, "stop": 99.0, "target": 102.0,
            "strength": 0.8, "required_confirmations_met": True, "regime": "TREND_UP",
        })
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        assert not partial.is_terminal
        assert partial.components.signal_strength == 0.8
        assert 0.0 <= partial.base_quality_pre_conflict <= 1.0

    def test_wait_confirmation_is_not_terminal(self) -> None:
        signal = make_signal(
            required_data=[{"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 5, "htf": None}],
            generate_signal_response={"present": True, "direction": "LONG", "required_confirmations_met": False},
        )
        assert signal.state.value == "WAIT_CONFIRMATION"
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        assert not partial.is_terminal

    def test_evidence_is_bound_from_the_manager(self) -> None:
        mgr = FakeStrategyManager()
        contract = parse_contract(make_contract_dict(id="S1"))
        mgr.register("S1", contract, lifecycle=Lifecycle.VALIDATED)
        signal = make_signal(strategy_id="S1", generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True,
        })
        partial = score_signal_stage1(signal, mgr, {}, CONFIG)
        assert partial.evidence.lifecycle is Lifecycle.VALIDATED
        assert partial.evidence.contract is contract

    def test_conflict_penalty_placeholder_is_zero_pre_conflict(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True,
        })
        partial = score_signal_stage1(signal, None, {}, CONFIG)
        assert partial.components.conflict_penalty == 0.0

    def test_cache_is_shared_across_calls_for_the_same_strategy(self) -> None:
        mgr = FakeStrategyManager()
        contract = parse_contract(make_contract_dict(id="S1"))
        mgr.register("S1", contract)
        cache: EvidenceCache = {}
        s1 = make_signal(strategy_id="S1", generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True,
        })
        score_signal_stage1(s1, mgr, cache, CONFIG)
        score_signal_stage1(s1, mgr, cache, CONFIG)
        assert mgr.calls.count("get_contract:S1") == 1
