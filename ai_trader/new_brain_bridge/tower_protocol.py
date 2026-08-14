"""Client-side copy of the versioned wire format spoken to the isolated `ve_tower` worker
(`tower_worker/src/ve_tower_worker/protocol.py`).

**Deliberately duplicated, not shared as a common import.** The whole point of the isolation architecture
(CEO mandate, 2026-08-14, "Forma same-process e PROHIBITA") is that the AI Trader venv and the tower venv
never share an installed package -- publishing a third `ve_tower_protocol` package installed into BOTH
venvs would quietly reintroduce a shared dependency surface between them, undermining the isolation this
whole module exists to enforce. `PROTOCOL_VERSION` is the actual safety net against the two copies
drifting: `tower_client.py` refuses (`TOWER_UNAVAILABLE`/`PROTOCOL_VERSION_MISMATCH`) the moment the
worker echoes back a different version than this file declares, rather than silently trusting a field
layout the two sides no longer agree on.

Field names, types, and framing (4-byte big-endian length prefix + `json.dumps(..., sort_keys=True)`
UTF-8 bytes, no pickle) match `ve_tower_worker.protocol` exactly -- kept in lockstep by hand, the same way
`PROTOCOL_VERSION`/`REQUEST_SCHEMA_VERSION`/`RESPONSE_SCHEMA_VERSION` are bumped in both files together
whenever the contract itself changes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

PROTOCOL_VERSION = "1.0"
REQUEST_SCHEMA_VERSION = "1.0"

MAX_PAYLOAD_BYTES = 4 * 1024 * 1024

TOWER_UNAVAILABLE = "TOWER_UNAVAILABLE"
PROTOCOL_VERSION_MISMATCH = "PROTOCOL_VERSION_MISMATCH"
MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"
RESPONSE_IDENTITY_MISMATCH = "RESPONSE_IDENTITY_MISMATCH"
STALE_RESPONSE = "STALE_RESPONSE"
CONNECTION_FAILED = "CONNECTION_FAILED"


class TowerProtocolError(Exception):
    """Fail-closed marker for anything wrong with a response's shape or content."""


@dataclass(frozen=True, slots=True)
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


def _require_str(obj: dict[str, object], key: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str):
        raise TowerProtocolError(f"MALFORMED_RESPONSE: field '{key}' missing or not a string")
    return value


def parse_response_bytes(raw: bytes) -> TowerResponse:
    try:
        obj = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TowerProtocolError(f"MALFORMED_RESPONSE: not valid JSON ({exc})") from exc
    if not isinstance(obj, dict):
        raise TowerProtocolError("MALFORMED_RESPONSE: top-level JSON value is not an object")
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
