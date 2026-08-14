"""**FAKE. FOR ISOLATION-TEST USE ONLY. NEVER the default; never wired into `cli.main` or any production
launch path.** `decision.real_decision` (imported by `cli.py` by default) is the actual production
behavior -- it returns `TOWER_UNAVAILABLE` today because `ve_tower` genuinely is not installed.

This stub exists solely so `tests/test_server_roundtrip.py` can prove the IPC round-trip itself (framing,
serialization, identity echoing, protocol-version checking) works end-to-end WITHOUT depending on
`ve_tower` ever being installed. It returns a fixed, clearly-synthetic fixture -- never anything that
could be mistaken for a real market read. Injected into `server.serve` via its `decision_fn` parameter,
the same dependency-injection seam a real `ve_tower`-backed implementation will eventually use too.
"""

from __future__ import annotations

from ve_tower_worker.protocol import TowerRequest, TowerResponse

FAKE_TOWER_VERSION = "STUB-NOT-VE-TOWER-0.0.0"


def fake_decision(request: TowerRequest) -> TowerResponse:
    return TowerResponse(
        protocol_version=request.protocol_version,
        schema_version=request.schema_version,
        request_id=request.request_id,
        market_event_id=request.market_event_id,
        event_fingerprint=request.event_fingerprint,
        tower_version=FAKE_TOWER_VERSION,
        ok=True,
        n3_output={"synthetic_fixture": True, "market_map_available": False, "levels_available": False},
        n4_output={"synthetic_fixture": True, "confirmation_available": False},
        reason_codes=("STUB_FIXTURE_RESPONSE",),
    )
