"""E032 -- Premium Discount Flip -- CLEAN RERUN (holdout-excluded), 2026-07-21.

Remediation of the TERMINAL HOLDOUT BREACH incident (PROJECT_STATE_v2.md SS8.23,
EDGE_RESEARCH_PROTOCOL.md SS8). The original contaminated pass is `e032_premium_discount_flip.py` /
`e032_premium_discount_flip_results.json` -- preserved UNCHANGED as the audit trail. Same METHOD (same
two range definitions, same STEP/N windows, same quartile bucketing -- nothing tuned) with exactly one
substantive change: both D1 (daily/weekly range definitions) and M15 now load through `_common.load()`'s
mandatory holdout-cutoff enforcement instead of the old unfiltered `load(tf)` calls.

V0 hypothesis (frozen, verbatim, unchanged): "Price trading above/below the 50% equilibrium of a
defined range (premium/discount) is more likely to move toward, not away from, that equilibrium."
"""
import json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, mannwhitneyu
from _common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID

STEP = 16
NS = [16, 64]


def build_daily():
    d1, meta = load("D1", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    d1["date"] = d1["dt"].dt.date
    d1["eq_day"] = (d1["high"] + d1["low"]) / 2
    d1["range_day"] = d1["high"] - d1["low"]
    d1["eq_day"] = d1["eq_day"].shift(1)
    d1["range_day"] = d1["range_day"].shift(1)
    return d1[["date", "eq_day", "range_day"]], meta


def build_weekly():
    d1, meta = load("D1", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    d1["week"] = d1["dt"].dt.to_period("W-SUN")
    wk = d1.groupby("week").agg(high=("high", "max"), low=("low", "min"), last_date=("dt", "max")).reset_index()
    wk["eq_wk"] = (wk["high"] + wk["low"]) / 2
    wk["range_wk"] = wk["high"] - wk["low"]
    wk["eq_wk"] = wk["eq_wk"].shift(1)
    wk["range_wk"] = wk["range_wk"].shift(1)
    wk["week"] = wk["week"] + 1
    return wk[["week", "eq_wk", "range_wk"]], meta


def analyze(m, eq_col, range_col, label):
    idx = np.arange(0, len(m) - max(NS) - 1, STEP)
    valid = m[range_col].notna() & (m[range_col] > 0)
    idx = idx[valid.values[idx]]
    close = m["close"].values
    eq = m[eq_col].values[idx]
    rng = m[range_col].values[idx]
    dist0 = (close[idx] - eq) / rng
    rows = {"n": int(len(idx))}
    out = {}
    for N in NS:
        distN = (close[idx + N] - eq) / rng
        move_toward = np.abs(dist0) - np.abs(distN)
        adist = np.abs(dist0)
        q = pd.qcut(adist, 4, labels=["q1_near", "q2", "q3", "q4_extreme"], duplicates="drop")
        by_q = {}
        for lab in q.categories:
            sub = move_toward[q == lab]
            by_q[str(lab)] = dict(n=int(len(sub)), mean=float(np.mean(sub)) if len(sub) else None)
        low = move_toward[q == q.categories[0]]
        high = move_toward[q == q.categories[-1]]
        mw = mannwhitneyu(low, high, alternative="two-sided") if len(low) > 20 and len(high) > 20 else (None, None)
        sp = spearmanr(adist, move_toward)
        out[f"N{N}"] = dict(by_quartile=by_q,
                             extreme_vs_near_p=float(mw[1]) if mw[1] is not None else None,
                             extreme_mean=float(high.mean()), near_mean=float(low.mean()),
                             spearman_r=float(sp[0]), spearman_p=float(sp[1]))
    rows["results"] = out
    return rows


def main():
    m, meta_m15 = load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    m["date"] = m["dt"].dt.date
    m["week"] = m["dt"].dt.to_period("W-SUN")
    daily, meta_daily = build_daily()
    weekly, meta_weekly = build_weekly()
    m = m.merge(daily, on="date", how="left")
    m = m.merge(weekly, on="week", how="left")

    results = {"edge": "E032", "run_id": "clean_rerun_2026-07-21",
               "supersedes_contaminated_artifact": "e032_premium_discount_flip_results.json",
               "split_metadata": dict(M15=meta_m15, D1_for_daily=meta_daily, D1_for_weekly=meta_weekly),
               "n_bars": int(len(m)),
               "date_range": [str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])]}
    results["daily_range_definition"] = analyze(m, "eq_day", "range_day", "daily")
    results["weekly_range_definition"] = analyze(m, "eq_wk", "range_wk", "weekly")

    with open("e032_premium_discount_flip_clean_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
