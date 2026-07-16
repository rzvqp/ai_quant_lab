"""Phase 6.9 -- additional analysis over `phase69_results.json`'s checkpoint history (CEO's
"Additional Analysis" + "Required Output" requests not already produced directly by
`performance_analyzer.analyze()`). SCRATCH script (same precedent as `phase69_rolling_backtest.py`):
run once, results folded into the validation report, then deleted."""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
TREND_STRONG = 15.0


def main() -> None:
    data = json.loads((REPO_ROOT / "phase69_results.json").read_text(encoding="utf-8"))
    checkpoints = data["checkpoints"]
    all_ids = sorted(checkpoints[0]["states"])
    n_checkpoints = len(checkpoints)

    # ---- average ACTIVE count per checkpoint
    active_counts = [len(c["active_ids"]) for c in checkpoints]
    avg_active = statistics.fmean(active_counts)

    # ---- per-strategy state sequences
    state_seq: dict[str, list[str]] = {sid: [c["states"][sid] for c in checkpoints] for sid in all_ids}

    # ---- promotions / demotions (transitions between CONSECUTIVE checkpoints only)
    promotions = 0
    demotions = 0
    promotions_by_checkpoint = []
    demotions_by_checkpoint = []
    for i in range(1, n_checkpoints):
        promo = 0
        demo = 0
        for sid in all_ids:
            prev, cur = state_seq[sid][i - 1], state_seq[sid][i]
            if prev != "ACTIVE" and cur == "ACTIVE":
                promo += 1
            elif prev == "ACTIVE" and cur != "ACTIVE":
                demo += 1
        promotions += promo
        demotions += demo
        promotions_by_checkpoint.append(promo)
        demotions_by_checkpoint.append(demo)

    # ---- ACTIVE turnover per transition: |symmetric difference| / checkpoint count, averaged
    turnovers = []
    for i in range(1, n_checkpoints):
        prev_set = set(checkpoints[i - 1]["active_ids"])
        cur_set = set(checkpoints[i]["active_ids"])
        sym_diff = len(prev_set ^ cur_set)
        turnovers.append(sym_diff)
    avg_turnover_per_checkpoint = statistics.fmean(turnovers) if turnovers else 0.0

    # ---- checkpoints where the roster actually changed at all (event-level regime shifts)
    roster_change_checkpoints = sum(1 for t in turnovers if t > 0)

    # ---- average ACTIVE lifetime: consecutive-checkpoint run lengths (in periods), across all strategies
    lifetimes_periods = []
    for sid in all_ids:
        run = 0
        for state in state_seq[sid]:
            if state == "ACTIVE":
                run += 1
            else:
                if run > 0:
                    lifetimes_periods.append(run)
                run = 0
        if run > 0:
            lifetimes_periods.append(run)
    avg_lifetime_periods = statistics.fmean(lifetimes_periods) if lifetimes_periods else 0.0
    checkpoint_interval_days = data["config"]["checkpoint_interval_days"]

    # ---- time spent ACTIVE per strategy (ranked)
    time_active = {sid: sum(1 for s in state_seq[sid] if s == "ACTIVE") for sid in all_ids}
    most_active = sorted(time_active.items(), key=lambda kv: -kv[1])[:10]

    # ---- oscillation: number of state transitions (any state -> different state) per strategy
    transitions = {}
    for sid in all_ids:
        seq = state_seq[sid]
        transitions[sid] = sum(1 for i in range(1, len(seq)) if seq[i] != seq[i - 1])
    most_oscillating = sorted(transitions.items(), key=lambda kv: -kv[1])[:10]

    # ---- regime-adaptation trend-rule signal count (|trend_delta| >= 15, the classifier's own bump
    # threshold) -- a proxy for "regime change detected" at the per-strategy level, distinct from the
    # roster-level "did the ACTIVE set change" count above.
    trend_signal_count = 0
    strong_up = 0
    strong_down = 0
    for c in checkpoints:
        for sid in all_ids:
            td = c["trend_deltas"].get(sid)
            if td is None:
                continue
            if td >= TREND_STRONG:
                trend_signal_count += 1
                strong_up += 1
            elif td <= -TREND_STRONG:
                trend_signal_count += 1
                strong_down += 1

    # ---- sample-size robustness: 12m-window confidence (credibility weight) behind every ACTIVE
    # classification actually made (confidence=1 needs >=~90 trades at k=10 given credibility_weight
    # = n/(n+10); confidence=0.5 means n=10 trades)
    active_confidences = []
    for c in checkpoints:
        for sid in c["active_ids"]:
            active_confidences.append(c["confidences_12m"][sid])
    all_confidences = [c["confidences_12m"][sid] for c in checkpoints for sid in all_ids]

    summary = {
        "n_checkpoints": n_checkpoints,
        "checkpoint_interval_days": checkpoint_interval_days,
        "first_checkpoint": checkpoints[0]["date"],
        "last_checkpoint": checkpoints[-1]["date"],
        "avg_active_count": avg_active,
        "active_count_by_checkpoint": active_counts,
        "total_promotions": promotions,
        "total_demotions": demotions,
        "promotions_by_checkpoint": promotions_by_checkpoint,
        "demotions_by_checkpoint": demotions_by_checkpoint,
        "avg_turnover_per_checkpoint_transition": avg_turnover_per_checkpoint,
        "checkpoints_with_any_roster_change": roster_change_checkpoints,
        "checkpoints_with_any_roster_change_pct": roster_change_checkpoints / (n_checkpoints - 1) * 100.0,
        "avg_active_lifetime_periods": avg_lifetime_periods,
        "avg_active_lifetime_days": avg_lifetime_periods * checkpoint_interval_days,
        "n_active_spells_total": len(lifetimes_periods),
        "most_time_active_top10": most_active,
        "most_oscillating_top10": most_oscillating,
        "trend_signal_strong_up_count": strong_up,
        "trend_signal_strong_down_count": strong_down,
        "trend_signal_total_count": trend_signal_count,
        "active_decision_confidence_mean": statistics.fmean(active_confidences) if active_confidences else None,
        "active_decision_confidence_median": statistics.median(active_confidences) if active_confidences else None,
        "active_decision_confidence_min": min(active_confidences) if active_confidences else None,
        "all_decision_confidence_mean": statistics.fmean(all_confidences) if all_confidences else None,
        "active_decisions_with_confidence_below_0_5": sum(1 for c in active_confidences if c < 0.5),
        "active_decisions_total": len(active_confidences),
    }

    out_path = REPO_ROOT / "phase69_analysis.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
