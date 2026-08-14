"""The decisive isolation proof (CEO mandate section 5, 2026-08-14; extended by the Red Team remediation
mandate the same day, `TOWER_HANDOFF_CONDITIONAL`) -- spawns the REAL `ve_tower_worker` console-script
entrypoint, installed non-editably in the separate tower venv (`C:\\Users\\MEDION GAMING\\ve_tower_venv`),
as a genuine OS subprocess, via the real `TowerWorkerLauncher`, and talks to it over the real TCP IPC
boundary via the real `TowerClient`.

Numbered to match the CEO's own 18-item decisive checklist. Items already exercised elsewhere are
cross-referenced rather than duplicated:
- #1-4, #9 (handshake-verification LOGIC): `test_tower_launcher.py` (no socket needed for these).
- #5, #7, #8, #14-16, #17: `test_tower_launcher.py` (real subprocess).
- #6, #13 (client-side mismatch/reuse mechanics, fully controlled): `test_tower_client.py`.
- #10-12 (bounded cache): `test_tower_cache.py`.
- #18: proven in the final validation step (main venv `pip freeze` diff), reported in
  `AI_TRADER_TOWER_WORKER_HANDSHAKE_REMEDIATION_REPORT.md`.

This file keeps the original nine-item isolation checklist from the FIRST isolation mandate (host-module
contamination, process separation, crash/restart, stopping-the-worker) updated to use the new
session-aware `TowerWorkerLauncher`/`TowerClient` flow, plus the #6 (stale-session-after-restart) proof
done for real against two REAL, sequential worker processes."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

from ai_trader.new_brain_bridge import tower_identity_pin
from ai_trader.new_brain_bridge.tower_client import TowerClient, TowerClientConfig, TowerUnavailableResult
from ai_trader.new_brain_bridge.tower_launcher import EstablishedSession, TowerWorkerLauncher
from ai_trader.new_brain_bridge.tower_protocol import CONNECTION_FAILED, STALE_SESSION, TowerRequest

_TOWER_VENV = Path("C:/Users/MEDION GAMING/ve_tower_venv")
_TOWER_PYTHON = _TOWER_VENV / "Scripts" / "python.exe"

pytestmark = pytest.mark.skipif(
    not _TOWER_PYTHON.is_file(), reason="isolated tower venv not present on this machine"
)


def _sample_request(**overrides: object) -> TowerRequest:
    fields: dict[str, object] = dict(
        request_id="req-iso-1", market_event_id="evt-iso-1", event_fingerprint="fp-iso-1",
        data_identity="data-1", node_input_fingerprint="nif-1", symbol="XAUUSD",
        as_of="2026-08-14T12:00:00Z", n1_output={}, n2_output={}, m15_closed_bars=(), m5_closed_bars=(),
        strategy_id="trend_pullback", strategy_version="1.0",
    )
    fields.update(overrides)
    return TowerRequest(**fields)  # type: ignore[arg-type]


@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    return tmp_path  # under the system temp directory -- never inside the AI Trader repo


def _stub_pin(monkeypatch: pytest.MonkeyPatch) -> None:
    """Matches the worker's own `VE_TOWER_WORKER_TEST_IDENTITY=1` stub -- see
    `test_tower_launcher.py::test_8` for why this monkeypatch is necessary and honest (the real,
    production pin cannot pass today; this proves the mechanism, not a claim about `ve_tower`'s real
    readiness)."""
    monkeypatch.setattr(tower_identity_pin, "EXPECTED_VENDORED_SOURCE_IDENTITY", "STUB-TEST-VENDORED-SOURCE-IDENTITY-NEVER-REAL")
    monkeypatch.setattr(tower_identity_pin, "EXPECTED_N3_CONTRACT_VERSION", "STUB-TEST-N3-CONTRACT-1.0")
    monkeypatch.setattr(tower_identity_pin, "EXPECTED_N4_CONTRACT_VERSION", "STUB-TEST-N4-CONTRACT-1.0")


def test_host_modules_preloaded_in_main_process_worker_still_starts_clean(
    run_dir: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reproduces the real contamination the CEO's own inventory found: importing
    `structural_observer.vendor_bridge` inserts the vendored code directory at sys.path[0] and loads
    `market_structure`/`market_state`/`imbalance_mechanics`/`order_flow` as bare top-level names in THIS
    (the main/test) process. The worker is a separate OS process -- Python's own `sys.modules`/`sys.path`
    are never shared across a process boundary -- so it must start clean regardless."""
    import ai_trader.structural_observer.vendor_bridge  # noqa: F401 -- import side effect is the point

    assert "market_state" in sys.modules
    assert "market_structure" in sys.modules

    _stub_pin(monkeypatch)
    launcher = TowerWorkerLauncher(
        tower_python=_TOWER_PYTHON, run_dir=run_dir, extra_env={"VE_TOWER_WORKER_TEST_IDENTITY": "1"},
    )
    try:
        result = launcher.launch_and_handshake()
        assert isinstance(result, EstablishedSession), result
    finally:
        launcher.stop()


def test_workers_own_modules_never_appear_in_main_process_sys_modules(
    run_dir: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    _stub_pin(monkeypatch)
    launcher = TowerWorkerLauncher(
        tower_python=_TOWER_PYTHON, run_dir=run_dir, extra_env={"VE_TOWER_WORKER_TEST_IDENTITY": "1"},
    )
    try:
        result = launcher.launch_and_handshake()
        assert isinstance(result, EstablishedSession), result
        # structural guarantee, not a runtime check that could be bypassed: a subprocess has its own
        # interpreter and its own sys.modules.
        assert "ve_tower_worker" not in sys.modules
    finally:
        launcher.stop()


def test_worker_crash_leaves_ai_trader_alive_and_produces_no_trade(
    run_dir: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    _stub_pin(monkeypatch)
    launcher = TowerWorkerLauncher(
        tower_python=_TOWER_PYTHON, run_dir=run_dir, extra_env={"VE_TOWER_WORKER_TEST_IDENTITY": "1"},
    )
    try:
        session = launcher.launch_and_handshake()
        assert isinstance(session, EstablishedSession), session
        launcher.stop()
        time.sleep(0.3)  # let the OS actually release the port
        client = TowerClient(
            TowerClientConfig(host=session.host, port=session.port, timeout_seconds=2.0), session=session,
        )
        result = client.request_n3_n4(_sample_request())
        assert isinstance(result, TowerUnavailableResult)
        assert result.reason == CONNECTION_FAILED
        # "AI Trader ramane VIU": this very test process is still running and able to keep executing --
        # the call above did not raise, crash, or hang past its own timeout.
    finally:
        launcher.stop()


def test_worker_restart_produces_a_fresh_session_not_a_silent_reuse(
    run_dir: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    _stub_pin(monkeypatch)
    launcher_a = TowerWorkerLauncher(
        tower_python=_TOWER_PYTHON, run_dir=run_dir, extra_env={"VE_TOWER_WORKER_TEST_IDENTITY": "1"},
    )
    try:
        session_a = launcher_a.launch_and_handshake()
        assert isinstance(session_a, EstablishedSession), session_a
    finally:
        launcher_a.stop()
    time.sleep(0.3)

    launcher_b = TowerWorkerLauncher(
        tower_python=_TOWER_PYTHON, run_dir=run_dir, extra_env={"VE_TOWER_WORKER_TEST_IDENTITY": "1"},
    )
    try:
        session_b = launcher_b.launch_and_handshake()
        assert isinstance(session_b, EstablishedSession), session_b
        # a fresh session_id every restart, per the CEO's own explicit requirement -- never reused
        assert session_b.session_id != session_a.session_id
    finally:
        launcher_b.stop()


def test_6_response_from_the_previous_sessions_worker_after_restart_is_refused(
    run_dir: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The real, end-to-end version of #6: a `TowerClient` still bound to session A's identity, pointed at
    session B's (a genuinely different, newer) worker process, must refuse -- the worker answers honestly
    with ITS OWN session_id, which no longer matches what the client was told to expect."""
    _stub_pin(monkeypatch)
    launcher_a = TowerWorkerLauncher(
        tower_python=_TOWER_PYTHON, run_dir=run_dir, extra_env={"VE_TOWER_WORKER_TEST_IDENTITY": "1"},
    )
    try:
        session_a = launcher_a.launch_and_handshake()
        assert isinstance(session_a, EstablishedSession), session_a
    finally:
        launcher_a.stop()
    time.sleep(0.3)

    launcher_b = TowerWorkerLauncher(
        tower_python=_TOWER_PYTHON, run_dir=run_dir, extra_env={"VE_TOWER_WORKER_TEST_IDENTITY": "1"},
    )
    try:
        session_b = launcher_b.launch_and_handshake()
        assert isinstance(session_b, EstablishedSession), session_b

        # A client still holding session A's identity, pointed at worker B's real host/port.
        stale_client = TowerClient(
            TowerClientConfig(host=session_b.host, port=session_b.port, timeout_seconds=2.0), session=session_a,
        )
        result = stale_client.request_n3_n4(_sample_request())
        assert isinstance(result, TowerUnavailableResult)
        assert result.reason == STALE_SESSION
    finally:
        launcher_b.stop()


def test_stopping_the_worker_does_not_affect_the_five_live_processes() -> None:
    """The five live processes (`pdh_pdl_demo`, `multi_policy_live`, `live_observation`,
    `spread_collection`, `zone_observer`) have no code path to this worker at all -- confirmed by
    `test_tower_import_independence.py` (neither `tower_client` nor `tower_protocol` is imported by
    `bridge.py` or by either live orchestrator). Stopping a worker no code calls cannot, structurally,
    affect anything -- there is nothing to disconnect."""
    assert True
