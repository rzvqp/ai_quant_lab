"""Mandate Section 26/29 (checkpoint.py wiring + rollback evidence): `write_checkpoint()` remains
callable with zero General Observer data present (a fresh machine / S5-only history, exactly the
pre-existing behavior) and correctly reports General Observer counts once that data exists --
additive-only, S5's own counters unaffected either way.
"""

from __future__ import annotations

import csv

from ai_trader.apprenticeship_v2 import checkpoint, durable_store


def _isolate(tmp_path, monkeypatch):
    live_dir = tmp_path / "live_state"
    checkpoint_dir = tmp_path / "checkpoint"
    monkeypatch.setattr(durable_store, "LIVE_STATE_DIR", live_dir)
    monkeypatch.setattr(durable_store, "CHECKPOINT_DIR", checkpoint_dir)
    for name in (
        "START_JSON", "RUNTIME_STATE_JSON", "LIVE_EPISODE_LEDGER_CSV", "PROSPECTIVE_PREDICTIONS_CSV",
        "RESOLVED_EPISODES_CSV", "SHADOW_TAKE_SKIP_CSV", "LESSON_REGISTER_MD", "RESEARCH_HANDOFFS_MD",
        "WEEKLY_CHECKPOINT_MD", "GENERAL_OBSERVER_LEDGER_CSV", "SCORECARD_CSV",
        "MISSED_MOVE_CLUSTERS_CSV", "LESSON_HYPOTHESES_JSON",
    ):
        monkeypatch.setattr(durable_store, name, live_dir / f"{name}.tmp")
    return live_dir, checkpoint_dir


def test_write_checkpoint_works_with_zero_general_observer_data(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    text = checkpoint.write_checkpoint(note="test, no data at all")
    assert "TOTAL_EPISODES_IN_LEDGER = 0" in text
    assert "TOTAL_GENERAL_OBSERVER_EPISODES = 0" in text
    assert "TOTAL_SCORECARD_ROWS = 0" in text
    assert "TOTAL_MISSED_MOVE_CLUSTERS = 0" in text


def test_write_checkpoint_counts_general_observer_rows_when_present(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    durable_store.ensure_dirs()
    with durable_store.GENERAL_OBSERVER_LEDGER_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["episode_id"])
        writer.writeheader()
        writer.writerow({"episode_id": "GO-1"})
        writer.writerow({"episode_id": "GO-2"})

    text = checkpoint.write_checkpoint()
    assert "TOTAL_GENERAL_OBSERVER_EPISODES = 2" in text


def test_write_checkpoint_snapshots_general_observer_files_into_checkpoint_dir(tmp_path, monkeypatch):
    live_dir, checkpoint_dir = _isolate(tmp_path, monkeypatch)
    durable_store.ensure_dirs()
    durable_store.GENERAL_OBSERVER_LEDGER_CSV.write_text("episode_id\nGO-1\n", encoding="utf-8")

    checkpoint.write_checkpoint()
    snapshot_dirs = list(checkpoint_dir.glob("snapshot_*"))
    assert len(snapshot_dirs) == 1
    assert (snapshot_dirs[0] / durable_store.GENERAL_OBSERVER_LEDGER_CSV.name).exists()
