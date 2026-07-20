"""E028 -- Fibonacci OTE -- Discovery-stage analysis (Flow A).

V0 (frozen, verbatim): "The 61.8%-79% 'optimal trade entry' retracement zone of an impulsive move
offers a statistically favorable continuation entry."

Method (disclosed):
1. Swing (fractal) detection on M15: a bar is a swing high if its high is the maximum among the 11
   bars centered on it (5 either side); swing low analogously with lows. k=5 is a plain, undisclosed-
   tuning default (not searched).
2. Zigzag construction: candidate fractal points are scanned in time order; consecutive same-type
   points are collapsed to the more extreme one; an opposite-type point confirms the pending extreme
   as a swing and starts a new pending point. This produces a strictly-alternating high/low swing
   sequence -- standard, disclosed zigzag logic, not proprietary.
3. For every consecutive swing triple (A, B, C): leg A->B is the "impulsive move," leg B->C is the
   retracement. retracement_pct = |C-B| / |A-B| (can exceed 1.0 -- a full reversal past A).
4. The swing AFTER C, D, is used to test continuation: continuation_magnitude = dir(A->B) * (D-B) /
   |A-B|, signed such that a POSITIVE value means D exceeded B in the original impulse direction
   (continuation), and non-positive means the market failed to make a new impulse-direction extreme
   before reversing again.
5. retracement_pct is bucketed into V0's own named zones (<0.382, 0.382-0.618, 0.618-0.79 [the OTE
   zone], 0.79-1.0, >1.0) and continuation_magnitude/continuation-rate is compared across zones.
"""
import json
import numpy as np
import pandas as pd
from _common import load

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
    m = load("M15")
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
    df.to_csv("e028_legs.csv", index=False)

    bins = [-0.001, 0.382, 0.618, 0.79, 1.0, np.inf]
    labels = ["lt_382", "382_618", "OTE_618_79", "79_100", "gt_100_full_reversal"]
    df["zone"] = pd.cut(df["retr_pct"], bins=bins, labels=labels)

    results = {"edge": "E028", "n_bars": int(len(m)), "n_swings": len(swings), "n_legs": int(len(df)),
               "date_range": [str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])], "by_zone": {}}
    for lab in labels:
        sub = df[df.zone == lab]
        results["by_zone"][lab] = dict(n=int(len(sub)),
                                        continuation_rate=float(sub["continued"].mean()) if len(sub) else None,
                                        mean_cont_mag=float(sub["cont_mag"].mean()) if len(sub) else None,
                                        median_cont_mag=float(sub["cont_mag"].median()) if len(sub) else None)

    with open("e028_fibonacci_ote_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
