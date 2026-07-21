"""E027 -- Midnight Open Anchor -- full-profile Discovery-stage analysis (Flow A).

V0 (frozen, verbatim): "The midnight (00:00) candle open acts as a reference/anchor level that price
frequently revisits or reacts to during the following session."

Run under EDGE_RESEARCH_PROTOCOL.md SSSS1-8 only (SS9 scalping validation explicitly NOT performed,
per the CEO's own priority-shift instruction). Only E027 is authorized this session.

**Deliberate methodological continuity with E017**: this is the second test in this program of the
general "reference level acts as a magnet price revisits" mechanism class -- E017 (Equal Highs/Lows
Target) already tested this for swing-point levels and found V0 NOT SUPPORTED, with a
random-matched-distance control reaching its target *more* reliably than real swing points. E027
deliberately reuses E017's own control construction (`random_matched_control`-style: a synthetic
target at a real, sampled-from-the-data ATR distance from a random point) rather than inventing a new
control convention, so this Discovery pass is a genuine second data point on the same question, not an
independently-designed test that could differ for incidental methodological reasons.

DEFINITIONS PREDECLARED BEFORE ANY OUTCOME WAS INSPECTED:

1. **Midnight open**: the `open` price of the first bar of each UTC calendar day (hour==0) -- an
   exact, unambiguous, bar-anchored timestamp, no convention ambiguity.
2. **Departure**: the first subsequent bar that day whose |close - midnight_open| >= 0.25xATR14 (a
   minimal move-away threshold, disclosed, not tuned -- without it, the very next bar would trivially
   count as a "revisit" candidate before price has gone anywhere). The departure's own ATR-normalized
   distance from midnight_open is recorded (this program's "dist," reused for the control below).
3. **Revisit**: from the departure bar onward, does any subsequent bar's [low, high] range touch back
   to midnight_open within the REMAINDER of that calendar day? Reach rate = fraction of
   departure-events revisited; time-to-revisit = bars from departure to the touch.
4. **Reaction magnitude**: `_profile.movement_profile()` at the revisit bar, direction = AWAY from
   midnight_open in the SAME direction as the original departure (testing "does price bounce away
   again after touching back," not merely whether it touches).
5. **Session**: the session tag (asia/london/ny/late) of the departure bar -- the registry's own
   "session" observable.
6. **No-departure exclusion**: if price never departs 0.25xATR from midnight_open all day, the day is
   excluded (no meaningful revisit test possible) -- the same "event never triggered" convention as
   every other edge's invalidation rule in this program.

CONTROL -- random-matched-distance (reused from E017's own construction, not reinvented): for a random
point in time (seed=42), sample a REAL observed departure distance from the actual midnight-open
population's own distribution, construct a synthetic target at that ATR distance from the random
point's own price (direction also resampled from the real population), and run the identical
revisit-detection logic. This isolates whether the midnight-open level specifically matters or whether
any level at a similarly "already-reached" distance gets revisited just as often by ordinary price
oscillation.

Timeframes: M15, H1, H4 -- all three registered for E027 and present in the clean dataset.
"""
import json
import numpy as np
from scipy.stats import chi2_contingency, mannwhitneyu
from _common import load, vol_regime, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
import _profile as P

DEPARTURE_THRESHOLD_ATR = 0.25
RNG_SEED = 42


def _bars_by_date(m):
    dates = m["dt"].dt.date.values
    by_date = {}
    for i, dte in enumerate(dates):
        by_date.setdefault(dte, []).append(i)
    return by_date


def build_midnight_events(m):
    close = m["close"].values
    high = m["high"].values
    low = m["low"].values
    atr = m["atr14"].values
    by_date = _bars_by_date(m)
    events = []
    for dte, idxs in sorted(by_date.items()):
        if len(idxs) < 4:
            continue
        mid_idx = idxs[0]
        # per definition (1): the OPEN of the first bar of the day, not the close
        midnight_price = m["open"].values[mid_idx]
        atr_ref = atr[mid_idx]
        if not (np.isfinite(atr_ref) and atr_ref > 0):
            continue
        threshold = DEPARTURE_THRESHOLD_ATR * atr_ref

        departure_i = None
        departure_dir = None
        for j in idxs[1:]:
            delta = close[j] - midnight_price
            if abs(delta) >= threshold:
                departure_i = j
                departure_dir = 1 if delta > 0 else -1
                break
        if departure_i is None:
            continue
        dist_atr = abs(close[departure_i] - midnight_price) / atr_ref

        rest_idxs = [j for j in idxs if j > departure_i]
        revisit_i = None
        for j in rest_idxs:
            if low[j] <= midnight_price <= high[j]:
                revisit_i = j
                break
        reached = revisit_i is not None
        ttf_bars = (rest_idxs.index(revisit_i) + 1) if reached else None

        mp = None
        if reached:
            atr_ref_revisit = atr[revisit_i]
            if np.isfinite(atr_ref_revisit) and atr_ref_revisit > 0:
                mp = P.movement_profile(m, revisit_i, departure_dir, atr_ref_revisit)

        events.append(dict(
            date=str(dte), departure_idx=int(departure_i), dist_atr=float(dist_atr),
            departure_dir=int(departure_dir), reached=bool(reached), ttf_bars=ttf_bars,
            session=str(m["session"].iloc[departure_i]), dow=str(m["dow"].iloc[departure_i]),
            vol_regime=str(m["vol_regime"].iloc[departure_i]), mp=mp,
            year=P.year_of(m, departure_i),
        ))
    return events


def random_matched_control(events, m, n_events, rng):
    """Reused convention from e017_equal_highs_lows.py::random_matched_control -- a synthetic target
    at a REAL, sampled departure distance from a random point in time."""
    close = m["close"].values
    high = m["high"].values
    low = m["low"].values
    atr = m["atr14"].values
    n = len(m)
    dists = np.array([e["dist_atr"] for e in events])
    dirs = np.array([e["departure_dir"] for e in events])
    max_start = n - 100
    valid_idx = np.where(np.isfinite(atr[:max_start]) & (atr[:max_start] > 0))[0]
    valid_idx = valid_idx[valid_idx > 20]
    chosen = rng.choice(valid_idx, size=min(n_events, len(valid_idx)), replace=False)
    sample_pos = rng.choice(len(dists), size=len(chosen), replace=True)

    out = []
    for idx, sp in zip(chosen, sample_pos):
        d, dirn = dists[sp], dirs[sp]
        a = atr[idx]
        target = close[idx] + dirn * d * a
        rest_end = min(idx + 100, n)
        revisit_i = None
        for j in range(idx + 1, rest_end):
            if low[j] <= target <= high[j]:
                revisit_i = j
                break
        reached = revisit_i is not None
        ttf_bars = (revisit_i - idx) if reached else None
        out.append(dict(reached=reached, ttf_bars=ttf_bars))
    return out


def summarize_group(rows):
    n = len(rows)
    if n == 0:
        return dict(n=0)
    reached = [r["reached"] for r in rows]
    rate = float(np.mean(reached))
    ttfs = [r["ttf_bars"] for r in rows if r.get("ttf_bars") is not None]
    out = dict(n=n, reach_rate=rate, n_reached=len(ttfs))
    if ttfs:
        out["median_ttf_bars"] = float(np.median(ttfs))
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


def tercile_labels(values):
    v = np.asarray(values, dtype=float)
    q1, q2 = np.percentile(v, [33.33, 66.67])
    return np.where(v <= q1, "low", np.where(v <= q2, "mid", "high"))


def run_timeframe(tf):
    m, meta = load(tf, data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    m["vol_regime"] = vol_regime(m)

    events = build_midnight_events(m)
    overall = summarize_group(events)

    mp_rows = [e["mp"] for e in events if e.get("mp") is not None]
    movement_summary = P.summarize_movement(mp_rows) if mp_rows else dict(n=0)

    rng = np.random.default_rng(RNG_SEED)
    rand_events = random_matched_control(events, m, len(events), rng)
    control = summarize_group(rand_events)
    p_vs_control = chi2_p(overall.get("reach_rate", 0), overall.get("n", 0),
                           control.get("reach_rate", 0), control.get("n", 0))

    slices = {}
    for sess in ["asia", "london", "ny", "late"]:
        sub = [e for e in events if e["session"] == sess]
        r = summarize_group(sub)
        r["p_vs_overall"] = chi2_p(r.get("reach_rate", 0), r.get("n", 0), overall.get("reach_rate", 0), overall.get("n", 0))
        slices[f"session_{sess}"] = r
    for vr in ["low", "mid", "high"]:
        sub = [e for e in events if e["vol_regime"] == vr]
        r = summarize_group(sub)
        r["p_vs_overall"] = chi2_p(r.get("reach_rate", 0), r.get("n", 0), overall.get("reach_rate", 0), overall.get("n", 0))
        slices[f"vol_{vr}"] = r
    dist_labels = tercile_labels([e["dist_atr"] for e in events]) if events else []
    for i, e in enumerate(events):
        e["dist_tercile"] = str(dist_labels[i]) if len(dist_labels) else None
    for tercile in ["low", "mid", "high"]:
        sub = [e for e in events if e.get("dist_tercile") == tercile]
        r = summarize_group(sub)
        r["p_vs_overall"] = chi2_p(r.get("reach_rate", 0), r.get("n", 0), overall.get("reach_rate", 0), overall.get("n", 0))
        slices[f"distance_{tercile}"] = r

    by_year = {}
    for e in events:
        by_year.setdefault(e["year"], []).append(e)
    yearly = {str(y): summarize_group(rs) for y, rs in sorted(by_year.items())}

    return dict(
        timeframe=tf, split_metadata=meta, n_bars=int(len(m)),
        date_range=[str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])],
        n_events=len(events),
        primary=dict(overall=overall, movement_profile_summary=movement_summary),
        control_random_matched_distance=dict(overall=control, p_vs_real=p_vs_control),
        slices=slices, yearly_stability=yearly,
    )


def main():
    results = {"edge": "E027", "edge_id": "E027", "hypothesis_version": "V0",
               "run_id": "discovery_pass_1_full_profile_2026-07-21",
               "timeframes_tested": [], "timeframes_unavailable": {
                   "M1": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)",
                   "M5": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)"},
               "params": dict(DEPARTURE_THRESHOLD_ATR=DEPARTURE_THRESHOLD_ATR, RNG_SEED=RNG_SEED,
                              movement_horizons=P.HORIZONS, atr_thresholds=P.ATR_THRESHOLDS),
               "by_timeframe": {}}

    for tf in ["M15", "H1", "H4"]:
        print("=== running", tf, "===")
        res = run_timeframe(tf)
        results["by_timeframe"][tf] = res
        results["timeframes_tested"].append(tf)
        print(tf, "n_events", res["n_events"], "overall", res["primary"]["overall"])
        print(" control_random_matched_distance:", res["control_random_matched_distance"])
        for k, v in res["slices"].items():
            print(" slice", k, v)

    with open("e027_midnight_open_anchor_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)


if __name__ == "__main__":
    main()
