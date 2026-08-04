"""Bridge into the SAME two vendored submodules `pdh_pdl_demo` already bridges (CEO instruction,
2026-08-04: "cablarea pentru politici multiple... motorul demo_gate_engine comun, nu duplicat").

**`vendor/alpha_automation_detectors`** (already pinned, `discovery-mk-matrix-v1` @ `61cbd58`): reused
here for `institutional_levels.py` (PDH/PDL, same as CAND-0001), PLUS the two additional primitive
modules CAND-0007/CAND-0019 need that CAND-0001 never touched: `imbalance_mechanics.py` (FVG/CE-50,
CAND-0007) and `order_flow.py` (DemandZone, CAND-0019), and `interactions.py` (the generic same-bar
confluence locator both new policies use). Content-hash-verified byte-identical to what
`POLICY_LEVEL_FVG_CONFLUENCE_v2.md`/`POLICY_DZ_LEVEL_CONFLUENCE_v2.md`/`POLICY_LEVEL_BREAK_DRIVE_v3.md`
cite in their own W10 blocks (`sha256` of each file at the pinned commit matches each policy's own
cited hash exactly), even though the exact commit label those docs cite (`8edbf99...`) isn't itself
reachable from this local clone's history -- content identity is what W10 actually requires, not the
literal commit object.

**`vendor/alpha_automation_demo_gate`** (already pinned, same commit CAND-0001 uses,
`86304e7578ff461fcf23826c07f0295272b1fbc5`): the SAME frozen `demo_gate_engine/pdh_pdl_demo_engine.py`
-- `simulate_demo_trade`/`DemoSignal`/`min_executable_risk` are policy-agnostic (confirmed by reading:
`DemoSignal` takes only `entry_idx, direction, stop, target, atr, effective_spread, cost, day_end_idx`,
nothing PDH/PDL-specific), so ONE import here serves all four policies -- never duplicated, never
reimplemented, exactly the CEO's own constraint.

Never modified -- this package only reads from both submodules, same discipline as
`pdh_pdl_demo/vendor_bridge.py`."""

from __future__ import annotations

import sys
from pathlib import Path

_DETECTORS_CODE_PATH = Path(__file__).resolve().parents[2] / "vendor" / "alpha_automation_detectors" / "code"
_DEMO_GATE_PATH = Path(__file__).resolve().parents[2] / "vendor" / "alpha_automation_demo_gate" / "demo_gate_engine"

for _p in (_DETECTORS_CODE_PATH, _DEMO_GATE_PATH):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from market_structure import Block  # type: ignore[import-not-found] # noqa: E402
from market_state import ATR_WINDOW, atr14, expansion, sessions  # type: ignore[import-not-found] # noqa: E402
from institutional_levels import (  # type: ignore[import-not-found] # noqa: E402
    LevelKind,
    LevelTouch,
    ReferenceLevel,
    compute_prior_day_levels,
    detect_level_touches,
)
from imbalance_mechanics import (  # type: ignore[import-not-found] # noqa: E402
    FVGKind,
    FairValueGap,
    FvgReaction,
    detect_fvg_reactions,
    detect_fvgs,
)
from order_flow import (  # type: ignore[import-not-found] # noqa: E402
    DemandZone,
    OrderBlockKind,
    detect_demand_zones,
)
from interactions import confluence, price_in_zone, to_mask  # type: ignore[import-not-found] # noqa: E402
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
    "ATR_WINDOW",
    "atr14",
    "expansion",
    "sessions",
    "LevelKind",
    "LevelTouch",
    "ReferenceLevel",
    "compute_prior_day_levels",
    "detect_level_touches",
    "FVGKind",
    "FairValueGap",
    "FvgReaction",
    "detect_fvgs",
    "detect_fvg_reactions",
    "DemandZone",
    "OrderBlockKind",
    "detect_demand_zones",
    "confluence",
    "price_in_zone",
    "to_mask",
    "DemoSignal",
    "DemoTradeResult",
    "ExitReason",
    "min_executable_risk",
    "simulate_demo_trade",
    "simulate_demo_trades",
]
