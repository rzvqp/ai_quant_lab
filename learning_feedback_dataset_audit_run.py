"""Learning Feedback -- Phase 1 Closeout: full dataset audit (CEO directive, 2026-07-24). Read-only
analysis of the Stage 2 full-capture repository (`learning_feedback_data/full_capture/`, 688
PositionOutcome / 688 Outcome / 26 InterimRealization / 23,639 Observation, per
`LEARNING_FEEDBACK_PHASE1_STAGE2_FULL_CAPTURE_REPORT.md`). **Zero `ai_trader/` file touched. Zero new
production logic. No performance/edge/profitability interpretation** -- every statistic below is
descriptive shape only (counts, means, medians, sign counts), never a verdict on any strategy's own
worth, per the CEO's own explicit "this is not a strategy audit" instruction.

Reuses only the repository's own already-existing, already-tested public read API
(`iter_outcomes`/`iter_position_outcomes`/`iter_interim_realizations`/`iter_observations`,
`get_outcome`/`get_position_outcome`/`get_interim_realization`/`get_observation`) -- never re-implements
parsing, never reaches into `ai_trader/simulation`/`shadow_evidence` internals.
"""

from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from ai_trader.context_memory.contracts import EdgeEvidenceId
from ai_trader.context_memory.enums import OutcomeKind, OutcomeStatus
from ai_trader.context_memory.repository import ContextMemoryRepository
from ai_trader.shadow_evidence.config import all_registered_strategies

REPO_ROOT = Path(__file__).resolve().parent
FULL_CAPTURE_PATH = REPO_ROOT / "learning_feedback_data" / "full_capture"
WINDOW_START = 1_729_674_000
WINDOW_END = 1_761_210_000
EXPECTED_RUN_ID = "LF-STAGE2-FULL-CAPTURE"
REPORT_PATH = REPO_ROOT / "learning_feedback_dataset_audit_results.json"


def _sign(x: float) -> str:
    if x > 0:
        return "positive"
    if x < 0:
        return "negative"
    return "zero"


def _describe(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0}
    return {
        "count": len(values), "mean": statistics.fmean(values), "median": statistics.median(values),
        "min": min(values), "max": max(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
    }


def main() -> None:
    repo = ContextMemoryRepository(FULL_CAPTURE_PATH)
    repo.rebuild()

    outcomes = list(repo.iter_outcomes())
    position_outcomes = list(repo.iter_position_outcomes())
    interims = list(repo.iter_interim_realizations())
    observations = list(repo.iter_observations())

    audit: dict[str, Any] = {}

    # ============================================================================================
    # 1. Integrity
    # ============================================================================================
    audit["integrity"] = {
        "total_position_outcomes": len(position_outcomes),
        "total_outcomes": len(outcomes),
        "total_interim_realizations": len(interims),
        "total_observations": len(observations),
        "all_position_outcomes_constructed_without_error": True,  # rebuild() would have raised otherwise
        "outcomes_resolved": sum(1 for o in outcomes if o.status is OutcomeStatus.RESOLVED),
        "outcomes_non_resolved": sum(1 for o in outcomes if o.status is not OutcomeStatus.RESOLVED),
        "outcomes_non_resolved_breakdown": dict(Counter(
            o.status.value for o in outcomes if o.status is not OutcomeStatus.RESOLVED
        )),
    }

    from ai_trader.context_memory.identities import compute_edge_evidence_id, compute_position_outcome_id

    orphan_terminal = [
        po for po in position_outcomes if repo.get_outcome(EdgeEvidenceId(po.terminal_outcome_id.value)) is None
    ]
    orphan_interim_refs = [
        (po.position_key, irid) for po in position_outcomes for irid in po.constituent_interim_realization_ids
        if repo.get_interim_realization(irid) is None
    ]
    orphan_obs_outcome = [o for o in outcomes if repo.get_observation(o.observation_id) is None]
    orphan_obs_position_outcome = [po for po in position_outcomes if repo.get_observation(po.observation_id) is None]
    orphan_obs_interim = [ir for ir in interims if repo.get_observation(ir.observation_id) is None]

    audit["integrity"]["broken_links"] = {
        "position_outcome_terminal_outcome_id_unresolved": len(orphan_terminal),
        "position_outcome_interim_realization_id_unresolved": len(orphan_interim_refs),
        "outcome_observation_id_unresolved": len(orphan_obs_outcome),
        "position_outcome_observation_id_unresolved": len(orphan_obs_position_outcome),
        "interim_realization_observation_id_unresolved": len(orphan_obs_interim),
    }

    # Line-count cross-check: iterated record count must equal physical JSONL line count exactly (catches
    # any silent double-append/skip that wouldn't otherwise surface).
    line_counts = {}
    for name, count in (
        ("outcomes.jsonl", len(outcomes)), ("position_outcomes.jsonl", len(position_outcomes)),
        ("interim_realizations.jsonl", len(interims)), ("observations.jsonl", len(observations)),
    ):
        path = FULL_CAPTURE_PATH / name
        physical_lines = sum(1 for _ in path.open(encoding="utf-8")) if path.exists() else 0
        line_counts[name] = {"iterated_count": count, "physical_line_count": physical_lines, "match": physical_lines == count}
    audit["integrity"]["line_count_cross_check"] = line_counts

    # ============================================================================================
    # 2. Consistency
    # ============================================================================================
    outcome_ids = [compute_edge_evidence_id(o).value for o in outcomes]
    po_ids = [compute_position_outcome_id(po).value for po in position_outcomes]
    audit["consistency"] = {
        "duplicate_outcome_ids": len(outcome_ids) - len(set(outcome_ids)),
        "duplicate_position_outcome_ids": len(po_ids) - len(set(po_ids)),
        "duplicate_position_keys_across_position_outcomes": (
            len(position_outcomes) - len({po.position_key for po in position_outcomes})
        ),
    }

    # run_id consistency: position_key/Shadow position_id both embed run_id as their own leading
    # colon-separated field, by pre-existing design (position_registry.py:36-41, shadow_evidence/
    # engine.py:334) -- verified empirically here, not assumed.
    run_id_prefixes = Counter(po.position_key.split(":", 1)[0] for po in position_outcomes)
    interim_run_id_prefixes = Counter(ir.position_key.split(":", 1)[0] for ir in interims)
    audit["consistency"]["run_id_prefixes_in_position_outcomes"] = dict(run_id_prefixes)
    audit["consistency"]["run_id_prefixes_in_interim_realizations"] = dict(interim_run_id_prefixes)
    audit["consistency"]["run_id_fully_consistent"] = (
        set(run_id_prefixes) <= {EXPECTED_RUN_ID} and set(interim_run_id_prefixes) <= {EXPECTED_RUN_ID}
    )

    # Arithmetic identity check: total_net_pnl should equal total_gross_pnl - total_costs (not enforced
    # by __post_init__, computed by the adapter -- verified empirically, not assumed).
    arithmetic_mismatches = [
        {"position_key": po.position_key, "gross": po.total_gross_pnl, "costs": po.total_costs,
         "net": po.total_net_pnl, "expected_net": po.total_gross_pnl - po.total_costs}
        for po in position_outcomes
        if abs((po.total_gross_pnl - po.total_costs) - po.total_net_pnl) > 1e-6
    ]
    audit["consistency"]["net_pnl_arithmetic_mismatches"] = len(arithmetic_mismatches)
    audit["consistency"]["net_pnl_arithmetic_mismatch_examples"] = arithmetic_mismatches[:5]

    # Sign-consistency check: PositionOutcome.total_net_pnl sign vs its own terminal Outcome.normalized_result sign.
    sign_mismatches = []
    for po in position_outcomes:
        terminal = repo.get_outcome(EdgeEvidenceId(po.terminal_outcome_id.value))
        if terminal is not None and terminal.normalized_result is not None:
            if _sign(po.total_net_pnl) != _sign(terminal.normalized_result) and po.total_net_pnl != 0 and terminal.normalized_result != 0:
                sign_mismatches.append({
                    "position_key": po.position_key, "total_net_pnl": po.total_net_pnl,
                    "terminal_outcome_normalized_result": terminal.normalized_result,
                })
    audit["consistency"]["position_outcome_vs_terminal_outcome_sign_mismatches"] = len(sign_mismatches)
    audit["consistency"]["sign_mismatch_examples"] = sign_mismatches[:5]

    # ============================================================================================
    # 3. Distributions (descriptive only)
    # ============================================================================================
    dist: dict[str, Any] = {}

    dist["position_outcome_by_kind"] = dict(Counter(po.outcome_kind.value for po in position_outcomes))
    dist["position_outcome_by_strategy"] = {}
    strat_kind: dict[str, Counter[str]] = defaultdict(Counter)
    for po in position_outcomes:
        strat_kind[po.strategy_id][po.outcome_kind.value] += 1
    dist["position_outcome_by_strategy"] = {k: dict(v) for k, v in sorted(strat_kind.items())}

    dist["position_outcome_total_qty_closed"] = _describe([po.total_qty_closed for po in position_outcomes])
    dist["position_outcome_total_gross_pnl"] = _describe([po.total_gross_pnl for po in position_outcomes])
    dist["position_outcome_total_net_pnl"] = _describe([po.total_net_pnl for po in position_outcomes])
    dist["position_outcome_total_costs"] = _describe([po.total_costs for po in position_outcomes])
    dist["position_outcome_holding_time_seconds"] = _describe(
        [po.terminal_as_of - po.opened_as_of for po in position_outcomes]
    )
    dist["position_outcome_weighted_avg_exit_price_null_count"] = sum(
        1 for po in position_outcomes if po.weighted_avg_exit_price is None
    )
    dist["position_outcome_result_sign"] = dict(Counter(_sign(po.total_net_pnl) for po in position_outcomes))

    dist["outcome_by_kind"] = dict(Counter(o.outcome_kind.value for o in outcomes))
    dist["outcome_normalized_result_sign"] = dict(Counter(
        _sign(o.normalized_result) for o in outcomes if o.normalized_result is not None
    ))
    dist["outcome_normalized_result_shape"] = _describe(
        [o.normalized_result for o in outcomes if o.normalized_result is not None]
    )

    dist["interim_realization_by_kind"] = dict(Counter(ir.outcome_kind.value for ir in interims))
    dist["interim_realization_by_strategy"] = dict(Counter(ir.strategy_id for ir in interims))
    dist["interim_realization_normalized_result_present_count"] = sum(
        1 for ir in interims if ir.normalized_result is not None
    )
    dist["interim_realization_unavailable_count"] = sum(1 for ir in interims if ir.unavailable_reason is not None)

    # Context join: session_state / volatility_regime / trend_m15 / multi_timeframe_agreement, joined via
    # each record's own observation_id -- only fields Context Memory's ContextSnapshot actually stores.
    session_by_kind: dict[str, Counter[str]] = defaultdict(Counter)
    volatility_by_kind: dict[str, Counter[str]] = defaultdict(Counter)
    trend_by_kind: dict[str, Counter[str]] = defaultdict(Counter)
    agreement_by_kind: dict[str, Counter[str]] = defaultdict(Counter)
    missing_observation_join = 0
    for po in position_outcomes:
        obs = repo.get_observation(po.observation_id)
        if obs is None:
            missing_observation_join += 1
            continue
        snap = obs.context_snapshot
        session_by_kind[po.outcome_kind.value][snap.session_state or "UNKNOWN"] += 1
        volatility_by_kind[po.outcome_kind.value][snap.volatility_regime.value] += 1
        trend_by_kind[po.outcome_kind.value][snap.trend_m15.value] += 1
        agreement_by_kind[po.outcome_kind.value][snap.multi_timeframe_agreement.value] += 1
    dist["position_outcome_by_session"] = {k: dict(v) for k, v in session_by_kind.items()}
    dist["position_outcome_by_volatility_regime"] = {k: dict(v) for k, v in volatility_by_kind.items()}
    dist["position_outcome_by_trend_m15"] = {k: dict(v) for k, v in trend_by_kind.items()}
    dist["position_outcome_by_multi_timeframe_agreement"] = {k: dict(v) for k, v in agreement_by_kind.items()}
    dist["position_outcome_observation_join_failures"] = missing_observation_join

    # Direction: NOT a stored field on Outcome/PositionOutcome/InterimRealization. Recoverable, best-
    # effort, ONLY for PORTFOLIO-kind via position_key's own 4th colon-separated field (make_position_key's
    # own documented shape "{run_id}:{symbol}:{opened_as_of}:{direction}") -- Shadow's own position_id
    # shape carries no direction field at all. Disclosed as a genuine, real data-model gap, not invented.
    direction_portfolio = Counter()
    direction_unparseable = 0
    for po in position_outcomes:
        if po.outcome_kind is OutcomeKind.PORTFOLIO:
            parts = po.position_key.split(":")
            if len(parts) == 4:
                direction_portfolio[parts[3]] += 1
            else:
                direction_unparseable += 1
    dist["position_outcome_direction_portfolio_kind_only"] = dict(direction_portfolio)
    dist["position_outcome_direction_unparseable_count"] = direction_unparseable
    dist["direction_available_for_strategy_kind"] = False
    dist["close_reason_available"] = False  # not persisted anywhere in Context Memory's own contracts today

    audit["distributions"] = dist

    # ============================================================================================
    # 4. Coverage
    # ============================================================================================
    all_43 = sorted(all_registered_strategies())
    strategies_with_position_outcome = {po.strategy_id for po in position_outcomes}
    strategies_ever_present = set()
    for obs in observations:
        for ref in obs.present_edges:
            strategies_ever_present.add(ref.strategy_id)
    never_present_at_all = sorted(set(all_43) - strategies_ever_present)
    present_but_no_outcome = sorted(strategies_ever_present - strategies_with_position_outcome)

    audit["coverage"] = {
        "total_registered_strategies": len(all_43),
        "strategies_with_at_least_one_position_outcome": len(strategies_with_position_outcome),
        "strategies_ever_present_per_edge_intelligence": len(strategies_ever_present),
        "strategies_never_present_at_all": never_present_at_all,
        "strategies_present_but_zero_position_outcome": present_but_no_outcome,
    }

    # ============================================================================================
    # 5. Anomalies
    # ============================================================================================
    anomalies: dict[str, Any] = {}

    out_of_window_position_outcomes = [
        po.position_key for po in position_outcomes
        if not (WINDOW_START <= po.opened_as_of <= WINDOW_END and WINDOW_START <= po.terminal_as_of <= WINDOW_END)
    ]
    out_of_window_outcomes = [
        compute_edge_evidence_id(o).value for o in outcomes
        if not (WINDOW_START <= o.observation_as_of <= WINDOW_END)
        or (o.resolution_as_of is not None and not (WINDOW_START <= o.resolution_as_of <= WINDOW_END))
    ]
    anomalies["timestamps_outside_configured_window"] = {
        "position_outcomes": len(out_of_window_position_outcomes),
        "outcomes": len(out_of_window_outcomes),
        "examples": (out_of_window_position_outcomes + out_of_window_outcomes)[:5],
    }

    excessive_interim_counts = [
        {"position_key": po.position_key, "constituent_count": len(po.constituent_interim_realization_ids)}
        for po in position_outcomes if len(po.constituent_interim_realization_ids) > 5
    ]
    anomalies["position_outcomes_with_more_than_5_interim_realizations"] = excessive_interim_counts

    zero_qty_or_negative = [po.position_key for po in position_outcomes if po.total_qty_closed <= 0]
    anomalies["non_positive_total_qty_closed"] = zero_qty_or_negative  # structurally impossible (__post_init__), sanity re-check

    unresolved_outcomes_detail = [
        {"strategy_id": o.strategy_id, "status": o.status.value, "unavailable_reason":
         o.unavailable_reason.value if o.unavailable_reason else None}
        for o in outcomes if o.status is not OutcomeStatus.RESOLVED
    ]
    anomalies["non_resolved_outcomes_detail"] = unresolved_outcomes_detail

    # Interim realizations whose position_key never appears in any PositionOutcome -- a LEGITIMATE state
    # (position still open at window end after a partial exit) if it occurs, not corruption; disclosed.
    po_position_keys = {po.position_key for po in position_outcomes}
    dangling_interims = sorted({ir.position_key for ir in interims} - po_position_keys)
    anomalies["interim_realizations_with_no_terminal_position_outcome"] = dangling_interims

    audit["anomalies"] = anomalies

    with REPORT_PATH.open("w") as f:
        json.dump(audit, f, indent=2, default=str)
    print(f"wrote {REPORT_PATH}")
    print(json.dumps(audit, indent=2, default=str)[:3000])


if __name__ == "__main__":
    main()
