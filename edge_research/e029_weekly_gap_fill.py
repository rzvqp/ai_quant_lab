"""E029 -- Weekly Gap Fill -- Discovery-stage analysis (Flow A).

V0 (frozen, verbatim): "A price gap between Friday's close and Sunday/Monday's open tends to be
filled within the following sessions."

Method (disclosed):
- Week-boundary detection: on the M15 series, any bar whose gap to the previous bar exceeds 20 hours
  is treated as a week-open bar (the normal M15 spacing is 900s; the weekend closure is by far the
  largest recurring gap in this feed).
- gap = week_open_price(open) - prior_close (the last traded price before the weekend).
- "Filled" = the first bar, searching forward from the week-open bar, whose [low,high] range reaches
  back to the prior_close level. time_to_fill = number of M15 bars from week-open to that bar (in
  hours). A fill horizon of 5 trading days (480 M15 bars) is used -- if not filled by then, classified
  not-filled-in-week (V0 says "within the following sessions", read here as "within the trading week
  that follows", the most literal, undisputed reading).
- Slices: gap size tercile, gap direction (up/down), week-of-month (1st-5th Monday of the calendar
  month).
"""
import json
import numpy as np
import pandas as pd
from _common import load

HORIZON_BARS = 480  # 5 trading days of M15


def main():
    m = load("M15")
    t = m["time"].values
    gap_hours = np.diff(t) / 3600.0
    week_open_idx = np.where(gap_hours > 20)[0] + 1  # index of the bar AFTER the big gap

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
    df = df[df["abs_gap"] >= 0.05].reset_index(drop=True)  # exclude data-artifact "gaps" (feed echoes prior close)
    df["gap_tercile"] = pd.qcut(df["abs_gap"], 3, labels=["small", "medium", "large"], duplicates="drop")
    df.to_csv("e029_gap_events.csv", index=False)

    results = {"edge": "E029", "n_bars": int(len(m)),
               "date_range": [str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])],
               "n_weekend_boundaries_detected": n_total,
               "n_excluded_near_zero_artifact": n_near_zero,
               "n_weekly_gaps": int(len(df)),
               "overall_fill_rate": float(df["filled"].mean()),
               "overall_median_ttf_hours": float(df.loc[df.filled, "ttf_hours"].median()),
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

    with open("e029_weekly_gap_fill_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
