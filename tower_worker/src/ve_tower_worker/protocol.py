"""Versioned local IPC contract between AI Trader (client) and the isolated tower worker (server).

**Transport choice, and why**: a plain TCP socket on `127.0.0.1`, with a 4-byte big-endian length prefix
followed by UTF-8 JSON bytes (`json.dumps(..., sort_keys=True)` for deterministic serialization). Considered
and rejected:
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
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

PROTOCOL_VERSION = "1.0"
REQUEST_SCHEMA_VERSION = "1.0"
RESPONSE_SCHEMA_VERSION = "1.0"

MAX_PAYLOAD_BYTES = 4 * 1024 * 1024
"""Enforced on both the outgoing serialize (client and server refuse to send an oversized frame) and the
incoming length-prefix read (refuses to allocate a buffer for a length prefix that exceeds this, closing
the connection instead) -- the second check is the one that actually matters for safety: it bounds memory
allocation against a malformed or hostile length prefix before a single payload byte is read."""

TOWER_UNAVAILABLE = "TOWER_UNAVAILABLE"
PROTOCOL_VERSION_MISMATCH = "PROTOCOL_VERSION_MISMATCH"
MALFORMED_REQUEST = "MALFORMED_REQUEST"
PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"
RESPONSE_IDENTITY_MISMATCH = "RESPONSE_IDENTITY_MISMATCH"
STALE_RESPONSE = "STALE_RESPONSE"


class ProtocolValidationError(Exception):
    """Fail-closed: raised by `validate_request`/`validate_response` on any missing field, wrong type, or
    malformed shape. Never partially trust a parsed payload."""


@dataclass(frozen=True, slots=True)
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

    def to_json_bytes(self) -> bytes:
        payload = {
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


@dataclass(frozen=True, slots=True)
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
    reason_codes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_bytes(self) -> bytes:
        payload = {
            "protocol_version": self.protocol_version,
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "market_event_id": self.market_event_id,
            "event_fingerprint": self.event_fingerprint,
            "tower_version": self.tower_version,
            "ok": self.ok,
            "n3_output": self.n3_output,
            "n4_output": self.n4_output,
            "reason_codes": list(self.reason_codes),
        }
        return json.dumps(payload, sort_keys=True).encode("utf-8")


def _require_str(obj: dict[str, object], key: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str):
        raise ProtocolValidationError(f"MALFORMED_REQUEST: field '{key}' missing or not a string")
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


def parse_request(raw: bytes) -> TowerRequest:
    """Fail-closed: any missing/mistyped field raises `ProtocolValidationError` before a `TowerRequest`
    is ever constructed -- the server never operates on a partially-trusted object."""
    try:
        obj = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolValidationError(f"MALFORMED_REQUEST: not valid JSON ({exc})") from exc
    if not isinstance(obj, dict):
        raise ProtocolValidationError("MALFORMED_REQUEST: top-level JSON value is not an object")
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
    try:
        obj = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolValidationError(f"MALFORMED_REQUEST: not valid JSON ({exc})") from exc
    if not isinstance(obj, dict):
        raise ProtocolValidationError("MALFORMED_REQUEST: top-level JSON value is not an object")
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
