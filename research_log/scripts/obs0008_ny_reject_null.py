"""OBS-0008 (NRQ-1b): Escalate the NY up-reject reversion vs a SESSION-MATCHED null.
Pre-reg: measure NY up-reject continuation-excess relative to the NY-session's OWN forward-move
baseline (not the global drift). Reversion beyond baseline confirmed only if reject-excess mean
CI95 < 0 AND below the 2.5th pct of a matched null (random NY bars, same K). Falsify if reject
mean is within the NY-bar forward-move distribution.
"""
from _lab import *
import numpy as np

df, meta = load("H1"); df, daily = add_prior_day(df)
n = len(df)
# NY up-reject interactions
recs = []
for day, g in df.groupby("day"):
    ph = g["pdh"].iloc[0]
    if not (ph == ph):
        continue
    idx = list(g.index)
    up = next((i for i in idx if df["high"].iat[i] > ph), None)
    if up is not None and df["close"].iat[up] < ph and df["session"].iat[up] == "ny":
        recs.append(up)
print("OBS-0008 | NY up-reject interactions:", len(recs))

ny_idx = df.index[df["session"] == "ny"].tolist()
for K in (6, 12):
    ny_drift = np.mean([fwd(df, i, K) for i in ny_idx if fwd(df, i, K) is not None])
    rej = [fwd(df, i, K) - ny_drift for i in recs if fwd(df, i, K) is not None]  # excess vs NY baseline
    st = summ(rej); lo, hi = boot_ci(rej)
    # matched null: distribution of mean over random NY-bar samples of same size
    pool = np.array([fwd(df, i, K) - ny_drift for i in ny_idx if fwd(df, i, K) is not None])
    rng = np.random.default_rng(7)
    null = np.array([pool[rng.integers(0, len(pool), len(rej))].mean() for _ in range(3000)])
    p_left = float((null <= st["mean"]).mean())
    print(line(f"K={K} NY up-reject excess", st, f"CI95=[{lo:+.2f},{hi:+.2f}]  null_left_p={p_left:.3f}"))
