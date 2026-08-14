"""TCP loopback server for the isolated tower worker. Binds `127.0.0.1` only (never `0.0.0.0` -- this is a
strictly local IPC boundary, never meant to accept a connection from another host). One connection, one
request, one response -- no persistent session state, no server-side memory of prior requests, matching
the "duplicate request -> IDEMPOTENT result" requirement structurally: the same request bytes in always
produce the same response bytes out, because nothing here depends on anything but the request itself.
"""

from __future__ import annotations

import json
import socket
from collections.abc import Callable

from ve_tower_worker.decision import real_decision
from ve_tower_worker.protocol import (
    MALFORMED_REQUEST,
    PROTOCOL_VERSION,
    PROTOCOL_VERSION_MISMATCH,
    ProtocolValidationError,
    RESPONSE_SCHEMA_VERSION,
    TowerRequest,
    TowerResponse,
    pack_frame,
    parse_request,
    unpack_length_prefix,
)

DecisionFn = Callable[[TowerRequest], TowerResponse]


class TowerConnectionClosed(Exception):
    """Raised when the peer closes the connection mid-frame (fewer bytes than declared)."""


def _recv_exact(conn: socket.socket, n: int) -> bytes:
    chunks: list[bytes] = []
    remaining = n
    while remaining > 0:
        chunk = conn.recv(remaining)
        if not chunk:
            raise TowerConnectionClosed(f"connection closed after {n - remaining} of {n} bytes")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def recv_frame(conn: socket.socket) -> bytes:
    prefix = _recv_exact(conn, 4)
    length = unpack_length_prefix(prefix)
    return _recv_exact(conn, length)


def _best_effort_echo_fields(request_bytes: bytes) -> tuple[str, str, str]:
    """Used only to build a diagnosable error response when `parse_request` itself fails -- best-effort,
    never trusted for anything beyond echoing identity back to a caller that already sent bad data."""
    try:
        obj = json.loads(request_bytes.decode("utf-8", errors="replace"))
        if not isinstance(obj, dict):
            obj = {}
    except (UnicodeDecodeError, json.JSONDecodeError):
        obj = {}
    def _str_or_unknown(key: str) -> str:
        value = obj.get(key)
        return value if isinstance(value, str) else "UNKNOWN"

    return _str_or_unknown("request_id"), _str_or_unknown("market_event_id"), _str_or_unknown("event_fingerprint")


class TowerWorkerServer:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 0,
        decision_fn: DecisionFn = real_decision,
        timeout_seconds: float = 30.0,
    ) -> None:
        self._decision_fn = decision_fn
        self._timeout_seconds = timeout_seconds
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((host, port))
        self._sock.listen(5)
        self.host, self.port = self._sock.getsockname()

    def build_response(self, request_bytes: bytes) -> TowerResponse:
        try:
            request = parse_request(request_bytes)
        except ProtocolValidationError:
            request_id, market_event_id, event_fingerprint = _best_effort_echo_fields(request_bytes)
            return TowerResponse(
                protocol_version=PROTOCOL_VERSION,
                schema_version=RESPONSE_SCHEMA_VERSION,
                request_id=request_id,
                market_event_id=market_event_id,
                event_fingerprint=event_fingerprint,
                tower_version="UNAVAILABLE",
                ok=False,
                n3_output=None,
                n4_output=None,
                reason_codes=(MALFORMED_REQUEST,),
            )
        if request.protocol_version != PROTOCOL_VERSION:
            return TowerResponse(
                protocol_version=PROTOCOL_VERSION,
                schema_version=RESPONSE_SCHEMA_VERSION,
                request_id=request.request_id,
                market_event_id=request.market_event_id,
                event_fingerprint=request.event_fingerprint,
                tower_version="UNAVAILABLE",
                ok=False,
                n3_output=None,
                n4_output=None,
                reason_codes=(PROTOCOL_VERSION_MISMATCH,),
            )
        return self._decision_fn(request)

    def handle_one_connection(self) -> None:
        conn, _addr = self._sock.accept()
        try:
            conn.settimeout(self._timeout_seconds)
            request_bytes = recv_frame(conn)
            response = self.build_response(request_bytes)
            conn.sendall(pack_frame(response.to_json_bytes()))
        except (TowerConnectionClosed, ProtocolValidationError, TimeoutError, OSError):
            pass
        finally:
            conn.close()

    def serve_forever(self) -> None:
        while True:
            self.handle_one_connection()

    def close(self) -> None:
        self._sock.close()
