"""E028 -- Fibonacci OTE -- CLEAN RERUN (holdout-excluded), 2026-07-21.

Remediation of the TERMINAL HOLDOUT BREACH incident (PROJECT_STATE_v2.md SS8.23,
EDGE_RESEARCH_PROTOCOL.md SS8). The original contaminated pass is `e028_fibonacci_ote.py` /
`e028_fibonacci_ote_results.json` / `e028_legs.csv` -- all preserved UNCHANGED as the audit trail. Same
METHOD (same k=5 fractal, same zigzag construction, same zone bins -- nothing tuned) with exactly one
substantive change: data now loads through `_common.load()`'s mandatory holdout-cutoff enforcement
instead of the old unfiltered `load("M15")` call.

V0 hypothesis (frozen, verbatim, unchanged): "The 61.8%-79% 'optimal trade entry' retracement zone of
an impulsive move offers a statistically favorable continuation entry."
"""
import json
import numpy as np
import pandas as pd
from _common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID

K = 5


def detect_swings(m):
    h = m["high"].values
    l = m["low"].values
    n = len(m)
    is_high = np.zeros(n, dtype=bool)
    is_low = np.zeros(n, dtype=bool)
    for i in range(K, n - K):
        window_h = h[i - K:i + K + 1]
        if h[i] == window_h.max() and (window_h == h[i]).sum() == 1:
            is_high[i] = True
        window_l = l[i - K:i + K + 1]
        if l[i] == window_l.min() and (window_l == l[i]).sum() == 1:
            is_low[i] = True

    candidates = sorted(
        [(i, "high", h[i]) for i in np.where(is_high)[0]] + [(i, "low", l[i]) for i in np.where(is_low)[0]],
        key=lambda x: x[0])

    swings = []
    cur_type = cur_price = cur_idx = None
    for idx, typ, price in candidates:
        if cur_type is None:
            cur_type, cur_price, cur_idx = typ, price, idx
            continue
        if typ == cur_type:
            if (typ == "high" and price > cur_price) or (typ == "low" and price < cur_price):
                cur_price, cur_idx = price, idx
        else:
            swings.append((cur_idx, cur_type, cur_price))
            cur_type, cur_price, cur_idx = typ, price, idx
    swings.append((cur_idx, cur_type, cur_price))
    return swings


def main():
    m, meta = load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    swings = detect_swings(m)
    print("n_swings", len(swings))

    rows = []
    for i in range(len(swings) - 3):
        a_idx, a_typ, a_price = swings[i]
        b_idx, b_typ, b_price = swings[i + 1]
        c_idx, c_typ, c_price = swings[i + 2]
        d_idx, d_typ, d_price = swings[i + 3]
        leg = b_price - a_price
        if leg == 0:
            continue
        retr_pct = abs(c_price - b_price) / abs(leg)
        dir_ab = 1.0 if leg > 0 else -1.0
        cont_mag = dir_ab * (d_price - b_price) / abs(leg)
        rows.append(dict(a_idx=a_idx, b_idx=b_idx, c_idx=c_idx, d_idx=d_idx,
                          leg_size=abs(leg), retr_pct=retr_pct, cont_mag=cont_mag,
                          continued=int(cont_mag > 0),
                          session=m["session"].iloc[b_idx], dow=m["dow"].iloc[b_idx]))
    df = pd.DataFrame(rows)
    df.to_csv("e028_legs_clean.csv", index=False)

    bins = [-0.001, 0.382, 0.618, 0.79, 1.0, np.inf]
    labels = ["lt_382", "382_618", "OTE_618_79", "79_100", "gt_100_full_reversal"]
    df["zone"] = pd.cut(df["retr_pct"], bins=bins, labels=labels)

    results = {"edge": "E028", "run_id": "clean_rerun_2026-07-21",
               "supersedes_contaminated_artifact": "e028_fibonacci_ote_results.json",
               "split_metadata": meta,
               "n_bars": int(len(m)), "n_swings": len(swings), "n_legs": int(len(df)),
               "date_range": [str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])], "by_zone": {}}
    for lab in labels:
        sub = df[df.zone == lab]
        results["by_zone"][lab] = dict(n=int(len(sub)),
                                        continuation_rate=float(sub["continued"].mean()) if len(sub) else None,
                                        mean_cont_mag=float(sub["cont_mag"].mean()) if len(sub) else None,
                                        median_cont_mag=float(sub["cont_mag"].median()) if len(sub) else None)

    with open("e028_fibonacci_ote_clean_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
