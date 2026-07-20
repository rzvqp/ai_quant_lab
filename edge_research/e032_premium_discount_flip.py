"""E032 -- Premium Discount Flip -- Discovery-stage analysis (Flow A).

V0 (frozen, verbatim): "Price trading above/below the 50% equilibrium of a defined range (premium/
discount) is more likely to move toward, not away from, that equilibrium."

Method (disclosed): the registry itself lists "range-defining logic used" as an observable variable
to test, not a fixed choice -- two independent, disclosed range definitions are tried:
  (a) previous COMPLETED calendar day's D1 [low, high] (available from the day's first M15 bar,
      lookahead-safe, analogous to the ADR construction in E026);
  (b) previous COMPLETED calendar week's range (Mon-Sun D1 high/low), available from the new week's
      first bar.
For each definition, equilibrium = (range_high + range_low) / 2, range_size = range_high - range_low.
distance_t = (close_t - equilibrium) / range_size (signed; >0 = premium/above eq, <0 = discount/below).
Snapshots are sampled every 16 M15 bars (~4h) rather than every bar, to reduce within-period
autocorrelation. At each snapshot: movement_toward_eq = |distance_t| - |distance_{t+N}| (same
equilibrium/range_size held fixed across the window) for N in {16 (~4h), 64 (~16h)}. Positive value =
price moved closer to equilibrium; negative = moved further into premium/discount.
Distance is bucketed into quartiles of |distance_t| and movement_toward_eq is compared across
buckets (Spearman correlation + extreme-quartile Mann-Whitney), predicting a positive relationship
(bigger initial extremes -> more reversion) if V0 holds.
"""
import json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, mannwhitneyu
from _common import load

STEP = 16
NS = [16, 64]


def build_daily():
    d1 = load("D1")
    d1["date"] = d1["dt"].dt.date
    d1["eq_day"] = (d1["high"] + d1["low"]) / 2
    d1["range_day"] = d1["high"] - d1["low"]
    d1["eq_day"] = d1["eq_day"].shift(1)
    d1["range_day"] = d1["range_day"].shift(1)
    return d1[["date", "eq_day", "range_day"]]


def build_weekly():
    d1 = load("D1")
    d1["week"] = d1["dt"].dt.to_period("W-SUN")
    wk = d1.groupby("week").agg(high=("high", "max"), low=("low", "min"), last_date=("dt", "max")).reset_index()
    wk["eq_wk"] = (wk["high"] + wk["low"]) / 2
    wk["range_wk"] = wk["high"] - wk["low"]
    wk["eq_wk"] = wk["eq_wk"].shift(1)
    wk["range_wk"] = wk["range_wk"].shift(1)
    wk["week"] = wk["week"] + 1  # applies to the NEXT week
    return wk[["week", "eq_wk", "range_wk"]]


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
    m = load("M15")
    m["date"] = m["dt"].dt.date
    m["week"] = m["dt"].dt.to_period("W-SUN")
    m = m.merge(build_daily(), on="date", how="left")
    m = m.merge(build_weekly(), on="week", how="left")

    results = {"edge": "E032", "n_bars": int(len(m)),
               "date_range": [str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])]}
    results["daily_range_definition"] = analyze(m, "eq_day", "range_day", "daily")
    results["weekly_range_definition"] = analyze(m, "eq_wk", "range_wk", "weekly")

    with open("e032_premium_discount_flip_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
