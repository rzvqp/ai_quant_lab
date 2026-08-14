"""The one seam between the IPC boundary (`server.py`) and `ve_tower` itself.

**Today, `ve_tower` is not installed anywhere** -- 0.1.0 was rejected (`TOWER_HANDOFF_FAIL`); no repaired
version exists yet; CEO instruction is explicit: "NU instala versiunea respinsa in runtime." `real_decision`
below reflects that honestly: it tries the import, and if `ve_tower` isn't there, returns a well-formed
`TOWER_UNAVAILABLE` response rather than raising -- this IS the production behavior today, not a stand-in
for it. Once VE delivers a verified, SHA-256-checked wheel installed into THIS venv (never the AI Trader
venv -- see `env/README.md`), this function starts resolving requests for real, with no other code in this
package needing to change.
"""

from __future__ import annotations

import importlib

from ve_tower_worker.protocol import TOWER_UNAVAILABLE, TowerRequest, TowerResponse


def real_decision(request: TowerRequest) -> TowerResponse:
    """Fail-closed on `ve_tower` absence. Never invents N3/N4 output."""
    try:
        ve_tower = importlib.import_module("ve_tower")
    except ImportError:
        return TowerResponse(
            protocol_version=request.protocol_version,
            schema_version=request.schema_version,
            request_id=request.request_id,
            market_event_id=request.market_event_id,
            event_fingerprint=request.event_fingerprint,
            tower_version="UNAVAILABLE",
            ok=False,
            n3_output=None,
            n4_output=None,
            session_id="",  # overwritten unconditionally by server.py's own _stamp_session
            worker_identity_fingerprint="",
            reason_codes=(TOWER_UNAVAILABLE,),
        )
    # Deliberately unreachable until ve_tower is actually installed in this venv. What goes here is
    # dictated entirely by ve_tower's own real, ratified API -- not written speculatively today.
    raise NotImplementedError(
        "ve_tower is importable but real_decision has no wiring yet -- "
        "this is expected until TOWER_HANDOFF_PASS defines the real call shape. "
        f"ve_tower module found: {ve_tower!r}"
    )
