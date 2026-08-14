from __future__ import annotations

import socket
import threading

from ve_tower_worker.decision_stub import FAKE_TOWER_VERSION, fake_decision
from ve_tower_worker.protocol import (
    MALFORMED_REQUEST,
    PROTOCOL_VERSION_MISMATCH,
    parse_response,
    pack_frame,
    unpack_length_prefix,
)
from ve_tower_worker.server import TowerWorkerServer, recv_frame


def _make_server() -> TowerWorkerServer:
    return TowerWorkerServer(host="127.0.0.1", port=0, decision_fn=fake_decision, timeout_seconds=5.0)


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
            b'{"protocol_version": "1.0", "schema_version": "1.0", "request_id": "r1", '
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
    finally:
        server.close()


def test_protocol_version_mismatch_is_refused() -> None:
    server = _make_server()
    try:
        thread = _serve_one_in_background(server)
        request_json = (
            b'{"protocol_version": "99.0", "schema_version": "1.0", "request_id": "r2", '
            b'"market_event_id": "e2", "event_fingerprint": "f2", "data_identity": "d1", '
            b'"node_input_fingerprint": "n1", "symbol": "XAUUSD", "as_of": "2026-08-14T00:00:00Z", '
            b'"n1_output": {}, "n2_output": {}, "m15_closed_bars": [], "m5_closed_bars": [], '
            b'"strategy_id": "trend_pullback", "strategy_version": "1.0"}'
        )
        response = parse_response(_send_and_receive(server, request_json))
        thread.join(timeout=5.0)
        assert not response.ok
        assert response.reason_codes == (PROTOCOL_VERSION_MISMATCH,)
        # identity still echoed even on refusal, so a caller can tell which request failed
        assert response.request_id == "r2"
        assert response.market_event_id == "e2"
    finally:
        server.close()


def test_malformed_request_gets_diagnosable_refusal() -> None:
    server = _make_server()
    try:
        thread = _serve_one_in_background(server)
        response = parse_response(_send_and_receive(server, b"not json"))
        thread.join(timeout=5.0)
        assert not response.ok
        assert response.reason_codes == (MALFORMED_REQUEST,)
        assert response.request_id == "UNKNOWN"
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
