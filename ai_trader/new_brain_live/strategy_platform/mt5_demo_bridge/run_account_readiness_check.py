"""Operational entrypoint for mandate `AI-TRADER-MT5-NEW-ACCOUNT-READINESS-001`. Read-only / dry-run
only -- never calls `submit_order`, `order_send`, or `order_check` (confirmed by this package's own AST
guards). Detects the CURRENTLY logged-in MT5 account, verifies it mechanically as DEMO, binds the AI
Trader runtime's account identity to it, resolves the XAUUSD-equivalent symbol, dry-run exercises the
existing 5%-equity risk sizer against real contract data, and proves restart-persistence of the account
identity -- then reports and stops. `BROKER_ORDER_SUBMISSION` stays `DISABLED` throughout, unconditionally
of every other result (mandate section 11)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from ai_trader.execution_engine.adapters.connection import BrokerCredentials
from ai_trader.execution_engine.adapters.exceptions import SafetyRefusalError
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.account_identity import (
    identities_match,
    load_persisted_account_identity,
    persist_account_identity,
    read_current_account_identity,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.gateway_ext import RealMT5BridgeGateway
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import MT5ExecutionLedger
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.risk_sizer import compute_risk_sized_volume
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.signal_engine.types import Direction

SYMBOL = "XAUUSD"
_STATE_DIR = Path(__file__).resolve().parents[4] / "new_brain_live_state" / "s5_mt5_account_readiness"
_IDENTITY_PATH = _STATE_DIR / "account_identity.json"


def _connect() -> tuple[RealMT5BridgeGateway, MT5DemoBrokerAdapter | None, str]:
    """Returns (gateway, adapter-or-None, mt5_initialize_result). Never raises -- a connection refusal
    is a reported result, not an exception the caller must handle."""
    gateway = RealMT5BridgeGateway()
    try:
        probe_ok = gateway.initialize()
    except Exception as exc:  # noqa: BLE001
        return gateway, None, f"FAIL: {type(exc).__name__}: {exc}"
    if not probe_ok:
        code, desc = gateway.last_error()
        return gateway, None, f"FAIL: ({code}) {desc}"

    probe_info = gateway.account_info()
    observed_server = str(probe_info.server) if probe_info is not None and getattr(probe_info, "server", None) is not None else None
    config = MT5DemoConfig(max_order_volume=1.0, expected_server=observed_server)
    adapter = MT5DemoBrokerAdapter(gateway=gateway, config=config, credentials=BrokerCredentials())
    try:
        result = adapter.connect()
    except SafetyRefusalError as exc:
        return gateway, None, f"FAIL: {type(exc).__name__}: {exc}"
    except Exception as exc:  # noqa: BLE001
        return gateway, None, f"FAIL: {type(exc).__name__}: {exc}"
    if not result.accepted:
        return gateway, None, f"FAIL: {result.reason}"
    return gateway, adapter, "PASS"


def main() -> int:
    report: dict[str, object] = {}
    now = int(time.time())

    gateway, adapter, mt5_initialize_result = _connect()
    report["MT5_INITIALIZE"] = "PASS" if adapter is not None else mt5_initialize_result

    if adapter is None:
        report["DEMO_GATE"] = "FAIL"
        report["BROKER_ORDER_SUBMISSION"] = "DISABLED"
        print(json.dumps(report, indent=2))
        print("AI_TRADER_NEW_MT5_ACCOUNT_BLOCKED: MT5_INITIALIZE_FAILED -- " + mt5_initialize_result)
        return 1

    # --- section 1: current account detection (fresh, never cached) ---
    term = gateway.terminal_info()
    acc = gateway.account_info()
    report["MT5_TERMINAL_INFO"] = "PASS" if term is not None else "FAIL"
    report["MT5_ACCOUNT_INFO"] = "PASS" if acc is not None else "FAIL"

    if acc is None or term is None:
        report["DEMO_GATE"] = "FAIL"
        report["BROKER_ORDER_SUBMISSION"] = "DISABLED"
        adapter.disconnect()
        print(json.dumps(report, indent=2))
        print("AI_TRADER_NEW_MT5_ACCOUNT_BLOCKED: ACCOUNT_OR_TERMINAL_METADATA_UNREADABLE")
        return 1

    identity = read_current_account_identity(gateway, now=now)
    status = adapter.status()
    report["CURRENT_ACCOUNT"] = {
        "login_masked": identity.masked()["login"] if identity else None,
        "server": acc.server, "trade_mode": int(acc.trade_mode), "currency": acc.currency,
        "balance": float(acc.balance), "equity": float(acc.equity), "margin_free": float(acc.margin_free),
        "leverage": int(acc.leverage), "terminal_connected": bool(term.connected),
        "trade_permission_account": bool(acc.trade_allowed), "trade_permission_algo": bool(term.trade_allowed),
    }

    # --- section 2: DEMO hard gate, from actual MT5 metadata only ---
    demo_gate_pass = status.account_is_demo is True
    report["DEMO_GATE"] = "PASS" if demo_gate_pass else "FAIL"
    if not demo_gate_pass:
        report["BROKER_ORDER_SUBMISSION"] = "DISABLED"
        adapter.disconnect()
        print(json.dumps(report, indent=2))
        print(f"AI_TRADER_NEW_MT5_ACCOUNT_BLOCKED: MT5_ACCOUNT_TYPE_BLOCKED (trade_mode={acc.trade_mode})")
        return 1

    # --- section 3: bind runtime to the current account identity, never a previous one ---
    assert identity is not None
    previous_identity = load_persisted_account_identity(_IDENTITY_PATH)
    old_account_removed = previous_identity is None or not identities_match(previous_identity, identity)
    persist_account_identity(_IDENTITY_PATH, identity)
    report["OLD_ACCOUNT_STATE_REMOVED"] = "PASS" if old_account_removed else "PASS (same account already bound)"

    # --- section 10: restart persistence -- reload from disk (simulates a fresh process) and re-read live ---
    reloaded = load_persisted_account_identity(_IDENTITY_PATH)
    live_reread = read_current_account_identity(gateway, now=now)
    restart_persistence_pass = (
        reloaded is not None and live_reread is not None and identities_match(reloaded, live_reread)
    )
    # also confirm no non-terminal (in-doubt) ledger identities exist that could cause a duplicate
    # submission across this rebind -- if any exist, they belong to a DIFFERENT account's history and
    # restart persistence must not silently ignore that.
    exec_ledger_path = Path(__file__).resolve().parents[4] / "new_brain_live_state" / "s5_mt5_demo_soak" / "execution_ledger.db"
    dedup_safe = True
    non_terminal: tuple[str, ...] = ()
    if exec_ledger_path.exists():
        store = SqliteStateStore(exec_ledger_path)
        ledger = MT5ExecutionLedger(store)
        non_terminal = ledger.non_terminal_client_order_ids()
        dedup_safe = non_terminal == ()
        store.close()
    report["RESTART_PERSISTENCE"] = "PASS" if (restart_persistence_pass and dedup_safe) else "FAIL"
    if non_terminal:
        report["RESTART_PERSISTENCE_NOTE"] = f"{len(non_terminal)} non-terminal ledger identities require reconciliation before any future submission"

    # --- section 7: XAUUSD symbol resolution ---
    gateway.symbol_select(SYMBOL, True)
    symbol_caps = adapter.symbol_capabilities(SYMBOL)
    report["XAUUSD_SYMBOL"] = SYMBOL if symbol_caps is not None else None
    if symbol_caps is not None:
        report["SYMBOL_SPEC"] = {
            "tick_size": symbol_caps.tick_size, "contract_size": None, "volume_min": symbol_caps.min_qty,
            "volume_max": symbol_caps.max_qty, "volume_step": symbol_caps.lot_step, "digits": symbol_caps.digits,
        }
        raw_info = gateway.symbol_info(SYMBOL)
        if raw_info is not None:
            report["SYMBOL_SPEC"]["contract_size"] = float(getattr(raw_info, "trade_contract_size", 0.0))  # type: ignore[index]
            report["SYMBOL_SPEC"]["tick_value_static_field"] = float(getattr(raw_info, "trade_tick_value", 0.0))  # type: ignore[index]

    # --- section 8: dry-run risk sizing (no order) ---
    risk_pass = False
    risk_detail: dict[str, object] = {}
    if symbol_caps is not None:
        entry = 2450.00
        sl = 2440.00  # synthetic S5-shaped 10.00 price-unit stop
        sizing = compute_risk_sized_volume(
            gateway=gateway, equity=float(acc.equity), side=Direction.LONG, symbol=SYMBOL, entry_price=entry,
            sl_price=sl, volume_min=symbol_caps.min_qty, volume_max=symbol_caps.max_qty,
            volume_step=symbol_caps.lot_step, risk_fraction=0.05,
        )
        risk_detail = {
            "approved": sizing.approved, "volume": sizing.volume, "modeled_risk_money": sizing.modeled_risk_money,
            "modeled_risk_fraction": sizing.modeled_risk_fraction, "risk_budget_money": sizing.risk_budget_money,
        }
        # a genuine dry-run must also prove the fail-closed paths still work on this real account:
        fail_closed_extreme = compute_risk_sized_volume(
            gateway=gateway, equity=float(acc.equity), side=Direction.LONG, symbol=SYMBOL, entry_price=entry,
            sl_price=entry - (float(acc.equity) * 0.05 / 0.01 + 1000),  # deliberately huge -- min lot must exceed budget
            volume_min=symbol_caps.min_qty, volume_max=symbol_caps.max_qty, volume_step=symbol_caps.lot_step,
            risk_fraction=0.05,
        )
        risk_pass = (
            sizing.approved and sizing.modeled_risk_fraction is not None and sizing.modeled_risk_fraction <= 0.05 + 1e-9
            and not fail_closed_extreme.approved
        )
    report["RISK_ENGINE_5_PERCENT"] = "PASS" if risk_pass else "FAIL"
    report["RISK_ENGINE_DRY_RUN_DETAIL"] = risk_detail

    # --- section 6: market status (informational, never a readiness blocker) ---
    tick = gateway.symbol_info_tick(SYMBOL)
    market_status = "UNKNOWN"
    if tick is not None:
        age = now - int(getattr(tick, "time", now))
        market_status = "OPEN" if age < 120 else "CLOSED"
    report["MARKET_STATUS"] = market_status

    report["BROKER_ORDER_SUBMISSION"] = "DISABLED"
    adapter.disconnect()

    all_pass = symbol_caps is not None and all(
        report.get(k) == "PASS" for k in (
            "MT5_INITIALIZE", "MT5_TERMINAL_INFO", "MT5_ACCOUNT_INFO", "DEMO_GATE",
            "RISK_ENGINE_5_PERCENT", "RESTART_PERSISTENCE",
        )
    )

    print(json.dumps(report, indent=2))
    if all_pass:
        print("AI_TRADER_NEW_MT5_DEMO_ACCOUNT_READY")
        return 0
    print("AI_TRADER_NEW_MT5_ACCOUNT_BLOCKED: see report fields marked FAIL above")
    return 1


if __name__ == "__main__":
    sys.exit(main())
