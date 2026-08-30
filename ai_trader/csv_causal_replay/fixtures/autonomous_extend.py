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

## Part 2: `bind_extended_fixture()` -- the extend-to-engine identity handoff

Real end-to-end preflight (synthetic data) found a second gap once `extend_next_bar()` existed:
it creates fixture N+1 on disk, but never touches `durable_state.source_identity` (by design --
see point 3 above, "never touches durable state itself"). Nothing else did either. So the very next
real `engine.step()` -- constructed against the new fixture N+1, as it must be to read bar N+1 at
all -- fails `SourceIdentityMismatchError`, because `engine.py`'s own identity check (unmodified,
still exactly as fail-closed as before) correctly observes that durable state still names fixture N.

**The fix is not to weaken that check.** It is to add the missing explicit state transition:
`bind_extended_fixture()` updates ONLY `DurableState.source_identity` (to the verified identity of
the newly-extended fixture) via the exact same atomic `DurablePointerStore.save()` every other
mutation in this package already uses -- `last_committed_bar`, `last_committed_timestamp`,
`next_bar`, `pending_decision`, `open_event_state_reference` all pass through utterly unchanged
(`dataclasses.replace(state, source_identity=new_identity)`, nothing else touched). This is a
TRANSPORT-metadata update, not a scientific-state one.

**Idempotent by construction, not by a special-cased retry path**: `bind_extended_fixture()`
computes its own target the same way `extend_next_bar()` does (`current sealed_through_bar_index +
1`) and checks whether that specific fixture exists on disk yet:

- Fixture N+1 does not exist yet -> no-op, returns state unchanged (covers "crash before fixture N+1
  creation", and "restart before any extension was even attempted").
- Fixture N+1 exists, state not yet bound to it -> binds now (covers "crash after fixture creation,
  before bind" -- simply call this function again after restart).
- Calling it again once already bound -> the target for THIS call is now N+2 (since
  `sealed_through_bar_index` already advanced to N+1); if N+2 doesn't exist yet, another no-op.

So there is no separate "was this specific bind already done" flag to get out of sync -- the state
IS the flag (state's own `sealed_through_bar_index` vs. what exists on disk one past it).

**Content-integrity, not merely manifest-trust**: before binding, the candidate fixture's first
`current sealed_through_bar_index` Q4 rows are read back (via `SealedReader`, bounded at that exact
count) and compared byte-for-byte against the currently-bound fixture's own rows -- confirming the
candidate is genuinely a one-bar EXTENSION of the fixture already in use, not a different or
tampered file that merely claims the right boundary in its manifest.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from ai_trader.csv_causal_replay.identity import (
    ADAPTER_VERSION, M15_BAR_INTERVAL_SECONDS, Q4_START_TS, SourceIdentity, XAUUSD_M15_SYMBOL, hash_file,
)
from ai_trader.csv_causal_replay.persistence import DurablePointerStore
from ai_trader.csv_causal_replay.sealed_reader import SealedReader, SealedReaderConfig
from ai_trader.csv_causal_replay.types import DurableState
from ai_trader.csv_causal_replay.fixtures.materialize_sealed_fixture import OUTPUT_DIR, materialize


class OneBarUnlockRefusedError(Exception):
    """Fail-closed refusal from `extend_next_bar()`. Deliberately not joined to
    `ai_trader.csv_causal_replay.errors.CSVCausalReplayError` -- this module lives in `fixtures/`, a
    layer built ON TOP of the core engine (`errors.py`/`engine.py` do not import from `fixtures/` and
    should not need to know this exception exists) rather than a new member of the core state
    machine's own hierarchy."""


class IdentityHandoffRefusedError(Exception):
    """Fail-closed refusal from `bind_extended_fixture()` -- same reasoning as
    `OneBarUnlockRefusedError` for not joining the core `errors.py` hierarchy. Distinct exception
    type (not reused from `OneBarUnlockRefusedError`) so callers/tests can tell "the extension
    itself was refused" apart from "the extension succeeded but the identity handoff was refused"."""


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


def _fixture_rows_match(path_a: Path, path_b: Path, *, q4_row_count: int) -> bool:
    """True iff both fixtures' first `q4_row_count` Q4 rows are byte-identical in timestamp and
    OHLCV content (warm-up rows are not compared -- a longer/shorter warm-up window does not change
    which Q4 bars are causally available, and `materialize()` always regenerates the warm-up window
    fresh from `source_path` rather than copying it, so it is not expected to be identical from-file
    to from-file in general, only the Q4-range content is)."""
    config = SealedReaderConfig(
        symbol=XAUUSD_M15_SYMBOL, bar_interval_seconds=M15_BAR_INTERVAL_SECONDS,
        q4_start_ts=Q4_START_TS, max_q4_bar_index=q4_row_count,
    )

    def _q4_rows(path: Path) -> list[tuple[int, float, float, float, float, float]]:
        # Deliberately breaks out of the generator as soon as `q4_row_count` rows are collected --
        # a plain list comprehension would drain `iter_rows()` to exhaustion, and the CANDIDATE
        # fixture (already one bar longer than `q4_row_count`) would then trip its own
        # `SealedBoundaryError` at row `q4_row_count + 1` even though this function only ever wanted
        # the first `q4_row_count` rows from it (caught by
        # test_no_scientific_field_changes_during_bind failing during development).
        rows: list[tuple[int, float, float, float, float, float]] = []
        with SealedReader(path, config=config) as reader:
            for r in reader.iter_rows():
                if r.q4_bar_index is not None:
                    rows.append((r.bar.ts_open, r.bar.open, r.bar.high, r.bar.low, r.bar.close, r.bar.volume))
                    if len(rows) == q4_row_count:
                        break
        return rows
    return _q4_rows(path_a) == _q4_rows(path_b)


def bind_extended_fixture(*, store: DurablePointerStore, output_dir: Path = OUTPUT_DIR) -> DurableState:
    """The extend-to-engine identity handoff (see this module's own "Part 2" docstring section for
    the full design). Idempotent: safe to call after any crash point, and safe to call when there is
    nothing new to bind (returns the unchanged current state). Never reads the unsealed multi-year
    source -- everything here operates on already-sealed fixtures only."""
    if not store.exists():
        raise IdentityHandoffRefusedError(f"no durable state at {store.path} -- nothing to bind")
    state = store.load()

    if state.pending_decision is not None:
        raise IdentityHandoffRefusedError(
            f"pending_decision is set for bar {state.pending_decision.bar_id} -- a decision must be "
            "committed before the sealed boundary identity can be rebound"
        )

    current_sealed = state.source_identity.sealed_through_bar_index
    current_fixture_path = output_dir / state.source_identity.source_file_name
    if not current_fixture_path.exists():
        raise IdentityHandoffRefusedError(
            f"durable state names {current_fixture_path} as its currently-bound source, but it does "
            "not exist on disk -- refusing to bind from an unverifiable state"
        )
    if hash_file(current_fixture_path) != state.source_identity.content_hash:
        raise IdentityHandoffRefusedError(
            f"{current_fixture_path} content hash does not match durable state's recorded hash -- "
            "refusing to bind against a possibly-tampered currently-bound fixture"
        )

    candidate_boundary = current_sealed + 1
    candidate_path = output_dir / f"Q4_SEALED_1_{candidate_boundary}.csv"
    candidate_manifest_path = output_dir / f"Q4_SEALED_1_{candidate_boundary}_MANIFEST.json"
    if not candidate_path.exists():
        return state  # nothing to bind yet -- idempotent no-op (crash-before-creation / not-yet-extended)

    if not candidate_manifest_path.exists():
        raise IdentityHandoffRefusedError(
            f"{candidate_path} exists but its manifest {candidate_manifest_path} does not -- refusing "
            "to bind an incompletely-materialized fixture"
        )
    manifest = json.loads(candidate_manifest_path.read_text(encoding="utf-8"))
    if manifest.get("sealed_through_bar_index") != candidate_boundary:
        raise IdentityHandoffRefusedError(
            f"{candidate_manifest_path} claims sealed_through_bar_index="
            f"{manifest.get('sealed_through_bar_index')!r}, expected exactly {candidate_boundary} -- "
            "refusing to bind a fixture whose own manifest disagrees with its filename"
        )
    actual_candidate_hash = hash_file(candidate_path)
    if actual_candidate_hash != manifest.get("content_hash"):
        raise IdentityHandoffRefusedError(
            f"{candidate_path} content hash {actual_candidate_hash} does not match its own manifest's "
            f"recorded {manifest.get('content_hash')!r} -- refusing to bind a tampered-since-creation fixture"
        )
    if not _fixture_rows_match(current_fixture_path, candidate_path, q4_row_count=current_sealed):
        raise IdentityHandoffRefusedError(
            f"{candidate_path}'s first {current_sealed} Q4 rows do not match {current_fixture_path} "
            "byte-for-byte -- refusing to bind a fixture that is not genuinely a one-bar extension of "
            "the fixture currently in use"
        )

    new_identity = SourceIdentity(
        source_file_name=candidate_path.name, content_hash=actual_candidate_hash,
        symbol=manifest["symbol"], timeframe=manifest["timeframe"],
        bar_interval_seconds=manifest["bar_interval_seconds"], first_bar_ts_open=manifest["first_bar_ts_open"],
        sealed_through_bar_index=candidate_boundary, adapter_version=manifest.get("adapter_version", ADAPTER_VERSION),
    )
    new_state = dataclasses.replace(state, source_identity=new_identity)
    store.save(new_state)
    return new_state
