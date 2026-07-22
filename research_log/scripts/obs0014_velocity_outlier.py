"""OBS-0014: Independent descriptive test of the lab's existing frozen Discovery Candidate DC-0001
('isolated single-bar velocity outlier followed by gradual multi-bar continuation'). Pre-reg:
velocity outlier = |close-open|/ATR14 > 1.5, isolated = prior bar |body|/ATR < 0.8. direction =
sign(close-open). Forward K-bar continuation = direction*(fwd - drift). DC-0001 predicts positive
continuation (CI95>0). Falsify if continuation excess <= 0.
"""
from _lab import *
import numpy as np

df, meta = load("H1")
df["body"] = df["close"] - df["open"]
df["vel"] = df["body"] / df["atr14"]
recs = []
for i in range(1, len(df)):
    v = df["vel"].iat[i]; vp = df["vel"].iat[i - 1]
    if v == v and vp == vp and abs(v) > 1.5 and abs(vp) < 0.8:
        recs.append((i, np.sign(df["body"].iat[i])))
print("OBS-0014 | isolated velocity-outlier bars:", len(recs))
for K in (3, 6, 12):
    d = drift(df, K)
    ex = [s * (fwd(df, i, K) - d) for (i, s) in recs if fwd(df, i, K) is not None]
    st = summ(ex); lo, hi = boot_ci(ex)
    flag = "  continuation CI>0" if lo > 0 else ("  reversal CI<0" if hi < 0 else "  n.s.")
    print(line(f"K={K} outlier->continuation", st, f"CI95=[{lo:+.2f},{hi:+.2f}]{flag}"))
