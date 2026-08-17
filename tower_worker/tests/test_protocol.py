from __future__ import annotations

import json

import pytest

from ve_tower_worker.protocol import (
    MAX_PAYLOAD_BYTES,
    UNKNOWN_REQUEST_FIELD,
    ProtocolValidationError,
    HandshakeRequest,
    HandshakeResponse,
    TowerChainResponse,
    WorkerIdentity,
    pack_frame,
    parse_chain_request,
    parse_handshake_request,
    parse_handshake_response,
    peek_frame_type,
    unpack_length_prefix,
)

_SAMPLE_SERIES_FIELDS = ("open", "high", "low", "close")


def _sample_request_dict(**overrides: object) -> dict[str, object]:
    fields: dict[str, object] = {
        "type": "chain_request", "protocol_version": "3.0", "schema_version": "1.0",
        "request_id": "req-1", "market_event_id": "evt-1", "trace_id": "trace-1",
        "correlation_id": "corr-1", "symbol": "XAUUSD", "as_of": 1_700_000_000,
        "configuration_fingerprint": "cfg-1", "regime_axes_status": ["TREND_UP"],
        "h1_open": [2000.0], "h1_high": [2001.0], "h1_low": [1999.0], "h1_close": [2000.5],
        "h1_time": [1_699_996_400], "h1_source_identity": "tower-client:XAUUSD:H1", "h1_max_staleness_s": None,
        "m15_open": [2000.0], "m15_high": [2001.0], "m15_low": [1999.0], "m15_close": [2000.5],
        "m15_time": [1_699_999_400], "m15_source_identity": "tower-client:XAUUSD:M15", "m15_max_staleness_s": None,
        "m5_high": [2001.0], "m5_low": [1999.0], "m5_close": [2000.5],
        "m5_time": [1_699_999_700], "m5_source_identity": "tower-client:XAUUSD:M5", "m5_max_staleness_s": None,
        "strategy_id": "trend_pullback", "strategy_version": "1.0", "side": 1,
        "expected_n2_contract": "tower-n2-request-v1", "expected_n3_contract": "tower-n3-request-v2",
        "expected_n4_contract": "tower-n4-request-v2",
    }
    fields.update(overrides)
    return fields


def test_chain_request_round_trip() -> None:
    raw = json.dumps(_sample_request_dict(), sort_keys=True).encode("utf-8")
    parsed = parse_chain_request(raw)
    assert parsed.request_id == "req-1"
    assert parsed.symbol == "XAUUSD"
    assert parsed.side == 1
    assert parsed.h1_open == (2000.0,)
    assert parsed.regime_axes_status == ("TREND_UP",)
    assert parsed.expected_n2_contract == "tower-n2-request-v1"


def test_chain_request_rejects_unknown_field() -> None:
    raw = json.dumps(_sample_request_dict(n2_fingerprint="sneaky"), sort_keys=True).encode("utf-8")
    with pytest.raises(ProtocolValidationError, match=UNKNOWN_REQUEST_FIELD):
        parse_chain_request(raw)


def test_chain_request_rejects_bias_available_field() -> None:
    """The exact CEO-named forbidden field (section 5): `bias_available` is no longer a legal wire field
    at all -- N2 is computed entirely inside the chain, never asserted by the client."""
    raw = json.dumps(_sample_request_dict(bias_available=True), sort_keys=True).encode("utf-8")
    with pytest.raises(ProtocolValidationError, match=UNKNOWN_REQUEST_FIELD):
        parse_chain_request(raw)


def test_chain_response_round_trip() -> None:
    response = TowerChainResponse(
        protocol_version="3.0", schema_version="2.0", request_id="req-1", market_event_id="evt-1",
        correlation_id="corr-1", configuration_fingerprint="cfg-1", tower_version="0.5.0",
        chain_binding_version="tower-chain-binding-v1", chain_response_contract_version="tower-chain-response-v1",
        chain_fingerprint="fp-1", chain_status="n2_n3_n4_ok", terminal_reason_code="ok",
        ok=True, n2_output={"bias_available": True}, n3_output={"market_map_available": True}, n4_output=None,
        session_id="sess-1", worker_identity_fingerprint="fingerprint-1", reason_codes=("N2_OK",),
    )
    obj = json.loads(response.to_json_bytes())
    assert obj["ok"] is True
    assert obj["chain_fingerprint"] == "fp-1"
    assert obj["n2_output"] == {"bias_available": True}


def _sample_identity(**overrides: object) -> WorkerIdentity:
    fields: dict[str, object] = {
        "worker_package_version": "0.3.0", "worker_delivery_commit": "abc123", "protocol_version": "3.0",
        "ve_tower_package_version": "0.5.0", "package_build_commit": "b128d8b",
        "state_delivery_commit": "26470f5", "wheel_sha256": "deadbeef" * 8,
        "vendored_source_identity": "vendored-digest", "n3_contract_version": "tower-n3-request-v2",
        "n4_contract_version": "tower-n4-request-v2", "n2_contract_version": "tower-n2-request-v1",
        "chain_request_contract_version": "tower-chain-request-v1",
        "chain_response_contract_version": "tower-chain-response-v1",
        "tower_chain_binding_version": "tower-chain-binding-v1", "production_entrypoint": "run_tower_chain",
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


def test_identity_with_pending_chain_fields_round_trips_as_none() -> None:
    """A pre-0.5.0 worker (or a manifest that failed to write the new fields) round-trips these as `None`
    -- honest absence, never backfilled."""
    identity = _sample_identity(
        n2_contract_version=None, chain_request_contract_version=None,
        chain_response_contract_version=None, tower_chain_binding_version=None, production_entrypoint=None,
    )
    response = HandshakeResponse(
        session_id="sess-1", hmac_hex="feedface", identity=identity, pid=1234,
        process_start_identity="start-token", readiness_state="READY",
    )
    parsed = parse_handshake_response(response.to_json_bytes())
    assert parsed.identity.n2_contract_version is None
    assert parsed.identity.production_entrypoint is None


def test_identity_with_no_worker_delivery_manifest_round_trips_worker_delivery_commit_as_none() -> None:
    """worker_delivery_commit is optional -- honestly `None` before any install-time manifest exists,
    never a hardcoded self-referential constant (CEO correction, 2026-08-14)."""
    identity = _sample_identity(worker_delivery_commit=None)
    response = HandshakeResponse(
        session_id="sess-1", hmac_hex="feedface", identity=identity, pid=1234,
        process_start_identity="start-token", readiness_state="READY",
    )
    parsed = parse_handshake_response(response.to_json_bytes())
    assert parsed.identity.worker_delivery_commit is None


def test_peek_frame_type_routes_handshake_vs_chain_request() -> None:
    handshake = HandshakeRequest(session_id="s", challenge_hex="c")
    raw = json.dumps(_sample_request_dict(), sort_keys=True).encode("utf-8")
    assert peek_frame_type(handshake.to_json_bytes()) == "handshake"
    assert peek_frame_type(raw) == "chain_request"


def test_peek_frame_type_rejects_missing_type() -> None:
    with pytest.raises(ProtocolValidationError):
        peek_frame_type(b'{"no_type_field": true}')


def test_parse_chain_request_rejects_non_json() -> None:
    with pytest.raises(ProtocolValidationError):
        parse_chain_request(b"not json at all")


def test_parse_chain_request_rejects_missing_field() -> None:
    obj = _sample_request_dict()
    del obj["symbol"]
    with pytest.raises(ProtocolValidationError):
        parse_chain_request(json.dumps(obj).encode("utf-8"))


def test_parse_chain_request_rejects_non_object_top_level() -> None:
    with pytest.raises(ProtocolValidationError):
        parse_chain_request(b"[1, 2, 3]")


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
