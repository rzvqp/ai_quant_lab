"""Unit tests for :mod:`ai_trader.context_memory.repository`."""

from __future__ import annotations

import json
import threading
from pathlib import Path

import pytest

from ai_trader.context_memory.repository import (
    ConflictingDuplicateError,
    ContextMemoryRepository,
    RepositoryCorruptionError,
    RepositoryPathError,
    RepositoryWriteError,
    _JsonlStream,
)
from ai_trader.context_memory.codec import (
    UnsupportedSchemaVersionError,
    decode_context_snapshot,
    encode_context_snapshot,
)
from ai_trader.context_memory.identities import compute_context_snapshot_id
from ai_trader.context_memory.tests._fixtures import (
    AS_OF,
    make_edge_reference,
    make_observation,
    make_pending_outcome,
    make_snapshot,
)


def _repo(tmp_path: Path) -> ContextMemoryRepository:
    return ContextMemoryRepository(tmp_path / "repo")


# ------------------------------------------------------------------ append / duplicate policy


def test_first_append(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    snap = make_snapshot()
    record_id = repo.append_context_snapshot(snap)
    assert record_id == compute_context_snapshot_id(snap)
    assert repo.count_context_snapshots() == 1


def test_repeated_exact_append_is_idempotent(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    snap = make_snapshot()
    first = repo.append_context_snapshot(snap)
    second = repo.append_context_snapshot(snap)
    assert first == second
    assert repo.count_context_snapshots() == 1  # no second line written


def test_conflicting_duplicate_is_rejected(tmp_path: Path) -> None:
    # White-box: the public Repository API can never construct this scenario (an ID is always freshly
    # computed from the object being appended), so this documented policy is proven directly against
    # the internal _JsonlStream, whose append() takes an explicit, caller-supplied id.
    stream = _JsonlStream(
        tmp_path / "stream.jsonl", encode_context_snapshot, decode_context_snapshot, compute_context_snapshot_id,
    )
    snap_a = make_snapshot()
    snap_b = make_snapshot(instrument="EURUSD")
    stream.append(snap_a, "shared-id")
    with pytest.raises(ConflictingDuplicateError):
        stream.append(snap_b, "shared-id")


def test_deterministic_batch_append(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    snaps = [make_snapshot(as_of=AS_OF + i) for i in range(3)]
    ids = repo.append_context_snapshots(snaps)
    assert ids == tuple(compute_context_snapshot_id(s) for s in snaps)
    assert repo.count_context_snapshots() == 3
    assert list(repo.iter_context_snapshots()) == snaps  # caller order preserved


# ------------------------------------------------------------------ read


def test_read_by_id(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    snap = make_snapshot()
    record_id = repo.append_context_snapshot(snap)
    assert repo.get_context_snapshot(record_id) == snap


def test_read_missing_id_returns_none(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    missing = compute_context_snapshot_id(make_snapshot(as_of=AS_OF + 999))
    assert repo.get_context_snapshot(missing) is None


def test_deterministic_iteration_order(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    snaps = [make_snapshot(as_of=AS_OF + i) for i in range(5)]
    for s in snaps:
        repo.append_context_snapshot(s)
    assert list(repo.iter_context_snapshots()) == snaps


def test_record_type_isolation(tmp_path: Path) -> None:
    # "Filter by record type" is satisfied structurally -- each stream is already exactly one type.
    repo = _repo(tmp_path)
    repo.append_context_snapshot(make_snapshot())
    repo.append_observation(make_observation())
    assert repo.count_context_snapshots() == 1
    assert repo.count_observations() == 1
    assert all(hasattr(x, "instrument") for x in repo.iter_context_snapshots())
    assert all(hasattr(x, "present_edges") for x in repo.iter_observations())


# ------------------------------------------------------------------ reopen / rebuild


def test_reopen_and_rebuild(tmp_path: Path) -> None:
    path = tmp_path / "repo"
    snap = make_snapshot()
    repo1 = ContextMemoryRepository(path)
    record_id = repo1.append_context_snapshot(snap)

    repo2 = ContextMemoryRepository(path)  # fresh instance, same path
    assert repo2.count_context_snapshots() == 1
    assert repo2.get_context_snapshot(record_id) == snap


def test_rebuild_method_picks_up_external_changes(tmp_path: Path) -> None:
    path = tmp_path / "repo"
    repo1 = ContextMemoryRepository(path)
    repo2 = ContextMemoryRepository(path)
    snap = make_snapshot()
    repo1.append_context_snapshot(snap)
    assert repo2.count_context_snapshots() == 0  # repo2 hasn't rebuilt yet
    repo2.rebuild()
    assert repo2.count_context_snapshots() == 1


# ------------------------------------------------------------------ integrity / corruption


def test_integrity_verification_on_healthy_repository(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    repo.append_context_snapshot(make_snapshot())
    repo.append_observation(make_observation())
    report = repo.verify_integrity()
    assert report.ok
    assert report.context_snapshot_count == 1
    assert report.observation_count == 1
    assert report.corrupt_lines == ()


def test_malformed_record_detection_on_open(tmp_path: Path) -> None:
    path = tmp_path / "repo"
    repo = ContextMemoryRepository(path)
    repo.append_context_snapshot(make_snapshot())
    with (path / "context_snapshots.jsonl").open("a", encoding="utf-8") as f:
        f.write("not valid json at all\n")
    with pytest.raises(RepositoryCorruptionError):
        ContextMemoryRepository(path)


def test_truncated_record_detection(tmp_path: Path) -> None:
    path = tmp_path / "repo"
    repo = ContextMemoryRepository(path)
    repo.append_context_snapshot(make_snapshot())
    with (path / "context_snapshots.jsonl").open("a", encoding="utf-8") as f:
        f.write('{"record_id": "abc", "sequence": 1, "payload": {"instrument": "XAU\n')  # truncated mid-line
    with pytest.raises(RepositoryCorruptionError):
        ContextMemoryRepository(path)


def test_tampered_payload_is_detected_via_id_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "repo"
    repo = ContextMemoryRepository(path)
    repo.append_context_snapshot(make_snapshot())
    snapshot_file = path / "context_snapshots.jsonl"
    lines = snapshot_file.read_text(encoding="utf-8").splitlines()
    envelope = json.loads(lines[0])
    envelope["payload"]["instrument"] = "TAMPERED"  # payload changed, record_id NOT recomputed
    snapshot_file.write_text(json.dumps(envelope) + "\n", encoding="utf-8")
    with pytest.raises(RepositoryCorruptionError, match="does not match"):
        ContextMemoryRepository(path)


def test_unsupported_schema_detection(tmp_path: Path) -> None:
    path = tmp_path / "repo"
    repo = ContextMemoryRepository(path)
    repo.append_context_snapshot(make_snapshot())
    snapshot_file = path / "context_snapshots.jsonl"
    lines = snapshot_file.read_text(encoding="utf-8").splitlines()
    envelope = json.loads(lines[0])
    envelope["payload"]["context_memory_schema_version"] = {"namespace": "context_memory", "version": "v999"}
    snapshot_file.write_text(json.dumps(envelope) + "\n", encoding="utf-8")
    with pytest.raises(UnsupportedSchemaVersionError):
        ContextMemoryRepository(path)


def test_verify_integrity_reports_corruption_without_raising(tmp_path: Path) -> None:
    path = tmp_path / "repo"
    repo = ContextMemoryRepository(path)
    repo.append_context_snapshot(make_snapshot())
    with (path / "observations.jsonl").open("a", encoding="utf-8") as f:
        f.write("garbage\n")
    # repo (already open, unaffected) can still report on-disk corruption without re-raising itself
    report = repo.verify_integrity()
    assert not report.ok
    assert len(report.corrupt_lines) == 1


# ------------------------------------------------------------------ path handling


def test_repository_creates_missing_directory(tmp_path: Path) -> None:
    path = tmp_path / "does" / "not" / "exist" / "yet"
    repo = ContextMemoryRepository(path)
    assert path.is_dir()
    assert repo.count_context_snapshots() == 0


def test_invalid_path_raises(tmp_path: Path) -> None:
    file_path = tmp_path / "not_a_directory.txt"
    file_path.write_text("hello", encoding="utf-8")
    with pytest.raises(RepositoryPathError):
        ContextMemoryRepository(file_path)


# ------------------------------------------------------------------ immutability / no mutation


def test_source_records_remain_unchanged_after_append(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    snap = make_snapshot()
    original = make_snapshot()
    repo.append_context_snapshot(snap)
    assert snap == original  # append never mutates its own argument


def test_no_future_data_survives_the_round_trip(tmp_path: Path) -> None:
    import dataclasses

    from ai_trader.context_memory.contracts import ContextSnapshot

    repo = _repo(tmp_path)
    record_id = repo.append_context_snapshot(make_snapshot())
    retrieved = repo.get_context_snapshot(record_id)
    assert retrieved is not None
    forbidden = {"realized_return", "future_price", "mfe", "mae", "win_loss_label", "trade_result"}
    assert {f.name for f in dataclasses.fields(ContextSnapshot)}.isdisjoint(forbidden)


# ------------------------------------------------------------------ concurrency


def test_concurrent_appends_within_one_process_are_serialized(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    snaps = [make_snapshot(as_of=AS_OF + i) for i in range(20)]

    def append_all() -> None:
        for s in snaps:
            repo.append_context_snapshot(s)

    threads = [threading.Thread(target=append_all) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # 4 threads each appending the SAME 20 snapshots -- idempotency + the lock must leave exactly 20
    # distinct records, never a race-induced duplicate or corrupted count.
    assert repo.count_context_snapshots() == 20


# ------------------------------------------------------------------ outcomes end-to-end


def test_outcome_append_and_read(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    obs_id = repo.append_observation(make_observation())
    outcome = make_pending_outcome(obs_id)
    record_id = repo.append_outcome(outcome)
    assert repo.get_outcome(record_id) == outcome
    assert repo.count_outcomes() == 1


def test_get_observation_and_iter_outcomes(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    obs = make_observation()
    obs_id = repo.append_observation(obs)
    assert repo.get_observation(obs_id) == obs

    outcome = make_pending_outcome(obs_id)
    repo.append_outcome(outcome)
    assert list(repo.iter_outcomes()) == [outcome]


def test_batch_append_observations_and_outcomes(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    observations = [make_observation(context_snapshot=make_snapshot(as_of=AS_OF + i)) for i in range(3)]
    obs_ids = repo.append_observations(observations)
    assert len(obs_ids) == 3
    assert [repo.get_observation(oid) for oid in obs_ids] == observations

    outcomes = [make_pending_outcome(obs_ids[0], strategy_id="S1"), make_pending_outcome(obs_ids[0], strategy_id="S2")]
    out_ids = repo.append_outcomes(outcomes)
    assert len(out_ids) == 2
    assert repo.count_outcomes() == 2


def test_root_path_property(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    assert repo.root_path == tmp_path / "repo"


def test_blank_lines_are_skipped_on_rebuild_and_verify(tmp_path: Path) -> None:
    path = tmp_path / "repo"
    repo = ContextMemoryRepository(path)
    repo.append_context_snapshot(make_snapshot())
    with (path / "context_snapshots.jsonl").open("a", encoding="utf-8") as f:
        f.write("\n")  # a trailing blank line -- must not be treated as a record at all
    reopened = ContextMemoryRepository(path)
    assert reopened.count_context_snapshots() == 1
    assert reopened.verify_integrity().ok


def test_malformed_envelope_missing_keys(tmp_path: Path) -> None:
    path = tmp_path / "repo"
    repo = ContextMemoryRepository(path)
    repo.append_context_snapshot(make_snapshot())
    with (path / "context_snapshots.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"record_id": "abc"}) + "\n")  # missing "sequence"/"payload"
    with pytest.raises(RepositoryCorruptionError, match="malformed envelope"):
        ContextMemoryRepository(path)


def test_undecodable_payload_wrapped_as_corruption(tmp_path: Path) -> None:
    path = tmp_path / "repo"
    repo = ContextMemoryRepository(path)
    repo.append_context_snapshot(make_snapshot())
    with (path / "context_snapshots.jsonl").open("a", encoding="utf-8") as f:
        # valid JSON envelope, but a payload missing required fields -> ContextMemoryValidationError,
        # not UnsupportedSchemaVersionError -- must be wrapped as RepositoryCorruptionError.
        bad_payload = {"record_type": "context_memory.context_snapshot", "context_memory_schema_version": {"namespace": "context_memory", "version": "v1"}}
        f.write(json.dumps({"record_id": "zzz", "sequence": 1, "payload": bad_payload}) + "\n")
    with pytest.raises(RepositoryCorruptionError, match="undecodable payload"):
        ContextMemoryRepository(path)


def test_verify_reports_tampered_payload_without_reopening(tmp_path: Path) -> None:
    path = tmp_path / "repo"
    repo = ContextMemoryRepository(path)
    repo.append_context_snapshot(make_snapshot())
    snapshot_file = path / "context_snapshots.jsonl"
    lines = snapshot_file.read_text(encoding="utf-8").splitlines()
    envelope = json.loads(lines[0])
    envelope["payload"]["instrument"] = "TAMPERED"
    snapshot_file.write_text(json.dumps(envelope) + "\n", encoding="utf-8")
    report = repo.verify_integrity()  # verify() itself, not a fresh reopen -- exercises _ingest_line_readonly's own ID-mismatch branch
    assert not report.ok


def test_write_failure_is_wrapped_as_repository_write_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _repo(tmp_path)

    def _boom(*args: object, **kwargs: object) -> None:
        raise OSError("disk full (simulated)")

    monkeypatch.setattr("os.fsync", _boom)
    with pytest.raises(RepositoryWriteError):
        repo.append_context_snapshot(make_snapshot())
