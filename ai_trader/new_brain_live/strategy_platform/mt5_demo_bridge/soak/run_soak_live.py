"""Operational entrypoint for the S5 MT5 DEMO unattended soak (mandate `AI-TRADER-S5-MT5-DEMO-
UNATTENDED-SOAK-001`). Connects to whatever MT5 terminal/account is already open, mechanically verifies
DEMO status, then runs `soak_loop.run_soak` until one of the section-23 termination conditions fires.

Usage: `python -m ...soak.run_soak_live [max_calendar_days]` -- omit for the full 60-day default. A
Windows Scheduled Task (mirroring the existing `AITraderLiveShadow` precedent) is the intended way to
keep this running unattended across restarts; this script itself does not register one."""

from __future__ import annotations

import dataclasses
import json
import sys
import time
from pathlib import Path

from ai_trader.execution_engine.adapters.connection import BrokerCredentials
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.gateway_ext import RealMT5BridgeGateway
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import MT5ExecutionLedger
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak.safety_monitor import SafetyMonitor
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak.soak_loop import SoakTerminationConfig, run_soak
from ai_trader.new_brain_live.strategy_platform.real_ev_engine import CostModel
from ai_trader.new_brain_live.strategy_platform.risk_execution_adapter import RiskExecutionDeps
from ai_trader.new_brain_live.strategy_platform.shadow_ledger import ShadowLedger
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import PortfolioState, RiskContext, SymbolRiskSnapshot
from ai_trader.risk_manager_live.types import AccountState, InstrumentSpecification

SYMBOL = "XAUUSD"


def _risk_execution_deps(*, equity: float) -> RiskExecutionDeps:
    account = AccountState(as_of=0, currency="USD", balance=equity, equity=equity, margin_used=0.0, margin_free=equity, margin_level=None, leverage=500.0, is_demo=True)
    portfolio = PortfolioState(as_of=0, equity=equity, equity_high_water_mark=equity)
    instrument = InstrumentSpecification(symbol=SYMBOL, tick_size=0.01, lot_step=0.01, min_volume=0.01, max_volume=100.0, contract_size=100.0, point_value=1.0, margin_currency="USD")
    snapshot = SymbolRiskSnapshot(atr=5.0, atr_rolling_median=5.0, current_spread=0.5, liquidity_proxy=1.0, is_weekend_gap=False, bars_since_gap=100, is_past_friday_cutoff=False, is_near_session_close=False, minutes_to_high_impact_event=999.0)
    risk_context = RiskContext(as_of=0, per_symbol={SYMBOL: snapshot})
    config = RiskConfig()
    config.filters.reference_spread[SYMBOL] = 1.0
    config.filters.liquidity_floor[SYMBOL] = 0.5
    config.sizing.point_value[SYMBOL] = 1.0
    return RiskExecutionDeps(account=account, portfolio=portfolio, instrument=instrument, risk_context=risk_context, risk_config=config)


def _log_startup_event(state_dir: Path, message: str) -> None:
    """Appends one line to `startup_events.log` -- diagnosability for a Scheduled-Task-launched process
    with no attached console (mandate section 28/29: never a credential, always local-only)."""
    state_dir.mkdir(parents=True, exist_ok=True)
    with (state_dir / "startup_events.log").open("a", encoding="utf-8") as f:
        f.write(f"{int(time.time())} {message}\n")


def main() -> int:
    max_calendar_days = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
    repo_root = Path(__file__).resolve().parents[5]
    state_dir = repo_root / "new_brain_live_state" / "s5_mt5_demo_soak"

    gateway = RealMT5BridgeGateway()

    # mandate AI-TRADER-MT5-NEW-ACCOUNT-READINESS-001 section 3: bind to whatever account is CURRENTLY
    # logged in, never a previous mandate's hardcoded server literal -- see run_live_demo.py's own
    # identical comment for the full rationale.
    try:
        probe_ok = gateway.initialize()
    except Exception:  # noqa: BLE001 -- a failed probe just means no pin is possible; connect() below still runs and reports the real failure
        probe_ok = False
    observed_server = None
    if probe_ok:
        probe_info = gateway.account_info()
        observed_server = str(probe_info.server) if probe_info is not None and getattr(probe_info, "server", None) is not None else None

    config = MT5DemoConfig(max_order_volume=1.0, expected_server=observed_server)
    adapter = MT5DemoBrokerAdapter(gateway=gateway, config=config, credentials=BrokerCredentials())

    try:
        connect_result = adapter.connect()
    except Exception as exc:  # noqa: BLE001 -- a Scheduled Task run has no console; never crash silently
        _log_startup_event(state_dir, f"CONNECT_EXCEPTION: {type(exc).__name__}: {exc}")
        print(json.dumps({"status": "S5_MT5_DEMO_CONNECTION_BLOCKED", "reason": str(exc)}))
        return 1
    if not connect_result.accepted:
        _log_startup_event(state_dir, f"CONNECT_REFUSED: {connect_result.reason}")
        print(json.dumps({"status": "S5_MT5_DEMO_CONNECTION_BLOCKED", "reason": connect_result.reason}))
        return 1
    status = adapter.status()
    if status.account_is_demo is not True:
        adapter.disconnect()
        _log_startup_event(state_dir, f"SAFETY_FAIL: account_trade_mode={status.account_trade_mode!r}")
        print(json.dumps({"status": "S5_MT5_DEMO_SAFETY_FAIL"}))
        return 2
    _log_startup_event(state_dir, f"CONNECTED: server={status.server} trade_mode={status.account_trade_mode}")
    print("ACCOUNT_PROOF:", json.dumps({"trade_mode": str(status.account_trade_mode), "server": status.server, "algo_trading_status": str(status.algo_trading_status)}))

    equity_info = gateway.account_info()
    equity = float(equity_info.equity) if equity_info is not None and getattr(equity_info, "equity", None) is not None else 10_000.0

    state_dir.mkdir(parents=True, exist_ok=True)
    exec_store = SqliteStateStore(state_dir / "execution_ledger.db")
    shadow_store = SqliteStateStore(state_dir / "shadow_ledger.db")
    safety_store = SqliteStateStore(state_dir / "safety_events.db")

    try:
        report = run_soak(
            adapter=adapter, gateway=gateway, config=config, execution_ledger=MT5ExecutionLedger(exec_store),
            shadow_ledger=ShadowLedger(shadow_store), risk_execution_deps=_risk_execution_deps(equity=equity),
            cost_model=CostModel(cost_model_id="AI_TRADER_SHADOW_COST_MODEL_v1", full_spread_price=0.0, entry_slippage_price=0.12, exit_slippage_price=0.12),
            safety_monitor=SafetyMonitor(safety_store), symbol=SYMBOL, state_dir=state_dir, poll_interval_seconds=5.0,
            termination=SoakTerminationConfig(max_calendar_days=max_calendar_days),
        )
        print("SOAK_REPORT:", json.dumps(dataclasses.asdict(report)))
        exit_code = 0
    except Exception as exc:  # noqa: BLE001 -- catastrophic setup failure (e.g. the warmup fetch itself
        # raising) must never crash silently with no record -- Task Scheduler restarts this process, so
        # the NEXT run's startup reconciliation is what actually protects against duplicate submission,
        # not this process staying alive; logging here is purely for diagnosability.
        _log_startup_event(state_dir, f"SOAK_EXCEPTION: {type(exc).__name__}: {exc}")
        print(json.dumps({"status": "S5_MT5_DEMO_UNATTENDED_SOAK_BLOCKED", "reason": str(exc)}))
        exit_code = 3
    finally:
        exec_store.close()
        shadow_store.close()
        safety_store.close()
        adapter.disconnect()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
