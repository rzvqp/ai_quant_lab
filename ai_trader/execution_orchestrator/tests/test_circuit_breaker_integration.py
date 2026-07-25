"""The exact Risk Audit #1 scenario, at the orchestrator level: a loss/drawdown breach must suspend
trading for the REST of the day, not just deny the one proposal that triggered it. Two sequential
`orchestrate()` calls sharing a threaded `TradingCircuitState`; the second call's own instantaneous
portfolio state would, on its own, pass every existing check (drawdown recovered below the BREACH
threshold) -- it must still be denied, because it has not recovered below the tighter RESET threshold.
A caller that never opts into circuit tracking (the default, every pre-existing test in this package)
must see byte-identical behavior -- proven separately by the full existing suite staying green."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_trader.execution_orchestrator.engine import orchestrate
from ai_trader.execution_orchestrator.tests._fixtures import make_candidate, make_deps, make_market_context
from ai_trader.execution_orchestrator.types import OrchestratorConfig
from ai_trader.risk_manager.types import EngineState, PortfolioState
from ai_trader.risk_manager_live.types import READY_CIRCUIT_STATE

AS_OF = 1_700_000_000


def _no_recognition_config() -> OrchestratorConfig:
    return OrchestratorConfig(recognition_pattern_id=None)


@dataclass(frozen=True, slots=True)
class _FakeSource:
    portfolio: PortfolioState

    def current_portfolio_state(self) -> PortfolioState:
        return self.portfolio


def test_suspension_persists_across_calls_even_when_the_second_call_looks_fine_alone(tmp_path: Path) -> None:
    equity_hwm = 200_000.0

    # Call 1: a genuine drawdown breach (15% > the 12% default max_drawdown_pct).
    breached_portfolio = PortfolioState(
        as_of=AS_OF, equity=equity_hwm * (1 - 0.15), equity_high_water_mark=equity_hwm,
    )
    deps1 = make_deps(tmp_path, portfolio=breached_portfolio)
    result1 = orchestrate(
        make_candidate(as_of=AS_OF), make_market_context(as_of=AS_OF), deps1,
        config=_no_recognition_config(), circuit_state=READY_CIRCUIT_STATE, pnl_source=_FakeSource(breached_portfolio),
    )
    assert result1.approved is False
    assert "TRADING_SUSPENDED" in result1.reason_codes
    assert result1.circuit_state_after is not None
    assert result1.circuit_state_after.state is EngineState.SUSPENDED

    # Call 2, one hour later: drawdown has improved to 10% -- BELOW the 12% breach line, so a system
    # with no persistent memory would re-approve the risk check on this portfolio alone. It is still
    # ABOVE the 8% reset line, so the circuit must stay suspended.
    partially_recovered_portfolio = PortfolioState(
        as_of=AS_OF + 3600, equity=equity_hwm * (1 - 0.10), equity_high_water_mark=equity_hwm,
    )
    deps2 = make_deps(tmp_path, portfolio=partially_recovered_portfolio)
    result2 = orchestrate(
        make_candidate(as_of=AS_OF + 3600), make_market_context(as_of=AS_OF + 3600), deps2,
        config=_no_recognition_config(), circuit_state=result1.circuit_state_after,
        pnl_source=_FakeSource(partially_recovered_portfolio),
    )
    assert result2.approved is False
    assert "TRADING_SUSPENDED" in result2.reason_codes
    assert result2.circuit_state_after is not None
    assert result2.circuit_state_after.state is EngineState.SUSPENDED
    assert result2.context is None  # short-circuited before context engine even ran, like emergency_stop


def test_circuit_clears_once_fully_recovered_and_the_next_call_proceeds(tmp_path: Path) -> None:
    equity_hwm = 200_000.0
    breached_portfolio = PortfolioState(
        as_of=AS_OF, equity=equity_hwm * (1 - 0.15), equity_high_water_mark=equity_hwm,
    )
    result1 = orchestrate(
        make_candidate(as_of=AS_OF), make_market_context(as_of=AS_OF), make_deps(tmp_path, portfolio=breached_portfolio),
        config=_no_recognition_config(), circuit_state=READY_CIRCUIT_STATE, pnl_source=_FakeSource(breached_portfolio),
    )
    assert result1.circuit_state_after is not None and result1.circuit_state_after.state is EngineState.SUSPENDED

    fully_recovered_portfolio = PortfolioState(
        as_of=AS_OF + 3600, equity=equity_hwm * (1 - 0.01), equity_high_water_mark=equity_hwm,
    )
    result2 = orchestrate(
        make_candidate(as_of=AS_OF + 3600), make_market_context(as_of=AS_OF + 3600),
        make_deps(tmp_path, portfolio=fully_recovered_portfolio), config=_no_recognition_config(),
        circuit_state=result1.circuit_state_after, pnl_source=_FakeSource(fully_recovered_portfolio),
    )
    assert result2.circuit_state_after is not None
    assert result2.circuit_state_after.state is EngineState.READY
    assert result2.approved is True  # the circuit no longer blocks it; reaches the normal happy path


def test_caller_that_does_not_opt_in_sees_unchanged_behavior(tmp_path: Path) -> None:
    """No `circuit_state`/`pnl_source` supplied -- the exact pre-fix call shape. Must behave
    byte-identically to every pre-existing test in this package (proven broadly by the rest of the
    suite; this test pins the specific claim that `circuit_state_after` stays `None`)."""
    result = orchestrate(
        make_candidate(), make_market_context(), make_deps(tmp_path), config=_no_recognition_config(),
    )
    assert result.approved is True
    assert result.circuit_state_after is None
