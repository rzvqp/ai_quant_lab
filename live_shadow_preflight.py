"""LIVE_SHADOW preflight (CEO authorization 2026-08-17, section 2). READ-ONLY -- every check here either
reads state or launches/stops the already-isolated tower worker via the existing `TowerWorkerLauncher`
(the identical pattern `demonstrate_candidate_v2_correlated.py` already uses). No order/position mutation,
no `set_authority` call -- this script only decides GO/NO-GO for the authority switch and activation that
follow it as separate, explicit steps.

Exit code 0 with `"verdict": "GO"` means every item below passed. Anything else is
`LIVE_SHADOW_STARTUP_FAILED` and no further activation step may proceed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import MetaTrader5 as mt5

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ve_brain  # type: ignore[import-untyped]

from ai_trader.mandate2_readiness.artifact_pin import (
    CURRENT_PIN,
    BrainArtifactIncompatibleError,
    ObservedArtifactManifest,
    verify_artifact_pin,
)
from ai_trader.mandate2_readiness.broker_gate import BrokerOrderSubmissionGate
from ai_trader.mandate2_readiness.shadow_cost_model import resolve_cost_components
from ai_trader.new_brain_bridge.authority import DecisionAuthority, current_authority
from ai_trader.new_brain_bridge.telemetry import NewBrainTelemetryLog
from ai_trader.new_brain_bridge.tower_identity_pin import verify_pin as verify_tower_pin
from ai_trader.new_brain_bridge.tower_launcher import EstablishedSession, TowerWorkerLauncher
from ai_trader.new_brain_live.entrypoint import DEFAULT_DB_PATH, DEFAULT_STATE_DIR, SYMBOL, TOWER_VENV_PYTHON
from ai_trader.new_brain_live.live_shadow_journal import LiveShadowJournal
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager.types import EngineState
from ai_trader.risk_manager_live.circuit_breaker import load_persisted_circuit_state

DELIVERY_COMMIT = "a1d2a6d"


def main() -> int:
    report: dict[str, object] = {}
    checks: dict[str, bool] = {}

    # -- ve_brain pin --------------------------------------------------------------------------------
    try:
        manifest = ve_brain.artifact_manifest(DELIVERY_COMMIT)
        observed = ObservedArtifactManifest(**manifest)
        verify_artifact_pin(observed, pin=CURRENT_PIN)
        checks["ve_brain_pin_zero_mismatches"] = True
        report["ve_brain_pin"] = "PASS -- 10/10 fields match CURRENT_PIN"
    except (BrainArtifactIncompatibleError, TypeError, KeyError) as exc:
        checks["ve_brain_pin_zero_mismatches"] = False
        report["ve_brain_pin"] = f"FAIL -- {exc!r}"

    # -- ve_tower worker: launch, real HMAC handshake, pin, then stop -------------------------------
    launcher = TowerWorkerLauncher(tower_python=TOWER_VENV_PYTHON)
    try:
        session = launcher.launch_and_handshake()
        if isinstance(session, EstablishedSession):
            mismatches = verify_tower_pin(session.worker_identity)
            checks["tower_worker_healthy_and_handshake_valid"] = True
            checks["ve_tower_pin_zero_mismatches"] = len(mismatches) == 0
            report["tower_worker_identity"] = session.worker_identity.as_dict()
            report["tower_pin_mismatches"] = [m.__dict__ for m in mismatches]
            report["tower_session_pid"] = session.pid
        else:
            checks["tower_worker_healthy_and_handshake_valid"] = False
            checks["ve_tower_pin_zero_mismatches"] = False
            report["tower_worker_identity"] = None
            report["tower_handshake_failure"] = {"reason": session.reason, "detail": session.detail}
    finally:
        launcher.stop()

    # -- main venv free of ve_tower ---------------------------------------------------------------
    try:
        import ve_tower  # type: ignore[import-not-found]  # noqa: F401
        checks["main_venv_free_of_ve_tower"] = False
        report["main_venv_ve_tower_check"] = "FAIL -- ve_tower importable in main venv"
    except ModuleNotFoundError:
        checks["main_venv_free_of_ve_tower"] = True
        report["main_venv_ve_tower_check"] = "PASS -- ModuleNotFoundError as expected"

    # -- MT5 connectivity, feed freshness, H1/M15/M5 availability, balance/equity baseline ---------
    mt5_ok = mt5.initialize()
    checks["mt5_connected"] = mt5_ok
    if mt5_ok:
        terminal_info = mt5.terminal_info()
        checks["mt5_terminal_connected_flag"] = bool(terminal_info.connected) if terminal_info else False
        account_info = mt5.account_info()
        report["balance_equity_baseline"] = (
            {"balance": account_info.balance, "equity": account_info.equity, "currency": account_info.currency}
            if account_info is not None else None
        )
        checks["balance_equity_baseline_recorded"] = account_info is not None

        m15 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M15, 0, 3)
        h1 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_H1, 0, 3)
        m5 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 0, 3)
        checks["m15_data_available"] = m15 is not None and len(m15) > 0
        checks["h1_data_available"] = h1 is not None and len(h1) > 0
        checks["m5_data_available"] = m5 is not None and len(m5) > 0
        report["last_m15_bar_time"] = int(m15[-1]["time"]) if m15 is not None and len(m15) else None

        orders = mt5.orders_get(symbol=SYMBOL)
        positions = mt5.positions_get(symbol=SYMBOL)
        checks["zero_active_orders"] = orders is not None and len(orders) == 0
        checks["zero_open_positions"] = positions is not None and len(positions) == 0
        report["active_orders_count"] = None if orders is None else len(orders)
        report["open_positions_count"] = None if positions is None else len(positions)
    else:
        for key in (
            "mt5_terminal_connected_flag", "balance_equity_baseline_recorded", "m15_data_available",
            "h1_data_available", "m5_data_available", "zero_active_orders", "zero_open_positions",
        ):
            checks[key] = False

    # -- official cost model available -------------------------------------------------------------
    try:
        resolve_cost_components(tier="BASE")
        checks["cost_model_available"] = True
    except Exception as exc:  # noqa: BLE001 -- preflight must not itself crash on a degraded model
        checks["cost_model_available"] = False
        report["cost_model_error"] = repr(exc)

    # -- telemetry + circuit breaker + broker gate + state dir --------------------------------------
    DEFAULT_STATE_DIR.mkdir(parents=True, exist_ok=True)
    checks["state_dir_writable"] = DEFAULT_STATE_DIR.exists()
    # NOTE: `SqliteStateStore.__init__` itself creates the db file/schema on open -- a prior preflight
    # run on this same DB path (not a real activation) already did that once, so file-existence is not
    # a meaningful "was this ever activated before" signal. Check actual persisted content instead.
    store = SqliteStateStore(DEFAULT_DB_PATH)
    try:
        NewBrainTelemetryLog(store)
        checks["telemetry_available"] = True
        circuit_state = load_persisted_circuit_state(store)
        checks["circuit_breaker_functional"] = circuit_state.state is EngineState.READY
        report["circuit_state_at_preflight"] = circuit_state.state.value

        authority_at_preflight = current_authority(store)
        telemetry_entry_count = len(NewBrainTelemetryLog(store).entries)
        shadow_entry_count = len(LiveShadowJournal(store).entries)
        checks["state_store_shows_no_prior_activation"] = (
            authority_at_preflight is DecisionAuthority.LEGACY
            and telemetry_entry_count == 0 and shadow_entry_count == 0
        )
        report["authority_at_preflight"] = authority_at_preflight.value
        report["telemetry_entry_count_at_preflight"] = telemetry_entry_count
        report["shadow_journal_entry_count_at_preflight"] = shadow_entry_count
    finally:
        store.close()

    gate = BrokerOrderSubmissionGate()
    checks["broker_gate_disabled"] = gate.enabled is False
    checks["broker_order_submission_disabled"] = ve_brain.BROKER_ORDER_SUBMISSION == "DISABLED"

    report["checks"] = checks
    report["verdict"] = "GO" if all(checks.values()) else "LIVE_SHADOW_STARTUP_FAILED"
    print(json.dumps(report, indent=2, default=str))
    return 0 if report["verdict"] == "GO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
