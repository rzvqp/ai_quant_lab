"""STOP-SIZE PROFILER (CEO filter, run BEFORE screening performance — saves runs).

For each candidate structure, measure the natural STOP size distribution in DOLLARS. Keep only families
whose median stop is large enough that the measured live spread (~0.05-0.08) is a small fraction of risk:
  median stop > ~$5  -> spread is <~2% of risk (acceptable, the zone where CAND-0037 lives)
  median stop < ~$1  -> spread is >10% of risk (the zone where S3 DIED)
Also report frequency (events/day) — we need BOTH a wide anchor AND better frequency than weekly.
Ratified primitives imported @5443077. Holdout sealed. Lookahead-safe features.
"""
from __future__ import annotations
import os, sys, json
import numpy as np, pandas as pd
for _c in [os.environ.get("RATIFIED_CODE_DIR"),
           r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\44ba92ba-04ad-40f2-a48e-0ee6a8aca893\scratchpad\ratified_code\code"]:
    if _c and os.path.isdir(_c):
        sys.path.insert(0, _c); break
from edge_research._common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
from edge_research._screen import derive_blocks, day_index_ny17, bars_to_period_end
from institutional_levels import (compute_prior_day_levels, compute_prior_week_levels,
                                  derive_week_index, LevelKind)
from session_levels import compute_prior_session_levels, derive_session_index, session_labels, SessionLevelKind
from order_flow import detect_order_blocks
from market_state import expansion


def dist(a, days):
    a = np.asarray([x for x in a if np.isfinite(x) and x > 0], float)
    if not len(a):
        return dict(n=0)
    return dict(n=int(len(a)), per_day=round(len(a) / days, 3),
                median=round(float(np.median(a)), 2), p25=round(float(np.percentile(a, 25)), 2),
                p75=round(float(np.percentile(a, 75)), 2),
                spread8c_pct_of_median=round(0.08 / float(np.median(a)) * 100, 1))


def main():
    d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    o = d["open"].to_numpy(); h = d["high"].to_numpy(); l = d["low"].to_numpy(); c = d["close"].to_numpy()
    t = d["time"].to_numpy(); n = len(d); blocks = derive_blocks(d)
    days = (d["dt"].max() - d["dt"].min()).days
    day_idx = day_index_ny17(t); week_idx = derive_week_index(day_idx)
    sess_idx = derive_session_index(t); sess_lbl = session_labels(t); sess = d["session"].to_numpy()
    H = d["high"]; L = d["low"]
    out = {}

    # prior-period RANGES (the breakout structural stop = opposite level = the range)
    def pair_ranges(levels, hk, lk, keyfn):
        pr = {}
        for lv in levels:
            if lv.kind in (hk, lk):
                pr.setdefault(keyfn(lv), {})[lv.kind] = lv.price
        return [abs(p[hk] - p[lk]) for p in pr.values() if hk in p and lk in p]

    day_l = compute_prior_day_levels(h, l, day_idx, blocks)
    out["prior_DAY_range"] = dist(pair_ranges(day_l, LevelKind.PDH, LevelKind.PDL,
                                  lambda lv: (lv.block_index, lv.source_period_start)), days)
    wk_l = compute_prior_week_levels(h, l, day_idx, week_idx, blocks)
    out["prior_WEEK_range (CAND-0037 stop)"] = dist(pair_ranges(wk_l, LevelKind.WEEKLY_HIGH, LevelKind.WEEKLY_LOW,
                                  lambda lv: (lv.block_index, lv.available_idx)), days)
    ss_l = compute_prior_session_levels(h, l, sess_idx, sess_lbl, blocks)
    out["prior_SESSION_range_all"] = dist(pair_ranges(ss_l, SessionLevelKind.SESSION_HIGH, SessionLevelKind.SESSION_LOW,
                                  lambda lv: (lv.block_index, lv.source_session_start)), days)
    # prior-NY-session range only
    ny_ranges = []
    pr = {}
    for lv in ss_l:
        if lv.kind in (SessionLevelKind.SESSION_HIGH, SessionLevelKind.SESSION_LOW) and lv.session_label == "ny":
            pr.setdefault((lv.block_index, lv.source_session_start), {})[lv.kind] = lv.price
    for p in pr.values():
        if SessionLevelKind.SESSION_HIGH in p and SessionLevelKind.SESSION_LOW in p:
            ny_ranges.append(abs(p[SessionLevelKind.SESSION_HIGH] - p[SessionLevelKind.SESSION_LOW]))
    out["prior_NY_session_range"] = dist(ny_ranges, days)

    # H4 range (16 M15 bars) — rolling, shifted
    h4 = (H.rolling(16).max().shift(1) - L.rolling(16).min().shift(1)).to_numpy()
    out["H4_range_rolling16"] = dist(h4[np.isfinite(h4)], days)

    # order-block heights (all, and the LARGE tail)
    obs = detect_order_blocks(o, h, l, c, n)
    ob_heights = [abs(ob.zone_upper - ob.zone_lower) for ob in obs]
    out["OB_height_all"] = dist(ob_heights, days)
    if ob_heights:
        thr = np.percentile([x for x in ob_heights if x > 0], 75)
        out["OB_height_large_top25pct"] = dist([x for x in ob_heights if x >= thr], days)

    # compression-accumulated range: range over the compression window preceding each expansion bar
    exp = expansion(o, h, l, c)
    atr = d["atr14"].to_numpy(); atr_ma = pd.Series(atr).rolling(50).mean().to_numpy()
    compress = (atr < 0.8 * atr_ma)
    comp_ranges = []
    for i in np.flatnonzero(exp):
        # walk back while compressed, accumulate range
        j = i - 1; hh = h[i]; ll = l[i]
        steps = 0
        while j >= 0 and compress[j] and steps < 200:
            hh = max(hh, h[j]); ll = min(ll, l[j]); j -= 1; steps += 1
        if steps >= 2:
            comp_ranges.append(hh - ll)
    out["compression_accumulated_range"] = dist(comp_ranges, days)

    result = dict(profiler="stop_size_by_family", days=days, price_median=round(float(np.median(c)), 1),
                  measured_spread=dict(median=0.05, p75=0.08, max=0.16),
                  note="keep families with median stop >~$5 (spread<2% risk); need per_day toward 3-4",
                  families=out)
    print(json.dumps(result, indent=2, default=float))
    with open(os.path.join(os.path.dirname(__file__), "stop_profiler_results.json"), "w") as f:
        json.dump(result, f, indent=2, default=float)


if __name__ == "__main__":
    main()
