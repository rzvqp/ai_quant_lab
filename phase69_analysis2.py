"""Phase 6.9 -- second analysis pass: per-checkpoint state-count tables, the zero-evidence timeline,
and n_trades reconstruction from stored 12m credibility weights (n = conf*10/(1-conf), inverting
`credibility_weight(n) = n/(n+10)`). SCRATCH script, same precedent as the other phase69_*.py files."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def n_trades_from_confidence(conf: float) -> float:
    if conf >= 1.0:
        return float("inf")
    return conf * 10.0 / (1.0 - conf)


def main() -> None:
    data = json.loads((REPO_ROOT / "phase69_results.json").read_text(encoding="utf-8"))
    checkpoints = data["checkpoints"]
    all_ids = sorted(checkpoints[0]["states"])

    print("=== per-checkpoint state counts ===")
    state_count_rows = []
    for c in checkpoints:
        counts = {"ACTIVE": 0, "WATCHLIST": 0, "PROBATION": 0, "DISABLED": 0}
        for sid in all_ids:
            counts[c["states"][sid]] += 1
        zero_evidence = sum(1 for sid in all_ids if c["overall_scores"][sid] is None)
        row = {"date": c["date"], **counts, "zero_evidence_strategies": zero_evidence}
        state_count_rows.append(row)
        print(row)

    # first checkpoint where EVERY strategy has zero evidence in all 3 windows
    first_all_zero = next((r for r in state_count_rows if r["zero_evidence_strategies"] == len(all_ids)), None)
    print()
    print("first checkpoint where ALL 43 strategies have zero evidence in every window:", first_all_zero)

    # n_trades_12m reconstruction at the FIRST post-bootstrap checkpoint (most evidence available of
    # any post-bootstrap checkpoint, since trades haven't yet aged out of the 12m window)
    first_cp = checkpoints[0]
    n_trades_12m = {
        sid: n_trades_from_confidence(first_cp["confidences_12m"][sid]) for sid in all_ids
    }
    nonzero = sorted(((sid, n) for sid, n in n_trades_12m.items() if n > 0), key=lambda kv: -kv[1])
    print()
    print(f"=== n_trades in the 12-month window AT THE FIRST CHECKPOINT ({first_cp['date']}) ===")
    print(f"strategies with >0 trades in the 12m window: {len(nonzero)} / {len(all_ids)}")
    for sid, n in nonzero:
        print(f"  {sid}: {n:.0f} trades (12m window)")
    print(f"strategies with a 12m score >= 65 (ACTIVE band) at this checkpoint: "
          f"{sum(1 for sid in all_ids if (first_cp['overall_scores'][sid] or 0) >= 65)}")

    out = {
        "state_count_by_checkpoint": state_count_rows,
        "first_all_zero_evidence_checkpoint": first_all_zero,
        "n_trades_12m_at_first_checkpoint": n_trades_12m,
    }
    (REPO_ROOT / "phase69_analysis2.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\nWrote phase69_analysis2.json")


if __name__ == "__main__":
    main()
