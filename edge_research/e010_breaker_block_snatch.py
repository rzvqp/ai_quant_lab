"""E010 -- Breaker Block Snatch -- full-profile Discovery-stage analysis (Flow A).

V0 (frozen, verbatim): "A failed order block that flips polarity ('breaker') is often revisited and
respected as support/resistance in the opposite direction."

Run under the post-remediation regime (EDGE_RESEARCH_PROTOCOL.md SS8) -- data loads exclusively via
`_common.load()`; the full-profile template (movement/context/robustness) uses `_profile.py`.

Method (disclosed, exploratory -- Discovery stage only, no tuning/optimization):
1. **Order block (OB) detection**: a displacement bar i is one where range[i] = high[i]-low[i] >
   1.5 x ATR14[i-1] (prior bar's ATR, so the displacement bar's own range never inflates its own
   reference) AND a strong directional body (|close-open| >= 0.5 x range). If bullish displacement, the
   last BEARISH (close<open) bar within the preceding 10 bars is the bullish-OB candidate (zone =
   [low,high] of that bar); if bearish displacement, the last BULLISH bar within 10 prior bars is the
   bearish-OB candidate. 10-bar lookback and 1.5x/0.5x thresholds are plain, disclosed defaults --
   swept for sensitivity, not searched for a favorable result.
2. **Breaker flip**: a bullish OB flips to a bearish breaker the first time a LATER bar's CLOSE falls
   below the OB zone's low (a decisive violation, not just an intrabar wick); bearish OB -> bullish
   breaker symmetric on a close above the zone's high.
3. **V0 test**: after the flip, does price REVISIT the OB zone, and does it REACT (reverse) in the new,
   flipped-polarity direction? Uses `_profile.py::movement_profile()` -- direction = the flip's own new
   polarity (e.g. a bullish-OB-turned-bearish-breaker predicts price falls on a later approach).
4. **Controls**:
   - **Unflipped-OB control**: OBs that are NEVER later closed-through within the test horizon --
     tested for reaction in their ORIGINAL (unflipped) polarity, the natural "is flipping special"
     baseline.
   - **Random-matched-distance control** (seed=42): synthetic zones at random bar locations, distance
     profile resampled from the breaker group's own empirical distances -- tests generic
     proximity/travel explanations.
5. **Timeframes**: M15 and H1 (both on disk); M1/M5 are NOT available anywhere in this project's data
   (`EDGE_DISCOVERY_ROADMAP.md` SS1's own, previously-established gap finding) -- documented, not
   re-derived.
6. **Context slices**: session, simple trend context (20-bar EMA-slope sign, ATR-normalized, disclosed
   not tuned), volatility regime, day-of-week, and a daily-expansion flag (has today already consumed
   >=70% of ADR14 in either direction) via `_profile.py::attach_daily_context()`.
7. **Robustness**: displacement-threshold sensitivity (1.2x/1.5x/2.0x ATR), yearly subperiod stability.
"""
import json
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from _common import load, vol_regime, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
import _profile as P

LOOKBACK_OB = 10
DISP_MULTS = [1.2, 1.5, 2.0]
PRIMARY_DISP = 1.5
BODY_FRAC = 0.5
REVISIT_HORIZON = 480  # 5 trading days
RNG_SEED = 42


def detect_obs_and_breakers(m, disp_mult):
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

    # find breaker flip: first later CLOSE beyond the OB zone in the opposite direction
    breakers, unflipped = [], []
    for e in events:
        j = e["ob_idx"]
        zone_low, zone_high = e["ob_low"], e["ob_high"]
        end = min(j + 1 + REVISIT_HORIZON, n)
        flip_idx = None
        if e["ob_polarity"] == "bull":
            seg = c[j + 1:end]
            hit = np.where(seg < zone_low)[0]
            if len(hit):
                flip_idx = j + 1 + int(hit[0])
        else:
            seg = c[j + 1:end]
            hit = np.where(seg > zone_high)[0]
            if len(hit):
                flip_idx = j + 1 + int(hit[0])
        if flip_idx is not None:
            new_dir = -1 if e["ob_polarity"] == "bull" else 1  # bull OB -> bearish breaker -> predict down
            breakers.append(dict(**e, confirm_idx=flip_idx, direction=new_dir))
        else:
            orig_dir = 1 if e["ob_polarity"] == "bull" else -1
            unflipped.append(dict(**e, confirm_idx=j, direction=orig_dir))
    return breakers, unflipped


def revisit_and_react(m, ev, horizon=REVISIT_HORIZON):
    idx = ev["confirm_idx"]
    zone_low, zone_high = ev["ob_low"], ev["ob_high"]
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


def random_matched(m, real_rows, group_label, n_events, horizon, rng):
    close = m["close"].values
    atr = m["atr14"].values
    n = len(m)
    dists = []
    for r in real_rows:
        if r.get("revisited") and r.get("dist") is not None:
            dists.append(r["dist"])
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
        zone_low, zone_high = zone_center - 0.25 * a, zone_center + 0.25 * a
        end = min(idx + 1 + horizon, n)
        revisited = bool(((m["low"].values[idx + 1:end] <= zone_high) & (m["high"].values[idx + 1:end] >= zone_low)).any())
        out.append(dict(revisited=revisited))
    return out


def build_rows(m, events, horizon=REVISIT_HORIZON):
    rows = []
    for e in events:
        r = revisit_and_react(m, e, horizon)
        if r is None:
            continue
        row = dict(e)
        row["revisited"] = r["revisited"]
        atr_ref = m["atr14"].values[e["confirm_idx"]]
        row["dist"] = None
        if r["revisited"] and np.isfinite(atr_ref) and atr_ref > 0:
            row["ttr_bars"] = r["ttr_bars"]
            row["dist"] = (abs((e["ob_low"] + e["ob_high"]) / 2 - m["close"].values[e["confirm_idx"]]) / atr_ref)
        if r["revisited"] and r["mp"] is not None:
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


def outcome_summary(rows):
    n = len(rows)
    if n == 0:
        return dict(n=0)
    revisit_rate = float(np.mean([r["revisited"] for r in rows]))
    reacted = [r for r in rows if r["revisited"] and r["outcome"] is not None]
    n_reacted = len(reacted)
    out = dict(n=n, revisit_rate=revisit_rate, n_revisited_with_outcome=n_reacted)
    if reacted:
        outs = [r["outcome"] for r in reacted]
        out["continuation_rate"] = float(np.mean([o == "continuation" for o in outs]))
        out["reversal_rate"] = float(np.mean([o == "reversal" for o in outs]))
        out["stall_rate"] = float(np.mean([o == "stall" for o in outs]))
        mps = [r["mp"] for r in reacted]
        out["movement_summary"] = P.summarize_movement(mps)
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
    d1, meta_d1 = load("D1", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    m["vol_regime"] = vol_regime(m)
    m = P.attach_daily_context(m, d1)

    breakers, unflipped = detect_obs_and_breakers(m, PRIMARY_DISP)
    breaker_rows = build_rows(m, breakers)
    unflipped_rows = build_rows(m, unflipped)

    rng = np.random.default_rng(RNG_SEED)
    rand_rows = random_matched(m, breaker_rows, "breaker", len(breaker_rows), REVISIT_HORIZON, rng)
    rand_revisit_rate = float(np.mean([r["revisited"] for r in rand_rows])) if rand_rows else None

    b_sum = outcome_summary(breaker_rows)
    u_sum = outcome_summary(unflipped_rows)

    p_revisit_vs_unflipped = chi2_p(b_sum.get("revisit_rate", 0), b_sum.get("n", 0),
                                     u_sum.get("revisit_rate", 0), u_sum.get("n", 0))
    p_revisit_vs_random = chi2_p(b_sum.get("revisit_rate", 0), b_sum.get("n", 0),
                                  rand_revisit_rate or 0, len(rand_rows)) if rand_rows else None
    p_reaction_vs_unflipped = None
    if b_sum.get("n_revisited_with_outcome", 0) > 20 and u_sum.get("n_revisited_with_outcome", 0) > 20:
        p_reaction_vs_unflipped = chi2_p(b_sum.get("continuation_rate", 0), b_sum["n_revisited_with_outcome"],
                                          u_sum.get("continuation_rate", 0), u_sum["n_revisited_with_outcome"])

    slices = {}
    for sess in ["asia", "london", "ny", "late"]:
        bs = [r for r in breaker_rows if r["session"] == sess]
        slices[f"session_{sess}"] = outcome_summary(bs)
    for vr in ["low", "mid", "high"]:
        bv = [r for r in breaker_rows if r["vol_regime"] == vr]
        slices[f"vol_{vr}"] = outcome_summary(bv)
    for tr in ["bull", "bear", "range"]:
        bt = [r for r in breaker_rows if r["trend"] == tr]
        slices[f"trend_{tr}"] = outcome_summary(bt)
    for dow in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        bd = [r for r in breaker_rows if r["dow"] == dow]
        slices[f"dow_{dow}"] = outcome_summary(bd)

    # displacement-threshold sensitivity
    disp_sensitivity = {}
    for mult in DISP_MULTS:
        b2, u2 = detect_obs_and_breakers(m, mult)
        b2_rows = build_rows(m, b2)
        disp_sensitivity[str(mult)] = dict(n_breakers=len(b2_rows),
                                            summary=outcome_summary(b2_rows))

    # yearly subperiod stability (breaker group)
    by_year = {}
    for r in breaker_rows:
        by_year.setdefault(r["year"], []).append(r)
    yearly = {str(y): outcome_summary(rs) for y, rs in sorted(by_year.items())}

    return dict(
        timeframe=tf, split_metadata=meta, n_bars=int(len(m)),
        date_range=[str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])],
        n_breakers=len(breaker_rows), n_unflipped=len(unflipped_rows), n_random=len(rand_rows),
        primary=dict(breaker=b_sum, unflipped_control=u_sum, random_matched_revisit_rate=rand_revisit_rate,
                     p_revisit_vs_unflipped=p_revisit_vs_unflipped, p_revisit_vs_random=p_revisit_vs_random,
                     p_reaction_vs_unflipped=p_reaction_vs_unflipped),
        slices=slices, displacement_sensitivity=disp_sensitivity, yearly_stability=yearly,
    )


def main():
    results = {"edge": "E010", "edge_id": "E010", "hypothesis_version": "V0",
               "run_id": "discovery_pass_1_full_profile_2026-07-22",
               "timeframes_tested": [], "timeframes_unavailable": {
                   "M1": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)",
                   "M5": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)"},
               "params": dict(LOOKBACK_OB=LOOKBACK_OB, DISP_MULTS=DISP_MULTS, PRIMARY_DISP=PRIMARY_DISP,
                               BODY_FRAC=BODY_FRAC, REVISIT_HORIZON=REVISIT_HORIZON, RNG_SEED=RNG_SEED,
                               movement_horizons=P.HORIZONS, atr_thresholds=P.ATR_THRESHOLDS),
               "by_timeframe": {}}

    for tf in ["M15", "H1"]:
        print("=== running", tf, "===")
        res = run_timeframe(tf)
        results["by_timeframe"][tf] = res
        results["timeframes_tested"].append(tf)
        p = res["primary"]
        print(tf, "n_breakers", res["n_breakers"], "n_unflipped", res["n_unflipped"])
        print(" breaker:", p["breaker"])
        print(" unflipped:", p["unflipped_control"])
        print(" random_revisit_rate:", p["random_matched_revisit_rate"])
        print(" p_revisit_vs_unflipped:", p["p_revisit_vs_unflipped"],
              "p_revisit_vs_random:", p["p_revisit_vs_random"],
              "p_reaction_vs_unflipped:", p["p_reaction_vs_unflipped"])

    with open("e010_breaker_block_snatch_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)


if __name__ == "__main__":
    main()
