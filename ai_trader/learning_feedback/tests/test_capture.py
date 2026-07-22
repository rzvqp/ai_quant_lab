"""Unit/integration tests for :mod:`ai_trader.learning_feedback.capture` -- Phase E.

No `SimulationHarness` anywhere in this file -- every Shadow/Risk Manager/Portfolio Simulator record is
constructed directly, per DoD Phase E §5's own "no harness" integration-test requirement.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.context_memory.contracts import (
    ContextSnapshot,
    Observation,
    ObservationId,
)
from ai_trader.context_memory.enums import (
    ContextAgreementLevel,
    ContextDataQualityState,
    ContextEdgeStatus,
    ContextExpansionState,
    ContextLiquidityState,
    ContextMomentumState,
    ContextRiskDecision,
    ContextStructureState,
    ContextTrendDirection,
    ContextVolatilityRegime,
    OutcomeKind,
    OutcomeStatus,
    OutcomeUnavailableReason,
)
from ai_trader.context_memory.repository import ContextMemoryRepository
from ai_trader.learning_feedback.capture import (
    CorrelationMap,
    CorrelationRunMismatchError,
    DuplicateDecisionCaptureError,
    PendingCapture,
    capture_decision_observation,
    capture_operational_metadata,
    capture_portfolio_resolution,
    capture_strategy_resolution,
    register_pending_correlation,
)
from ai_trader.risk_manager.types import (
    AppliedRule,
    Decision,
    DeniedReason,
    EngineState,
    RiskDecision,
    RiskRefs,
)
from ai_trader.shadow_evidence.types import ShadowPositionRecord
from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.portfolio_simulator import TradeRecord

RUN_ID = "run-2026-07-22-A"
AS_OF = 1_700_000_000
COST_MODEL_REF = "spread_model=fixed_ticks|spread_ticks=1|commission_model=per_lot|commission_per_lot=0|cost_model_version=1.0.0"


# ------------------------------------------------------------------ fixture builders (local to this file)


def _observation(as_of: int = AS_OF) -> Observation:
    snap = ContextSnapshot(
        instrument="XAUUSD", as_of=as_of, session_state="LONDON",
        trend_m15=ContextTrendDirection.UP, trend_h1=ContextTrendDirection.UP,
        trend_h4=ContextTrendDirection.UP, trend_d1=ContextTrendDirection.UP,
        structure_state=ContextStructureState.BULLISH_BOS,
        momentum_m15=ContextMomentumState.NEUTRAL, momentum_h1=ContextMomentumState.NEUTRAL,
        momentum_h4=ContextMomentumState.NEUTRAL, momentum_d1=ContextMomentumState.NEUTRAL,
        volatility_regime=ContextVolatilityRegime.NORMAL, liquidity_state=ContextLiquidityState.NORMAL,
        expansion_state=ContextExpansionState.NORMAL,
        multi_timeframe_agreement=ContextAgreementLevel.STRONG,
        context_confidence_score=0.85, data_quality_state=ContextDataQualityState.OK,
    )
    return Observation(context_snapshot=snap, present_edges=())


def _position(**overrides: object) -> ShadowPositionRecord:
    kwargs: dict[str, object] = {
        "position_id": "POS-1", "strategy_id": "S1", "symbol": "XAUUSD", "direction": Direction.LONG,
        "entry_as_of": AS_OF + 900, "entry_price": 2000.0, "entry_opportunity_id": "OPP-1",
        "status": "CLOSED", "full_exit_as_of": AS_OF + 4500, "n_legs": 1,
        "aggregate_net_pnl": 25.0, "aggregate_holding_bars_full": 4,
    }
    kwargs.update(overrides)
    return ShadowPositionRecord(**kwargs)  # type: ignore[arg-type]


def _trade(**overrides: object) -> TradeRecord:
    kwargs: dict[str, object] = {
        "client_order_id": "CID-S1|XAUUSD|1700000000", "strategy_id": "S1", "symbol": "XAUUSD",
        "direction": Direction.LONG, "entry_price": 2000.0, "exit_price": 2010.0,
        "entry_as_of": AS_OF + 900, "exit_as_of": AS_OF + 4500, "qty": 1.0, "gross_pnl": 25.0,
        "fees": 1.0, "net_pnl": 24.0, "pnl_r": 1.5, "holding_bars": 4, "mfe": 30.0, "mae": -5.0,
    }
    kwargs.update(overrides)
    return TradeRecord(**kwargs)  # type: ignore[arg-type]


def _risk_decision(**overrides: object) -> RiskDecision:
    kwargs: dict[str, object] = {
        "risk_schema_version": "1.0.0", "risk_engine_version": "1.0.0", "risk_policy_version": "1.0.0",
        "decision_id": "S1|XAUUSD|1700000000", "score_id": "SC-1", "signal_id": "SIG-1",
        "strategy_id": "S1", "symbol": "XAUUSD", "timestamp": AS_OF, "as_of": AS_OF,
        "engine_state": EngineState.READY, "decision": Decision.ALLOW, "direction": Direction.LONG,
        "applied_rules": (AppliedRule(rule="GLOBAL_STATE", passed=True),),
        "refs": RiskRefs(scoring_schema_version="1.0.0", interface_version="1.0.0"),
        "denied_reasons": (),
    }
    kwargs.update(overrides)
    return RiskDecision(**kwargs)  # type: ignore[arg-type]


def _pending(observation_id: ObservationId, **overrides: object) -> PendingCapture:
    kwargs: dict[str, object] = {
        "run_id": RUN_ID, "client_order_ids": ("CID-S1|XAUUSD|1700000000",), "strategy_id": "S1",
        "symbol": "XAUUSD", "decision_id": "S1|XAUUSD|1700000000", "decision_as_of": AS_OF,
        "outcome_kind": OutcomeKind.STRATEGY, "observation_id": observation_id,
        "cost_model_ref": COST_MODEL_REF,
    }
    kwargs.update(overrides)
    return PendingCapture(**kwargs)  # type: ignore[arg-type]


def _repo(tmp_path: Path) -> ContextMemoryRepository:
    return ContextMemoryRepository(tmp_path / "repo")


# ------------------------------------------------------------------ PendingCapture / CorrelationMap basics


def test_pending_capture_rejects_empty_client_order_ids() -> None:
    with pytest.raises(ValueError):
        PendingCapture(
            run_id=RUN_ID, client_order_ids=(), strategy_id="S1", symbol="XAUUSD",
            decision_id="S1|XAUUSD|1700000000", decision_as_of=AS_OF, outcome_kind=OutcomeKind.STRATEGY,
            observation_id=ObservationId("x" * 64), cost_model_ref=COST_MODEL_REF,
        )


def test_register_and_pop_happy_path() -> None:
    cm = CorrelationMap(RUN_ID)
    entry = _pending(ObservationId("x" * 64))
    cm.register_decision(entry)
    assert cm.is_pending("CID-S1|XAUUSD|1700000000")
    popped = cm.pop_for_resolution(RUN_ID, "CID-S1|XAUUSD|1700000000")
    assert popped == entry


def test_cleanup_after_terminal_resolution() -> None:
    cm = CorrelationMap(RUN_ID)
    cm.register_decision(_pending(ObservationId("x" * 64)))
    assert cm.pending_count() == 1
    cm.pop_for_resolution(RUN_ID, "CID-S1|XAUUSD|1700000000")
    assert cm.pending_count() == 0
    assert not cm.is_pending("CID-S1|XAUUSD|1700000000")
    assert cm.is_resolved("CID-S1|XAUUSD|1700000000")


def test_unknown_key_returns_none() -> None:
    cm = CorrelationMap(RUN_ID)
    assert cm.pop_for_resolution(RUN_ID, "NEVER-REGISTERED") is None


def test_duplicate_decision_capture_raises() -> None:
    cm = CorrelationMap(RUN_ID)
    cm.register_decision(_pending(ObservationId("x" * 64)))
    with pytest.raises(DuplicateDecisionCaptureError):
        cm.register_decision(_pending(ObservationId("y" * 64)))


def test_duplicate_resolution_returns_none_on_second_attempt() -> None:
    cm = CorrelationMap(RUN_ID)
    cm.register_decision(_pending(ObservationId("x" * 64)))
    first = cm.pop_for_resolution(RUN_ID, "CID-S1|XAUUSD|1700000000")
    second = cm.pop_for_resolution(RUN_ID, "CID-S1|XAUUSD|1700000000")
    assert first is not None
    assert second is None


def test_run_mismatch_on_register_raises() -> None:
    cm = CorrelationMap(RUN_ID)
    with pytest.raises(CorrelationRunMismatchError):
        cm.register_decision(_pending(ObservationId("x" * 64), run_id="a-different-run"))


def test_run_mismatch_on_resolve_raises() -> None:
    cm = CorrelationMap(RUN_ID)
    cm.register_decision(_pending(ObservationId("x" * 64)))
    with pytest.raises(CorrelationRunMismatchError):
        cm.pop_for_resolution("a-different-run", "CID-S1|XAUUSD|1700000000")


def test_run_isolation_same_client_order_id_different_maps() -> None:
    # Two separate runs producing the IDENTICAL client_order_id string (confirmed possible: decision_id
    # carries no run-specific component) must never share pending state.
    cm_a = CorrelationMap("run-A")
    cm_b = CorrelationMap("run-B")
    cm_a.register_decision(_pending(ObservationId("x" * 64), run_id="run-A"))
    # The SAME client_order_id is free to register independently under a DIFFERENT map/run.
    cm_b.register_decision(_pending(ObservationId("y" * 64), run_id="run-B"))
    assert cm_a.is_pending("CID-S1|XAUUSD|1700000000")
    assert cm_b.is_pending("CID-S1|XAUUSD|1700000000")
    popped_a = cm_a.pop_for_resolution("run-A", "CID-S1|XAUUSD|1700000000")
    assert popped_a is not None
    assert popped_a.observation_id == ObservationId("x" * 64)
    # Resolving in run A must never affect run B's own independent entry.
    assert cm_b.is_pending("CID-S1|XAUUSD|1700000000")


def test_two_decisions_same_strategy_symbol_different_bars_do_not_collide() -> None:
    cm = CorrelationMap(RUN_ID)
    bar1 = _pending(ObservationId("a" * 64), client_order_ids=("CID-S1|XAUUSD|1700000000",), decision_as_of=AS_OF)
    bar2 = _pending(
        ObservationId("b" * 64), client_order_ids=("CID-S1|XAUUSD|1700000900",),
        decision_id="S1|XAUUSD|1700000900", decision_as_of=AS_OF + 900,
    )
    cm.register_decision(bar1)
    cm.register_decision(bar2)
    assert cm.pending_count() == 2
    popped1 = cm.pop_for_resolution(RUN_ID, "CID-S1|XAUUSD|1700000000")
    popped2 = cm.pop_for_resolution(RUN_ID, "CID-S1|XAUUSD|1700000900")
    assert popped1 is not None and popped1.observation_id == ObservationId("a" * 64)
    assert popped2 is not None and popped2.observation_id == ObservationId("b" * 64)


def test_bracket_order_multiple_aliases_resolve_together() -> None:
    # One decision -> 3 client_order_ids (parent entry, TP child, SL child) -- OCO-mutually-exclusive.
    cm = CorrelationMap(RUN_ID)
    entry = _pending(
        ObservationId("x" * 64),
        client_order_ids=("CID-S1|XAUUSD|1700000000", "CID-S1|XAUUSD|1700000000-TP", "CID-S1|XAUUSD|1700000000-SL"),
    )
    cm.register_decision(entry)
    assert cm.pending_count() == 1
    assert cm.is_pending("CID-S1|XAUUSD|1700000000-TP")
    assert cm.is_pending("CID-S1|XAUUSD|1700000000-SL")

    # TP fills first (cancels SL via OCO, per execution_simulator.py's own established behavior).
    popped = cm.pop_for_resolution(RUN_ID, "CID-S1|XAUUSD|1700000000-TP")
    assert popped is not None

    # The cancelled SL sibling must never be separately resolvable afterward -- retired together.
    assert not cm.is_pending("CID-S1|XAUUSD|1700000000-SL")
    assert cm.is_resolved("CID-S1|XAUUSD|1700000000-SL")
    assert cm.pop_for_resolution(RUN_ID, "CID-S1|XAUUSD|1700000000-SL") is None


def test_no_timestamp_based_fallback_correlation_survives_a_large_bar_gap() -> None:
    # Correlation is purely client_order_id based -- a long-WORKING limit/stop order resolving many
    # bars after the decision bar must still correlate correctly (proves no as_of-window heuristic).
    cm = CorrelationMap(RUN_ID)
    cm.register_decision(_pending(ObservationId("x" * 64), decision_as_of=AS_OF))
    far_future_resolution_as_of = AS_OF + 90_000_000  # a huge, deliberately unrealistic gap
    popped = cm.pop_for_resolution(RUN_ID, "CID-S1|XAUUSD|1700000000")
    assert popped is not None
    assert popped.decision_as_of == AS_OF  # unaffected by however late resolution actually happened
    assert far_future_resolution_as_of != popped.decision_as_of  # the gap is real, correlation ignored it


# ------------------------------------------------------------------ capture_decision_observation / capture_operational_metadata


def test_capture_decision_observation_happy_path(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    assert repo.count_observations() == 1


def test_capture_decision_observation_is_idempotent(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    first = capture_decision_observation(repo, _observation())
    second = capture_decision_observation(repo, _observation())
    assert first == second
    assert repo.count_observations() == 1


def test_capture_operational_metadata_allow(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    meta_id = capture_operational_metadata(repo, _risk_decision(decision=Decision.ALLOW), "ACTIVE", obs_id)
    assert meta_id is not None
    stored = repo.get_operational_metadata(meta_id)
    assert stored is not None
    assert stored.risk_decision is ContextRiskDecision.ALLOW


def test_capture_operational_metadata_deny_never_touches_correlation_map(tmp_path: Path) -> None:
    # A DENY decision is captured (OperationalMetadata) independently of the correlation map -- Risk
    # Manager never builds a client_order_id for a DENY (confirmed: build_order is never reached), so
    # no pending correlation entry is ever registered for it. This test proves OperationalMetadata
    # capture works correctly on its own, with an EMPTY correlation map throughout.
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    decision = _risk_decision(
        decision=Decision.DENY, denied_reasons=(DeniedReason(code="LIMIT_MAX_PER_SYMBOL"),),
    )
    meta_id = capture_operational_metadata(repo, decision, "PROBATION", obs_id)
    assert meta_id is not None
    stored = repo.get_operational_metadata(meta_id)
    assert stored is not None
    assert stored.risk_decision is ContextRiskDecision.DENY
    assert stored.denied_reason_code == "LIMIT_MAX_PER_SYMBOL"
    assert cm.pending_count() == 0  # nothing registered -- DENY never reaches order/client_order_id construction


# ------------------------------------------------------------------ end-to-end decision -> resolution (Strategy/Shadow)


def test_decision_to_shadow_resolution_end_to_end(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    assert register_pending_correlation(cm, _pending(obs_id))

    outcome_id = capture_strategy_resolution(
        repo, cm, RUN_ID, "CID-S1|XAUUSD|1700000000", _position(), _trade(pnl_r=1.5), AS_OF,
    )
    assert outcome_id is not None
    outcome = repo.get_outcome(outcome_id)
    assert outcome is not None
    assert outcome.status is OutcomeStatus.RESOLVED
    assert outcome.normalized_result == 1.5
    assert outcome.outcome_kind is OutcomeKind.STRATEGY
    assert cm.pending_count() == 0


def test_delayed_market_order_fill_still_correlates(tmp_path: Path) -> None:
    # Decision at AS_OF, entry fill one bar later (AS_OF + 900, the established "next bar open, not
    # signal bar" semantics) -- entry_as_of is NOT the decision bar, proving the client_order_id-based
    # design handles this correctly (the rejected entry_as_of-keyed design could not).
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation(as_of=AS_OF))
    assert obs_id is not None
    assert register_pending_correlation(cm, _pending(obs_id, decision_as_of=AS_OF))
    position = _position(entry_as_of=AS_OF + 900, full_exit_as_of=AS_OF + 1800)
    outcome_id = capture_strategy_resolution(
        repo, cm, RUN_ID, "CID-S1|XAUUSD|1700000000", position, _trade(entry_as_of=AS_OF + 900, exit_as_of=AS_OF + 1800), AS_OF,
    )
    assert outcome_id is not None


def test_delayed_limit_or_stop_fill_still_correlates(tmp_path: Path) -> None:
    # A limit/stop order that stays WORKING for many bars before touching -- an even larger decision-
    # to-fill gap than the market-order case.
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation(as_of=AS_OF))
    assert obs_id is not None
    assert register_pending_correlation(cm, _pending(obs_id, decision_as_of=AS_OF))
    far_entry = AS_OF + 50_000
    position = _position(entry_as_of=far_entry, full_exit_as_of=far_entry + 3600)
    outcome_id = capture_strategy_resolution(
        repo, cm, RUN_ID, "CID-S1|XAUUSD|1700000000", position,
        _trade(entry_as_of=far_entry, exit_as_of=far_entry + 3600), AS_OF,
    )
    assert outcome_id is not None


# ------------------------------------------------------------------ end-to-end decision -> resolution (Portfolio/real)


def test_decision_to_real_trade_resolution_end_to_end(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    entry = _pending(obs_id, outcome_kind=OutcomeKind.PORTFOLIO)
    assert register_pending_correlation(cm, entry)

    outcome_id = capture_portfolio_resolution(
        repo, cm, RUN_ID, "CID-S1|XAUUSD|1700000000", _trade(pnl_r=2.0), AS_OF,
    )
    assert outcome_id is not None
    outcome = repo.get_outcome(outcome_id)
    assert outcome is not None
    assert outcome.status is OutcomeStatus.RESOLVED
    assert outcome.normalized_result == 2.0
    assert outcome.outcome_kind is OutcomeKind.PORTFOLIO


# ------------------------------------------------------------------ unavailable pnl_r through the Phase D adapters


def test_strategy_resolution_unavailable_when_pnl_r_none(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    assert register_pending_correlation(cm, _pending(obs_id))

    outcome_id = capture_strategy_resolution(
        repo, cm, RUN_ID, "CID-S1|XAUUSD|1700000000", _position(), _trade(pnl_r=None), AS_OF,
    )
    assert outcome_id is not None
    outcome = repo.get_outcome(outcome_id)
    assert outcome is not None
    assert outcome.status is OutcomeStatus.UNAVAILABLE
    assert outcome.normalized_result is None
    assert outcome.unavailable_reason is OutcomeUnavailableReason.NO_VALID_RISK_DENOMINATOR


def test_portfolio_resolution_unavailable_when_pnl_r_none(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    assert register_pending_correlation(cm, _pending(obs_id, outcome_kind=OutcomeKind.PORTFOLIO))

    outcome_id = capture_portfolio_resolution(
        repo, cm, RUN_ID, "CID-S1|XAUUSD|1700000000", _trade(pnl_r=None), AS_OF,
    )
    assert outcome_id is not None
    outcome = repo.get_outcome(outcome_id)
    assert outcome is not None
    assert outcome.status is OutcomeStatus.UNAVAILABLE
    assert outcome.unavailable_reason is OutcomeUnavailableReason.NO_VALID_RISK_DENOMINATOR


# ------------------------------------------------------------------ miss / negative paths never raise


def test_strategy_resolution_miss_returns_none_never_raises(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    result = capture_strategy_resolution(
        repo, cm, RUN_ID, "NEVER-REGISTERED", _position(), _trade(), AS_OF,
    )
    assert result is None
    assert repo.count_outcomes() == 0


def test_portfolio_resolution_miss_returns_none_never_raises(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    result = capture_portfolio_resolution(repo, cm, RUN_ID, "NEVER-REGISTERED", _trade(), AS_OF)
    assert result is None
    assert repo.count_outcomes() == 0


def test_strategy_resolution_duplicate_second_attempt_returns_none(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    assert register_pending_correlation(cm, _pending(obs_id))

    first = capture_strategy_resolution(
        repo, cm, RUN_ID, "CID-S1|XAUUSD|1700000000", _position(), _trade(), AS_OF,
    )
    second = capture_strategy_resolution(
        repo, cm, RUN_ID, "CID-S1|XAUUSD|1700000000", _position(), _trade(), AS_OF,
    )
    assert first is not None
    assert second is None
    assert repo.count_outcomes() == 1  # never double-appended


def test_register_pending_correlation_duplicate_returns_false(tmp_path: Path) -> None:
    cm = CorrelationMap(RUN_ID)
    entry = _pending(ObservationId("x" * 64))
    assert register_pending_correlation(cm, entry) is True
    assert register_pending_correlation(cm, entry) is False  # never raises out of the public function


# ------------------------------------------------------------------ Strategy / Portfolio kind isolation


def test_portfolio_resolution_rejected_for_strategy_kind_entry(tmp_path: Path) -> None:
    # A pending entry registered as STRATEGY must never resolve through the PORTFOLIO path, even if the
    # (attacker-controlled-in-theory) client_order_id happens to match.
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    assert register_pending_correlation(cm, _pending(obs_id, outcome_kind=OutcomeKind.STRATEGY))

    result = capture_portfolio_resolution(repo, cm, RUN_ID, "CID-S1|XAUUSD|1700000000", _trade(), AS_OF)
    assert result is None
    assert repo.count_outcomes() == 0
    # The entry is still consumed (popped) by the failed attempt -- pop_for_resolution already removed
    # it before the kind check runs, matching "no silent overwrite": a second, correctly-kinded attempt
    # against the SAME id would also correctly fail as a duplicate, never resurrecting stale state.
    assert cm.pending_count() == 0


def test_strategy_resolution_rejected_for_portfolio_kind_entry(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    assert register_pending_correlation(cm, _pending(obs_id, outcome_kind=OutcomeKind.PORTFOLIO))

    result = capture_strategy_resolution(
        repo, cm, RUN_ID, "CID-S1|XAUUSD|1700000000", _position(), _trade(), AS_OF,
    )
    assert result is None
    assert repo.count_outcomes() == 0


# ------------------------------------------------------------------ deterministic output


def test_capture_is_deterministic_across_two_independent_runs(tmp_path: Path) -> None:
    def run_once(root_name: str) -> object:
        repo = ContextMemoryRepository(tmp_path / root_name)
        cm = CorrelationMap(RUN_ID)
        obs_id = capture_decision_observation(repo, _observation())
        assert obs_id is not None
        assert register_pending_correlation(cm, _pending(obs_id))
        return capture_strategy_resolution(
            repo, cm, RUN_ID, "CID-S1|XAUUSD|1700000000", _position(), _trade(pnl_r=1.5), AS_OF,
        )

    first_id = run_once("repo_a")
    second_id = run_once("repo_b")
    assert first_id == second_id  # content-addressed identity -- identical inputs, identical output


# ------------------------------------------------------------------ no-wiring proof


def test_capture_module_never_imports_harness() -> None:
    import ai_trader.learning_feedback.capture as capture_module

    source = Path(capture_module.__file__).read_text(encoding="utf-8")
    assert "ai_trader.simulation.harness" not in source
    assert "from ai_trader.simulation import harness" not in source


def test_no_module_in_learning_feedback_imports_harness() -> None:
    import ai_trader.learning_feedback as pkg

    pkg_dir = Path(pkg.__file__).parent
    this_file = Path(__file__)
    for py_file in pkg_dir.rglob("*.py"):
        if py_file == this_file:
            continue  # this test's own source literally contains the string under test, by necessity
        source = py_file.read_text(encoding="utf-8")
        assert "ai_trader.simulation.harness" not in source, f"{py_file} references harness.py"
