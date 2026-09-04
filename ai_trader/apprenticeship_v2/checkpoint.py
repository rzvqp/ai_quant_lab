"""Section 30 -- durable checkpoints every 25 resolved independent episodes or one completed
calendar trading week, whichever occurs first. A checkpoint snapshots the live (gitignored) state
into `docs/trader_apprenticeship/apprenticeship_v2/` (git-tracked) so the CEO/other departments can
review progress without needing access to this machine's local runtime state -- mirrors the
completed Q4 replay's own git-checkpoint discipline exactly.

This module only READS the live CSV/JSON artifacts and WRITES a snapshot markdown + copies of the
CSVs into the checkpoint directory; it never mutates the live state itself. Committing the snapshot
to git is a separate, explicit step (this module does not call git)."""

from __future__ import annotations

import csv
import datetime
import json
import shutil

from ai_trader.apprenticeship_v2 import durable_store

CHECKPOINT_EVERY_N_RESOLVED = 25


def _count_rows(path) -> int:
    if not path.exists():
        return 0
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def resolved_count_since_last_checkpoint() -> int:
    state = durable_store.load_runtime_state()
    total_resolved = _count_rows(durable_store.RESOLVED_EPISODES_CSV)
    last_checkpoint_resolved_count = int(state.get("last_checkpoint_resolved_count", 0))
    return total_resolved - last_checkpoint_resolved_count


def checkpoint_due() -> bool:
    if resolved_count_since_last_checkpoint() >= CHECKPOINT_EVERY_N_RESOLVED:
        return True
    state = durable_store.load_runtime_state()
    last_checkpoint_utc = state.get("last_checkpoint_utc")
    if last_checkpoint_utc is None:
        return False  # no checkpoint has ever run yet -- the caller decides whether to force one at startup
    last = datetime.datetime.fromisoformat(last_checkpoint_utc)
    return (datetime.datetime.now(datetime.timezone.utc) - last) >= datetime.timedelta(days=7)


def write_checkpoint(*, note: str = "") -> str:
    """Returns the checkpoint markdown's own text (also written to WEEKLY_CHECKPOINT_MD, appended,
    and a timestamped copy of the raw CSVs is saved into the git-tracked checkpoint dir)."""
    durable_store.ensure_dirs()
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    total_episodes = _count_rows(durable_store.LIVE_EPISODE_LEDGER_CSV)
    total_predictions = _count_rows(durable_store.PROSPECTIVE_PREDICTIONS_CSV)
    total_resolved = _count_rows(durable_store.RESOLVED_EPISODES_CSV)
    total_shadow = _count_rows(durable_store.SHADOW_TAKE_SKIP_CSV)

    by_expectation: dict[str, int] = {}
    if durable_store.PROSPECTIVE_PREDICTIONS_CSV.exists():
        with durable_store.PROSPECTIVE_PREDICTIONS_CSV.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                key = row.get("ai_trader_expectation") or "UNSET"
                by_expectation[key] = by_expectation.get(key, 0) + 1

    lines = [
        f"## Checkpoint {now_iso}", "",
        f"- TOTAL_EPISODES_IN_LEDGER = {total_episodes}",
        f"- TOTAL_FROZEN_PREDICTIONS = {total_predictions}",
        f"- TOTAL_RESOLVED_EPISODES = {total_resolved}",
        f"- TOTAL_SHADOW_TAKE_SKIP_RECORDS = {total_shadow}",
        f"- PREDICTIONS_BY_EXPECTATION = {json.dumps(by_expectation)}",
    ]

    # General Observer V1.1 additions -- additive only: these files may not exist at all (the
    # subsystem may never have run on this machine), in which case _count_rows returns 0 and this
    # section simply reports zeros, exactly like every S5 counter above already does before its own
    # first episode.
    total_general_episodes = _count_rows(durable_store.GENERAL_OBSERVER_LEDGER_CSV)
    total_scorecard_rows = _count_rows(durable_store.SCORECARD_CSV)
    total_missed_move_clusters = _count_rows(durable_store.MISSED_MOVE_CLUSTERS_CSV)
    lines += [
        f"- TOTAL_GENERAL_OBSERVER_EPISODES = {total_general_episodes}",
        f"- TOTAL_SCORECARD_ROWS = {total_scorecard_rows}",
        f"- TOTAL_MISSED_MOVE_CLUSTERS = {total_missed_move_clusters}",
    ]

    if note:
        lines.append(f"- NOTE: {note}")
    lines.append("")
    text = "\n".join(lines)

    with durable_store.WEEKLY_CHECKPOINT_MD.open("a", encoding="utf-8") as f:
        f.write(text + "\n---\n\n")

    # Snapshot the raw CSVs into the git-tracked checkpoint dir, timestamped, for durable review.
    snap_dir = durable_store.CHECKPOINT_DIR / f"snapshot_{now_iso.replace(':', '').replace('+00:00', 'Z')}"
    snap_dir.mkdir(parents=True, exist_ok=True)
    for src in (
        durable_store.LIVE_EPISODE_LEDGER_CSV, durable_store.PROSPECTIVE_PREDICTIONS_CSV,
        durable_store.RESOLVED_EPISODES_CSV, durable_store.SHADOW_TAKE_SKIP_CSV,
        durable_store.GENERAL_OBSERVER_LEDGER_CSV, durable_store.SCORECARD_CSV,
        durable_store.MISSED_MOVE_CLUSTERS_CSV, durable_store.LESSON_HYPOTHESES_JSON,
    ):
        if src.exists():
            shutil.copy2(src, snap_dir / src.name)
    (snap_dir / "CHECKPOINT_SUMMARY.md").write_text(text, encoding="utf-8")

    state = durable_store.load_runtime_state()
    state["last_checkpoint_utc"] = now_iso
    state["last_checkpoint_resolved_count"] = total_resolved
    durable_store.save_runtime_state(state)

    return text
