"""E029 -- Weekly Gap Fill -- CLEAN RERUN (holdout-excluded), 2026-07-21.

Remediation of the TERMINAL HOLDOUT BREACH incident (PROJECT_STATE_v2.md SS8.23,
EDGE_RESEARCH_PROTOCOL.md SS8). The original contaminated pass is `e029_weekly_gap_fill.py` /
`e029_weekly_gap_fill_results.json` / `e029_gap_events.csv` -- all preserved UNCHANGED as the audit
trail. Same METHOD (same 20h week-boundary threshold, same $0.05 near-zero-artifact exclusion, same
480-bar fill horizon -- nothing tuned) with exactly one substantive change: data now loads through
`_common.load()`'s mandatory holdout-cutoff enforcement instead of the old unfiltered `load("M15")`.

V0 hypothesis (frozen, verbatim, unchanged): "A price gap between Friday's close and Sunday/Monday's
open tends to be filled within the following sessions."
"""
import json
import numpy as np
import pandas as pd
from _common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID

HORIZON_BARS = 480  # 5 trading days of M15


def main():
    m, meta = load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    t = m["time"].values
    gap_hours = np.diff(t) / 3600.0
    week_open_idx = np.where(gap_hours > 20)[0] + 1

    rows = []
    for i in week_open_idx:
        if i < 1 or i + 2 >= len(m):
            continue
        prior_close = m["close"].iloc[i - 1]
        wk_open = m["open"].iloc[i]
        gap = wk_open - prior_close
        end = min(i + HORIZON_BARS, len(m))
        seg_low = m["low"].values[i:end]
        seg_high = m["high"].values[i:end]
        filled_mask = (seg_low <= prior_close) & (seg_high >= prior_close)
        filled_idx = np.where(filled_mask)[0]
        filled = len(filled_idx) > 0
        ttf_bars = int(filled_idx[0]) if filled else None
        week_of_month = (m["dt"].iloc[i].day - 1) // 7 + 1
        rows.append(dict(i=int(i), date=str(m["dt"].iloc[i].date()), gap=float(gap),
                          gap_dir="up" if gap > 0 else "down",
                          filled=bool(filled), ttf_hours=(ttf_bars * 0.25) if filled else None,
                          week_of_month=int(week_of_month), dow_open=m["dow"].iloc[i]))
    df = pd.DataFrame(rows)
    df["abs_gap"] = df["gap"].abs()
    n_total = len(df)
    n_near_zero = int((df["abs_gap"] < 0.05).sum())
    df = df[df["abs_gap"] >= 0.05].reset_index(drop=True)
    df["gap_tercile"] = pd.qcut(df["abs_gap"], 3, labels=["small", "medium", "large"], duplicates="drop")
    df.to_csv("e029_gap_events_clean.csv", index=False)

    results = {"edge": "E029", "run_id": "clean_rerun_2026-07-21",
               "supersedes_contaminated_artifact": "e029_weekly_gap_fill_results.json",
               "split_metadata": meta,
               "n_bars": int(len(m)),
               "date_range": [str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])],
               "n_weekend_boundaries_detected": n_total,
               "n_excluded_near_zero_artifact": n_near_zero,
               "n_weekly_gaps": int(len(df)),
               "overall_fill_rate": float(df["filled"].mean()) if len(df) else None,
               "overall_median_ttf_hours": float(df.loc[df.filled, "ttf_hours"].median()) if df["filled"].any() else None,
               "by_direction": {}, "by_gap_tercile": {}, "by_week_of_month": {}}

    for k, v in df.groupby("gap_dir"):
        results["by_direction"][k] = dict(n=int(len(v)), fill_rate=float(v["filled"].mean()),
                                           median_ttf_hours=float(v.loc[v.filled, "ttf_hours"].median()) if v.filled.any() else None,
                                           mean_abs_gap=float(v["abs_gap"].mean()))
    for k, v in df.groupby("gap_tercile", observed=True):
        results["by_gap_tercile"][str(k)] = dict(n=int(len(v)), fill_rate=float(v["filled"].mean()),
                                                  median_ttf_hours=float(v.loc[v.filled, "ttf_hours"].median()) if v.filled.any() else None)
    for k, v in df.groupby("week_of_month"):
        results["by_week_of_month"][int(k)] = dict(n=int(len(v)), fill_rate=float(v["filled"].mean()))

    with open("e029_weekly_gap_fill_clean_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
