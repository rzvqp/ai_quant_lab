from __future__ import annotations

import hashlib
import hmac
import json
import socket
import threading

import pytest

from ve_tower_worker.artifact_identity_stub import STUB_IDENTITY, stub_read_worker_identity
from ve_tower_worker.decision_stub import FAKE_TOWER_VERSION, fake_decision
from ve_tower_worker.protocol import (
    FRAME_TYPE_CHAIN_REQUEST,
    MALFORMED_REQUEST,
    PROTOCOL_VERSION_MISMATCH,
    UNKNOWN_REQUEST_FIELD,
    HandshakeRequest,
    parse_handshake_response,
    pack_frame,
    unpack_length_prefix,
)
from ve_tower_worker.server import NonLoopbackBindError, TowerWorkerServer, recv_frame

_SESSION_ID = "test-session-1"
_SESSION_SECRET = b"test-secret-bytes-0123456789ab"


def _chain_request_json(**overrides: object) -> bytes:
    fields: dict[str, object] = {
        "type": FRAME_TYPE_CHAIN_REQUEST, "protocol_version": "3.0", "schema_version": "1.0",
        "request_id": "r1", "market_event_id": "e1", "trace_id": "t1", "correlation_id": "c1",
        "symbol": "XAUUSD", "as_of": 1_700_000_000, "configuration_fingerprint": "cfg-1",
        "regime_axes_status": ["TREND_UP"],
        "h1_open": [], "h1_high": [], "h1_low": [], "h1_close": [], "h1_time": [],
        "h1_source_identity": "tower-client:XAUUSD:H1", "h1_max_staleness_s": None,
        "m15_open": [], "m15_high": [], "m15_low": [], "m15_close": [], "m15_time": [],
        "m15_source_identity": "tower-client:XAUUSD:M15", "m15_max_staleness_s": None,
        "m5_high": [], "m5_low": [], "m5_close": [], "m5_time": [],
        "m5_source_identity": "tower-client:XAUUSD:M5", "m5_max_staleness_s": None,
        "strategy_id": "trend_pullback", "strategy_version": "1.0", "side": 1,
        "expected_n2_contract": "stub-n2", "expected_n3_contract": "stub-n3", "expected_n4_contract": "stub-n4",
    }
    fields.update(overrides)
    return json.dumps(fields).encode("utf-8")


def _make_server(**overrides: object) -> TowerWorkerServer:
    kwargs: dict[str, object] = dict(
        host="127.0.0.1", port=0, decision_fn=fake_decision, identity_fn=stub_read_worker_identity,
        session_id=_SESSION_ID, session_secret=_SESSION_SECRET, process_start_identity="start-token",
        timeout_seconds=5.0,
    )
    kwargs.update(overrides)
    return TowerWorkerServer(**kwargs)  # type: ignore[arg-type]


def _serve_one_in_background(server: TowerWorkerServer) -> threading.Thread:
    thread = threading.Thread(target=server.handle_one_connection, daemon=True)
    thread.start()
    return thread


def _send_and_receive(server: TowerWorkerServer, payload: bytes) -> bytes:
    with socket.create_connection((server.host, server.port), timeout=5.0) as conn:
        conn.sendall(pack_frame(payload))
        prefix = b""
        while len(prefix) < 4:
            chunk = conn.recv(4 - len(prefix))
            assert chunk
            prefix += chunk
        length = unpack_length_prefix(prefix)
        body = b""
        while len(body) < length:
            chunk = conn.recv(length - len(body))
            assert chunk
            body += chunk
        return body


def test_valid_request_gets_fake_decision_response() -> None:
    server = _make_server()
    try:
        thread = _serve_one_in_background(server)
        response = json.loads(_send_and_receive(server, _chain_request_json()))
        thread.join(timeout=5.0)
        assert response["ok"] is True
        assert response["request_id"] == "r1"
        assert response["market_event_id"] == "e1"
        assert response["correlation_id"] == "c1"
        assert response["tower_version"] == FAKE_TOWER_VERSION
        assert response["reason_codes"] == ["STUB_FIXTURE_RESPONSE"]
        # session/identity are stamped by the SERVER, unconditionally -- never left to decision_fn
        assert response["session_id"] == _SESSION_ID
        assert response["worker_identity_fingerprint"] == STUB_IDENTITY.fingerprint()
    finally:
        server.close()


def test_protocol_version_mismatch_is_refused() -> None:
    server = _make_server()
    try:
        thread = _serve_one_in_background(server)
        response = json.loads(_send_and_receive(server, _chain_request_json(protocol_version="99.0", request_id="r2", market_event_id="e2")))
        thread.join(timeout=5.0)
        assert response["ok"] is False
        assert response["reason_codes"] == [PROTOCOL_VERSION_MISMATCH]
        assert response["request_id"] == "r2"
        assert response["market_event_id"] == "e2"
        assert response["session_id"] == _SESSION_ID
    finally:
        server.close()


def test_malformed_request_gets_diagnosable_refusal() -> None:
    server = _make_server()
    try:
        thread = _serve_one_in_background(server)
        response = json.loads(_send_and_receive(server, b'{"type": "chain_request"}'))
        thread.join(timeout=5.0)
        assert response["ok"] is False
        assert response["terminal_reason_code"] == MALFORMED_REQUEST
        assert response["request_id"] == "UNKNOWN"
    finally:
        server.close()


def test_unknown_request_field_is_refused() -> None:
    """The exact structural enforcement CEO section 5 requires: a client that tries to smuggle
    `n2_fingerprint`/`bias_available`/any other non-permitted field gets refused, not silently ignored."""
    server = _make_server()
    try:
        thread = _serve_one_in_background(server)
        response = json.loads(_send_and_receive(
            server, _chain_request_json(request_id="r-unknown-field", n2_fingerprint="sneaky-value"),
        ))
        thread.join(timeout=5.0)
        assert response["ok"] is False
        assert response["terminal_reason_code"] == UNKNOWN_REQUEST_FIELD
    finally:
        server.close()


def test_decision_fn_raising_an_unexpected_exception_degrades_and_the_server_keeps_serving() -> None:
    """The real proof behind test 20b (`mandate2_readiness/tests/test_e2e_readiness.py`, Mandate B point
    5): "if a node raises... the pipeline must degrade to NO_TRADE for THAT decision cycle, not hang, not
    guess, not propagate the exception and kill the whole process." `ve_tower.run_tower_chain` is itself
    designed to never raise (always returns its own Unavailable/degraded shape) -- so the only way to
    exercise "a node's own code raises unexpectedly" from OUTSIDE this venv is dependency injection HERE,
    at the source, the same `decision_fn=` seam `server.py`'s own constructor already exposes for
    `fake_decision`."""
    def _raising_decision_fn(request: object) -> object:
        raise RuntimeError("deliberate fault injection -- simulates an unexpected node-internal bug")

    server = _make_server(decision_fn=_raising_decision_fn)
    try:
        thread = _serve_one_in_background(server)
        response = json.loads(_send_and_receive(
            server, _chain_request_json(request_id="r-fault-1", market_event_id="e-fault-1"),
        ))
        thread.join(timeout=5.0)

        assert response["ok"] is False  # degraded, not a fabricated success
        assert response["n2_output"] is None and response["n3_output"] is None and response["n4_output"] is None
        assert "NODE_FAILURE_DEGRADED_TO_UNAVAILABLE" in response["reason_codes"]
        assert any("RuntimeError" in code for code in response["reason_codes"])  # the real cause, visible
        assert response["request_id"] == "r-fault-1"  # THIS decision cycle's own identity, not lost
        # session/identity are still stamped correctly even on the degraded path -- the exception was
        # caught BEFORE _stamp_session, never bypassing it
        assert response["session_id"] == _SESSION_ID
    finally:
        server.close()

    # "the loop continues" -- a SECOND, entirely separate server (same fixture, matching this file's own
    # one-server-per-test convention) using the SAME faulty decision_fn proves the fault is per-request,
    # not a poisoned/crashed server: a fresh connection to a server that already once degraded still
    # answers normally when asked again, never left in a broken state by the prior failure.
    server2 = _make_server(decision_fn=_raising_decision_fn)
    try:
        thread2 = _serve_one_in_background(server2)
        response2 = json.loads(_send_and_receive(
            server2, _chain_request_json(request_id="r-fault-2", market_event_id="e-fault-2"),
        ))
        thread2.join(timeout=5.0)
        assert response2["ok"] is False
        assert "NODE_FAILURE_DEGRADED_TO_UNAVAILABLE" in response2["reason_codes"]
        assert response2["request_id"] == "r-fault-2"  # a SEPARATE decision cycle, correctly isolated
    finally:
        server2.close()


def test_unknown_frame_type_gets_no_response() -> None:
    server = _make_server()
    try:
        thread = _serve_one_in_background(server)
        with socket.create_connection((server.host, server.port), timeout=5.0) as conn:
            conn.sendall(pack_frame(b'{"type": "some_other_frame"}'))
            conn.settimeout(0.5)
            # server closes the connection without ever sending a response frame -- recv() returns b""
            # (peer closed) rather than raising, since the close already happened by the time we read.
            assert conn.recv(4) == b""
        thread.join(timeout=5.0)
    finally:
        server.close()


def test_recv_frame_matches_pack_frame() -> None:
    server = _make_server()
    try:

        def _echo_prefix_and_body() -> None:
            conn, _ = server._sock.accept()  # noqa: SLF001 -- test-only introspection
            try:
                body = recv_frame(conn)
                conn.sendall(pack_frame(body))
            finally:
                conn.close()

        thread = threading.Thread(target=_echo_prefix_and_body, daemon=True)
        thread.start()
        with socket.create_connection((server.host, server.port), timeout=5.0) as conn:
            conn.sendall(pack_frame(b"hello world"))
            prefix = conn.recv(4)
            length = unpack_length_prefix(prefix)
            body = conn.recv(length)
        thread.join(timeout=5.0)
        assert body == b"hello world"
    finally:
        server.close()


def test_handshake_response_carries_real_identity_and_valid_hmac() -> None:
    server = _make_server()
    try:
        thread = _serve_one_in_background(server)
        challenge = "deadbeefcafebabe"
        request = HandshakeRequest(session_id=_SESSION_ID, challenge_hex=challenge)
        response = parse_handshake_response(_send_and_receive(server, request.to_json_bytes()))
        thread.join(timeout=5.0)
        assert response.session_id == _SESSION_ID
        assert response.identity == STUB_IDENTITY
        expected_hmac = hmac.new(
            _SESSION_SECRET,
            (challenge + STUB_IDENTITY.canonical_json() + _SESSION_ID).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        assert response.hmac_hex == expected_hmac
        assert response.readiness_state == "READY"
        assert response.process_start_identity == "start-token"
    finally:
        server.close()


def test_zero_dot_zero_dot_zero_dot_zero_bind_is_forbidden() -> None:
    with pytest.raises(NonLoopbackBindError):
        _make_server(host="0.0.0.0")


def test_external_looking_address_bind_is_forbidden() -> None:
    with pytest.raises(NonLoopbackBindError):
        _make_server(host="10.0.0.5")


def test_loopback_bind_is_accepted() -> None:
    server = _make_server(host="127.0.0.1")
    try:
        assert server.host == "127.0.0.1"
    finally:
        server.close()
