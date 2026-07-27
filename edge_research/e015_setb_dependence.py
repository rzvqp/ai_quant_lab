"""E015-V1 dependence-structure MEASUREMENT (CEO task 2026-07-25). STRUCTURE ONLY.

Reconstructs the SAME order-block/visit events STEP 3 used on Set B (deterministic detector, identical
countable-filter), then measures the sampling dependence structure the chi-square independence
assumption requires. It computes NO outcome (no movement_profile, no continuation/reversal), NO p-value,
NO threshold — only event geometry: counts, visits-per-OB, forward-window overlap, and same-bar/same-hour
collisions. Facts only; no interpretation, no validity conclusion. E015-V1 stays SUSPENDED.
"""
import json
from bisect import bisect_right, bisect_left

import numpy as np

import _profile as P
from _common import vol_regime
from _setb import load_setb, countable_events
import e015_order_block_remitigation as M15

WARMUP = 250
FN_960 = M15.TRACK_HORIZON + max(P.HORIZONS)   # 1010 (STEP 3 countable filter)
FWD = max(P.HORIZONS)                          # 50 -- movement_profile forward window [vidx+1 .. vidx+50]


def measure(tf):
    m, meta = load_setb(tf, hypothesis_id="E015-V1-dependence-audit", provenance_edges=["E015"],
                        warmup_bars=WARMUP)
    m["vol_regime"] = vol_regime(m)
    m["date"] = m["dt"].dt.date
    obs = M15.detect_obs(m, M15.PRIMARY_DISP)
    kept_idx, report = countable_events(m, [o["ob_idx"] for o in obs], FN_960)
    kept = set(kept_idx)
    obs_kept = [o for o in obs if o["ob_idx"] in kept]

    times = m["time"].values
    n = len(m)
    atr = m["atr14"].values

    visits = []                 # one dict PER ROW, exactly as STEP 3's build_visit_rows produced them
    zone_visit_counts = {}      # ob_idx -> visits per OB event (same across duplicate events of the zone)
    ob_events_with_visits = 0   # OB EVENTS (duplicates kept) that produced >=1 visit row
    zone_event_counts = {}      # ob_idx -> number of OB events mapping to that zone
    for o in obs_kept:
        atr_ref = atr[o["ob_idx"]]
        if not (np.isfinite(atr_ref) and atr_ref > 0):   # replicate build_visit_rows OB-level guard
            continue
        vs = [v for v in M15.visits_for_ob(m, o) if v + 1 < n]  # movement_profile None guard (never trips)
        if not vs:
            continue
        ob_events_with_visits += 1
        oi = int(o["ob_idx"])
        zone_event_counts[oi] = zone_event_counts.get(oi, 0) + 1
        zone_visit_counts[oi] = len(vs)
        for vn, vidx in enumerate(vs, start=1):
            visits.append(dict(ob_idx=oi, visit_number=min(vn, M15.MAX_VISIT_BUCKET),
                               visit_idx=int(vidx), t=int(times[vidx])))

    # ---- (1) distinct OBs and total visits, per group (+ duplicate-event structure) ----
    total_visits = len(visits)
    distinct_zones = len(zone_visit_counts)
    distinct_zone_visit_pairs = len({(v["ob_idx"], v["visit_idx"]) for v in visits})
    by_bucket = {}
    for b in (1, 2, 3):
        sub = [v for v in visits if v["visit_number"] == b]
        by_bucket[b] = dict(n_rows=len(sub), n_distinct_zones=len({v["ob_idx"] for v in sub}),
                            n_distinct_zone_visit_pairs=len({(v["ob_idx"], v["visit_idx"]) for v in sub}))
    g1 = [v for v in visits if v["visit_number"] == 1]
    g2plus = [v for v in visits if v["visit_number"] >= 2]
    duplication = dict(
        ob_events_with_visits=ob_events_with_visits, distinct_zones=distinct_zones,
        duplicate_ob_events=ob_events_with_visits - distinct_zones,
        total_visit_rows=total_visits, distinct_zone_visit_pairs=distinct_zone_visit_pairs,
        exact_duplicate_visit_rows=total_visits - distinct_zone_visit_pairs,
        zones_hit_by_multiple_events=int(sum(1 for c in zone_event_counts.values() if c > 1)),
        max_events_for_one_zone=int(max(zone_event_counts.values())) if zone_event_counts else 0,
    )

    # ---- (2) visits-per-OB distribution (per distinct zone) ----
    counts = np.array(sorted(zone_visit_counts.values()))
    per_ob_dist = dict(
        n_obs=int(len(counts)),
        median=float(np.median(counts)) if len(counts) else None,
        max=int(counts.max()) if len(counts) else None,
        mean=float(counts.mean()) if len(counts) else None,
        obs_with_exactly_1_visit=int((counts == 1).sum()),
        obs_with_more_than_1_visit=int((counts > 1).sum()),
        histogram={str(k): int((counts == k).sum()) for k in range(1, int(counts.max()) + 1)} if len(counts) else {},
    )

    # ---- (3) forward-window overlap: for each visit, how many OTHER visits fall in [vidx+1, vidx+FWD] ----
    idx_sorted = sorted(v["visit_idx"] for v in visits)
    overlaps = []
    for v in visits:
        lo = v["visit_idx"] + 1
        hi = v["visit_idx"] + FWD
        left = bisect_left(idx_sorted, lo)
        right = bisect_right(idx_sorted, hi)
        cnt = right - left                       # visits with idx in [lo, hi]; excludes self (self idx < lo)
        overlaps.append(cnt)
    overlaps = np.array(overlaps)
    ov = dict(
        median=float(np.median(overlaps)), mean=float(overlaps.mean()), max=int(overlaps.max()),
        pct_zero_overlap=float((overlaps == 0).mean()),
        distribution={
            "0": int((overlaps == 0).sum()), "1": int((overlaps == 1).sum()),
            "2": int((overlaps == 2).sum()), "3-5": int(((overlaps >= 3) & (overlaps <= 5)).sum()),
            "6-10": int(((overlaps >= 6) & (overlaps <= 10)).sum()), ">10": int((overlaps > 10).sum()),
        },
    )

    # ---- (4) same-bar / same-hour collisions (split: same zone = duplication, diff zone = overlap) ----
    from collections import Counter, defaultdict
    bar_counter = Counter(v["visit_idx"] for v in visits)
    same_bar_visits = sum(c for c in bar_counter.values() if c > 1)
    n_bars_multi = sum(1 for c in bar_counter.values() if c > 1)
    # of the same-bar collisions, how many involve DIFFERENT zones vs the same zone
    bar_to_zones = defaultdict(set)
    for v in visits:
        bar_to_zones[v["visit_idx"]].add(v["ob_idx"])
    bars_multi_diff_zone = sum(1 for b, z in bar_to_zones.items() if bar_counter[b] > 1 and len(z) > 1)
    bars_multi_same_zone_only = sum(1 for b, z in bar_to_zones.items() if bar_counter[b] > 1 and len(z) == 1)
    hour_counter = Counter(int(v["t"] // 3600) for v in visits)
    same_hour_visits = sum(c for c in hour_counter.values() if c > 1)
    n_hours_multi = sum(1 for c in hour_counter.values() if c > 1)
    collisions = dict(
        distinct_bars_with_a_visit=len(bar_counter),
        bars_with_multiple_visits=n_bars_multi, visits_sharing_a_bar=same_bar_visits,
        bars_multi_from_different_zones=bars_multi_diff_zone,
        bars_multi_from_same_zone_only=bars_multi_same_zone_only,
        distinct_hours_with_a_visit=len(hour_counter),
        hours_with_multiple_visits=n_hours_multi, visits_sharing_an_hour=same_hour_visits,
    )

    return dict(tf=tf, countable_report=report, forward_window_bars=FWD,
                nominal_n=dict(total_visits=total_visits, distinct_zones=distinct_zones,
                               visit1_rows=len(g1), visit2plus_rows=len(g2plus), by_bucket=by_bucket),
                duplication=duplication, visits_per_ob=per_ob_dist,
                forward_overlap=ov, collisions=collisions)


def main():
    out = {"measurement": "E015-V1_dependence_structure", "note": "STRUCTURE ONLY -- no outcome, no p, no threshold",
           "by_tf": {}}
    for tf in ["M15", "H1"]:
        r = measure(tf)
        out["by_tf"][tf] = r
        print("=" * 78)
        print(f"E015-V1 dependence structure -- {tf}")
        print("=" * 78)
        nn = r["nominal_n"]
        du = r["duplication"]
        print(f"(1) distinct zones={nn['distinct_zones']} total_visit_rows={nn['total_visits']} | "
              f"visit-1 rows={nn['visit1_rows']} visit-2+ rows={nn['visit2plus_rows']}")
        for b in (1, 2, 3):
            bb = nn["by_bucket"][b]
            print(f"      bucket visit-{b}: rows={bb['n_rows']} distinct_zones={bb['n_distinct_zones']} "
                  f"distinct_zone-visit_pairs={bb['n_distinct_zone_visit_pairs']}")
        print(f"    DUPLICATION: OB events={du['ob_events_with_visits']} vs distinct zones={du['distinct_zones']} "
              f"(dup events={du['duplicate_ob_events']}); total rows={du['total_visit_rows']} vs distinct "
              f"zone-visit pairs={du['distinct_zone_visit_pairs']} (exact-dup rows={du['exact_duplicate_visit_rows']})")
        vp = r["visits_per_ob"]
        print(f"(2) visits/OB: median={vp['median']} max={vp['max']} mean={round(vp['mean'],3)} | "
              f"OBs with 1 visit={vp['obs_with_exactly_1_visit']} with >1={vp['obs_with_more_than_1_visit']}")
        print(f"      histogram(visits->#OBs)={vp['histogram']}")
        ov = r["forward_overlap"]
        print(f"(3) forward-window overlap (other visits in [vidx+1,vidx+{FWD}]): median={ov['median']} "
              f"mean={round(ov['mean'],3)} max={ov['max']} pct_zero={round(ov['pct_zero_overlap'],4)}")
        print(f"      distribution={ov['distribution']}")
        co = r["collisions"]
        print(f"(4) same-bar: {co['visits_sharing_a_bar']} visits across {co['bars_with_multiple_visits']} bars "
              f"(diff-zone bars={co['bars_multi_from_different_zones']}, same-zone-only bars={co['bars_multi_from_same_zone_only']}) | "
              f"same-hour: {co['visits_sharing_an_hour']} visits across {co['hours_with_multiple_visits']} hours")

    with open("e015_setb_dependence_results.json", "w") as f:
        json.dump(out, f, indent=2, default=str)


if __name__ == "__main__":
    main()
