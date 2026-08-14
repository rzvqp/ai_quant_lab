"""`TowerClient` operational-safety tests (CEO mandate section 4) -- a minimal, hand-rolled fake TCP
responder built directly from `tower_protocol`'s own framing functions, deliberately NOT importing
`ve_tower_worker` (that package is only ever installed in the separate tower venv -- this main-venv test
suite proves the CLIENT's own safety properties independent of the real worker's implementation; the real
worker is exercised for real in `test_tower_isolation.py`)."""

from __future__ import annotations

import json
import socket
import threading

from ai_trader.new_brain_bridge.tower_client import (
    TowerClient,
    TowerClientConfig,
    TowerN3N4Result,
    TowerUnavailableResult,
)
from ai_trader.new_brain_bridge.tower_protocol import (
    CONNECTION_FAILED,
    MALFORMED_RESPONSE,
    PROTOCOL_VERSION_MISMATCH,
    RESPONSE_IDENTITY_MISMATCH,
    STALE_RESPONSE,
    TowerRequest,
    pack_frame,
    unpack_length_prefix,
)


def _sample_request(**overrides: object) -> TowerRequest:
    fields: dict[str, object] = dict(
        request_id="req-1", market_event_id="evt-1", event_fingerprint="fp-1", data_identity="data-1",
        node_input_fingerprint="nif-1", symbol="XAUUSD", as_of="2026-08-14T12:00:00Z",
        n1_output={}, n2_output={}, m15_closed_bars=(), m5_closed_bars=(), strategy_id="trend_pullback",
        strategy_version="1.0",
    )
    fields.update(overrides)
    return TowerRequest(**fields)  # type: ignore[arg-type]


class _FakeServer:
    """Accepts exactly one connection, sends back whatever `response_bytes` was configured (or hangs
    until timeout if `hang=True`), and records how many connections it actually accepted -- used to
    prove the client's cache never re-hits the network for a duplicate request."""

    def __init__(self, response_bytes: bytes | None = None, hang: bool = False) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("127.0.0.1", 0))
        self._sock.listen(5)
        self.host, self.port = self._sock.getsockname()
        self._response_bytes = response_bytes
        self._hang = hang
        self.connection_count = 0
        self._stop = False
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def _serve(self) -> None:
        while not self._stop:
            self._sock.settimeout(0.2)
            try:
                conn, _ = self._sock.accept()
            except OSError:
                continue
            self.connection_count += 1
            try:
                if self._hang:
                    conn.settimeout(0.05)
                    try:
                        conn.recv(4)
                    except OSError:
                        pass
                elif self._response_bytes is not None:
                    prefix = b""
                    while len(prefix) < 4:
                        prefix += conn.recv(4 - len(prefix))
                    length = unpack_length_prefix(prefix)
                    body = b""
                    while len(body) < length:
                        body += conn.recv(length - len(body))
                    conn.sendall(pack_frame(self._response_bytes))
            finally:
                conn.close()

    def stop(self) -> None:
        self._stop = True
        self._sock.close()
        self._thread.join(timeout=2.0)


def _response_json(**fields: object) -> bytes:
    base = {
        "protocol_version": "1.0", "schema_version": "1.0", "request_id": "req-1",
        "market_event_id": "evt-1", "event_fingerprint": "fp-1", "tower_version": "0.1.0", "ok": True,
        "n3_output": {"a": 1}, "n4_output": None, "reason_codes": [],
    }
    base.update(fields)
    return json.dumps(base).encode("utf-8")


def test_successful_round_trip() -> None:
    server = _FakeServer(response_bytes=_response_json())
    try:
        client = TowerClient(TowerClientConfig(host=server.host, port=server.port, timeout_seconds=2.0))
        result = client.request_n3_n4(_sample_request())
        assert isinstance(result, TowerN3N4Result)
        assert result.n3_output == {"a": 1}
    finally:
        server.stop()


def test_connection_refused_is_tower_unavailable() -> None:
    client = TowerClient(TowerClientConfig(host="127.0.0.1", port=1, timeout_seconds=1.0))
    result = client.request_n3_n4(_sample_request())
    assert isinstance(result, TowerUnavailableResult)
    assert result.reason == CONNECTION_FAILED


def test_hanging_worker_times_out_to_tower_unavailable() -> None:
    server = _FakeServer(hang=True)
    try:
        client = TowerClient(TowerClientConfig(host=server.host, port=server.port, timeout_seconds=0.3))
        result = client.request_n3_n4(_sample_request())
        assert isinstance(result, TowerUnavailableResult)
        assert result.reason == CONNECTION_FAILED
    finally:
        server.stop()


def test_malformed_response_is_refused() -> None:
    server = _FakeServer(response_bytes=b"not json")
    try:
        client = TowerClient(TowerClientConfig(host=server.host, port=server.port, timeout_seconds=2.0))
        result = client.request_n3_n4(_sample_request())
        assert isinstance(result, TowerUnavailableResult)
        assert result.reason == MALFORMED_RESPONSE
    finally:
        server.stop()


def test_protocol_version_mismatch_is_refused() -> None:
    server = _FakeServer(response_bytes=_response_json(protocol_version="99.0"))
    try:
        client = TowerClient(TowerClientConfig(host=server.host, port=server.port, timeout_seconds=2.0))
        result = client.request_n3_n4(_sample_request())
        assert isinstance(result, TowerUnavailableResult)
        assert result.reason == PROTOCOL_VERSION_MISMATCH
    finally:
        server.stop()


def test_response_identity_mismatch_is_refused() -> None:
    server = _FakeServer(response_bytes=_response_json(request_id="someone-elses-request"))
    try:
        client = TowerClient(TowerClientConfig(host=server.host, port=server.port, timeout_seconds=2.0))
        result = client.request_n3_n4(_sample_request())
        assert isinstance(result, TowerUnavailableResult)
        assert result.reason == RESPONSE_IDENTITY_MISMATCH
    finally:
        server.stop()


def test_stale_response_same_request_id_different_event_is_refused() -> None:
    """The specific 'rezultat TARDIV pentru alt eveniment' scenario: request_id reused, but the event
    it actually answers is a different one -- the client must not silently accept it as the answer to
    THIS request."""
    server = _FakeServer(response_bytes=_response_json(event_fingerprint="a-different-event-fp"))
    try:
        client = TowerClient(TowerClientConfig(host=server.host, port=server.port, timeout_seconds=2.0))
        result = client.request_n3_n4(_sample_request())
        assert isinstance(result, TowerUnavailableResult)
        assert result.reason == STALE_RESPONSE
    finally:
        server.stop()


def test_worker_own_refusal_reason_is_propagated() -> None:
    server = _FakeServer(response_bytes=_response_json(ok=False, reason_codes=["TOWER_UNAVAILABLE"]))
    try:
        client = TowerClient(TowerClientConfig(host=server.host, port=server.port, timeout_seconds=2.0))
        result = client.request_n3_n4(_sample_request())
        assert isinstance(result, TowerUnavailableResult)
        assert result.reason == "TOWER_UNAVAILABLE"
    finally:
        server.stop()


def test_duplicate_request_is_idempotent_and_never_re_hits_the_network() -> None:
    server = _FakeServer(response_bytes=_response_json())
    try:
        client = TowerClient(TowerClientConfig(host=server.host, port=server.port, timeout_seconds=2.0))
        request = _sample_request()
        first = client.request_n3_n4(request)
        second = client.request_n3_n4(request)
        assert first == second
        assert server.connection_count == 1
    finally:
        server.stop()


def test_health_check_true_when_listening() -> None:
    server = _FakeServer(response_bytes=_response_json())
    try:
        client = TowerClient(TowerClientConfig(host=server.host, port=server.port, timeout_seconds=1.0))
        assert client.health_check() is True
    finally:
        server.stop()


def test_health_check_false_when_nothing_listening() -> None:
    client = TowerClient(TowerClientConfig(host="127.0.0.1", port=1, timeout_seconds=1.0))
    assert client.health_check() is False
