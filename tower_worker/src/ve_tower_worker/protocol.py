"""Versioned local IPC contract between AI Trader (client) and the isolated tower worker (server).

**v3, 2026-08-17 (Red Team RT-TOWER-0008 remediation, `N2_HANDOFF_PASS`/`N2_CHAIN_BINDING_PASS`)**:
replaces the v2 `TowerRequest`/`TowerResponse` (N3/N4-only, client-supplied `n2_output`/`n1_output`,
locally-fabricated identity fields) with `TowerChainRequest`/`TowerChainResponse`. `parse_chain_request`
is the enforcement point for the CEO's own ban list ("Clientul NU poate trimite: n2_fingerprint,
bias_available, output_fingerprint N2, N2Response, N3Response, identitati intermediare sintetice") --
ANY key in the incoming JSON object that is not in `_ALLOWED_CHAIN_REQUEST_FIELDS` is rejected with
`UNKNOWN_REQUEST_FIELD` before a `TowerChainRequest` is ever constructed. This is a structural guarantee,
not a convention: even a client that WANTED to smuggle a fabricated identity field has no wire slot to put
it in that this parser will accept.

**v2, 2026-08-14 (Red Team remediation, `TOWER_HANDOFF_CONDITIONAL`)**: added the session handshake
(`HandshakeRequest`/`HandshakeResponse`/`WorkerIdentity`) and per-response session/identity binding
(`TowerChainResponse.session_id`/`worker_identity_fingerprint`). Unchanged by this v3 revision. A frame's
`type` field discriminates handshake frames from chain request/response frames on the same wire -- see
`FRAME_TYPE_*`.

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

PROTOCOL_VERSION = "3.0"
REQUEST_SCHEMA_VERSION = "1.0"
RESPONSE_SCHEMA_VERSION = "2.0"

MAX_PAYLOAD_BYTES = 4 * 1024 * 1024
"""Enforced on both the outgoing serialize (client and server refuse to send an oversized frame) and the
incoming length-prefix read (refuses to allocate a buffer for a length prefix that exceeds this, closing
the connection instead) -- the second check is the one that actually matters for safety: it bounds memory
allocation against a malformed or hostile length prefix before a single payload byte is read."""

FRAME_TYPE_HANDSHAKE = "handshake"
FRAME_TYPE_HANDSHAKE_RESPONSE = "handshake_response"
FRAME_TYPE_CHAIN_REQUEST = "chain_request"
FRAME_TYPE_CHAIN_RESPONSE = "chain_response"

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
NODE_FAILURE_DEGRADED_TO_UNAVAILABLE = "NODE_FAILURE_DEGRADED_TO_UNAVAILABLE"
UNKNOWN_REQUEST_FIELD = "UNKNOWN_REQUEST_FIELD"


class ProtocolValidationError(Exception):
    """Fail-closed: raised by `parse_*` on any missing field, wrong type, or malformed shape. Never
    partially trust a parsed payload."""


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkerIdentity:
    """Every field the CEO's own handshake spec names, with correctly SEPARATED identities (per the
    CEO's own correction: `6daf2aa` is `package_build_commit`, never a stand-in for "source identity of
    every ratified module"). Fields the worker cannot yet determine (because `ve_tower` is not installed,
    or because VE's manifest has not yet supplied a value) are `None` -- honest absence, never a
    fabricated placeholder.

    `worker_delivery_commit` is likewise `None` unless a real `worker_delivery_manifest.json` exists in
    the tower venv -- per the CEO's own second correction (2026-08-14, closing the pin): a commit cannot
    contain its own hash, so this value is NEVER a constant hardcoded into this package's own source.
    It comes from the installer, which runs AFTER a real commit already exists and can honestly record
    `git rev-parse HEAD` at that point -- the exact precedent VE already established for `ve_brain`'s own
    `artifact_manifest(delivery_commit)`."""

    worker_package_version: str
    worker_delivery_commit: str | None
    protocol_version: str
    ve_tower_package_version: str | None
    package_build_commit: str | None
    state_delivery_commit: str | None
    wheel_sha256: str | None
    vendored_source_identity: str | None
    n3_contract_version: str | None
    n4_contract_version: str | None
    n2_contract_version: str | None = None
    chain_request_contract_version: str | None = None
    chain_response_contract_version: str | None = None
    tower_chain_binding_version: str | None = None
    production_entrypoint: str | None = None
    atr_source_commit: str | None = None
    """Chain-binding fields (RT-TOWER-0008 remediation, 2026-08-17, `ve_tower` 0.5.0): `None` for a
    worker running against a pre-0.5.0 `ve_tower` -- honest absence, never backfilled.

    `atr_source_commit` (RT-TOWER-0010, 2026-08-17, `ve_tower` 0.5.2): the vendored `market_state`
    module's own source commit backing the real `atr14` now threaded into `run_n3`/`run_n4` -- `None`
    for a worker running against 0.5.0 (which hardcoded `atr=None`)."""

    def as_dict(self) -> dict[str, object]:
        return {
            "worker_package_version": self.worker_package_version,
            "worker_delivery_commit": self.worker_delivery_commit,
            "protocol_version": self.protocol_version,
            "ve_tower_package_version": self.ve_tower_package_version,
            "package_build_commit": self.package_build_commit,
            "state_delivery_commit": self.state_delivery_commit,
            "wheel_sha256": self.wheel_sha256,
            "vendored_source_identity": self.vendored_source_identity,
            "n3_contract_version": self.n3_contract_version,
            "n4_contract_version": self.n4_contract_version,
            "n2_contract_version": self.n2_contract_version,
            "chain_request_contract_version": self.chain_request_contract_version,
            "chain_response_contract_version": self.chain_response_contract_version,
            "tower_chain_binding_version": self.tower_chain_binding_version,
            "production_entrypoint": self.production_entrypoint,
            "atr_source_commit": self.atr_source_commit,
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
        worker_delivery_commit=_opt_str("worker_delivery_commit"),
        protocol_version=_require_str(obj, "protocol_version"),
        ve_tower_package_version=_opt_str("ve_tower_package_version"),
        package_build_commit=_opt_str("package_build_commit"),
        state_delivery_commit=_opt_str("state_delivery_commit"),
        wheel_sha256=_opt_str("wheel_sha256"),
        vendored_source_identity=_opt_str("vendored_source_identity"),
        n3_contract_version=_opt_str("n3_contract_version"),
        n4_contract_version=_opt_str("n4_contract_version"),
        n2_contract_version=_opt_str("n2_contract_version"),
        chain_request_contract_version=_opt_str("chain_request_contract_version"),
        chain_response_contract_version=_opt_str("chain_response_contract_version"),
        tower_chain_binding_version=_opt_str("tower_chain_binding_version"),
        production_entrypoint=_opt_str("production_entrypoint"),
        atr_source_commit=_opt_str("atr_source_commit"),
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


_ALLOWED_CHAIN_REQUEST_FIELDS = frozenset({
    "type", "protocol_version", "schema_version", "request_id",
    "market_event_id", "trace_id", "correlation_id", "symbol", "as_of", "configuration_fingerprint",
    "regime_axes_status",
    "h1_open", "h1_high", "h1_low", "h1_close", "h1_time", "h1_source_identity", "h1_max_staleness_s",
    "m15_open", "m15_high", "m15_low", "m15_close", "m15_time", "m15_source_identity", "m15_max_staleness_s",
    "m5_high", "m5_low", "m5_close", "m5_time", "m5_source_identity", "m5_max_staleness_s",
    "strategy_id", "strategy_version", "side",
    "expected_n2_contract", "expected_n3_contract", "expected_n4_contract",
})
"""The COMPLETE, EXHAUSTIVE set of fields a chain request may carry -- CEO section 4/5 (2026-08-17):
"Camp necunoscut: UNKNOWN_REQUEST_FIELD, fail-closed." AND "Clientul NU poate trimite: n2_fingerprint,
bias_available, output_fingerprint N2, N2Response, N3Response, identitati intermediare sintetice." Checked
by `parse_chain_request` BEFORE any field is read into a `TowerChainRequest` -- an extra key is rejected
outright, not silently dropped."""


@dataclass(frozen=True, slots=True, kw_only=True)
class TowerChainRequest:
    request_id: str
    market_event_id: str
    trace_id: str
    correlation_id: str
    symbol: str
    as_of: int
    configuration_fingerprint: str
    regime_axes_status: tuple[str, ...]
    h1_open: tuple[float, ...]
    h1_high: tuple[float, ...]
    h1_low: tuple[float, ...]
    h1_close: tuple[float, ...]
    h1_time: tuple[int, ...]
    h1_source_identity: str
    m15_open: tuple[float, ...]
    m15_high: tuple[float, ...]
    m15_low: tuple[float, ...]
    m15_close: tuple[float, ...]
    m15_time: tuple[int, ...]
    m15_source_identity: str
    m5_high: tuple[float, ...]
    m5_low: tuple[float, ...]
    m5_close: tuple[float, ...]
    m5_time: tuple[int, ...]
    m5_source_identity: str
    strategy_id: str
    strategy_version: str
    side: int
    expected_n2_contract: str
    expected_n3_contract: str
    expected_n4_contract: str
    h1_max_staleness_s: int | None = None
    m15_max_staleness_s: int | None = None
    m5_max_staleness_s: int | None = None
    protocol_version: str = PROTOCOL_VERSION
    schema_version: str = REQUEST_SCHEMA_VERSION
    type: str = FRAME_TYPE_CHAIN_REQUEST


@dataclass(frozen=True, slots=True, kw_only=True)
class TowerChainResponse:
    protocol_version: str
    schema_version: str
    request_id: str
    market_event_id: str
    correlation_id: str
    configuration_fingerprint: str
    tower_version: str
    chain_binding_version: str
    chain_response_contract_version: str
    chain_fingerprint: str
    chain_status: str
    terminal_reason_code: str
    ok: bool
    n2_output: dict[str, object] | None
    n3_output: dict[str, object] | None
    n4_output: dict[str, object] | None
    session_id: str
    worker_identity_fingerprint: str
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    type: str = FRAME_TYPE_CHAIN_RESPONSE

    def to_json_bytes(self) -> bytes:
        payload = {
            "type": self.type,
            "protocol_version": self.protocol_version,
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "market_event_id": self.market_event_id,
            "correlation_id": self.correlation_id,
            "configuration_fingerprint": self.configuration_fingerprint,
            "tower_version": self.tower_version,
            "chain_binding_version": self.chain_binding_version,
            "chain_response_contract_version": self.chain_response_contract_version,
            "chain_fingerprint": self.chain_fingerprint,
            "chain_status": self.chain_status,
            "terminal_reason_code": self.terminal_reason_code,
            "ok": self.ok,
            "n2_output": self.n2_output,
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


def _require_float_list(obj: dict[str, object], key: str) -> tuple[float, ...]:
    value = obj.get(key)
    if not isinstance(value, list) or not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in value):
        raise ProtocolValidationError(f"MALFORMED_REQUEST: field '{key}' missing or not a list of numbers")
    return tuple(float(x) for x in value)


def _require_int_list(obj: dict[str, object], key: str) -> tuple[int, ...]:
    value = obj.get(key)
    if not isinstance(value, list) or not all(isinstance(x, int) and not isinstance(x, bool) for x in value):
        raise ProtocolValidationError(f"MALFORMED_REQUEST: field '{key}' missing or not a list of ints")
    return tuple(value)


def _require_str_list(obj: dict[str, object], key: str) -> tuple[str, ...]:
    value = obj.get(key)
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise ProtocolValidationError(f"MALFORMED_REQUEST: field '{key}' missing or not a list of strings")
    return tuple(value)


def _opt_int(obj: dict[str, object], key: str) -> int | None:
    value = obj.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ProtocolValidationError(f"MALFORMED_REQUEST: field '{key}' must be an int or null")
    return value


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


def parse_chain_request(raw: bytes) -> TowerChainRequest:
    """Fail-closed: any missing/mistyped field, OR any field NOT in `_ALLOWED_CHAIN_REQUEST_FIELDS`,
    raises `ProtocolValidationError` before a `TowerChainRequest` is ever constructed -- the server never
    operates on a partially-trusted OR over-permissive object."""
    obj = _parse_object(raw)
    extra_fields = set(obj) - _ALLOWED_CHAIN_REQUEST_FIELDS
    if extra_fields:
        raise ProtocolValidationError(
            f"{UNKNOWN_REQUEST_FIELD}: field(s) not permitted on a chain request: {sorted(extra_fields)}"
        )
    return TowerChainRequest(
        protocol_version=_require_str(obj, "protocol_version"),
        schema_version=_require_str(obj, "schema_version"),
        request_id=_require_str(obj, "request_id"),
        market_event_id=_require_str(obj, "market_event_id"),
        trace_id=_require_str(obj, "trace_id"),
        correlation_id=_require_str(obj, "correlation_id"),
        symbol=_require_str(obj, "symbol"),
        as_of=_require_int(obj, "as_of"),
        configuration_fingerprint=_require_str(obj, "configuration_fingerprint"),
        regime_axes_status=_require_str_list(obj, "regime_axes_status"),
        h1_open=_require_float_list(obj, "h1_open"), h1_high=_require_float_list(obj, "h1_high"),
        h1_low=_require_float_list(obj, "h1_low"), h1_close=_require_float_list(obj, "h1_close"),
        h1_time=_require_int_list(obj, "h1_time"), h1_source_identity=_require_str(obj, "h1_source_identity"),
        h1_max_staleness_s=_opt_int(obj, "h1_max_staleness_s"),
        m15_open=_require_float_list(obj, "m15_open"), m15_high=_require_float_list(obj, "m15_high"),
        m15_low=_require_float_list(obj, "m15_low"), m15_close=_require_float_list(obj, "m15_close"),
        m15_time=_require_int_list(obj, "m15_time"),
        m15_source_identity=_require_str(obj, "m15_source_identity"),
        m15_max_staleness_s=_opt_int(obj, "m15_max_staleness_s"),
        m5_high=_require_float_list(obj, "m5_high"), m5_low=_require_float_list(obj, "m5_low"),
        m5_close=_require_float_list(obj, "m5_close"), m5_time=_require_int_list(obj, "m5_time"),
        m5_source_identity=_require_str(obj, "m5_source_identity"),
        m5_max_staleness_s=_opt_int(obj, "m5_max_staleness_s"),
        strategy_id=_require_str(obj, "strategy_id"), strategy_version=_require_str(obj, "strategy_version"),
        side=_require_int(obj, "side"),
        expected_n2_contract=_require_str(obj, "expected_n2_contract"),
        expected_n3_contract=_require_str(obj, "expected_n3_contract"),
        expected_n4_contract=_require_str(obj, "expected_n4_contract"),
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
