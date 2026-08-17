"""**FAKE. FOR ISOLATION-TEST USE ONLY. NEVER the default; never wired into `cli.main` or any production
launch path.** `decision.real_decision` (imported by `cli.py` by default) is the actual production
behavior -- it calls the real, installed `ve_tower.run_tower_chain`.

This stub exists solely so `tests/test_server_roundtrip.py` can prove the IPC round-trip itself (framing,
serialization, identity echoing, protocol-version checking) works end-to-end WITHOUT depending on
`ve_tower` ever being installed. It returns a fixed, clearly-synthetic fixture -- never anything that
could be mistaken for a real market read. Injected into `server.serve` via its `decision_fn` parameter,
the same dependency-injection seam the real `ve_tower`-backed implementation uses too."""

from __future__ import annotations

from ve_tower_worker.protocol import TowerChainRequest, TowerChainResponse

FAKE_TOWER_VERSION = "STUB-NOT-VE-TOWER-0.0.0"


def fake_decision(request: TowerChainRequest) -> TowerChainResponse:
    return TowerChainResponse(
        protocol_version=request.protocol_version,
        schema_version=request.schema_version,
        request_id=request.request_id,
        market_event_id=request.market_event_id,
        correlation_id=request.correlation_id,
        configuration_fingerprint=request.configuration_fingerprint,
        tower_version=FAKE_TOWER_VERSION,
        chain_binding_version="STUB-CHAIN-BINDING-0.0.0",
        chain_response_contract_version="STUB-CHAIN-RESPONSE-0.0.0",
        chain_fingerprint="STUB-CHAIN-FINGERPRINT",
        chain_status="STUB_FIXTURE",
        terminal_reason_code="STUB_FIXTURE_RESPONSE",
        ok=True,
        n2_output={"synthetic_fixture": True, "bias_available": False},
        n3_output={"synthetic_fixture": True, "market_map_available": False, "levels_available": False},
        n4_output={"synthetic_fixture": True, "confirmation_available": False},
        session_id="",  # overwritten unconditionally by server.py's own _stamp_session
        worker_identity_fingerprint="",
        reason_codes=("STUB_FIXTURE_RESPONSE",),
    )
