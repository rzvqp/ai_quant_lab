"""E006 -- Asia Range Expansion Failure -- full-profile Discovery-stage analysis (Flow A).

V0 (frozen, verbatim): "Breakouts of the Asia session range fail more often under certain conditions
than others."

Run under EDGE_RESEARCH_PROTOCOL.md SS SS1-8 only (Discovery stage; SS9 scalping validation explicitly
NOT performed here per the CEO's own priority-shift instruction). Full-profile template per the CEO's
"overnight full edge profile" directive, reusing `_profile.py`. Reordered ahead of E013/E016 per the
CEO-approved priority audit (2026-07-21) -- selected as the first genuinely novel, low-redundancy
edge in the Tier-1 queue.

Note on V0's own wording: this is explicitly a HETEROGENEITY claim ("fail more often under certain
conditions than OTHERS"), not a simple "breakouts mostly fail" claim -- so the primary test is whether
failure rate varies significantly across the stated observable variables (range width, direction, day
of week, volatility regime, which later session the breakout occurs in), not merely whether the
overall failure rate exceeds 50%.

Method (disclosed, exploratory -- Discovery stage only, no tuning/optimization):
1. **Asia session range**: per calendar UTC date, the high/low spanned by all M15 bars tagged
   `session=='asia'` by `_common.load()` (hour < 8 UTC, i.e. 00:00-07:59 UTC, the SAME session-tagging
   convention used by every other edge in this program -- not redefined here). A date's Asia range is
   only used if at least 28 of the 32 possible M15 bars in that window are present (>=87.5% session
   completeness, disclosed, not tuned) -- guards against data gaps producing a spuriously narrow/wide
   range from a partial session.
2. **Breakout**: the FIRST bar after the Asia session ends that day (session in {london, ny, late})
   whose CLOSE is beyond the Asia range (> asia_high for an upside breakout, < asia_low for a downside
   breakout). Only the first breakout per calendar day is used as the primary event (avoids
   within-day pseudo-replication from repeated back-and-forth crossings -- the same "first instance
   only" convention already used elsewhere in this program, e.g. E015's visit-1 priority).
3. **Failure / sustained classification**: observed over a FIXED, disclosed window -- the remainder of
   the calendar day following the breakout (up to 64 M15 bars / 16 hours, i.e. through the end of the
   `late` session, capped at the next date's Asia session start if shorter). FAILURE = price's CLOSE
   crosses back onto the opposite side of the broken level at any point in that window (for an upside
   breakout: close < asia_high; downside: close > asia_low). SUSTAINED = no such close occurs within
   the window. Time-to-failure (in M15 bars) is recorded for failures.
4. **Standard reaction profile**: `_profile.py::movement_profile()` is also computed at the breakout
   (direction = breakout direction), same 6 horizons / 5 ATR thresholds as every other edge this
   session, purely for comparability -- the PRIMARY outcome variable for V0 itself is the binary
   failure/sustained flag described in (3), since that is literally what V0 and the registry's own
   "Measured outcome" field describe.
5. **Context features per event**: asia_range normalized by the M15 ATR14 at the breakout bar,
   breakout direction, day of week, `_common.vol_regime()` tercile, which session the breakout
   occurred in (london/ny/late), and year -- exactly the registry's own listed "Observable variables."
6. **Control (structural, not merely random-noise)**: identical breakout/failure logic applied to a
   RANDOM, non-Asia 8-hour window per date (uniform random start hour in [0,15], seed=42) instead of
   the real 00:00-07:59 Asia window. This tests whether any failure-rate heterogeneity found is
   Asia-specific (as V0's own implied mechanism -- low-liquidity overnight session -- would predict)
   or a generic property of "any overnight/session-sized range," which would falsify the Asia-specific
   framing even if a heterogeneity pattern exists. This also directly addresses the open
   generic-mean-reversion confound flagged in `NEXT_SESSION_FLOW_A.md` for E026/E032.
7. **Timeframes**: M15 (primary -- the finest granularity available in this project, per
   EDGE_DISCOVERY_ROADMAP.md's own disclosed caveat that session-boundary precision is somewhat
   reduced without M1 data but "the core question is testable"). H1 is run as a secondary,
   coarser-resolution robustness check only (Asia-session-boundary precision is markedly worse on H1;
   reported, not treated as equally authoritative).
8. **Robustness**: Asia-boundary sensitivity (narrower 01:00-05:59 and wider 00:00-08:59 UTC window
   definitions, vs. the primary 00:00-07:59), and yearly stability.
"""
import json
import numpy as np
from scipy.stats import chi2_contingency, mannwhitneyu
from _common import load, vol_regime, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
import _profile as P

FAILURE_HORIZON_HOURS = 16  # remainder of the trading day following the Asia session
MIN_SESSION_COMPLETENESS_FRAC = 0.875  # >=87.5% of a session window's expected bars must be present
ASIA_HOUR_VARIANTS = {
    "primary_0_8": (0, 8),     # matches _common.py's own session tag exactly
    "narrow_1_6": (1, 6),
    "wide_0_9": (0, 9),
}
RNG_SEED = 42


def _bars_per_hour(m):
    """Infer the timeframe's bar spacing directly from the data (timeframe-agnostic, no hardcoded
    M15 assumption) -- median consecutive-bar time delta, in hours."""
    deltas = m["dt"].diff().dropna().dt.total_seconds() / 3600.0
    median_delta_h = float(deltas.median())
    return 1.0 / median_delta_h if median_delta_h > 0 else 1.0


def _bars_by_date(m):
    """Group row indices by UTC calendar date, in time order (dates are already sorted since m is)."""
    dates = m["dt"].dt.date.values
    by_date = {}
    for i, dte in enumerate(dates):
        by_date.setdefault(dte, []).append(i)
    return by_date


def detect_breakouts(m, hour_lo, hour_hi, bars_per_hour):
    """hour_lo/hour_hi: UTC hour half-open window [hour_lo, hour_hi) defining the 'Asia-like' session.
    bars_per_hour: inferred from the loaded timeframe's own bar spacing (timeframe-agnostic).
    Returns one event per calendar date (at most), the first post-window breakout."""
    hours = m["dt"].dt.hour.values
    highs = m["high"].values
    lows = m["low"].values
    closes = m["close"].values
    atr = m["atr14"].values
    by_date = _bars_by_date(m)
    window_bars = (hour_hi - hour_lo) * bars_per_hour
    min_completeness = max(1, round(window_bars * MIN_SESSION_COMPLETENESS_FRAC))
    horizon_bars = max(1, round(FAILURE_HORIZON_HOURS * bars_per_hour))
    events = []
    dates_sorted = sorted(by_date.keys())
    for dte in dates_sorted:
        idxs = by_date[dte]
        session_idxs = [i for i in idxs if hour_lo <= hours[i] < hour_hi]
        if len(session_idxs) < min_completeness:
            continue
        s_high = highs[session_idxs].max()
        s_low = lows[session_idxs].min()
        if not (np.isfinite(s_high) and np.isfinite(s_low)) or s_high <= s_low:
            continue
        post_idxs = [i for i in idxs if hours[i] >= hour_hi]
        breakout_i = None
        direction = None
        for i in post_idxs:
            if closes[i] > s_high:
                breakout_i = i
                direction = 1
                break
            if closes[i] < s_low:
                breakout_i = i
                direction = -1
                break
        if breakout_i is None:
            continue
        atr_ref = atr[breakout_i]
        if not (np.isfinite(atr_ref) and atr_ref > 0):
            continue
        level = s_high if direction == 1 else s_low
        n = len(m)
        end = min(breakout_i + 1 + horizon_bars, n)
        # cap at next date's session start if that comes sooner (keeps the window inside "this day")
        next_date_idxs = by_date.get(_next_date_key(dates_sorted, dte), [])
        if next_date_idxs:
            end = min(end, next_date_idxs[0])
        fut_close = closes[breakout_i + 1:end]
        if direction == 1:
            fail_mask = fut_close < s_high
        else:
            fail_mask = fut_close > s_low
        failed = bool(fail_mask.any())
        ttf = int(np.argmax(fail_mask)) + 1 if failed else None
        events.append(dict(
            date=str(dte), breakout_idx=int(breakout_i), direction=int(direction),
            level=float(level), range_size=float(s_high - s_low), atr_ref=float(atr_ref),
            failed=failed, time_to_failure_bars=ttf, obs_window_bars=int(end - breakout_i - 1),
        ))
    return events


def _next_date_key(dates_sorted, dte):
    i = dates_sorted.index(dte)
    return dates_sorted[i + 1] if i + 1 < len(dates_sorted) else None


def random_window_breakouts(m, hour_span, rng, bars_per_hour):
    """Structural control: same logic, but the 'session' is a random hour_span-length window per date
    starting at a random hour, instead of the real Asia hours. seed=42, one random start per date,
    frozen before any result is examined."""
    hours = m["dt"].dt.hour.values
    highs = m["high"].values
    lows = m["low"].values
    closes = m["close"].values
    atr = m["atr14"].values
    by_date = _bars_by_date(m)
    dates_sorted = sorted(by_date.keys())
    window_bars = hour_span * bars_per_hour
    min_completeness = max(1, round(window_bars * MIN_SESSION_COMPLETENESS_FRAC))
    horizon_bars = max(1, round(FAILURE_HORIZON_HOURS * bars_per_hour))
    events = []
    for dte in dates_sorted:
        start_hour = int(rng.integers(0, 24 - hour_span - 1))  # leaves room for a post-window scan
        hour_lo, hour_hi = start_hour, start_hour + hour_span
        idxs = by_date[dte]
        session_idxs = [i for i in idxs if hour_lo <= hours[i] < hour_hi]
        if len(session_idxs) < min_completeness:
            continue
        s_high = highs[session_idxs].max()
        s_low = lows[session_idxs].min()
        if not (np.isfinite(s_high) and np.isfinite(s_low)) or s_high <= s_low:
            continue
        post_idxs = [i for i in idxs if hours[i] >= hour_hi]
        breakout_i = None
        direction = None
        for i in post_idxs:
            if closes[i] > s_high:
                breakout_i = i
                direction = 1
                break
            if closes[i] < s_low:
                breakout_i = i
                direction = -1
                break
        if breakout_i is None:
            continue
        atr_ref = atr[breakout_i]
        if not (np.isfinite(atr_ref) and atr_ref > 0):
            continue
        n = len(m)
        end = min(breakout_i + 1 + horizon_bars, n)
        next_date_idxs = by_date.get(_next_date_key(dates_sorted, dte), [])
        if next_date_idxs:
            end = min(end, next_date_idxs[0])
        fut_close = closes[breakout_i + 1:end]
        if direction == 1:
            fail_mask = fut_close < s_high
        else:
            fail_mask = fut_close > s_low
        failed = bool(fail_mask.any())
        events.append(dict(date=str(dte), direction=int(direction), failed=failed,
                            breakout_session=str(m["session"].iloc[breakout_i])))
    return events


def attach_event_context(m, ev):
    idx = ev["breakout_idx"]
    ctx = P.context_features(m, idx)
    breakout_session = str(m["session"].iloc[idx])
    row = dict(ev)
    row.update(ctx)
    row["breakout_session"] = breakout_session
    row["year"] = P.year_of(m, idx)
    row["range_atr"] = ev["range_size"] / ev["atr_ref"] if ev["atr_ref"] > 0 else None
    direction = ev["direction"]
    mp = P.movement_profile(m, idx, direction, ev["atr_ref"])
    row["mp"] = mp
    return row


def failure_rate(rows):
    n = len(rows)
    if n == 0:
        return dict(n=0)
    fails = sum(1 for r in rows if r["failed"])
    ttfs = [r["time_to_failure_bars"] for r in rows if r.get("time_to_failure_bars") is not None]
    return dict(n=n, failure_rate=float(fails / n), sustained_rate=float((n - fails) / n),
                median_time_to_failure_bars=float(np.median(ttfs)) if ttfs else None)


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
    """Lookahead-safe-N/A here (Discovery-stage, whole-sample terciles used for slicing only, not for
    any live signal) -- simple whole-sample cut, disclosed."""
    v = np.asarray(values, dtype=float)
    q1, q2 = np.percentile(v, [33.33, 66.67])
    labels = np.where(v <= q1, "low", np.where(v <= q2, "mid", "high"))
    return labels


def run_timeframe(tf):
    m, meta = load(tf, data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    d1, _ = load("D1", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    m["vol_regime"] = vol_regime(m)
    m = P.attach_daily_context(m, d1)

    bph = _bars_per_hour(m)
    hour_lo, hour_hi = ASIA_HOUR_VARIANTS["primary_0_8"]
    raw_events = detect_breakouts(m, hour_lo, hour_hi, bph)
    rows = [attach_event_context(m, ev) for ev in raw_events]

    overall = failure_rate(rows)

    # --- context slices: failure rate by each stated V0 observable, vs overall baseline ---
    slices = {}
    range_labels = tercile_labels([r["range_atr"] for r in rows]) if rows else []
    for i, r in enumerate(rows):
        r["range_tercile"] = str(range_labels[i]) if len(range_labels) else None

    def slice_stat(key, val):
        sub = [r for r in rows if r.get(key) == val]
        fr = failure_rate(sub)
        p = chi2_p(fr.get("failure_rate", 0), fr.get("n", 0), overall["failure_rate"], overall["n"])
        fr["p_vs_overall"] = p
        return fr

    for tercile in ["low", "mid", "high"]:
        slices[f"range_{tercile}"] = slice_stat("range_tercile", tercile)
    for d, name in [(1, "up"), (-1, "down")]:
        slices[f"direction_{name}"] = slice_stat("direction", d)
    for dow in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        slices[f"dow_{dow}"] = slice_stat("dow", dow)
    for vr in ["low", "mid", "high"]:
        slices[f"vol_{vr}"] = slice_stat("vol_regime", vr)
    for sess in ["london", "ny", "late"]:
        slices[f"breakout_session_{sess}"] = slice_stat("breakout_session", sess)

    # --- structural control: random non-Asia window, same logic, seed=42 ---
    rng = np.random.default_rng(RNG_SEED)
    rand_events = random_window_breakouts(m, hour_hi - hour_lo, rng, bph)
    rand_overall = failure_rate(rand_events)
    p_real_vs_random = chi2_p(overall.get("failure_rate", 0), overall.get("n", 0),
                               rand_overall.get("failure_rate", 0), rand_overall.get("n", 0))

    # --- falsification attempt: is "breakout_session" heterogeneity Asia-specific, or would ANY
    # preceding reference range show the same "NY breakouts sustain more" pattern? Slice the RANDOM
    # control's own events by the session the breakout itself falls in and compare directly against
    # the real-Asia session slices computed above. ---
    control_session_slices = {}
    for sess in ["london", "ny", "late"]:
        sub = [r for r in rand_events if r.get("breakout_session") == sess]
        control_session_slices[sess] = failure_rate(sub)

    # --- robustness: Asia-boundary sensitivity ---
    boundary_sensitivity = {}
    for name, (lo, hi) in ASIA_HOUR_VARIANTS.items():
        if name == "primary_0_8":
            boundary_sensitivity[name] = overall
            continue
        ev2 = detect_breakouts(m, lo, hi, bph)
        boundary_sensitivity[name] = failure_rate(ev2)

    # --- yearly stability ---
    by_year = {}
    for r in rows:
        by_year.setdefault(r["year"], []).append(r)
    yearly = {str(y): failure_rate(rs) for y, rs in sorted(by_year.items())}

    # --- standard movement-profile summary (comparability with other edges) ---
    mp_rows = [r["mp"] for r in rows if r.get("mp") is not None]
    movement_summary = P.summarize_movement(mp_rows) if mp_rows else dict(n=0)

    return dict(
        timeframe=tf, split_metadata=meta, n_bars=int(len(m)),
        date_range=[str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])],
        n_events=len(rows),
        primary=dict(overall=overall, movement_profile_summary=movement_summary),
        slices=slices,
        control_random_window=dict(overall=rand_overall, p_real_vs_random=p_real_vs_random,
                                    n_random_events=len(rand_events),
                                    session_slices=control_session_slices),
        boundary_sensitivity=boundary_sensitivity,
        yearly_stability=yearly,
    )


def main():
    results = {"edge": "E006", "edge_id": "E006", "hypothesis_version": "V0",
               "run_id": "discovery_pass_1_full_profile_2026-07-21",
               "timeframes_tested": [], "timeframes_unavailable": {
                   "M1": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)",
                   "M5": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)"},
               "params": dict(FAILURE_HORIZON_HOURS=FAILURE_HORIZON_HOURS,
                              MIN_SESSION_COMPLETENESS_FRAC=MIN_SESSION_COMPLETENESS_FRAC,
                              ASIA_HOUR_VARIANTS=ASIA_HOUR_VARIANTS, RNG_SEED=RNG_SEED,
                              movement_horizons=P.HORIZONS, atr_thresholds=P.ATR_THRESHOLDS),
               "by_timeframe": {}}

    for tf in ["M15", "H1"]:
        print("=== running", tf, "===")
        res = run_timeframe(tf)
        results["by_timeframe"][tf] = res
        results["timeframes_tested"].append(tf)
        print(tf, "n_events", res["n_events"], "overall", res["primary"]["overall"])
        print(" control (random window):", res["control_random_window"]["overall"],
              "p_real_vs_random:", res["control_random_window"]["p_real_vs_random"])
        print(" control session slices (falsification check):", res["control_random_window"]["session_slices"])
        for k, v in res["slices"].items():
            print(" slice", k, v)

    with open("e006_asia_range_expansion_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)


if __name__ == "__main__":
    main()
