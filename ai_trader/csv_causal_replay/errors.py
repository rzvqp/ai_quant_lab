"""CSV causal replay fail-closed error hierarchy (CSV_CAUSAL_REPLAY_ADAPTER_V1, mandate section 8).

Every one of these is a REFUSAL, never a silent repair and never a best-effort guess -- mirrors
`ai_trader.n1_replay.errors`'s own convention (one concrete subclass per named refusal condition,
all inheriting a common base), applied to the CSV pointer/commit state machine instead of the N1
regime pipeline. No automatic repair path exists anywhere in this package for any of these -- every
constructor call site that could raise one of these instead raises it and leaves durable state
exactly as it was before the call (verified by `tests/test_adversarial.py`, not merely asserted
here).
"""

from __future__ import annotations


class CSVCausalReplayError(Exception):
    """Base class for every fail-closed refusal this package raises."""


class SourceIdentityMismatchError(CSVCausalReplayError):
    """The CSV file's own content hash (or symbol/timeframe/bar-interval identity) does not match
    the identity recorded in durable state at the last commit. Raised before any bar is read from
    the mismatched file -- a silently-swapped or silently-updated source file must never be trusted
    to continue an existing pointer."""


class TimestampOrderError(CSVCausalReplayError):
    """The next candidate row's `time` is not strictly greater than the last-committed bar's `time`
    by a positive amount -- covers both an exact duplicate-timestamp row and a genuinely
    out-of-order (backward) row. Distinct from `DuplicateBarError` (mandate: "duplicate bar" is a
    request-level replay of an already-committed bar id; this is a SOURCE-level ordering defect in
    the file itself)."""


class DuplicateBarError(CSVCausalReplayError):
    """The caller's commit references a `bar_id` that does not equal `durable_state.next_bar` --
    most commonly because it was already committed. Never silently reapplied or treated as a no-op
    success; the caller must re-derive the correct next bar id from `status()` before retrying."""


class SkippedBarError(CSVCausalReplayError):
    """The sealed source's row sequence, at the pointer's current position, does not contain the
    bar immediately following the last commit -- i.e. the reader would have to skip at least one
    row to proceed. Distinct from a classified `GapRecord` (mandate section 8's "skipped bar" is
    about the ADAPTER silently jumping past real rows that exist in the file; a classified gap is
    the SOURCE itself having no rows for an interval -- see `sealed_reader.read_next` for exactly
    where each is raised)."""


class PointerMismatchError(CSVCausalReplayError):
    """The caller's `expected_pointer_before` does not equal the durable state's own
    `last_committed_bar`/`last_committed_timestamp` at call time -- the crash-recovery/concurrent-
    caller guard, mirroring `causal_replay.js`'s own `POINTER_MISMATCH` (mandate: "pointer
    mismatch"). Fails closed before any row is read or any state is mutated."""


class MissingCommitError(CSVCausalReplayError):
    """A bar has already been revealed (durable state has a `pending_decision` recorded for it) and
    the caller is attempting to reveal a further bar without first committing a decision for the
    pending one. Mirrors `causal_replay.js`'s mandatory per-bar handshake exactly."""


class WrongCommitBarError(CSVCausalReplayError):
    """`causal_commit_decision`'s `bar_id` argument does not equal the durable state's own
    `pending_decision.bar_id` -- the caller is trying to commit a decision for a bar other than the
    one actually pending. Distinct from `DuplicateBarError` (that is "no bar is pending, this one is
    already closed"); this is "a bar IS pending, but not the one you named"."""


class IncompleteDecisionRecordError(CSVCausalReplayError):
    """`decision_record` is missing one or more fields `REQUIRED_EVENT_FIELDS[decision_type]`
    mandates for the given `decision_type` (mirrors `causal_replay.js`'s own required-field map --
    see `types.REQUIRED_EVENT_FIELDS`)."""


class UnknownDecisionTypeError(CSVCausalReplayError):
    """`decision_type` is not one of the six recognized values. Refused rather than guessed --
    mandate section 8: "no automatic repair that could reveal future information," which an
    unrecognized/ambiguous decision type could silently become if given a default interpretation."""


class SealedBoundaryError(CSVCausalReplayError):
    """The caller (or, in the sealed dev/test reader, the underlying materialized fixture itself)
    attempted to read or reveal a bar beyond the sealed boundary (`SealedReader.max_bar_index` in
    dev/test; `AUTHORITATIVE_NEXT_UNSEEN_BAR` in the full-source reader once the durable pointer
    reaches it). This is the mechanical enforcement of BAR_379+ = SEALED (mandate section 1) --
    raised BEFORE the row is parsed into a `Bar`, not after, so no OHLCV value from beyond the
    boundary is ever constructed, held in a variable, or exception-message-interpolated (see
    `sealed_reader.SealedReader.read_next`'s own comment on why the row is never even sliced out of
    the line first)."""


class RestartAmbiguityError(CSVCausalReplayError):
    """Durable state was found on disk but is internally inconsistent (e.g. a `pending_decision`
    whose `bar_id` does not match `next_bar`, or a state file that fails its own schema/version
    check) -- refused rather than guessed at, per mandate section 8's "restart ambiguity". The
    caller must resolve the inconsistency out of band (inspecting the raw state file and the
    apprenticeship ledgers, exactly as `CAUSAL_REPLAY_ACCELERATOR_V1_HANDOFF.md` section 2 already
    instructs for the live-TradingView variant) before this engine will resume."""


class NonFiniteBarValueError(CSVCausalReplayError):
    """A row's OHLCV field parsed to NaN/Infinity, or failed to parse as a float at all. Refused
    before the row becomes a `Bar` -- mirrors `n1_replay.errors.NonFiniteAxesInputError`'s own
    reasoning (a non-finite value would otherwise propagate silently into every downstream
    computation)."""


class HybridModeLockedError(CSVCausalReplayError):
    """`run_until_gate` (HYBRID) was called while `DurableState.open_event_state_reference` is set
    -- mandate section 9: Q4-P007-003 is OPEN at the bar-378 resume boundary, so only `step`
    (ATOMIC) may be used until an explicit `P007_RESOLUTION` commit clears the reference. Refused
    before any bar is read."""
