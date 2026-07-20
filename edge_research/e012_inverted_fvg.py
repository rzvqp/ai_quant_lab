"""E012 -- Inverted Fair Value Gap -- full-profile Discovery-stage analysis (Flow A).

V0 (frozen, verbatim): "A Fair Value Gap that is fully violated ('inverted') flips role and acts as an
opposite-direction reaction zone."

Run under the post-remediation regime (EDGE_RESEARCH_PROTOCOL.md SS8); full-profile template per the
CEO's "overnight full edge profile" directive (2026-07-22), reusing `_profile.py` (built for E010).

Method (disclosed, exploratory -- Discovery stage only, no tuning/optimization):
1. **Fair Value Gap (FVG)**, standard 3-bar imbalance definition (reproduced from scratch, not imported
   -- this is a widely-described, non-proprietary construction): bullish FVG at bar i if
   low[i] > high[i-2] (zone = [high[i-2], low[i]]); bearish FVG if high[i] < low[i-2] (zone =
   [high[i], low[i-2]]).
2. **Inversion**: a bullish FVG inverts the first time a LATER bar's CLOSE falls below the zone's own
   low (high[i-2]) -- a full, decisive violation, not just an intrabar wick; bearish FVG inverts
   symmetric (close above the zone's high). This is V0's own "fully violated."
3. **V0 test**: after inversion, does price revisit the (now-inverted) zone, and does it react in the
   NEW, opposite direction (`_profile.py::movement_profile()`, same 7 horizons / 5 ATR thresholds as
   every other edge profiled this session)?
4. **Controls**: (1) **un-inverted-FVG control** -- FVGs never later fully violated within the test
   horizon, tested for reaction in their ORIGINAL role (the classic, un-flipped "FVG gets touched and
   holds" story) -- the natural "is inversion itself special" baseline; (2) **random-matched-distance
   control** (seed=42), no real structure.
5. **Timeframes**: M15 and H1 (both on disk); M1/M5 confirmed unavailable (project-wide gap, restated
   from E010, not re-derived).
6. **Context slices, robustness**: same battery as E010 (session/volatility/trend/day-of-week, yearly
   stability); FVG-size-threshold sensitivity in place of E010's displacement-threshold sensitivity
   (a minimum-gap-size filter, swept, not searched for a favorable value).
"""
import json
import numpy as np
from scipy.stats import chi2_contingency
from _common import load, vol_regime, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
import _profile as P

MIN_GAP_MULTS = [0.0, 0.1, 0.25]  # minimum FVG size as a fraction of ATR14; 0.0 = no filter (primary)
PRIMARY_MIN_GAP = 0.0
REVISIT_HORIZON = 480
RNG_SEED = 42


def detect_fvgs(m):
    h = m["high"].values
    l = m["low"].values
    atr = m["atr14"].values
    n = len(m)
    events = []
    for i in range(2, n):
        a = atr[i]
        if not np.isfinite(a) or a <= 0:
            continue
        if l[i] > h[i - 2]:
            gap = l[i] - h[i - 2]
            events.append(dict(fvg_idx=int(i), zone_low=float(h[i - 2]), zone_high=float(l[i]),
                                polarity="bull", gap_atr=float(gap / a)))
        elif h[i] < l[i - 2]:
            gap = l[i - 2] - h[i]
            events.append(dict(fvg_idx=int(i), zone_low=float(h[i]), zone_high=float(l[i - 2]),
                                polarity="bear", gap_atr=float(gap / a)))
    return events


def find_inversions(m, events, min_gap_mult, horizon=REVISIT_HORIZON):
    c = m["close"].values
    n = len(m)
    inverted, uninverted = [], []
    for e in events:
        if e["gap_atr"] < min_gap_mult:
            continue
        j = e["fvg_idx"]
        zone_low, zone_high = e["zone_low"], e["zone_high"]
        end = min(j + 1 + horizon, n)
        seg = c[j + 1:end]
        if e["polarity"] == "bull":
            hit = np.where(seg < zone_low)[0]
        else:
            hit = np.where(seg > zone_high)[0]
        if len(hit):
            inv_idx = j + 1 + int(hit[0])
            new_dir = -1 if e["polarity"] == "bull" else 1
            inverted.append(dict(**e, confirm_idx=inv_idx, direction=new_dir))
        else:
            orig_dir = 1 if e["polarity"] == "bull" else -1
            uninverted.append(dict(**e, confirm_idx=j, direction=orig_dir))
    return inverted, uninverted


def revisit_and_react(m, ev, horizon=REVISIT_HORIZON):
    idx = ev["confirm_idx"]
    zone_low, zone_high = ev["zone_low"], ev["zone_high"]
    high = m["high"].values
    low = m["low"].values
    atr = m["atr14"].values
    n = len(m)
    end = min(idx + 1 + horizon, n)
    if end <= idx + 1:
        return None
    revisited_mask = (low[idx + 1:end] <= zone_high) & (high[idx + 1:end] >= zone_low)
    revisited = bool(revisited_mask.any())
    if not revisited:
        return dict(revisited=False, mp=None)
    rv_i = int(np.argmax(revisited_mask))
    rv_idx = idx + 1 + rv_i
    atr_ref = atr[idx] if np.isfinite(atr[idx]) and atr[idx] > 0 else np.nan
    mp = P.movement_profile(m, rv_idx, ev["direction"], atr_ref)
    return dict(revisited=True, ttr_bars=rv_i, mp=mp)


def build_rows(m, events, horizon=REVISIT_HORIZON):
    rows = []
    for e in events:
        r = revisit_and_react(m, e, horizon)
        if r is None:
            continue
        row = dict(e)
        row["revisited"] = r["revisited"]
        if r["revisited"] and r["mp"] is not None:
            row["ttr_bars"] = r["ttr_bars"]
            row["outcome"] = r["mp"]["outcome"]
            row["mp"] = r["mp"]
        else:
            row["outcome"] = None
            row["mp"] = None
        ctx = P.context_features(m, e["confirm_idx"])
        row.update(ctx)
        row["year"] = P.year_of(m, e["confirm_idx"])
        rows.append(row)
    return rows


def random_matched(m, real_rows, n_events, horizon, rng):
    close = m["close"].values
    atr = m["atr14"].values
    n = len(m)
    dists = [abs((r["zone_low"] + r["zone_high"]) / 2 - close[r["confirm_idx"]]) / atr[r["confirm_idx"]]
             for r in real_rows if np.isfinite(atr[r["confirm_idx"]]) and atr[r["confirm_idx"]] > 0]
    if not dists:
        return []
    dists = np.array(dists)
    max_start = n - horizon - 60
    valid_idx = np.where(np.isfinite(atr[:max_start]) & (atr[:max_start] > 0))[0]
    valid_idx = valid_idx[valid_idx > 20]
    chosen = rng.choice(valid_idx, size=min(n_events, len(valid_idx)), replace=False)
    sampled_dist = rng.choice(dists, size=len(chosen), replace=True)
    out = []
    for idx, d in zip(chosen, sampled_dist):
        a = atr[idx]
        direction = rng.choice([-1, 1])
        zone_center = close[idx] - direction * d * a
        zone_low, zone_high = zone_center - 0.15 * a, zone_center + 0.15 * a
        end = min(idx + 1 + horizon, n)
        revisited = bool(((m["low"].values[idx + 1:end] <= zone_high) & (m["high"].values[idx + 1:end] >= zone_low)).any())
        out.append(dict(revisited=revisited))
    return out


def outcome_summary(rows):
    n = len(rows)
    if n == 0:
        return dict(n=0)
    revisit_rate = float(np.mean([r["revisited"] for r in rows]))
    reacted = [r for r in rows if r["revisited"] and r["outcome"] is not None]
    out = dict(n=n, revisit_rate=revisit_rate, n_revisited_with_outcome=len(reacted))
    if reacted:
        outs = [r["outcome"] for r in reacted]
        out["continuation_rate"] = float(np.mean([o == "continuation" for o in outs]))
        out["reversal_rate"] = float(np.mean([o == "reversal" for o in outs]))
        out["stall_rate"] = float(np.mean([o == "stall" for o in outs]))
        out["movement_summary"] = P.summarize_movement([r["mp"] for r in reacted])
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

    all_fvgs = detect_fvgs(m)
    inverted, uninverted = find_inversions(m, all_fvgs, PRIMARY_MIN_GAP)
    inv_rows = build_rows(m, inverted)
    uninv_rows = build_rows(m, uninverted)

    rng = np.random.default_rng(RNG_SEED)
    rand_rows = random_matched(m, inv_rows, len(inv_rows), REVISIT_HORIZON, rng)
    rand_revisit_rate = float(np.mean([r["revisited"] for r in rand_rows])) if rand_rows else None

    i_sum, u_sum = outcome_summary(inv_rows), outcome_summary(uninv_rows)
    p_revisit_vs_uninv = chi2_p(i_sum.get("revisit_rate", 0), i_sum.get("n", 0),
                                 u_sum.get("revisit_rate", 0), u_sum.get("n", 0))
    p_revisit_vs_random = chi2_p(i_sum.get("revisit_rate", 0), i_sum.get("n", 0),
                                  rand_revisit_rate or 0, len(rand_rows)) if rand_rows else None
    p_reaction_vs_uninv = None
    if i_sum.get("n_revisited_with_outcome", 0) > 20 and u_sum.get("n_revisited_with_outcome", 0) > 20:
        p_reaction_vs_uninv = chi2_p(i_sum.get("continuation_rate", 0), i_sum["n_revisited_with_outcome"],
                                      u_sum.get("continuation_rate", 0), u_sum["n_revisited_with_outcome"])

    slices = {}
    for sess in ["asia", "london", "ny", "late"]:
        slices[f"session_{sess}"] = outcome_summary([r for r in inv_rows if r["session"] == sess])
    for vr in ["low", "mid", "high"]:
        slices[f"vol_{vr}"] = outcome_summary([r for r in inv_rows if r["vol_regime"] == vr])
    for tr in ["bull", "bear", "range"]:
        slices[f"trend_{tr}"] = outcome_summary([r for r in inv_rows if r["trend"] == tr])
    for dow in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        slices[f"dow_{dow}"] = outcome_summary([r for r in inv_rows if r["dow"] == dow])

    gap_sensitivity = {}
    for mult in MIN_GAP_MULTS:
        inv2, _ = find_inversions(m, all_fvgs, mult)
        inv2_rows = build_rows(m, inv2)
        gap_sensitivity[str(mult)] = dict(n_inverted=len(inv2_rows), summary=outcome_summary(inv2_rows))

    by_year = {}
    for r in inv_rows:
        by_year.setdefault(r["year"], []).append(r)
    yearly = {str(y): outcome_summary(rs) for y, rs in sorted(by_year.items())}

    return dict(
        timeframe=tf, split_metadata=meta, n_bars=int(len(m)),
        date_range=[str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])],
        n_all_fvgs=len(all_fvgs), n_inverted=len(inv_rows), n_uninverted=len(uninv_rows), n_random=len(rand_rows),
        primary=dict(inverted=i_sum, uninverted_control=u_sum, random_matched_revisit_rate=rand_revisit_rate,
                     p_revisit_vs_uninverted=p_revisit_vs_uninv, p_revisit_vs_random=p_revisit_vs_random,
                     p_reaction_vs_uninverted=p_reaction_vs_uninv),
        slices=slices, gap_size_sensitivity=gap_sensitivity, yearly_stability=yearly,
    )


def main():
    results = {"edge": "E012", "edge_id": "E012", "hypothesis_version": "V0",
               "run_id": "discovery_pass_1_full_profile_2026-07-22",
               "timeframes_tested": [], "timeframes_unavailable": {
                   "M1": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)",
                   "M5": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)"},
               "params": dict(MIN_GAP_MULTS=MIN_GAP_MULTS, PRIMARY_MIN_GAP=PRIMARY_MIN_GAP,
                               REVISIT_HORIZON=REVISIT_HORIZON, RNG_SEED=RNG_SEED,
                               movement_horizons=P.HORIZONS, atr_thresholds=P.ATR_THRESHOLDS),
               "by_timeframe": {}}

    for tf in ["M15", "H1"]:
        print("=== running", tf, "===")
        res = run_timeframe(tf)
        results["by_timeframe"][tf] = res
        results["timeframes_tested"].append(tf)
        p = res["primary"]
        print(tf, "n_inverted", res["n_inverted"], "n_uninverted", res["n_uninverted"])
        print(" inverted:", p["inverted"])
        print(" uninverted:", p["uninverted_control"])
        print(" random_revisit_rate:", p["random_matched_revisit_rate"])
        print(" p_revisit_vs_uninverted:", p["p_revisit_vs_uninverted"],
              "p_revisit_vs_random:", p["p_revisit_vs_random"],
              "p_reaction_vs_uninverted:", p["p_reaction_vs_uninverted"])

    with open("e012_inverted_fvg_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)


if __name__ == "__main__":
    main()
