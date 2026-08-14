from __future__ import annotations

import pytest

from ve_tower_worker.protocol import (
    MAX_PAYLOAD_BYTES,
    ProtocolValidationError,
    TowerRequest,
    TowerResponse,
    pack_frame,
    parse_request,
    parse_response,
    unpack_length_prefix,
)


def _sample_request(**overrides: object) -> TowerRequest:
    fields: dict[str, object] = {
        "protocol_version": "1.0",
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
        protocol_version="1.0", schema_version="1.0", request_id="req-1", market_event_id="evt-1",
        event_fingerprint="fp-1", tower_version="0.1.0", ok=True,
        n3_output={"market_map_available": True}, n4_output=None, reason_codes=("N3_OK",),
    )
    parsed = parse_response(response.to_json_bytes())
    assert parsed == response


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
