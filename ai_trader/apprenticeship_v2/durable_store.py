"""Append-only durable artifacts (mandate Section 40, exact filenames). Frequent-write files
(episode ledger, predictions, resolved episodes, shadow take/skip, runtime state) live under
`new_brain_live_state/apprenticeship_v2/` -- this repo's own established convention for
frequently-changing, machine-local live-runtime state (gitignored: see `.gitignore` line 45), so a
15-minute tick never creates git noise. Periodic snapshots are checkpointed into
`docs/trader_apprenticeship/apprenticeship_v2/` (git-tracked) at the cadence Section 30 specifies --
handled by `checkpoint.py`, not this module.

CSV files with nested data (a snapshot, a horizon-metrics dict) carry that data as a single
JSON-encoded column rather than flattening it lossily -- still genuinely `.csv`, one row per
episode, append-only, human-openable in a spreadsheet, full fidelity preserved."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_STATE_DIR = REPO_ROOT / "new_brain_live_state" / "apprenticeship_v2"
CHECKPOINT_DIR = REPO_ROOT / "docs" / "trader_apprenticeship" / "apprenticeship_v2"

START_JSON = LIVE_STATE_DIR / "AI_TRADER_APPRENTICESHIP_V2_START.json"
RUNTIME_STATE_JSON = LIVE_STATE_DIR / "AI_TRADER_RUNTIME_STATE.json"
LIVE_EPISODE_LEDGER_CSV = LIVE_STATE_DIR / "AI_TRADER_LIVE_EPISODE_LEDGER.csv"
PROSPECTIVE_PREDICTIONS_CSV = LIVE_STATE_DIR / "AI_TRADER_PROSPECTIVE_PREDICTIONS.csv"
RESOLVED_EPISODES_CSV = LIVE_STATE_DIR / "AI_TRADER_RESOLVED_EPISODES.csv"
SHADOW_TAKE_SKIP_CSV = LIVE_STATE_DIR / "AI_TRADER_SHADOW_TAKE_SKIP.csv"
LESSON_REGISTER_MD = LIVE_STATE_DIR / "AI_TRADER_LESSON_REGISTER.md"
RESEARCH_HANDOFFS_MD = LIVE_STATE_DIR / "AI_TRADER_RESEARCH_HANDOFFS.md"
WEEKLY_CHECKPOINT_MD = LIVE_STATE_DIR / "AI_TRADER_WEEKLY_CHECKPOINT.md"

_LEDGER_FIELDS = [
    "episode_id", "timestamp_utc", "frozen_at_bar_ts", "episode_type", "symbol", "current_price",
    "setup_direction", "reference_levels_json", "snapshot_json", "qualitative_review_status",
]
_PREDICTIONS_FIELDS = [
    "episode_id", "reviewed_at_utc", "ai_trader_expectation", "confidence", "shadow_decision",
    "expected_failure_mode", "expected_confirmation_behavior", "expected_invalidation_behavior",
    "supporting_evidence", "conflicting_evidence", "full_record_json",
]
_RESOLVED_FIELDS = [
    "episode_id", "resolved_at_utc", "atr_at_episode_start", "horizons_json", "structural_resolution_json",
]
_SHADOW_FIELDS = [
    "episode_id", "timestamp_utc", "shadow_decision", "expectation_correct", "if_take_outcome_summary",
    "if_skip_was_correct", "winner_skipped", "loser_avoided",
]


def ensure_dirs() -> None:
    LIVE_STATE_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)


def _append_csv_row(path: Path, fieldnames: list[str], row: dict[str, Any]) -> None:
    ensure_dirs()
    is_new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if is_new:
            writer.writeheader()
        writer.writerow(row)


def append_episode_to_ledger(episode: "schemas.EpisodeRecord") -> None:  # type: ignore[name-defined]
    from ai_trader.apprenticeship_v2 import schemas

    assert isinstance(episode, schemas.EpisodeRecord)
    row = {
        "episode_id": episode.episode_id, "timestamp_utc": episode.timestamp_utc,
        "frozen_at_bar_ts": episode.frozen_at_bar_ts, "episode_type": episode.episode_type,
        "symbol": episode.symbol, "current_price": episode.current_price,
        "setup_direction": episode.setup_direction or "",
        "reference_levels_json": json.dumps(episode.reference_levels),
        "snapshot_json": json.dumps(episode.snapshot), "qualitative_review_status": episode.qualitative_review_status,
    }
    _append_csv_row(LIVE_EPISODE_LEDGER_CSV, _LEDGER_FIELDS, row)


def append_prediction(episode: "schemas.EpisodeRecord") -> None:  # type: ignore[name-defined]
    """Called once, at the moment a qualitative-review pass completes an episode (transitions it to
    FROZEN) -- never overwritten afterward (Section 16: never change prediction wording after
    resolution)."""
    row = {
        "episode_id": episode.episode_id, "reviewed_at_utc": episode.reviewed_at_utc,
        "ai_trader_expectation": episode.ai_trader_expectation, "confidence": episode.confidence,
        "shadow_decision": episode.shadow_decision, "expected_failure_mode": episode.expected_failure_mode,
        "expected_confirmation_behavior": episode.expected_confirmation_behavior,
        "expected_invalidation_behavior": episode.expected_invalidation_behavior,
        "supporting_evidence": episode.supporting_evidence, "conflicting_evidence": episode.conflicting_evidence,
        "full_record_json": json.dumps(episode.to_json_dict()),
    }
    _append_csv_row(PROSPECTIVE_PREDICTIONS_CSV, _PREDICTIONS_FIELDS, row)


def append_resolved_episode(resolved: "schemas.ResolvedEpisode") -> None:  # type: ignore[name-defined]
    row = {
        "episode_id": resolved.episode_id, "resolved_at_utc": resolved.resolved_at_utc,
        "atr_at_episode_start": resolved.atr_at_episode_start, "horizons_json": json.dumps(resolved.horizons),
        "structural_resolution_json": json.dumps(resolved.structural_resolution),
    }
    _append_csv_row(RESOLVED_EPISODES_CSV, _RESOLVED_FIELDS, row)


def append_shadow_take_skip(row: dict[str, Any]) -> None:
    _append_csv_row(SHADOW_TAKE_SKIP_CSV, _SHADOW_FIELDS, row)


def read_pending_episodes() -> list[dict[str, Any]]:
    """Episodes in the ledger not yet transitioned to FROZEN (i.e. still awaiting a qualitative-
    review pass). Reads the ledger fresh every call -- never cached."""
    if not LIVE_EPISODE_LEDGER_CSV.exists():
        return []
    pending = []
    with LIVE_EPISODE_LEDGER_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("qualitative_review_status") == "PENDING_LLM_REVIEW":
                pending.append(row)
    return pending


def read_open_episode_ids_without_resolution() -> set[str]:
    """Episode IDs present in the ledger but absent from the resolved-episodes file -- these are
    the episodes the resolution scorer must keep checking on future ticks."""
    if not LIVE_EPISODE_LEDGER_CSV.exists():
        return set()
    all_ids: set[str] = set()
    with LIVE_EPISODE_LEDGER_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            all_ids.add(row["episode_id"])
    resolved_ids: set[str] = set()
    if RESOLVED_EPISODES_CSV.exists():
        with RESOLVED_EPISODES_CSV.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                resolved_ids.add(row["episode_id"])
    return all_ids - resolved_ids


def read_episode_row(episode_id: str) -> dict[str, Any] | None:
    if not LIVE_EPISODE_LEDGER_CSV.exists():
        return None
    with LIVE_EPISODE_LEDGER_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["episode_id"] == episode_id:
                return row
    return None


def load_runtime_state() -> dict[str, Any]:
    if not RUNTIME_STATE_JSON.exists():
        return {}
    return json.loads(RUNTIME_STATE_JSON.read_text(encoding="utf-8"))


def save_runtime_state(state: dict[str, Any]) -> None:
    ensure_dirs()
    RUNTIME_STATE_JSON.write_text(json.dumps(state, indent=2), encoding="utf-8")
