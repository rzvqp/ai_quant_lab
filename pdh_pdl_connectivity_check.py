"""PDH-PDL Pre-Launch Connectivity Check (CEO directive, 2026-08-04: "Fa intai verificarea de
conectivitate, cum ai propus. Daca trece, lanseaza entrypoint.py..."). READ-ONLY -- exercises the SAME
real classes `entrypoint.py` will use (`RealMT5DemoGateway`, `RealMT5HistoryGateway`,
`MT5DemoBrokerAdapter`, `verify_safety_guards`), never raw `MetaTrader5` calls of its own, so a pass here
means the actual production wiring works, not just that the terminal is reachable.

**Explicitly NOT sent**: no `order_send`/`order_check` call anywhere in this script -- this is a
connectivity/precondition check, not the installation test (that already ran, XAUUSD_INFRA_TEST_REPORT.md,
ticket 499680521). It DOES read `positions_get` (to confirm no stale PDH-PDL position already sits open
under MAGIC_NUMBER before a continuous loop starts watching it) and `history_deals_get` (to prove the
history-reading gateway leg genuinely works against this terminal, not just structurally).

Throwaway diagnostic, matching this project's own established "diagnostic script, not a permanent
library change" precedent (`mt5_connectivity_probe.py`) -- never imported by any `ai_trader/` production
code. Exit code 0 = all checks passed, safe to launch. Exit code 1 = at least one check failed, DO NOT
launch."""

from __future__ import annotations

import json
import sys

from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.gateway import RealMT5DemoGateway
from ai_trader.mt5_demo_execution.safety import verify_safety_guards
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.mt5_pnl_source.gateway import RealMT5HistoryGateway
from ai_trader.pdh_pdl_demo.entrypoint import DEFAULT_DB_PATH, DEFAULT_STATE_DIR, SYMBOL
from ai_trader.pdh_pdl_demo.recognition_rule import MAGIC_NUMBER
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager.types import EngineState
from ai_trader.risk_manager_live.circuit_breaker import load_persisted_circuit_state

report: dict[str, object] = {}
all_passed = True


def _fail(key: str, detail: object) -> None:
    global all_passed
    report[key] = detail
    all_passed = False


def main() -> int:
    global all_passed

    order_gateway = RealMT5DemoGateway()
    initialized = order_gateway.initialize()
    report["order_gateway_initialize"] = initialized
    if not initialized:
        _fail("order_gateway_initialize_error", order_gateway.last_error())
        print(json.dumps(report, indent=2, default=str))
        return 1

    history_gateway = RealMT5HistoryGateway()
    history_initialized = history_gateway.initialize()
    report["history_gateway_initialize"] = history_initialized
    if not history_initialized:
        _fail("history_gateway_initialize_error", history_gateway.last_error())

    try:
        config = MT5DemoConfig(expected_server="FusionMarkets-Demo")
        demo_adapter = MT5DemoBrokerAdapter(gateway=order_gateway, config=config)
        connection = demo_adapter.connect()
        report["demo_adapter_connect_accepted"] = connection.accepted
        report["demo_adapter_connect_reason"] = connection.reason
        if not connection.accepted:
            _fail("demo_adapter_connect_failed", connection.reason)

        safety_report = verify_safety_guards(demo_adapter, config, symbol=SYMBOL)
        report["safety_guard_report"] = {
            "connected": safety_report.connected, "account_is_demo": safety_report.account_is_demo,
            "algo_trading_enabled": safety_report.algo_trading_enabled,
            "server_matches_expected": safety_report.server_matches_expected,
            "max_volume_configured": safety_report.max_volume_configured,
            "market_open": safety_report.market_open, "all_passed": safety_report.all_passed,
        }
        if not safety_report.all_passed:
            _fail("safety_guards_not_all_passed", report["safety_guard_report"])

        raw_symbol_info = order_gateway.symbol_info(SYMBOL)
        if raw_symbol_info is None:
            _fail("symbol_info_unavailable", SYMBOL)
        else:
            tick_value = getattr(raw_symbol_info, "trade_tick_value", None)
            tick_size = getattr(raw_symbol_info, "trade_tick_size", None)
            contract_size = getattr(raw_symbol_info, "trade_contract_size", None)
            report["symbol_info"] = {
                "trade_tick_value": tick_value, "trade_tick_size": tick_size,
                "trade_contract_size": contract_size, "volume_min": getattr(raw_symbol_info, "volume_min", None),
                "volume_step": getattr(raw_symbol_info, "volume_step", None),
            }
            if tick_value is None or tick_size is None or contract_size is None:
                _fail("symbol_info_missing_sizing_fields", report["symbol_info"])
            else:
                report["point_value_per_unit_derived"] = float(tick_value) / float(tick_size) / float(contract_size)

        if history_initialized:
            import time

            now = int(time.time())
            deals = history_gateway.history_deals_get(now - 3600, now)
            report["history_deals_get_reachable"] = deals is not None
            if deals is None:
                _fail("history_deals_get_failed", history_gateway.last_error())

            positions = history_gateway.positions_get(SYMBOL)
            report["positions_get_reachable"] = positions is not None
            if positions is None:
                _fail("positions_get_failed", history_gateway.last_error())
            else:
                stale = [p for p in positions if int(getattr(p, "magic", -1)) == MAGIC_NUMBER]
                report["stale_pdh_pdl_position_count"] = len(stale)
                if stale:
                    _fail(
                        "stale_pdh_pdl_position_already_open",
                        f"{len(stale)} open position(s) under MAGIC_NUMBER={MAGIC_NUMBER} already exist "
                        "-- the orchestrator would refuse to submit a fresh candidate (ALREADY_IN_POSITION) "
                        "until this clears; investigate before launch",
                    )

        DEFAULT_STATE_DIR.mkdir(parents=True, exist_ok=True)
        state_store = SqliteStateStore(DEFAULT_DB_PATH)
        try:
            circuit_state = load_persisted_circuit_state(state_store)
            report["circuit_state"] = {"state": circuit_state.state.value, "reason_code": circuit_state.reason_code}
            if circuit_state.state is not EngineState.READY:
                _fail("circuit_not_ready", report["circuit_state"])
        finally:
            state_store.close()

    finally:
        order_gateway.shutdown()
        report["shutdown_called"] = True

    report["all_passed"] = all_passed
    print(json.dumps(report, indent=2, default=str))
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
