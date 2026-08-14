"""The definitive real-artifact proof -- CEO Phase 2, steps 3-4: "porneste worker-ul real cu handshake HMAC
real... ruleaza fixture-ul N3/N4 prin IPC real." Unlike `test_tower_launcher.py`'s `test_8_...` (which
deliberately uses `VE_TOWER_WORKER_TEST_IDENTITY=1` -- the worker's OWN stub identity, monkeypatched pin --
because when it was written `ve_tower` genuinely was not installed anywhere), this test spawns the worker
with **no test-identity override**, against the genuinely installed `ve_tower` 0.3.0 (`STAGED_INSTALL_
AUTHORIZED`, `tower_worker/env/install_ve_tower.ps1`). A real handshake, a real identity pin match, and a
real N3/N4 fixture answered by `ve_tower.run_n3`/`run_n4` themselves -- not a stub anywhere in the chain.

Skips cleanly if the isolated tower venv isn't present on this machine (same convention as
`test_tower_launcher.py`'s real-subprocess tests)."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.new_brain_bridge.tower_client import TowerClient, TowerClientConfig, TowerN3N4Result
from ai_trader.new_brain_bridge.tower_launcher import EstablishedSession, TowerWorkerLauncher
from ai_trader.new_brain_bridge.tower_protocol import PROTOCOL_VERSION, REQUEST_SCHEMA_VERSION, TowerRequest

_TOWER_VENV = Path("C:/Users/MEDION GAMING/ve_tower_venv")
_TOWER_PYTHON = _TOWER_VENV / "Scripts" / "python.exe"

pytestmark_real = pytest.mark.skipif(
    not _TOWER_PYTHON.is_file(), reason="isolated tower venv not present on this machine"
)

_AS_OF = 1_700_000_000


def _synthetic_bars(*, count: int, step_seconds: int, as_of: int, start_price: float) -> tuple[dict[str, object], ...]:
    """Same deterministic generator as `tower_worker/tests/test_decision.py` -- duplicated rather than
    imported, since this test runs in the MAIN venv and must never import anything from `ve_tower_worker`
    (that package is only ever installed in the isolated tower venv)."""
    bars: list[dict[str, object]] = []
    price = start_price
    state = 12345
    first_time = as_of - (count - 1) * step_seconds
    for i in range(count):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        delta = ((state % 200) - 100) / 100.0
        open_ = price
        close = price + delta
        high = max(open_, close) + abs(delta) * 0.5 + 0.1
        low = min(open_, close) - abs(delta) * 0.5 - 0.1
        bars.append({
            "time": first_time + i * step_seconds,
            "open": round(open_, 2), "high": round(high, 2),
            "low": round(low, 2), "close": round(close, 2),
        })
        price = close
    return tuple(bars)


def _fixture_request() -> TowerRequest:
    return TowerRequest(
        protocol_version=PROTOCOL_VERSION, schema_version=REQUEST_SCHEMA_VERSION,
        request_id="real-e2e-req-1", market_event_id="XAUUSD:15:1700000000", event_fingerprint="",
        data_identity="d1", node_input_fingerprint="n1",
        symbol="XAUUSD", as_of=str(_AS_OF),
        n1_output={"available": True, "fingerprint": "n1fp-test"},
        n2_output={"available": True, "fingerprint": "n2fp-test", "bias_direction": "LONG"},
        m15_closed_bars=_synthetic_bars(count=150, step_seconds=900, as_of=_AS_OF, start_price=2000.0),
        m5_closed_bars=_synthetic_bars(count=150, step_seconds=300, as_of=_AS_OF, start_price=2010.0),
        strategy_id="trend_pullback", strategy_version="1.0",
    )


@pytestmark_real
def test_real_worker_handshake_is_accepted_with_no_test_identity_override(tmp_path: Path) -> None:
    """The literal task-273 completion criterion: a genuine `EstablishedSession`, not a `HandshakeFailure`
    -- for the first time ever with the real artifact installed, no stub, no monkeypatch."""
    launcher = TowerWorkerLauncher(tower_python=_TOWER_PYTHON, run_dir=tmp_path)
    try:
        result = launcher.launch_and_handshake()
        assert isinstance(result, EstablishedSession), f"expected EstablishedSession, got {result!r}"
        assert result.worker_identity.ve_tower_package_version == "0.3.0"
        assert result.worker_identity.package_build_commit == "6daf2aa"
    finally:
        launcher.stop()


@pytestmark_real
def test_real_worker_answers_a_real_n3_n4_fixture_over_real_ipc(tmp_path: Path) -> None:
    """Full round trip: real handshake -> real `TowerClient` -> real socket -> real `ve_tower.run_n3`/
    `run_n4` -> real response, session-and-identity-verified on the way back."""
    launcher = TowerWorkerLauncher(tower_python=_TOWER_PYTHON, run_dir=tmp_path)
    try:
        session = launcher.launch_and_handshake()
        assert isinstance(session, EstablishedSession), f"expected EstablishedSession, got {session!r}"

        client = TowerClient(
            TowerClientConfig(host=session.host, port=session.port, timeout_seconds=10.0), session=session,
        )
        result = client.request_n3_n4(_fixture_request())

        assert isinstance(result, TowerN3N4Result), f"expected TowerN3N4Result, got {result!r}"
        assert result.tower_version == "0.3.0"
        assert result.n3_output is not None
        assert "market_map_available" in result.n3_output
        assert isinstance(result.n3_output["market_map_available"], bool)
        # n4_output is present iff N3 found a map and a bias_direction was supplied (it was, above) --
        # never asserting a specific TRUE/FALSE outcome, only that the wiring itself produced an honest,
        # well-formed answer from the real artifact.
        if result.n3_output["market_map_available"]:
            assert result.n4_output is not None
            assert "confirmation_available" in result.n4_output
    finally:
        launcher.stop()
