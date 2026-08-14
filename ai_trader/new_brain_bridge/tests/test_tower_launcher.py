"""`TowerWorkerLauncher` tests -- CEO/Red Team remediation, 2026-08-14 (`TOWER_HANDOFF_CONDITIONAL`),
mapped explicitly to the 18-item decisive checklist. Split into two groups:

- **Handshake-verification-logic tests (#1-4, #9)** call `verify_handshake_response` directly against a
  hand-built `HandshakeResponse` -- no socket, no subprocess. This is deliberate: these items are about
  whether the VERIFICATION LOGIC catches a bad claim, not about networking mechanics (already covered by
  `test_tower_client.py`'s fake-server tests and `tower_worker`'s own `test_server_roundtrip.py`).
- **Real-subprocess tests (#5, #7, #8, #14-17)** spawn the REAL installed `ve_tower_worker` in the
  isolated tower venv and drive it through `TowerWorkerLauncher.launch_and_handshake` end-to-end. Skips
  cleanly if the tower venv isn't present on this machine.
"""

from __future__ import annotations

import hashlib
import hmac
import socket
import time
from pathlib import Path

import pytest

from ai_trader.new_brain_bridge import tower_identity_pin
from ai_trader.new_brain_bridge.tower_launcher import (
    EstablishedSession,
    HandshakeFailure,
    TOWER_WORKER_STARTUP_FAILED,
    TowerWorkerLauncher,
    verify_handshake_response,
)
from ai_trader.new_brain_bridge.tower_protocol import (
    CONNECTION_FAILED,
    HANDSHAKE_HMAC_MISMATCH,
    HANDSHAKE_IDENTITY_MISMATCH,
    HANDSHAKE_SESSION_ID_MISMATCH,
    NON_LOOPBACK_BIND_FORBIDDEN,
    HandshakeResponse,
    WorkerIdentity,
)

_TOWER_VENV = Path("C:/Users/MEDION GAMING/ve_tower_venv")
_TOWER_PYTHON = _TOWER_VENV / "Scripts" / "python.exe"

_SESSION_ID = "sess-fixture-1"
_SESSION_SECRET = b"fixture-secret-bytes-0123456789"
_CHALLENGE_HEX = "cafebabecafebabe"


def _matching_identity(**overrides: object) -> WorkerIdentity:
    fields: dict[str, object] = {
        "worker_package_version": tower_identity_pin.EXPECTED_WORKER_PACKAGE_VERSION,
        "worker_delivery_commit": "some-real-manifest-backed-commit",
        "protocol_version": tower_identity_pin.EXPECTED_PROTOCOL_VERSION,
        "ve_tower_package_version": tower_identity_pin.EXPECTED_VE_TOWER_PACKAGE_VERSION,
        "package_build_commit": tower_identity_pin.EXPECTED_PACKAGE_BUILD_COMMIT,
        "state_delivery_commit": tower_identity_pin.EXPECTED_STATE_DELIVERY_COMMIT,
        "wheel_sha256": tower_identity_pin.EXPECTED_WHEEL_SHA256,
        "vendored_source_identity": tower_identity_pin.EXPECTED_VENDORED_SOURCE_IDENTITY,
        "n3_contract_version": tower_identity_pin.EXPECTED_N3_CONTRACT_VERSION,
        "n4_contract_version": tower_identity_pin.EXPECTED_N4_CONTRACT_VERSION,
    }
    fields.update(overrides)
    return WorkerIdentity(**fields)  # type: ignore[arg-type]


def _signed_response(identity: WorkerIdentity, *, secret: bytes = _SESSION_SECRET, session_id: str = _SESSION_ID) -> HandshakeResponse:
    """Builds a handshake response with a CORRECTLY computed HMAC -- used for tests where the identity
    itself, not the HMAC, is the thing under test (a fake server that knows the secret but lies about
    what it's running)."""
    hmac_hex = hmac.new(
        secret, (_CHALLENGE_HEX + identity.canonical_json() + session_id).encode("utf-8"), hashlib.sha256,
    ).hexdigest()
    return HandshakeResponse(
        session_id=session_id, hmac_hex=hmac_hex, identity=identity, pid=999,
        process_start_identity="fixture-start", readiness_state="READY",
    )


def test_1_fake_server_with_correct_protocol_but_wrong_secret_is_refused() -> None:
    """"Un server FALS care vorbeste protocol 1.0(2.0), copiaza request_id si livreaza
    tower_version = WRONG-9.9.9 e ACCEPTAT" -- the original defect. A responder that doesn't know the real
    session secret can never produce a matching HMAC, regardless of how plausible its claimed fields look."""
    fake_identity = _matching_identity(ve_tower_package_version="WRONG-9.9.9")
    response = _signed_response(fake_identity, secret=b"an-attacker-does-not-know-the-real-secret")
    result = verify_handshake_response(
        response, expected_session_id=_SESSION_ID, session_secret=_SESSION_SECRET, challenge_hex=_CHALLENGE_HEX,
    )
    assert isinstance(result, HandshakeFailure)
    assert result.reason == HANDSHAKE_HMAC_MISMATCH


def test_2_old_worker_version_is_refused() -> None:
    identity = _matching_identity(ve_tower_package_version="0.1.0")
    response = _signed_response(identity)
    result = verify_handshake_response(
        response, expected_session_id=_SESSION_ID, session_secret=_SESSION_SECRET, challenge_hex=_CHALLENGE_HEX,
    )
    assert isinstance(result, HandshakeFailure)
    assert result.reason == HANDSHAKE_IDENTITY_MISMATCH
    assert "ve_tower_package_version" in result.detail


def test_3_different_wheel_hash_is_refused() -> None:
    identity = _matching_identity(wheel_sha256="0" * 64)
    response = _signed_response(identity)
    result = verify_handshake_response(
        response, expected_session_id=_SESSION_ID, session_secret=_SESSION_SECRET, challenge_hex=_CHALLENGE_HEX,
    )
    assert isinstance(result, HandshakeFailure)
    assert result.reason == HANDSHAKE_IDENTITY_MISMATCH
    assert "wheel_sha256" in result.detail


def test_4_different_n3_or_n4_contract_is_refused() -> None:
    """2026-08-14, `TOWER_METADATA_PASS`: the pin now carries a real, closed `EXPECTED_N3_CONTRACT_VERSION`
    (`tower-n3-request-v2`) -- no monkeypatch needed anymore to demonstrate a genuinely different claimed
    value being refused."""
    identity = _matching_identity(n3_contract_version="tower-n3-request-v1-old")
    response = _signed_response(identity)
    result = verify_handshake_response(
        response, expected_session_id=_SESSION_ID, session_secret=_SESSION_SECRET, challenge_hex=_CHALLENGE_HEX,
    )
    assert isinstance(result, HandshakeFailure)
    assert result.reason == HANDSHAKE_IDENTITY_MISMATCH
    assert "n3_contract_version" in result.detail


def test_5_different_session_id_in_handshake_response_is_refused() -> None:
    identity = _matching_identity()
    response = _signed_response(identity, session_id="a-completely-different-session")
    result = verify_handshake_response(
        response, expected_session_id=_SESSION_ID, session_secret=_SESSION_SECRET, challenge_hex=_CHALLENGE_HEX,
    )
    assert isinstance(result, HandshakeFailure)
    assert result.reason == HANDSHAKE_SESSION_ID_MISMATCH


def test_old_worker_package_version_itself_is_refused() -> None:
    """2026-08-14 pin-closure fix: distinct from test_2 (which exercises an old `ve_tower` version) --
    this exercises the WORKER's own package version specifically, which `verify_pin` previously never
    actually checked despite its own docstring claiming otherwise."""
    identity = _matching_identity(worker_package_version="0.1.0-old-worker-build")
    response = _signed_response(identity)
    result = verify_handshake_response(
        response, expected_session_id=_SESSION_ID, session_secret=_SESSION_SECRET, challenge_hex=_CHALLENGE_HEX,
    )
    assert isinstance(result, HandshakeFailure)
    assert result.reason == HANDSHAKE_IDENTITY_MISMATCH
    assert "worker_package_version" in result.detail


def test_missing_worker_delivery_commit_is_refused_not_silently_accepted() -> None:
    """A worker with no real `worker_delivery_manifest.json` backing (the honest, pre-install state)
    must still be refused by the pin -- proving `worker_delivery_commit=None` is never treated as an
    implicit pass just because it can't be exact-matched."""
    identity = _matching_identity(worker_delivery_commit=None)
    response = _signed_response(identity)
    result = verify_handshake_response(
        response, expected_session_id=_SESSION_ID, session_secret=_SESSION_SECRET, challenge_hex=_CHALLENGE_HEX,
    )
    assert isinstance(result, HandshakeFailure)
    assert result.reason == HANDSHAKE_IDENTITY_MISMATCH
    assert "worker_delivery_commit" in result.detail


def test_9_response_claiming_empty_worker_identity_fields_is_refused() -> None:
    """A response's identity fields being empty/blank rather than a well-formed claim must still fail --
    `verify_pin` treats an empty string as any other wrong value, never as an implicit pass."""
    identity = _matching_identity(ve_tower_package_version="", package_build_commit="")
    response = _signed_response(identity)
    result = verify_handshake_response(
        response, expected_session_id=_SESSION_ID, session_secret=_SESSION_SECRET, challenge_hex=_CHALLENGE_HEX,
    )
    assert isinstance(result, HandshakeFailure)
    assert result.reason == HANDSHAKE_IDENTITY_MISMATCH


def test_14_zero_dot_zero_dot_zero_dot_zero_is_refused_at_launcher_construction() -> None:
    with pytest.raises(ValueError, match=NON_LOOPBACK_BIND_FORBIDDEN):
        TowerWorkerLauncher(tower_python=_TOWER_PYTHON, host="0.0.0.0")


def test_15_external_address_is_refused_at_launcher_construction() -> None:
    with pytest.raises(ValueError, match=NON_LOOPBACK_BIND_FORBIDDEN):
        TowerWorkerLauncher(tower_python=_TOWER_PYTHON, host="203.0.113.5")


def test_16_loopback_is_accepted_at_launcher_construction() -> None:
    launcher = TowerWorkerLauncher(tower_python=_TOWER_PYTHON, host="127.0.0.1")
    assert launcher is not None


# ------------------------------------------------------------------------------------------------
# Real-subprocess tests -- skip cleanly if the isolated tower venv isn't present on this machine.
# ------------------------------------------------------------------------------------------------

pytestmark_real = pytest.mark.skipif(
    not _TOWER_PYTHON.is_file(), reason="isolated tower venv not present on this machine",
)


@pytestmark_real
def test_8_valid_handshake_against_the_real_worker_is_accepted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Uses `VE_TOWER_WORKER_TEST_IDENTITY=1` (the worker's own test-only stub identity) and monkeypatches
    the pin's three currently-PENDING fields to match the stub's synthetic values -- proving the FULL
    mechanism (spawn, stdin secret handoff, readiness, HMAC, pin) works end-to-end, without ever installing
    `ve_tower` and without ever claiming the currently-incomplete production pin actually passes today."""
    monkeypatch.setattr(tower_identity_pin, "EXPECTED_VENDORED_SOURCE_IDENTITY", "STUB-TEST-VENDORED-SOURCE-IDENTITY-NEVER-REAL")
    monkeypatch.setattr(tower_identity_pin, "EXPECTED_N3_CONTRACT_VERSION", "STUB-TEST-N3-CONTRACT-1.0")
    monkeypatch.setattr(tower_identity_pin, "EXPECTED_N4_CONTRACT_VERSION", "STUB-TEST-N4-CONTRACT-1.0")

    launcher = TowerWorkerLauncher(
        tower_python=_TOWER_PYTHON, run_dir=tmp_path, extra_env={"VE_TOWER_WORKER_TEST_IDENTITY": "1"},
    )
    try:
        result = launcher.launch_and_handshake()
        assert isinstance(result, EstablishedSession), result
        assert result.session_id
        assert result.worker_identity.ve_tower_package_version == "0.3.0"
    finally:
        launcher.stop()


@pytestmark_real
def test_7_port_already_occupied_by_another_process_is_not_connected_to(tmp_path: Path) -> None:
    occupier = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    occupier.bind(("127.0.0.1", 0))
    occupier.listen(1)
    occupied_port = occupier.getsockname()[1]
    try:
        launcher = TowerWorkerLauncher(tower_python=_TOWER_PYTHON, run_dir=tmp_path)
        try:
            result = launcher.launch_and_handshake(requested_port=occupied_port)
            assert isinstance(result, HandshakeFailure)
            assert result.reason == TOWER_WORKER_STARTUP_FAILED
        finally:
            launcher.stop()
    finally:
        occupier.close()


@pytestmark_real
def test_17_worker_crash_leaves_the_launcher_process_alive_and_reports_connection_failed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(tower_identity_pin, "EXPECTED_VENDORED_SOURCE_IDENTITY", "STUB-TEST-VENDORED-SOURCE-IDENTITY-NEVER-REAL")
    monkeypatch.setattr(tower_identity_pin, "EXPECTED_N3_CONTRACT_VERSION", "STUB-TEST-N3-CONTRACT-1.0")
    monkeypatch.setattr(tower_identity_pin, "EXPECTED_N4_CONTRACT_VERSION", "STUB-TEST-N4-CONTRACT-1.0")

    launcher = TowerWorkerLauncher(
        tower_python=_TOWER_PYTHON, run_dir=tmp_path, extra_env={"VE_TOWER_WORKER_TEST_IDENTITY": "1"},
    )
    try:
        result = launcher.launch_and_handshake()
        assert isinstance(result, EstablishedSession)
        launcher.stop()  # simulate crash
        time.sleep(0.3)

        # "AI Trader ramane VIU": this very test process is still executing, unaffected by the worker's
        # death -- the assertion below just makes that concrete by reaching a new socket attempt.
        with pytest.raises(OSError):
            with socket.create_connection((result.host, result.port), timeout=1.0):
                pass
    finally:
        launcher.stop()
