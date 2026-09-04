"""Retrospective missed-move audit (design doc Section 10, CEO-locked third/fourth addenda) --
`RETROSPECTIVELY_IDENTIFIED_MISSED_EVENT` / `RETROSPECTIVE_MISSED_MOVE_CLUSTER`. Structurally distinct
from `EpisodeRecord` (Section 22): never carries BEFORE-shaped fields, prospective confidence, or a
`directional_hypothesis` field name -- enforced by `RetrospectiveMissedMoveCluster` simply not having
those fields, not by a shared-shape runtime check. Never counts toward lesson evidence
(`RETROSPECTIVE_MISSED_EVENT_CAN_INCREMENT_LESSON_SUPPORT = NO`, Section 10) -- this module has no
code path that writes into `lesson_voting.py`'s inputs at all.

This is a genuinely SEPARATE audit from the general-observer trigger pipeline (`episode_builder.py`):
H1 timeframe, not M15; a rolling 4-bar/1-bar-step window, not a per-bar trigger; evaluated identically
for every H1 close regardless of whether an episode already exists there. Nothing here creates an
`EpisodeRecord`, ever.
"""

from __future__ import annotations

import dataclasses
import hashlib
from typing import TYPE_CHECKING

from ai_trader.apprenticeship_v2.general_observer.primitives import atr14
from ai_trader.apprenticeship_v2.schemas import GENERAL_OBSERVER_EVENT_TYPES, RetrospectiveMissedMoveCluster

if TYPE_CHECKING:
    from ai_trader.apprenticeship_v2.mt5_read_only_source import ReadOnlyBar

MISSED_MOVE_AUDIT_WINDOW_H1_BARS = 4  # CEO-locked, Section 10 third addendum
MISSED_MOVE_ATR_MULTIPLIER = 2.0  # CEO-locked
MISSED_MOVE_PRECEDING_COVERAGE_LOOKBACK_SECONDS = 3600  # 1 H1 bar, CEO-locked fourth addendum
H1_SECONDS = 3600


@dataclasses.dataclass(frozen=True, slots=True)
class AuditCandidateResult:
    window_start_ts: int  # H1.close_timestamp[t-4]
    window_end_ts: int  # H1.close_timestamp[t]
    status: str  # "MATERIAL" | "NOT_MATERIAL" | "UNSCORABLE_ATR_UNAVAILABLE"
    direction: str | None  # "BULLISH" | "BEARISH" -- set only when status == "MATERIAL"
    magnitude: float | None
    atr_reference: float | None  # ATR14_H1[t-4], fixed at the window's start


def audit_candidate(h1_bars: "list[ReadOnlyBar]", t_index: int) -> AuditCandidateResult | None:
    """One `AUDIT_CANDIDATE[t]` (Section 10). `h1_bars` must be causal H1 bars in ascending order;
    `t_index` is the (0-based) index of H1 bar `t`, the window's end. Returns `None` if `t_index < 4`
    (no `close[t-4]` exists yet) -- not a valid candidate at all, distinct from `UNSCORABLE_ATR_
    UNAVAILABLE`, which requires a real window whose ATR reference just isn't computable yet."""
    if t_index < 4 or t_index >= len(h1_bars):
        return None
    start_bar = h1_bars[t_index - MISSED_MOVE_AUDIT_WINDOW_H1_BARS]
    end_bar = h1_bars[t_index]
    magnitude = abs(end_bar.close - start_bar.close)
    # ATR14_H1[t-4]: causal AS OF the window START only -- computed on H1 bars up to and including
    # bar (t-4), never re-computed using bars inside the four-hour interval (Section 10, verbatim).
    atr_ref = atr14(h1_bars[: t_index - MISSED_MOVE_AUDIT_WINDOW_H1_BARS + 1])
    if atr_ref is None:
        return AuditCandidateResult(
            window_start_ts=start_bar.ts_close, window_end_ts=end_bar.ts_close,
            status="UNSCORABLE_ATR_UNAVAILABLE", direction=None, magnitude=magnitude, atr_reference=None,
        )
    if magnitude < MISSED_MOVE_ATR_MULTIPLIER * atr_ref:  # exact equality qualifies as material
        return AuditCandidateResult(
            window_start_ts=start_bar.ts_close, window_end_ts=end_bar.ts_close,
            status="NOT_MATERIAL", direction=None, magnitude=magnitude, atr_reference=atr_ref,
        )
    direction = "BULLISH" if end_bar.close > start_bar.close else "BEARISH"
    return AuditCandidateResult(
        window_start_ts=start_bar.ts_close, window_end_ts=end_bar.ts_close,
        status="MATERIAL", direction=direction, magnitude=magnitude, atr_reference=atr_ref,
    )


def coverage_window(candidate: AuditCandidateResult) -> tuple[int, int]:
    """Both boundaries inclusive (Section 10) -- `coverage_window_start = window_start_ts - 1h`,
    `coverage_window_end = window_end_ts`."""
    return candidate.window_start_ts - MISSED_MOVE_PRECEDING_COVERAGE_LOOKBACK_SECONDS, candidate.window_end_ts


def is_covered(candidate: AuditCandidateResult, general_episode_rows: list[dict]) -> bool:
    """Section 10's four-part coverage test (A-D), all required, any one matching row suffices.
    `general_episode_rows` must be general-observer ledger rows only (never S5) -- S5 alone never
    satisfies condition D by construction, since S5_OCCURRENCE is never in that row set at all
    (matches `durable_store.read_all_general_episode_rows()`'s own S5-exclusion)."""
    if candidate.status != "MATERIAL":
        return False
    start, end = coverage_window(candidate)
    for row in general_episode_rows:
        if row.get("prospective_eligibility") != "YES":  # A
            continue
        ts = int(row["frozen_at_bar_ts"])
        if not (start <= ts <= end):  # B
            continue
        if row.get("directional_hypothesis") != candidate.direction:  # C -- exact match only
            continue
        if row.get("episode_type") not in GENERAL_OBSERVER_EVENT_TYPES:  # D
            continue
        return True
    return False


def classify_for_clustering(candidate: AuditCandidateResult, general_episode_rows: list[dict]) -> str:
    """Collapses `audit_candidate` + `is_covered` into the 4-way status the cluster state machine
    consumes: "MATERIAL_UNCOVERED" | "MATERIAL_COVERED" | "NOT_MATERIAL" | "UNSCORABLE_ATR_UNAVAILABLE"."""
    if candidate.status in ("NOT_MATERIAL", "UNSCORABLE_ATR_UNAVAILABLE"):
        return candidate.status
    return "MATERIAL_COVERED" if is_covered(candidate, general_episode_rows) else "MATERIAL_UNCOVERED"


def _make_cluster_id(candidate: AuditCandidateResult) -> str:
    """Cluster-ID construction is explicitly VE's own non-semantic engineering choice (Section 10:
    "an engineering choice, not a market-semantic choice") -- a deterministic hash over exactly the
    three CEO-fixed semantic identity inputs (window-start, window-end, direction), same
    hash-for-determinism style already used by `snapshot.compute_snapshot_hash`."""
    raw = f"{candidate.window_start_ts}:{candidate.window_end_ts}:{candidate.direction}"
    return "CLUSTER-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _start_cluster(candidate: AuditCandidateResult) -> RetrospectiveMissedMoveCluster:
    assert candidate.direction is not None and candidate.magnitude is not None and candidate.atr_reference is not None
    return RetrospectiveMissedMoveCluster(
        cluster_id=_make_cluster_id(candidate), direction=candidate.direction,
        canonical_window_start_ts=candidate.window_start_ts, canonical_window_end_ts=candidate.window_end_ts,
        canonical_magnitude=candidate.magnitude, canonical_atr_reference=candidate.atr_reference,
        canonical_normalized_magnitude=candidate.magnitude / candidate.atr_reference,
        qualifying_window_count=1, cluster_terminated_at_ts=None,
    )


def _finalize(cluster: RetrospectiveMissedMoveCluster) -> RetrospectiveMissedMoveCluster:
    """`cluster_terminated_at_ts` = the window-end timestamp of the LAST candidate that actually
    continued the cluster -- derived arithmetically from the canonical (first) candidate's own
    window-end plus the qualifying-window count, since each continuing candidate is, by definition,
    "the immediately next rolling candidate" (exactly one H1 bar / 3600s later than the previous
    one) -- no extra mutable field needed beyond what the frozen dataclass already carries."""
    last_end_ts = cluster.canonical_window_end_ts + (cluster.qualifying_window_count - 1) * H1_SECONDS
    return dataclasses.replace(cluster, cluster_terminated_at_ts=last_end_ts)


def cluster_from_dict(d: dict) -> RetrospectiveMissedMoveCluster:
    """Reconstructs a `RetrospectiveMissedMoveCluster` from a plain dict (e.g. loaded back out of
    durable runtime-state JSON, simulating a process restart). `record_class` has `init=False` on
    the dataclass (a frozen, never-settable field) -- `dataclasses.asdict`-based round-tripping
    through JSON carries it along as a plain key, which must be dropped before reconstruction or
    `RetrospectiveMissedMoveCluster(**d)` raises `TypeError`."""
    kwargs = {k: v for k, v in d.items() if k != "record_class"}
    return RetrospectiveMissedMoveCluster(**kwargs)


def advance_cluster_state(
    classification: str, candidate: AuditCandidateResult, active_cluster: RetrospectiveMissedMoveCluster | None,
) -> tuple[RetrospectiveMissedMoveCluster | None, RetrospectiveMissedMoveCluster | None]:
    """One step of Section 10's rolling cluster state machine. Call once per newly-audited H1
    candidate, in strict chronological order (no skipping -- `MISSED_MOVE_CLUSTER_GAP_BRIDGING = NO`
    is enforced simply by never being given the option to skip ahead), feeding the first return value
    back in as the next call's `active_cluster`.

    Returns `(new_active_cluster, finalized_cluster_or_None)` -- the second element is non-`None`
    exactly once, on the tick a cluster terminates (persist it via
    `durable_store.append_missed_move_cluster()` at that point, exactly once per cluster, per
    Section 10's "written EXACTLY ONCE per cluster, at termination")."""
    if classification == "MATERIAL_UNCOVERED":
        if active_cluster is not None and active_cluster.direction == candidate.direction:
            continuation = dataclasses.replace(active_cluster, qualifying_window_count=active_cluster.qualifying_window_count + 1)
            return continuation, None
        # Either no active cluster, or a direction change -- close the old (if any), open a new one
        # from THIS SAME candidate, in the same step (Section 10, verbatim).
        finalized = _finalize(active_cluster) if active_cluster is not None else None
        return _start_cluster(candidate), finalized
    # NOT_MATERIAL / MATERIAL_COVERED / UNSCORABLE_ATR_UNAVAILABLE -- terminates any active cluster,
    # starts nothing (this candidate itself never qualifies to start a cluster).
    finalized = _finalize(active_cluster) if active_cluster is not None else None
    return None, finalized
