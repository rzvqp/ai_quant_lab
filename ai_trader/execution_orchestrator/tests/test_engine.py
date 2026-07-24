from __future__ import annotations

from pathlib import Path

from ai_trader.execution_engine.types import OrderState
from ai_trader.execution_orchestrator.engine import correlation_id_for, orchestrate
from ai_trader.execution_orchestrator.tests._fixtures import make_candidate, make_deps, make_market_context
from ai_trader.execution_orchestrator.types import ExecutionMode, OrchestratorConfig


def _no_recognition_config(**overrides: object) -> OrchestratorConfig:
    kwargs: dict[str, object] = {"recognition_pattern_id": None}
    kwargs.update(overrides)
    return OrchestratorConfig(**kwargs)  # type: ignore[arg-type]


def test_full_pipeline_reaches_acknowledged_order(tmp_path: Path) -> None:
    candidate = make_candidate()
    result = orchestrate(candidate, make_market_context(), make_deps(tmp_path), config=_no_recognition_config())
    assert result.approved is True
    assert result.order_result is not None
    assert result.order_result.state is OrderState.ACKNOWLEDGED
    assert result.confidence is not None
    assert result.risk_decision is not None
    assert result.risk_decision.approved is True
    assert result.portfolio_decision is not None
    assert result.portfolio_decision.approved is True


def test_correlation_id_is_deterministic_and_propagated(tmp_path: Path) -> None:
    candidate = make_candidate()
    expected = correlation_id_for(candidate)
    result = orchestrate(candidate, make_market_context(), make_deps(tmp_path), config=_no_recognition_config())
    assert result.correlation_id == expected
    assert result.order_result is not None


def test_emergency_stop_short_circuits_before_any_stage(tmp_path: Path) -> None:
    candidate = make_candidate()
    result = orchestrate(
        candidate, make_market_context(), make_deps(tmp_path), emergency_stop=True, config=_no_recognition_config(),
    )
    assert result.approved is False
    assert "EMERGENCY_STOP_ACTIVE" in result.reason_codes
    assert result.context is None


def test_live_mode_is_refused_unconditionally(tmp_path: Path) -> None:
    candidate = make_candidate()
    result = orchestrate(
        candidate, make_market_context(), make_deps(tmp_path), mode=ExecutionMode.LIVE, config=_no_recognition_config(),
    )
    assert result.approved is False
    assert "LIVE_TRADING_NOT_AUTHORIZED" in result.reason_codes
    assert result.context is None
    assert result.order_result is None


def test_demo_mode_refuses_non_demo_account(tmp_path: Path) -> None:
    from ai_trader.execution_orchestrator.tests._fixtures import make_account

    deps = make_deps(tmp_path, account=make_account(is_demo=False))
    candidate = make_candidate()
    result = orchestrate(candidate, make_market_context(), deps, mode=ExecutionMode.DEMO, config=_no_recognition_config())
    assert result.approved is False
    assert "NON_DEMO_ACCOUNT_REFUSED" in result.reason_codes


def test_demo_mode_still_never_reports_a_non_dry_run_order(tmp_path: Path) -> None:
    """Disclosed limitation: DEMO is functionally identical to DRY_RUN this phase -- Order Manager
    (Phase 3) is structurally dry-run-only."""
    candidate = make_candidate()
    result = orchestrate(
        candidate, make_market_context(), make_deps(tmp_path), mode=ExecutionMode.DEMO, config=_no_recognition_config(),
    )
    assert result.approved is True
    assert result.order_result is not None
    assert result.order_result.dry_run is True


def test_stale_candidate_denied() -> None:
    from pathlib import Path as _Path
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        candidate = make_candidate(as_of=1_700_010_000)  # 10,000s after market_context's own as_of
        result = orchestrate(candidate, make_market_context(), make_deps(_Path(tmp)), config=_no_recognition_config())
        assert result.approved is False
        assert "STALE_CANDIDATE" in result.reason_codes


def test_idempotent_repeated_call_never_double_submits(tmp_path: Path) -> None:
    candidate = make_candidate()
    deps = make_deps(tmp_path)  # same ledger/journal reused across both calls
    first = orchestrate(candidate, make_market_context(), deps, config=_no_recognition_config())
    second = orchestrate(candidate, make_market_context(), deps, config=_no_recognition_config())
    assert first.order_result is not None and second.order_result is not None
    assert first.order_result.client_order_id == second.order_result.client_order_id
    assert len(deps.ledger) == 1


def test_calculation_trace_never_empty_on_any_path(tmp_path: Path) -> None:
    candidate = make_candidate()
    result = orchestrate(
        candidate, make_market_context(), make_deps(tmp_path), emergency_stop=True, config=_no_recognition_config(),
    )
    assert len(result.calculation_trace) >= 1
