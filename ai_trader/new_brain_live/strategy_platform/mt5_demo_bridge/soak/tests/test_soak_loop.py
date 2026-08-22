from __future__ import annotations

from pathlib import Path

from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import MT5ExecutionLedger
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak.safety_monitor import ACCOUNT_NOT_DEMO, SafetyMonitor
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak.soak_loop import (
    SoakTerminationConfig,
    run_soak,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.tests._fixtures import (
    FakeMT5BridgeGateway,
    make_connected_demo_adapter,
    make_ledger,
)
from ai_trader.new_brain_live.strategy_platform.real_ev_engine import CostModel
from ai_trader.new_brain_live.strategy_platform.risk_execution_adapter import RiskExecutionDeps
from ai_trader.new_brain_live.strategy_platform.shadow_ledger import ShadowLedger
from ai_trader.new_brain_live.strategy_platform.tests._fixtures import make_risk_execution_deps
from ai_trader.persistent_state.store import SqliteStateStore

SYMBOL = "XAUUSD"
_BAR_SECONDS = 900
_COST = CostModel(cost_model_id="AI_TRADER_SHADOW_COST_MODEL_v1", full_spread_price=0.0, entry_slippage_price=0.12, exit_slippage_price=0.12)


def _rate(ts: int, price: float) -> dict[str, float]:
    return {"time": ts, "open": price, "high": price + 0.3, "low": price - 0.3, "close": price, "tick_volume": 100.0}


def _flat_rates(*, count: int, end_ts: int, base_price: float = 2000.0) -> list[dict[str, float]]:
    return [_rate(end_ts - (count - i) * _BAR_SECONDS, base_price) for i in range(count)]


def _harness(tmp_path: Path) -> tuple[FakeMT5BridgeGateway, object, MT5ExecutionLedger, SqliteStateStore, ShadowLedger, SqliteStateStore, SafetyMonitor, SqliteStateStore]:
    gw = FakeMT5BridgeGateway()
    adapter = make_connected_demo_adapter(gw, config=MT5DemoConfig(max_order_volume=1.0))
    exec_ledger, exec_store = make_ledger(tmp_path, "exec.db")
    shadow_store = SqliteStateStore(tmp_path / "shadow.db")
    safety_store = SqliteStateStore(tmp_path / "safety.db")
    safety_monitor = SafetyMonitor(safety_store)
    return gw, adapter, exec_ledger, exec_store, ShadowLedger(shadow_store), shadow_store, safety_monitor, safety_store


def test_terminates_on_calendar_days_elapsed_condition_b(tmp_path: Path) -> None:
    gw, adapter, exec_ledger, exec_store, shadow_ledger, shadow_store, safety_monitor, safety_store = _harness(tmp_path)
    now = 10_000_000
    gw._rates = _flat_rates(count=25, end_ts=now - 2 * _BAR_SECONDS)
    ticks = iter([float(now), float(now) + 1, float(now) + 61 * 86400])  # 61 days on the 3rd check -> exceeds 60

    def now_fn() -> float:
        return next(ticks, float(now) + 999999)

    report = run_soak(
        adapter=adapter, gateway=gw, config=MT5DemoConfig(max_order_volume=1.0), execution_ledger=exec_ledger,  # type: ignore[arg-type]
        shadow_ledger=shadow_ledger, risk_execution_deps=RiskExecutionDeps(**make_risk_execution_deps()),  # type: ignore[arg-type]
        cost_model=_COST, safety_monitor=safety_monitor, symbol=SYMBOL, state_dir=tmp_path / "state",
        poll_interval_seconds=0.0, termination=SoakTerminationConfig(max_calendar_days=60.0),
        sleep=lambda s: None, now_fn=now_fn,
    )
    assert report.termination_reason == "B_CALENDAR_DAYS_ELAPSED"
    assert report.final_status[0] == "S5_MT5_DEMO_UNATTENDED_SOAK_COMPLETE"
    exec_store.close(); shadow_store.close(); safety_store.close()


def test_terminates_on_explicit_stop_condition_d(tmp_path: Path) -> None:
    gw, adapter, exec_ledger, exec_store, shadow_ledger, shadow_store, safety_monitor, safety_store = _harness(tmp_path)
    now = 10_000_000
    gw._rates = _flat_rates(count=25, end_ts=now - 2 * _BAR_SECONDS)
    calls = {"n": 0}

    def should_stop() -> bool:
        calls["n"] += 1
        return calls["n"] >= 2  # stop on the second termination check

    report = run_soak(
        adapter=adapter, gateway=gw, config=MT5DemoConfig(max_order_volume=1.0), execution_ledger=exec_ledger,  # type: ignore[arg-type]
        shadow_ledger=shadow_ledger, risk_execution_deps=RiskExecutionDeps(**make_risk_execution_deps()),  # type: ignore[arg-type]
        cost_model=_COST, safety_monitor=safety_monitor, symbol=SYMBOL, state_dir=tmp_path / "state",
        poll_interval_seconds=0.0, should_stop=should_stop, sleep=lambda s: None, now_fn=lambda: float(now),
    )
    assert report.termination_reason == "D_EXPLICIT_STOP"
    exec_store.close(); shadow_store.close(); safety_store.close()


def test_pre_tripped_safety_monitor_terminates_immediately_as_blocked(tmp_path: Path) -> None:
    gw, adapter, exec_ledger, exec_store, shadow_ledger, shadow_store, safety_monitor, safety_store = _harness(tmp_path)
    now = 10_000_000
    gw._rates = _flat_rates(count=25, end_ts=now - 2 * _BAR_SECONDS)
    safety_monitor.trip(ACCOUNT_NOT_DEMO, "pre-tripped for this test", at=now)

    report = run_soak(
        adapter=adapter, gateway=gw, config=MT5DemoConfig(max_order_volume=1.0), execution_ledger=exec_ledger,  # type: ignore[arg-type]
        shadow_ledger=shadow_ledger, risk_execution_deps=RiskExecutionDeps(**make_risk_execution_deps()),  # type: ignore[arg-type]
        cost_model=_COST, safety_monitor=safety_monitor, symbol=SYMBOL, state_dir=tmp_path / "state",
        poll_interval_seconds=0.0, sleep=lambda s: None, now_fn=lambda: float(now),
    )
    assert report.termination_reason == "C_SAFETY_BLOCKER"
    assert report.final_status[0] == "S5_MT5_DEMO_UNATTENDED_SOAK_BLOCKED"
    assert len(gw.order_send_calls) == 0
    exec_store.close(); shadow_store.close(); safety_store.close()


def test_no_genuine_signal_reports_honestly(tmp_path: Path) -> None:
    gw, adapter, exec_ledger, exec_store, shadow_ledger, shadow_store, safety_monitor, safety_store = _harness(tmp_path)
    now = 10_000_000
    gw._rates = _flat_rates(count=25, end_ts=now - 2 * _BAR_SECONDS)  # flat bars -- never a breakout
    calls = {"n": 0}

    def should_stop() -> bool:
        calls["n"] += 1
        return calls["n"] >= 2  # let one full processing pass happen, then stop

    report = run_soak(
        adapter=adapter, gateway=gw, config=MT5DemoConfig(max_order_volume=1.0), execution_ledger=exec_ledger,  # type: ignore[arg-type]
        shadow_ledger=shadow_ledger, risk_execution_deps=RiskExecutionDeps(**make_risk_execution_deps()),  # type: ignore[arg-type]
        cost_model=_COST, safety_monitor=safety_monitor, symbol=SYMBOL, state_dir=tmp_path / "state",
        poll_interval_seconds=0.0, should_stop=should_stop, sleep=lambda s: None, now_fn=lambda: float(now),
    )
    assert report.submitted_orders == 0
    assert report.closed_trades == 0
    assert "NO_GENUINE_S5_SIGNAL_OBSERVED" in report.final_status
    assert report.exceptions == ()
    exec_store.close(); shadow_store.close(); safety_store.close()


def test_restart_reconciliation_runs_before_any_new_processing(tmp_path: Path) -> None:
    """An ambiguous in-doubt identity present at soak startup must trip the safety monitor via
    reconciliation BEFORE the soak even attempts its own warmup/processing."""
    from types import SimpleNamespace

    from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import (
        PENDING_SUBMISSION,
        MT5ExecutionLedgerRecord,
    )

    gw, adapter, exec_ledger, exec_store, shadow_ledger, shadow_store, safety_monitor, safety_store = _harness(tmp_path)
    now = 10_000_000
    gw._rates = _flat_rates(count=25, end_ts=now - 2 * _BAR_SECONDS)
    exec_ledger.record(MT5ExecutionLedgerRecord(
        client_order_id="cid-x", decision_id="dec-x", state=PENDING_SUBMISSION, as_of=now,
        strategy_id="s5_c_2d587447_opening_range_breakout_long", strategy_version="rep_7472f3d412f2",
        symbol=SYMBOL, side="LONG", requested_entry=2000.0, actual_quote_bid=None, actual_quote_ask=None,
        sl=1990.0, tp=2030.0, requested_volume=1.0, modeled_risk_money=1.0, modeled_risk_fraction=0.0001,
        account_trade_mode="AccountTradeMode.DEMO", evidence_fingerprint="fp", order_request_id="req-x",
    ))
    gw._positions = (
        SimpleNamespace(symbol=SYMBOL, volume=1.0, price_open=2000.0, time=now, ticket=1),
        SimpleNamespace(symbol=SYMBOL, volume=1.0, price_open=2000.1, time=now, ticket=2),
    )

    report = run_soak(
        adapter=adapter, gateway=gw, config=MT5DemoConfig(max_order_volume=1.0), execution_ledger=exec_ledger,  # type: ignore[arg-type]
        shadow_ledger=shadow_ledger, risk_execution_deps=RiskExecutionDeps(**make_risk_execution_deps()),  # type: ignore[arg-type]
        cost_model=_COST, safety_monitor=safety_monitor, symbol=SYMBOL, state_dir=tmp_path / "state",
        poll_interval_seconds=0.0, sleep=lambda s: None, now_fn=lambda: float(now),
    )
    assert report.termination_reason == "C_SAFETY_BLOCKER"
    assert safety_monitor.is_blocked() is True
    exec_store.close(); shadow_store.close(); safety_store.close()


def test_health_snapshot_written_during_run(tmp_path: Path) -> None:
    gw, adapter, exec_ledger, exec_store, shadow_ledger, shadow_store, safety_monitor, safety_store = _harness(tmp_path)
    now = 10_000_000
    gw._rates = _flat_rates(count=25, end_ts=now - 2 * _BAR_SECONDS)
    state_dir = tmp_path / "state"
    calls = {"n": 0}

    def should_stop() -> bool:
        calls["n"] += 1
        return calls["n"] >= 2

    run_soak(
        adapter=adapter, gateway=gw, config=MT5DemoConfig(max_order_volume=1.0), execution_ledger=exec_ledger,  # type: ignore[arg-type]
        shadow_ledger=shadow_ledger, risk_execution_deps=RiskExecutionDeps(**make_risk_execution_deps()),  # type: ignore[arg-type]
        cost_model=_COST, safety_monitor=safety_monitor, symbol=SYMBOL, state_dir=state_dir,
        poll_interval_seconds=0.0, should_stop=should_stop, sleep=lambda s: None, now_fn=lambda: float(now),
    )
    assert (state_dir / "health.json").exists()
    exec_store.close(); shadow_store.close(); safety_store.close()
