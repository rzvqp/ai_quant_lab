"""Client-side wire-format tests -- `tower_protocol.py`'s own serialization and validation, independent of
any real worker process (see `test_tower_client.py` for socket-level behavior and `test_tower_isolation.py`
for the real cross-process end-to-end proof)."""

from __future__ import annotations

import pytest

from ai_trader.new_brain_bridge.tower_protocol import (
    MAX_PAYLOAD_BYTES,
    TowerProtocolError,
    TowerRequest,
    TowerResponse,
    pack_frame,
    parse_response_bytes,
    unpack_length_prefix,
)


def _sample_request() -> TowerRequest:
    return TowerRequest(
        request_id="req-1", market_event_id="evt-1", event_fingerprint="fp-1", data_identity="data-1",
        node_input_fingerprint="nif-1", symbol="XAUUSD", as_of="2026-08-14T12:00:00Z",
        n1_output={"structure": "strong"}, n2_output={"atr14": 1.2},
        m15_closed_bars=({"time": 1, "close": 1.5},), m5_closed_bars=(), strategy_id="trend_pullback",
        strategy_version="1.0",
    )


def test_request_serializes_with_default_protocol_and_schema_versions() -> None:
    request = _sample_request()
    assert request.protocol_version == "1.0"
    assert request.schema_version == "1.0"
    raw = request.to_json_bytes()
    assert b'"protocol_version": "1.0"' in raw


def test_parse_response_round_trip() -> None:
    response = TowerResponse(
        protocol_version="1.0", schema_version="1.0", request_id="req-1", market_event_id="evt-1",
        event_fingerprint="fp-1", tower_version="0.1.0", ok=True, n3_output={"a": 1}, n4_output=None,
        reason_codes=("N3_OK",),
    )
    import json

    raw = json.dumps(
        {
            "protocol_version": response.protocol_version, "schema_version": response.schema_version,
            "request_id": response.request_id, "market_event_id": response.market_event_id,
            "event_fingerprint": response.event_fingerprint, "tower_version": response.tower_version,
            "ok": response.ok, "n3_output": response.n3_output, "n4_output": response.n4_output,
            "reason_codes": list(response.reason_codes),
        }
    ).encode("utf-8")
    parsed = parse_response_bytes(raw)
    assert parsed == response


def test_parse_response_rejects_missing_ok_field() -> None:
    with pytest.raises(TowerProtocolError):
        parse_response_bytes(b'{"protocol_version": "1.0"}')


def test_parse_response_rejects_non_json() -> None:
    with pytest.raises(TowerProtocolError):
        parse_response_bytes(b"not json")


def test_pack_frame_rejects_oversized_payload() -> None:
    with pytest.raises(TowerProtocolError):
        pack_frame(b"x" * (MAX_PAYLOAD_BYTES + 1))


def test_unpack_length_prefix_rejects_oversized_declared_length() -> None:
    with pytest.raises(TowerProtocolError):
        unpack_length_prefix((MAX_PAYLOAD_BYTES + 1).to_bytes(4, "big"))
