"""Client-side copy of the versioned wire format spoken to the isolated `ve_tower` worker
(`tower_worker/src/ve_tower_worker/protocol.py`).

**v3, 2026-08-17 (Red Team RT-TOWER-0008 remediation, `N2_HANDOFF_PASS`/`N2_CHAIN_BINDING_PASS`)**:
replaces the v2 `TowerRequest`/`TowerResponse` (N3/N4-only, client-supplied `n2_output`/`n1_output`/
locally-fabricated `event_fingerprint`/`data_identity`/`node_input_fingerprint`) with `TowerChainRequest`/
`TowerChainResponse` -- the client sends ONLY the raw inputs a real chain call needs (bars, symbol, as_of,
strategy identity, the STRATEGY's own contracted side, expected contract versions); N2/N3/N4 identity is
computed EXCLUSIVELY inside the worker's `ve_tower.run_tower_chain` and returned, never asserted by the
client. `parse_chain_request` (worker-side mirror) rejects ANY field not in `_ALLOWED_CHAIN_REQUEST_FIELDS`
with `UNKNOWN_REQUEST_FIELD` -- this is the structural enforcement that a client literally cannot smuggle
`n2_fingerprint`/`bias_available`/a fabricated `N2Response`/`N3Response` onto the wire, not just a
convention nobody violates.

**v2, 2026-08-14 (Red Team remediation, `TOWER_HANDOFF_CONDITIONAL`)**: added the session handshake
(`HandshakeRequest`/`HandshakeResponse`/`WorkerIdentity`) and per-response session/identity binding.
Unchanged by this v3 revision.

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

PROTOCOL_VERSION = "3.0"
REQUEST_SCHEMA_VERSION = "1.0"

MAX_PAYLOAD_BYTES = 4 * 1024 * 1024

FRAME_TYPE_HANDSHAKE = "handshake"
FRAME_TYPE_HANDSHAKE_RESPONSE = "handshake_response"
FRAME_TYPE_CHAIN_REQUEST = "chain_request"
FRAME_TYPE_CHAIN_RESPONSE = "chain_response"

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
UNKNOWN_REQUEST_FIELD = "UNKNOWN_REQUEST_FIELD"


class TowerProtocolError(Exception):
    """Fail-closed marker for anything wrong with a response's shape or content."""


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkerIdentity:
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
    worker running against a pre-0.5.0 `ve_tower` (0.3.0/0.4.0 have no `run_tower_chain`/N2 at all) --
    honest absence, never backfilled. `tower_identity_pin.py`'s own `verify_pin` treats these as required
    exact-match fields once the pin itself is bumped to a 0.5.0+ expectation.

    `atr_source_commit` (RT-TOWER-0010, 2026-08-17, `ve_tower` 0.5.2): the vendored `market_state` module's
    own source commit that `run_tower_chain` now threads a genuine `atr14` value from into `run_n3`/
    `run_n4` -- `None` for a worker running against 0.5.0 (which hardcoded `atr=None`, see
    `INTEGRATION_BLOCKED_TOWER_CHAIN_ATR_UNAVAILABLE.md`)."""

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
        worker_delivery_commit=_opt_str(obj, "worker_delivery_commit"),
        protocol_version=_require_str(obj, "protocol_version"),
        ve_tower_package_version=_opt_str(obj, "ve_tower_package_version"),
        package_build_commit=_opt_str(obj, "package_build_commit"),
        state_delivery_commit=_opt_str(obj, "state_delivery_commit"),
        wheel_sha256=_opt_str(obj, "wheel_sha256"),
        vendored_source_identity=_opt_str(obj, "vendored_source_identity"),
        n3_contract_version=_opt_str(obj, "n3_contract_version"),
        n4_contract_version=_opt_str(obj, "n4_contract_version"),
        n2_contract_version=_opt_str(obj, "n2_contract_version"),
        chain_request_contract_version=_opt_str(obj, "chain_request_contract_version"),
        chain_response_contract_version=_opt_str(obj, "chain_response_contract_version"),
        tower_chain_binding_version=_opt_str(obj, "tower_chain_binding_version"),
        production_entrypoint=_opt_str(obj, "production_entrypoint"),
        atr_source_commit=_opt_str(obj, "atr_source_commit"),
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
"""The COMPLETE, EXHAUSTIVE set of fields a chain request may carry -- CEO section 4 (2026-08-17):
"Clientul NU poate trimite: n2_fingerprint, bias_available, output_fingerprint N2, N2Response, N3Response,
identitati intermediare sintetice." Nothing outside this set is a legal request field; `parse_chain_request`
(worker-side) rejects any extra key with `UNKNOWN_REQUEST_FIELD` rather than silently ignoring it -- this
is what makes the ban structural rather than a convention nobody happens to violate."""


@dataclass(frozen=True, slots=True, kw_only=True)
class TowerChainRequest:
    """Mirrors `ve_tower.ChainRequest`'s own real, empirically-introspected field set almost 1:1 (RT-
    TOWER-0008, 2026-08-17) -- the worker's `decision.py` constructs a `ve_tower.ChainRequest` directly
    from this, field-for-field, with zero client-asserted N2/N3/N4 identity anywhere. `side` is an int
    (1=LONG, -1=SHORT) sourced by the CALLER from the selected strategy's own OFFICIAL, ROUTER-ELIGIBLE
    `allowed_directions` -- `bridge.py` never defaults it, never lets an operator set it, never copies it
    from N2's own output (see `bridge.py`'s own docstring for the exact provenance chain)."""

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

    def to_json_bytes(self) -> bytes:
        payload: dict[str, object] = {
            "type": self.type,
            "protocol_version": self.protocol_version,
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "market_event_id": self.market_event_id,
            "trace_id": self.trace_id,
            "correlation_id": self.correlation_id,
            "symbol": self.symbol,
            "as_of": self.as_of,
            "configuration_fingerprint": self.configuration_fingerprint,
            "regime_axes_status": list(self.regime_axes_status),
            "h1_open": list(self.h1_open), "h1_high": list(self.h1_high), "h1_low": list(self.h1_low),
            "h1_close": list(self.h1_close), "h1_time": list(self.h1_time),
            "h1_source_identity": self.h1_source_identity, "h1_max_staleness_s": self.h1_max_staleness_s,
            "m15_open": list(self.m15_open), "m15_high": list(self.m15_high), "m15_low": list(self.m15_low),
            "m15_close": list(self.m15_close), "m15_time": list(self.m15_time),
            "m15_source_identity": self.m15_source_identity, "m15_max_staleness_s": self.m15_max_staleness_s,
            "m5_high": list(self.m5_high), "m5_low": list(self.m5_low), "m5_close": list(self.m5_close),
            "m5_time": list(self.m5_time), "m5_source_identity": self.m5_source_identity,
            "m5_max_staleness_s": self.m5_max_staleness_s,
            "strategy_id": self.strategy_id, "strategy_version": self.strategy_version, "side": self.side,
            "expected_n2_contract": self.expected_n2_contract,
            "expected_n3_contract": self.expected_n3_contract,
            "expected_n4_contract": self.expected_n4_contract,
        }
        assert set(payload) <= _ALLOWED_CHAIN_REQUEST_FIELDS, "internal: emitted a field outside the allowlist"
        return json.dumps(payload, sort_keys=True).encode("utf-8")


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


def _parse_object(raw: bytes) -> dict[str, object]:
    try:
        obj = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TowerProtocolError(f"MALFORMED_RESPONSE: not valid JSON ({exc})") from exc
    if not isinstance(obj, dict):
        raise TowerProtocolError("MALFORMED_RESPONSE: top-level JSON value is not an object")
    return obj


def parse_chain_response_bytes(raw: bytes) -> TowerChainResponse:
    obj = _parse_object(raw)
    ok = obj.get("ok")
    if not isinstance(ok, bool):
        raise TowerProtocolError("MALFORMED_RESPONSE: field 'ok' missing or not a bool")
    n2_output = obj.get("n2_output")
    if n2_output is not None and not isinstance(n2_output, dict):
        raise TowerProtocolError("MALFORMED_RESPONSE: field 'n2_output' not an object or null")
    n3_output = obj.get("n3_output")
    if n3_output is not None and not isinstance(n3_output, dict):
        raise TowerProtocolError("MALFORMED_RESPONSE: field 'n3_output' not an object or null")
    n4_output = obj.get("n4_output")
    if n4_output is not None and not isinstance(n4_output, dict):
        raise TowerProtocolError("MALFORMED_RESPONSE: field 'n4_output' not an object or null")
    reason_codes_raw = obj.get("reason_codes")
    if not isinstance(reason_codes_raw, list) or not all(isinstance(r, str) for r in reason_codes_raw):
        raise TowerProtocolError("MALFORMED_RESPONSE: field 'reason_codes' missing or not a list of strings")
    return TowerChainResponse(
        protocol_version=_require_str(obj, "protocol_version"),
        schema_version=_require_str(obj, "schema_version"),
        request_id=_require_str(obj, "request_id"),
        market_event_id=_require_str(obj, "market_event_id"),
        correlation_id=_require_str(obj, "correlation_id"),
        configuration_fingerprint=_require_str(obj, "configuration_fingerprint"),
        tower_version=_require_str(obj, "tower_version"),
        chain_binding_version=_require_str(obj, "chain_binding_version"),
        chain_response_contract_version=_require_str(obj, "chain_response_contract_version"),
        chain_fingerprint=_require_str(obj, "chain_fingerprint"),
        chain_status=_require_str(obj, "chain_status"),
        terminal_reason_code=_require_str(obj, "terminal_reason_code"),
        ok=ok,
        n2_output=n2_output,
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
