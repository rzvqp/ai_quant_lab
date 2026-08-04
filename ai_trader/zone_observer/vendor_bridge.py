"""Bridge into vendored zone/level detectors -- pure observation, feeds the Level-3 confluence map
(CEO instruction, 2026-08-04). Wires FIVE things, deliberately NOT six:

1. `session_levels.py` PRIMITIVE A ONLY (`compute_prior_session_levels`,
   `detect_session_level_touches`, `detect_session_mid_touches`, `derive_session_index`).
   Primitive B (`compute_persistent_session_levels`) is explicitly forbidden without the k=1.0xATR
   filter (produces 89-188 active levels unfiltered) -- not imported here at all.
2. `order_flow.detect_demand_zones` -- the ONE order_flow.py function `structural_observer` does
   NOT already record (it already tracks `detect_order_blocks`/`track_breaker`/
   `detect_mitigations`/`detect_rejections` live, verified byte-identical to this same commit --
   see `ZONE_OBSERVER_ACTIVATION_REPORT.md`). Not re-importing the other four: that would duplicate
   an already-running, unchanged observation, not add one.
3. `imbalance_mechanics.detect_inverse_fvgs` + `count_bpr` -- `detect_fvgs` itself is ALSO imported,
   but ONLY as the required input to these two (never re-recorded as its own event --
   `structural_observer` already records FVG_FORMED/FVG_REACTION from the identical function).
4. `institutional_levels.compute_prior_week_levels` (+ `derive_week_index`) -- PWH/PWL formation
   only. `detect_level_touches` in this same module explicitly excludes WEEKLY_HIGH/WEEKLY_LOW
   ("doar fereastra zilnica") -- no ratified weekly-touch detector exists, so none is invented here;
   `observer.py` records formation only and says so.
5. `order_block_void.detect_liquidity_voids` (+ `VoidKind`) -- NOT the `OrderBlock`/
   `resolve_validity_and_measurement` half of that same file, which raises `NotImplementedError` by
   its own design (OB formation criterion is an open question, explicitly unblocked only for
   `zone_lower`/`zone_upper`, not autonomous detection).

**Two vendor sources, two sys.path entries, deliberately NOT one submodule pin move.** `market_structure.py`
and `liquidity_mechanics.py` have a REAL functional diff between the currently-pinned submodule commit
(`61cbd58c3d5da19001b125b65d669ddad54a14c4`) and the CEO-cited `bf02dd2` (a cascade-semantics fix to
`detect_breaks`/`label_structure`, v2.7.38) -- `structural_observer` already imports `detect_breaks` from
the CURRENTLY PINNED commit, live, right now. Moving the shared submodule pin to `bf02dd2` would silently
change `structural_observer`'s already-running STRUCTURE_BREAK output -- exactly the kind of engine-adjacent
change forbidden this session ("Nu opri procesele existente", VE/Red Team's own current attack on the
execution engine). Verified byte-for-byte (`git rev-parse <commit>:<path>`, not just `git diff --stat`
silence) that `order_flow.py`, `imbalance_mechanics.py`, `order_block_void.py`, and `institutional_levels.py`
are IDENTICAL blobs between the two commits -- so those four import from the EXISTING, unmoved submodule
pin with zero risk. `session_levels.py` genuinely does not exist at the pinned commit; it is vendored here
as a single, byte-verified file (`vendor/alpha_automation_session_levels/session_levels.py`, git blob hash
`95dc487b8cbe5c07d2436daeda31de3c840f655f`, confirmed via `git hash-object` against `bf02dd2`'s own blob) --
NOT a submodule, since a fourth submodule for one file was judged more machinery than the one-time-pinned
risk it avoids. Its own internal imports (`Block`, `session_of`, `_runs`) resolve against the EXISTING,
unmoved submodule path -- all three confirmed byte-identical between the two commits."""

from __future__ import annotations

import sys
from pathlib import Path

_DETECTORS_CODE_PATH = Path(__file__).resolve().parents[2] / "vendor" / "alpha_automation_detectors" / "code"
_SESSION_LEVELS_PATH = Path(__file__).resolve().parents[2] / "vendor" / "alpha_automation_session_levels"

for _path in (_DETECTORS_CODE_PATH, _SESSION_LEVELS_PATH):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from market_structure import Block  # type: ignore[import-not-found] # noqa: E402

from session_levels import (  # type: ignore[import-not-found] # noqa: E402
    SessionLevel,
    SessionLevelKind,
    SessionLevelTouch,
    compute_prior_session_levels,
    derive_session_index,
    detect_session_level_touches,
    detect_session_mid_touches,
    session_labels,
)

from order_flow import DemandZone, detect_demand_zones  # type: ignore[import-not-found] # noqa: E402

from imbalance_mechanics import (  # type: ignore[import-not-found] # noqa: E402
    FVGKind,
    detect_fvgs,
    detect_inverse_fvgs,
    count_bpr,
)

from institutional_levels import (  # type: ignore[import-not-found] # noqa: E402
    LevelKind,
    ReferenceLevel,
    compute_prior_week_levels,
    derive_week_index,
)

from order_block_void import (  # type: ignore[import-not-found] # noqa: E402
    LiquidityVoid,
    VoidKind,
    detect_liquidity_voids,
)

__all__ = [
    "Block",
    "SessionLevel",
    "SessionLevelKind",
    "SessionLevelTouch",
    "compute_prior_session_levels",
    "derive_session_index",
    "detect_session_level_touches",
    "detect_session_mid_touches",
    "session_labels",
    "DemandZone",
    "detect_demand_zones",
    "FVGKind",
    "detect_fvgs",
    "detect_inverse_fvgs",
    "count_bpr",
    "LevelKind",
    "ReferenceLevel",
    "compute_prior_week_levels",
    "derive_week_index",
    "LiquidityVoid",
    "VoidKind",
    "detect_liquidity_voids",
]
