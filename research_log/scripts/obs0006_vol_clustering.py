"""OBS-0006 (ORQ-007): Volatility clustering on the official metric (Parkinson log-range
r = ln(high/low)) -- and its CONDITION. Pre-reg: measure lag autocorr of r on H1; and the
condition -- is 1-bar clustering stronger in some sessions than others? Also conditional mean
r_{t+1} given r_t quartile. Clustering is expected (confirmation of the volatility primitive);
the research question is WHERE it concentrates (ORQ-007 clustering-condition).
"""
from _lab import *
import numpy as np

df, meta = load("H1")
r = np.log(df["high"] / df["low"]).replace([np.inf, -np.inf], np.nan).dropna()
r = r[r > 0]
print("OBS-0006 |", len(r), "H1 Parkinson log-range obs")
rr = r.values
print("\nlag autocorrelation of r_t (Parkinson log-range):")
for lag in (1, 2, 3, 6, 12, 24):
    a = rr[:-lag]; b = rr[lag:]
    print(f"  lag {lag:2d}: acf={np.corrcoef(a, b)[0,1]:+.3f}")

q = np.quantile(rr, [0.25, 0.75])
nxt = rr[1:]; cur = rr[:-1]
loq = nxt[cur <= q[0]]; hiq = nxt[cur >= q[1]]
print(f"\nmean r_(t+1): after LOW-quartile r_t = {loq.mean():.5f}   after HIGH-quartile r_t = {hiq.mean():.5f}"
      f"   ratio={hiq.mean()/loq.mean():.2f}x")

print("\nlag-1 clustering by session (acf of r within each session's bars):")
dfr = df.copy(); dfr["r"] = np.log(dfr["high"] / dfr["low"])
for ss in ("asia", "london", "ny", "late"):
    s = dfr[dfr["session"] == ss]["r"].replace([np.inf, -np.inf], np.nan).dropna().values
    if len(s) > 50:
        print(f"  {ss:7s} n={len(s):5d} acf1={np.corrcoef(s[:-1], s[1:])[0,1]:+.3f} mean_r={s.mean():.5f}")
