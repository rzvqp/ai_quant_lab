"""Mandate section 14: pointer progression, wrong commit, missing commit, duplicate commit, crash
after reveal before commit, clean restart, source hash mismatch, indicator no-lookahead (delegated
to test_ema.py), ATOMIC mode, HYBRID heartbeat, decision-event interruption, P007/MGMT004/NO_TRADE
protection.
"""

from __future__ import annotations

import json

import pytest

from ai_trader.csv_causal_replay.engine import CSVCausalReplayEngine
from ai_trader.csv_causal_replay.errors import (
    HybridModeLockedError, IncompleteDecisionRecordError, MissingCommitError, PointerMismatchError,
    SealedBoundaryError, SourceIdentityMismatchError, UnknownDecisionTypeError, WrongCommitBarError,
)
from ai_trader.csv_causal_replay.persistence import DurablePointerStore

BAR_378_TS = 1_602_036_900
BAR_379_TS = 1_602_037_800  # would-be next open -- must NEVER appear as an accepted value anywhere


# ── seeding / pointer progression ────────────────────────────────────────────────────────────────

def test_seed_establishes_next_bar_379_without_revealing_it(seeded_engine):
    state = seeded_engine.status()
    assert state.last_committed_bar == BAR_378_TS
    assert state.next_bar == 379
    assert state.pending_decision is None
    assert state.open_event_state_reference == "Q4-P007-003:OPEN"


def test_seeding_twice_is_refused(engine):
    engine.seed_from_known_state(session_id="s1", last_committed_bar_index=378, open_event_state_reference=None)
    with pytest.raises(Exception):  # RestartAmbiguityError
        engine.seed_from_known_state(session_id="s2", last_committed_bar_index=378, open_event_state_reference=None)


# ── ATOMIC mode / bar 379 sealed boundary (the mandate's central safety property) ───────────────

def test_atomic_step_past_378_is_sealed_and_refused(seeded_engine):
    """The single most important test in this suite: seeded exactly at the real, current bar-378
    boundary, a step forward MUST be refused -- BAR_379+ = SEALED is not conditional."""
    with pytest.raises(SealedBoundaryError) as excinfo:
        seeded_engine.step(expected_pointer_before=BAR_378_TS)
    # The refusal must not itself leak bar 379's timestamp as if it were an accepted value.
    assert str(BAR_379_TS) not in str(excinfo.value) or "refus" in str(excinfo.value).lower()


def test_atomic_step_within_sealed_range_succeeds(engine):
    """Seeds at bar 200 (an arbitrary interior point, not the mandate's own frozen boundary) purely
    to prove step() works at all within the authorized range -- bar 378 itself is deliberately never
    exercised as a reveal target anywhere in this suite (see test_atomic_step_past_378 above)."""
    engine.seed_from_known_state(session_id="s", last_committed_bar_index=200, open_event_state_reference=None)
    state_before = engine.status()
    revealed = engine.step(expected_pointer_before=state_before.last_committed_timestamp)
    assert revealed.bar_index == 201
    assert revealed.bar.close > 0


def test_pointer_progression_across_several_bars(engine):
    engine.seed_from_known_state(session_id="s", last_committed_bar_index=200, open_event_state_reference=None)
    for expected_index in range(201, 206):
        state = engine.status()
        revealed = engine.step(expected_pointer_before=state.last_committed_timestamp)
        assert revealed.bar_index == expected_index
        engine.commit_decision(bar_id=revealed.bar.ts_open, decision_type="ROUTINE_NO_EVENT", decision_record={})
    assert engine.status().next_bar == 206


# ── commit handshake: wrong / missing / duplicate ────────────────────────────────────────────────

def test_missing_commit_blocks_next_step(engine):
    engine.seed_from_known_state(session_id="s", last_committed_bar_index=200, open_event_state_reference=None)
    state = engine.status()
    engine.step(expected_pointer_before=state.last_committed_timestamp)
    with pytest.raises(MissingCommitError):
        engine.step(expected_pointer_before=state.last_committed_timestamp)


def test_wrong_commit_bar_id_is_refused(engine):
    engine.seed_from_known_state(session_id="s", last_committed_bar_index=200, open_event_state_reference=None)
    state = engine.status()
    revealed = engine.step(expected_pointer_before=state.last_committed_timestamp)
    with pytest.raises(WrongCommitBarError):
        engine.commit_decision(
            bar_id=revealed.bar.ts_open + 900, decision_type="ROUTINE_NO_EVENT", decision_record={},
        )


def test_duplicate_commit_is_refused(engine):
    engine.seed_from_known_state(session_id="s", last_committed_bar_index=200, open_event_state_reference=None)
    state = engine.status()
    revealed = engine.step(expected_pointer_before=state.last_committed_timestamp)
    engine.commit_decision(bar_id=revealed.bar.ts_open, decision_type="ROUTINE_NO_EVENT", decision_record={})
    with pytest.raises(MissingCommitError):  # nothing pending anymore -- a second commit has nothing to target
        engine.commit_decision(bar_id=revealed.bar.ts_open, decision_type="ROUTINE_NO_EVENT", decision_record={})


def test_commit_without_any_pending_reveal_is_refused(engine):
    engine.seed_from_known_state(session_id="s", last_committed_bar_index=200, open_event_state_reference=None)
    with pytest.raises(MissingCommitError):
        engine.commit_decision(bar_id=123, decision_type="ROUTINE_NO_EVENT", decision_record={})


def test_unknown_decision_type_is_refused(engine):
    engine.seed_from_known_state(session_id="s", last_committed_bar_index=200, open_event_state_reference=None)
    state = engine.status()
    revealed = engine.step(expected_pointer_before=state.last_committed_timestamp)
    with pytest.raises(UnknownDecisionTypeError):
        engine.commit_decision(bar_id=revealed.bar.ts_open, decision_type="MADE_UP_TYPE", decision_record={})


# ── pointer mismatch / crash / restart ───────────────────────────────────────────────────────────

def test_pointer_mismatch_refused_before_any_bar_is_read(engine):
    engine.seed_from_known_state(session_id="s", last_committed_bar_index=200, open_event_state_reference=None)
    with pytest.raises(PointerMismatchError):
        engine.step(expected_pointer_before=999_999_999)
    # No pending decision was created by the refused attempt.
    assert engine.status().pending_decision is None


def test_crash_after_reveal_before_commit_then_restart_is_recoverable(sealed_fixture_path, tmp_path):
    state_path = tmp_path / "durable_state.json"
    store1 = DurablePointerStore(state_path)
    engine1 = CSVCausalReplayEngine(sealed_csv_path=sealed_fixture_path, store=store1)
    engine1.seed_from_known_state(session_id="s", last_committed_bar_index=200, open_event_state_reference=None)
    state = engine1.status()
    revealed = engine1.step(expected_pointer_before=state.last_committed_timestamp)
    # Simulate a process crash: engine1/store1 are simply dropped, never committing bar 201.
    del engine1, store1

    store2 = DurablePointerStore(state_path)
    engine2 = CSVCausalReplayEngine(sealed_csv_path=sealed_fixture_path, store=store2)
    restarted_state = engine2.status()
    assert restarted_state.pending_decision is not None
    assert restarted_state.pending_decision.bar_id == revealed.bar.ts_open
    # The crash-recovered session commits the SAME bar it crashed on -- no skip, no duplicate.
    engine2.commit_decision(bar_id=revealed.bar.ts_open, decision_type="ROUTINE_NO_EVENT", decision_record={})
    assert engine2.status().next_bar == 202


def test_clean_restart_with_no_pending_decision(sealed_fixture_path, tmp_path):
    state_path = tmp_path / "durable_state.json"
    engine1 = CSVCausalReplayEngine(sealed_csv_path=sealed_fixture_path, store=DurablePointerStore(state_path))
    engine1.seed_from_known_state(session_id="s", last_committed_bar_index=200, open_event_state_reference=None)
    s = engine1.status()
    revealed = engine1.step(expected_pointer_before=s.last_committed_timestamp)
    engine1.commit_decision(bar_id=revealed.bar.ts_open, decision_type="ROUTINE_NO_EVENT", decision_record={})
    del engine1

    engine2 = CSVCausalReplayEngine(sealed_csv_path=sealed_fixture_path, store=DurablePointerStore(state_path))
    restarted = engine2.status()
    assert restarted.next_bar == 202
    assert restarted.pending_decision is None
    # No skip: the next real step reveals exactly bar 202, not 203.
    next_revealed = engine2.step(expected_pointer_before=restarted.last_committed_timestamp)
    assert next_revealed.bar_index == 202


def test_source_hash_mismatch_is_refused(sealed_fixture_path, tmp_path):
    state_path = tmp_path / "durable_state.json"
    engine1 = CSVCausalReplayEngine(sealed_csv_path=sealed_fixture_path, store=DurablePointerStore(state_path))
    engine1.seed_from_known_state(session_id="s", last_committed_bar_index=200, open_event_state_reference=None)
    del engine1

    # A byte-different "sealed" file at the same path-shape -- simulates a swapped/edited source.
    tampered = tmp_path / "tampered.csv"
    original_lines = sealed_fixture_path.read_text(encoding="utf-8").splitlines(keepends=True)
    original_lines[-1] = original_lines[-1].replace("1880.434", "9999.999")
    tampered.write_text("".join(original_lines), encoding="utf-8")

    engine2 = CSVCausalReplayEngine(sealed_csv_path=tampered, store=DurablePointerStore(state_path))
    state = engine2.status()
    with pytest.raises(SourceIdentityMismatchError):
        engine2.step(expected_pointer_before=state.last_committed_timestamp)


# ── HYBRID heartbeat / decision-event interruption / P007 ATOMIC lock ──────────────────────────

def test_hybrid_mode_refused_while_p007_open(seeded_engine):
    """Mandate section 9: Q4-P007-003 is OPEN at the real bar-378 boundary, so HYBRID must be
    refused outright, before any bar is read."""
    with pytest.raises(HybridModeLockedError):
        seeded_engine.run_until_gate(expected_pointer_before=BAR_378_TS, max_bars=8)


def test_hybrid_mode_available_once_p007_reference_is_cleared(engine):
    engine.seed_from_known_state(session_id="s", last_committed_bar_index=200, open_event_state_reference=None)
    state = engine.status()
    result = engine.run_until_gate(expected_pointer_before=state.last_committed_timestamp, max_bars=8)
    assert result.stopped_reason in ("EVENT_GATE", "HEARTBEAT_CEILING")
    assert len(result.bars_processed) <= 8
    assert len(result.bars_processed) >= 1


def test_hybrid_heartbeat_ceiling_never_exceeds_8_bars(engine):
    engine.seed_from_known_state(session_id="s", last_committed_bar_index=200, open_event_state_reference=None)
    state = engine.status()
    result = engine.run_until_gate(
        expected_pointer_before=state.last_committed_timestamp, max_bars=8, registered_levels=(),
    )
    assert len(result.bars_processed) <= 8


def test_hybrid_run_only_leaves_the_final_bar_pending_a_commit(engine):
    engine.seed_from_known_state(session_id="s", last_committed_bar_index=200, open_event_state_reference=None)
    state = engine.status()
    result = engine.run_until_gate(expected_pointer_before=state.last_committed_timestamp, max_bars=8)
    final_bar = result.bars_processed[-1]
    pending = engine.status().pending_decision
    assert pending is not None
    assert pending.bar_id == final_bar.bar.ts_open
    # Every intermediate bar was revealed (visible in bars_processed) but none silently skipped.
    indices = [b.bar_index for b in result.bars_processed]
    assert indices == list(range(indices[0], indices[0] + len(indices)))


def test_decision_event_interrupts_hybrid_run_before_the_heartbeat_ceiling(engine):
    """Registers a structural level guaranteed to be touched by the very first bar after seeding,
    forcing an EVENT_GATE stop at bar count 1, well short of the 8-bar ceiling."""
    engine.seed_from_known_state(session_id="s", last_committed_bar_index=200, open_event_state_reference=None)
    state = engine.status()
    next_bar_index = state.next_bar
    engine._ensure_loaded()  # test-only: peek the real close to register a level guaranteed to fire
    real_close = engine._bars_by_q4_index[next_bar_index].close
    result = engine.run_until_gate(
        expected_pointer_before=state.last_committed_timestamp, max_bars=8,
        registered_levels=({"price": real_close, "tolerance": 0.5},),
    )
    assert result.stopped_reason == "EVENT_GATE"
    assert result.firing.gate == "STRUCTURAL_LEVEL_TOUCH"
    assert len(result.bars_processed) == 1


def test_hybrid_run_requires_no_pending_commit_to_start(engine):
    engine.seed_from_known_state(session_id="s", last_committed_bar_index=200, open_event_state_reference=None)
    state = engine.status()
    engine.step(expected_pointer_before=state.last_committed_timestamp)  # leaves a bar pending
    with pytest.raises(MissingCommitError):
        engine.run_until_gate(expected_pointer_before=state.last_committed_timestamp, max_bars=8)


# ── decision-record protection: TRADE_CONTRACT / P007 / MGMT004 / NO_TRADE ──────────────────────

def _reveal_one(engine):
    engine.seed_from_known_state(session_id="s", last_committed_bar_index=200, open_event_state_reference=None)
    state = engine.status()
    return engine.step(expected_pointer_before=state.last_committed_timestamp)


def test_trade_contract_requires_all_seven_fields(engine):
    revealed = _reveal_one(engine)
    with pytest.raises(IncompleteDecisionRecordError):
        engine.commit_decision(
            bar_id=revealed.bar.ts_open, decision_type="TRADE_CONTRACT",
            decision_record={"entry": 1900.0, "direction": "LONG"},  # missing 5 required fields
        )


def test_trade_contract_accepted_with_all_fields(engine):
    revealed = _reveal_one(engine)
    engine.commit_decision(
        bar_id=revealed.bar.ts_open, decision_type="TRADE_CONTRACT",
        decision_record={
            "entry": 1900.0, "direction": "LONG", "initial_stop": 1895.0, "structural_target": 1910.0,
            "baseline_management": "static", "thesis": "test", "invalidation": "close below 1895",
        },
    )
    assert engine.status().pending_decision is None


def test_p007_resolution_requires_trigger_bar_id_and_resolution(engine):
    revealed = _reveal_one(engine)
    with pytest.raises(IncompleteDecisionRecordError):
        engine.commit_decision(
            bar_id=revealed.bar.ts_open, decision_type="P007_RESOLUTION", decision_record={"trigger_bar_id": 1},
        )


def test_p007_resolution_clears_the_open_event_reference(engine):
    engine.seed_from_known_state(
        session_id="s", last_committed_bar_index=200, open_event_state_reference="Q4-P007-003:OPEN",
    )
    state = engine.status()
    revealed = engine.step(expected_pointer_before=state.last_committed_timestamp)
    engine.commit_decision(
        bar_id=revealed.bar.ts_open, decision_type="P007_RESOLUTION",
        decision_record={"trigger_bar_id": 340, "resolution": "SUPPORT"},
    )
    assert engine.status().open_event_state_reference is None


def test_mgmt004_trigger_requires_trade_bar_id_and_r_multiple(engine):
    revealed = _reveal_one(engine)
    with pytest.raises(IncompleteDecisionRecordError):
        engine.commit_decision(bar_id=revealed.bar.ts_open, decision_type="MGMT004_TRIGGER", decision_record={})


def test_no_trade_actionable_requires_setup_description_and_rationale(engine):
    revealed = _reveal_one(engine)
    with pytest.raises(IncompleteDecisionRecordError):
        engine.commit_decision(
            bar_id=revealed.bar.ts_open, decision_type="NO_TRADE_ACTIONABLE",
            decision_record={"setup_description": "range top rejection"},  # missing rationale
        )


def test_routine_no_event_requires_no_fields(engine):
    revealed = _reveal_one(engine)
    engine.commit_decision(bar_id=revealed.bar.ts_open, decision_type="ROUTINE_NO_EVENT", decision_record={})
    assert engine.status().pending_decision is None


# ── durable state persistence shape ──────────────────────────────────────────────────────────────

def test_durable_state_file_is_valid_json_with_expected_top_level_shape(seeded_engine, store):
    raw = json.loads(store.path.read_text(encoding="utf-8"))
    assert raw["durable_state_schema_version"] == "csv-causal-replay-state-v1"
    assert raw["state"]["next_bar"] == 379
    assert raw["state"]["source_identity"]["sealed_through_bar_index"] == 378
