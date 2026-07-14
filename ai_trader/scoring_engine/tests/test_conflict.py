"""Tests for :mod:`ai_trader.scoring_engine.conflict`."""

from __future__ import annotations

from ai_trader.scoring_engine.conflict import compute_conflict_penalties
from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.pipeline import PartialScore, score_signal_stage1
from ai_trader.scoring_engine.tests.fixtures.fake_strategy_manager import FakeStrategyManager, make_signal
from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict

CONFIG = ScoringConfig()


def _partial(
    strategy_id: str, direction: str, strength: float, manager: FakeStrategyManager | None = None,
) -> PartialScore:
    signal = make_signal(strategy_id=strategy_id, generate_signal_response={
        "present": True, "direction": direction, "entry": 100.0,
        "stop": 99.0 if direction == "LONG" else 101.0, "target": 102.0 if direction == "LONG" else 98.0,
        "strength": strength, "required_confirmations_met": True,
    })
    return score_signal_stage1(signal, manager, {}, CONFIG)


def _manager_with_class(strategy_id: str, klass: str) -> FakeStrategyManager:
    mgr = FakeStrategyManager()
    contract = parse_contract(make_contract_dict(id=strategy_id, klass=klass))
    mgr.register(strategy_id, contract)
    return mgr


class TestNoConflict:
    def test_single_signal_has_no_conflict(self) -> None:
        p = _partial("S1", "LONG", 0.8)
        results = compute_conflict_penalties([p])
        assert results[0].conflict_penalty == 0.0
        assert results[0].reason_codes == ()

    def test_terminal_partials_get_zero_conflict(self) -> None:
        signal = make_signal(detect_response={"setup_forming": False})
        terminal = score_signal_stage1(signal, None, {}, CONFIG)
        results = compute_conflict_penalties([terminal])
        assert results[0].conflict_penalty == 0.0

    def test_same_direction_no_class_info_has_no_correlation(self) -> None:
        p1 = _partial("S1", "LONG", 0.9)
        p2 = _partial("S2", "LONG", 0.5)
        results = compute_conflict_penalties([p1, p2])
        assert results[0].conflict_penalty == 0.0
        assert results[1].conflict_penalty == 0.0


class TestOpposingConflict:
    def test_lower_quality_opposing_signal_is_penalized(self) -> None:
        strong = _partial("S1", "LONG", 0.95)
        weak = _partial("S2", "SHORT", 0.2)
        results = compute_conflict_penalties([strong, weak])
        assert results[0].conflict_penalty == 0.0  # the stronger side is unaffected
        assert results[1].conflict_penalty == 0.5
        assert results[1].reason_codes[0].code == "CONFLICT_OPPOSING"

    def test_higher_quality_side_is_never_penalized_by_a_weaker_opposer(self) -> None:
        strong = _partial("S1", "LONG", 0.95)
        weak = _partial("S2", "SHORT", 0.2)
        results = compute_conflict_penalties([weak, strong])  # order swapped
        by_id = {p.signal.strategy_id: r for p, r in zip([weak, strong], results)}
        assert by_id["S1"].conflict_penalty == 0.0
        assert by_id["S2"].conflict_penalty == 0.5

    def test_equal_quality_is_not_strictly_higher_so_no_penalty(self) -> None:
        a = _partial("S1", "LONG", 0.5)
        b = _partial("S2", "SHORT", 0.5)
        results = compute_conflict_penalties([a, b])
        assert results[0].conflict_penalty == 0.0
        assert results[1].conflict_penalty == 0.0


class TestCorrelatedConflict:
    def test_same_direction_same_class_is_penalized(self) -> None:
        mgr = _manager_with_class("S1", "sweep")
        mgr.register("S2", parse_contract(make_contract_dict(id="S2", klass="sweep")))
        p1 = _partial("S1", "LONG", 0.7, manager=mgr)
        p2 = _partial("S2", "LONG", 0.6, manager=mgr)
        results = compute_conflict_penalties([p1, p2])
        assert results[0].conflict_penalty == 0.2
        assert results[0].reason_codes[0].code == "CONFLICT_CORRELATED"
        assert results[1].conflict_penalty == 0.2

    def test_same_direction_different_class_is_not_correlated(self) -> None:
        mgr = FakeStrategyManager()
        mgr.register("S1", parse_contract(make_contract_dict(id="S1", klass="sweep")))
        mgr.register("S2", parse_contract(make_contract_dict(id="S2", klass="breakout")))
        p1 = _partial("S1", "LONG", 0.7, manager=mgr)
        p2 = _partial("S2", "LONG", 0.6, manager=mgr)
        results = compute_conflict_penalties([p1, p2])
        assert results[0].conflict_penalty == 0.0
        assert results[1].conflict_penalty == 0.0

    def test_correlated_penalty_caps_at_04(self) -> None:
        mgr = FakeStrategyManager()
        for sid in ("S1", "S2", "S3", "S4"):
            mgr.register(sid, parse_contract(make_contract_dict(id=sid, klass="sweep")))
        partials = [_partial(sid, "LONG", 0.5, manager=mgr) for sid in ("S1", "S2", "S3", "S4")]
        results = compute_conflict_penalties(partials)
        # each of the 4 has 3 correlated peers -> 0.2*3=0.6, capped at 0.4
        for r in results:
            assert r.conflict_penalty == 0.4

    def test_opposite_direction_same_class_does_not_count_as_correlated(self) -> None:
        """Correlation only applies to SAME-direction stacking (SCORING_MODEL.md §4) -- a same-class
        peer trading the opposite direction must be excluded from the correlated count entirely (it
        may still contribute to the OPPOSING penalty instead, a separate mechanism)."""
        mgr = FakeStrategyManager()
        mgr.register("S1", parse_contract(make_contract_dict(id="S1", klass="sweep")))
        mgr.register("S2", parse_contract(make_contract_dict(id="S2", klass="sweep")))
        long_signal = _partial("S1", "LONG", 0.5, manager=mgr)
        short_signal = _partial("S2", "SHORT", 0.5, manager=mgr)
        results = compute_conflict_penalties([long_signal, short_signal])
        assert not any(r.code == "CONFLICT_CORRELATED" for r in results[0].reason_codes)
        assert not any(r.code == "CONFLICT_CORRELATED" for r in results[1].reason_codes)

    def test_missing_evidence_does_not_participate_in_correlation(self) -> None:
        mgr = FakeStrategyManager()
        mgr.register("S1", parse_contract(make_contract_dict(id="S1", klass="sweep")))
        # S2 unregistered -> evidence missing -> no class info
        p1 = _partial("S1", "LONG", 0.7, manager=mgr)
        p2 = _partial("S2", "LONG", 0.6, manager=mgr)
        results = compute_conflict_penalties([p1, p2])
        assert results[0].conflict_penalty == 0.0
        assert results[1].conflict_penalty == 0.0


class TestDeterminism:
    def test_result_order_matches_input_order(self) -> None:
        p1 = _partial("S1", "LONG", 0.9)
        p2 = _partial("S2", "SHORT", 0.2)
        results = compute_conflict_penalties([p1, p2])
        assert len(results) == 2

    def test_repeated_calls_are_identical(self) -> None:
        p1 = _partial("S1", "LONG", 0.9)
        p2 = _partial("S2", "SHORT", 0.2)
        first = compute_conflict_penalties([p1, p2])
        second = compute_conflict_penalties([p1, p2])
        assert first == second
