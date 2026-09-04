"""Frozen snapshot + hash (design doc Section 8, steps 2-4). The snapshot SHAPE is identical to
`loop.py::_snapshot()` (same bar-count-per-timeframe convention, same dict shape) -- redeclared here
rather than imported for the same `MetaTrader5` transitive-import reason documented in
`primitives.py`. `frozen_snapshot_hash` is new: no hashing of `snapshot` occurs anywhere in the
existing S5 code path (confirmed before writing this file) -- `START_JSON`'s own one-off
`content_sha256` is unrelated, reused here only as a style precedent (same algorithm, same
hex-digest convention), not as shared code.
"""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_trader.apprenticeship_v2.mt5_read_only_source import ReadOnlyBar

SNAPSHOT_BAR_COUNTS = {"H4": 12, "H1": 24, "M15": 60, "M5": 48}
"""Byte-identical to `loop.py::SNAPSHOT_BAR_COUNTS` -- the design doc requires the exact existing
`_snapshot()` shape (Section 3: "`_snapshot()` in `loop.py` already captures H4/H1/M15/M5
identically -- never an independent trigger source"); kept as the same literal values, not
re-derived."""


def _bar_to_dict(b: "ReadOnlyBar") -> dict[str, object]:
    return {
        "ts_open": b.ts_open, "ts_close": b.ts_close, "open": b.open, "high": b.high, "low": b.low,
        "close": b.close, "volume": b.volume,
    }


def build_snapshot(
    h4: "list[ReadOnlyBar]", h1: "list[ReadOnlyBar]", m15: "list[ReadOnlyBar]", m5: "list[ReadOnlyBar]",
) -> dict[str, list[dict[str, object]]]:
    """Every bar list passed in must already be causally-closed-only (the same guarantee
    `mt5_read_only_source.fetch_causal_closed_bars` already provides) and must not extend past the
    trigger bar -- this function does not itself filter by trigger timestamp; that is the caller's
    responsibility (mandate section 10's own "prefix invariance" test proves callers uphold it)."""
    return {
        "H4": [_bar_to_dict(b) for b in h4[-SNAPSHOT_BAR_COUNTS["H4"]:]],
        "H1": [_bar_to_dict(b) for b in h1[-SNAPSHOT_BAR_COUNTS["H1"]:]],
        "M15": [_bar_to_dict(b) for b in m15[-SNAPSHOT_BAR_COUNTS["M15"]:]],
        "M5": [_bar_to_dict(b) for b in m5[-SNAPSHOT_BAR_COUNTS["M5"]:]],
    }


def compute_snapshot_hash(snapshot: dict[str, list[dict[str, object]]]) -> str:
    """SHA-256 over the snapshot's OWN canonical JSON serialization (design doc Section 8 step 4) --
    `sort_keys=True` makes this independent of dict-insertion order (Python dicts preserve insertion
    order, which is not itself a semantic property of the snapshot's content, so it must not affect
    the hash), and a fixed separator makes the serialization whitespace-independent too. Deterministic:
    the same snapshot content always produces the same hash, on any machine, any process."""
    canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def verify_snapshot_hash(snapshot: dict[str, list[dict[str, object]]], expected_hash: str) -> bool:
    """Tamper detection (design doc Section 10's own required test): recomputes the hash fresh and
    compares -- any mutation to the snapshot's content changes the hash."""
    return compute_snapshot_hash(snapshot) == expected_hash
