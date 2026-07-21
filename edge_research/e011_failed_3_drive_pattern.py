"""E011 -- Failed 3 Drive Pattern -- full-profile Discovery-stage analysis (Flow A).

V0 (frozen, verbatim): "A three-push ('three drive') pattern that fails to complete its third leg
produces a reliable reversal signal."

Run under EDGE_RESEARCH_PROTOCOL.md SSSS1-8 only (SS9 scalping validation explicitly NOT performed,
per the CEO's own priority-shift instruction). Only E011 is authorized this session. First edge in
this program to use a swing/leg (harmonic-style) detector rather than the OB/FVG/CHoCH/compression or
session-timing families already studied -- deliberately diversifies pattern-class risk per the
2026-07-21 priority audit.

DEFINITIONS PREDECLARED BEFORE ANY OUTCOME WAS INSPECTED:

1. **Swing point (fractal, k=3)**: a bar is a confirmed swing high if its high exceeds the high of the
   3 bars immediately before AND after it; a confirmed swing low is the mirror on lows. k=3 matches
   E009's own already-used fractal-k convention in this program (methodological consistency); k=5 and
   k=8 (E009's own other tested values) are run as a disclosed sensitivity check, not a search for a
   favorable value.
2. **Lookahead-safe confirmation**: a swing point at bar i is only KNOWN to be a swing point once bars
   i+1..i+k have been observed -- so the swing is timestamped as "confirmed" at bar i+k, not at bar i
   itself. All forward-looking measurement starts from the confirmation bar, never from the swing bar
   itself, to avoid look-ahead bias.
3. **Zigzag simplification**: consecutive same-type swings (two swing highs with no intervening swing
   low, or vice versa) are collapsed to keep only the more extreme one -- the standard zigzag
   convention, disclosed, not tuned.
4. **Three-drive pattern (symmetry-agnostic construction, deliberately avoiding a Fibonacci-ratio
   curve-fit)**: five consecutive alternating swing points P0(low)-P1(high)-P2(low)-P3(high)-P4(low)
   for a bullish (upward) 3-drive setup, requiring only P3 > P1 (drive 2 exceeds drive 1) -- no
   specific retracement-ratio or extension-ratio requirement is part of the DETECTION criteria (that
   would risk overfitting to a specific harmonic convention not stated in V0). The bearish mirror uses
   P0(high)-P1(low)-P2(high)-P3(low)-P4(high) with P3 < P1.
5. **Completed vs. failed third leg**: after P4, the next confirmed swing point in the drive direction
   (a swing high for the bullish case) is checked: if it EXCEEDS P3, the 3-drive is COMPLETED; if it
   does NOT exceed P3 (a lower or equal high), the third leg FAILED. Only the first such subsequent
   swing point is used (no chasing multiple further attempts).
6. **Leg symmetry (descriptive only, NOT a detection criterion)**: `leg2_leg1_ratio = (P3-P2)/(P1-P0)`
   (bullish case; magnitudes), recorded and sliced into terciles, exactly analogous to how
   "compression_ratio" and "range width" were used as descriptive slices (not detection thresholds) in
   E014 and E006.
7. **Response horizon**: 50 bars -- the shared ceiling of `_profile.HORIZONS`, unchanged across the
   whole program.
8. **Outcome definition**: `_profile.movement_profile()` called with `direction = -drive_direction`
   (predicting a REVERSAL against the completed drives) -- its own "continuation" output therefore
   means "the predicted reversal happened," its own "reversal" output means "the drives continued
   instead" (the opposite of V0's prediction), and "stall" is unchanged. Relabeled in all outputs as
   `reversal_confirmed` / `drive_continued` / `stall` to avoid this terminology collision.

CONTROLS:
- **Control A -- generic swing point**: an ordinary, isolated swing high/low with NO 3-drive structure
  requirement at all (just any confirmed swing point), tested for the same "does the market reverse
  from here" question -- isolates whether the 3-drive's specific 5-point structure adds anything beyond
  "this is a local extreme."
- **Control B -- random-matched baseline**: fully synthetic random points (seed=42), the same
  convention as E006/E010/E012/E014/E015's own random-matched controls -- the ordinary
  mean-reversion baseline.

Timeframes: M15, H1, H4 -- all three registered for E011 and present in the clean dataset.
"""
import json
import numpy as np
from scipy.stats import chi2_contingency
from _common import load, vol_regime, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
import _profile as P

FRACTAL_K_PRIMARY = 3
FRACTAL_K_VARIANTS = [3, 5, 8]
RNG_SEED = 42


def detect_swings(m, k):
    """Returns a time-ordered, zigzag-simplified list of dicts: {idx, kind ('high'/'low'), price,
    confirm_idx (idx+k, the first bar at which this swing point is knowable)}."""
    h = m["high"].values
    l = m["low"].values
    n = len(m)
    raw = []
    for i in range(k, n - k):
        if h[i] == max(h[i - k:i + k + 1]) and h[i] > max(h[i - k:i]) and h[i] > max(h[i + 1:i + k + 1]):
            raw.append(dict(idx=i, kind="high", price=float(h[i]), confirm_idx=i + k))
        if l[i] == min(l[i - k:i + k + 1]) and l[i] < min(l[i - k:i]) and l[i] < min(l[i + 1:i + k + 1]):
            raw.append(dict(idx=i, kind="low", price=float(l[i]), confirm_idx=i + k))
    raw.sort(key=lambda x: x["idx"])

    # zigzag simplification: collapse consecutive same-kind swings, keep the more extreme
    simplified = []
    for s in raw:
        if simplified and simplified[-1]["kind"] == s["kind"]:
            if s["kind"] == "high" and s["price"] > simplified[-1]["price"]:
                simplified[-1] = s
            elif s["kind"] == "low" and s["price"] < simplified[-1]["price"]:
                simplified[-1] = s
            # else: keep existing (less extreme new point discarded)
        else:
            simplified.append(s)
    return simplified


def detect_3drive_events(m, swings):
    """Scans the zigzag sequence for P0-P1-P2-P3-P4 quintuples (bullish: low-high-low-high-low with
    P3>P1; bearish mirror), then classifies the next swing in the drive direction as completed/failed."""
    events = []
    for i in range(len(swings) - 4):
        p0, p1, p2, p3, p4 = swings[i:i + 5]
        kinds = (p0["kind"], p1["kind"], p2["kind"], p3["kind"], p4["kind"])
        if kinds == ("low", "high", "low", "high", "low") and p3["price"] > p1["price"]:
            drive_direction = 1  # bullish 3-drive-up
            # next swing high after p4
            nxt = next((s for s in swings[i + 5:] if s["kind"] == "high"), None)
            if nxt is None:
                continue
            completed = nxt["price"] > p3["price"]
            events.append(dict(p0=p0, p1=p1, p2=p2, p3=p3, p4=p4, next_swing=nxt,
                                drive_direction=drive_direction, completed=completed,
                                leg1=p1["price"] - p0["price"], leg2=p3["price"] - p2["price"]))
        elif kinds == ("high", "low", "high", "low", "high") and p3["price"] < p1["price"]:
            drive_direction = -1  # bearish 3-drive-down
            nxt = next((s for s in swings[i + 5:] if s["kind"] == "low"), None)
            if nxt is None:
                continue
            completed = nxt["price"] < p3["price"]
            events.append(dict(p0=p0, p1=p1, p2=p2, p3=p3, p4=p4, next_swing=nxt,
                                drive_direction=drive_direction, completed=completed,
                                leg1=p0["price"] - p1["price"], leg2=p2["price"] - p3["price"]))
    return events


def attach_outcome(m, ev):
    """Reference/entry point: the next_swing's own CONFIRMATION bar (lookahead-safe) -- for a failed
    3rd leg, this is the lower-high (or higher-low) point itself, once known; for a completed 3-drive,
    this is the new extreme, once known."""
    idx = ev["next_swing"]["confirm_idx"]
    atr = m["atr14"].values
    n = len(m)
    if idx >= n:
        return None
    atr_ref = atr[idx]
    if not (np.isfinite(atr_ref) and atr_ref > 0):
        return None
    reversal_direction = -ev["drive_direction"]  # V0 predicts a reversal AGAINST the drives
    mp = P.movement_profile(m, idx, reversal_direction, atr_ref)
    if mp is None:
        return None
    ctx = P.context_features(m, idx)
    row = dict(entry_idx=idx, drive_direction=ev["drive_direction"], completed=ev["completed"],
               leg1_atr=abs(ev["leg1"]) / atr_ref, leg2_atr=abs(ev["leg2"]) / atr_ref,
               leg_symmetry=abs(ev["leg2"]) / abs(ev["leg1"]) if ev["leg1"] != 0 else None,
               reversal_confirmed=(mp["outcome"] == "continuation"),
               drive_continued=(mp["outcome"] == "reversal"),
               stall=(mp["outcome"] == "stall"), mp=mp)
    row.update(ctx)
    row["year"] = P.year_of(m, idx)
    return row


def generic_swing_control(m, swings, n_target, rng):
    """Control A: ordinary, isolated swing points (any confirmed swing, no 3-drive structure), tested
    for the same "does price reverse from here" question, direction = away from the swing (a swing
    high predicts reversal down, a swing low predicts reversal up -- the natural, generic prediction
    for an isolated local extreme, not tied to any drive-count)."""
    atr = m["atr14"].values
    n = len(m)
    valid = [s for s in swings if s["confirm_idx"] < n]
    chosen_idx = rng.choice(len(valid), size=min(n_target, len(valid)), replace=False)
    rows = []
    for i in chosen_idx:
        s = valid[i]
        idx = s["confirm_idx"]
        atr_ref = atr[idx]
        if not (np.isfinite(atr_ref) and atr_ref > 0):
            continue
        direction = -1 if s["kind"] == "high" else 1  # predict reversal away from the extreme
        mp = P.movement_profile(m, idx, direction, atr_ref)
        if mp is None:
            continue
        rows.append(dict(reversal_confirmed=(mp["outcome"] == "continuation")))
    return rows


def random_matched_control(m, n_target, rng):
    close = m["close"].values
    atr = m["atr14"].values
    n = len(m)
    max_start = n - 60
    valid_idx = np.where(np.isfinite(atr[:max_start]) & (atr[:max_start] > 0))[0]
    valid_idx = valid_idx[valid_idx > 20]
    chosen = rng.choice(valid_idx, size=min(n_target, len(valid_idx)), replace=False)
    rows = []
    for idx in chosen:
        atr_ref = atr[idx]
        direction = int(rng.choice([1, -1]))
        mp = P.movement_profile(m, idx, direction, atr_ref)
        if mp is None:
            continue
        rows.append(dict(reversal_confirmed=(mp["outcome"] == "continuation")))
    return rows


def rate(rows, key="reversal_confirmed"):
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


def tercile_labels(values):
    v = np.asarray(values, dtype=float)
    q1, q2 = np.percentile(v, [33.33, 66.67])
    return np.where(v <= q1, "low", np.where(v <= q2, "mid", "high"))


def run_timeframe(tf):
    m, meta = load(tf, data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    d1, _ = load("D1", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    m["vol_regime"] = vol_regime(m)
    m = P.attach_daily_context(m, d1)

    swings = detect_swings(m, FRACTAL_K_PRIMARY)
    raw_events = detect_3drive_events(m, swings)
    rows = [attach_outcome(m, ev) for ev in raw_events]
    rows = [r for r in rows if r is not None]

    failed = [r for r in rows if not r["completed"]]
    completed = [r for r in rows if r["completed"]]

    primary = dict(
        failed=rate(failed), completed=rate(completed),
        p_failed_vs_completed=chi2_p(rate(failed).get("rate", 0), rate(failed).get("n", 0),
                                       rate(completed).get("rate", 0), rate(completed).get("n", 0)),
    )

    # --- controls (matched to the FAILED population's size, the primary V0 population) ---
    rng = np.random.default_rng(RNG_SEED)
    n_target = len(failed)
    control_a = generic_swing_control(m, swings, n_target, rng)
    control_b = random_matched_control(m, n_target, rng)
    controls = dict(
        control_A_generic_swing=dict(
            overall=rate(control_a),
            p_vs_failed=chi2_p(rate(failed).get("rate", 0), rate(failed).get("n", 0),
                                 rate(control_a).get("rate", 0), rate(control_a).get("n", 0))),
        control_B_random_matched=dict(
            overall=rate(control_b),
            p_vs_failed=chi2_p(rate(failed).get("rate", 0), rate(failed).get("n", 0),
                                 rate(control_b).get("rate", 0), rate(control_b).get("n", 0))),
    )
    cross_control_p = chi2_p(rate(control_a).get("rate", 0), rate(control_a).get("n", 0),
                              rate(control_b).get("rate", 0), rate(control_b).get("n", 0))

    # --- examination variables (failed population only) ---
    slices = {}

    def slice_stat(rows_src, key, val):
        sub = [r for r in rows_src if r.get(key) == val]
        r = rate(sub)
        r["p_vs_failed_overall"] = chi2_p(r.get("rate", 0), r.get("n", 0),
                                            rate(failed).get("rate", 0), rate(failed).get("n", 0))
        return r

    for vr in ["low", "mid", "high"]:
        slices[f"vol_{vr}"] = slice_stat(failed, "vol_regime", vr)
    for d, name in [(1, "bullish_setup"), (-1, "bearish_setup")]:
        slices[f"direction_{name}"] = slice_stat(failed, "drive_direction", d)

    sym_vals = [r["leg_symmetry"] for r in failed if r.get("leg_symmetry") is not None]
    if sym_vals:
        sym_labels = tercile_labels(sym_vals)
        sym_rows = [r for r in failed if r.get("leg_symmetry") is not None]
        for i, r in enumerate(sym_rows):
            r["symmetry_tercile"] = str(sym_labels[i])
        for tercile in ["low", "mid", "high"]:
            slices[f"symmetry_{tercile}"] = slice_stat(sym_rows, "symmetry_tercile", tercile)

    # --- robustness: fractal-k sensitivity ---
    k_sensitivity = {}
    for k in FRACTAL_K_VARIANTS:
        if k == FRACTAL_K_PRIMARY:
            k_sensitivity[str(k)] = dict(n_events=len(rows), failed=rate(failed), completed=rate(completed))
            continue
        swings_k = detect_swings(m, k)
        events_k = detect_3drive_events(m, swings_k)
        rows_k = [attach_outcome(m, ev) for ev in events_k]
        rows_k = [r for r in rows_k if r is not None]
        failed_k = [r for r in rows_k if not r["completed"]]
        completed_k = [r for r in rows_k if r["completed"]]
        k_sensitivity[str(k)] = dict(n_events=len(rows_k), failed=rate(failed_k), completed=rate(completed_k))

    # --- yearly stability (failed population) ---
    by_year = {}
    for r in failed:
        by_year.setdefault(r["year"], []).append(r)
    yearly = {str(y): rate(rs) for y, rs in sorted(by_year.items())}

    return dict(
        timeframe=tf, split_metadata=meta, n_bars=int(len(m)),
        date_range=[str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])],
        n_swings=len(swings), n_3drive_events=len(rows),
        primary=primary, controls=controls, cross_control_A_vs_B_p=cross_control_p,
        slices=slices, k_sensitivity=k_sensitivity, yearly_stability=yearly,
    )


def main():
    results = {"edge": "E011", "edge_id": "E011", "hypothesis_version": "V0",
               "run_id": "discovery_pass_1_full_profile_2026-07-21",
               "timeframes_tested": [], "timeframes_unavailable": {
                   "M1": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)",
                   "M5": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)"},
               "params": dict(FRACTAL_K_PRIMARY=FRACTAL_K_PRIMARY, FRACTAL_K_VARIANTS=FRACTAL_K_VARIANTS,
                              RNG_SEED=RNG_SEED, movement_horizons=P.HORIZONS, atr_thresholds=P.ATR_THRESHOLDS),
               "by_timeframe": {}}

    for tf in ["M15", "H1", "H4"]:
        print("=== running", tf, "===")
        res = run_timeframe(tf)
        results["by_timeframe"][tf] = res
        results["timeframes_tested"].append(tf)
        print(tf, "n_swings", res["n_swings"], "n_3drive_events", res["n_3drive_events"])
        print(" primary:", res["primary"])
        print(" controls:", res["controls"], "cross_control_A_vs_B_p:", res["cross_control_A_vs_B_p"])
        for k, v in res["slices"].items():
            print(" slice", k, v)
        print(" k_sensitivity:", res["k_sensitivity"])

    with open("e011_failed_3_drive_pattern_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)


if __name__ == "__main__":
    main()
