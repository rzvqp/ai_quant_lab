"""Client-side wire-format tests -- `tower_protocol.py`'s own serialization and validation, independent of
any real worker process (see `test_tower_client.py` for socket-level behavior and `test_tower_isolation.py`
for the real cross-process end-to-end proof)."""

from __future__ import annotations

import json

import pytest

from ai_trader.new_brain_bridge.tower_protocol import (
    MAX_PAYLOAD_BYTES,
    TowerChainRequest,
    TowerChainResponse,
    TowerProtocolError,
    pack_frame,
    parse_chain_response_bytes,
    unpack_length_prefix,
)


def _sample_request() -> TowerChainRequest:
    return TowerChainRequest(
        request_id="req-1", market_event_id="evt-1", trace_id="trace-1", correlation_id="corr-1",
        symbol="XAUUSD", as_of=1_700_000_000, configuration_fingerprint="cfg-1",
        regime_axes_status=("TREND_UP",),
        h1_open=(2000.0,), h1_high=(2001.0,), h1_low=(1999.0,), h1_close=(2000.5,), h1_time=(1_699_996_400,),
        h1_source_identity="tower-client:XAUUSD:H1",
        m15_open=(2000.0,), m15_high=(2001.0,), m15_low=(1999.0,), m15_close=(2000.5,), m15_time=(1_699_999_400,),
        m15_source_identity="tower-client:XAUUSD:M15",
        m5_high=(2001.0,), m5_low=(1999.0,), m5_close=(2000.5,), m5_time=(1_699_999_700,),
        m5_source_identity="tower-client:XAUUSD:M5",
        strategy_id="trend_pullback", strategy_version="1.0", side=1,
        expected_n2_contract="tower-n2-request-v1", expected_n3_contract="tower-n3-request-v2",
        expected_n4_contract="tower-n4-request-v2",
    )


def test_request_serializes_with_default_protocol_and_schema_versions() -> None:
    request = _sample_request()
    assert request.protocol_version == "3.0"
    assert request.schema_version == "1.0"
    raw = request.to_json_bytes()
    assert b'"protocol_version": "3.0"' in raw
    assert b'"type": "chain_request"' in raw


def test_request_never_emits_a_field_outside_the_allowlist() -> None:
    """Belt-and-braces: `to_json_bytes` itself asserts every emitted key is in
    `_ALLOWED_CHAIN_REQUEST_FIELDS` -- this test just proves that assertion doesn't silently pass by
    checking the actual emitted keys against the same set the worker enforces on parse."""
    from ai_trader.new_brain_bridge.tower_protocol import _ALLOWED_CHAIN_REQUEST_FIELDS  # noqa: SLF001

    raw = _sample_request().to_json_bytes()
    obj = json.loads(raw)
    assert set(obj) <= _ALLOWED_CHAIN_REQUEST_FIELDS
    assert "bias_direction" not in obj
    assert "n2_fingerprint" not in obj
    assert "bias_available" not in obj


def test_parse_chain_response_round_trip() -> None:
    response = TowerChainResponse(
        protocol_version="3.0", schema_version="2.0", request_id="req-1", market_event_id="evt-1",
        correlation_id="corr-1", configuration_fingerprint="cfg-1", tower_version="0.5.0",
        chain_binding_version="tower-chain-binding-v1", chain_response_contract_version="tower-chain-response-v1",
        chain_fingerprint="chain-fp-1", chain_status="n2_n3_n4_ok", terminal_reason_code="ok",
        ok=True, n2_output={"bias_available": True}, n3_output={"a": 1}, n4_output=None,
        session_id="sess-1", worker_identity_fingerprint="fingerprint-1", reason_codes=("N2_N3_OK",),
    )
    raw = json.dumps({
        "protocol_version": response.protocol_version, "schema_version": response.schema_version,
        "request_id": response.request_id, "market_event_id": response.market_event_id,
        "correlation_id": response.correlation_id, "configuration_fingerprint": response.configuration_fingerprint,
        "tower_version": response.tower_version, "chain_binding_version": response.chain_binding_version,
        "chain_response_contract_version": response.chain_response_contract_version,
        "chain_fingerprint": response.chain_fingerprint, "chain_status": response.chain_status,
        "terminal_reason_code": response.terminal_reason_code,
        "ok": response.ok, "n2_output": response.n2_output, "n3_output": response.n3_output,
        "n4_output": response.n4_output, "session_id": response.session_id,
        "worker_identity_fingerprint": response.worker_identity_fingerprint,
        "reason_codes": list(response.reason_codes),
    }).encode("utf-8")
    parsed = parse_chain_response_bytes(raw)
    assert parsed == response


def test_parse_chain_response_rejects_missing_ok_field() -> None:
    with pytest.raises(TowerProtocolError):
        parse_chain_response_bytes(b'{"protocol_version": "3.0"}')


def test_parse_chain_response_rejects_non_json() -> None:
    with pytest.raises(TowerProtocolError):
        parse_chain_response_bytes(b"not json")


def test_pack_frame_rejects_oversized_payload() -> None:
    with pytest.raises(TowerProtocolError):
        pack_frame(b"x" * (MAX_PAYLOAD_BYTES + 1))


def test_unpack_length_prefix_rejects_oversized_declared_length() -> None:
    with pytest.raises(TowerProtocolError):
        unpack_length_prefix((MAX_PAYLOAD_BYTES + 1).to_bytes(4, "big"))
