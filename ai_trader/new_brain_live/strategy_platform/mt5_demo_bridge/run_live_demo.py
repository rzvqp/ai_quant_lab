"""Operational entrypoint for the mandate's live-connected DEMO run (mandate sections 30, 38, 42-44).
Connects to WHATEVER MT5 terminal/account is already open on this machine, mechanically verifies DEMO
status before doing anything else, and runs the bounded incremental live loop. Prints only masked,
non-secret account proof (section 38) -- never a login number, password, or token."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from ai_trader.execution_engine.adapters.connection import BrokerCredentials
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.gateway_ext import RealMT5BridgeGateway
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.live_runtime_loop import report_to_json, run_live_loop
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import MT5ExecutionLedger
from ai_trader.new_brain_live.strategy_platform.real_ev_engine import CostModel
from ai_trader.new_brain_live.strategy_platform.risk_execution_adapter import RiskExecutionDeps
from ai_trader.new_brain_live.strategy_platform.shadow_ledger import ShadowLedger
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import PortfolioState, RiskContext, SymbolRiskSnapshot
from ai_trader.risk_manager_live.types import AccountState, InstrumentSpecification

SYMBOL = "XAUUSD"


def _risk_execution_deps(*, equity: float) -> RiskExecutionDeps:
    account = AccountState(
        as_of=0, currency="USD", balance=equity, equity=equity, margin_used=0.0, margin_free=equity,
        margin_level=None, leverage=500.0, is_demo=True,
    )
    portfolio = PortfolioState(as_of=0, equity=equity, equity_high_water_mark=equity)
    instrument = InstrumentSpecification(
        symbol=SYMBOL, tick_size=0.01, lot_step=0.01, min_volume=0.01, max_volume=100.0, contract_size=100.0,
        point_value=1.0, margin_currency="USD",
    )
    snapshot = SymbolRiskSnapshot(
        atr=5.0, atr_rolling_median=5.0, current_spread=0.5, liquidity_proxy=1.0, is_weekend_gap=False,
        bars_since_gap=100, is_past_friday_cutoff=False, is_near_session_close=False,
        minutes_to_high_impact_event=999.0,
    )
    risk_context = RiskContext(as_of=0, per_symbol={SYMBOL: snapshot})
    config = RiskConfig()
    config.filters.reference_spread[SYMBOL] = 1.0
    config.filters.liquidity_floor[SYMBOL] = 0.5
    config.sizing.point_value[SYMBOL] = 1.0
    return RiskExecutionDeps(account=account, portfolio=portfolio, instrument=instrument, risk_context=risk_context, risk_config=config)


def main() -> int:
    max_duration_seconds = float(sys.argv[1]) if len(sys.argv) > 1 else 90.0
    gateway = RealMT5BridgeGateway()

    # mandate AI-TRADER-MT5-NEW-ACCOUNT-READINESS-001 section 3: the CURRENT MT5 terminal state is
    # authoritative -- never a hardcoded/previous-account server literal. A bare, unpinned probe
    # discovers whatever account is CURRENTLY logged in; expected_server is then pinned to that
    # observed value for the rest of this process's own lifetime (still a real safety net -- it still
    # catches a mid-session account switch, just never a stale one from a prior mandate's account).
    probe_ok = gateway.initialize()
    observed_server = None
    if probe_ok:
        probe_info = gateway.account_info()
        observed_server = str(probe_info.server) if probe_info is not None and getattr(probe_info, "server", None) is not None else None

    config = MT5DemoConfig(max_order_volume=1.0, expected_server=observed_server)
    adapter = MT5DemoBrokerAdapter(gateway=gateway, config=config, credentials=BrokerCredentials())

    connect_result = adapter.connect()
    if not connect_result.accepted:
        print(json.dumps({"status": "S5_MT5_DEMO_CONNECTION_BLOCKED", "reason": connect_result.reason}))
        return 1

    status = adapter.status()
    account_proof = {
        "trade_mode": str(status.account_trade_mode), "account_is_demo": status.account_is_demo,
        "server": status.server, "terminal_build": status.terminal_build,
        "algo_trading_status": str(status.algo_trading_status),
    }
    print("ACCOUNT_PROOF:", json.dumps(account_proof))

    if status.account_is_demo is not True:
        adapter.disconnect()
        print(json.dumps({"status": "S5_MT5_DEMO_SAFETY_FAIL", "reason": "account_is_demo is not True after connect"}))
        return 2

    gw_for_equity = gateway.account_info()
    equity = float(gw_for_equity.equity) if gw_for_equity is not None and getattr(gw_for_equity, "equity", None) is not None else 10_000.0
    currency = str(gw_for_equity.currency) if gw_for_equity is not None and getattr(gw_for_equity, "currency", None) is not None else "UNKNOWN"
    symbol_caps = adapter.symbol_capabilities(SYMBOL)
    print("SIZING_CONTEXT:", json.dumps({
        "equity_used_for_sizing": equity, "currency": currency,
        "symbol_contract": None if symbol_caps is None else {
            "min_qty": symbol_caps.min_qty, "max_qty": symbol_caps.max_qty, "lot_step": symbol_caps.lot_step,
            "tick_size": symbol_caps.tick_size, "digits": symbol_caps.digits,
        },
    }))

    repo_root = Path(__file__).resolve().parents[4]
    state_dir = repo_root / "new_brain_live_state" / "s5_mt5_demo"
    state_dir.mkdir(parents=True, exist_ok=True)
    exec_store = SqliteStateStore(state_dir / "execution_ledger.db")
    shadow_store = SqliteStateStore(state_dir / "shadow_ledger.db")
    execution_ledger = MT5ExecutionLedger(exec_store)
    shadow_ledger = ShadowLedger(shadow_store)
    cost_model = CostModel(cost_model_id="AI_TRADER_SHADOW_COST_MODEL_v1", full_spread_price=0.0, entry_slippage_price=0.12, exit_slippage_price=0.12)

    started = time.time()
    report = run_live_loop(
        adapter=adapter, gateway=gateway, config=config, execution_ledger=execution_ledger,
        shadow_ledger=shadow_ledger, risk_execution_deps=_risk_execution_deps(equity=equity),
        cost_model=cost_model, symbol=SYMBOL, poll_interval_seconds=5.0, max_duration_seconds=max_duration_seconds,
    )
    print("LIVE_LOOP_REPORT:", report_to_json(report))

    exec_store.close()
    shadow_store.close()
    adapter.disconnect()

    if report.reconciliation_blocked:
        final_status = "S5_MT5_DEMO_RECONCILIATION_BLOCKED"
    elif report.demo_orders_submitted > 0:
        final_status = "S5_GENUINE_MT5_DEMO_ORDER_EXECUTED"
    else:
        final_status = "S5_MT5_DEMO_ORDER_PATH_READY_AWAITING_GENUINE_S5_DEMO_SIGNAL"
    print(json.dumps({"final_status": final_status, "wall_clock_seconds": time.time() - started}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
