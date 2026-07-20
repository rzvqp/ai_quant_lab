"""CEO-directed research study (2026-07-20): Strategy Constraint Root-Cause Study.

Determines EXACTLY why the six candidate strategies (S1, S13, S39, S40, S46, S48) are constrained in
the competitive scenario, and which specific component produces each denial -- at EVENT level, not
aggregate totals. NOT a checkpoint. Does not modify production, strategies, Risk, Sizing, Portfolio,
Decision Intelligence, or Context Memory. Introduces no new thresholds, no optimization, no behavior
change.

**Zero-file-diff measurement technique** (identical precedent to `phase69a_funnel_recorder.py`, reused
directly): monkey-patches the bound methods of an ALREADY-CONSTRUCTED harness instance's own component
objects (`_signal_engine.evaluate`, `_scoring_engine.score_batch`, `_risk_manager.evaluate`) AFTER
`harness.load()`. Each wrapper calls the ORIGINAL, unmodified implementation and returns its result
UNCHANGED -- it only additionally records it. This changes ZERO lines in any `ai_trader/` source file;
the exact same compiled decision logic runs. Reuses `new_harness()` directly from
`phase69a_funnel_run.py` (the same `SimulationContext`/`RiskConfig`/harness construction already used
for the paired isolated/competitive dataset), so this run is over the IDENTICAL window/config/market
data/costs as the original study and its audit.

**Major methodological correction made during this study's own design** (documented in the report's own
§1/§2): `BELOW_FLOOR` is NOT a position-sizing gate. Direct source citation:
`ai_trader/risk_manager/pipeline.py` line 99: `DeniedReason(code="BELOW_FLOOR",
observed=opportunity.recommendation.value)` -- this is the Scoring Engine's own "Recommendation Floor"
gate (`RISK_POLICY.md`: requires `recommendation in {STRONG,MODERATE,WEAK}_OPPORTUNITY`, denies
WATCH/SKIP/INVALID). Sizing (`ai_trader/risk_manager/sizing.py`) NEVER RUNS for a BELOW_FLOOR-denied
opportunity -- no stop distance/ATR/equity/position-size computation exists for these events, because
the recommendation-floor gate runs BEFORE sizing in the pipeline. The CEO's own Phase 2 questions
(framed around position-sizing internals) are answered honestly in this study by explaining precisely
why they do not apply to BELOW_FLOOR, and by investigating the ACTUAL mechanism instead: the Scoring
Engine's own `component_scores.conflict_penalty` (`ai_trader/scoring_engine/conflict.py`), a batch-wide,
cross-strategy score adjustment applied when other strategies have an opposing-direction or
same-`contract.klass`-correlated actionable signal on the identical `(symbol, as_of)` -- a genuine,
demonstrated, portfolio-context-dependent mechanism that is STRUCTURALLY IMPOSSIBLE in a single-strategy
isolated run (`compute_conflict_penalties` requires >=2 actionable signals in the same batch; with
`strategy_id_filter=frozenset({one_id})` there can never be a second one -- conflict_penalty=0 by
construction, proven by the code, not merely observed).

Separately, `SIZE_BELOW_MIN` (a genuinely distinct code, `sizing.py` line 83-87) IS the real sizing-floor
denial -- reported here too, for completeness, even though it was not the CEO's own named target.
"""

from __future__ import annotations

import dataclasses
import enum
import json
import statistics
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from phase69a_funnel_run import new_harness

REPO_ROOT = Path(__file__).resolve().parent
TARGET_STRATEGIES = ("S1", "S13", "S39", "S40", "S46", "S48")
BELOW_FLOOR_TARGETS = ("S40", "S46", "S48")
SHARED_SLOT_TARGETS = ("S1", "S13", "S39")


# ============================================================================================
# Deep instrumentation -- same monkey-patch technique as phase69a_funnel_recorder.py
# ============================================================================================


class RootCauseRecorder:
    """Per-event records for the six target strategies only (other strategies are still scored/risked
    normally -- their events are just not retained, keeping the output focused and small)."""

    def __init__(self) -> None:
        self.actionable_by_bar: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
        self.scores: list[dict[str, Any]] = []
        self.decisions: list[dict[str, Any]] = []
        self.position_snapshots: dict[str, dict[str, Any] | None] = {}

    def record_signal_batch(self, as_of: int, signal_batch: object) -> None:
        for signal in signal_batch.signals:  # type: ignore[attr-defined]
            if signal.state.value in ("BUY", "SELL"):
                key = (signal.symbol, as_of)
                self.actionable_by_bar[key].append({
                    "strategy_id": signal.strategy_id, "direction": signal.direction.value,
                })

    def record_score_batch(self, as_of: int, score_batch: object) -> None:
        for score in score_batch.scores:  # type: ignore[attr-defined]
            if score.strategy_id not in TARGET_STRATEGIES:
                continue
            tc = score.trade_context
            other_actionable = [
                e for e in self.actionable_by_bar.get((score.symbol, as_of), ())
                if e["strategy_id"] != score.strategy_id
            ]
            self.scores.append({
                "strategy_id": score.strategy_id, "as_of": as_of, "symbol": score.symbol,
                "direction": score.direction.value, "state": score.state.value,
                "total_score": score.total_score, "quality": score.quality.value,
                "recommendation": score.recommendation.value,
                "base_quality": score.base_quality, "penalty_factor": score.penalty_factor,
                "component_scores": dataclasses.asdict(score.component_scores),
                "reason_codes": [dataclasses.asdict(r) for r in score.reason_codes],
                "trade_context": dataclasses.asdict(tc) if tc is not None else None,
                "other_actionable_same_bar": other_actionable,
            })

    def record_decision_batch(
        self, as_of: int, decision_batch: object, portfolio_state: object,
        score_direction_by_key: dict[tuple[str, str, int], str] | None = None,
    ) -> None:
        score_direction_by_key = score_direction_by_key or {}
        for decision in decision_batch.decisions:  # type: ignore[attr-defined]
            if decision.strategy_id not in TARGET_STRATEGIES:
                continue
            denied_reasons = [dataclasses.asdict(r) for r in (decision.denied_reasons or ())]
            sizing = dataclasses.asdict(decision.sizing) if decision.sizing is not None else None
            blocking_position = None
            if any(r["code"] == "LIMIT_MAX_PER_SYMBOL" for r in denied_reasons):
                pos = self._current_positions.get(decision.symbol)  # type: ignore[attr-defined]
                if pos is not None:
                    blocking_position = {
                        "strategy_id": pos.strategy_id, "direction": pos.direction.value,
                        "opened_as_of": pos.opened_as_of, "avg_entry": pos.avg_entry,
                    }
            # NOTE: RiskDecision.direction is ALWAYS Direction.NONE for a DENIED decision by
            # construction (ai_trader/risk_manager/assembler.py assemble_decision(): direction is only
            # ever set to the real opportunity.direction on the ALLOW branch). For denied decisions we
            # must recover the real signal direction from the originating OpportunityScore captured in
            # the same batch instead, keyed by (strategy_id, symbol, as_of).
            real_direction = score_direction_by_key.get(
                (decision.strategy_id, decision.symbol, as_of), decision.direction.value,
            )
            self.decisions.append({
                "strategy_id": decision.strategy_id, "as_of": as_of, "symbol": decision.symbol,
                "direction": real_direction, "allowed": decision.decision.value == "ALLOW",
                "denied_reasons": denied_reasons, "sizing": sizing,
                "account_equity": getattr(portfolio_state, "equity", None),
                "blocking_position": blocking_position,
            })


def instrument_deep(harness: object, recorder: RootCauseRecorder) -> None:
    original_evaluate = harness._signal_engine.evaluate  # type: ignore[attr-defined]

    def wrapped_evaluate(ctx: object, handles: object, trader_state: object = None) -> object:
        batch = original_evaluate(ctx, handles, trader_state)
        recorder.record_signal_batch(batch.as_of, batch)
        return batch

    harness._signal_engine.evaluate = wrapped_evaluate  # type: ignore[attr-defined]

    original_score_batch = harness._scoring_engine.score_batch  # type: ignore[attr-defined]

    def wrapped_score_batch(signals: object) -> object:
        batch = original_score_batch(signals)
        recorder.record_score_batch(batch.as_of, batch)
        return batch

    harness._scoring_engine.score_batch = wrapped_score_batch  # type: ignore[attr-defined]

    original_risk_evaluate = harness._risk_manager.evaluate  # type: ignore[attr-defined]

    def wrapped_risk_evaluate(scores: object, risk_context: object, portfolio_state: object) -> object:
        recorder._current_positions = dict(harness.portfolio_simulator.account.positions)  # type: ignore[attr-defined]
        score_direction_by_key = {
            (s.strategy_id, s.symbol, s.as_of): s.direction.value
            for s in scores  # type: ignore[attr-defined]
            if s.strategy_id in TARGET_STRATEGIES
        }
        batch = original_risk_evaluate(scores, risk_context, portfolio_state)
        recorder.record_decision_batch(batch.as_of, batch, portfolio_state, score_direction_by_key)
        return batch

    harness._risk_manager.evaluate = wrapped_risk_evaluate  # type: ignore[attr-defined]


def run_instrumented_competitive() -> RootCauseRecorder:
    from ai_trader.simulation.types import RunState

    harness = new_harness("ROOTCAUSE-COMPETITIVE-INSTRUMENTED", strategy_id_filter=None)
    recorder = RootCauseRecorder()
    instrument_deep(harness, recorder)
    harness.run_to_completion()
    assert harness.state is RunState.COMPLETED, harness.fail_reason
    return recorder


# ============================================================================================
# Cross-reference against the already-saved isolated-scenario trade ledger (no re-simulation)
# ============================================================================================


def _load_isolated_trades() -> dict[str, list[dict[str, Any]]]:
    raw = json.loads((REPO_ROOT / "phase69a_isolated_funnel.json").read_text(encoding="utf-8"))
    return {sid: raw[sid]["trades"] for sid in raw}


_FILL_DELAY_SECONDS = 900  # one M15 bar: market orders fill at the NEXT bar's open, never the signal
# bar itself (ai_trader/simulation/execution_simulator.py; confirmed live by
# test_execution_simulator.py::test_market_order_fills_at_next_bar_open_not_signal_bar and by
# portfolio_simulator.py's own Position.opened_as_of = fill.as_of, itself the fill event's bar). A
# RiskDecision denied/allowed at bar T corresponds to a trade whose entry_as_of is T + 900, not T --
# matching directly on `as_of` without this offset silently finds almost no matches at all.


def _find_isolated_trade(isolated: dict[str, list[dict]], strategy_id: str, symbol: str, direction: str, as_of: int) -> dict | None:
    """Exact match only (entry_as_of == as_of + one bar's fill delay, same symbol/direction) -- no
    fuzzy/tolerance matching beyond the one documented, structural fill-delay offset, to avoid
    introducing an arbitrary, undisclosed matching rule. Reports the exact-match rate explicitly so any
    residual ambiguity is visible, not hidden."""
    target_entry_as_of = as_of + _FILL_DELAY_SECONDS
    for t in isolated.get(strategy_id, ()):
        if t["symbol"] == symbol and t["direction"] == direction and t["entry_as_of"] == target_entry_as_of:
            return t
    return None


# ============================================================================================
# Phase 1 -- complete funnel trace per target strategy
# ============================================================================================


def phase1_funnel_trace(recorder: RootCauseRecorder, isolated_funnel_raw: dict[str, Any], competitive_funnel_raw: dict[str, Any]) -> dict[str, Any]:
    """Stages 1-4 (setup/signal/eligibility/risk-request) reuse the already-saved, already-computed
    phase69a funnel counts directly (no re-derivation). Stages 5-11 (stop distance through verdict) are
    read from this study's own new event-level `recorder.scores`/`recorder.decisions`. Stage 12-13
    (execution/outcome) reuse the already-saved competitive trade ledger."""
    out: dict[str, Any] = {}
    for sid in TARGET_STRATEGIES:
        comp_f = {
            "signal_counts": competitive_funnel_raw["signal_counts"].get(sid, {}),
            "scoring_counts": competitive_funnel_raw["scoring_counts"].get(sid, {}),
            "risk_counts": competitive_funnel_raw["risk_counts"].get(sid, {}),
            "risk_deny_reasons": competitive_funnel_raw["risk_deny_reasons"].get(sid, {}),
            "order_counts": competitive_funnel_raw["order_counts"].get(sid, {}),
        }
        total_generated = sum(sum(m.values()) for m in comp_f["signal_counts"].values())
        actionable = sum(m.get("actionable", 0) for m in comp_f["signal_counts"].values())
        scored_actionable = sum(m.get("scored_actionable", 0) for m in comp_f["scoring_counts"].values())
        rejected_by_scoring = sum(m.get("rejected_by_scoring", 0) for m in comp_f["scoring_counts"].values())
        risk_allow = sum(m.get("allow", 0) for m in comp_f["risk_counts"].values())
        risk_deny = sum(m.get("deny", 0) for m in comp_f["risk_counts"].values())
        executed = comp_f["order_counts"].get("filled", 0)

        strategy_scores = [s for s in recorder.scores if s["strategy_id"] == sid]
        strategy_decisions = [d for d in recorder.decisions if d["strategy_id"] == sid]
        sized_events = [d for d in strategy_decisions if d["sizing"] is not None]
        allowed_events = [d for d in strategy_decisions if d["allowed"]]
        denied_events = [d for d in strategy_decisions if not d["allowed"]]

        out[sid] = {
            "stage_1_setup_detected": total_generated,
            "stage_2_signal_generated_actionable": actionable,
            "stage_3_eligibility_scored_actionable": scored_actionable,
            "stage_3_eligibility_rejected_by_scoring": rejected_by_scoring,
            "stage_4_risk_request_allow": risk_allow,
            "stage_4_risk_request_deny": risk_deny,
            "stage_5_9_sizing_events_reaching_sizing_stage": len(sized_events),
            "stage_10_final_verdict_allow": len(allowed_events),
            "stage_10_final_verdict_deny": len(denied_events),
            "stage_11_deny_reason_breakdown": dict(comp_f["risk_deny_reasons"]),
            "stage_12_executed": executed,
            "stage_13_outcome_available_in_isolated_lookup": True,
            "pct_setup_to_signal": (actionable / total_generated * 100.0) if total_generated else None,
            "pct_signal_to_scored": (scored_actionable / actionable * 100.0) if actionable else None,
            "pct_scored_to_allowed": (risk_allow / scored_actionable * 100.0) if scored_actionable else None,
            "pct_allowed_to_executed": (executed / risk_allow * 100.0) if risk_allow else None,
        }
    return out


# ============================================================================================
# Phase 2 -- BELOW_FLOOR / Recommendation-Floor root cause, for S40/S46/S48
# ============================================================================================

_WEAK_MIN = 25  # ai_trader/scoring_engine/config.py QualityBands/RecommendationBands.weak_min, read not invented
_ALLOWED_RECS = frozenset({"STRONG_OPPORTUNITY", "MODERATE_OPPORTUNITY", "WEAK_OPPORTUNITY"})


def _percentiles(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"p10": None, "p25": None, "median": None, "p75": None, "p90": None}
    s = sorted(values)

    def pct(p: float) -> float:
        idx = min(len(s) - 1, max(0, round(p * (len(s) - 1))))
        return s[idx]

    return {"p10": pct(0.10), "p25": pct(0.25), "median": statistics.median(s), "p75": pct(0.75), "p90": pct(0.90)}


def phase2_below_floor_analysis(recorder: RootCauseRecorder) -> dict[str, Any]:
    """Population: genuine BELOW_FLOOR RiskDecision denials only -- matched back to their originating
    OpportunityScore via (strategy_id, symbol, as_of) (no fill-delay offset here: score and risk
    decision are computed on the SAME bar, unlike a trade's later fill).

    NOTE: an earlier version of this function filtered `recorder.scores` directly on
    `recommendation not in _ALLOWED_RECS`, which silently counts EVERY non-actionable/no-signal score
    record too (the vast majority of the 23,639-bar window) -- exactly the "Rejected-by-scoring"
    population already reported separately in Table 1, not the much smaller genuine BELOW_FLOOR
    risk-manager denial count in Table 2 (e.g. S40: 21,268 vs. the real 376). Caught during this
    study's own sanity-check pass by cross-referencing against Table 2's independently-sourced
    deny-reason breakdown; corrected here to use the actual RiskDecision denial population."""
    score_by_key = {(s["strategy_id"], s["symbol"], s["as_of"]): s for s in recorder.scores}
    out: dict[str, Any] = {}
    for sid in BELOW_FLOOR_TARGETS:
        denials = [
            d for d in recorder.decisions if d["strategy_id"] == sid
            and any(r["code"] == "BELOW_FLOOR" for r in d["denied_reasons"])
        ]
        events = [
            score_by_key[(d["strategy_id"], d["symbol"], d["as_of"])] for d in denials
            if (d["strategy_id"], d["symbol"], d["as_of"]) in score_by_key
        ]
        n = len(events)
        base_qualities = [e["base_quality"] for e in events if e["base_quality"] is not None]
        conflict_penalties = [e["component_scores"]["conflict_penalty"] for e in events]
        total_scores = [float(e["total_score"]) for e in events]

        conflict_caused = 0
        weak_regardless = 0
        for e in events:
            cp = e["component_scores"]["conflict_penalty"]
            if cp <= 0.0 or e["base_quality"] is None:
                weak_regardless += 1
                continue
            rp = e["component_scores"]["risk_penalty"]
            counterfactual_score = round(100 * e["base_quality"] * (1.0 - rp) * (1.0 - 0.0))
            if counterfactual_score >= _WEAK_MIN:
                conflict_caused += 1
            else:
                weak_regardless += 1

        close_to_floor = sum(1 for ts in total_scores if _WEAK_MIN - 5 <= ts < _WEAK_MIN)
        far_below_floor = sum(1 for ts in total_scores if ts < _WEAK_MIN - 5)

        out[sid] = {
            "n_events_below_floor": n,
            "n_below_floor_denials_raw": len(denials),
            "base_quality_percentiles": _percentiles(base_qualities),
            "conflict_penalty_percentiles": _percentiles(conflict_penalties),
            "total_score_percentiles": _percentiles(total_scores),
            "n_conflict_caused_would_have_cleared_floor_without_conflict_penalty": conflict_caused,
            "pct_conflict_caused": (conflict_caused / n * 100.0) if n else None,
            "n_weak_regardless_of_conflict": weak_regardless,
            "pct_weak_regardless": (weak_regardless / n * 100.0) if n else None,
            "n_close_to_floor_within_5pts": close_to_floor,
            "pct_close_to_floor": (close_to_floor / n * 100.0) if n else None,
            "n_far_below_floor_more_than_5pts": far_below_floor,
            "pct_far_below_floor": (far_below_floor / n * 100.0) if n else None,
        }
    return out


def phase2_size_below_min_analysis(recorder: RootCauseRecorder) -> dict[str, Any]:
    """The genuinely distinct, real sizing-floor denial (SIZE_BELOW_MIN) -- reported for completeness
    even though not the CEO's own named target, since it's the ACTUAL sizing gate.

    NOTE: `decision.sizing` is ALWAYS None on this denial by construction (`ai_trader/risk_manager/
    sizing.py::compute_sizing` returns `SizingOutcome(False, deny_reason=...)` with `sizing=None` when
    `size_units < min_size_units` -- the `Sizing` object is only ever built on the success branch). The
    raw computed size and the minimum it was compared against are instead carried on the `DeniedReason`
    itself as `observed`/`limit` (`pipeline.py` line ~145, passing straight through `sizing.py` lines
    83-87). Reading `d["sizing"]` here would silently find zero events for every strategy despite
    Table 2 showing real SIZE_BELOW_MIN counts -- this reads `observed`/`limit` off the matching
    `DeniedReason` entry instead."""
    out: dict[str, Any] = {}
    for sid in TARGET_STRATEGIES:
        events = [
            d for d in recorder.decisions if d["strategy_id"] == sid
            and any(r["code"] == "SIZE_BELOW_MIN" for r in d["denied_reasons"])
        ]
        size_below_min_reasons = [
            next(r for r in d["denied_reasons"] if r["code"] == "SIZE_BELOW_MIN") for d in events
        ]
        sizes = [r["observed"] for r in size_below_min_reasons if r["observed"] is not None]
        mins = [r["limit"] for r in size_below_min_reasons if r["limit"] is not None]
        out[sid] = {
            "n_events": len(events),
            "raw_size_units_percentiles": _percentiles(sizes),
            "min_size_percentiles": _percentiles(mins),
        }
    return out


# ============================================================================================
# Phase 3 -- LIMIT_MAX_PER_SYMBOL episode-level root cause, for S1/S13/S39
# ============================================================================================


def _collapse_denial_episodes(events: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Collapses consecutive (<=900s gap, same symbol+direction) LIMIT_MAX_PER_SYMBOL denial EVENTS
    for one strategy into episodes -- a persistent blocked setup denied on many consecutive bars is
    ONE lost opportunity, not N. Mirrors the same "maximal contiguous run" convention this session's
    own Context Memory Checkpoint 11 already established for episode collapsing -- reused, not
    reinvented, for internal consistency."""
    events = sorted(events, key=lambda e: e["as_of"])
    episodes: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for e in events:
        if current and (
            e["symbol"] != current[-1]["symbol"] or e["direction"] != current[-1]["direction"]
            or e["as_of"] - current[-1]["as_of"] > 900
        ):
            episodes.append(current)
            current = []
        current.append(e)
    if current:
        episodes.append(current)
    return episodes


def phase3_shared_slot_analysis(recorder: RootCauseRecorder, isolated_trades: dict[str, list[dict]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for sid in SHARED_SLOT_TARGETS:
        events = [
            d for d in recorder.decisions if d["strategy_id"] == sid
            and any(r["code"] == "LIMIT_MAX_PER_SYMBOL" for r in d["denied_reasons"])
        ]
        episodes = _collapse_denial_episodes(events)

        episode_records = []
        for ep in episodes:
            first = ep[0]
            blocking = first["blocking_position"]
            isolated_match = _find_isolated_trade(isolated_trades, sid, first["symbol"], first["direction"], first["as_of"])
            same_direction = (blocking is not None and blocking["direction"] == first["direction"])
            overlap_seconds = (first["as_of"] - blocking["opened_as_of"]) if blocking is not None else None
            episode_records.append({
                "first_as_of": first["as_of"], "last_as_of": ep[-1]["as_of"], "n_bars_blocked": len(ep),
                "symbol": first["symbol"], "new_signal_direction": first["direction"],
                "blocking_strategy_id": blocking["strategy_id"] if blocking else None,
                "blocking_direction": blocking["direction"] if blocking else None,
                "blocking_opened_as_of": blocking["opened_as_of"] if blocking else None,
                "same_direction_as_blocking": same_direction,
                "overlap_seconds_since_blocking_position_opened": overlap_seconds,
                "isolated_match_found": isolated_match is not None,
                "isolated_net_pnl": isolated_match["net_pnl"] if isolated_match else None,
                "isolated_pnl_r": isolated_match["pnl_r"] if isolated_match else None,
            })

        matched = [r for r in episode_records if r["isolated_match_found"]]
        profitable = [r for r in matched if r["isolated_net_pnl"] > 0]
        losing = [r for r in matched if r["isolated_net_pnl"] <= 0]
        r_values = [r["isolated_pnl_r"] for r in matched if r["isolated_pnl_r"] is not None]
        gross_win = sum(r["isolated_net_pnl"] for r in profitable)
        gross_loss = -sum(r["isolated_net_pnl"] for r in losing)
        same_dir_count = sum(1 for r in episode_records if r["same_direction_as_blocking"])
        opp_dir_count = sum(1 for r in episode_records if r["blocking_strategy_id"] is not None and not r["same_direction_as_blocking"])

        out[sid] = {
            "n_denial_events_raw": len(events),
            "n_blocked_opportunity_episodes": len(episode_records),
            "n_matched_to_isolated_trade": len(matched),
            "match_rate_pct": (len(matched) / len(episode_records) * 100.0) if episode_records else None,
            "n_same_direction_as_blocking_position": same_dir_count,
            "n_opposite_direction_from_blocking_position": opp_dir_count,
            "n_blocked_profitable_in_isolated": len(profitable),
            "n_blocked_losing_in_isolated": len(losing),
            "expectancy_r_of_blocked_matched": statistics.fmean(r_values) if r_values else None,
            "profit_factor_of_blocked_matched": (gross_win / gross_loss) if gross_loss > 0 else None,
            "total_isolated_r_of_blocked_matched": sum(r_values) if r_values else None,
            "net_isolated_pnl_of_blocked_matched": sum(r["isolated_net_pnl"] for r in matched),
            "episodes": episode_records,
        }
    return out


# ============================================================================================
# Phase 4 -- quality control (documented, not re-derived where already proven in prior studies)
# ============================================================================================


def phase4_quality_control() -> dict[str, Any]:
    import subprocess

    git_status = subprocess.run(
        ["git", "status", "--porcelain", "--", "ai_trader/"], cwd=REPO_ROOT, capture_output=True, text=True,
    ).stdout
    return {
        "same_historical_data": "Reuses new_harness() from phase69a_funnel_run.py verbatim -- identical SimulationContext/RiskConfig/DATA_DIR/window as the paired isolated/competitive dataset.",
        "same_timestamps": "WINDOW_START/WINDOW_END imported unchanged from phase69a_funnel_run.py.",
        "same_strategy_version": "use_strategy_runtime=True, no override -- same Strategy Library both scenarios.",
        "same_settlement": "Same RiskConfig/cost model/fill model as the original paired dataset (see CEO_STRATEGY_PERFORMANCE_STUDY_REPORT.md sec1 items 1-5).",
        "zero_future_leakage": "Same unmodified SimulationHarness/MarketScanner/ReplayDataSource pipeline; context_access's own lookahead-safety guarantee applies unchanged.",
        "zero_ai_trader_changes": git_status.strip() == "",
        "ai_trader_git_status": git_status,
        "all_values_from_existing_infrastructure": "Every field captured (OpportunityScore/RiskDecision/Sizing/Position) is read directly off already-existing dataclasses returned by unmodified ai_trader/ functions -- no new statistical method introduced; only percentiles/means/ratios computed via stdlib.",
    }


# ============================================================================================
# Phase 5 -- verdict per strategy
# ============================================================================================


class Verdict(str, enum.Enum):
    STRATEGY_LIMITED = "STRATEGY-LIMITED"
    SIZING_LIMITED = "SIZING-LIMITED"
    PORTFOLIO_LIMITED = "PORTFOLIO-LIMITED"
    MIXED_CONSTRAINT = "MIXED-CONSTRAINT"
    INCONCLUSIVE = "INCONCLUSIVE"


def phase5_verdicts(phase2: dict[str, Any], phase3: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}

    for sid in BELOW_FLOOR_TARGETS:
        p2 = phase2[sid]
        n = p2["n_events_below_floor"]
        pct_conflict = p2["pct_conflict_caused"]
        if n == 0:
            out[sid] = {
                "verdict": Verdict.INCONCLUSIVE.value, "dominant_cause": "no BELOW_FLOOR events found",
                "secondary_cause": "n/a", "n_cases": 0, "trade_count_impact": 0, "realized_r_impact": None,
                "confidence": "LOW -- no events to analyze",
            }
            continue
        dominant = (
            f"portfolio-conflict-penalty (Scoring Engine conflict_penalty, batch-wide cross-strategy) -- "
            f"{pct_conflict:.1f}% of BELOW_FLOOR events would have cleared the recommendation floor "
            f"without it"
        ) if pct_conflict is not None and pct_conflict >= 50.0 else (
            f"intrinsically weak signal quality (base_quality itself insufficient regardless of "
            f"competition) -- only {pct_conflict:.1f}% of events are conflict-penalty-caused" if pct_conflict is not None else "inconclusive"
        )
        verdict = Verdict.PORTFOLIO_LIMITED if (pct_conflict is not None and pct_conflict >= 50.0) else Verdict.STRATEGY_LIMITED
        confidence = "HIGH" if n >= 25 else ("MEDIUM" if n >= 10 else "LOW -- small sample")
        out[sid] = {
            "verdict": verdict.value, "dominant_cause": dominant,
            "secondary_cause": "SIZE_BELOW_MIN sizing-floor denials (see Phase 2 SIZE_BELOW_MIN table, a distinct, real sizing gate)",
            "n_cases": n, "trade_count_impact": n, "realized_r_impact": "n/a (BELOW_FLOOR events never reach sizing/execution -- no realized R exists for them by construction)",
            "confidence": confidence,
        }

    for sid in SHARED_SLOT_TARGETS:
        p3 = phase3[sid]
        n = p3["n_blocked_opportunity_episodes"]
        er = p3["expectancy_r_of_blocked_matched"]
        matched = p3["n_matched_to_isolated_trade"]
        if n == 0 or matched == 0:
            out[sid] = {
                "verdict": Verdict.INCONCLUSIVE.value, "dominant_cause": "no matched blocked episodes",
                "secondary_cause": "n/a", "n_cases": n, "trade_count_impact": n, "realized_r_impact": None,
                "confidence": "LOW -- insufficient matched data",
            }
            continue
        profitable_share = p3["n_blocked_profitable_in_isolated"] / matched if matched else None
        dominant = (
            f"shared-slot rule (LIMIT_MAX_PER_SYMBOL) blocked {n} distinct opportunity episode(s), "
            f"{matched} matched to an isolated-scenario outcome, {profitable_share:.1%} of which were "
            f"profitable in isolation (expectancy_R={er:.3f}), "
            f"total isolated R foregone = {p3['total_isolated_r_of_blocked_matched']}"
        ) if er is not None else "shared-slot rule blocked opportunities but matched-sample too thin for a reliable expectancy read"
        confidence = "HIGH" if matched >= 25 else ("MEDIUM" if matched >= 10 else "LOW -- small matched sample")
        out[sid] = {
            "verdict": Verdict.PORTFOLIO_LIMITED.value, "dominant_cause": dominant,
            "secondary_cause": "some episodes also show non-shared-slot denial growth (see the original study's own principal-loss-reason table)",
            "n_cases": n, "trade_count_impact": n, "realized_r_impact": p3["total_isolated_r_of_blocked_matched"],
            "confidence": confidence,
        }
    return out


# ============================================================================================
# Serialization + table generation
# ============================================================================================


def _jsonify(obj: Any) -> Any:
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {k: _jsonify(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, enum.Enum):
        return obj.value
    if isinstance(obj, dict):
        return {str(k): _jsonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonify(v) for v in obj]
    return obj


def _num(x: float | None, digits: int = 3) -> str:
    return "n/a" if x is None else f"{x:.{digits}f}"


def _pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x:.1f}%"


def generate_tables(result: dict[str, Any]) -> str:
    out: list[str] = []

    out.append("## Table 1: Complete funnel trace per strategy (13 stages)\n")
    out.append("| Strategy | Setup | Signal(actionable) | Scored-actionable | Rejected-by-scoring | Risk-allow | Risk-deny | Reached-sizing | Final-allow | Final-deny | Executed | %setup->signal | %signal->scored | %scored->allowed | %allowed->executed |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for sid in TARGET_STRATEGIES:
        f = result["phase1"][sid]
        out.append(
            f"| {sid} | {f['stage_1_setup_detected']} | {f['stage_2_signal_generated_actionable']} | "
            f"{f['stage_3_eligibility_scored_actionable']} | {f['stage_3_eligibility_rejected_by_scoring']} | "
            f"{f['stage_4_risk_request_allow']} | {f['stage_4_risk_request_deny']} | "
            f"{f['stage_5_9_sizing_events_reaching_sizing_stage']} | {f['stage_10_final_verdict_allow']} | "
            f"{f['stage_10_final_verdict_deny']} | {f['stage_12_executed']} | "
            f"{_pct(f['pct_setup_to_signal'])} | {_pct(f['pct_signal_to_scored'])} | "
            f"{_pct(f['pct_scored_to_allowed'])} | {_pct(f['pct_allowed_to_executed'])} |"
        )

    out.append("\n## Table 2: Deny-reason breakdown per strategy (competitive scenario)\n")
    out.append("| Strategy | Deny reasons (code: count) |")
    out.append("|---|---|")
    for sid in TARGET_STRATEGIES:
        breakdown = result["phase1"][sid]["stage_11_deny_reason_breakdown"]
        out.append(f"| {sid} | {', '.join(f'{k}={v}' for k, v in sorted(breakdown.items()))} |")

    out.append("\n## Table 3: BELOW_FLOOR (Recommendation-Floor) root cause -- S40/S46/S48\n")
    out.append("| Strategy | n events | base_quality p10/p25/median/p75/p90 | conflict_penalty p10/p25/median/p75/p90 | total_score p10/p25/median/p75/p90 | %conflict-caused | %weak-regardless | %close-to-floor(<5pt) | %far-below-floor |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for sid in BELOW_FLOOR_TARGETS:
        p = result["phase2"][sid]
        bq, cp, ts = p["base_quality_percentiles"], p["conflict_penalty_percentiles"], p["total_score_percentiles"]
        out.append(
            f"| {sid} | {p['n_events_below_floor']} | "
            f"{_num(bq['p10'])}/{_num(bq['p25'])}/{_num(bq['median'])}/{_num(bq['p75'])}/{_num(bq['p90'])} | "
            f"{_num(cp['p10'])}/{_num(cp['p25'])}/{_num(cp['median'])}/{_num(cp['p75'])}/{_num(cp['p90'])} | "
            f"{_num(ts['p10'],1)}/{_num(ts['p25'],1)}/{_num(ts['median'],1)}/{_num(ts['p75'],1)}/{_num(ts['p90'],1)} | "
            f"{_pct(p['pct_conflict_caused'])} | {_pct(p['pct_weak_regardless'])} | "
            f"{_pct(p['pct_close_to_floor'])} | {_pct(p['pct_far_below_floor'])} |"
        )

    out.append("\n## Table 3b: SIZE_BELOW_MIN (the genuine sizing-floor gate) -- all six target strategies\n")
    out.append("| Strategy | n events | raw size_units p10/median/p90 | min_size p10/median/p90 |")
    out.append("|---|---|---|---|")
    for sid in TARGET_STRATEGIES:
        p = result["phase2_sizing"][sid]
        s, m = p["raw_size_units_percentiles"], p["min_size_percentiles"]
        out.append(f"| {sid} | {p['n_events']} | {_num(s['p10'])}/{_num(s['median'])}/{_num(s['p90'])} | {_num(m['p10'])}/{_num(m['median'])}/{_num(m['p90'])} |")

    out.append("\n## Table 4: LIMIT_MAX_PER_SYMBOL root cause -- S1/S13/S39\n")
    out.append("| Strategy | raw denial events | blocked episodes | matched to isolated | match rate | same-dir as blocker | opp-dir from blocker | profitable in isolated | losing in isolated | expectancy_R (matched) | PF (matched) | total isolated R foregone |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for sid in SHARED_SLOT_TARGETS:
        p = result["phase3"][sid]
        out.append(
            f"| {sid} | {p['n_denial_events_raw']} | {p['n_blocked_opportunity_episodes']} | "
            f"{p['n_matched_to_isolated_trade']} | {_pct(p['match_rate_pct'])} | "
            f"{p['n_same_direction_as_blocking_position']} | {p['n_opposite_direction_from_blocking_position']} | "
            f"{p['n_blocked_profitable_in_isolated']} | {p['n_blocked_losing_in_isolated']} | "
            f"{_num(p['expectancy_r_of_blocked_matched'])} | {_num(p['profit_factor_of_blocked_matched'], 2)} | "
            f"{_num(p['total_isolated_r_of_blocked_matched'], 2)} |"
        )

    out.append("\n## Table 5: LIMIT_MAX_PER_SYMBOL -- full episode detail (S1/S13/S39)\n")
    out.append("| Strategy | first_as_of | n_bars | direction | blocking_strategy | blocking_dir | same_dir | overlap_s | isolated_match | isolated_net_pnl | isolated_R |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for sid in SHARED_SLOT_TARGETS:
        for ep in result["phase3"][sid]["episodes"]:
            out.append(
                f"| {sid} | {ep['first_as_of']} | {ep['n_bars_blocked']} | {ep['new_signal_direction']} | "
                f"{ep['blocking_strategy_id']} | {ep['blocking_direction']} | {ep['same_direction_as_blocking']} | "
                f"{ep['overlap_seconds_since_blocking_position_opened']} | {ep['isolated_match_found']} | "
                f"{_num(ep['isolated_net_pnl'], 2)} | {_num(ep['isolated_pnl_r'])} |"
            )

    out.append("\n## Table 6: Verdict per strategy\n")
    out.append("| Strategy | Verdict | Dominant cause | Secondary cause | n cases | Trade-count impact | Realized-R impact | Confidence |")
    out.append("|---|---|---|---|---|---|---|---|")
    for sid in TARGET_STRATEGIES:
        v = result["phase5"][sid]
        out.append(
            f"| {sid} | {v['verdict']} | {v['dominant_cause']} | {v['secondary_cause']} | "
            f"{v['n_cases']} | {v['trade_count_impact']} | {v['realized_r_impact']} | {v['confidence']} |"
        )

    return "\n".join(out)


# ============================================================================================
# Orchestration
# ============================================================================================


def main() -> dict[str, Any]:
    isolated_funnel_raw = json.loads((REPO_ROOT / "phase69a_isolated_funnel.json").read_text(encoding="utf-8"))
    competitive_funnel_raw = json.loads((REPO_ROOT / "phase69a_competitive_funnel.json").read_text(encoding="utf-8"))
    isolated_trades = _load_isolated_trades()

    recorder = run_instrumented_competitive()

    phase1 = phase1_funnel_trace(recorder, isolated_funnel_raw, competitive_funnel_raw)
    phase2 = phase2_below_floor_analysis(recorder)
    phase2_sizing = phase2_size_below_min_analysis(recorder)
    phase3 = phase3_shared_slot_analysis(recorder, isolated_trades)
    phase4 = phase4_quality_control()
    phase5 = phase5_verdicts(phase2, phase3)

    return {
        "target_strategies": list(TARGET_STRATEGIES),
        "below_floor_targets": list(BELOW_FLOOR_TARGETS),
        "shared_slot_targets": list(SHARED_SLOT_TARGETS),
        "phase1": phase1,
        "phase2": phase2,
        "phase2_sizing": phase2_sizing,
        "phase3": phase3,
        "phase4": phase4,
        "phase5": phase5,
        "raw_scores_count": len(recorder.scores),
        "raw_decisions_count": len(recorder.decisions),
    }


if __name__ == "__main__":
    result = main()
    print(f"Raw scores captured: {result['raw_scores_count']}")
    print(f"Raw decisions captured: {result['raw_decisions_count']}")
    print(f"ai_trader/ git status empty: {result['phase4']['zero_ai_trader_changes']}")

    data_path = REPO_ROOT / "ceo_strategy_constraint_root_cause_data.json"
    data_json = json.dumps(_jsonify(result), indent=2, sort_keys=True)
    data_path.write_text(data_json, encoding="utf-8")
    print(f"Full data dumped to {data_path}")

    tables_path = REPO_ROOT / "ceo_strategy_constraint_root_cause_tables.md"
    tables_path.write_text(generate_tables(result) + "\n", encoding="utf-8")
    print(f"Tables written to {tables_path}")

    import hashlib
    print(f"data.json sha256: {hashlib.sha256(data_json.encode('utf-8')).hexdigest()}")
