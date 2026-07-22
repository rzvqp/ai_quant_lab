"""OBS-0013: Temporal stability (pseudo-OOS) of the NY up-reject lead, WITHOUT spending the
reserved holdout. Split pre-cutoff data at 2025-01-01. Pre-reg: if the NY up-reject reversion is
real it should appear in BOTH halves (same sign, ideally nominal). If it lives in only one half,
it is likely noise/regime-specific. Continuation-excess vs within-half NY baseline, K6.
"""
from _lab import *
import numpy as np

df, meta = load("H1"); df, daily = add_prior_day(df)
df["half"] = np.where(df["dt"] < pd.Timestamp("2025-01-01T00:00:00+00:00"), "A(2023-24)", "B(2025)")
K = 6
for half in ("A(2023-24)", "B(2025)"):
    d = df[df["half"] == half]
    recs = []
    for day, g in d.groupby("day"):
        ph = g["pdh"].iloc[0]
        if not (ph == ph):
            continue
        idx = list(g.index)
        up = next((i for i in idx if df["high"].iat[i] > ph), None)
        if up is not None and df["close"].iat[up] < ph and df["session"].iat[up] == "ny":
            recs.append(up)
    ny_idx = d.index[d["session"] == "ny"].tolist()
    base = np.mean([fwd(df, i, K) for i in ny_idx if fwd(df, i, K) is not None])
    ex = [fwd(df, i, K) - base for i in recs if fwd(df, i, K) is not None]
    st = summ(ex); lo, hi = boot_ci(ex)
    print(line(f"{half} NY up-reject K6", st, f"CI95=[{lo:+.2f},{hi:+.2f}]"))
