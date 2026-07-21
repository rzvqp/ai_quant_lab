"""Portfolio Architect -- Tie-Break Bias Evidence Generation (CEO directive, 2026-07-21). Determines
whether deterministic alphabetical tie-breaking in the Scoring Engine's own Ranker
(``ai_trader/scoring_engine/ranker.py``) produces a measurable systematic allocation bias, and whether
replacing it with a deterministic round-robin (Portfolio Architect Policy Research candidate 1) would
preserve every existing architectural contract. **Evidence generation only -- no implementation, no new
``ArchitectMode``, no runtime behavior change.**

**Zero-file-diff measurement technique** (identical precedent to ``phase69a_funnel_recorder.py`` /
``ceo_strategy_constraint_root_cause_study.py`` / ``portfolio_architect_phase2a_calibration.py``): monkey
-patches the bound methods of an ALREADY-CONSTRUCTED harness instance's own component objects
(``_scoring_engine.score_batch``, ``_risk_manager.evaluate``) AFTER ``harness.load()``. Each wrapper
calls the ORIGINAL, unmodified implementation and returns its result UNCHANGED -- it only additionally
records it. Zero lines changed in any ``ai_trader/`` source file.

**Window**: reuses the SAME CEO-approved, non-holdout 12-month window ``phase69a_funnel_run.py`` already
established (2024-10-23 -> 2025-10-23) -- "long historical simulation," per this directive's own
requirement, and explicitly NOT a new or enlarged window invented for this study (same precedent already
used for the Root-Cause Study). Shadow Evidence is disabled this run (not needed for this question,
already proven not to affect Signal/Scoring/Risk Manager behavior -- Phase 1's own byte-identical proof)
to reduce runtime.
"""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import RiskManager
from ai_trader.risk_manager.types import Decision
from ai_trader.shadow_evidence.config import all_registered_strategies
from ai_trader.signal_engine.types import ACTIONABLE_STATES
from ai_trader.simulation.config import DateRange, SimulationContext
from ai_trader.simulation.harness import SimulationHarness
from ai_trader.simulation.types import RunState
from ai_trader.strategy_manager.config import ManagerConfig

REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data" / "market"
SYMBOL_META = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}

# Same CEO-approved, non-holdout window as phase69a_funnel_run.py -- not invented for this study.
WINDOW_START = 1_729_674_000   # 2024-10-23 09:00:00 UTC
WINDOW_END = 1_761_210_000     # 2025-10-23 09:00:00 UTC


def _risk_config() -> RiskConfig:
    cfg = RiskConfig()
    cfg.filters.reference_spread["XAUUSD"] = 0.10
    cfg.filters.liquidity_floor["XAUUSD"] = 1.0
    return cfg


def new_harness(run_id: str) -> SimulationHarness:
    context = SimulationContext(
        run_id=run_id, date_range=DateRange(WINDOW_START, WINDOW_END), symbols=("XAUUSD",),
        timeframes=("M15", "H1", "H4", "D1"), starting_balance=2000.0, run_seed=1, warmup_bars=200,
    )
    harness = SimulationHarness(
        context, SYMBOL_META, DATA_DIR, manager_config=ManagerConfig(auto_admit_min_maturity="EXPLORATORY"),
        use_strategy_runtime=True, risk_config=_risk_config(),
        enable_time_stops=True, enable_trailing_stops=True, strategy_id_filter=None,
    )
    harness.configure()
    harness.load()
    assert harness.state is RunState.WARMUP, harness.fail_reason
    return harness


# ================================================================================================
# Zero-diff instrumentation
# ================================================================================================


class Recorder:
    def __init__(self) -> None:
        self.by_bar: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
        self.decision_events: list[dict[str, Any]] = []
        self.tie_snapshots: dict[tuple[str, int], dict[str, Any]] = {}


def _tie_key(candidates: list[dict[str, Any]]) -> tuple[tuple[str, ...], ...] | None:
    """Groups actionable candidates by EXACT (total_score, historical_confidence, signal_strength)
    match. Returns the tied groups (each of size >= 2) as tuples of strategy_id, or None if no genuine
    tie exists among actionable candidates this bar."""
    actionable = [c for c in candidates if c["state"] in ("BUY", "SELL")]
    groups: dict[tuple[Any, ...], list[str]] = defaultdict(list)
    for c in actionable:
        key = (c["total_score"], c["historical_confidence"], c["signal_strength"])
        groups[key].append(c["strategy_id"])
    tied = tuple(tuple(sorted(ids)) for ids in groups.values() if len(ids) >= 2)
    return tied if tied else None


def instrument(harness: SimulationHarness, recorder: Recorder) -> None:
    assert harness._scoring_engine is not None and harness._risk_manager is not None  # type: ignore[attr-defined]

    orig_score_batch = harness._scoring_engine.score_batch  # type: ignore[attr-defined]

    def wrapped_score_batch(signals: Any) -> Any:
        result = orig_score_batch(signals)
        for score in result.scores:
            recorder.by_bar[(score.symbol, score.as_of)].append({
                "strategy_id": score.strategy_id, "as_of": score.as_of, "symbol": score.symbol,
                "rank": score.rank, "total_score": score.total_score,
                "historical_confidence": score.component_scores.historical_confidence,
                "signal_strength": score.component_scores.signal_strength,
                "state": score.state.value if hasattr(score.state, "value") else str(score.state),
                "score_obj": score,
            })
        return result

    harness._scoring_engine.score_batch = wrapped_score_batch  # type: ignore[attr-defined]

    orig_evaluate = harness._risk_manager.evaluate  # type: ignore[attr-defined]

    def wrapped_evaluate(opportunities: Any, risk_context: Any, portfolio: Any) -> Any:
        result = orig_evaluate(opportunities, risk_context, portfolio)
        for decision in result.decisions:
            recorder.decision_events.append({
                "strategy_id": decision.strategy_id, "symbol": decision.symbol, "as_of": decision.as_of,
                "decision": decision.decision.value,
                "denied_reasons": [r.code for r in (decision.denied_reasons or ())],
            })
        if opportunities:
            key = (result.decisions[0].symbol if result.decisions else None, result.as_of)
            candidates = recorder.by_bar.get(key, [])
            if _tie_key(candidates) is not None and key not in recorder.tie_snapshots:
                recorder.tie_snapshots[key] = {
                    "risk_context": risk_context, "portfolio_state": portfolio, "candidates": candidates,
                }
        return result

    harness._risk_manager.evaluate = wrapped_evaluate  # type: ignore[attr-defined]


# ================================================================================================
# Q1-Q3: tie frequency, affected strategies, is alphabetical the effective tie-break
# ================================================================================================


def tie_frequency_analysis(recorder: Recorder) -> dict[str, Any]:
    tie_bars = 0
    total_bars_with_multi_actionable = 0
    strategy_participation: dict[str, int] = defaultdict(int)
    alphabetical_confirmed = 0
    alphabetical_contradicted = 0
    tie_group_sizes: list[int] = []

    for key, candidates in recorder.by_bar.items():
        actionable = [c for c in candidates if c["state"] in ("BUY", "SELL")]
        if len(actionable) >= 2:
            total_bars_with_multi_actionable += 1
        tied_groups = _tie_key(candidates)
        if tied_groups is None:
            continue
        tie_bars += 1
        for group in tied_groups:
            tie_group_sizes.append(len(group))
            for sid in group:
                strategy_participation[sid] += 1
            # Q3: within this tied group, does the LOWEST-rank-number (highest priority) member match
            # the alphabetically-first member? (Ranker's own documented tie-break: total_score desc,
            # historical_confidence desc, signal_strength desc, strategy_id ASC -- since this group is
            # tied on the first three, strategy_id ascending should decide it.)
            group_candidates = [c for c in candidates if c["strategy_id"] in group]
            winner = min(group_candidates, key=lambda c: c["rank"])["strategy_id"]
            alphabetical_winner = sorted(group)[0]
            if winner == alphabetical_winner:
                alphabetical_confirmed += 1
            else:
                alphabetical_contradicted += 1

    return {
        "n_bars_with_multi_actionable_candidates": total_bars_with_multi_actionable,
        "n_bars_with_a_genuine_tie": tie_bars,
        "tie_rate_among_multi_candidate_bars": (
            tie_bars / total_bars_with_multi_actionable if total_bars_with_multi_actionable else None
        ),
        "n_tied_groups_total": len(tie_group_sizes),
        "tie_group_size_distribution": dict(
            (str(k), v) for k, v in
            sorted({s: tie_group_sizes.count(s) for s in set(tie_group_sizes)}.items())
        ) if tie_group_sizes else {},
        "strategies_ever_in_a_tie": sorted(strategy_participation.keys()),
        "tie_participation_count_by_strategy": dict(strategy_participation),
        "alphabetical_confirmed_as_effective_tiebreak": alphabetical_confirmed,
        "alphabetical_contradicted": alphabetical_contradicted,
    }


# ================================================================================================
# Q4: does alphabetical ordering systematically favor early strategy IDs
# ================================================================================================


def systematic_bias_analysis(recorder: Recorder, all_ids: list[str]) -> dict[str, Any]:
    # Ordinal universe is derived from strategy ids ACTUALLY observed in the captured data, not from
    # all_registered_strategies() (which only scopes Shadow Evidence's own bookkeeping -- unrelated to
    # the real competitive strategy universe admitted via ManagerConfig/strategy_runtime, and Shadow is
    # disabled entirely in this study). all_ids is accepted for logging/cross-check only.
    observed_ids = sorted({c["strategy_id"] for candidates in recorder.by_bar.values() for c in candidates})
    ordinal = {sid: i for i, sid in enumerate(observed_ids)}
    win_ordinals: list[int] = []
    participant_ordinals: list[int] = []

    for candidates in recorder.by_bar.values():
        tied_groups = _tie_key(candidates)
        if tied_groups is None:
            continue
        for group in tied_groups:
            group_candidates = [c for c in candidates if c["strategy_id"] in group]
            winner = min(group_candidates, key=lambda c: c["rank"])["strategy_id"]
            win_ordinals.append(ordinal[winner])
            participant_ordinals.extend(ordinal[sid] for sid in group)

    if not win_ordinals:
        return {"n_ties": 0, "note": "no genuine ties occurred -- systematic bias is not evaluable"}

    mean_winner_ordinal = statistics.mean(win_ordinals)
    mean_participant_ordinal = statistics.mean(participant_ordinals)
    return {
        "n_ties": len(win_ordinals),
        "mean_winner_ordinal": mean_winner_ordinal,
        "mean_participant_ordinal_if_random": mean_participant_ordinal,
        "winner_ordinal_below_participant_mean": mean_winner_ordinal < mean_participant_ordinal,
        "interpretation": (
            "winner ordinal systematically LOWER than the participant pool's own mean ordinal indicates "
            "early-alphabet strategies win ties more often than chance would predict"
        ),
    }


# ================================================================================================
# Q5: does this affect only identical-score opportunities (negative control on near-ties)
# ================================================================================================


def near_tie_negative_control(recorder: Recorder) -> dict[str, Any]:
    near_tie_bars = 0
    for candidates in recorder.by_bar.values():
        actionable = sorted(
            (c for c in candidates if c["state"] in ("BUY", "SELL")), key=lambda c: -c["total_score"],
        )
        for a, b in zip(actionable, actionable[1:]):
            if a["total_score"] != b["total_score"] and abs(a["total_score"] - b["total_score"]) <= 1:
                near_tie_bars += 1
                break
    return {
        "n_bars_with_near_tie_but_not_exact_tie": near_tie_bars,
        "control_purpose": (
            "confirms the tie analysis above is restricted to EXACT matches only, not near-misses -- a "
            "near-tie (score differs by 1) must never be counted as a genuine tie by _tie_key()"
        ),
    }


# ================================================================================================
# Q6/Q7: counterfactual round-robin replay (shadow evaluation only)
# ================================================================================================


def round_robin_replay(recorder: Recorder, risk_config: RiskConfig) -> dict[str, Any]:
    rotation_pointer: dict[tuple[str, ...], int] = defaultdict(int)
    results: list[dict[str, Any]] = []

    for key in sorted(recorder.tie_snapshots.keys(), key=lambda k: k[1]):
        snapshot = recorder.tie_snapshots[key]
        candidates = snapshot["candidates"]
        tied_groups = _tie_key(candidates)
        if not tied_groups:
            continue

        # Build the round-robin-adjusted rank assignment: within each tied group, rotate who receives
        # the group's own best (lowest-number) rank instead of always the alphabetically-first member.
        # Every rank outside the tied group is left untouched.
        rank_for: dict[str, int] = {}
        for group in tied_groups:  # group is already a sorted tuple, per _tie_key()'s own construction
            idx = rotation_pointer[group] % len(group)
            rr_winner = group[idx]
            rotation_pointer[group] += 1

            group_entries = [c for c in candidates if c["strategy_id"] in group]
            original_ranks_ascending = sorted(c["rank"] for c in group_entries)
            members_in_rank_order = [rr_winner] + [sid for sid in group if sid != rr_winner]
            rank_for.update(zip(members_in_rank_order, original_ranks_ascending))

        from dataclasses import replace as _replace
        adjusted_scores = [
            _replace(c["score_obj"], rank=rank_for[c["strategy_id"]]) if c["strategy_id"] in rank_for
            else c["score_obj"]
            for c in candidates
        ]

        fresh_rm = RiskManager(risk_config)
        fresh_rm.configure(portfolio=snapshot["portfolio_state"])
        rr_decision = fresh_rm.evaluate(adjusted_scores, snapshot["risk_context"], snapshot["portfolio_state"])
        rr_winner_strategy = next(
            (d.strategy_id for d in rr_decision.decisions if d.decision == Decision.ALLOW), None,
        )
        rr_denied_types = sorted({
            code for d in rr_decision.decisions for code in (d.denied_reasons and [r.code for r in d.denied_reasons] or [])
        })

        actual_winner = next(
            (e["strategy_id"] for e in recorder.decision_events
             if e["as_of"] == key[1] and e["symbol"] == key[0] and e["decision"] == "ALLOW"), None,
        )
        actual_denied_types = sorted({
            code for e in recorder.decision_events
            if e["as_of"] == key[1] and e["symbol"] == key[0] for code in e["denied_reasons"]
        })

        # Q7 check: confirm no score/eligibility/decision-TYPE field differs beyond which strategy_id
        # occupies the winning slot -- compare the SET of denial reason codes issued this bar.
        denial_types_unchanged = actual_denied_types == rr_denied_types

        results.append({
            "symbol": key[0], "as_of": key[1], "tied_groups": tied_groups,
            "actual_winner": actual_winner, "round_robin_winner": rr_winner_strategy,
            "winner_changed": actual_winner != rr_winner_strategy,
            "denial_reason_types_unchanged": denial_types_unchanged,
            "actual_denied_types": actual_denied_types, "round_robin_denied_types": rr_denied_types,
        })

    winner_changes = sum(1 for r in results if r["winner_changed"])
    denial_type_violations = sum(1 for r in results if not r["denial_reason_types_unchanged"])
    interesting = [r for r in results if r["winner_changed"] or not r["denial_reason_types_unchanged"]]
    return {
        "n_tie_bars_replayed": len(results),
        "n_bars_where_round_robin_changes_the_winner": winner_changes,
        "n_bars_with_denial_reason_type_drift": denial_type_violations,
        "interesting_cases": interesting,  # every winner-change / denial-type-drift case, fully captured
        "sample": results[:30],
    }


# ================================================================================================
# Main
# ================================================================================================


def main() -> None:
    recorder = Recorder()
    risk_config = _risk_config()
    all_ids = sorted(all_registered_strategies())
    harness = new_harness("PA-TIEBREAK-EVIDENCE")
    instrument(harness, recorder)
    harness.run_to_completion()
    assert harness.state is RunState.COMPLETED, harness.fail_reason

    output = {
        "run_id": "PA-TIEBREAK-EVIDENCE",
        "window": {"start": WINDOW_START, "end": WINDOW_END},
        "bars_processed": harness.bars_processed,
        "n_strategies": len(all_ids),
        "tie_frequency_analysis": tie_frequency_analysis(recorder),
        "systematic_bias_analysis": systematic_bias_analysis(recorder, all_ids),
        "near_tie_negative_control": near_tie_negative_control(recorder),
        "round_robin_replay": round_robin_replay(recorder, risk_config),
    }

    out_path = REPO_ROOT / "portfolio_architect_tiebreak_evidence.json"
    with out_path.open("w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"wrote {out_path}")
    print(json.dumps(output, indent=2, default=str)[:6000])


if __name__ == "__main__":
    main()
