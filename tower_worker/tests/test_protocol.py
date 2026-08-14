from __future__ import annotations

import pytest

from ve_tower_worker.protocol import (
    MAX_PAYLOAD_BYTES,
    ProtocolValidationError,
    HandshakeRequest,
    HandshakeResponse,
    TowerRequest,
    TowerResponse,
    WorkerIdentity,
    pack_frame,
    parse_handshake_request,
    parse_handshake_response,
    parse_request,
    parse_response,
    peek_frame_type,
    unpack_length_prefix,
)


def _sample_request(**overrides: object) -> TowerRequest:
    fields: dict[str, object] = {
        "protocol_version": "2.0",
        "schema_version": "1.0",
        "request_id": "req-1",
        "market_event_id": "evt-1",
        "event_fingerprint": "fp-1",
        "data_identity": "data-1",
        "node_input_fingerprint": "nif-1",
        "symbol": "XAUUSD",
        "as_of": "2026-08-14T12:00:00Z",
        "n1_output": {"structure": "strong", "direction": "up"},
        "n2_output": {"atr14": 1.23},
        "m15_closed_bars": ({"time": 1, "open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5},),
        "m5_closed_bars": (),
        "strategy_id": "trend_pullback",
        "strategy_version": "1.0",
    }
    fields.update(overrides)
    return TowerRequest(**fields)  # type: ignore[arg-type]


def test_request_round_trip() -> None:
    request = _sample_request()
    parsed = parse_request(request.to_json_bytes())
    assert parsed == request


def test_response_round_trip() -> None:
    response = TowerResponse(
        protocol_version="2.0", schema_version="2.0", request_id="req-1", market_event_id="evt-1",
        event_fingerprint="fp-1", tower_version="0.1.0", ok=True,
        n3_output={"market_map_available": True}, n4_output=None,
        session_id="sess-1", worker_identity_fingerprint="fingerprint-1", reason_codes=("N3_OK",),
    )
    parsed = parse_response(response.to_json_bytes())
    assert parsed == response


def _sample_identity(**overrides: object) -> WorkerIdentity:
    fields: dict[str, object] = {
        "worker_package_version": "0.2.0", "worker_build_commit": "abc123", "protocol_version": "2.0",
        "ve_tower_package_version": "0.3.0", "package_build_commit": "6daf2aa",
        "state_delivery_commit": "0207ffa", "wheel_sha256": "deadbeef" * 8,
        "vendored_source_identity": "vendored-digest", "n3_contract_version": "1.0",
        "n4_contract_version": "1.0",
    }
    fields.update(overrides)
    return WorkerIdentity(**fields)  # type: ignore[arg-type]


def test_handshake_request_round_trip() -> None:
    request = HandshakeRequest(session_id="sess-1", challenge_hex="abcd1234")
    parsed = parse_handshake_request(request.to_json_bytes())
    assert parsed == request


def test_handshake_response_round_trip() -> None:
    response = HandshakeResponse(
        session_id="sess-1", hmac_hex="feedface", identity=_sample_identity(), pid=1234,
        process_start_identity="start-token", readiness_state="READY",
    )
    parsed = parse_handshake_response(response.to_json_bytes())
    assert parsed == response


def test_identity_with_pending_fields_round_trips_as_none() -> None:
    identity = _sample_identity(vendored_source_identity=None, n3_contract_version=None, n4_contract_version=None)
    response = HandshakeResponse(
        session_id="sess-1", hmac_hex="feedface", identity=identity, pid=1234,
        process_start_identity="start-token", readiness_state="READY",
    )
    parsed = parse_handshake_response(response.to_json_bytes())
    assert parsed.identity.vendored_source_identity is None
    assert parsed.identity.n3_contract_version is None


def test_peek_frame_type_routes_handshake_vs_n3n4_request() -> None:
    handshake = HandshakeRequest(session_id="s", challenge_hex="c")
    request = _sample_request()
    assert peek_frame_type(handshake.to_json_bytes()) == "handshake"
    assert peek_frame_type(request.to_json_bytes()) == "n3n4_request"


def test_peek_frame_type_rejects_missing_type() -> None:
    with pytest.raises(ProtocolValidationError):
        peek_frame_type(b'{"no_type_field": true}')


def test_parse_request_rejects_non_json() -> None:
    with pytest.raises(ProtocolValidationError):
        parse_request(b"not json at all")


def test_parse_request_rejects_missing_field() -> None:
    request = _sample_request()
    raw = request.to_json_bytes()
    import json

    obj = json.loads(raw)
    del obj["symbol"]
    with pytest.raises(ProtocolValidationError):
        parse_request(json.dumps(obj).encode("utf-8"))


def test_parse_request_rejects_non_object_top_level() -> None:
    with pytest.raises(ProtocolValidationError):
        parse_request(b"[1, 2, 3]")


def test_pack_frame_rejects_oversized_payload() -> None:
    with pytest.raises(ProtocolValidationError):
        pack_frame(b"x" * (MAX_PAYLOAD_BYTES + 1))


def test_unpack_length_prefix_rejects_oversized_declared_length() -> None:
    oversized_prefix = (MAX_PAYLOAD_BYTES + 1).to_bytes(4, "big")
    with pytest.raises(ProtocolValidationError):
        unpack_length_prefix(oversized_prefix)


def test_unpack_length_prefix_rejects_wrong_length() -> None:
    with pytest.raises(ProtocolValidationError):
        unpack_length_prefix(b"\x00\x00")


def test_pack_and_unpack_frame_agree_on_length() -> None:
    payload = b'{"hello": "world"}'
    framed = pack_frame(payload)
    length = unpack_length_prefix(framed[:4])
    assert length == len(payload)
    assert framed[4:] == payload
