"""Real end-to-end tests for the extend -> bind -> engine.step() identity handoff.

Reproduces, on synthetic data only (bars 1-10 -> 11 -> 12, never real Q4 379/380), the exact chain
the mandate requires: REAL `extend_next_bar()`, REAL `bind_extended_fixture()`, a REAL
`CSVCausalReplayEngine.step()`/`commit_decision()`, and a REAL restart (fresh `DurablePointerStore`
instance over the same file) -- nothing here simulates or mocks the engine transition.
"""

from __future__ import annotations

import csv
import dataclasses
import json

import pytest

from ai_trader.csv_causal_replay.engine import CSVCausalReplayEngine
from ai_trader.csv_causal_replay.errors import SourceIdentityMismatchError
from ai_trader.csv_causal_replay.fixtures.autonomous_extend import (
    IdentityHandoffRefusedError, bind_extended_fixture, extend_next_bar,
)
from ai_trader.csv_causal_replay.fixtures.materialize_sealed_fixture import materialize
from ai_trader.csv_causal_replay.identity import M15_BAR_INTERVAL_SECONDS, Q4_START_TS, SourceIdentity
from ai_trader.csv_causal_replay.persistence import DurablePointerStore
from ai_trader.csv_causal_replay.types import DurableState

SYNTHETIC_SOURCE_BAR_COUNT = 20
SEALED_AT = 10


def _write_synthetic_source(path, bar_count: int = SYNTHETIC_SOURCE_BAR_COUNT):
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time", "open", "high", "low", "close", "volume"])
        for i in range(bar_count):
            ts = Q4_START_TS + i * M15_BAR_INTERVAL_SECONDS
            close = 1000.0 + i + 1
            writer.writerow([ts, close - 1, close + 1, close - 1, close, 100 + i])


def _seed_sealed_scenario(tmp_path):
    source_path = tmp_path / "synthetic_source.csv"
    _write_synthetic_source(source_path)
    output_dir = tmp_path / "data"
    manifest = materialize(source_path, max_q4_bar_index=SEALED_AT, output_dir=output_dir)

    identity = SourceIdentity(
        source_file_name=manifest["source_file_name"], content_hash=manifest["content_hash"],
        symbol=manifest["symbol"], timeframe=manifest["timeframe"],
        bar_interval_seconds=manifest["bar_interval_seconds"], first_bar_ts_open=manifest["first_bar_ts_open"],
        sealed_through_bar_index=manifest["sealed_through_bar_index"], adapter_version=manifest["adapter_version"],
    )
    state = DurableState(
        source_identity=identity, session_id="test", last_committed_bar=manifest["last_bar_ts_open"],
        last_committed_timestamp=manifest["last_bar_ts_open"], next_bar=SEALED_AT + 1, pending_decision=None,
        open_event_state_reference=None, adapter_version=manifest["adapter_version"],
    )
    store_path = tmp_path / "state.json"
    store = DurablePointerStore(store_path)
    store.save(state)
    return source_path, output_dir, store_path


# ── §5 real end-to-end contract, two full cycles ────────────────────────────────────────────────

def test_real_extend_bind_step_commit_restart_extend_bind_step_chain(tmp_path):
    source_path, output_dir, store_path = _seed_sealed_scenario(tmp_path)
    store = DurablePointerStore(store_path)

    # Cycle 1: bar 10 -> bar 11, real chain throughout.
    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    bound_state = bind_extended_fixture(store=store, output_dir=output_dir)
    assert bound_state.source_identity.sealed_through_bar_index == SEALED_AT + 1

    engine = CSVCausalReplayEngine(sealed_csv_path=output_dir / bound_state.source_identity.source_file_name, store=store)
    revealed = engine.step(expected_pointer_before=bound_state.last_committed_timestamp)  # REAL step()
    assert revealed.bar_index == SEALED_AT + 1
    assert engine.status().pending_decision is not None
    engine.commit_decision(bar_id=revealed.bar.ts_open, decision_type="ROUTINE_NO_EVENT", decision_record={})  # REAL commit
    assert engine.status().next_bar == SEALED_AT + 2

    # Restart: brand-new store instance over the same file.
    del store, engine
    store2 = DurablePointerStore(store_path)

    # Cycle 2: bar 11 -> bar 12, real chain again, proving this isn't a one-shot fix.
    extend_next_bar(store=store2, source_path=source_path, output_dir=output_dir)
    bound_state2 = bind_extended_fixture(store=store2, output_dir=output_dir)
    assert bound_state2.source_identity.sealed_through_bar_index == SEALED_AT + 2

    engine2 = CSVCausalReplayEngine(sealed_csv_path=output_dir / bound_state2.source_identity.source_file_name, store=store2)
    revealed2 = engine2.step(expected_pointer_before=bound_state2.last_committed_timestamp)  # REAL step() again
    assert revealed2.bar_index == SEALED_AT + 2
    engine2.commit_decision(bar_id=revealed2.bar.ts_open, decision_type="ROUTINE_NO_EVENT", decision_record={})
    assert engine2.status().next_bar == SEALED_AT + 3


def test_engine_step_fails_closed_without_bind_proving_the_check_was_not_weakened(tmp_path):
    """Negative control: extend WITHOUT binding, then try to step a fresh engine against the new
    fixture directly -- must still fail exactly as before. Proves the fix is additive (bind), not a
    relaxation of engine.step()'s own identity check."""
    source_path, output_dir, store_path = _seed_sealed_scenario(tmp_path)
    store = DurablePointerStore(store_path)
    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    # Deliberately skip bind_extended_fixture().
    new_fixture_path = output_dir / f"Q4_SEALED_1_{SEALED_AT + 1}.csv"
    engine = CSVCausalReplayEngine(sealed_csv_path=new_fixture_path, store=store)
    state = store.load()
    with pytest.raises(SourceIdentityMismatchError):
        engine.step(expected_pointer_before=state.last_committed_timestamp)


# ── §4 crash safety: B (after creation, before bind), C (after bind, before step) ──────────────

def test_crash_after_fixture_creation_before_bind_is_recoverable(tmp_path):
    source_path, output_dir, store_path = _seed_sealed_scenario(tmp_path)
    store = DurablePointerStore(store_path)
    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    # Crash simulated here: process exits before bind_extended_fixture() ever runs.
    del store

    store2 = DurablePointerStore(store_path)
    state_before_bind = store2.load()
    assert state_before_bind.source_identity.sealed_through_bar_index == SEALED_AT  # not yet bound

    bound = bind_extended_fixture(store=store2, output_dir=output_dir)  # recovery: just call bind
    assert bound.source_identity.sealed_through_bar_index == SEALED_AT + 1
    assert bound.last_committed_bar == state_before_bind.last_committed_bar  # scientific state untouched
    assert bound.next_bar == state_before_bind.next_bar


def test_crash_after_bind_before_step_is_recoverable(tmp_path):
    source_path, output_dir, store_path = _seed_sealed_scenario(tmp_path)
    store = DurablePointerStore(store_path)
    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    bind_extended_fixture(store=store, output_dir=output_dir)
    # Crash simulated here: process exits before engine.step() is ever called.
    del store

    store2 = DurablePointerStore(store_path)
    state = store2.load()
    assert state.source_identity.sealed_through_bar_index == SEALED_AT + 1
    engine = CSVCausalReplayEngine(sealed_csv_path=output_dir / state.source_identity.source_file_name, store=store2)
    revealed = engine.step(expected_pointer_before=state.last_committed_timestamp)  # just works, nothing special needed
    assert revealed.bar_index == SEALED_AT + 1


# ── idempotency / no-op cases ────────────────────────────────────────────────────────────────────

def test_bind_before_any_extension_is_a_safe_no_op(tmp_path):
    _source_path, output_dir, store_path = _seed_sealed_scenario(tmp_path)
    store = DurablePointerStore(store_path)
    before = store.load()
    result = bind_extended_fixture(store=store, output_dir=output_dir)
    assert result.source_identity.sealed_through_bar_index == before.source_identity.sealed_through_bar_index
    assert result == before


def test_calling_bind_twice_after_one_extension_is_idempotent(tmp_path):
    source_path, output_dir, store_path = _seed_sealed_scenario(tmp_path)
    store = DurablePointerStore(store_path)
    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    first = bind_extended_fixture(store=store, output_dir=output_dir)
    second = bind_extended_fixture(store=store, output_dir=output_dir)  # nothing new to bind
    assert first == second


# ── wrong fixture hash / stale source_identity rejected ─────────────────────────────────────────

def test_bind_refuses_a_tampered_candidate_fixture(tmp_path):
    source_path, output_dir, store_path = _seed_sealed_scenario(tmp_path)
    store = DurablePointerStore(store_path)
    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    candidate = output_dir / f"Q4_SEALED_1_{SEALED_AT + 1}.csv"
    text = candidate.read_text(encoding="utf-8")
    candidate.write_text(text.replace(str(1000.0 + SEALED_AT + 1), "9999.0"), encoding="utf-8")
    with pytest.raises(IdentityHandoffRefusedError, match="tampered-since-creation"):
        bind_extended_fixture(store=store, output_dir=output_dir)


def test_bind_refuses_when_currently_bound_fixture_is_tampered(tmp_path):
    source_path, output_dir, store_path = _seed_sealed_scenario(tmp_path)
    store = DurablePointerStore(store_path)
    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    current = output_dir / f"Q4_SEALED_1_{SEALED_AT}.csv"
    current.write_text(current.read_text(encoding="utf-8") + "\n", encoding="utf-8")  # corrupt it
    with pytest.raises(IdentityHandoffRefusedError, match="possibly-tampered currently-bound fixture"):
        bind_extended_fixture(store=store, output_dir=output_dir)


def test_bind_refuses_a_manifest_that_disagrees_with_its_own_filename(tmp_path):
    source_path, output_dir, store_path = _seed_sealed_scenario(tmp_path)
    store = DurablePointerStore(store_path)
    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    manifest_path = output_dir / f"Q4_SEALED_1_{SEALED_AT + 1}_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["sealed_through_bar_index"] = SEALED_AT + 2  # lie about the boundary
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(IdentityHandoffRefusedError, match="disagrees with its filename"):
        bind_extended_fixture(store=store, output_dir=output_dir)


# ── pending decision blocks bind too (not only extend) ──────────────────────────────────────────

def test_pending_decision_blocks_bind(tmp_path):
    source_path, output_dir, store_path = _seed_sealed_scenario(tmp_path)
    store = DurablePointerStore(store_path)
    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    state = store.load()
    from ai_trader.csv_causal_replay.types import PendingDecision
    pending = PendingDecision(
        bar_id=state.last_committed_timestamp, bar_timestamp=state.last_committed_timestamp,
        bar_index=SEALED_AT,
    )
    tampered = dataclasses.replace(state, pending_decision=pending, next_bar=SEALED_AT)
    store.save(tampered)
    with pytest.raises(IdentityHandoffRefusedError, match="pending_decision is set"):
        bind_extended_fixture(store=store, output_dir=output_dir)


# ── scientific state must not mutate during bind ────────────────────────────────────────────────

def test_no_scientific_field_changes_during_bind(tmp_path):
    source_path, output_dir, store_path = _seed_sealed_scenario(tmp_path)
    store = DurablePointerStore(store_path)
    before = store.load()
    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    after = bind_extended_fixture(store=store, output_dir=output_dir)

    assert after.session_id == before.session_id
    assert after.last_committed_bar == before.last_committed_bar
    assert after.last_committed_timestamp == before.last_committed_timestamp
    assert after.next_bar == before.next_bar
    assert after.pending_decision == before.pending_decision
    assert after.open_event_state_reference == before.open_event_state_reference
    assert after.adapter_version == before.adapter_version
    # Only source_identity is different -- and only in the way expected.
    assert after.source_identity != before.source_identity
    assert after.source_identity.sealed_through_bar_index == before.source_identity.sealed_through_bar_index + 1


# ── engine.py's own symbol bug (found by this mandate's real E2E test, not merely inferred) ────
#
# `_ensure_loaded()` previously hardcoded symbol="UNKNOWN" for every fixture it opened (present
# since the original adapter commit, previously flagged only as a cosmetic nonblocking note by Red
# Team's E103 review). This mandate's real extend->bind->step() chain proved it BLOCKING: a
# correctly manifest-derived identity from bind_extended_fixture() could never match it. Fixed by
# reading the fixture's own sibling manifest instead of hardcoding a placeholder -- these two tests
# prove the fix does not create a NEW hole against the REAL Q4 checkpoint, whose own durable state
# (frozen before this fix existed) still carries the literal symbol="UNKNOWN" value today.

def test_stale_legacy_unknown_symbol_checkpoint_still_fails_closed_without_extension(tmp_path):
    """Mirrors the REAL Q4 checkpoint's exact current shape (source_identity.symbol == 'UNKNOWN',
    baked in before this fix existed) -- stepping it directly, without extending first, must still
    be refused. The exception type changed (SourceIdentityMismatchError now fires before the
    SealedBoundaryError that used to fire first) but the bar is unreachable either way -- this is a
    diagnostic-clarity change, not a safety regression."""
    source_path, output_dir, store_path = _seed_sealed_scenario(tmp_path)
    store = DurablePointerStore(store_path)
    state = store.load()
    stale_identity = dataclasses.replace(state.source_identity, symbol="UNKNOWN")
    store.save(dataclasses.replace(state, source_identity=stale_identity))

    engine = CSVCausalReplayEngine(sealed_csv_path=output_dir / stale_identity.source_file_name, store=store)
    with pytest.raises(SourceIdentityMismatchError):
        engine.step(expected_pointer_before=state.last_committed_timestamp)


def test_stale_legacy_unknown_symbol_self_heals_through_a_real_bind(tmp_path):
    """The SAME stale checkpoint as above, but now taken through the intended real path (extend +
    bind) -- the symbol self-corrects automatically (bind always derives a fresh identity from the
    target manifest, never carries the old identity's symbol forward), requiring no manual state
    edit, and the subsequent real step() succeeds."""
    source_path, output_dir, store_path = _seed_sealed_scenario(tmp_path)
    store = DurablePointerStore(store_path)
    state = store.load()
    stale_identity = dataclasses.replace(state.source_identity, symbol="UNKNOWN")
    store.save(dataclasses.replace(state, source_identity=stale_identity))

    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    bound = bind_extended_fixture(store=store, output_dir=output_dir)
    assert bound.source_identity.symbol == "OANDA:XAUUSD"

    engine = CSVCausalReplayEngine(sealed_csv_path=output_dir / bound.source_identity.source_file_name, store=store)
    revealed = engine.step(expected_pointer_before=bound.last_committed_timestamp)
    assert revealed.bar_index == SEALED_AT + 1
