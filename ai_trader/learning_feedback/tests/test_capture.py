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
    PendingPosition,
    PositionCorrelationMap,
    capture_decision_observation,
    capture_operational_metadata,
    capture_portfolio_interim,
    capture_portfolio_resolution,
    capture_portfolio_terminal,
    capture_strategy_interim,
    capture_strategy_resolution,
    capture_strategy_terminal,
    promote_opening_fill,
    register_flip_position,
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


# =====================================================================================================
# Position-scoped correlation (Architectural Decision Package, Decisions 1-3)
# =====================================================================================================

POSITION_KEY_A = "run-2026-07-22-A:XAUUSD:1700000000:LONG"
POSITION_KEY_B = "run-2026-07-22-A:XAUUSD:1700000900:SHORT"


def _pending_position(observation_id: ObservationId, **overrides: object) -> PendingPosition:
    kwargs: dict[str, object] = {
        "run_id": RUN_ID, "position_key": POSITION_KEY_A, "strategy_id": "S1", "symbol": "XAUUSD",
        "outcome_kind": OutcomeKind.PORTFOLIO, "observation_id": observation_id,
        "cost_model_ref": COST_MODEL_REF, "decision_as_of": AS_OF,
    }
    kwargs.update(overrides)
    return PendingPosition(**kwargs)  # type: ignore[arg-type]


# ------------------------------------------------------------------ PositionCorrelationMap basics


def test_position_map_register_and_get_happy_path() -> None:
    pm = PositionCorrelationMap(RUN_ID)
    entry = _pending_position(ObservationId("x" * 64))
    pm.register(entry)
    assert pm.is_pending(POSITION_KEY_A)
    assert pm.get(POSITION_KEY_A) == entry


def test_position_map_get_does_not_retire() -> None:
    pm = PositionCorrelationMap(RUN_ID)
    pm.register(_pending_position(ObservationId("x" * 64)))
    pm.get(POSITION_KEY_A)
    pm.get(POSITION_KEY_A)
    assert pm.is_pending(POSITION_KEY_A)  # still pending after repeated peeks
    assert not pm.is_resolved(POSITION_KEY_A)


def test_position_map_retire_pops_and_marks_resolved() -> None:
    pm = PositionCorrelationMap(RUN_ID)
    pm.register(_pending_position(ObservationId("x" * 64)))
    retired = pm.retire(RUN_ID, POSITION_KEY_A)
    assert retired is not None
    assert not pm.is_pending(POSITION_KEY_A)
    assert pm.is_resolved(POSITION_KEY_A)
    assert pm.retire(RUN_ID, POSITION_KEY_A) is None  # duplicate retire is a miss, never raises


def test_position_map_unknown_key_returns_none() -> None:
    pm = PositionCorrelationMap(RUN_ID)
    assert pm.get("never-registered") is None
    assert pm.retire(RUN_ID, "never-registered") is None


def test_position_map_duplicate_registration_raises() -> None:
    pm = PositionCorrelationMap(RUN_ID)
    pm.register(_pending_position(ObservationId("x" * 64)))
    with pytest.raises(DuplicateDecisionCaptureError):
        pm.register(_pending_position(ObservationId("y" * 64)))


def test_position_map_run_mismatch_raises() -> None:
    pm = PositionCorrelationMap(RUN_ID)
    with pytest.raises(CorrelationRunMismatchError):
        pm.register(_pending_position(ObservationId("x" * 64), run_id="a-different-run"))
    pm.register(_pending_position(ObservationId("x" * 64)))
    with pytest.raises(CorrelationRunMismatchError):
        pm.retire("a-different-run", POSITION_KEY_A)


def test_position_map_drain_pending_retires_everything() -> None:
    pm = PositionCorrelationMap(RUN_ID)
    pm.register(_pending_position(ObservationId("x" * 64)))
    pm.register(_pending_position(ObservationId("y" * 64), position_key=POSITION_KEY_B))
    drained = pm.drain_pending()
    assert {e.position_key for e in drained} == {POSITION_KEY_A, POSITION_KEY_B}
    assert pm.pending_count() == 0
    assert pm.is_resolved(POSITION_KEY_A)
    assert pm.is_resolved(POSITION_KEY_B)


def test_position_map_drain_pending_is_idempotent() -> None:
    pm = PositionCorrelationMap(RUN_ID)
    pm.register(_pending_position(ObservationId("x" * 64)))
    first = pm.drain_pending()
    second = pm.drain_pending()
    assert len(first) == 1
    assert second == ()


# ------------------------------------------------------------------ promote_opening_fill


def test_promote_opening_fill_happy_path(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    pm = PositionCorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    assert register_pending_correlation(cm, _pending(obs_id, outcome_kind=OutcomeKind.PORTFOLIO))

    ok = promote_opening_fill(
        cm, pm, RUN_ID, "CID-S1|XAUUSD|1700000000", POSITION_KEY_A, OutcomeKind.PORTFOLIO,
    )
    assert ok is True
    assert pm.is_pending(POSITION_KEY_A)
    assert not cm.is_pending("CID-S1|XAUUSD|1700000000")  # decision-time candidate consumed
    entry = pm.get(POSITION_KEY_A)
    assert entry is not None
    assert entry.observation_id == obs_id
    assert entry.strategy_id == "S1"


def test_promote_opening_fill_unknown_client_order_id_returns_false() -> None:
    cm = CorrelationMap(RUN_ID)
    pm = PositionCorrelationMap(RUN_ID)
    ok = promote_opening_fill(cm, pm, RUN_ID, "NEVER-REGISTERED", POSITION_KEY_A, OutcomeKind.PORTFOLIO)
    assert ok is False
    assert pm.pending_count() == 0


def test_promote_opening_fill_kind_mismatch_returns_false(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    pm = PositionCorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    assert register_pending_correlation(cm, _pending(obs_id, outcome_kind=OutcomeKind.STRATEGY))

    ok = promote_opening_fill(
        cm, pm, RUN_ID, "CID-S1|XAUUSD|1700000000", POSITION_KEY_A, OutcomeKind.PORTFOLIO,
    )
    assert ok is False
    assert pm.pending_count() == 0


# ------------------------------------------------------------------ register_flip_position


def test_register_flip_position_derives_from_old_entry() -> None:
    pm = PositionCorrelationMap(RUN_ID)
    pm.register(_pending_position(ObservationId("x" * 64), strategy_id="S1"))

    ok = register_flip_position(pm, RUN_ID, POSITION_KEY_A, POSITION_KEY_B, "S2")
    assert ok is True
    new_entry = pm.get(POSITION_KEY_B)
    assert new_entry is not None
    assert new_entry.strategy_id == "S2"  # flipping fill's own strategy, not the old owner's
    assert new_entry.observation_id == ObservationId("x" * 64)  # same decision's Observation, carried over
    # old entry is untouched (still pending) -- register_flip_position never retires it itself
    assert pm.is_pending(POSITION_KEY_A)


def test_register_flip_position_unknown_old_key_returns_false() -> None:
    pm = PositionCorrelationMap(RUN_ID)
    ok = register_flip_position(pm, RUN_ID, "never-registered", POSITION_KEY_B, "S2")
    assert ok is False
    assert pm.pending_count() == 0


# ------------------------------------------------------------------ capture_portfolio_terminal / capture_portfolio_interim


def test_capture_portfolio_terminal_happy_path(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    pm = PositionCorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    pm.register(_pending_position(obs_id))

    outcome_id = capture_portfolio_terminal(repo, pm, RUN_ID, POSITION_KEY_A, _trade(pnl_r=1.2), AS_OF)
    assert outcome_id is not None
    outcome = repo.get_outcome(outcome_id)
    assert outcome is not None
    assert outcome.status is OutcomeStatus.RESOLVED
    assert outcome.normalized_result == 1.2
    assert not pm.is_pending(POSITION_KEY_A)
    assert pm.is_resolved(POSITION_KEY_A)


def test_capture_portfolio_terminal_duplicate_returns_none(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    pm = PositionCorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    pm.register(_pending_position(obs_id))

    first = capture_portfolio_terminal(repo, pm, RUN_ID, POSITION_KEY_A, _trade(), AS_OF)
    second = capture_portfolio_terminal(repo, pm, RUN_ID, POSITION_KEY_A, _trade(), AS_OF)
    assert first is not None
    assert second is None
    assert repo.count_outcomes() == 1


def test_capture_portfolio_terminal_kind_mismatch_returns_none(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    pm = PositionCorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    pm.register(_pending_position(obs_id, outcome_kind=OutcomeKind.STRATEGY))

    result = capture_portfolio_terminal(repo, pm, RUN_ID, POSITION_KEY_A, _trade(), AS_OF)
    assert result is None
    assert repo.count_outcomes() == 0


def test_capture_portfolio_interim_happy_path_does_not_retire(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    pm = PositionCorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    pm.register(_pending_position(obs_id))

    realization_id = capture_portfolio_interim(repo, pm, RUN_ID, POSITION_KEY_A, _trade(pnl_r=0.3), AS_OF)
    assert realization_id is not None
    realization = repo.get_interim_realization(realization_id)
    assert realization is not None
    assert realization.normalized_result == 0.3
    assert realization.position_key == POSITION_KEY_A
    assert pm.is_pending(POSITION_KEY_A)  # still open -- interim never retires


def test_capture_portfolio_interim_multiple_partials_same_position_key(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    pm = PositionCorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    pm.register(_pending_position(obs_id))

    first = capture_portfolio_interim(
        repo, pm, RUN_ID, POSITION_KEY_A, _trade(client_order_id="CO-1", qty=3.0, pnl_r=0.3), AS_OF,
    )
    second = capture_portfolio_interim(
        repo, pm, RUN_ID, POSITION_KEY_A, _trade(client_order_id="CO-2", qty=4.0, pnl_r=0.5), AS_OF,
    )
    assert first is not None
    assert second is not None
    assert first != second  # two distinct, economically different realizations, NEITHER discarded
    assert repo.count_interim_realizations() == 2
    assert pm.is_pending(POSITION_KEY_A)  # position still open after both partials


def test_capture_portfolio_interim_miss_returns_none(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    pm = PositionCorrelationMap(RUN_ID)
    result = capture_portfolio_interim(repo, pm, RUN_ID, "never-registered", _trade(), AS_OF)
    assert result is None
    assert repo.count_interim_realizations() == 0


def test_capture_portfolio_interim_kind_mismatch_returns_none(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    pm = PositionCorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    pm.register(_pending_position(obs_id, outcome_kind=OutcomeKind.STRATEGY))
    result = capture_portfolio_interim(repo, pm, RUN_ID, POSITION_KEY_A, _trade(), AS_OF)
    assert result is None


# ------------------------------------------------------------------ capture_strategy_terminal / capture_strategy_interim


def test_capture_strategy_terminal_happy_path(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    pm = PositionCorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    pm.register(_pending_position(obs_id, outcome_kind=OutcomeKind.STRATEGY))

    outcome_id = capture_strategy_terminal(
        repo, pm, RUN_ID, POSITION_KEY_A, _position(), _trade(pnl_r=1.5), AS_OF,
    )
    assert outcome_id is not None
    outcome = repo.get_outcome(outcome_id)
    assert outcome is not None
    assert outcome.outcome_kind is OutcomeKind.STRATEGY
    assert not pm.is_pending(POSITION_KEY_A)


def test_capture_strategy_interim_happy_path_does_not_retire(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    pm = PositionCorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    pm.register(_pending_position(obs_id, outcome_kind=OutcomeKind.STRATEGY))

    realization_id = capture_strategy_interim(repo, pm, RUN_ID, POSITION_KEY_A, _trade(pnl_r=0.2), AS_OF)
    assert realization_id is not None
    assert pm.is_pending(POSITION_KEY_A)


def test_capture_strategy_terminal_kind_mismatch_returns_none(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    pm = PositionCorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    pm.register(_pending_position(obs_id, outcome_kind=OutcomeKind.PORTFOLIO))
    result = capture_strategy_terminal(repo, pm, RUN_ID, POSITION_KEY_A, _position(), _trade(), AS_OF)
    assert result is None


# ------------------------------------------------------------------ end-to-end: decision -> promote -> interim -> terminal


def test_end_to_end_decision_to_multi_partial_terminal_close(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    pm = PositionCorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    assert register_pending_correlation(cm, _pending(obs_id, outcome_kind=OutcomeKind.PORTFOLIO))

    assert promote_opening_fill(
        cm, pm, RUN_ID, "CID-S1|XAUUSD|1700000000", POSITION_KEY_A, OutcomeKind.PORTFOLIO,
    )

    # two partial exits -- both captured, neither discarded, position stays open. Distinct pnl_r/
    # exit_as_of so the two InterimRealizations are genuinely different records, not an idempotent
    # duplicate of each other (they ARE different economic events, per Lifecycle Specification Finding C).
    r1 = capture_portfolio_interim(
        repo, pm, RUN_ID, POSITION_KEY_A, _trade(client_order_id="CO-1", qty=3.0, pnl_r=0.4, exit_as_of=AS_OF + 300), AS_OF,
    )
    r2 = capture_portfolio_interim(
        repo, pm, RUN_ID, POSITION_KEY_A, _trade(client_order_id="CO-2", qty=4.0, pnl_r=0.9, exit_as_of=AS_OF + 800), AS_OF,
    )
    assert r1 is not None and r2 is not None
    assert repo.count_interim_realizations() == 2
    assert repo.count_outcomes() == 0

    # final close -- brings the position to zero, produces the ONE terminal Outcome, retires the key
    final = capture_portfolio_terminal(repo, pm, RUN_ID, POSITION_KEY_A, _trade(client_order_id="CO-3", qty=3.0), AS_OF)
    assert final is not None
    assert repo.count_outcomes() == 1
    assert not pm.is_pending(POSITION_KEY_A)


def test_end_to_end_flip_closes_old_and_opens_new(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    pm = PositionCorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    assert register_pending_correlation(cm, _pending(obs_id, outcome_kind=OutcomeKind.PORTFOLIO, strategy_id="S1"))
    assert promote_opening_fill(
        cm, pm, RUN_ID, "CID-S1|XAUUSD|1700000000", POSITION_KEY_A, OutcomeKind.PORTFOLIO,
    )

    # the flip's own single fill: register the new side FIRST (per capture.py's own documented ordering),
    # using the flipping fill's own strategy (which may differ from the old owner's, per Decision 2)
    assert register_flip_position(pm, RUN_ID, POSITION_KEY_A, POSITION_KEY_B, "S2")
    # ... then resolve the old side terminally, via the ONE TradeRecord the flip's closing side produced
    old_outcome_id = capture_portfolio_terminal(repo, pm, RUN_ID, POSITION_KEY_A, _trade(strategy_id="S1"), AS_OF)
    assert old_outcome_id is not None
    assert not pm.is_pending(POSITION_KEY_A)

    # the new position is now tracked, attributed to S2, using the SAME Observation as the old decision
    assert pm.is_pending(POSITION_KEY_B)
    new_entry = pm.get(POSITION_KEY_B)
    assert new_entry is not None
    assert new_entry.strategy_id == "S2"
    assert new_entry.observation_id == obs_id

    # it later closes independently, on its own eventual terminal fill -- observation_as_of stays AS_OF
    # (the SAME Observation carried over from the original decision, per Decision 2), only the trade's
    # own exit_as_of moves forward in time.
    new_outcome_id = capture_portfolio_terminal(
        repo, pm, RUN_ID, POSITION_KEY_B,
        _trade(strategy_id="S2", client_order_id="CO-LATER", exit_as_of=AS_OF + 5000), AS_OF,
    )
    assert new_outcome_id is not None
    assert new_outcome_id != old_outcome_id
    assert repo.count_outcomes() == 2


def test_hold_and_mark_end_of_run_never_fabricates_an_outcome(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    pm = PositionCorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    assert register_pending_correlation(cm, _pending(obs_id, outcome_kind=OutcomeKind.PORTFOLIO))
    assert promote_opening_fill(
        cm, pm, RUN_ID, "CID-S1|XAUUSD|1700000000", POSITION_KEY_A, OutcomeKind.PORTFOLIO,
    )

    # end of run: position never closed (HOLD_AND_MARK) -- drain, never fabricate an Outcome
    drained = pm.drain_pending()
    assert len(drained) == 1
    assert drained[0].position_key == POSITION_KEY_A
    assert repo.count_outcomes() == 0
    assert repo.count_interim_realizations() == 0
    assert pm.pending_count() == 0


# =====================================================================================================
# CorrelationMap.discard / drain_pending -- Sprint 2 Blocker 3 (full lifecycle/cleanup)
# =====================================================================================================


def test_correlation_map_discard_retires_without_producing_an_outcome() -> None:
    cm = CorrelationMap(RUN_ID)
    obs_id = ObservationId("x" * 64)
    entry = _pending(obs_id)
    cm.register_decision(entry)
    discarded = cm.discard(RUN_ID, "CID-S1|XAUUSD|1700000000")
    assert discarded == entry
    assert not cm.is_pending("CID-S1|XAUUSD|1700000000")
    assert cm.is_resolved("CID-S1|XAUUSD|1700000000")


def test_correlation_map_discard_unknown_key_returns_none() -> None:
    cm = CorrelationMap(RUN_ID)
    assert cm.discard(RUN_ID, "never-registered") is None


def test_correlation_map_discard_retires_every_bracket_alias() -> None:
    cm = CorrelationMap(RUN_ID)
    obs_id = ObservationId("x" * 64)
    entry = _pending(
        obs_id,
        client_order_ids=("CID-S1|XAUUSD|1700000000", "CID-S1|XAUUSD|1700000000-TP", "CID-S1|XAUUSD|1700000000-SL"),
    )
    cm.register_decision(entry)
    cm.discard(RUN_ID, "CID-S1|XAUUSD|1700000000-TP")
    assert not cm.is_pending("CID-S1|XAUUSD|1700000000")
    assert not cm.is_pending("CID-S1|XAUUSD|1700000000-SL")
    assert cm.is_resolved("CID-S1|XAUUSD|1700000000")
    assert cm.is_resolved("CID-S1|XAUUSD|1700000000-SL")


def test_correlation_map_drain_pending_empties_and_retires_everything() -> None:
    cm = CorrelationMap(RUN_ID)
    obs_id = ObservationId("x" * 64)
    cm.register_decision(_pending(obs_id, client_order_ids=("CO-A",)))
    cm.register_decision(_pending(obs_id, client_order_ids=("CO-B",)))
    drained = cm.drain_pending()
    assert len(drained) == 2
    assert cm.pending_count() == 0
    assert cm.is_resolved("CO-A")
    assert cm.is_resolved("CO-B")


def test_correlation_map_drain_pending_is_idempotent() -> None:
    cm = CorrelationMap(RUN_ID)
    obs_id = ObservationId("x" * 64)
    cm.register_decision(_pending(obs_id, client_order_ids=("CO-A",)))
    first = cm.drain_pending()
    second = cm.drain_pending()
    assert len(first) == 1
    assert second == ()


def test_correlation_map_drain_pending_counts_bracket_entry_once() -> None:
    cm = CorrelationMap(RUN_ID)
    obs_id = ObservationId("x" * 64)
    cm.register_decision(_pending(obs_id, client_order_ids=("CO-A", "CO-A-TP", "CO-A-SL")))
    drained = cm.drain_pending()
    assert len(drained) == 1  # one PendingCapture, not one per alias
    assert cm.pending_count() == 0


# =====================================================================================================
# PositionOutcome accumulation -- Sprint 2 Blocker 2 (CEO-ratified, additive)
# =====================================================================================================


def test_position_map_accumulate_appends_partial_without_retiring() -> None:
    pm = PositionCorrelationMap(RUN_ID)
    pm.register(_pending_position(ObservationId("x" * 64)))
    updated = pm.accumulate(RUN_ID, POSITION_KEY_A, _trade(client_order_id="CO-1"))
    assert updated is not None
    assert len(updated.accumulated_partials) == 1
    assert pm.is_pending(POSITION_KEY_A)  # still open -- accumulate never retires


def test_position_map_accumulate_records_interim_realization_id() -> None:
    pm = PositionCorrelationMap(RUN_ID)
    pm.register(_pending_position(ObservationId("x" * 64)))
    from ai_trader.context_memory.contracts import InterimRealizationId

    updated = pm.accumulate(
        RUN_ID, POSITION_KEY_A, _trade(client_order_id="CO-1"),
        interim_realization_id=InterimRealizationId("i" * 64),
    )
    assert updated is not None
    assert updated.interim_realization_ids == (InterimRealizationId("i" * 64),)


def test_position_map_accumulate_unknown_key_returns_none() -> None:
    pm = PositionCorrelationMap(RUN_ID)
    assert pm.accumulate(RUN_ID, "never-registered", _trade()) is None


def test_position_map_accumulate_run_mismatch_raises() -> None:
    pm = PositionCorrelationMap(RUN_ID)
    pm.register(_pending_position(ObservationId("x" * 64)))
    with pytest.raises(CorrelationRunMismatchError):
        pm.accumulate("a-different-run", POSITION_KEY_A, _trade())


def test_end_to_end_multi_partial_position_produces_one_position_outcome(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    pm = PositionCorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    assert register_pending_correlation(cm, _pending(obs_id, outcome_kind=OutcomeKind.PORTFOLIO))
    assert promote_opening_fill(
        cm, pm, RUN_ID, "CID-S1|XAUUSD|1700000000", POSITION_KEY_A, OutcomeKind.PORTFOLIO,
    )

    r1 = capture_portfolio_interim(
        repo, pm, RUN_ID, POSITION_KEY_A,
        _trade(client_order_id="CO-1", qty=3.0, pnl_r=0.4, exit_as_of=AS_OF + 300, gross_pnl=15.0, net_pnl=14.0, fees=1.0),
        AS_OF,
    )
    r2 = capture_portfolio_interim(
        repo, pm, RUN_ID, POSITION_KEY_A,
        _trade(client_order_id="CO-2", qty=4.0, pnl_r=0.9, exit_as_of=AS_OF + 800, gross_pnl=40.0, net_pnl=38.0, fees=2.0),
        AS_OF,
    )
    assert r1 is not None and r2 is not None

    terminal_trade = _trade(
        client_order_id="CO-3", qty=3.0, pnl_r=0.6, exit_as_of=AS_OF + 1200, gross_pnl=25.0, net_pnl=23.0, fees=2.0,
    )
    outcome_id = capture_portfolio_terminal(repo, pm, RUN_ID, POSITION_KEY_A, terminal_trade, AS_OF)
    assert outcome_id is not None

    # exactly ONE terminal Outcome (unchanged return contract) and exactly ONE PositionOutcome
    assert repo.count_outcomes() == 1
    assert repo.count_position_outcomes() == 1
    assert repo.count_interim_realizations() == 2

    position_outcomes = list(repo.iter_position_outcomes())
    assert len(position_outcomes) == 1
    po = position_outcomes[0]
    assert po.position_key == POSITION_KEY_A
    assert po.total_qty_closed == 10.0  # 3 + 4 + 3
    assert po.total_net_pnl == pytest.approx(14.0 + 38.0 + 23.0)
    assert po.total_gross_pnl == pytest.approx(15.0 + 40.0 + 25.0)
    assert po.total_costs == pytest.approx(1.0 + 2.0 + 2.0)
    assert po.terminal_outcome_id == outcome_id
    assert len(po.constituent_interim_realization_ids) == 2  # both partials, not the terminal one
    assert po.terminal_as_of == terminal_trade.exit_as_of
    assert not pm.is_pending(POSITION_KEY_A)


def test_single_partial_position_outcome_matches_naive_terminal_close(tmp_path: Path) -> None:
    # Continuity proof: a position closed by exactly ONE fill (no interim partials at all) must produce
    # a PositionOutcome whose aggregate is identical to that single fill's own raw economics.
    repo = _repo(tmp_path)
    cm = CorrelationMap(RUN_ID)
    pm = PositionCorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    assert register_pending_correlation(cm, _pending(obs_id, outcome_kind=OutcomeKind.PORTFOLIO))
    assert promote_opening_fill(
        cm, pm, RUN_ID, "CID-S1|XAUUSD|1700000000", POSITION_KEY_A, OutcomeKind.PORTFOLIO,
    )

    trade = _trade(pnl_r=1.2, qty=5.0, gross_pnl=50.0, net_pnl=47.0, fees=3.0)
    outcome_id = capture_portfolio_terminal(repo, pm, RUN_ID, POSITION_KEY_A, trade, AS_OF)
    assert outcome_id is not None

    po = list(repo.iter_position_outcomes())[0]
    assert po.total_qty_closed == trade.qty
    assert po.total_gross_pnl == trade.gross_pnl
    assert po.total_net_pnl == trade.net_pnl
    assert po.total_costs == trade.fees
    assert po.constituent_interim_realization_ids == ()


def test_strategy_side_also_produces_position_outcome(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    pm = PositionCorrelationMap(RUN_ID)
    obs_id = capture_decision_observation(repo, _observation())
    assert obs_id is not None
    pm.register(_pending_position(obs_id, outcome_kind=OutcomeKind.STRATEGY))

    trade = _trade(pnl_r=0.8)
    outcome_id = capture_strategy_terminal(repo, pm, RUN_ID, POSITION_KEY_A, _position(), trade, AS_OF)
    assert outcome_id is not None
    assert repo.count_position_outcomes() == 1
    po = list(repo.iter_position_outcomes())[0]
    assert po.outcome_kind is OutcomeKind.STRATEGY
