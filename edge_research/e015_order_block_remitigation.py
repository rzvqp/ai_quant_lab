"""E015 -- Order Block Re-Mitigation -- full-profile Discovery-stage analysis (Flow A).

V0 (frozen, verbatim): "An order block that has already been mitigated once can be revisited a second
time and still produce a reaction."

Run under the post-remediation regime (EDGE_RESEARCH_PROTOCOL.md SS8); full-profile template per the
CEO's "overnight full edge profile" directive, reusing `_profile.py`.

Method (disclosed, exploratory -- Discovery stage only, no tuning/optimization):
1. **Order block (OB)**: identical, disclosed construction to E010 (displacement bar with range >
   1.5xATR14(prior) and directional body >=50% of range; the last opposite-colored bar within the
   preceding 10 bars is the OB zone) -- reused unchanged for methodological consistency across the two
   order-block edges, not re-tuned.
2. **Mitigation (visit)**: a contiguous span of bars whose range overlaps the OB zone
   (low<=zone_high AND high>=zone_low); consecutive touches within a 4-bar gap are merged into ONE
   visit (reduces chop/whipsaw pseudo-replication, same cooldown logic already used for E025's round-
   number events). Visits are numbered sequentially (1st, 2nd, 3rd, ...) in time order.
3. **Censoring, deliberately avoiding the look-ahead/tautology risk flagged for CEC-001
   (CROSS_EDGE_RESEARCH_CANDIDATES.md)**: visit tracking for a given OB STOPS the first time a later
   bar's CLOSE decisively violates the zone (the E010 "breaker" definition) -- this uses only
   information available up to and including that bar; no visit's own classification (1st/2nd/3rd/...)
   depends on knowledge of the OB's own more-distant future beyond "has it broken yet, as of now."
4. **V0 test**: for each visit number (1st, 2nd, 3rd+), does price react (reverse away from the zone,
   in the OB's ORIGINAL polarity direction) after that visit? Uses `_profile.py::movement_profile()`,
   same 7 horizons/5 ATR thresholds as every other edge this session. V0 predicts the 2nd+ visit still
   produces a real reaction -- tested directly by comparing visit-1 vs visit-2 vs visit-3+ reaction
   rate/magnitude (a within-population, repeated-measures design -- no external "does an OB work at
   all" control needed here, since that question is already covered by E010/CEC-001; the control
   needed HERE is whether any visit-number-dependent decay is specific to order blocks or a generic
   revisit property).
5. **Control**: random-matched-distance zones (seed=42, no real structure), same visit/censoring logic
   applied, to test whether a decay-or-not pattern by visit number is generic rather than OB-specific.
6. **Timeframes**: M15 and H1 (M1/M5 unavailable, restated from E010/E012, not re-derived). **Context
   slices, robustness**: same battery as E010/E012 (session/volatility/trend/day-of-week, yearly
   stability, displacement-threshold sensitivity).
"""
import json
import numpy as np
from scipy.stats import chi2_contingency, mannwhitneyu
from _common import load, vol_regime, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
import _profile as P

LOOKBACK_OB = 10
DISP_MULTS = [1.2, 1.5, 2.0]
PRIMARY_DISP = 1.5
BODY_FRAC = 0.5
TRACK_HORIZON = 960  # 10 trading days -- longer than E010/E012's 480, to give room for multiple visits
VISIT_COOLDOWN = 4
RNG_SEED = 42
MAX_VISIT_BUCKET = 3  # 1st, 2nd, 3rd-or-later


def detect_obs(m, disp_mult):
    o = m["open"].values
    h = m["high"].values
    l = m["low"].values
    c = m["close"].values
    atr = m["atr14"].values
    n = len(m)
    rng_ = h - l
    events = []
    for i in range(LOOKBACK_OB + 1, n):
        prior_atr = atr[i - 1]
        if not np.isfinite(prior_atr) or prior_atr <= 0:
            continue
        if rng_[i] <= disp_mult * prior_atr:
            continue
        body = abs(c[i] - o[i])
        if body < BODY_FRAC * rng_[i]:
            continue
        bullish_disp = c[i] > o[i]
        ob_j = None
        for j in range(i - 1, max(i - 1 - LOOKBACK_OB, -1), -1):
            if bullish_disp and c[j] < o[j]:
                ob_j = j
                break
            if (not bullish_disp) and c[j] > o[j]:
                ob_j = j
                break
        if ob_j is None:
            continue
        events.append(dict(ob_idx=int(ob_j), ob_low=float(l[ob_j]), ob_high=float(h[ob_j]),
                            disp_idx=int(i), ob_polarity="bull" if bullish_disp else "bear"))
    return events


def visits_for_ob(m, ob, horizon=TRACK_HORIZON):
    """Returns list of visit dicts (visit_number, start_idx) up to (not including) any breaker close."""
    j = ob["ob_idx"]
    zone_low, zone_high = ob["ob_low"], ob["ob_high"]
    polarity = ob["ob_polarity"]
    n = len(m)
    end = min(j + 1 + horizon, n)
    low = m["low"].values[j + 1:end]
    high = m["high"].values[j + 1:end]
    close = m["close"].values[j + 1:end]

    touch_mask = (low <= zone_high) & (high >= zone_low)
    if polarity == "bull":
        break_mask = close < zone_low
    else:
        break_mask = close > zone_high
    break_pos = np.argmax(break_mask) if break_mask.any() else len(break_mask)

    visits = []
    i = 0
    last_touch_end = None
    while i < break_pos:
        if touch_mask[i]:
            if last_touch_end is not None and (i - last_touch_end) <= VISIT_COOLDOWN:
                last_touch_end = i
            else:
                visits.append(j + 1 + i)
                last_touch_end = i
        i += 1
    return visits


def build_visit_rows(m, obs):
    rows = []
    for ob in obs:
        visits = visits_for_ob(m, ob)
        direction = 1 if ob["ob_polarity"] == "bull" else -1
        atr_ref = m["atr14"].values[ob["ob_idx"]]
        if not (np.isfinite(atr_ref) and atr_ref > 0):
            continue
        for vn, vidx in enumerate(visits, start=1):
            mp = P.movement_profile(m, vidx, direction, atr_ref)
            if mp is None:
                continue
            ctx = P.context_features(m, vidx)
            row = dict(ob_idx=ob["ob_idx"], visit_number=min(vn, MAX_VISIT_BUCKET), visit_idx=vidx,
                       outcome=mp["outcome"], mp=mp, direction=direction)
            row.update(ctx)
            row["year"] = P.year_of(m, vidx)
            rows.append(row)
    return rows


def random_matched_visits(m, n_obs, horizon, rng):
    close = m["close"].values
    atr = m["atr14"].values
    n = len(m)
    max_start = n - horizon - 60
    valid_idx = np.where(np.isfinite(atr[:max_start]) & (atr[:max_start] > 0))[0]
    valid_idx = valid_idx[valid_idx > 20]
    chosen = rng.choice(valid_idx, size=min(n_obs, len(valid_idx)), replace=False)
    rows = []
    for idx in chosen:
        a = atr[idx]
        half_width = 0.5 * a
        center = close[idx]
        zone_low, zone_high = center - half_width, center + half_width
        polarity = rng.choice(["bull", "bear"])
        ob = dict(ob_idx=int(idx), ob_low=float(zone_low), ob_high=float(zone_high), ob_polarity=polarity)
        visits = visits_for_ob(m, ob, horizon)
        direction = 1 if polarity == "bull" else -1
        for vn, vidx in enumerate(visits, start=1):
            mp = P.movement_profile(m, vidx, direction, a)
            if mp is None:
                continue
            rows.append(dict(visit_number=min(vn, MAX_VISIT_BUCKET), outcome=mp["outcome"], mp=mp))
    return rows


def summarize_by_visit(rows):
    out = {}
    for vn in range(1, MAX_VISIT_BUCKET + 1):
        sub = [r for r in rows if r["visit_number"] == vn]
        n = len(sub)
        if n == 0:
            out[str(vn)] = dict(n=0)
            continue
        outs = [r["outcome"] for r in sub]
        d = dict(n=n, continuation_rate=float(np.mean([o == "continuation" for o in outs])),
                  reversal_rate=float(np.mean([o == "reversal" for o in outs])),
                  stall_rate=float(np.mean([o == "stall" for o in outs])))
        d["movement_summary"] = P.summarize_movement([r["mp"] for r in sub])
        out[str(vn)] = d
    return out


def chi2_p(rate1, n1, rate2, n2):
    if n1 == 0 or n2 == 0:
        return None
    s1, s2 = round(rate1 * n1), round(rate2 * n2)
    try:
        _, p, _, _ = chi2_contingency([[s1, n1 - s1], [s2, n2 - s2]])
        return float(p)
    except Exception:
        return None


def run_timeframe(tf):
    m, meta = load(tf, data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    d1, _ = load("D1", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    m["vol_regime"] = vol_regime(m)
    m = P.attach_daily_context(m, d1)

    obs = detect_obs(m, PRIMARY_DISP)
    rows = build_visit_rows(m, obs)
    by_visit = summarize_by_visit(rows)

    v1 = [r for r in rows if r["visit_number"] == 1]
    v2 = [r for r in rows if r["visit_number"] == 2]
    v3 = [r for r in rows if r["visit_number"] == 3]
    p_v1_vs_v2 = chi2_p(by_visit["1"].get("continuation_rate", 0), by_visit["1"].get("n", 0),
                         by_visit["2"].get("continuation_rate", 0), by_visit["2"].get("n", 0))
    p_v1_vs_v3 = chi2_p(by_visit["1"].get("continuation_rate", 0), by_visit["1"].get("n", 0),
                         by_visit["3"].get("continuation_rate", 0), by_visit["3"].get("n", 0))

    rng = np.random.default_rng(RNG_SEED)
    rand_rows = random_matched_visits(m, len(obs), TRACK_HORIZON, rng)
    rand_by_visit = summarize_by_visit(rand_rows)

    slices = {}
    for sess in ["asia", "london", "ny", "late"]:
        s1 = [r for r in v1 if r["session"] == sess]
        s2 = [r for r in v2 if r["session"] == sess]
        slices[f"session_{sess}"] = dict(v1=summarize_by_visit(s1)["1"] if s1 else dict(n=0),
                                          v2=summarize_by_visit([dict(r, visit_number=1) for r in s2])["1"] if s2 else dict(n=0))
    for vr in ["low", "mid", "high"]:
        s1 = [r for r in v1 if r["vol_regime"] == vr]
        s2 = [r for r in v2 if r["vol_regime"] == vr]
        slices[f"vol_{vr}"] = dict(v1=summarize_by_visit(s1)["1"] if s1 else dict(n=0),
                                    v2=summarize_by_visit([dict(r, visit_number=1) for r in s2])["1"] if s2 else dict(n=0))
    for tr in ["bull", "bear", "range"]:
        s1 = [r for r in v1 if r["trend"] == tr]
        s2 = [r for r in v2 if r["trend"] == tr]
        slices[f"trend_{tr}"] = dict(v1=summarize_by_visit(s1)["1"] if s1 else dict(n=0),
                                      v2=summarize_by_visit([dict(r, visit_number=1) for r in s2])["1"] if s2 else dict(n=0))

    disp_sensitivity = {}
    for mult in DISP_MULTS:
        obs2 = detect_obs(m, mult)
        rows2 = build_visit_rows(m, obs2)
        disp_sensitivity[str(mult)] = dict(n_obs=len(obs2), by_visit=summarize_by_visit(rows2))

    by_year = {}
    for r in v1 + v2 + v3:
        by_year.setdefault(r["year"], []).append(r)
    yearly = {}
    for y, rs in sorted(by_year.items()):
        yearly[str(y)] = dict(
            v1=summarize_by_visit([r for r in rs if r["visit_number"] == 1])["1"],
            v2=summarize_by_visit([dict(r, visit_number=1) for r in rs if r["visit_number"] == 2])["1"])

    return dict(
        timeframe=tf, split_metadata=meta, n_bars=int(len(m)),
        date_range=[str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])],
        n_obs=len(obs), n_visits_total=len(rows),
        primary=dict(by_visit=by_visit, random_matched_by_visit=rand_by_visit,
                     p_v1_vs_v2=p_v1_vs_v2, p_v1_vs_v3=p_v1_vs_v3),
        slices=slices, displacement_sensitivity=disp_sensitivity, yearly_stability=yearly,
    )


def main():
    results = {"edge": "E015", "edge_id": "E015", "hypothesis_version": "V0",
               "run_id": "discovery_pass_1_full_profile_2026-07-22",
               "timeframes_tested": [], "timeframes_unavailable": {
                   "M1": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)",
                   "M5": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)"},
               "params": dict(LOOKBACK_OB=LOOKBACK_OB, DISP_MULTS=DISP_MULTS, PRIMARY_DISP=PRIMARY_DISP,
                               BODY_FRAC=BODY_FRAC, TRACK_HORIZON=TRACK_HORIZON,
                               VISIT_COOLDOWN=VISIT_COOLDOWN, RNG_SEED=RNG_SEED,
                               movement_horizons=P.HORIZONS, atr_thresholds=P.ATR_THRESHOLDS),
               "by_timeframe": {}}

    for tf in ["M15", "H1"]:
        print("=== running", tf, "===")
        res = run_timeframe(tf)
        results["by_timeframe"][tf] = res
        results["timeframes_tested"].append(tf)
        p = res["primary"]
        print(tf, "n_obs", res["n_obs"], "n_visits_total", res["n_visits_total"])
        for vn in ["1", "2", "3"]:
            print(" visit", vn, p["by_visit"][vn])
        print(" random matched:", p["random_matched_by_visit"])
        print(" p_v1_vs_v2:", p["p_v1_vs_v2"], "p_v1_vs_v3:", p["p_v1_vs_v3"])

    with open("e015_order_block_remitigation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)


if __name__ == "__main__":
    main()
