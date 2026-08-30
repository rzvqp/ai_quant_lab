"""Adversarial tests for the Red Team E104 remediation (`fixtures.autonomous_extend.extend_next_bar`).

Uses ONLY synthetic data at a synthetic boundary (bars 1-10, extending to 11) -- never the real Q4
2020 data, never bar 379/380. `Q4_START_TS` (the real 2020-10-01 constant) is still used for the
synthetic rows' timestamps, since `SealedReaderConfig`/`materialize()` classify "Q4" rows by that
constant -- only the OHLCV VALUES are synthetic/fake, not the timestamp convention.
"""

from __future__ import annotations

import csv
import dataclasses

import pytest

from ai_trader.csv_causal_replay.fixtures.autonomous_extend import OneBarUnlockRefusedError, extend_next_bar
from ai_trader.csv_causal_replay.fixtures.materialize_sealed_fixture import materialize
from ai_trader.csv_causal_replay.identity import M15_BAR_INTERVAL_SECONDS, Q4_START_TS, SourceIdentity
from ai_trader.csv_causal_replay.persistence import DurablePointerStore
from ai_trader.csv_causal_replay.types import DurableState, PendingDecision

SYNTHETIC_SOURCE_BAR_COUNT = 20  # the "unsealed" synthetic source contains bars 1..20
SEALED_AT = 10  # the synthetic scenario starts already sealed through bar 10


def _write_synthetic_source(path, bar_count: int = SYNTHETIC_SOURCE_BAR_COUNT):
    """A tiny, fully-synthetic OHLCV series -- NOT real XAUUSD prices, NOT the real Q4 source file.
    Bar N's close is just 1000.0 + N, purely so tests can assert on it unambiguously."""
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time", "open", "high", "low", "close", "volume"])
        for i in range(bar_count):
            ts = Q4_START_TS + i * M15_BAR_INTERVAL_SECONDS
            close = 1000.0 + i + 1
            writer.writerow([ts, close - 1, close + 1, close - 1, close, 100 + i])


def _seed_sealed_scenario(tmp_path):
    """Builds a synthetic source, materializes it sealed through SEALED_AT via the REAL
    materialize(), and returns (source_path, output_dir, store, state) with durable state
    consistently pointed at that fixture -- next_bar = SEALED_AT + 1, pending_decision=None."""
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
    store = DurablePointerStore(tmp_path / "state.json")
    store.save(state)
    return source_path, output_dir, store, state


# ── valid N -> N+1 ────────────────────────────────────────────────────────────────────────────────

def test_valid_extension_produces_exactly_one_more_bar(tmp_path):
    source_path, output_dir, store, _ = _seed_sealed_scenario(tmp_path)
    manifest = extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    assert manifest["sealed_through_bar_index"] == SEALED_AT + 1
    assert manifest["q4_bar_count"] == SEALED_AT + 1
    assert (output_dir / f"Q4_SEALED_1_{SEALED_AT + 1}.csv").exists()
    # The original lower-boundary fixture is untouched.
    assert (output_dir / f"Q4_SEALED_1_{SEALED_AT}.csv").exists()


def test_extension_never_reads_or_writes_bar_12_or_beyond(tmp_path):
    source_path, output_dir, store, _ = _seed_sealed_scenario(tmp_path)
    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    new_fixture = (output_dir / f"Q4_SEALED_1_{SEALED_AT + 1}.csv").read_text(encoding="utf-8")
    bar_12_ts = str(Q4_START_TS + 11 * M15_BAR_INTERVAL_SECONDS)  # bar index 12's ts_open
    assert bar_12_ts not in new_fixture


# ── reject N -> N+2 / arbitrary large N ─────────────────────────────────────────────────────────

def test_extend_next_bar_has_no_parameter_to_request_an_arbitrary_boundary():
    import inspect
    sig = inspect.signature(extend_next_bar)
    assert set(sig.parameters) == {"store", "source_path", "output_dir"}


def test_next_bar_skip_ahead_is_refused(tmp_path):
    source_path, output_dir, store, state = _seed_sealed_scenario(tmp_path)
    tampered = dataclasses.replace(state, next_bar=SEALED_AT + 2)  # claims a skip past +1
    store.save(tampered)
    with pytest.raises(OneBarUnlockRefusedError, match="does not represent exactly one authorized step"):
        extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    assert not (output_dir / f"Q4_SEALED_1_{SEALED_AT + 2}.csv").exists()
    assert not (output_dir / f"Q4_SEALED_1_{SEALED_AT + 1}.csv").exists()


# ── pending decision blocks extension ───────────────────────────────────────────────────────────

def test_pending_decision_blocks_extension(tmp_path):
    source_path, output_dir, store, state = _seed_sealed_scenario(tmp_path)
    pending = PendingDecision(
        bar_id=state.last_committed_timestamp, bar_timestamp=state.last_committed_timestamp,
        bar_index=SEALED_AT,
    )
    tampered = dataclasses.replace(state, pending_decision=pending, next_bar=SEALED_AT)
    store.save(tampered)
    with pytest.raises(OneBarUnlockRefusedError, match="pending_decision is set"):
        extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    assert not (output_dir / f"Q4_SEALED_1_{SEALED_AT + 1}.csv").exists()


# ── stale / tampered pointer blocks ─────────────────────────────────────────────────────────────

def test_stale_last_committed_timestamp_is_refused(tmp_path):
    source_path, output_dir, store, state = _seed_sealed_scenario(tmp_path)
    tampered = dataclasses.replace(state, last_committed_timestamp=999_999_999)  # not any real bar
    store.save(tampered)
    with pytest.raises(OneBarUnlockRefusedError, match="does not equal source_identity.sealed_through_bar_index"):
        extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    assert not (output_dir / f"Q4_SEALED_1_{SEALED_AT + 1}.csv").exists()


def test_last_committed_timestamp_pointing_at_an_earlier_bar_is_refused(tmp_path):
    """A subtler tamper: the timestamp IS real, but names an earlier bar than the claimed seal."""
    source_path, output_dir, store, state = _seed_sealed_scenario(tmp_path)
    earlier_ts = Q4_START_TS + 4 * M15_BAR_INTERVAL_SECONDS  # bar index 5's ts, not bar 10's
    tampered = dataclasses.replace(state, last_committed_timestamp=earlier_ts)
    store.save(tampered)
    with pytest.raises(OneBarUnlockRefusedError, match="does not equal source_identity.sealed_through_bar_index"):
        extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)


# ── sealed_through mismatch (state vs. fixture disagree) ───────────────────────────────────────

def test_source_identity_hash_mismatch_is_refused(tmp_path):
    source_path, output_dir, store, state = _seed_sealed_scenario(tmp_path)
    tampered_identity = dataclasses.replace(state.source_identity, content_hash="0" * 64)
    tampered = dataclasses.replace(state, source_identity=tampered_identity)
    store.save(tampered)
    with pytest.raises(OneBarUnlockRefusedError, match="does not match durable state's recorded"):
        extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)


def test_missing_current_fixture_file_is_refused(tmp_path):
    source_path, output_dir, store, state = _seed_sealed_scenario(tmp_path)
    (output_dir / f"Q4_SEALED_1_{SEALED_AT}.csv").unlink()
    with pytest.raises(OneBarUnlockRefusedError, match="does not exist on disk"):
        extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)


# ── duplicate extension / lower-boundary overwrite protection ──────────────────────────────────

def test_duplicate_extension_is_refused_not_silently_reapplied(tmp_path):
    source_path, output_dir, store, _ = _seed_sealed_scenario(tmp_path)
    first = extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    original_bytes = (output_dir / f"Q4_SEALED_1_{SEALED_AT + 1}.csv").read_bytes()
    # Calling again WITHOUT updating durable state (as if commit_decision() had never run) --
    # next_bar is still SEALED_AT+1, but the target file already exists.
    with pytest.raises(OneBarUnlockRefusedError, match="already exists"):
        extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    assert (output_dir / f"Q4_SEALED_1_{SEALED_AT + 1}.csv").read_bytes() == original_bytes  # untouched


def test_cannot_be_tricked_into_overwriting_an_existing_higher_extension(tmp_path):
    source_path, output_dir, store, state = _seed_sealed_scenario(tmp_path)
    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)  # creates SEALED_AT+1
    higher_bytes = (output_dir / f"Q4_SEALED_1_{SEALED_AT + 1}.csv").read_bytes()

    # Simulate a corrupted/rolled-back state that still names the ORIGINAL SEALED_AT fixture as
    # current (as if extension had never happened) -- attempting to "re-extend" targets the SAME
    # SEALED_AT+1 file, which already exists from the real extension above.
    with pytest.raises(OneBarUnlockRefusedError, match="already exists"):
        extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    assert (output_dir / f"Q4_SEALED_1_{SEALED_AT + 1}.csv").read_bytes() == higher_bytes


# ── restart from durable state ──────────────────────────────────────────────────────────────────

def test_extension_works_correctly_after_a_simulated_restart(tmp_path):
    source_path, output_dir, store, _ = _seed_sealed_scenario(tmp_path)
    del store  # simulate process exit
    fresh_store = DurablePointerStore(tmp_path / "state.json")  # a brand-new instance, same file
    manifest = extend_next_bar(store=fresh_store, source_path=source_path, output_dir=output_dir)
    assert manifest["sealed_through_bar_index"] == SEALED_AT + 1


# ── future row not exposed on failure (applies to every refusal case above) ────────────────────

def test_no_state_file_ever_present_at_the_uncommitted_extension_path(tmp_path):
    """A final, blanket check: after every refused scenario in this file, the would-be-extended
    fixture is absent -- refusal happens strictly before any write, for every gate independently."""
    source_path, output_dir, store, state = _seed_sealed_scenario(tmp_path)
    tampered = dataclasses.replace(state, next_bar=SEALED_AT + 5)
    store.save(tampered)
    with pytest.raises(OneBarUnlockRefusedError):
        extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    for n in range(SEALED_AT + 1, SEALED_AT + 6):
        assert not (output_dir / f"Q4_SEALED_1_{n}.csv").exists()
