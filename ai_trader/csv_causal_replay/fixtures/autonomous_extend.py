"""Autonomous-Q4 fail-closed one-bar extension gate.

Remediates Red Team's `RT-CSV-INCREMENTAL-UNLOCK-BAR379-REVIEW-001` (E104, commit `61e88aa`,
`SAFE_FOR_AUTONOMOUS_SEQUENTIAL_Q4=NO`) single blocking finding, `ONE_BAR_UNLOCK_ENFORCED=FAIL`:
`materialize_sealed_fixture.materialize()`'s `--max-bar` accepts an arbitrary boundary and reads
nothing from durable state, so a single call (`--max-bar 5900`) would materialize bars 380..5900 --
bulk future exposure the engine's own per-bar `step()`/`commit_decision()` handshake does not
prevent, because materialization is a separate code path from that handshake entirely.

`extend_next_bar()` below is the ONLY entrypoint an autonomous Q4-continuation runtime may call to
grow the sealed boundary. It:

1. Derives `TARGET_BOUNDARY = durable_state.source_identity.sealed_through_bar_index + 1`
   INTERNALLY -- the caller supplies a source path (needed to actually read the new bar's content)
   and a durable-state store, never a boundary value. There is no parameter through which a caller
   could request `current + 2`, `current + 10`, or any other N.
2. Refuses (`OneBarUnlockRefusedError`, no fixture written, no state touched) unless ALL of:
   - `pending_decision is None` (mandate section 5: commit-before-extend)
   - the currently-open sealed fixture named in durable state still exists and its content hash
     still matches what durable state recorded (`SourceIdentityMismatchError`'s own concern, applied
     here to the EXTENSION path rather than `engine.step()`)
   - `last_committed_timestamp` is genuinely present, AT the fixture's own claimed
     `sealed_through_bar_index` -- verified by looking the timestamp up in the fixture's own row
     content (not merely trusting the state file's internal arithmetic; a state file with a
     correct-looking `next_bar` but a tampered `last_committed_timestamp` is caught here)
   - `next_bar == sealed_through_bar_index + 1` exactly
3. On success, calls `materialize_sealed_fixture.materialize()` with the internally-derived target
   and returns its manifest. Never touches durable state itself -- extending the fixture and
   consuming the new bar via `engine.step()`/`commit_decision()` remain two separate, separately
   observable actions (this function makes ONE new bar's data READABLE; it does not reveal or commit
   it through the causal handshake).

**Explicit reachability distinction (mandate section 4)**: `materialize_sealed_fixture.materialize()`
/ its CLI (`--max-bar`) remain available, unchanged, for CEO-authorized manual/research use -- e.g.
rebuilding a fixture, or a deliberate multi-bar jump under explicit one-off authorization outside the
autonomous loop. Nothing in THIS module, or in `engine.py`, calls that arbitrary-N path. An
autonomous Q4-continuation runtime must be wired to `extend_next_bar()` alone.
"""

from __future__ import annotations

from pathlib import Path

from ai_trader.csv_causal_replay.identity import (
    M15_BAR_INTERVAL_SECONDS, Q4_START_TS, XAUUSD_M15_SYMBOL, hash_file,
)
from ai_trader.csv_causal_replay.persistence import DurablePointerStore
from ai_trader.csv_causal_replay.sealed_reader import SealedReader, SealedReaderConfig
from ai_trader.csv_causal_replay.fixtures.materialize_sealed_fixture import OUTPUT_DIR, materialize


class OneBarUnlockRefusedError(Exception):
    """Fail-closed refusal from `extend_next_bar()`. Deliberately not joined to
    `ai_trader.csv_causal_replay.errors.CSVCausalReplayError` -- this module lives in `fixtures/`, a
    layer built ON TOP of the core engine (`errors.py`/`engine.py` do not import from `fixtures/` and
    should not need to know this exception exists) rather than a new member of the core state
    machine's own hierarchy."""


def _bar_index_for_timestamp(sealed_csv_path: Path, ts: int, *, ceiling: int) -> int | None:
    """Looks up which Q4 bar index a timestamp corresponds to, by reading an ALREADY-sealed fixture
    up to its own claimed boundary (`ceiling`) -- never touches the unsealed multi-year source.
    Reading is bounded at `ceiling` deliberately, not an arbitrarily large number: if the fixture on
    disk somehow contains MORE rows than its own claimed boundary (a tamper/corruption scenario),
    `SealedReader` raises `SealedBoundaryError` once iteration would exceed `ceiling` -- surfacing
    that as a hard failure here rather than silently reading past what the fixture claims to be
    sealed through. Returns `None` if `ts` is not found among the rows actually read (e.g. it names a
    warm-up bar, or a bar past `ceiling`)."""
    config = SealedReaderConfig(
        symbol=XAUUSD_M15_SYMBOL, bar_interval_seconds=M15_BAR_INTERVAL_SECONDS,
        q4_start_ts=Q4_START_TS, max_q4_bar_index=ceiling,
    )
    with SealedReader(sealed_csv_path, config=config) as reader:
        for row in reader.iter_rows():
            if row.bar.ts_open == ts:
                return row.q4_bar_index
    return None


def extend_next_bar(*, store: DurablePointerStore, source_path: Path, output_dir: Path = OUTPUT_DIR) -> dict:
    if not store.exists():
        raise OneBarUnlockRefusedError(f"no durable state at {store.path} -- nothing to extend")
    state = store.load()

    if state.pending_decision is not None:
        raise OneBarUnlockRefusedError(
            f"pending_decision is set for bar {state.pending_decision.bar_id} -- a decision must be "
            "committed (commit_decision()) before the sealed boundary can be extended"
        )

    current_sealed = state.source_identity.sealed_through_bar_index
    current_fixture_path = output_dir / state.source_identity.source_file_name
    if not current_fixture_path.exists():
        raise OneBarUnlockRefusedError(
            f"durable state names {current_fixture_path} as its sealed source, but it does not "
            "exist on disk -- refusing to extend from an unverifiable state"
        )
    actual_hash = hash_file(current_fixture_path)
    if actual_hash != state.source_identity.content_hash:
        raise OneBarUnlockRefusedError(
            f"{current_fixture_path} content hash {actual_hash} does not match durable state's "
            f"recorded {state.source_identity.content_hash} -- refusing to extend a possibly-"
            "tampered or since-modified fixture"
        )

    if state.last_committed_timestamp is None:
        raise OneBarUnlockRefusedError(
            "durable state has no last_committed_timestamp -- nothing has been committed yet, so "
            "there is no confirmed boundary to extend from"
        )
    committed_index = _bar_index_for_timestamp(
        current_fixture_path, state.last_committed_timestamp, ceiling=current_sealed,
    )
    if committed_index != current_sealed:
        raise OneBarUnlockRefusedError(
            f"last_committed_timestamp={state.last_committed_timestamp} maps to Q4 bar index "
            f"{committed_index!r} in the sealed fixture, which does not equal "
            f"source_identity.sealed_through_bar_index={current_sealed} -- durable state and the "
            "sealed fixture disagree about where the boundary actually is; refusing to extend"
        )

    if state.next_bar != current_sealed + 1:
        raise OneBarUnlockRefusedError(
            f"next_bar={state.next_bar} != sealed_through_bar_index + 1 = {current_sealed + 1} -- "
            "refusing to extend from a state that does not represent exactly one authorized step "
            "forward from the current seal"
        )

    target_boundary = current_sealed + 1
    new_fixture_path = output_dir / f"Q4_SEALED_1_{target_boundary}.csv"
    if new_fixture_path.exists():
        raise OneBarUnlockRefusedError(
            f"{new_fixture_path} already exists -- refusing a duplicate/overwrite extension; if this "
            "is a genuine retry after a prior successful extension, read its existing manifest "
            "rather than re-materializing"
        )

    return materialize(source_path, max_q4_bar_index=target_boundary, output_dir=output_dir)
