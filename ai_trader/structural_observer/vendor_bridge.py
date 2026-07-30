"""Bridge into the vendored structural-detector code (Mandate 4, 2026-07-29). CEO instruction:
"Puntea cross-repo... Construieste puntea -- submodul, vendoring sau install, alegi tu si justifici."

**Choice: git submodule, pinned to an exact commit** (`vendor/alpha_automation_detectors`, tracking
`ai_quant_lab-alpha-automation` branch `discovery-mk-matrix-v1`). Justification: these seven modules are
described as frozen and, for several, independently audited -- a submodule pin is a cryptographic-strength
provenance record (the exact commit becomes part of THIS repo's own git history), so any future update is
a deliberate, auditable action (bumping the pointer), never silent drift. Vendoring (copying the source)
was rejected because it forks the code the moment it's copied -- a fix or a further audit on the
original would never propagate, and the copy could silently diverge from what "frozen and audited"
means. A package install was rejected because the source has no packaging metadata (`code/` is a flat
script directory, not a distributable package) -- building one would mean modifying a repository this
mandate does not authorize touching.

**Why this file exists, specifically**: the vendored modules use PLAIN, non-namespaced imports
(`from market_structure import Block`, not `from vendor.alpha_automation_detectors.code.market_structure
import Block`) -- in their own repository they are flat scripts that assume `code/` itself is on
`sys.path`, not an installable package. This file is the ONE place that performs that `sys.path`
insertion, so nothing else in `ai_trader` needs to know the vendored code isn't a normal package.
Nothing in the vendored code is modified -- confirmed unchanged from the submodule's own pinned commit
(`61cbd58c3d5da19001b125b65d669ddad54a14c4`) by construction: this file only reads from it.

mypy cannot resolve these dynamically path-inserted imports statically -- hence the `type: ignore`
comments below, the same convention already used for `RealMT5Gateway`'s own `import MetaTrader5`. Every
value that crosses this boundary is immediately converted to a concretely-typed Python primitive at the
call site in `observer.py`, matching the fail-closed `getattr`-based boundary convention already
established for MT5's own untyped return values (`mt5_pnl_source`, `mt5_account_bridge`).
"""

from __future__ import annotations

import sys
from pathlib import Path

_VENDOR_CODE_PATH = Path(__file__).resolve().parents[2] / "vendor" / "alpha_automation_detectors" / "code"

if str(_VENDOR_CODE_PATH) not in sys.path:
    sys.path.insert(0, str(_VENDOR_CODE_PATH))

from market_structure import Block, detect_swings, label_structure, detect_breaks  # type: ignore[import-not-found] # noqa: E402
from imbalance_mechanics import detect_fvgs, detect_fvg_reactions  # type: ignore[import-not-found] # noqa: E402
from market_state import expansion, compression, sessions  # type: ignore[import-not-found] # noqa: E402
from order_flow import (  # type: ignore[import-not-found] # noqa: E402
    detect_order_blocks,
    track_breaker,
    detect_mitigations,
    detect_rejections,
)

__all__ = [
    "Block",
    "detect_swings",
    "label_structure",
    "detect_breaks",
    "detect_fvgs",
    "detect_fvg_reactions",
    "expansion",
    "compression",
    "sessions",
    "detect_order_blocks",
    "track_breaker",
    "detect_mitigations",
    "detect_rejections",
]
