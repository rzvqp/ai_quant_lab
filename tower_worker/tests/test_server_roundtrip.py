from __future__ import annotations

import hashlib
import hmac
import socket
import threading

import pytest

from ve_tower_worker.artifact_identity_stub import STUB_IDENTITY, stub_read_worker_identity
from ve_tower_worker.decision_stub import FAKE_TOWER_VERSION, fake_decision
from ve_tower_worker.protocol import (
    FRAME_TYPE_N3N4_REQUEST,
    MALFORMED_REQUEST,
    PROTOCOL_VERSION_MISMATCH,
    HandshakeRequest,
    parse_handshake_response,
    parse_response,
    pack_frame,
    unpack_length_prefix,
)
from ve_tower_worker.server import NonLoopbackBindError, TowerWorkerServer, recv_frame

_SESSION_ID = "test-session-1"
_SESSION_SECRET = b"test-secret-bytes-0123456789ab"


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
        request_json = (
            b'{"type": "' + FRAME_TYPE_N3N4_REQUEST.encode() + b'", "protocol_version": "2.0", '
            b'"schema_version": "1.0", "request_id": "r1", '
            b'"market_event_id": "e1", "event_fingerprint": "f1", "data_identity": "d1", '
            b'"node_input_fingerprint": "n1", "symbol": "XAUUSD", "as_of": "2026-08-14T00:00:00Z", '
            b'"n1_output": {}, "n2_output": {}, "m15_closed_bars": [], "m5_closed_bars": [], '
            b'"strategy_id": "trend_pullback", "strategy_version": "1.0"}'
        )
        response_bytes = _send_and_receive(server, request_json)
        response = parse_response(response_bytes)
        thread.join(timeout=5.0)
        assert response.ok
        assert response.request_id == "r1"
        assert response.market_event_id == "e1"
        assert response.event_fingerprint == "f1"
        assert response.tower_version == FAKE_TOWER_VERSION
        assert response.reason_codes == ("STUB_FIXTURE_RESPONSE",)
        # session/identity are stamped by the SERVER, unconditionally -- never left to decision_fn
        assert response.session_id == _SESSION_ID
        assert response.worker_identity_fingerprint == STUB_IDENTITY.fingerprint()
    finally:
        server.close()


def test_protocol_version_mismatch_is_refused() -> None:
    server = _make_server()
    try:
        thread = _serve_one_in_background(server)
        request_json = (
            b'{"type": "' + FRAME_TYPE_N3N4_REQUEST.encode() + b'", "protocol_version": "99.0", '
            b'"schema_version": "1.0", "request_id": "r2", '
            b'"market_event_id": "e2", "event_fingerprint": "f2", "data_identity": "d1", '
            b'"node_input_fingerprint": "n1", "symbol": "XAUUSD", "as_of": "2026-08-14T00:00:00Z", '
            b'"n1_output": {}, "n2_output": {}, "m15_closed_bars": [], "m5_closed_bars": [], '
            b'"strategy_id": "trend_pullback", "strategy_version": "1.0"}'
        )
        response = parse_response(_send_and_receive(server, request_json))
        thread.join(timeout=5.0)
        assert not response.ok
        assert response.reason_codes == (PROTOCOL_VERSION_MISMATCH,)
        assert response.request_id == "r2"
        assert response.market_event_id == "e2"
        assert response.session_id == _SESSION_ID
    finally:
        server.close()


def test_malformed_request_gets_diagnosable_refusal() -> None:
    server = _make_server()
    try:
        thread = _serve_one_in_background(server)
        response = parse_response(_send_and_receive(server, b'{"type": "n3n4_request"}'))
        thread.join(timeout=5.0)
        assert not response.ok
        assert response.reason_codes == (MALFORMED_REQUEST,)
        assert response.request_id == "UNKNOWN"
    finally:
        server.close()


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
