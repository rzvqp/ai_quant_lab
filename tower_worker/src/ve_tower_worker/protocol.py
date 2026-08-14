"""Versioned local IPC contract between AI Trader (client) and the isolated tower worker (server).

**v2, 2026-08-14 (Red Team remediation, `TOWER_HANDOFF_CONDITIONAL`)**: adds the session handshake
(`HandshakeRequest`/`HandshakeResponse`/`WorkerIdentity`) and per-response session/identity binding
(`TowerResponse.session_id`/`worker_identity_fingerprint`). A frame's `type` field discriminates
handshake frames from N3/N4 request/response frames on the same wire -- see `FRAME_TYPE_*`.

**Transport choice, and why**: a plain TCP socket on `127.0.0.1` ONLY (never `0.0.0.0`, never a
non-loopback address -- enforced at the server's construction site, see `server.py`), with a 4-byte
big-endian length prefix followed by UTF-8 JSON bytes (`json.dumps(..., sort_keys=True)` for deterministic
serialization). Considered and rejected:
- `multiprocessing.connection` (stdlib, would work on both venvs with zero extra dependency) -- rejected
  because its own `Connection.send()`/`recv()` convenience methods pickle by default; defending against
  someone later calling those instead of the raw `send_bytes()`/`recv_bytes()` methods is a standing footgun
  this contract avoids entirely by not depending on that module at all.
- Named pipes -- rejected because a correct Windows implementation needs `pywin32`, adding a dependency to
  BOTH venvs for something a loopback TCP socket already does with zero dependencies.
- gRPC/protobuf -- rejected as disproportionate: the whole point of the tower venv is a minimal, auditable
  dependency surface (numpy + pandas, pinned, hashed -- nothing else); a schema-compiler toolchain works
  against that goal for a single local request/response pair.

**No pickle. No `eval`/`exec` of transmitted data anywhere in this module.** Every field is a JSON
primitive; every value is validated against an explicit type before use, on both ends, matching this
codebase's own established fail-closed `assert isinstance(...)` convention (see `new_brain_bridge/telemetry.py`).

**The session secret never appears in this module, on the wire, in any frame, in any log line, or in any
exception message.** It is handed off out-of-band (worker's own stdin, at process launch -- see `cli.py`)
and used only as an HMAC key, computed and compared locally on each side. Only the resulting `hmac_hex`
crosses the wire.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

PROTOCOL_VERSION = "2.0"
REQUEST_SCHEMA_VERSION = "1.0"
RESPONSE_SCHEMA_VERSION = "2.0"

MAX_PAYLOAD_BYTES = 4 * 1024 * 1024
"""Enforced on both the outgoing serialize (client and server refuse to send an oversized frame) and the
incoming length-prefix read (refuses to allocate a buffer for a length prefix that exceeds this, closing
the connection instead) -- the second check is the one that actually matters for safety: it bounds memory
allocation against a malformed or hostile length prefix before a single payload byte is read."""

FRAME_TYPE_HANDSHAKE = "handshake"
FRAME_TYPE_HANDSHAKE_RESPONSE = "handshake_response"
FRAME_TYPE_N3N4_REQUEST = "n3n4_request"
FRAME_TYPE_N3N4_RESPONSE = "n3n4_response"

TOWER_UNAVAILABLE = "TOWER_UNAVAILABLE"
PROTOCOL_VERSION_MISMATCH = "PROTOCOL_VERSION_MISMATCH"
MALFORMED_REQUEST = "MALFORMED_REQUEST"
PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"
RESPONSE_IDENTITY_MISMATCH = "RESPONSE_IDENTITY_MISMATCH"
STALE_RESPONSE = "STALE_RESPONSE"
STALE_SESSION = "STALE_SESSION"
REQUEST_ID_REUSE_MISMATCH = "REQUEST_ID_REUSE_MISMATCH"
NON_LOOPBACK_BIND_FORBIDDEN = "NON_LOOPBACK_BIND_FORBIDDEN"
HANDSHAKE_HMAC_MISMATCH = "HANDSHAKE_HMAC_MISMATCH"
HANDSHAKE_IDENTITY_MISMATCH = "HANDSHAKE_IDENTITY_MISMATCH"
HANDSHAKE_SESSION_ID_MISMATCH = "HANDSHAKE_SESSION_ID_MISMATCH"
HANDSHAKE_NOT_ESTABLISHED = "HANDSHAKE_NOT_ESTABLISHED"


class ProtocolValidationError(Exception):
    """Fail-closed: raised by `parse_*` on any missing field, wrong type, or malformed shape. Never
    partially trust a parsed payload."""


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkerIdentity:
    """Every field the CEO's own handshake spec names, with correctly SEPARATED identities (per the
    CEO's own correction: `6daf2aa` is `package_build_commit`, never a stand-in for "source identity of
    every ratified module"). Fields the worker cannot yet determine (because `ve_tower` is not installed,
    or because VE's manifest has not yet supplied a value) are `None` -- honest absence, never a
    fabricated placeholder."""

    worker_package_version: str
    worker_build_commit: str
    protocol_version: str
    ve_tower_package_version: str | None
    package_build_commit: str | None
    state_delivery_commit: str | None
    wheel_sha256: str | None
    vendored_source_identity: str | None
    n3_contract_version: str | None
    n4_contract_version: str | None

    def as_dict(self) -> dict[str, object]:
        return {
            "worker_package_version": self.worker_package_version,
            "worker_build_commit": self.worker_build_commit,
            "protocol_version": self.protocol_version,
            "ve_tower_package_version": self.ve_tower_package_version,
            "package_build_commit": self.package_build_commit,
            "state_delivery_commit": self.state_delivery_commit,
            "wheel_sha256": self.wheel_sha256,
            "vendored_source_identity": self.vendored_source_identity,
            "n3_contract_version": self.n3_contract_version,
            "n4_contract_version": self.n4_contract_version,
        }

    def canonical_json(self) -> str:
        """Deterministic (`sort_keys=True`) representation -- the exact bytes fed into the HMAC and hashed
        for the response-binding fingerprint. Both sides must produce byte-identical output for the same
        logical identity, or the handshake can never agree even when nothing is actually wrong."""
        return json.dumps(self.as_dict(), sort_keys=True)

    def fingerprint(self) -> str:
        import hashlib

        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def worker_identity_from_dict(obj: dict[str, object]) -> WorkerIdentity:
    def _opt_str(key: str) -> str | None:
        value = obj.get(key)
        if value is None:
            return None
        if not isinstance(value, str):
            raise ProtocolValidationError(f"MALFORMED_REQUEST: field '{key}' must be a string or null")
        return value

    return WorkerIdentity(
        worker_package_version=_require_str(obj, "worker_package_version"),
        worker_build_commit=_require_str(obj, "worker_build_commit"),
        protocol_version=_require_str(obj, "protocol_version"),
        ve_tower_package_version=_opt_str("ve_tower_package_version"),
        package_build_commit=_opt_str("package_build_commit"),
        state_delivery_commit=_opt_str("state_delivery_commit"),
        wheel_sha256=_opt_str("wheel_sha256"),
        vendored_source_identity=_opt_str("vendored_source_identity"),
        n3_contract_version=_opt_str("n3_contract_version"),
        n4_contract_version=_opt_str("n4_contract_version"),
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class HandshakeRequest:
    session_id: str
    challenge_hex: str
    type: str = FRAME_TYPE_HANDSHAKE

    def to_json_bytes(self) -> bytes:
        payload = {"type": self.type, "session_id": self.session_id, "challenge_hex": self.challenge_hex}
        return json.dumps(payload, sort_keys=True).encode("utf-8")


@dataclass(frozen=True, slots=True, kw_only=True)
class HandshakeResponse:
    session_id: str
    hmac_hex: str
    identity: WorkerIdentity
    pid: int
    process_start_identity: str
    readiness_state: str
    type: str = FRAME_TYPE_HANDSHAKE_RESPONSE

    def to_json_bytes(self) -> bytes:
        payload = {
            "type": self.type,
            "session_id": self.session_id,
            "hmac_hex": self.hmac_hex,
            "identity": self.identity.as_dict(),
            "pid": self.pid,
            "process_start_identity": self.process_start_identity,
            "readiness_state": self.readiness_state,
        }
        return json.dumps(payload, sort_keys=True).encode("utf-8")


@dataclass(frozen=True, slots=True, kw_only=True)
class TowerRequest:
    protocol_version: str
    schema_version: str
    request_id: str
    market_event_id: str
    event_fingerprint: str
    data_identity: str
    node_input_fingerprint: str
    symbol: str
    as_of: str
    n1_output: dict[str, object]
    n2_output: dict[str, object]
    m15_closed_bars: tuple[dict[str, object], ...]
    m5_closed_bars: tuple[dict[str, object], ...]
    strategy_id: str
    strategy_version: str
    type: str = FRAME_TYPE_N3N4_REQUEST

    def to_json_bytes(self) -> bytes:
        payload = {
            "type": self.type,
            "protocol_version": self.protocol_version,
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "market_event_id": self.market_event_id,
            "event_fingerprint": self.event_fingerprint,
            "data_identity": self.data_identity,
            "node_input_fingerprint": self.node_input_fingerprint,
            "symbol": self.symbol,
            "as_of": self.as_of,
            "n1_output": self.n1_output,
            "n2_output": self.n2_output,
            "m15_closed_bars": list(self.m15_closed_bars),
            "m5_closed_bars": list(self.m5_closed_bars),
            "strategy_id": self.strategy_id,
            "strategy_version": self.strategy_version,
        }
        return json.dumps(payload, sort_keys=True).encode("utf-8")


@dataclass(frozen=True, slots=True, kw_only=True)
class TowerResponse:
    protocol_version: str
    schema_version: str
    request_id: str
    market_event_id: str
    event_fingerprint: str
    tower_version: str
    ok: bool
    n3_output: dict[str, object] | None
    n4_output: dict[str, object] | None
    session_id: str
    worker_identity_fingerprint: str
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    type: str = FRAME_TYPE_N3N4_RESPONSE

    def to_json_bytes(self) -> bytes:
        payload = {
            "type": self.type,
            "protocol_version": self.protocol_version,
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "market_event_id": self.market_event_id,
            "event_fingerprint": self.event_fingerprint,
            "tower_version": self.tower_version,
            "ok": self.ok,
            "n3_output": self.n3_output,
            "n4_output": self.n4_output,
            "session_id": self.session_id,
            "worker_identity_fingerprint": self.worker_identity_fingerprint,
            "reason_codes": list(self.reason_codes),
        }
        return json.dumps(payload, sort_keys=True).encode("utf-8")


def _require_str(obj: dict[str, object], key: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str):
        raise ProtocolValidationError(f"MALFORMED_REQUEST: field '{key}' missing or not a string")
    return value


def _require_int(obj: dict[str, object], key: str) -> int:
    value = obj.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ProtocolValidationError(f"MALFORMED_REQUEST: field '{key}' missing or not an int")
    return value


def _require_dict(obj: dict[str, object], key: str) -> dict[str, object]:
    value = obj.get(key)
    if not isinstance(value, dict):
        raise ProtocolValidationError(f"MALFORMED_REQUEST: field '{key}' missing or not an object")
    return value


def _require_bar_list(obj: dict[str, object], key: str) -> tuple[dict[str, object], ...]:
    value = obj.get(key)
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ProtocolValidationError(f"MALFORMED_REQUEST: field '{key}' missing or not a list of objects")
    return tuple(value)


def peek_frame_type(raw: bytes) -> str:
    """Reads only the `type` discriminator, for routing before full parsing. Fail-closed: any non-object
    JSON, invalid JSON, or missing/non-string `type` raises rather than defaulting to a guess."""
    try:
        obj = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolValidationError(f"MALFORMED_REQUEST: not valid JSON ({exc})") from exc
    if not isinstance(obj, dict):
        raise ProtocolValidationError("MALFORMED_REQUEST: top-level JSON value is not an object")
    return _require_str(obj, "type")


def parse_handshake_request(raw: bytes) -> HandshakeRequest:
    obj = _parse_object(raw)
    return HandshakeRequest(
        session_id=_require_str(obj, "session_id"), challenge_hex=_require_str(obj, "challenge_hex"),
    )


def parse_handshake_response(raw: bytes) -> HandshakeResponse:
    obj = _parse_object(raw)
    identity_obj = _require_dict(obj, "identity")
    return HandshakeResponse(
        session_id=_require_str(obj, "session_id"), hmac_hex=_require_str(obj, "hmac_hex"),
        identity=worker_identity_from_dict(identity_obj), pid=_require_int(obj, "pid"),
        process_start_identity=_require_str(obj, "process_start_identity"),
        readiness_state=_require_str(obj, "readiness_state"),
    )


def _parse_object(raw: bytes) -> dict[str, object]:
    try:
        obj = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolValidationError(f"MALFORMED_REQUEST: not valid JSON ({exc})") from exc
    if not isinstance(obj, dict):
        raise ProtocolValidationError("MALFORMED_REQUEST: top-level JSON value is not an object")
    return obj


def parse_request(raw: bytes) -> TowerRequest:
    """Fail-closed: any missing/mistyped field raises `ProtocolValidationError` before a `TowerRequest`
    is ever constructed -- the server never operates on a partially-trusted object."""
    obj = _parse_object(raw)
    return TowerRequest(
        protocol_version=_require_str(obj, "protocol_version"),
        schema_version=_require_str(obj, "schema_version"),
        request_id=_require_str(obj, "request_id"),
        market_event_id=_require_str(obj, "market_event_id"),
        event_fingerprint=_require_str(obj, "event_fingerprint"),
        data_identity=_require_str(obj, "data_identity"),
        node_input_fingerprint=_require_str(obj, "node_input_fingerprint"),
        symbol=_require_str(obj, "symbol"),
        as_of=_require_str(obj, "as_of"),
        n1_output=_require_dict(obj, "n1_output"),
        n2_output=_require_dict(obj, "n2_output"),
        m15_closed_bars=_require_bar_list(obj, "m15_closed_bars"),
        m5_closed_bars=_require_bar_list(obj, "m5_closed_bars"),
        strategy_id=_require_str(obj, "strategy_id"),
        strategy_version=_require_str(obj, "strategy_version"),
    )


def parse_response(raw: bytes) -> TowerResponse:
    """Fail-closed, mirroring `parse_request`. Called by the CLIENT on the worker's reply -- a malformed
    reply must never be silently treated as a valid (even if empty) N3/N4 output."""
    obj = _parse_object(raw)
    ok = obj.get("ok")
    if not isinstance(ok, bool):
        raise ProtocolValidationError("MALFORMED_REQUEST: field 'ok' missing or not a bool")
    n3_output = obj.get("n3_output")
    if n3_output is not None and not isinstance(n3_output, dict):
        raise ProtocolValidationError("MALFORMED_REQUEST: field 'n3_output' not an object or null")
    n4_output = obj.get("n4_output")
    if n4_output is not None and not isinstance(n4_output, dict):
        raise ProtocolValidationError("MALFORMED_REQUEST: field 'n4_output' not an object or null")
    reason_codes_raw = obj.get("reason_codes")
    if not isinstance(reason_codes_raw, list) or not all(isinstance(r, str) for r in reason_codes_raw):
        raise ProtocolValidationError("MALFORMED_REQUEST: field 'reason_codes' missing or not a list of strings")
    return TowerResponse(
        protocol_version=_require_str(obj, "protocol_version"),
        schema_version=_require_str(obj, "schema_version"),
        request_id=_require_str(obj, "request_id"),
        market_event_id=_require_str(obj, "market_event_id"),
        event_fingerprint=_require_str(obj, "event_fingerprint"),
        tower_version=_require_str(obj, "tower_version"),
        ok=ok,
        n3_output=n3_output,
        n4_output=n4_output,
        session_id=_require_str(obj, "session_id"),
        worker_identity_fingerprint=_require_str(obj, "worker_identity_fingerprint"),
        reason_codes=tuple(reason_codes_raw),
    )


def pack_frame(payload: bytes) -> bytes:
    """4-byte big-endian length prefix + payload. Raises `ProtocolValidationError` (not a silent truncate)
    if the payload exceeds `MAX_PAYLOAD_BYTES` -- enforced on the SEND side too, not only on receive."""
    if len(payload) > MAX_PAYLOAD_BYTES:
        raise ProtocolValidationError(f"PAYLOAD_TOO_LARGE: {len(payload)} bytes > {MAX_PAYLOAD_BYTES}")
    return len(payload).to_bytes(4, "big") + payload


def unpack_length_prefix(prefix: bytes) -> int:
    """Decodes the 4-byte length prefix and enforces `MAX_PAYLOAD_BYTES` BEFORE any attempt to read that
    many bytes off the socket -- the check that actually bounds memory allocation against a hostile or
    corrupted prefix."""
    if len(prefix) != 4:
        raise ProtocolValidationError("MALFORMED_REQUEST: length prefix must be exactly 4 bytes")
    length = int.from_bytes(prefix, "big")
    if length > MAX_PAYLOAD_BYTES:
        raise ProtocolValidationError(f"PAYLOAD_TOO_LARGE: declared length {length} > {MAX_PAYLOAD_BYTES}")
    return length
