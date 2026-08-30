"""Wires the P007 prospective gate into the real Q4 replay path (CEO mandate: wire P007 gate into
real Q4 replay loop; Red Team E109 nonblocking note "not yet wired into a resume loop").

`reveal_next_bar_with_p007_gate()` is THE canonical entrypoint for revealing one new Q4 bar going
forward -- it composes, in the exact required order (mandate section 2), the pieces this whole
mandate chain already built and tested separately:

    extend_next_bar() -> bind_extended_fixture() -> engine.step() -> apply_p007_gate()

as ONE call, so a bar can never be revealed without the gate having evaluated it -- "a bar must not
be classified as routine/HYBRID before the P007 gate has evaluated that bar" is now a structural
property of the only reveal path, not a convention callers have to remember to follow in the right
order every time.

**Does NOT call `commit_decision()`** -- committing a decision remains the reasoning layer's own
explicit act, exactly as it always has been throughout this whole mandate chain. This function
handles only the MECHANICAL portion (reveal + gate); it returns control (and a signal-rich result)
to the caller for reasoning and an explicit commit.

**Addresses Red Team E109's "stale-ref masking" nonblocking note directly**: `apply_p007_gate()` on
its own only ever transitions `open_event_state_reference` from `None` to a candidate (by design --
see `p007_gate.py`'s own docstring on why it never auto-clears). That leaves a real, disclosed gap: a
prospectively-open P007 whose underlying price condition has ALREADY reclaimed (the detector,
replayed fresh, would report `is_open=False`) but whose durable-state lock is still set (because no
`P007_RESOLUTION` has been committed yet) is invisible to a caller that only looks at whether the
gate just flagged something NEW. `WiredRevealResult.p007_naturally_reclaimed_but_still_locked`
surfaces that condition explicitly, every call, so the reasoning layer is never left to guess -- it
does not auto-resolve anything (that stays an explicit commit), it only makes the "you may want to
consider resolving this now" signal impossible to silently miss.

**Does not touch P007's definition, S5, MGMT-004, MT5/risk/execution, or `engine.py`** -- this module
imports only the already-accepted `extend_next_bar`/`bind_extended_fixture`/`apply_p007_gate`/
`compute_p007_candidate_reference` and the unmodified `CSVCausalReplayEngine`; nothing here
reimplements or redefines anything those already do.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

from ai_trader.csv_causal_replay.engine import CSVCausalReplayEngine
from ai_trader.csv_causal_replay.fixtures.autonomous_extend import bind_extended_fixture, extend_next_bar
from ai_trader.csv_causal_replay.fixtures.materialize_sealed_fixture import OUTPUT_DIR
from ai_trader.csv_causal_replay.p007_gate import apply_p007_gate, compute_p007_candidate_reference
from ai_trader.csv_causal_replay.persistence import DurablePointerStore
from ai_trader.csv_causal_replay.types import DurableState, RevealedBar


@dataclasses.dataclass(frozen=True, slots=True)
class WiredRevealResult:
    revealed: RevealedBar
    """The bar `engine.step()` just revealed -- a `pending_decision` now exists for it; the caller
    must commit a decision for it before another bar can be revealed (unchanged, existing
    `engine.py` behavior -- this wrapper does not relax it)."""

    state_after_gate: DurableState
    """Durable state AFTER the gate ran -- `open_event_state_reference` here reflects whatever the
    gate decided for THIS bar (unchanged from before, newly set, or still set from an earlier
    candidate)."""

    new_p007_candidate_detected: bool
    """True iff THIS call's gate transitioned `open_event_state_reference` from `None` to a fresh
    candidate -- i.e. this specific bar is the trigger. HYBRID (`run_until_gate`) is refused from
    this point forward until an explicit `P007_RESOLUTION` commit clears it -- the existing,
    unmodified `engine.py` mechanism; this flag only tells the caller WHY, for this bar."""

    p007_naturally_reclaimed_but_still_locked: bool
    """True iff a P007 is currently locked (`state_after_gate.open_event_state_reference is not
    None`) AND the detector, replayed fresh through this same bar, would report the pattern as no
    longer open (price has crossed back at-or-above the causal H1 EMA50) -- yet no
    `P007_RESOLUTION` has been committed, so the lock is still mechanically in effect. Signals only;
    never auto-resolves (mandate section 2/4: resolution stays an explicit, reasoning-dependent
    commit) -- addresses Red Team E109's "stale-ref masking" nonblocking note by making this
    condition impossible to silently miss rather than by changing who decides."""


def reveal_next_bar_with_p007_gate(
    *, store: DurablePointerStore, source_path: Path, output_dir: Path = OUTPUT_DIR,
) -> WiredRevealResult:
    state_before = store.load()
    open_before = state_before.open_event_state_reference

    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    bind_extended_fixture(store=store, output_dir=output_dir)

    state_bound = store.load()
    engine = CSVCausalReplayEngine(
        sealed_csv_path=output_dir / state_bound.source_identity.source_file_name, store=store,
    )
    revealed = engine.step(expected_pointer_before=state_bound.last_committed_timestamp)

    gated_state = apply_p007_gate(store=store, output_dir=output_dir)
    new_candidate_detected = open_before is None and gated_state.open_event_state_reference is not None

    naturally_reclaimed = False
    if gated_state.open_event_state_reference is not None:
        current_fixture_path = output_dir / gated_state.source_identity.source_file_name
        candidate = compute_p007_candidate_reference(
            current_fixture_path, upto_q4_bar_index=gated_state.source_identity.sealed_through_bar_index,
        )
        naturally_reclaimed = candidate is None

    return WiredRevealResult(
        revealed=revealed, state_after_gate=gated_state,
        new_p007_candidate_detected=new_candidate_detected,
        p007_naturally_reclaimed_but_still_locked=naturally_reclaimed,
    )
