"""Bridge into `vendor/alpha_automation_detectors` only -- this package never sends an order and never
calls the frozen `demo_gate_engine` (CEO instruction, 2026-08-04: "Fara ordine, fara cost"), so it does
NOT bridge `vendor/alpha_automation_demo_gate` at all, unlike `pdh_pdl_demo`/`multi_policy_live`.

Exposes exactly what's needed for a read-only level-touch marker + volatility proxy: PDH/PDL levels and
touches (`institutional_levels`, the SAME ratified primitive `pdh_pdl_demo` uses for CAND-0001), ATR14
(`market_state`), and session labeling (`market_state.sessions`). Never modified -- this package only
reads."""

from __future__ import annotations

import sys
from pathlib import Path

_DETECTORS_CODE_PATH = Path(__file__).resolve().parents[2] / "vendor" / "alpha_automation_detectors" / "code"

if str(_DETECTORS_CODE_PATH) not in sys.path:
    sys.path.insert(0, str(_DETECTORS_CODE_PATH))

from market_structure import Block  # type: ignore[import-not-found] # noqa: E402
from market_state import atr14, sessions  # type: ignore[import-not-found] # noqa: E402
from institutional_levels import (  # type: ignore[import-not-found] # noqa: E402
    LevelKind,
    LevelTouch,
    ReferenceLevel,
    compute_prior_day_levels,
    detect_level_touches,
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
]
