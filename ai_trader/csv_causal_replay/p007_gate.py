"""Durable P007 prospective-detection gate (CEO mandate: durable Q4 P007 prospective detection
gate). The missing piece Red Team's E108 review found: AI Trader's own record cited a preventive
fix in `q4_batch_runner.py` that does not exist anywhere in the repository ("the cited preventive
fix is NOT verifiable... recommend the fix be actually committed + tested"). `apply_p007_gate()`
below is that fix, committed and tested.

**Never touches `engine.py`** -- mandate section 2's own "do not redesign the replay architecture"
is honored literally: `engine.py`'s existing `open_event_state_reference` mechanism (already used
for Q4-P007-003, already what `run_until_gate` already refuses on) is reused exactly as-is. This
module only ever WRITES that one field, through the exact same
`dataclasses.replace(state, ...)` + `DurablePointerStore.save()` pattern
`fixtures.autonomous_extend.bind_extended_fixture()` already established for updating one field of
durable state without touching the others.

**One-directional by design**: this gate only ever transitions `open_event_state_reference` from
`None` to a candidate reference (a fresh mechanical detection) -- it NEVER clears it. Clearing stays
exactly what it already was: an explicit `engine.commit_decision(decision_type="P007_RESOLUTION",
...)` call, the reasoning layer's own prospective classification, not a mechanical side effect of
price crossing back above the EMA (mandate section 4: "force reasoning-dependent handling... until
the event is prospectively classified/resolved" -- classification is the reasoning layer's job).
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

from ai_trader.csv_causal_replay.identity import M15_BAR_INTERVAL_SECONDS, Q4_START_TS, XAUUSD_M15_SYMBOL
from ai_trader.csv_causal_replay.p007_detector import P007Detector
from ai_trader.csv_causal_replay.persistence import DurablePointerStore
from ai_trader.csv_causal_replay.sealed_reader import SealedReader, SealedReaderConfig
from ai_trader.csv_causal_replay.types import DurableState


class P007GateRefusedError(Exception):
    """Raised only for a genuine anomaly (the currently-bound fixture is missing) -- never raised
    merely because there is nothing new to flag; that case is a normal no-op return, not an error."""


def compute_p007_candidate_reference(sealed_csv_path: Path, *, upto_q4_bar_index: int) -> str | None:
    """Pure function, no state file access: replays `sealed_csv_path` (warm-up + Q4 rows) through a
    fresh `P007Detector` up to `upto_q4_bar_index` and returns the candidate reference that SHOULD
    be in effect -- `None` if no P007 is currently open, or
    `"Q4-P007-CANDIDATE:OPEN@bar_<trigger_index>"` if one is. Rebuilt from scratch every call
    (mandate section 2: minimal, no new persisted detector state) -- cheap at this data's scale
    (a few hundred to a few thousand M15 bars is a trivial replay)."""
    config = SealedReaderConfig(
        symbol=XAUUSD_M15_SYMBOL, bar_interval_seconds=M15_BAR_INTERVAL_SECONDS,
        q4_start_ts=Q4_START_TS, max_q4_bar_index=upto_q4_bar_index,
    )
    detector = P007Detector()
    with SealedReader(sealed_csv_path, config=config) as reader:
        for row in reader.iter_rows():
            if row.q4_bar_index is None:
                detector.feed_warmup(row.bar)
            else:
                detector.feed(row.bar, row.q4_bar_index)
    if not detector.is_open:
        return None
    return f"Q4-P007-CANDIDATE:OPEN@bar_{detector.open_since_bar_index}"


def apply_p007_gate(*, store: DurablePointerStore, output_dir: Path) -> DurableState:
    """Loads current durable state, recomputes whether a P007 candidate should be open as of the
    currently-bound fixture's own sealed boundary, and -- ONLY if that recomputation newly says
    "open" while durable state currently says `open_event_state_reference is None` -- writes the
    updated state. Safe to call after every `engine.step()`/`bind_extended_fixture()`, including
    while a decision is still pending for the just-revealed bar (unlike
    `extend_next_bar`/`bind_extended_fixture`, this function does NOT require
    `pending_decision is None` -- its whole purpose is to inform the CURRENT pending decision before
    it is committed, so the reasoning layer sees the flag before deciding how to classify that bar)."""
    state = store.load()
    if state.open_event_state_reference is not None:
        return state  # already flagged (this candidate or an earlier one) -- idempotent no-op,
        # checked FIRST so an already-open state never depends on the fixture still being readable

    current_fixture_path = output_dir / state.source_identity.source_file_name
    if not current_fixture_path.exists():
        raise P007GateRefusedError(
            f"durable state names {current_fixture_path} as its sealed source, but it does not "
            "exist on disk -- refusing to evaluate the P007 gate against an unverifiable fixture"
        )

    candidate = compute_p007_candidate_reference(
        current_fixture_path, upto_q4_bar_index=state.source_identity.sealed_through_bar_index,
    )
    if candidate is None:
        return state  # nothing open -- no-op, matches "never auto-clears" (see module docstring)

    new_state = dataclasses.replace(state, open_event_state_reference=candidate)
    store.save(new_state)
    return new_state
