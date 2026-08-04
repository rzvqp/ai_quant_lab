"""Bridge into TWO vendored submodules for CAND-0001 PDH-PDL v2.0 DEMO wiring (CEO instruction,
2026-08-03: "Cableaza CAND-0001 PDH-PDL v2.0 la executie DEMO").

**`vendor/alpha_automation_detectors`** (already pinned for `structural_observer`, Mandate 4 Step 3,
`discovery-mk-matrix-v1` @ `61cbd58`): reused here for `institutional_levels.py`'s ratified
`compute_prior_day_levels`/`detect_level_touches`/`LevelKind`/`ReferenceLevel`/`LevelTouch` (Part A,
grounding confirmed byte-identical to `POLICY_PDH_PDL_v2.md`'s own cited commit `8edbf99` -- `git diff`
between the two commits for this file is empty) and `market_state.atr14` (the `atr` field
`DemoSignal`/S2 need -- reused, not recalculated, per Part B's own "no new calculation invented" rule).

**`vendor/alpha_automation_demo_gate`** (`alpha-automation-v1` branch): pinned at
`06e4e00b6222904f1aca5bedb5f39142fa08dcc5` -- `demo_gate_engine/pdh_pdl_demo_engine.py`, the DEMO
gate-enforcement engine, RT-CODE-A-0005-fixed and independently re-verified by Red Team's re-attack
(RT-CODE-A-0010, `c806cbe` in THIS repo's own history -- not the submodule's -- verdict
PASS_WITH_LIMITATIONS). **Moved up from the prior pin (`86304e7`, pre-fix)** on 2026-08-04 once the CEO
confirmed the re-attack verdict; the prior pin's `DemoSignal.day_end_idx` field was renamed to
`time_stop_idx` by this fix (one meaning: last scan bar = force-close limit) -- this package's own
`orchestration.py` was updated to pass `time_stop_idx=` at the same time, still with the SAME live-valid
value (the real calendar day boundary, `PendingPdhPdlTrade.day_end_idx` -- an internal name, unrelated
to the renamed field, kept as-is). Self-contained (only `dataclasses`/`enum`/`typing`), so this pin needs
no further dependency resolution. **Never modified -- this package only reads from it.**
`simulate_demo_trade`/`simulate_demo_trades` are called ONLY post-hoc, after a position has already
closed, per the CEO's own confirmation ("Motorul se cheama o data, dupa inchidere") -- never as a live
decision input.
"""

from __future__ import annotations

import sys
from pathlib import Path

_DETECTORS_CODE_PATH = Path(__file__).resolve().parents[2] / "vendor" / "alpha_automation_detectors" / "code"
_DEMO_GATE_PATH = Path(__file__).resolve().parents[2] / "vendor" / "alpha_automation_demo_gate" / "demo_gate_engine"

for _p in (_DETECTORS_CODE_PATH, _DEMO_GATE_PATH):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from market_structure import Block  # type: ignore[import-not-found] # noqa: E402
from market_state import atr14, sessions  # type: ignore[import-not-found] # noqa: E402
from institutional_levels import (  # type: ignore[import-not-found] # noqa: E402
    LevelKind,
    LevelTouch,
    ReferenceLevel,
    compute_prior_day_levels,
    detect_level_touches,
)
from pdh_pdl_demo_engine import (  # type: ignore[import-not-found] # noqa: E402
    DemoSignal,
    DemoTradeResult,
    ExitReason,
    min_executable_risk,
    simulate_demo_trade,
    simulate_demo_trades,
)

__all__ = [
    "Block",
    "atr14",
    "sessions",
    "LevelKind",
    "LevelTouch",
    "ReferenceLevel",
    "compute_prior_day_levels",
    "detect_level_touches",
    "DemoSignal",
    "DemoTradeResult",
    "ExitReason",
    "min_executable_risk",
    "simulate_demo_trade",
    "simulate_demo_trades",
]
