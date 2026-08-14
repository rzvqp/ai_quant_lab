"""TCP loopback server for the isolated tower worker.

**Loopback-only bind, enforced structurally.** `host` is checked against `LOOPBACK_ALLOWED_HOSTS` BEFORE
the socket is even constructed -- `--host 0.0.0.0` (or any other non-loopback address) is refused with
`NonLoopbackBindError` before a single syscall touches the network. `::1` is deliberately NOT in the
allowlist yet -- the CEO's own mandate made it explicitly optional ("optional ::1 daca e implementat si
testat corect"), and adding IPv6 support without dedicated tests for it would be exactly the kind of
half-verified addition this remediation exists to eliminate elsewhere.

**Session handshake.** Every connection's first frame is dispatched by its `type` field
(`FRAME_TYPE_HANDSHAKE` vs `FRAME_TYPE_N3N4_REQUEST`) -- see `protocol.peek_frame_type`. A handshake frame
gets a `HandshakeResponse` carrying the worker's REAL identity (read once at construction from
`identity_fn`, never re-derived from anything a client sends) and an HMAC over
`challenge + canonical_identity + session_id`, keyed by the session secret handed off via `cli.py`'s stdin
channel at launch -- never sent over this socket. Every N3/N4 response is stamped with the worker's own
`session_id`/`worker_identity_fingerprint` by THIS module, unconditionally, overwriting whatever
`decision_fn` returned for those two fields -- `decision.py`/`decision_stub.py` stay session-unaware by
design; this is the one place those fields become authoritative.

One connection, one request, one response -- no persistent per-connection state beyond the session itself,
matching the "duplicate request -> IDEMPOTENT result" requirement structurally: the same request bytes in
always produce the same response bytes out (aside from the session fields, constant for the worker's
whole lifetime), because nothing here depends on anything but the request itself.
"""

from __future__ import annotations

import dataclasses
import hashlib
import hmac
import json
import os
import socket
from collections.abc import Callable

from ve_tower_worker.artifact_identity import read_real_worker_identity
from ve_tower_worker.decision import real_decision
from ve_tower_worker.protocol import (
    FRAME_TYPE_HANDSHAKE,
    FRAME_TYPE_N3N4_REQUEST,
    MALFORMED_REQUEST,
    PROTOCOL_VERSION,
    PROTOCOL_VERSION_MISMATCH,
    ProtocolValidationError,
    RESPONSE_SCHEMA_VERSION,
    HandshakeResponse,
    TowerRequest,
    TowerResponse,
    WorkerIdentity,
    pack_frame,
    parse_handshake_request,
    parse_request,
    peek_frame_type,
    unpack_length_prefix,
)

DecisionFn = Callable[[TowerRequest], TowerResponse]
IdentityFn = Callable[[], WorkerIdentity]

LOOPBACK_ALLOWED_HOSTS = ("127.0.0.1",)


class NonLoopbackBindError(Exception):
    """reason_code = NON_LOOPBACK_BIND_FORBIDDEN."""


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
        identity_fn: IdentityFn = read_real_worker_identity,
        session_id: str = "",
        session_secret: bytes = b"",
        process_start_identity: str = "",
        timeout_seconds: float = 30.0,
    ) -> None:
        if host not in LOOPBACK_ALLOWED_HOSTS:
            raise NonLoopbackBindError(
                f"NON_LOOPBACK_BIND_FORBIDDEN: {host!r} is not an allowed loopback address "
                f"(allowed: {LOOPBACK_ALLOWED_HOSTS})"
            )
        self._decision_fn = decision_fn
        self._session_id = session_id
        self._session_secret = session_secret
        self._process_start_identity = process_start_identity
        self._timeout_seconds = timeout_seconds
        self._identity = identity_fn()
        self._identity_fingerprint = self._identity.fingerprint()
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
            response = TowerResponse(
                protocol_version=PROTOCOL_VERSION, schema_version=RESPONSE_SCHEMA_VERSION,
                request_id=request_id, market_event_id=market_event_id, event_fingerprint=event_fingerprint,
                tower_version="UNAVAILABLE", ok=False, n3_output=None, n4_output=None,
                session_id="", worker_identity_fingerprint="", reason_codes=(MALFORMED_REQUEST,),
            )
            return self._stamp_session(response)
        if request.protocol_version != PROTOCOL_VERSION:
            response = TowerResponse(
                protocol_version=PROTOCOL_VERSION, schema_version=RESPONSE_SCHEMA_VERSION,
                request_id=request.request_id, market_event_id=request.market_event_id,
                event_fingerprint=request.event_fingerprint, tower_version="UNAVAILABLE", ok=False,
                n3_output=None, n4_output=None, session_id="", worker_identity_fingerprint="",
                reason_codes=(PROTOCOL_VERSION_MISMATCH,),
            )
            return self._stamp_session(response)
        return self._stamp_session(self._decision_fn(request))

    def _stamp_session(self, response: TowerResponse) -> TowerResponse:
        """The ONE place `session_id`/`worker_identity_fingerprint` become authoritative -- always
        overwrites whatever `decision_fn` returned for those two fields, so decision logic can stay
        session-unaware without any risk of it accidentally forging or omitting them."""
        return dataclasses.replace(
            response, session_id=self._session_id, worker_identity_fingerprint=self._identity_fingerprint,
        )

    def build_handshake_response_bytes(self, request_bytes: bytes) -> bytes:
        handshake_request = parse_handshake_request(request_bytes)
        mac_input = (
            handshake_request.challenge_hex + self._identity.canonical_json() + self._session_id
        ).encode("utf-8")
        hmac_hex = hmac.new(self._session_secret, mac_input, hashlib.sha256).hexdigest()
        response = HandshakeResponse(
            session_id=self._session_id, hmac_hex=hmac_hex, identity=self._identity, pid=os.getpid(),
            process_start_identity=self._process_start_identity, readiness_state="READY",
        )
        return response.to_json_bytes()

    def handle_one_connection(self) -> None:
        conn, _addr = self._sock.accept()
        try:
            conn.settimeout(self._timeout_seconds)
            request_bytes = recv_frame(conn)
            frame_type = peek_frame_type(request_bytes)
            if frame_type == FRAME_TYPE_HANDSHAKE:
                response_bytes = self.build_handshake_response_bytes(request_bytes)
            elif frame_type == FRAME_TYPE_N3N4_REQUEST:
                response_bytes = self.build_response(request_bytes).to_json_bytes()
            else:
                return  # unknown frame type -- close without responding, same as any other malformed input
            conn.sendall(pack_frame(response_bytes))
        except (TowerConnectionClosed, ProtocolValidationError, TimeoutError, OSError):
            pass
        finally:
            conn.close()

    def serve_forever(self) -> None:
        while True:
            self.handle_one_connection()

    def close(self) -> None:
        self._sock.close()
