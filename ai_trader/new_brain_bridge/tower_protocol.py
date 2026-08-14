"""Client-side copy of the versioned wire format spoken to the isolated `ve_tower` worker
(`tower_worker/src/ve_tower_worker/protocol.py`).

**v2, 2026-08-14 (Red Team remediation, `TOWER_HANDOFF_CONDITIONAL`)**: adds the session handshake
(`HandshakeRequest`/`HandshakeResponse`/`WorkerIdentity`) and per-response session/identity binding
(`TowerResponse.session_id`/`worker_identity_fingerprint`).

**Deliberately duplicated, not shared as a common import.** The whole point of the isolation architecture
(CEO mandate, 2026-08-14, "Forma same-process e PROHIBITA") is that the AI Trader venv and the tower venv
never share an installed package -- publishing a third `ve_tower_protocol` package installed into BOTH
venvs would quietly reintroduce a shared dependency surface between them, undermining the isolation this
whole module exists to enforce. `PROTOCOL_VERSION` is the actual safety net against the two copies
drifting: `tower_client.py`/`tower_launcher.py` refuse the moment the worker echoes back a different
version than this file declares, rather than silently trusting a field layout the two sides no longer
agree on.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

PROTOCOL_VERSION = "2.0"
REQUEST_SCHEMA_VERSION = "1.0"

MAX_PAYLOAD_BYTES = 4 * 1024 * 1024

FRAME_TYPE_HANDSHAKE = "handshake"
FRAME_TYPE_HANDSHAKE_RESPONSE = "handshake_response"
FRAME_TYPE_N3N4_REQUEST = "n3n4_request"
FRAME_TYPE_N3N4_RESPONSE = "n3n4_response"

TOWER_UNAVAILABLE = "TOWER_UNAVAILABLE"
PROTOCOL_VERSION_MISMATCH = "PROTOCOL_VERSION_MISMATCH"
MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"
RESPONSE_IDENTITY_MISMATCH = "RESPONSE_IDENTITY_MISMATCH"
STALE_RESPONSE = "STALE_RESPONSE"
STALE_SESSION = "STALE_SESSION"
CONNECTION_FAILED = "CONNECTION_FAILED"
REQUEST_ID_REUSE_MISMATCH = "REQUEST_ID_REUSE_MISMATCH"
NON_LOOPBACK_BIND_FORBIDDEN = "NON_LOOPBACK_BIND_FORBIDDEN"
HANDSHAKE_HMAC_MISMATCH = "HANDSHAKE_HMAC_MISMATCH"
HANDSHAKE_IDENTITY_MISMATCH = "HANDSHAKE_IDENTITY_MISMATCH"
HANDSHAKE_SESSION_ID_MISMATCH = "HANDSHAKE_SESSION_ID_MISMATCH"
HANDSHAKE_NOT_ESTABLISHED = "HANDSHAKE_NOT_ESTABLISHED"


class TowerProtocolError(Exception):
    """Fail-closed marker for anything wrong with a response's shape or content."""


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkerIdentity:
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
        return json.dumps(self.as_dict(), sort_keys=True)

    def fingerprint(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def _opt_str(obj: dict[str, object], key: str) -> str | None:
    value = obj.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise TowerProtocolError(f"MALFORMED_RESPONSE: field '{key}' must be a string or null")
    return value


def _require_str(obj: dict[str, object], key: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str):
        raise TowerProtocolError(f"MALFORMED_RESPONSE: field '{key}' missing or not a string")
    return value


def _require_int(obj: dict[str, object], key: str) -> int:
    value = obj.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise TowerProtocolError(f"MALFORMED_RESPONSE: field '{key}' missing or not an int")
    return value


def _require_dict(obj: dict[str, object], key: str) -> dict[str, object]:
    value = obj.get(key)
    if not isinstance(value, dict):
        raise TowerProtocolError(f"MALFORMED_RESPONSE: field '{key}' missing or not an object")
    return value


def worker_identity_from_dict(obj: dict[str, object]) -> WorkerIdentity:
    return WorkerIdentity(
        worker_package_version=_require_str(obj, "worker_package_version"),
        worker_build_commit=_require_str(obj, "worker_build_commit"),
        protocol_version=_require_str(obj, "protocol_version"),
        ve_tower_package_version=_opt_str(obj, "ve_tower_package_version"),
        package_build_commit=_opt_str(obj, "package_build_commit"),
        state_delivery_commit=_opt_str(obj, "state_delivery_commit"),
        wheel_sha256=_opt_str(obj, "wheel_sha256"),
        vendored_source_identity=_opt_str(obj, "vendored_source_identity"),
        n3_contract_version=_opt_str(obj, "n3_contract_version"),
        n4_contract_version=_opt_str(obj, "n4_contract_version"),
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


def parse_handshake_response_bytes(raw: bytes) -> HandshakeResponse:
    obj = _parse_object(raw)
    identity_obj = _require_dict(obj, "identity")
    return HandshakeResponse(
        session_id=_require_str(obj, "session_id"), hmac_hex=_require_str(obj, "hmac_hex"),
        identity=worker_identity_from_dict(identity_obj), pid=_require_int(obj, "pid"),
        process_start_identity=_require_str(obj, "process_start_identity"),
        readiness_state=_require_str(obj, "readiness_state"),
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class TowerRequest:
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
    protocol_version: str = PROTOCOL_VERSION
    schema_version: str = REQUEST_SCHEMA_VERSION
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


def _parse_object(raw: bytes) -> dict[str, object]:
    try:
        obj = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TowerProtocolError(f"MALFORMED_RESPONSE: not valid JSON ({exc})") from exc
    if not isinstance(obj, dict):
        raise TowerProtocolError("MALFORMED_RESPONSE: top-level JSON value is not an object")
    return obj


def parse_response_bytes(raw: bytes) -> TowerResponse:
    obj = _parse_object(raw)
    ok = obj.get("ok")
    if not isinstance(ok, bool):
        raise TowerProtocolError("MALFORMED_RESPONSE: field 'ok' missing or not a bool")
    n3_output = obj.get("n3_output")
    if n3_output is not None and not isinstance(n3_output, dict):
        raise TowerProtocolError("MALFORMED_RESPONSE: field 'n3_output' not an object or null")
    n4_output = obj.get("n4_output")
    if n4_output is not None and not isinstance(n4_output, dict):
        raise TowerProtocolError("MALFORMED_RESPONSE: field 'n4_output' not an object or null")
    reason_codes_raw = obj.get("reason_codes")
    if not isinstance(reason_codes_raw, list) or not all(isinstance(r, str) for r in reason_codes_raw):
        raise TowerProtocolError("MALFORMED_RESPONSE: field 'reason_codes' missing or not a list of strings")
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
    if len(payload) > MAX_PAYLOAD_BYTES:
        raise TowerProtocolError(f"PAYLOAD_TOO_LARGE: {len(payload)} bytes > {MAX_PAYLOAD_BYTES}")
    return len(payload).to_bytes(4, "big") + payload


def unpack_length_prefix(prefix: bytes) -> int:
    if len(prefix) != 4:
        raise TowerProtocolError("MALFORMED_RESPONSE: length prefix must be exactly 4 bytes")
    length = int.from_bytes(prefix, "big")
    if length > MAX_PAYLOAD_BYTES:
        raise TowerProtocolError(f"PAYLOAD_TOO_LARGE: declared length {length} > {MAX_PAYLOAD_BYTES}")
    return length
