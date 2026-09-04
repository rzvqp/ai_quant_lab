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

# ---- General Observer V1.1 additions (design doc Sections 7/9/10/13a) ---------------------------
#
# GENERAL_OBSERVER_LEDGER_CSV is a SEPARATE file from LIVE_EPISODE_LEDGER_CSV, not a widened version
# of it -- LIVE_EPISODE_LEDGER_CSV already has 2 real rows in production with a 10-column header;
# `csv.DictWriter` in append ("a") mode never rewrites an existing header (see `_append_csv_row`
# below), so appending a wider row to that file would silently produce a structurally inconsistent
# CSV (a short header, long data rows) -- a real risk to the live S5 file, not a hypothetical one.
# A dedicated file with its own, wider field set carries zero risk to the existing one.
#
# `read_pending_episodes()`/`read_open_episode_ids_without_resolution()`/`read_episode_row()` are
# extended (additively, see below) to ALSO scan this file, so the mandate's own instruction to reuse
# `read_pending_episodes()` for the general-observer BEFORE-review queue is honored in substance --
# one unified pending-review view spanning both ledgers -- without ever touching the live file's
# own structure.
GENERAL_OBSERVER_LEDGER_CSV = LIVE_STATE_DIR / "AI_TRADER_GENERAL_OBSERVER_LEDGER.csv"
SCORECARD_CSV = LIVE_STATE_DIR / "AI_TRADER_SCORECARD.csv"
MISSED_MOVE_CLUSTERS_CSV = LIVE_STATE_DIR / "AI_TRADER_MISSED_MOVE_CLUSTERS.csv"
LESSON_HYPOTHESES_JSON = LIVE_STATE_DIR / "AI_TRADER_LESSON_HYPOTHESES.json"

_LEDGER_FIELDS = [
    "episode_id", "timestamp_utc", "frozen_at_bar_ts", "episode_type", "symbol", "current_price",
    "setup_direction", "reference_levels_json", "snapshot_json", "qualitative_review_status",
]
_GENERAL_LEDGER_FIELDS = _LEDGER_FIELDS + [
    "trigger_timeframe", "what_triggered_observation", "directional_hypothesis", "what_to_watch_next",
    "frozen_snapshot_hash", "prospective_eligibility", "underlying_move_id",
]
_SCORECARD_FIELDS = [
    "episode_id", "review_horizon", "original_expectation", "original_confidence",
    "mechanical_outcome_summary", "expectation_correct", "partial_reason", "scored_at_utc",
    "after_market_interpretation", "lesson_candidate_effect",
]
_MISSED_MOVE_CLUSTER_FIELDS = [
    "cluster_id", "record_class", "direction", "canonical_window_start_ts", "canonical_window_end_ts",
    "canonical_magnitude", "canonical_atr_reference", "canonical_normalized_magnitude",
    "qualifying_window_count", "cluster_terminated_at_ts",
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


def append_general_episode_to_ledger(episode: "schemas.EpisodeRecord") -> None:  # type: ignore[name-defined]
    """General-observer equivalent of `append_episode_to_ledger` -- writes to
    `GENERAL_OBSERVER_LEDGER_CSV`, never `LIVE_EPISODE_LEDGER_CSV` (S5 isolation). `setup_direction`
    is deliberately never populated by general-observer callers (stays `None`/""` -- that field is
    S5's own, per the design doc's explicit isolation requirement); direction lives in
    `directional_hypothesis` instead."""
    from ai_trader.apprenticeship_v2 import schemas

    assert isinstance(episode, schemas.EpisodeRecord)
    row = {
        "episode_id": episode.episode_id, "timestamp_utc": episode.timestamp_utc,
        "frozen_at_bar_ts": episode.frozen_at_bar_ts, "episode_type": episode.episode_type,
        "symbol": episode.symbol, "current_price": episode.current_price,
        "setup_direction": episode.setup_direction or "",
        "reference_levels_json": json.dumps(episode.reference_levels),
        "snapshot_json": json.dumps(episode.snapshot), "qualitative_review_status": episode.qualitative_review_status,
        "trigger_timeframe": episode.trigger_timeframe or "",
        "what_triggered_observation": episode.what_triggered_observation or "",
        "directional_hypothesis": episode.directional_hypothesis or "",
        "what_to_watch_next": episode.what_to_watch_next or "",
        "frozen_snapshot_hash": episode.frozen_snapshot_hash or "",
        "prospective_eligibility": episode.prospective_eligibility or "",
        "underlying_move_id": episode.underlying_move_id or "",
    }
    _append_csv_row(GENERAL_OBSERVER_LEDGER_CSV, _GENERAL_LEDGER_FIELDS, row)


def append_scorecard(entry: "schemas.ScorecardEntry") -> None:  # type: ignore[name-defined]
    """Section 9/16 -- append-only, one row per `(episode_id, review_horizon)`. Never overwrites an
    existing row; callers (the incremental horizon scorer) are responsible for not re-scoring an
    already-scored `(episode_id, review_horizon)` pair -- see
    `general_observer.scorecard.already_scored()`."""
    from ai_trader.apprenticeship_v2 import schemas

    assert isinstance(entry, schemas.ScorecardEntry)
    row = {
        "episode_id": entry.episode_id, "review_horizon": entry.review_horizon,
        "original_expectation": entry.original_expectation, "original_confidence": entry.original_confidence,
        "mechanical_outcome_summary": entry.mechanical_outcome_summary,
        "expectation_correct": entry.expectation_correct, "partial_reason": entry.partial_reason or "",
        "scored_at_utc": entry.scored_at_utc,
        "after_market_interpretation": entry.after_market_interpretation or "",
        "lesson_candidate_effect": entry.lesson_candidate_effect or "",
    }
    _append_csv_row(SCORECARD_CSV, _SCORECARD_FIELDS, row)


def read_scorecard_rows(episode_id: str | None = None) -> list[dict[str, Any]]:
    """All scorecard rows, optionally filtered to one episode. Reads fresh every call -- never
    cached, matching every other reader in this module."""
    if not SCORECARD_CSV.exists():
        return []
    rows = []
    with SCORECARD_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if episode_id is None or row.get("episode_id") == episode_id:
                rows.append(row)
    return rows


def append_missed_move_cluster(cluster: "schemas.RetrospectiveMissedMoveCluster") -> None:  # type: ignore[name-defined]
    """Section 10 -- written EXACTLY ONCE per cluster, at termination (never while a cluster is
    still active/accumulating continuations -- the active cluster's own in-progress state lives in
    runtime state, see `load_active_missed_move_cluster`/`save_active_missed_move_cluster` below,
    not in this append-only ledger)."""
    from ai_trader.apprenticeship_v2 import schemas

    assert isinstance(cluster, schemas.RetrospectiveMissedMoveCluster)
    row = {
        "cluster_id": cluster.cluster_id, "record_class": cluster.record_class, "direction": cluster.direction,
        "canonical_window_start_ts": cluster.canonical_window_start_ts,
        "canonical_window_end_ts": cluster.canonical_window_end_ts,
        "canonical_magnitude": cluster.canonical_magnitude, "canonical_atr_reference": cluster.canonical_atr_reference,
        "canonical_normalized_magnitude": cluster.canonical_normalized_magnitude,
        "qualifying_window_count": cluster.qualifying_window_count,
        "cluster_terminated_at_ts": cluster.cluster_terminated_at_ts if cluster.cluster_terminated_at_ts is not None else "",
    }
    _append_csv_row(MISSED_MOVE_CLUSTERS_CSV, _MISSED_MOVE_CLUSTER_FIELDS, row)


def read_missed_move_clusters() -> list[dict[str, Any]]:
    if not MISSED_MOVE_CLUSTERS_CSV.exists():
        return []
    with MISSED_MOVE_CLUSTERS_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_lesson_hypotheses() -> list[dict[str, Any]]:
    """Section 13a. Unlike the append-only CSVs, this is a small JSON list -- lesson hypotheses are
    few, and `lesson_status` legitimately changes over a hypothesis's life (recomputed, not
    appended-to), matching `load_runtime_state`/`save_runtime_state`'s own read-modify-write
    convention rather than the CSV append pattern used everywhere else in this module."""
    if not LESSON_HYPOTHESES_JSON.exists():
        return []
    return json.loads(LESSON_HYPOTHESES_JSON.read_text(encoding="utf-8"))


def save_lesson_hypotheses(hypotheses: list[dict[str, Any]]) -> None:
    ensure_dirs()
    LESSON_HYPOTHESES_JSON.write_text(json.dumps(hypotheses, indent=2), encoding="utf-8")


def append_resolved_episode(resolved: "schemas.ResolvedEpisode") -> None:  # type: ignore[name-defined]
    row = {
        "episode_id": resolved.episode_id, "resolved_at_utc": resolved.resolved_at_utc,
        "atr_at_episode_start": resolved.atr_at_episode_start, "horizons_json": json.dumps(resolved.horizons),
        "structural_resolution_json": json.dumps(resolved.structural_resolution),
    }
    _append_csv_row(RESOLVED_EPISODES_CSV, _RESOLVED_FIELDS, row)


def append_shadow_take_skip(row: dict[str, Any]) -> None:
    _append_csv_row(SHADOW_TAKE_SKIP_CSV, _SHADOW_FIELDS, row)


def _read_all_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_pending_episodes() -> list[dict[str, Any]]:
    """Episodes in EITHER ledger not yet transitioned to FROZEN (i.e. still awaiting a qualitative-
    review pass). Reads both files fresh every call -- never cached. Extended (additively) to also
    scan `GENERAL_OBSERVER_LEDGER_CSV` so this one function remains the single BEFORE-review queue
    surface for both S5 and general-observer episodes, per the design doc's own instruction to reuse
    it -- `LIVE_EPISODE_LEDGER_CSV`'s own read logic is unchanged, only unioned with a second source."""
    pending = [
        row for row in _read_all_rows(LIVE_EPISODE_LEDGER_CSV)
        if row.get("qualitative_review_status") == "PENDING_LLM_REVIEW"
    ]
    pending += [
        row for row in _read_all_rows(GENERAL_OBSERVER_LEDGER_CSV)
        if row.get("qualitative_review_status") == "PENDING_LLM_REVIEW"
    ]
    return pending


def read_open_episode_ids_without_resolution() -> set[str]:
    """Episode IDs present in either ledger but absent from the resolved-episodes file -- these are
    the episodes the resolution scorer must keep checking on future ticks. Extended (additively) to
    include `GENERAL_OBSERVER_LEDGER_CSV` alongside the original `LIVE_EPISODE_LEDGER_CSV`."""
    all_ids: set[str] = {row["episode_id"] for row in _read_all_rows(LIVE_EPISODE_LEDGER_CSV)}
    all_ids |= {row["episode_id"] for row in _read_all_rows(GENERAL_OBSERVER_LEDGER_CSV)}
    resolved_ids: set[str] = {row["episode_id"] for row in _read_all_rows(RESOLVED_EPISODES_CSV)}
    return all_ids - resolved_ids


def read_episode_row(episode_id: str) -> dict[str, Any] | None:
    """Checks `LIVE_EPISODE_LEDGER_CSV` first (unchanged lookup order/behavior for any existing S5
    caller), then `GENERAL_OBSERVER_LEDGER_CSV` if not found there."""
    for row in _read_all_rows(LIVE_EPISODE_LEDGER_CSV):
        if row["episode_id"] == episode_id:
            return row
    for row in _read_all_rows(GENERAL_OBSERVER_LEDGER_CSV):
        if row["episode_id"] == episode_id:
            return row
    return None


def read_all_general_episode_rows() -> list[dict[str, Any]]:
    """General-observer-only reader (never includes S5 rows) -- used by dedup/underlying-move-id/
    lesson-voting/missed-move-coverage code, all of which only ever need to reason about the 4
    general-observer classes, never S5_OCCURRENCE rows."""
    return _read_all_rows(GENERAL_OBSERVER_LEDGER_CSV)


def load_runtime_state() -> dict[str, Any]:
    if not RUNTIME_STATE_JSON.exists():
        return {}
    return json.loads(RUNTIME_STATE_JSON.read_text(encoding="utf-8"))


def save_runtime_state(state: dict[str, Any]) -> None:
    ensure_dirs()
    RUNTIME_STATE_JSON.write_text(json.dumps(state, indent=2), encoding="utf-8")
