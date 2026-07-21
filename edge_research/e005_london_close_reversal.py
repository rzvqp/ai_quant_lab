"""E005 -- London Close Reversal -- full-profile Discovery-stage analysis (Flow A).

V0 (frozen, verbatim): "The London session close produces recurring reversals."

Run under EDGE_RESEARCH_PROTOCOL.md SSSS1-8 only (SS9 scalping validation explicitly NOT performed,
per the CEO's own priority-shift instruction). Only E005 is authorized this session.

DEFINITIONS PREDECLARED BEFORE ANY OUTCOME WAS INSPECTED:

1. **London close boundary**: 13:00 UTC -- the exact hour `_common.load()`'s own session tagging
   transitions from 'london' (8-13 UTC) to 'ny' (13-21 UTC). Not redefined here; reused exactly.
2. **Pre-close window**: bars with UTC hour in [11, 13) -- the last 2 hours of the London session.
3. **Post-close window**: bars with UTC hour in [13, 15) -- the first 2 hours of the NY session. A
   fixed, symmetric 2-hour choice on each side of the boundary, disclosed, not tuned.
4. **Pre-close trend direction/strength**: sign and ATR-normalized magnitude of
   close(end of pre-close window) - open(start of pre-close window) -- a context feature akin to
   E006's/E008's own trend-direction constructions.
5. **Reversal definition**: the post-close window's own net directional move (same construction)
   OPPOSES the pre-close trend's sign. Reversal RATE = fraction of days where this holds; magnitude =
   the post-close window's ATR-normalized net move size, recorded for reversal days specifically (per
   the registry's own "size of the reversal" observable).
6. **Duration until reversal exhausts**: `_profile.movement_profile()`'s own by-threshold
   time-to-adverse-hit data, called at the close-boundary bar with `direction = -pre_close_direction`
   (predicting the reversal) -- its own "adverse_ttf" at the 1.0x-ATR threshold is used as the
   disclosed "duration until the reversal move exhausts / gives back" proxy.
7. **Minimum window completeness**: at least 75% of the expected bars in each 2-hour window must be
   present (guards against gapped/partial windows), matching the completeness-threshold spirit already
   used in E006.

CONTROLS:
- **Control A -- generic session boundary**: the identical pre/post-window reversal logic applied to
  the OTHER two session boundaries already tagged by `_common.load()` (Asia->London at 08:00, and
  NY->late at 21:00) -- tests whether any reversal tendency is specific to the LONDON close or a
  generic property of "any session transition."
- **Control B -- random-matched baseline**: a random UTC hour (seed=42, excluding the three real
  session-boundary hours) used as a synthetic "boundary" per day, same window construction -- the
  ordinary mean-reversion baseline used throughout this program.

Timeframes: M15 (primary), H1 (secondary, coarser -- both registered for E005, M1/M5 unavailable in
this project's data).
"""
import json
import numpy as np
from scipy.stats import chi2_contingency, mannwhitneyu
from _common import load, vol_regime, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
import _profile as P

PRE_WINDOW_HOURS = 2
POST_WINDOW_HOURS = 2
MIN_COMPLETENESS_FRAC = 0.75
RNG_SEED = 42


def _bars_per_hour(m):
    deltas = m["dt"].diff().dropna().dt.total_seconds() / 3600.0
    median_delta_h = float(deltas.median())
    return 1.0 / median_delta_h if median_delta_h > 0 else 1.0


def _bars_by_date(m):
    dates = m["dt"].dt.date.values
    by_date = {}
    for i, dte in enumerate(dates):
        by_date.setdefault(dte, []).append(i)
    return by_date


def _window_move(idxs, hours, hour_lo, hour_hi, open_, close, atr, bars_per_hour, min_frac=MIN_COMPLETENESS_FRAC):
    win_idxs = [i for i in idxs if hour_lo <= hours[i] < hour_hi]
    expected = (hour_hi - hour_lo) * bars_per_hour
    if len(win_idxs) < max(1, round(expected * min_frac)):
        return None
    atr_ref = atr[win_idxs[0]]
    if not (np.isfinite(atr_ref) and atr_ref > 0):
        return None
    delta = close[win_idxs[-1]] - open_[win_idxs[0]]
    direction = 1 if delta > 0 else (-1 if delta < 0 else 0)
    magnitude = abs(delta) / atr_ref
    return dict(direction=direction, magnitude=float(magnitude), atr_ref=float(atr_ref),
                start_idx=win_idxs[0], end_idx=win_idxs[-1])


def build_boundary_events(m, boundary_hour, bars_per_hour, pre_h=PRE_WINDOW_HOURS, post_h=POST_WINDOW_HOURS):
    hours = m["dt"].dt.hour.values
    open_ = m["open"].values
    close = m["close"].values
    atr = m["atr14"].values
    dow = m["dow"].values
    by_date = _bars_by_date(m)
    events = []
    for dte, idxs in sorted(by_date.items()):
        pre = _window_move(idxs, hours, boundary_hour - pre_h, boundary_hour, open_, close, atr, bars_per_hour)
        post = _window_move(idxs, hours, boundary_hour, boundary_hour + post_h, open_, close, atr, bars_per_hour)
        if pre is None or post is None or pre["direction"] == 0:
            continue
        reversal = post["direction"] != 0 and post["direction"] != pre["direction"]
        # entry/reference bar for the standard movement profile: first bar of the post-close window
        entry_idx = post["start_idx"]
        atr_ref = atr[entry_idx]
        mp = None
        if np.isfinite(atr_ref) and atr_ref > 0:
            mp = P.movement_profile(m, entry_idx, -pre["direction"], atr_ref)
        events.append(dict(
            date=str(dte), dow=str(dow[idxs[0]]), pre_direction=pre["direction"],
            pre_magnitude=pre["magnitude"], post_direction=post["direction"],
            post_magnitude=post["magnitude"], reversal=bool(reversal), entry_idx=entry_idx, mp=mp,
        ))
    return events


def rate(rows, key="reversal"):
    n = len(rows)
    if n == 0:
        return dict(n=0)
    k = sum(1 for r in rows if r[key])
    return dict(n=n, rate=float(k / n))


def chi2_p(rate1, n1, rate2, n2):
    if n1 == 0 or n2 == 0:
        return None
    s1, s2 = round(rate1 * n1), round(rate2 * n2)
    try:
        _, p, _, _ = chi2_contingency([[s1, n1 - s1], [s2, n2 - s2]])
        return float(p)
    except Exception:
        return None


def mwu_p(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(a) < 5 or len(b) < 5:
        return None
    try:
        _, p = mannwhitneyu(a, b, alternative="two-sided")
        return float(p)
    except Exception:
        return None


def describe(x):
    x = np.asarray(x, dtype=float)
    if len(x) == 0:
        return dict(n=0)
    return dict(n=int(len(x)), mean=float(x.mean()), median=float(np.median(x)), std=float(x.std()))


def attach_context(m, events):
    vr_col = m["vol_regime"].values
    for e in events:
        idx = e["entry_idx"]
        e["vol_regime"] = str(vr_col[idx]) if idx < len(vr_col) else None
        e["year"] = P.year_of(m, idx)
    return events


def run_timeframe(tf):
    m, meta = load(tf, data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    m["vol_regime"] = vol_regime(m)
    bph = _bars_per_hour(m)

    events = build_boundary_events(m, 13, bph)
    events = attach_context(m, events)

    overall = rate(events)
    reversal_days = [e for e in events if e["reversal"]]
    magnitude_desc = describe([e["post_magnitude"] for e in reversal_days])

    # duration-until-exhaustion proxy: adverse_ttf at the 1.0x ATR threshold, for reversal days with a valid mp
    ttfs = [e["mp"]["by_threshold"]["1.0"]["favorable_ttf"] for e in reversal_days
            if e.get("mp") and e["mp"]["by_threshold"]["1.0"]["favorable_hit"]]
    duration_desc = describe(ttfs) if ttfs else dict(n=0)

    primary = dict(overall=overall, reversal_magnitude=magnitude_desc, duration_to_exhaust_bars=duration_desc)

    # --- controls: other session boundaries (08:00 Asia->London, 21:00 NY->late) ---
    control_a = {}
    for label, hour in [("asia_to_london_08", 8), ("ny_to_late_21", 21)]:
        ev = build_boundary_events(m, hour, bph)
        r = rate(ev)
        r["p_vs_london_close"] = chi2_p(overall.get("rate", 0), overall.get("n", 0), r.get("rate", 0), r.get("n", 0))
        control_a[label] = r

    # --- control B: random-matched synthetic boundary hour (seed=42), excluding real boundary hours ---
    rng = np.random.default_rng(RNG_SEED)
    excluded = {8, 13, 21}
    candidate_hours = [h for h in range(1, 23) if h not in excluded]  # avoid wrap-around edge effects near midnight
    random_hour = int(rng.choice(candidate_hours))
    ev_b = build_boundary_events(m, random_hour, bph)
    control_b = rate(ev_b)
    control_b["random_hour_used"] = random_hour
    control_b["p_vs_london_close"] = chi2_p(overall.get("rate", 0), overall.get("n", 0),
                                              control_b.get("rate", 0), control_b.get("n", 0))

    # --- context slices ---
    slices = {}
    for dname in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        sub = [e for e in events if e["dow"] == dname]
        r = rate(sub)
        r["p_vs_overall"] = chi2_p(r.get("rate", 0), r.get("n", 0), overall.get("rate", 0), overall.get("n", 0))
        slices[f"dow_{dname}"] = r
    for vr in ["low", "mid", "high"]:
        sub = [e for e in events if e["vol_regime"] == vr]
        r = rate(sub)
        r["p_vs_overall"] = chi2_p(r.get("rate", 0), r.get("n", 0), overall.get("rate", 0), overall.get("n", 0))
        slices[f"vol_{vr}"] = r
    # pre-close trend strength tercile
    mags = [e["pre_magnitude"] for e in events]
    if mags:
        q1, q2 = np.percentile(mags, [33.33, 66.67])
        for label, lo, hi in [("weak", None, q1), ("mid", q1, q2), ("strong", q2, None)]:
            if lo is None:
                sub = [e for e in events if e["pre_magnitude"] <= hi]
            elif hi is None:
                sub = [e for e in events if e["pre_magnitude"] > lo]
            else:
                sub = [e for e in events if lo < e["pre_magnitude"] <= hi]
            r = rate(sub)
            r["p_vs_overall"] = chi2_p(r.get("rate", 0), r.get("n", 0), overall.get("rate", 0), overall.get("n", 0))
            slices[f"pretrend_{label}"] = r

    # --- yearly stability ---
    by_year = {}
    for e in events:
        by_year.setdefault(e["year"], []).append(e)
    yearly = {str(y): rate(rs) for y, rs in sorted(by_year.items())}

    return dict(
        timeframe=tf, split_metadata=meta, n_bars=int(len(m)),
        date_range=[str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])],
        n_events=len(events),
        primary=primary, control_A_other_boundaries=control_a, control_B_random_matched=control_b,
        slices=slices, yearly_stability=yearly,
    )


def main():
    results = {"edge": "E005", "edge_id": "E005", "hypothesis_version": "V0",
               "run_id": "discovery_pass_1_full_profile_2026-07-21",
               "timeframes_tested": [], "timeframes_unavailable": {
                   "M1": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)",
                   "M5": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)"},
               "params": dict(PRE_WINDOW_HOURS=PRE_WINDOW_HOURS, POST_WINDOW_HOURS=POST_WINDOW_HOURS,
                              MIN_COMPLETENESS_FRAC=MIN_COMPLETENESS_FRAC, RNG_SEED=RNG_SEED,
                              movement_horizons=P.HORIZONS, atr_thresholds=P.ATR_THRESHOLDS),
               "by_timeframe": {}}

    for tf in ["M15", "H1"]:
        print("=== running", tf, "===")
        res = run_timeframe(tf)
        results["by_timeframe"][tf] = res
        results["timeframes_tested"].append(tf)
        print(tf, "n_events", res["n_events"], "overall", res["primary"]["overall"])
        print(" reversal_magnitude:", res["primary"]["reversal_magnitude"])
        print(" duration_to_exhaust_bars:", res["primary"]["duration_to_exhaust_bars"])
        print(" control_A (other boundaries):", res["control_A_other_boundaries"])
        print(" control_B (random hour):", res["control_B_random_matched"])
        for k, v in res["slices"].items():
            print(" slice", k, v)

    with open("e005_london_close_reversal_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)


if __name__ == "__main__":
    main()
