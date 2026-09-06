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


def _write_checkpoint_snapshot(*, note: str) -> tuple[str, int, str]:
    """Builds the checkpoint markdown text, appends it to `WEEKLY_CHECKPOINT_MD`, and copies the raw
    artifacts into a timestamped, git-tracked snapshot directory. Shared by `write_checkpoint()` (S5)
    and `write_general_observer_checkpoint()` (General Observer, final closure mandate item 3) -- one
    set of live artifacts, two independent callers -- neither of which mutates the OTHER's own
    cadence-tracking runtime-state keys; that update happens separately in each caller. Returns
    `(text, total_resolved, now_iso)` -- `total_resolved` is still needed by `write_checkpoint()`'s
    own S5 cadence-state update; `now_iso` is the SAME timestamp already embedded in `text`'s own
    header, so callers record an identical timestamp in runtime state rather than a microseconds-
    later, separately-computed one."""
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
        durable_store.GENERAL_OBSERVER_PREDICTIONS_CSV,
    ):
        if src.exists():
            shutil.copy2(src, snap_dir / src.name)
    (snap_dir / "CHECKPOINT_SUMMARY.md").write_text(text, encoding="utf-8")

    return text, total_resolved, now_iso


def write_checkpoint(*, note: str = "") -> str:
    """Returns the checkpoint markdown's own text (also written to WEEKLY_CHECKPOINT_MD, appended,
    and a timestamped copy of the raw CSVs is saved into the git-tracked checkpoint dir). Updates
    S5's own cadence-tracking keys (`last_checkpoint_utc`/`last_checkpoint_resolved_count`) only --
    never General Observer's own `go_*` keys."""
    text, total_resolved, now_iso = _write_checkpoint_snapshot(note=note)
    state = durable_store.load_runtime_state()
    state["last_checkpoint_utc"] = now_iso
    state["last_checkpoint_resolved_count"] = total_resolved
    durable_store.save_runtime_state(state)
    return text


# ---- General Observer's own checkpoint cadence (final closure mandate item 3) ---------------------
#
# `checkpoint_due()`/`write_checkpoint()` above are S5's own: their cadence counts
# `RESOLVED_EPISODES_CSV` rows and tracks `last_checkpoint_utc`/`last_checkpoint_resolved_count` in
# the SHARED `AI_TRADER_RUNTIME_STATE.json`. Wiring THOSE functions into `main_general_observer.py`
# would (a) never actually trigger for a general-observer-only deployment (S5's own resolved-episode
# counter would stay at 0 forever), and (b) risk a genuine cross-process race if S5's own entrypoint
# is ever also wired to call them concurrently -- two processes read-modify-writing the SAME state
# keys. Both problems are avoided by giving General Observer its own, separately-keyed cadence,
# reusing the exact same "N completed units of work, or one week, whichever first" governance
# pattern (Section 30) with its own unit of work (`SCORECARD_CSV` rows -- a scored horizon is the
# closest general-observer analog to S5's own "resolved episode") and its own runtime-state keys
# (`go_last_checkpoint_utc`/`go_last_checkpoint_scorecard_count`, disjoint from S5's own
# `last_checkpoint_utc`/`last_checkpoint_resolved_count` -- no shared key, no race).

GENERAL_OBSERVER_CHECKPOINT_EVERY_N_SCORECARD_ROWS = 25


def general_observer_scorecard_count_since_last_checkpoint() -> int:
    state = durable_store.load_runtime_state()
    total_scorecard_rows = _count_rows(durable_store.SCORECARD_CSV)
    last = int(state.get("go_last_checkpoint_scorecard_count", 0))
    return total_scorecard_rows - last


def general_observer_checkpoint_due() -> bool:
    if general_observer_scorecard_count_since_last_checkpoint() >= GENERAL_OBSERVER_CHECKPOINT_EVERY_N_SCORECARD_ROWS:
        return True
    state = durable_store.load_runtime_state()
    last_checkpoint_utc = state.get("go_last_checkpoint_utc")
    if last_checkpoint_utc is None:
        return False  # no checkpoint has ever run yet -- the caller decides whether to force one at startup
    last = datetime.datetime.fromisoformat(last_checkpoint_utc)
    return (datetime.datetime.now(datetime.timezone.utc) - last) >= datetime.timedelta(days=7)


def write_general_observer_checkpoint(*, note: str = "") -> str:
    """General Observer's own checkpoint write -- same snapshot content and file set as
    `write_checkpoint()` (there is only one set of live artifacts to snapshot; both S5's and General
    Observer's own checkpoint triggers are simply two independent CALLERS of the same underlying
    snapshot), but tracks its OWN cadence state (`go_last_checkpoint_utc`/
    `go_last_checkpoint_scorecard_count`), never S5's own keys -- so calling this never resets S5's
    own checkpoint countdown, and vice versa."""
    text, _total_resolved, now_iso = _write_checkpoint_snapshot(note=note or "general_observer periodic checkpoint")
    state = durable_store.load_runtime_state()
    state["go_last_checkpoint_utc"] = now_iso
    state["go_last_checkpoint_scorecard_count"] = _count_rows(durable_store.SCORECARD_CSV)
    durable_store.save_runtime_state(state)
    return text
