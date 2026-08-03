"""Bridge into TWO vendored submodules for CAND-0001 PDH-PDL v2.0 DEMO wiring (CEO instruction,
2026-08-03: "Cableaza CAND-0001 PDH-PDL v2.0 la executie DEMO").

**`vendor/alpha_automation_detectors`** (already pinned for `structural_observer`, Mandate 4 Step 3,
`discovery-mk-matrix-v1` @ `61cbd58`): reused here for `institutional_levels.py`'s ratified
`compute_prior_day_levels`/`detect_level_touches`/`LevelKind`/`ReferenceLevel`/`LevelTouch` (Part A,
grounding confirmed byte-identical to `POLICY_PDH_PDL_v2.md`'s own cited commit `8edbf99` -- `git diff`
between the two commits for this file is empty) and `market_state.atr14` (the `atr` field
`DemoSignal`/S2 need -- reused, not recalculated, per Part B's own "no new calculation invented" rule).

**`vendor/alpha_automation_demo_gate`** (NEW submodule, this step): pins
`ai_quant_lab-alpha-automation`'s `alpha-automation-v1` branch at the EXACT commit the CEO cited,
`86304e7578ff461fcf23826c07f0295272b1fbc5` -- `demo_gate_engine/pdh_pdl_demo_engine.py`, the frozen,
CEO-authorized DEMO gate-enforcement engine (13/13 tests, mypy clean, per the CEO's own citation).
Self-contained (only `dataclasses`/`enum`/`typing` -- confirmed by reading the file before bridging),
so this pin needs no further dependency resolution. **Never modified -- this package only reads from
it.** `simulate_demo_trade`/`simulate_demo_trades` are called ONLY post-hoc, after a position has
already closed, per the CEO's own confirmation ("Motorul se cheama o data, dupa inchidere") -- never as
a live decision input.
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
