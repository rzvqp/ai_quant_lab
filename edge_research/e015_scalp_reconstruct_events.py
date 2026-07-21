"""E015-SCALP Phase 0 -- reconstructs the exact E015 detector (unchanged) and dumps the visit-1
("first mitigation") event population with real UTC timestamps, then selects a pilot sample using a
pre-registered, outcome-blind rule. This script does NOT alter e015_order_block_remitigation.py or its
own results; it re-runs the identical, frozen detector (same PRIMARY_DISP=1.5, same OB construction) to
recover per-event timestamps that were not persisted to a CSV in the original pass.

Pilot sample-selection rule (frozen BEFORE any TradingView replay, disclosed here verbatim):
1. Population = all visit-1 (first mitigation) events on M15, clean split, both directions pooled.
2. Stratify by (ob_polarity, session) so the pilot spans both directions and multiple sessions.
3. Within each non-empty stratum, pick events using a fixed seed (42, same convention as every other
   edge this program) -- NOT the "cleanest-looking" or highest/lowest-reaction event; the outcome
   (continuation/reversal/stall, mp fields) is explicitly NOT used as a selection criterion.
4. Cap at 5 events for this Phase 0 workflow-feasibility pilot (smaller than the CEO's own recommended
   10-20 -- disclosed scope reduction for this pass, given the per-event cost of manual candle-by-candle
   TradingView replay; intended as a first feasibility check, extendable by a future session if the
   Phase 0 verdict is FEASIBLE or FEASIBLE WITH LIMITATIONS).
"""
import json
import numpy as np
from _common import load, vol_regime, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
import _profile as P
from e015_order_block_remitigation import detect_obs, visits_for_ob, PRIMARY_DISP

SEED = 42
CAP = 5


def main():
    m, meta = load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    m["vol_regime"] = vol_regime(m)

    obs = detect_obs(m, PRIMARY_DISP)
    events = []
    for ob in obs:
        visits = visits_for_ob(m, ob)
        if not visits:
            continue
        v1_idx = visits[0]
        ctx = P.context_features(m, v1_idx)
        events.append(dict(
            ob_idx=ob["ob_idx"], ob_low=ob["ob_low"], ob_high=ob["ob_high"],
            ob_polarity=ob["ob_polarity"], disp_idx=ob["disp_idx"],
            visit1_idx=int(v1_idx), visit1_time_unix=int(m["time"].iloc[v1_idx]),
            visit1_dt_utc=str(m["dt"].iloc[v1_idx]),
            ob_formed_dt_utc=str(m["dt"].iloc[ob["ob_idx"]]),
            session=ctx["session"], dow=ctx["dow"], trend=ctx["trend"],
            vol_regime=str(m["vol_regime"].iloc[v1_idx]),
            year=int(m["dt"].iloc[v1_idx].year),
        ))

    print("total visit-1 events:", len(events))

    strata = {}
    for e in events:
        key = (e["ob_polarity"], e["session"])
        strata.setdefault(key, []).append(e)
    print("strata sizes:", {k: len(v) for k, v in strata.items()})

    rng = np.random.default_rng(SEED)
    keys = sorted(strata.keys())
    picked = []
    i = 0
    while len(picked) < CAP and any(strata[k] for k in keys):
        k = keys[i % len(keys)]
        pool = strata[k]
        if pool:
            idx = rng.integers(0, len(pool))
            picked.append(pool.pop(idx))
        i += 1

    picked.sort(key=lambda e: e["visit1_idx"])

    with open("e015_scalp_all_visit1_events.json", "w") as f:
        json.dump(events, f, indent=2, default=str)
    with open("e015_scalp_pilot_sample.json", "w") as f:
        json.dump(dict(seed=SEED, cap=CAP, selection_rule="stratified by (ob_polarity, session), "
                        "outcome-blind, fixed seed", pilot_events=picked), f, indent=2, default=str)

    print("\nPilot sample (n=%d):" % len(picked))
    for e in picked:
        print(f"  {e['ob_polarity']:4s} {e['session']:7s} {e['visit1_dt_utc']} "
              f"OB=[{e['ob_low']:.2f},{e['ob_high']:.2f}] formed={e['ob_formed_dt_utc']}")


if __name__ == "__main__":
    main()
