"""Tests for `evaluate_circuit_state` (Risk Audit #1 fix): a real breach must persist as a suspension
across calls, not just deny the one proposal in front of it; recovery must require the same hysteresis
gap the frozen `risk_manager.engine` already established for drawdown; `emergency_stop_requested` must
persist too, and never auto-clear."""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.risk_manager.types import EngineState, PortfolioState
from ai_trader.risk_manager_live.circuit_breaker import evaluate_circuit_state
from ai_trader.risk_manager_live.reason_codes import CIRCUIT_EMERGENCY_STOP_REQUESTED
from ai_trader.risk_manager_live.tests._fixtures import make_config, make_portfolio
from ai_trader.risk_manager_live.types import READY_CIRCUIT_STATE, TradingCircuitState

AS_OF = 1_700_000_000


@dataclass(frozen=True, slots=True)
class _FakeSource:
    portfolio: PortfolioState

    def current_portfolio_state(self) -> PortfolioState:
        return self.portfolio


def test_ready_state_with_no_breach_stays_ready() -> None:
    source = _FakeSource(make_portfolio())
    result = evaluate_circuit_state(READY_CIRCUIT_STATE, source, make_config(), AS_OF)
    assert result.state is EngineState.READY
    assert result.reason_code is None


def test_daily_loss_breach_transitions_to_suspended() -> None:
    config = make_config()
    breached = make_portfolio(realized_pnl_pct_daily=-config.loss_drawdown.max_daily_loss_pct - 0.01)
    result = evaluate_circuit_state(READY_CIRCUIT_STATE, _FakeSource(breached), config, AS_OF)
    assert result.state is EngineState.SUSPENDED
    assert result.reason_code == "LOSS_DAILY"
    assert result.since == AS_OF


def test_weekly_loss_breach_transitions_to_suspended() -> None:
    config = make_config()
    breached = make_portfolio(realized_pnl_pct_weekly=-config.loss_drawdown.max_weekly_loss_pct - 0.01)
    result = evaluate_circuit_state(READY_CIRCUIT_STATE, _FakeSource(breached), config, AS_OF)
    assert result.state is EngineState.SUSPENDED
    assert result.reason_code == "LOSS_WEEKLY"


def test_drawdown_breach_transitions_to_suspended() -> None:
    config = make_config()
    equity_hwm = 200_000.0
    breached = make_portfolio(
        equity_high_water_mark=equity_hwm,
        equity=equity_hwm * (1 - config.loss_drawdown.max_drawdown_pct - 0.01),
    )
    result = evaluate_circuit_state(READY_CIRCUIT_STATE, _FakeSource(breached), config, AS_OF)
    assert result.state is EngineState.SUSPENDED
    assert result.reason_code == "DRAWDOWN_MAX"


def test_suspended_state_persists_when_only_the_original_trigger_recovers() -> None:
    """The exact Risk Audit #1 scenario: a daily-loss breach suspends the account; by the next call,
    daily P&L alone has recovered above the breach threshold, but drawdown is still above the RESET
    threshold (0.08) even though it's below the BREACH threshold (0.12) -- a system with no persistent
    memory would re-approve here, since daily_pnl_pct alone now looks fine. It must not."""
    config = make_config()
    suspended = TradingCircuitState(state=EngineState.SUSPENDED, reason_code="LOSS_DAILY", since=AS_OF)
    equity_hwm = 200_000.0
    partially_recovered = make_portfolio(
        realized_pnl_pct_daily=-0.001,  # daily loss alone now looks fine
        equity_high_water_mark=equity_hwm,
        equity=equity_hwm * (1 - 0.10),  # drawdown 10%: below the 12% breach line, still above the 8% reset line
    )
    result = evaluate_circuit_state(suspended, _FakeSource(partially_recovered), config, AS_OF + 3600)
    assert result.state is EngineState.SUSPENDED
    assert result.reason_code == "LOSS_DAILY"
    assert result.since == AS_OF  # unchanged -- still the ORIGINAL breach, not silently re-stamped


def test_fully_recovered_clears_suspension() -> None:
    config = make_config()
    suspended = TradingCircuitState(state=EngineState.SUSPENDED, reason_code="LOSS_DAILY", since=AS_OF)
    equity_hwm = 200_000.0
    fully_recovered = make_portfolio(
        realized_pnl_pct_daily=-0.001, realized_pnl_pct_weekly=-0.001,
        equity_high_water_mark=equity_hwm, equity=equity_hwm * (1 - 0.01),
    )
    result = evaluate_circuit_state(suspended, _FakeSource(fully_recovered), config, AS_OF + 3600)
    assert result.state is EngineState.READY
    assert result.reason_code is None
    assert result.since is None


def test_emergency_stop_requested_overrides_everything() -> None:
    result = evaluate_circuit_state(
        READY_CIRCUIT_STATE, _FakeSource(make_portfolio()), make_config(), AS_OF,
        emergency_stop_requested=True,
    )
    assert result.state is EngineState.EMERGENCY_STOP
    assert result.reason_code == CIRCUIT_EMERGENCY_STOP_REQUESTED
    assert result.since == AS_OF


def test_emergency_stop_is_sticky_and_never_auto_clears() -> None:
    emergency = TradingCircuitState(
        state=EngineState.EMERGENCY_STOP, reason_code=CIRCUIT_EMERGENCY_STOP_REQUESTED, since=AS_OF,
    )
    healthy = make_portfolio()  # no breach anywhere
    result = evaluate_circuit_state(emergency, _FakeSource(healthy), make_config(), AS_OF + 3600)
    assert result.state is EngineState.EMERGENCY_STOP
    assert result.since == AS_OF  # unchanged
