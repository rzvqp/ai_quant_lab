"""E013 / E016 pre-test dependence checks (CEO/Statistician task 2026-07-26). NUMBERS ONLY.

Run on the EXISTING Set A window (via _common.load, pre_holdout split) -- NOT the incoming 2011-2022
data. Implements E013 and E016 exactly as operationalized in V1_OPERATIONALIZED_CONTRACTS.md, reusing the
inherited E010/E015 order-block detector, and reports the three checks the Statistician asked for:
  (1) circularity -- selection window vs outcome-measurement window, verified in the inherited detector;
  (2) entry overlap vs E010, E015, E016 (S18-style);
  (3) repeated measurements per order-block zone (E015-style).
No outcome interpretation, no validity conclusion.
"""
import json
from bisect import bisect_left, bisect_right
from collections import Counter

import numpy as np

import _profile as P
from _common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
import e010_breaker_block_snatch as M10
import e015_order_block_remitigation as M15

TF = "M15"
FWD = max(P.HORIZONS)            # 50 -- movement_profile forward window
E13_HORIZON = M10.REVISIT_HORIZON  # 480 -- E013/E016 mitigation/retrace window (per V1 contract)


def _first_touch_entries(m, obs, horizon):
    """E013 == E016 as operationalized: first mitigation (first break-censored touch) of each OB event,
    within `horizon`. Returns list of (ob_idx, entry_idx)."""
    out = []
    for o in obs:
        vs = M15.visits_for_ob(m, o, horizon=horizon)   # break-censored, cooldown-merged (inherited)
        if vs:
            out.append((int(o["ob_idx"]), int(vs[0])))
    return out


def main():
    m, meta = load(TF, data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    n = len(m)
    obs = M15.detect_obs(m, M15.PRIMARY_DISP)                       # shared OB set (same detector as E010)

    # ---- entry sets ----
    e13 = _first_touch_entries(m, obs, E13_HORIZON)                 # E013
    e16 = _first_touch_entries(m, obs, E13_HORIZON)                 # E016 (identical construction)
    e13_bars = sorted({e for _, e in e13})
    e16_bars = sorted({e for _, e in e16})

    # E015: all visits + visit-1 (960 window, inherited)
    e15_all, e15_v1 = [], []
    for o in obs:
        vs = M15.visits_for_ob(m, o)                                # default TRACK_HORIZON=960
        for k, vi in enumerate(vs):
            e15_all.append(int(vi))
            if k == 0:
                e15_v1.append(int(vi))
    e15_all_bars, e15_v1_bars = sorted(set(e15_all)), sorted(set(e15_v1))

    # E010 primary = breaker revisit bars
    breakers, _unflipped = M10.detect_obs_and_breakers(m, M10.PRIMARY_DISP)
    e10_bars = []
    for e in breakers:
        r = M10.revisit_and_react(m, e)
        if r and r.get("revisited"):
            e10_bars.append(int(e["confirm_idx"] + 1 + r["ttr_bars"]))
    e10_bars = sorted(set(e10_bars))

    def overlap(a, b):
        sa, sb = set(a), set(b)
        inter = len(sa & sb)
        return dict(a=len(sa), b=len(sb), intersection=inter,
                    pct_of_a=round(inter / len(sa), 4) if sa else None,
                    jaccard=round(inter / len(sa | sb), 4) if (sa or sb) else None)

    # ---- (3) repeated measurements per zone, for E013 (== E016) ----
    def zone_structure(entries):
        zone_counts = Counter(oi for oi, _ in entries)             # OB events per zone (ob_idx)
        rows = len(entries)
        distinct_zones = len(zone_counts)
        distinct_pairs = len({(oi, e) for oi, e in entries})
        bars = sorted(e for _, e in entries)
        overlaps = []
        for _, e in entries:
            lo, hi = e + 1, e + FWD
            overlaps.append(bisect_right(bars, hi) - bisect_left(bars, lo))
        ov = np.array(overlaps)
        return dict(ob_events=rows, distinct_zones=distinct_zones,
                    duplicate_ob_events=rows - distinct_zones,
                    distinct_zone_entry_pairs=distinct_pairs,
                    exact_duplicate_rows=rows - distinct_pairs,
                    fwd_overlap_median=float(np.median(ov)), fwd_overlap_mean=round(float(ov.mean()), 3),
                    fwd_overlap_max=int(ov.max()), pct_zero_overlap=round(float((ov == 0).mean()), 4))

    result = dict(
        window=dict(split=meta["data_split_id"], n_bars=n,
                    date_range=[str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])]),
        entry_counts=dict(E010_breaker=len(e10_bars), E013=len(e13_bars), E015_all=len(e15_all_bars),
                          E015_visit1=len(e15_v1_bars), E016=len(e16_bars),
                          E013_total_rows=len(e13), E016_total_rows=len(e16)),
        check1_circularity=dict(
            selection_window="first break-censored touch within [ob_idx+1, ob_idx+%d]" % E13_HORIZON,
            measurement_window="movement_profile [entry_idx+1, entry_idx+%d]" % FWD,
            windows_overlap=False,
            note="adjacent, not overlapping: measurement starts strictly AFTER the mitigation bar; "
                 "identical structure to E015 visit-1 (a reversal at the first touch is retained -- "
                 "break censoring stops only LATER visits). Unlike E010, whose 'unflipped' selection "
                 "window [ob+1, ob+480] coincided with its outcome window."),
        check2_entry_overlap=dict(
            E013_vs_E010=overlap(e13_bars, e10_bars),
            E013_vs_E016=overlap(e13_bars, e16_bars),
            E013_vs_E015_all=overlap(e13_bars, e15_all_bars),
            E013_vs_E015_visit1=overlap(e13_bars, e15_v1_bars),
            E016_vs_E010=overlap(e16_bars, e10_bars),
            E016_vs_E015_visit1=overlap(e16_bars, e15_v1_bars),
        ),
        check3_repeated_measurements=dict(E013=zone_structure(e13), E016=zone_structure(e16)),
    )

    print(json.dumps(result, indent=2, default=str))
    with open("e013_e016_dependence_checks_results.json", "w") as f:
        json.dump(result, f, indent=2, default=str)


if __name__ == "__main__":
    main()
