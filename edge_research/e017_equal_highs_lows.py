"""E017 -- Equal Highs / Lows Target -- Discovery-stage analysis (Flow A).

V0 (frozen, verbatim): "Clusters of equal highs/lows act as magnet levels that price is statistically
likely to reach before reversing."

This is the first edge run under the post-remediation regime (EDGE_RESEARCH_PROTOCOL.md SS8): data
loads exclusively through `_common.load()` with an explicit `data_split_id`/`cutoff` -- no direct CSV
read anywhere in this file.

Method (disclosed, exploratory -- Discovery stage only, no tuning/optimization):
1. Swing (fractal) detection, same k=5 method already used and disclosed for E028 (reproduced here
   from scratch, not imported -- each edge script is self-contained): a bar is a swing high/low if its
   high/low is the single extreme among the 11 bars centered on it.
2. For every CONSECUTIVE pair of same-type swings (p1, p2), p2 is the "target level" under test in
   BOTH groups below -- the only thing that differs between groups is whether p1 sat within tolerance
   of p2:
   - EQUAL group: |p2 - p1| <= tolerance x ATR14[p2] (a same-type swing recently confirmed within
     tolerance of the one before it -- an "equal highs/lows" pair).
   - ISOLATED-CONTROL group: the same test, but NOT within tolerance -- a normal, non-doubled swing.
   Tolerance is swept over {0.10, 0.15, 0.25, 0.40} x ATR (CEO requirement: clustering-tolerance
   sensitivity); 0.15 is the primary/headline value, chosen before any result was seen.
3. RANDOM-MATCHED-DISTANCE control (a second, stronger control): for a sample of purely random bar
   locations (fixed seed=42, no swing structure at all), a synthetic target is placed at a distance (in
   ATR units) resampled WITH REPLACEMENT from the EQUAL group's own empirical distance distribution --
   this tests whether the reach-rate found for real equal-highs/lows clusters is simply explained by
   "a target this close, given this much time, usually gets touched anyway" (generic
   continuation/range-expansion/proximity), independent of any real swing structure whatsoever.
4. For every event (all three groups): distance_at_detection = signed distance from the detection bar's
   close to the target, in ATR units. reach = whether price ever touches/exceeds the target within a
   horizon (96/480/1920 M15 bars = ~1/~5/~20 trading days -- horizon sensitivity, not optimized to any
   one value). time_to_reach in bars. reaction, if reached: signed distance (in ATR units) between the
   target and price N=16 bars (~4h) after the reach bar -- positive = price pulled back away from the
   target (a "reversal"), negative = price continued through it.
5. Both sides (equal-HIGHS and equal-LOWS) are run independently and compared for asymmetry.
"""
import json
import numpy as np
import pandas as pd
from _common import load, vol_regime, summarize, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID

K = 5
TOLS = [0.10, 0.15, 0.25, 0.40]
PRIMARY_TOL = 0.15
HORIZONS = [96, 480, 1920]
PRIMARY_HORIZON = 480
REACTION_N = 16
RNG_SEED = 42


def detect_swings(m):
    h = m["high"].values
    l = m["low"].values
    n = len(m)
    is_high = np.zeros(n, dtype=bool)
    is_low = np.zeros(n, dtype=bool)
    for i in range(K, n - K):
        window_h = h[i - K:i + K + 1]
        if h[i] == window_h.max() and (window_h == h[i]).sum() == 1:
            is_high[i] = True
        window_l = l[i - K:i + K + 1]
        if l[i] == window_l.min() and (window_l == l[i]).sum() == 1:
            is_low[i] = True
    highs = [(i, h[i]) for i in np.where(is_high)[0]]
    lows = [(i, l[i]) for i in np.where(is_low)[0]]
    return highs, lows


def build_pair_events(swing_points, m, tol, side):
    atr = m["atr14"].values
    close = m["close"].values
    events = []
    for k in range(len(swing_points) - 1):
        idx1, p1 = swing_points[k]
        idx2, p2 = swing_points[k + 1]
        atr_ref = atr[idx2]
        if not np.isfinite(atr_ref) or atr_ref <= 0:
            continue
        is_equal = abs(p2 - p1) <= tol * atr_ref
        target = p2
        if side == "high":
            dist = (target - close[idx2]) / atr_ref
        else:
            dist = (close[idx2] - target) / atr_ref
        events.append(dict(idx=int(idx2), target=float(target), is_equal=bool(is_equal),
                            dist=float(dist), session=str(m["session"].iloc[idx2]),
                            dow=str(m["dow"].iloc[idx2]), vol_regime=str(m["vol_regime"].iloc[idx2])))
    return events


def reach_stats(events, m, horizon, side, reaction_n=REACTION_N):
    high = m["high"].values
    low = m["low"].values
    close = m["close"].values
    atr = m["atr14"].values
    n = len(m)
    out = []
    for e in events:
        idx = e["idx"]
        target = e["target"]
        end = min(idx + 1 + horizon, n)
        if end <= idx + 1:
            continue
        if side == "high":
            seg = high[idx + 1:end]
            reached_mask = seg >= target
        else:
            seg = low[idx + 1:end]
            reached_mask = seg <= target
        reached = bool(reached_mask.any())
        ttf = int(np.argmax(reached_mask)) if reached else None
        reaction = None
        if reached:
            reach_idx = idx + 1 + ttf
            fut_idx = reach_idx + reaction_n
            a = atr[idx]
            if fut_idx < n and np.isfinite(a) and a > 0:
                if side == "high":
                    reaction = float((target - close[fut_idx]) / a)
                else:
                    reaction = float((close[fut_idx] - target) / a)
        row = dict(e)
        row.update(horizon=horizon, reached=reached, ttf_bars=ttf, reaction=reaction)
        out.append(row)
    return out


def random_matched_control(equal_events, m, side, n_events, horizon, rng):
    close = m["close"].values
    atr = m["atr14"].values
    n = len(m)
    dists = np.array([e["dist"] for e in equal_events])
    max_start = n - horizon - REACTION_N - 2
    valid_idx = np.where(np.isfinite(atr[:max_start]) & (atr[:max_start] > 0))[0]
    valid_idx = valid_idx[valid_idx > K]
    chosen = rng.choice(valid_idx, size=min(n_events, len(valid_idx)), replace=False)
    sampled_dist = rng.choice(dists, size=len(chosen), replace=True)
    events = []
    for idx, d in zip(chosen, sampled_dist):
        a = atr[idx]
        if side == "high":
            target = close[idx] + d * a
        else:
            target = close[idx] - d * a
        events.append(dict(idx=int(idx), target=float(target), is_equal=False, dist=float(d),
                            session=str(m["session"].iloc[idx]), dow=str(m["dow"].iloc[idx]),
                            vol_regime=str(m["vol_regime"].iloc[idx])))
    return events


def summarize_group(rows, key="reached"):
    n = len(rows)
    if n == 0:
        return dict(n=0)
    reached = [r["reached"] for r in rows]
    rate = float(np.mean(reached))
    ttfs = [r["ttf_bars"] for r in rows if r["ttf_bars"] is not None]
    reactions = np.array([r["reaction"] for r in rows if r["reaction"] is not None], dtype=float)
    out = dict(n=n, reach_rate=rate, n_reached=len(ttfs))
    if ttfs:
        out["median_ttf_bars"] = float(np.median(ttfs))
    if len(reactions):
        out["reaction_summary"] = summarize(reactions)
    return out


def run_side(m, side, split_meta):
    highs, lows = detect_swings(m)
    swing_points = highs if side == "high" else lows

    result = {"n_swing_points": len(swing_points), "by_tolerance": {}}

    for tol in TOLS:
        pair_events = build_pair_events(swing_points, m, tol, side)
        equal_pairs = [e for e in pair_events if e["is_equal"]]
        isolated_pairs = [e for e in pair_events if not e["is_equal"]]

        by_horizon = {}
        for hz in HORIZONS:
            eq_r = reach_stats(equal_pairs, m, hz, side)
            iso_r = reach_stats(isolated_pairs, m, hz, side)
            by_horizon[str(hz)] = dict(equal=summarize_group(eq_r), isolated=summarize_group(iso_r))
        result["by_tolerance"][str(tol)] = dict(
            n_equal=len(equal_pairs), n_isolated=len(isolated_pairs), by_horizon=by_horizon)

    # ---- primary tolerance: full slicing (session/vol/dow) + random-matched control ----
    pair_events = build_pair_events(swing_points, m, PRIMARY_TOL, side)
    equal_pairs = [e for e in pair_events if e["is_equal"]]
    isolated_pairs = [e for e in pair_events if not e["is_equal"]]

    eq_primary = reach_stats(equal_pairs, m, PRIMARY_HORIZON, side)
    iso_primary = reach_stats(isolated_pairs, m, PRIMARY_HORIZON, side)

    rng = np.random.default_rng(RNG_SEED)
    rand_events = random_matched_control(equal_pairs, m, side, len(equal_pairs), PRIMARY_HORIZON, rng)
    rand_primary = reach_stats(rand_events, m, PRIMARY_HORIZON, side)

    result["primary"] = dict(
        tolerance=PRIMARY_TOL, horizon=PRIMARY_HORIZON,
        equal=summarize_group(eq_primary), isolated=summarize_group(iso_primary),
        random_matched_distance=summarize_group(rand_primary),
        equal_mean_dist=float(np.mean([e["dist"] for e in equal_pairs])) if equal_pairs else None,
        isolated_mean_dist=float(np.mean([e["dist"] for e in isolated_pairs])) if isolated_pairs else None,
    )

    # distance-quantile-matched comparison (equal vs isolated), to control for the proximity confound
    all_dist = np.array([e["dist"] for e in equal_pairs] + [e["dist"] for e in isolated_pairs])
    if len(all_dist) > 40:
        qs = np.quantile(all_dist, [0.25, 0.5, 0.75])
        def bucket(d):
            if d <= qs[0]:
                return "q1"
            if d <= qs[1]:
                return "q2"
            if d <= qs[2]:
                return "q3"
            return "q4"
        eq_by_q, iso_by_q = {}, {}
        eq_rows = reach_stats(equal_pairs, m, PRIMARY_HORIZON, side)
        iso_rows = reach_stats(isolated_pairs, m, PRIMARY_HORIZON, side)
        for r in eq_rows:
            eq_by_q.setdefault(bucket(r["dist"]), []).append(r)
        for r in iso_rows:
            iso_by_q.setdefault(bucket(r["dist"]), []).append(r)
        result["distance_matched"] = {
            q: dict(equal=summarize_group(eq_by_q.get(q, [])), isolated=summarize_group(iso_by_q.get(q, [])))
            for q in ["q1", "q2", "q3", "q4"]
        }

    # session / volatility slices at primary tolerance+horizon
    slices = {}
    for sess in ["asia", "london", "ny", "late"]:
        eq_s = [r for r in eq_primary if r["session"] == sess]
        iso_s = [r for r in iso_primary if r["session"] == sess]
        slices[f"session_{sess}"] = dict(equal=summarize_group(eq_s), isolated=summarize_group(iso_s))
    for vr in ["low", "mid", "high"]:
        eq_v = [r for r in eq_primary if r["vol_regime"] == vr]
        iso_v = [r for r in iso_primary if r["vol_regime"] == vr]
        slices[f"vol_{vr}"] = dict(equal=summarize_group(eq_v), isolated=summarize_group(iso_v))
    result["slices"] = slices

    return result


def main():
    m, meta = load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    m["vol_regime"] = vol_regime(m)

    results = {"edge": "E017", "run_id": "discovery_pass_1_2026-07-21",
               "split_metadata": meta,
               "n_bars": int(len(m)),
               "date_range": [str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])],
               "params": dict(K=K, TOLS=TOLS, PRIMARY_TOL=PRIMARY_TOL, HORIZONS=HORIZONS,
                               PRIMARY_HORIZON=PRIMARY_HORIZON, REACTION_N=REACTION_N, RNG_SEED=RNG_SEED)}

    for side in ["high", "low"]:
        results[side] = run_side(m, side, meta)

    with open("e017_equal_highs_lows_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("split_metadata", json.dumps(meta, indent=2, default=str))
    for side in ["high", "low"]:
        p = results[side]["primary"]
        print(f"=== {side} === n_swing_points={results[side]['n_swing_points']}")
        print(" equal:", p["equal"])
        print(" isolated:", p["isolated"])
        print(" random_matched:", p["random_matched_distance"])
        print(" mean_dist equal/isolated:", p["equal_mean_dist"], p["isolated_mean_dist"])


if __name__ == "__main__":
    main()
