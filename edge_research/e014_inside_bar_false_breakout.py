"""E014 -- Inside Bar False Breakout -- full-profile Discovery-stage analysis (Flow A).

V0 (frozen, verbatim): "A false breakout of an inside-bar range frequently reverses back through the
range, offering a fade entry."

Run under EDGE_RESEARCH_PROTOCOL.md SSSS1-8 only (SS9 scalping validation explicitly NOT performed,
per the CEO's own priority-shift instruction). Only E014 is authorized this session -- no other edge
started in parallel.

DEFINITIONS PREDECLARED BEFORE ANY OUTCOME WAS INSPECTED (per the CEO's explicit requirement):

1. **Inside bar**: a bar whose high <= the immediately preceding bar's ("mother bar") high AND whose
   low >= the mother bar's low (strict containment, the standard, parameter-free technical definition).
2. **Nested/overlapping inside bars**: a chain of consecutive bars can each be inside the one before it
   (progressively tighter compression). ONLY THE FIRST inside bar in such a chain is used as a primary
   event (its own predecessor is a normal, non-inside bar) -- later bars in the same chain are treated
   as part of the same event, not counted separately. This avoids within-chain pseudo-replication, the
   same rationale as E006's first-breakout-of-day-only and E015's visit-1 priority conventions.
3. **Breakout**: the first bar after the inside bar whose CLOSE is beyond the inside bar's own range
   (> inside_high for an upside breakout, < inside_low for downside) -- same "close beyond the level"
   convention as E006, for methodological consistency across the program.
4. **False breakout (fade-through) definition**: V0's own wording is "reverses back THROUGH the range"
   -- read literally (a full traversal, not merely a return to neutral), so the PRIMARY definition
   requires price to subsequently CLOSE beyond the OPPOSITE boundary of the inside bar's range within
   the response horizon. A secondary, weaker metric (does price merely close back inside the range at
   all) is also recorded for comparison, but is not the primary V0 test.
5. **Response horizon**: 50 bars (the ceiling of `_profile.HORIZONS`, shared with every other edge's
   movement-profile ceiling -- avoids introducing a second, arbitrary time parameter alongside the
   standard profiling horizons).
6. **Invalidation rule**: if price never closes beyond either boundary within a generous 200-bar
   look-forward window, the inside bar is classified NO_BREAKOUT and excluded from the false-breakout-
   rate analysis entirely (the event never triggered, so there's nothing to classify as true/false).
   Inside bars with zero range, or an invalid (non-finite/non-positive) ATR reference at breakout, are
   also excluded.
7. **Dual-side (whipsaw) breakouts**: handled naturally by the fade-through definition itself -- if
   price closes above the inside bar's high and later closes below its low (or vice versa) within the
   horizon, that IS a confirmed false breakout under definition (4); no special-case logic is needed.
8. **First vs. repeated breakout attempt**: after the first attempt resolves as NOT a confirmed
   fade-through (either the horizon expires with price still outside without crossing the opposite
   side, or price returns inside the range without confirming the opposite side), a SECOND attempt is
   tracked if a new close beyond either boundary occurs within the remaining horizon budget. Attempts
   are bucketed 1st vs. 2nd-or-later (parallel to E015's visit-number bucketing, simplified to two
   buckets given the added complexity here).

CONTROLS (distinguishing 4 candidate explanations, per the CEO's explicit requirement):
- **Primary**: real inside bars (strict containment).
- **Control B -- generic single-bar breakout**: a random sample of ordinary bars (no compression or
  containment condition at all) used as the reference range with identical breakout/fade logic --
  isolates whether "breaking a recent single bar's real range" alone produces the fade tendency.
- **Control C -- generic compression**: bars in the lowest tercile of (own range / ATR14-prior),
  WITHOUT requiring strict inside-bar containment -- isolates compression from containment.
- **Control D -- ordinary mean reversion baseline**: fully synthetic, ATR-sized random-matched ranges
  at random points (seed=42), the same convention already used by E010/E012/E015 -- the most generic
  baseline, unrelated to any real bar structure at all.

Timeframes: M15, H1, H4 (all three registered for E014 and present in the clean dataset).
"""
import json
import numpy as np
from scipy.stats import chi2_contingency
from _common import load, vol_regime, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
import _profile as P

RESPONSE_HORIZON_BARS = max(P.HORIZONS)  # 50 -- shared ceiling with every other edge's profiling
NO_BREAKOUT_WINDOW_BARS = 200  # generous look-forward before giving up and calling it NO_BREAKOUT
MAX_ATTEMPT_BUCKET = 2  # 1st, 2nd-or-later
RNG_SEED = 42


def detect_inside_bars(m):
    """Returns first-in-chain inside bars only. Each event: mother_idx, inside_idx (last bar of a
    single-inside-bar event -- for a chain, this is intentionally the FIRST inside bar of the chain,
    per definition (2); later chain members are not separately counted)."""
    h = m["high"].values
    l = m["low"].values
    n = len(m)
    events = []
    prev_was_inside = False
    for i in range(1, n):
        is_inside = (h[i] <= h[i - 1]) and (l[i] >= l[i - 1])
        if is_inside and not prev_was_inside:
            events.append(dict(mother_idx=i - 1, inside_idx=i,
                                mother_high=float(h[i - 1]), mother_low=float(l[i - 1]),
                                inside_high=float(h[i]), inside_low=float(l[i])))
        prev_was_inside = is_inside
    return events


def _fade_track(m, ref_idx, ref_high, ref_low, horizon=RESPONSE_HORIZON_BARS,
                 no_breakout_window=NO_BREAKOUT_WINDOW_BARS):
    """Shared attempt-tracking state machine for a reference range [ref_low, ref_high] starting the
    scan at ref_idx+1. Returns a dict describing attempt 1 (and attempt 2 if applicable)."""
    close = m["close"].values
    n = len(m)
    scan_end = min(ref_idx + 1 + no_breakout_window, n)
    i = ref_idx + 1
    attempts = []
    while i < scan_end and len(attempts) < MAX_ATTEMPT_BUCKET:
        # find the next close beyond either boundary from position i onward
        breakout_i = None
        direction = None
        for j in range(i, scan_end):
            if close[j] > ref_high:
                breakout_i, direction = j, 1
                break
            if close[j] < ref_low:
                breakout_i, direction = j, -1
                break
        if breakout_i is None:
            break
        end = min(breakout_i + 1 + horizon, n)
        fut_close = close[breakout_i + 1:end]
        if direction == 1:
            fade_mask = fut_close < ref_low
            return_mask = fut_close <= ref_high  # weaker: returns to inside/below upper bound
        else:
            fade_mask = fut_close > ref_high
            return_mask = fut_close >= ref_low
        faded = bool(fade_mask.any())
        ttf = int(np.argmax(fade_mask)) + 1 if faded else None
        returned = bool(return_mask.any())
        attempts.append(dict(breakout_idx=int(breakout_i), direction=int(direction),
                              faded=faded, time_to_fade_bars=ttf, returned_inside=returned))
        if faded:
            break
        # attempt did not fade-through; look for a subsequent attempt after price returns inside
        if returned:
            reentry_pos = int(np.argmax(return_mask))
            i = breakout_i + 1 + reentry_pos + 1
        else:
            break  # never returned inside within the horizon -- sustained breakout, no further attempts
    return attempts


def build_events(m, inside_events):
    rows = []
    atr = m["atr14"].values
    for ev in inside_events:
        idx = ev["inside_idx"]
        atr_ref = atr[idx]
        rng = ev["inside_high"] - ev["inside_low"]
        if rng <= 0 or not (np.isfinite(atr_ref) and atr_ref > 0):
            continue
        attempts = _fade_track(m, idx, ev["inside_high"], ev["inside_low"])
        if not attempts:
            continue  # NO_BREAKOUT -- excluded per invalidation rule
        mother_rng = ev["mother_high"] - ev["mother_low"]
        compression_ratio = rng / mother_rng if mother_rng > 0 else None
        ctx = P.context_features(m, idx)
        for an, att in enumerate(attempts, start=1):
            direction = att["direction"]
            mp = P.movement_profile(m, att["breakout_idx"], -direction, atr_ref)  # -direction: fade is the OPPOSITE of the breakout
            row = dict(mother_idx=ev["mother_idx"], inside_idx=idx, attempt_number=min(an, MAX_ATTEMPT_BUCKET),
                       breakout_idx=att["breakout_idx"], direction=direction, faded=att["faded"],
                       time_to_fade_bars=att["time_to_fade_bars"], inside_range_atr=rng / atr_ref,
                       compression_ratio=compression_ratio, mother_range_atr=mother_rng / atr_ref if atr_ref else None,
                       mp=mp)
            row.update(ctx)
            row["breakout_session"] = str(m["session"].iloc[att["breakout_idx"]])
            row["year"] = P.year_of(m, att["breakout_idx"])
            rows.append(row)
    return rows


def random_bar_control(m, n_events, rng):
    """Control B: generic single-bar breakout -- a random sample of ORDINARY bars (no compression or
    containment condition) used as the reference range."""
    h = m["high"].values
    l = m["low"].values
    atr = m["atr14"].values
    n = len(m)
    valid = np.where(np.isfinite(atr[:n - NO_BREAKOUT_WINDOW_BARS - 1]) & (atr[:n - NO_BREAKOUT_WINDOW_BARS - 1] > 0))[0]
    valid = valid[valid > 20]
    chosen = rng.choice(valid, size=min(n_events, len(valid)), replace=False)
    rows = []
    for idx in chosen:
        ref_high, ref_low = float(h[idx]), float(l[idx])
        if ref_high <= ref_low:
            continue
        attempts = _fade_track(m, idx, ref_high, ref_low)
        if not attempts:
            continue
        for an, att in enumerate(attempts, start=1):
            rows.append(dict(attempt_number=min(an, MAX_ATTEMPT_BUCKET), faded=att["faded"]))
    return rows


def compression_only_control(m, n_events, rng):
    """Control C: generic compression, no containment requirement -- bars in the lowest tercile of
    (own range / prior ATR14), used as the reference range regardless of whether they are 'inside' the
    preceding bar."""
    h = m["high"].values
    l = m["low"].values
    atr = m["atr14"].values
    n = len(m)
    own_rng = h - l
    with np.errstate(invalid="ignore", divide="ignore"):
        rel = own_rng / atr
    valid_mask = np.isfinite(rel) & (rel > 0)
    valid_idx = np.where(valid_mask)[0]
    valid_idx = valid_idx[(valid_idx > 20) & (valid_idx < n - NO_BREAKOUT_WINDOW_BARS - 1)]
    if len(valid_idx) == 0:
        return []
    thresh = np.percentile(rel[valid_idx], 33.33)
    compressed_idx = valid_idx[rel[valid_idx] <= thresh]
    chosen = rng.choice(compressed_idx, size=min(n_events, len(compressed_idx)), replace=False)
    rows = []
    for idx in chosen:
        ref_high, ref_low = float(h[idx]), float(l[idx])
        if ref_high <= ref_low:
            continue
        attempts = _fade_track(m, idx, ref_high, ref_low)
        if not attempts:
            continue
        for an, att in enumerate(attempts, start=1):
            rows.append(dict(attempt_number=min(an, MAX_ATTEMPT_BUCKET), faded=att["faded"]))
    return rows


def random_matched_control(m, n_events, rng):
    """Control D: ordinary mean-reversion baseline -- fully synthetic ATR-sized ranges at random
    points, same convention as E010/E012/E015's own random-matched control."""
    close = m["close"].values
    atr = m["atr14"].values
    n = len(m)
    max_start = n - NO_BREAKOUT_WINDOW_BARS - 60
    valid_idx = np.where(np.isfinite(atr[:max_start]) & (atr[:max_start] > 0))[0]
    valid_idx = valid_idx[valid_idx > 20]
    chosen = rng.choice(valid_idx, size=min(n_events, len(valid_idx)), replace=False)
    rows = []
    for idx in chosen:
        a = atr[idx]
        half_width = 0.5 * a
        center = close[idx]
        ref_low, ref_high = center - half_width, center + half_width
        attempts = _fade_track(m, idx, ref_high, ref_low)
        if not attempts:
            continue
        for an, att in enumerate(attempts, start=1):
            rows.append(dict(attempt_number=min(an, MAX_ATTEMPT_BUCKET), faded=att["faded"]))
    return rows


def fade_rate(rows, attempt_number=None):
    sub = rows if attempt_number is None else [r for r in rows if r["attempt_number"] == attempt_number]
    n = len(sub)
    if n == 0:
        return dict(n=0)
    fades = sum(1 for r in sub if r["faded"])
    ttfs = [r["time_to_fade_bars"] for r in sub if r.get("time_to_fade_bars") is not None]
    return dict(n=n, fade_rate=float(fades / n), sustained_rate=float((n - fades) / n),
                median_time_to_fade_bars=float(np.median(ttfs)) if ttfs else None)


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

    inside_events = detect_inside_bars(m)
    rows = build_events(m, inside_events)
    attempt1_rows = [r for r in rows if r["attempt_number"] == 1]

    overall = fade_rate(attempt1_rows)

    # --- examination variables (attempt-1 only, to avoid attempt-number confound in slicing) ---
    slices = {}
    if attempt1_rows:
        comp_labels = tercile_labels([r["compression_ratio"] for r in attempt1_rows if r["compression_ratio"] is not None])
        comp_rows = [r for r in attempt1_rows if r["compression_ratio"] is not None]
        for i, r in enumerate(comp_rows):
            r["compression_tercile"] = str(comp_labels[i])
        mother_labels = tercile_labels([r["mother_range_atr"] for r in attempt1_rows if r["mother_range_atr"] is not None])
        mother_rows = [r for r in attempt1_rows if r["mother_range_atr"] is not None]
        for i, r in enumerate(mother_rows):
            r["mother_tercile"] = str(mother_labels[i])
    else:
        comp_rows, mother_rows = [], []

    def slice_stat(rows_src, key, val):
        sub = [r for r in rows_src if r.get(key) == val]
        fr = fade_rate(sub, attempt_number=None)
        p = chi2_p(fr.get("fade_rate", 0), fr.get("n", 0), overall.get("fade_rate", 0), overall.get("n", 0))
        fr["p_vs_overall"] = p
        return fr

    for d, name in [(1, "up"), (-1, "down")]:
        slices[f"direction_{name}"] = slice_stat(attempt1_rows, "direction", d)
    for tercile in ["low", "mid", "high"]:
        slices[f"mother_size_{tercile}"] = slice_stat(mother_rows, "mother_tercile", tercile)
        slices[f"compression_{tercile}"] = slice_stat(comp_rows, "compression_tercile", tercile)
    for vr in ["low", "mid", "high"]:
        slices[f"vol_{vr}"] = slice_stat(attempt1_rows, "vol_regime", vr)
    for sess in ["asia", "london", "ny", "late"]:
        slices[f"session_{sess}"] = slice_stat(attempt1_rows, "breakout_session", sess)
    for dow in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        slices[f"dow_{dow}"] = slice_stat(attempt1_rows, "dow", dow)

    # --- first vs. repeated attempt ---
    attempt2_rows = [r for r in rows if r["attempt_number"] == 2]
    attempt_comparison = dict(
        attempt_1=fade_rate(attempt1_rows), attempt_2=fade_rate(attempt2_rows),
        p_attempt1_vs_2=chi2_p(fade_rate(attempt1_rows).get("fade_rate", 0), fade_rate(attempt1_rows).get("n", 0),
                                fade_rate(attempt2_rows).get("fade_rate", 0), fade_rate(attempt2_rows).get("n", 0)))

    # --- controls B, C, D ---
    rng = np.random.default_rng(RNG_SEED)
    n_target = len(attempt1_rows)
    control_b = random_bar_control(m, n_target, rng)
    control_c = compression_only_control(m, n_target, rng)
    control_d = random_matched_control(m, n_target, rng)

    control_b_a1 = [r for r in control_b if r["attempt_number"] == 1]
    control_c_a1 = [r for r in control_c if r["attempt_number"] == 1]
    control_d_a1 = [r for r in control_d if r["attempt_number"] == 1]

    def attempt_decay_check(ctrl_rows):
        a1 = [r for r in ctrl_rows if r["attempt_number"] == 1]
        a2 = [r for r in ctrl_rows if r["attempt_number"] == 2]
        return dict(attempt_1=fade_rate(a1), attempt_2=fade_rate(a2),
                    p_1_vs_2=chi2_p(fade_rate(a1).get("fade_rate", 0), fade_rate(a1).get("n", 0),
                                     fade_rate(a2).get("fade_rate", 0), fade_rate(a2).get("n", 0)))

    controls = dict(
        control_B_generic_single_bar=dict(
            overall=fade_rate(control_b_a1),
            p_vs_real=chi2_p(overall.get("fade_rate", 0), overall.get("n", 0),
                              fade_rate(control_b_a1).get("fade_rate", 0), fade_rate(control_b_a1).get("n", 0)),
            attempt_decay=attempt_decay_check(control_b)),
        control_C_generic_compression=dict(
            overall=fade_rate(control_c_a1),
            p_vs_real=chi2_p(overall.get("fade_rate", 0), overall.get("n", 0),
                              fade_rate(control_c_a1).get("fade_rate", 0), fade_rate(control_c_a1).get("n", 0)),
            attempt_decay=attempt_decay_check(control_c)),
        control_D_random_matched=dict(
            overall=fade_rate(control_d_a1),
            p_vs_real=chi2_p(overall.get("fade_rate", 0), overall.get("n", 0),
                              fade_rate(control_d_a1).get("fade_rate", 0), fade_rate(control_d_a1).get("n", 0)),
            attempt_decay=attempt_decay_check(control_d)),
    )

    # --- cross-control comparisons: is COMPRESSION (not mere "real bar-ness") the genuine driver? ---
    cross_control = dict(
        C_vs_D=chi2_p(fade_rate(control_c_a1).get("fade_rate", 0), fade_rate(control_c_a1).get("n", 0),
                       fade_rate(control_d_a1).get("fade_rate", 0), fade_rate(control_d_a1).get("n", 0)),
        B_vs_D=chi2_p(fade_rate(control_b_a1).get("fade_rate", 0), fade_rate(control_b_a1).get("n", 0),
                       fade_rate(control_d_a1).get("fade_rate", 0), fade_rate(control_d_a1).get("n", 0)),
    )

    # --- yearly stability ---
    by_year = {}
    for r in attempt1_rows:
        by_year.setdefault(r["year"], []).append(r)
    yearly = {str(y): fade_rate(rs) for y, rs in sorted(by_year.items())}

    # --- standard movement-profile summary (fade direction as predicted direction) ---
    mp_rows = [r["mp"] for r in attempt1_rows if r.get("mp") is not None]
    movement_summary = P.summarize_movement(mp_rows) if mp_rows else dict(n=0)

    return dict(
        timeframe=tf, split_metadata=meta, n_bars=int(len(m)),
        date_range=[str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])],
        n_inside_bars_detected=len(inside_events), n_events_with_breakout=len(attempt1_rows),
        n_no_breakout_excluded=len(inside_events) - len(set(r["inside_idx"] for r in rows)),
        primary=dict(overall=overall, movement_profile_summary=movement_summary),
        slices=slices, attempt_comparison=attempt_comparison, controls=controls,
        cross_control=cross_control, yearly_stability=yearly,
    )


def main():
    results = {"edge": "E014", "edge_id": "E014", "hypothesis_version": "V0",
               "run_id": "discovery_pass_1_full_profile_2026-07-21",
               "timeframes_tested": [], "timeframes_unavailable": {
                   "M1": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)",
                   "M5": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)"},
               "params": dict(RESPONSE_HORIZON_BARS=RESPONSE_HORIZON_BARS,
                              NO_BREAKOUT_WINDOW_BARS=NO_BREAKOUT_WINDOW_BARS,
                              MAX_ATTEMPT_BUCKET=MAX_ATTEMPT_BUCKET, RNG_SEED=RNG_SEED,
                              movement_horizons=P.HORIZONS, atr_thresholds=P.ATR_THRESHOLDS),
               "by_timeframe": {}}

    for tf in ["M15", "H1", "H4"]:
        print("=== running", tf, "===")
        res = run_timeframe(tf)
        results["by_timeframe"][tf] = res
        results["timeframes_tested"].append(tf)
        print(tf, "n_inside_bars", res["n_inside_bars_detected"], "n_events", res["n_events_with_breakout"])
        print(" overall:", res["primary"]["overall"])
        print(" controls:", res["controls"])
        print(" cross_control (is compression the real driver?):", res["cross_control"])
        print(" attempt_comparison:", res["attempt_comparison"])
        for k, v in res["slices"].items():
            print(" slice", k, v)

    with open("e014_inside_bar_false_breakout_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)


if __name__ == "__main__":
    main()
