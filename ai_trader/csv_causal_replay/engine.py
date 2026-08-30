"""`CSVCausalReplayEngine` -- the CSV-backed causal state machine (mandate sections 5-9). Ports
`causal_replay.js`'s architecture (the mandate's own named conceptual reference, read in full from
`tradingview-mcp/src/core/causal_replay.js` before writing this file, not reconstructed from memory)
onto a sealed CSV source instead of a live TradingView pointer:

- `step` == `causalStepSnapshot` (Layer A): reveals exactly one bar, gated on no pending commit.
- `commit_decision` == `causalCommitDecision`: validates and clears the pending commit.
- `run_until_gate` == `causalRunUntilGate` (Layer B): reveals up to `MAX_HEARTBEAT_BARS` bars in one
  call with only the FIRST bar's pointer checked and only the LAST bar left pending a commit --
  identical internal-loop shape to the JS version's `_stepAndSnapshot` tight loop.

**What is genuinely new here, not in the JS version**: (1) durable, persisted state
(`persistence.DurablePointerStore`) instead of an in-memory flag -- mandate section 7, because
unlike a live TradingView browser tab, a CSV read has no independent ground-truth pointer to fall
back on if the process dies; every mutation goes through `DurablePointerStore.save`'s atomic write.
(2) `run_until_gate` additionally refuses whenever `open_event_state_reference` is set (mandate
section 9 -- Q4-P007-003 is OPEN at the resume boundary, so HYBRID must not be reachable until it is
explicitly cleared). (3) hitting the sealed boundary is a `SealedBoundaryError`, never silently
downgraded to an ordinary heartbeat-ceiling stop (mandate section 1: BAR_379+ = SEALED is absolute,
not a soft limit).

**Why loading the sealed fixture fully into memory here is safe** (unlike `sealed_reader`'s own
anti-`df.head(378)` warning, which is about the ORIGINAL multi-year source file): the fixture this
engine opens has ALREADY been through `SealedReader`'s bounded read once, at materialization time,
and by construction contains no row beyond bar 378. Loading an already-sealed, already-small
(~2400 rows) file fully is not the anti-pattern -- the anti-pattern is loading the UNSEALED file
fully, which this class never does and never accepts a path to (see `__init__`'s docstring)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

from ai_trader.csv_causal_replay.errors import (
    HybridModeLockedError, IncompleteDecisionRecordError, MissingCommitError, PointerMismatchError,
    RestartAmbiguityError, SealedBoundaryError, SourceIdentityMismatchError, UnknownDecisionTypeError,
    WrongCommitBarError,
)
from ai_trader.csv_causal_replay.gap_classification import classify_gap
from ai_trader.csv_causal_replay.identity import ADAPTER_VERSION, Q4_START_TS, SourceIdentity, hash_file
from ai_trader.csv_causal_replay.persistence import DurablePointerStore
from ai_trader.csv_causal_replay.sealed_reader import SealedReader, SealedReaderConfig
from ai_trader.csv_causal_replay.types import (
    MAX_HEARTBEAT_BARS, MECHANICAL_EVENT_GATES, REQUIRED_EVENT_FIELDS, Bar, DurableState,
    EventGateFiring, GapRecord, PendingDecision, RevealedBar, RunUntilGateResult,
)


def _evaluate_mechanical_gates(
    bar: Bar, gap_before: GapRecord | None, *, registered_levels: tuple[dict, ...], vol_range_threshold: float | None,
) -> EventGateFiring | None:
    """Same three mechanically-checkable gates as `causal_replay.js`'s `_evaluateMechanicalGates`,
    same order, same "gap wins first" priority."""
    if gap_before is not None:
        return EventGateFiring(gate="GAP_OR_INTEGRITY_ANOMALY", detail=gap_before.classification.value)
    for level in registered_levels:
        price = level["price"]
        tol = level.get("tolerance", 0.0)
        if bar.low - tol <= price <= bar.high + tol:
            return EventGateFiring(gate="STRUCTURAL_LEVEL_TOUCH", detail=f"price={price} tol={tol}")
    if vol_range_threshold is not None:
        bar_range = bar.high - bar.low
        if bar_range >= vol_range_threshold:
            return EventGateFiring(gate="MATERIAL_VOLATILITY_TRANSITION", detail=f"range={bar_range}")
    return None


class CSVCausalReplayEngine:
    def __init__(
        self, *, sealed_csv_path: Path, store: DurablePointerStore,
        clock: Callable[[], float] = time.time,
    ) -> None:
        """`sealed_csv_path` must point at an ALREADY-MATERIALIZED sealed fixture (i.e. the output
        of `fixtures.materialize_sealed_fixture`, or an equivalent file whose own name/hash/
        `sealed_through_bar_index` are known ahead of time) -- this class never accepts a path to,
        or opens, the original unsealed multi-year source file. `clock` is injected (mirrors
        `n1_replay.engine.N1ReplayEngine`'s own `clock` parameter) purely for deterministic tests;
        production use needs no override."""
        self._path = sealed_csv_path
        self._store = store
        self._clock = clock
        self._bars_by_q4_index: dict[int, Bar] = {}
        self._gap_before_by_q4_index: dict[int, GapRecord | None] = {}
        self._sealed_through_bar_index = 0
        self._symbol = ""
        self._bar_interval_seconds = 0
        self._first_bar_ts_open = 0
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        # Bound this read at a large-but-finite ceiling anyway (never trust the file's own claimed
        # size) -- if the fixture were somehow corrupted to contain more Q4-range rows than this,
        # SealedReader itself raises rather than this engine silently reading an unbounded amount.
        # q4_start_ts MUST be the real Q4 boundary (not 0) -- with 0, every warm-up row would also
        # satisfy `ts >= q4_start_ts` and get misclassified as a Q4 bar (caught by
        # test_engine.py::test_durable_state_file_is_valid_json_with_expected_top_level_shape
        # during development: sealed_through_bar_index came out as 2378, the total row count,
        # instead of 378).
        config = SealedReaderConfig(
            symbol="UNKNOWN", bar_interval_seconds=900, q4_start_ts=Q4_START_TS, max_q4_bar_index=100_000,
        )
        with SealedReader(self._path, config=config) as reader:
            first_ts: int | None = None
            for row in reader.iter_rows():
                if first_ts is None:
                    first_ts = row.bar.ts_open
                if row.q4_bar_index is not None:
                    self._bars_by_q4_index[row.q4_bar_index] = row.bar
                    self._gap_before_by_q4_index[row.q4_bar_index] = row.gap_before
                self._symbol = row.bar.symbol
                self._bar_interval_seconds = row.bar.ts_close - row.bar.ts_open
        self._sealed_through_bar_index = max(self._bars_by_q4_index) if self._bars_by_q4_index else 0
        self._first_bar_ts_open = first_ts or 0
        self._loaded = True

    def source_identity(self) -> SourceIdentity:
        self._ensure_loaded()
        return SourceIdentity(
            source_file_name=self._path.name, content_hash=hash_file(self._path), symbol=self._symbol,
            timeframe="M15", bar_interval_seconds=self._bar_interval_seconds,
            first_bar_ts_open=self._first_bar_ts_open, sealed_through_bar_index=self._sealed_through_bar_index,
            adapter_version=ADAPTER_VERSION,
        )

    # ── seeding (mandate section 7: reconstruct from durable state, never from UI/inference) ─────
    def seed_from_known_state(
        self, *, session_id: str, last_committed_bar_index: int, open_event_state_reference: str | None,
    ) -> DurableState:
        """Writes the INITIAL durable state matching an already-true prior fact (bar 378 was already
        consumed and committed under the old TradingView-replay system) -- does NOT itself reveal or
        commit any bar. Refuses to overwrite an existing durable state file (call this exactly once
        per fresh `store.path`; a real restart uses `status()`/`step()` against the existing file,
        never re-seeds)."""
        if self._store.exists():
            raise RestartAmbiguityError(
                f"durable state already exists at {self._store.path} -- seed_from_known_state() "
                "must be called exactly once per fresh state file; use status()/step() to resume "
                "an existing session"
            )
        self._ensure_loaded()
        identity = self.source_identity()
        last_bar = self._bars_by_q4_index.get(last_committed_bar_index)
        if last_bar is None:
            raise ValueError(
                f"seed_from_known_state: bar index {last_committed_bar_index} is not present in the "
                f"sealed fixture (sealed_through_bar_index={self._sealed_through_bar_index})"
            )
        state = DurableState(
            source_identity=identity, session_id=session_id, last_committed_bar=last_bar.ts_open,
            last_committed_timestamp=last_bar.ts_open, next_bar=last_committed_bar_index + 1,
            pending_decision=None, open_event_state_reference=open_event_state_reference,
            adapter_version=ADAPTER_VERSION,
        )
        self._store.save(state)
        return state

    def status(self) -> DurableState:
        return self._store.load()

    def _reveal_bar_at_index(self, q4_index: int) -> tuple[Bar, GapRecord | None]:
        self._ensure_loaded()
        if q4_index > self._sealed_through_bar_index:
            raise SealedBoundaryError(
                f"Q4 bar index {q4_index} exceeds this engine's sealed fixture "
                f"(sealed_through_bar_index={self._sealed_through_bar_index}). BAR_379+ = SEALED; "
                "refusing to reveal it. This is expected and correct if you are resuming from bar "
                f"{self._sealed_through_bar_index} -- see CSV_CAUSAL_REPLAY_ADAPTER_V1_HANDOFF.md."
            )
        bar = self._bars_by_q4_index[q4_index]
        gap = self._gap_before_by_q4_index[q4_index]
        return bar, gap

    def step(self, *, expected_pointer_before: int | None = None) -> RevealedBar:
        """Layer A -- `causalStepSnapshot` equivalent. Reveals exactly one bar."""
        state = self._store.load()
        if state.pending_decision is not None:
            raise MissingCommitError(
                f"bar {state.pending_decision.bar_id} was revealed and has not been committed via "
                "commit_decision() -- the pointer cannot advance until it is"
            )
        if expected_pointer_before is not None and state.last_committed_timestamp != expected_pointer_before:
            raise PointerMismatchError(
                f"caller expected last_committed_timestamp={expected_pointer_before} but durable "
                f"state has {state.last_committed_timestamp}"
            )
        if not state.source_identity.matches(self.source_identity()):
            raise SourceIdentityMismatchError(
                "the sealed fixture this engine just opened does not match the source identity "
                "recorded in durable state at the last commit -- refusing to step against a "
                "possibly-swapped file"
            )

        bar, gap = self._reveal_bar_at_index(state.next_bar)
        new_state = DurableState(
            source_identity=state.source_identity, session_id=state.session_id,
            last_committed_bar=state.last_committed_bar, last_committed_timestamp=state.last_committed_timestamp,
            next_bar=state.next_bar,
            pending_decision=PendingDecision(bar_id=bar.ts_open, bar_timestamp=bar.ts_open, bar_index=state.next_bar),
            open_event_state_reference=state.open_event_state_reference, adapter_version=state.adapter_version,
        )
        self._store.save(new_state)
        return RevealedBar(
            bar=bar, bar_index=state.next_bar, gap_before=gap,
            source_identity_fingerprint=state.source_identity.fingerprint(),
        )

    def commit_decision(self, *, bar_id: int, decision_type: str, decision_record: dict) -> DurableState:
        state = self._store.load()
        if state.pending_decision is None:
            raise MissingCommitError("there is no bar currently awaiting a decision commit")
        if bar_id != state.pending_decision.bar_id:
            raise WrongCommitBarError(
                f"commit targets bar_id {bar_id} but the pending bar is {state.pending_decision.bar_id}"
            )
        if decision_type not in REQUIRED_EVENT_FIELDS:
            raise UnknownDecisionTypeError(
                f"decision_type {decision_type!r} is not one of: {sorted(REQUIRED_EVENT_FIELDS)}"
            )
        required = REQUIRED_EVENT_FIELDS[decision_type]
        missing = [f for f in required if not decision_record.get(f)]
        if missing:
            raise IncompleteDecisionRecordError(f"decision_type {decision_type!r} requires fields: {missing}")

        committed_index = state.pending_decision.bar_index
        open_ref = state.open_event_state_reference
        if decision_type == "P007_RESOLUTION":
            open_ref = None  # the open P007 episode is now resolved -- clears the ATOMIC-mode lock
        new_state = DurableState(
            source_identity=state.source_identity, session_id=state.session_id,
            last_committed_bar=bar_id, last_committed_timestamp=bar_id, next_bar=committed_index + 1,
            pending_decision=None, open_event_state_reference=open_ref, adapter_version=state.adapter_version,
        )
        self._store.save(new_state)
        return new_state

    def run_until_gate(
        self, *, expected_pointer_before: int | None = None, max_bars: int = MAX_HEARTBEAT_BARS,
        registered_levels: tuple[dict, ...] = (), vol_range_threshold: float | None = None,
    ) -> RunUntilGateResult:
        """Layer B -- `causalRunUntilGate` equivalent, PLUS the mandate section 9 ATOMIC-mode lock:
        refuses outright while `open_event_state_reference` is set, before reading any bar."""
        state = self._store.load()
        if state.pending_decision is not None:
            raise MissingCommitError(
                f"bar {state.pending_decision.bar_id} is pending a decision commit; the runner cannot start"
            )
        if state.open_event_state_reference is not None:
            raise HybridModeLockedError(
                f"run_until_gate refused: open_event_state_reference="
                f"{state.open_event_state_reference!r} is set -- mandate section 9 requires ATOMIC "
                "mode (step()) only until this is cleared (a P007_RESOLUTION commit clears it)"
            )
        cap = min(max_bars, MAX_HEARTBEAT_BARS)
        if cap < 1:
            raise ValueError("max_bars must be >= 1")
        if expected_pointer_before is not None and state.last_committed_timestamp != expected_pointer_before:
            raise PointerMismatchError(
                f"caller expected last_committed_timestamp={expected_pointer_before} but durable "
                f"state has {state.last_committed_timestamp}"
            )

        revealed: list[RevealedBar] = []
        firing: EventGateFiring | None = None
        cursor_index = state.next_bar
        for _ in range(cap):
            bar, gap = self._reveal_bar_at_index(cursor_index)  # raises SealedBoundaryError, uncaught, if beyond 378
            revealed.append(RevealedBar(
                bar=bar, bar_index=cursor_index, gap_before=gap,
                source_identity_fingerprint=state.source_identity.fingerprint(),
            ))
            firing = _evaluate_mechanical_gates(
                bar, gap, registered_levels=registered_levels, vol_range_threshold=vol_range_threshold,
            )
            if firing is not None:
                break
            cursor_index += 1

        final = revealed[-1]
        new_state = DurableState(
            source_identity=state.source_identity, session_id=state.session_id,
            last_committed_bar=state.last_committed_bar, last_committed_timestamp=state.last_committed_timestamp,
            next_bar=final.bar_index,
            pending_decision=PendingDecision(
                bar_id=final.bar.ts_open, bar_timestamp=final.bar.ts_open, bar_index=final.bar_index,
            ),
            open_event_state_reference=state.open_event_state_reference, adapter_version=state.adapter_version,
        )
        self._store.save(new_state)
        return RunUntilGateResult(
            bars_processed=tuple(revealed),
            stopped_reason="EVENT_GATE" if firing is not None else "HEARTBEAT_CEILING",
            firing=firing,
        )
