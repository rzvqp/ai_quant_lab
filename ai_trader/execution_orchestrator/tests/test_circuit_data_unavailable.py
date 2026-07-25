"""Step 2 of #2 (2026-07-25): a `PortfolioStateSource` that cannot supply complete data must deny the
run, never be silently treated as "no losses" (Risk Audit #1's own point, now enforced at the
orchestrator boundary where the injected source is actually called)."""

from __future__ import annotations

from pathlib import Path

from ai_trader.execution_orchestrator.engine import orchestrate
from ai_trader.execution_orchestrator.tests._fixtures import make_candidate, make_deps, make_market_context
from ai_trader.execution_orchestrator.types import OrchestratorConfig
from ai_trader.risk_manager.types import PortfolioState
from ai_trader.risk_manager_live.types import READY_CIRCUIT_STATE


def _no_recognition_config() -> OrchestratorConfig:
    return OrchestratorConfig(recognition_pattern_id=None)


class _RaisingSource:
    def current_portfolio_state(self) -> PortfolioState:
        raise RuntimeError("account/position/deal data incomplete")


def test_data_unavailable_from_pnl_source_denies_the_run(tmp_path: Path) -> None:
    result = orchestrate(
        make_candidate(), make_market_context(), make_deps(tmp_path), config=_no_recognition_config(),
        circuit_state=READY_CIRCUIT_STATE, pnl_source=_RaisingSource(),
    )
    assert result.approved is False
    assert "CIRCUIT_DATA_UNAVAILABLE" in result.reason_codes
    assert result.context is None  # short-circuited before context engine even ran


def test_data_unavailable_leaves_circuit_state_unchanged_for_the_caller_to_retry(tmp_path: Path) -> None:
    result = orchestrate(
        make_candidate(), make_market_context(), make_deps(tmp_path), config=_no_recognition_config(),
        circuit_state=READY_CIRCUIT_STATE, pnl_source=_RaisingSource(),
    )
    assert result.circuit_state_after == READY_CIRCUIT_STATE
