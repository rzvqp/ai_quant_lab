"""Mandate Section 26/29 (checkpoint.py wiring + rollback evidence) and final closure mandate item 3
(General Observer's own checkpoint cadence): `write_checkpoint()` remains callable with zero General
Observer data present (a fresh machine / S5-only history, exactly the pre-existing behavior) and
correctly reports General Observer counts once that data exists -- additive-only, S5's own counters
unaffected either way. `general_observer_checkpoint_due()`/`write_general_observer_checkpoint()`
track their own, separately-keyed cadence -- never S5's `RESOLVED_EPISODES_CSV`-based counter, never
S5's own runtime-state keys.
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
        "MISSED_MOVE_CLUSTERS_CSV", "LESSON_HYPOTHESES_JSON", "GENERAL_OBSERVER_PREDICTIONS_CSV",
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


# ---- General Observer's own checkpoint cadence (final closure mandate item 3) ---------------------

def _write_scorecard_rows(n: int) -> None:
    durable_store.ensure_dirs()
    is_new = not durable_store.SCORECARD_CSV.exists()
    with durable_store.SCORECARD_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["episode_id", "review_horizon"])
        if is_new:
            writer.writeheader()
        for i in range(n):
            writer.writerow({"episode_id": f"GO-{i}", "review_horizon": "H1"})


def test_general_observer_checkpoint_not_due_with_zero_scorecard_rows_and_no_prior_checkpoint(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    assert checkpoint.general_observer_checkpoint_due() is False


def test_general_observer_checkpoint_due_after_enough_scorecard_rows_with_zero_s5_resolved_episodes(tmp_path, monkeypatch):
    """No dependence on S5-specific counters (mandate item 3's own explicit requirement) -- due
    purely from SCORECARD_CSV growth, with RESOLVED_EPISODES_CSV never populated at all."""
    _isolate(tmp_path, monkeypatch)
    assert not durable_store.RESOLVED_EPISODES_CSV.exists()
    _write_scorecard_rows(checkpoint.GENERAL_OBSERVER_CHECKPOINT_EVERY_N_SCORECARD_ROWS)
    assert checkpoint.general_observer_checkpoint_due() is True
    assert not durable_store.RESOLVED_EPISODES_CSV.exists()  # still never touched


def test_write_general_observer_checkpoint_does_not_reset_s5_own_cadence_state(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    durable_store.ensure_dirs()
    s5_state = {"last_checkpoint_utc": "2020-01-01T00:00:00+00:00", "last_checkpoint_resolved_count": 42}
    durable_store.save_runtime_state(s5_state)

    checkpoint.write_general_observer_checkpoint()

    reloaded = durable_store.load_runtime_state()
    assert reloaded["last_checkpoint_utc"] == "2020-01-01T00:00:00+00:00"  # S5's own key untouched
    assert reloaded["last_checkpoint_resolved_count"] == 42
    assert "go_last_checkpoint_utc" in reloaded  # General Observer's own key was set
    assert reloaded["go_last_checkpoint_scorecard_count"] == 0


def test_write_checkpoint_s5_does_not_reset_general_observer_own_cadence_state(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    durable_store.ensure_dirs()
    go_state = {"go_last_checkpoint_utc": "2020-01-01T00:00:00+00:00", "go_last_checkpoint_scorecard_count": 7}
    durable_store.save_runtime_state(go_state)

    checkpoint.write_checkpoint()

    reloaded = durable_store.load_runtime_state()
    assert reloaded["go_last_checkpoint_utc"] == "2020-01-01T00:00:00+00:00"  # General Observer's own key untouched
    assert reloaded["go_last_checkpoint_scorecard_count"] == 7
    assert "last_checkpoint_utc" in reloaded  # S5's own key was set


def test_general_observer_checkpoint_countdown_resets_after_writing(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    _write_scorecard_rows(checkpoint.GENERAL_OBSERVER_CHECKPOINT_EVERY_N_SCORECARD_ROWS)
    assert checkpoint.general_observer_checkpoint_due() is True
    checkpoint.write_general_observer_checkpoint()
    assert checkpoint.general_observer_scorecard_count_since_last_checkpoint() == 0
    assert checkpoint.general_observer_checkpoint_due() is False  # just checkpointed -- not due again immediately


def test_general_observer_checkpoint_restart_safe(tmp_path, monkeypatch):
    """Restart-safety: cadence state lives in the durable runtime-state JSON file, not in-memory --
    re-reading it fresh (simulating a restart) reproduces the identical due/not-due verdict."""
    _isolate(tmp_path, monkeypatch)
    _write_scorecard_rows(checkpoint.GENERAL_OBSERVER_CHECKPOINT_EVERY_N_SCORECARD_ROWS)
    checkpoint.write_general_observer_checkpoint()
    verdict_a = checkpoint.general_observer_checkpoint_due()
    verdict_b = checkpoint.general_observer_checkpoint_due()  # fresh read, no cache
    assert verdict_a is False
    assert verdict_b is False
