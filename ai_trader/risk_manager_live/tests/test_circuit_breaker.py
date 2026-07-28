"""Tests for `evaluate_circuit_state` (Risk Audit #1 fix): a real breach must persist as a suspension
across calls, not just deny the one proposal in front of it; recovery must require the same hysteresis
gap the frozen `risk_manager.engine` already established for drawdown; `emergency_stop_requested` must
persist too, and never auto-clear."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from ai_trader.risk_manager.types import EngineState, PortfolioState
from ai_trader.risk_manager_live.circuit_breaker import (
    emergency_stop_resets,
    evaluate_circuit_state,
    load_persisted_circuit_state,
    persist_circuit_state,
    reset_emergency_stop,
)
from ai_trader.risk_manager_live.reason_codes import CIRCUIT_EMERGENCY_STOP_REQUESTED
from ai_trader.risk_manager_live.tests._fixtures import make_config, make_portfolio
from ai_trader.risk_manager_live.types import READY_CIRCUIT_STATE, TradingCircuitState
from ai_trader.persistent_state.store import SqliteStateStore

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


# -- Mandate 3, Element 2 (2026-07-27): circuit-state persistence + the ONLY EMERGENCY_STOP reset path --


def test_load_returns_ready_when_nothing_has_ever_been_persisted() -> None:
    store = SqliteStateStore(":memory:")
    assert load_persisted_circuit_state(store) == READY_CIRCUIT_STATE


def test_persist_then_load_round_trips() -> None:
    store = SqliteStateStore(":memory:")
    suspended = TradingCircuitState(state=EngineState.SUSPENDED, reason_code="LOSS_DAILY", since=AS_OF)
    persist_circuit_state(store, suspended, AS_OF)
    assert load_persisted_circuit_state(store) == suspended


def test_load_returns_the_most_recently_persisted_state() -> None:
    store = SqliteStateStore(":memory:")
    persist_circuit_state(
        store, TradingCircuitState(state=EngineState.SUSPENDED, reason_code="LOSS_DAILY", since=AS_OF), AS_OF,
    )
    persist_circuit_state(store, READY_CIRCUIT_STATE, AS_OF + 3600)
    assert load_persisted_circuit_state(store) == READY_CIRCUIT_STATE


def test_suspended_state_survives_a_simulated_restart(tmp_path: Path) -> None:
    """The CEO's own first required test, verbatim: process suspended, restart, circuit breaker still
    active. A brand-new `SqliteStateStore` instance, same file -- not the same object -- proves genuine
    cross-process persistence, not one connection's own lifetime."""
    db_path = tmp_path / "state.db"
    store_before_restart = SqliteStateStore(db_path)
    suspended = TradingCircuitState(state=EngineState.SUSPENDED, reason_code="DRAWDOWN_MAX", since=AS_OF)
    persist_circuit_state(store_before_restart, suspended, AS_OF)
    store_before_restart.close()

    store_after_restart = SqliteStateStore(db_path)
    recovered = load_persisted_circuit_state(store_after_restart)

    assert recovered.state is EngineState.SUSPENDED
    assert recovered.reason_code == "DRAWDOWN_MAX"
    assert recovered.since == AS_OF


def test_emergency_stop_survives_a_simulated_restart_without_any_automatic_reset(tmp_path: Path) -> None:
    """The CEO's own explicit warning, restated: persistence must not become a back door through which
    a restart silently clears EMERGENCY_STOP. Loading the persisted state after restart must return
    EMERGENCY_STOP unchanged -- nothing about loading it triggers a reset."""
    db_path = tmp_path / "state.db"
    store_before_restart = SqliteStateStore(db_path)
    emergency = TradingCircuitState(
        state=EngineState.EMERGENCY_STOP, reason_code=CIRCUIT_EMERGENCY_STOP_REQUESTED, since=AS_OF,
    )
    persist_circuit_state(store_before_restart, emergency, AS_OF)
    store_before_restart.close()

    store_after_restart = SqliteStateStore(db_path)
    recovered = load_persisted_circuit_state(store_after_restart)

    assert recovered.state is EngineState.EMERGENCY_STOP
    assert recovered.reason_code == CIRCUIT_EMERGENCY_STOP_REQUESTED
    assert emergency_stop_resets(store_after_restart) == ()  # loading is not resetting


def test_reset_emergency_stop_requires_the_persisted_state_to_actually_be_emergency_stop() -> None:
    store = SqliteStateStore(":memory:")
    persist_circuit_state(store, READY_CIRCUIT_STATE, AS_OF)
    with pytest.raises(ValueError):
        reset_emergency_stop(store, reason="test", as_of=AS_OF + 100)


def test_reset_emergency_stop_requires_a_non_empty_reason() -> None:
    store = SqliteStateStore(":memory:")
    emergency = TradingCircuitState(
        state=EngineState.EMERGENCY_STOP, reason_code=CIRCUIT_EMERGENCY_STOP_REQUESTED, since=AS_OF,
    )
    persist_circuit_state(store, emergency, AS_OF)
    with pytest.raises(ValueError):
        reset_emergency_stop(store, reason="", as_of=AS_OF + 100)


def test_reset_emergency_stop_transitions_to_ready_and_persists_it() -> None:
    """The CEO's own second required test, verbatim: explicit reset, reason recorded, then the circuit
    breaker is inactive."""
    store = SqliteStateStore(":memory:")
    emergency = TradingCircuitState(
        state=EngineState.EMERGENCY_STOP, reason_code=CIRCUIT_EMERGENCY_STOP_REQUESTED, since=AS_OF,
    )
    persist_circuit_state(store, emergency, AS_OF)

    result = reset_emergency_stop(store, reason="False positive -- manually verified equity feed glitch", as_of=AS_OF + 100)

    assert result.state is EngineState.READY
    assert result.reason_code is None
    assert result.since is None
    assert load_persisted_circuit_state(store) == result  # the reset itself is durably persisted


def test_reset_emergency_stop_journals_the_reason_and_timestamp() -> None:
    store = SqliteStateStore(":memory:")
    emergency = TradingCircuitState(
        state=EngineState.EMERGENCY_STOP, reason_code=CIRCUIT_EMERGENCY_STOP_REQUESTED, since=AS_OF,
    )
    persist_circuit_state(store, emergency, AS_OF)

    reset_emergency_stop(store, reason="CEO-authorized after manual review", as_of=AS_OF + 100)

    resets = emergency_stop_resets(store)
    assert len(resets) == 1
    assert resets[0].reason == "CEO-authorized after manual review"
    assert resets[0].as_of == AS_OF + 100
    assert resets[0].previous_reason_code == CIRCUIT_EMERGENCY_STOP_REQUESTED


def test_reset_survives_a_simulated_restart_and_does_not_re_trigger(tmp_path: Path) -> None:
    """After a deliberate reset, a restart must load READY -- not somehow reopen EMERGENCY_STOP -- and
    the reset history must still be there."""
    db_path = tmp_path / "state.db"
    store_before_restart = SqliteStateStore(db_path)
    emergency = TradingCircuitState(
        state=EngineState.EMERGENCY_STOP, reason_code=CIRCUIT_EMERGENCY_STOP_REQUESTED, since=AS_OF,
    )
    persist_circuit_state(store_before_restart, emergency, AS_OF)
    reset_emergency_stop(store_before_restart, reason="verified safe", as_of=AS_OF + 100)
    store_before_restart.close()

    store_after_restart = SqliteStateStore(db_path)
    assert load_persisted_circuit_state(store_after_restart) == READY_CIRCUIT_STATE
    assert len(emergency_stop_resets(store_after_restart)) == 1
    assert emergency_stop_resets(store_after_restart)[0].reason == "verified safe"
