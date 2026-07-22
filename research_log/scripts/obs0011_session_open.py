"""OBS-0011 (new perspective): do session opens trigger volatility expansion / directional bias?
Pre-reg: compare Parkinson r at the London-open hour (07:00 UTC) and NY-open hour (13:00 UTC) to
the all-hours mean; and test whether the open bar's direction predicts the next 3 bars (continuation).
Descriptive. Expansion confirmed if open-hour r CI95 > all-hours mean.
"""
from _lab import *
import numpy as np

df, meta = load("H1")
df["r"] = np.log(df["high"] / df["low"]); df = df[df["r"] > 0].copy()
df["hour"] = df["dt"].dt.hour
allmean = df["r"].mean()
print(f"OBS-0011 | all-hours mean r = {allmean*1e4:.1f} (x1e4)")
for name, h in (("London open 07h", 7), ("NY open 13h", 13), ("Asia ~00h", 0)):
    sub = df[df["hour"] == h]
    a = sub["r"].values * 1e4
    lo, hi = boot_ci(a.tolist())
    # directional continuation: sign(open-bar close-open) vs next-3-bar move
    idx = sub.index.tolist()
    cont = []
    for i in idx:
        if i + 3 < len(df):
            openbar = np.sign(df["close"].iat[i] - df["open"].iat[i])
            nxt = df["close"].iat[i + 3] - df["close"].iat[i]
            if openbar != 0:
                cont.append(openbar * nxt)   # + = continuation
    st = summ(cont); clo, chi = boot_ci(cont)
    print(f"  {name:16s} r_mean={a.mean():.1f} CI[{lo:.1f},{hi:.1f}] "
          f"{'EXPANSION' if lo>allmean*1e4 else 'no-exp'} | open->next3 cont mean={st['mean']:+.2f} CI[{clo:+.2f},{chi:+.2f}]")
