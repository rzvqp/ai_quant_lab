"""Monthly event census, XAUUSD M15, pre-holdout. Mechanical definitions so counts are reproducible.
Bookkeeping only -- discovery still comes from replay observation.

compression   : >=4 consecutive bars with range < 0.5x rolling20 avg range (counted once per run)
sweep         : high > prior-20 high AND close back below it (or mirror on lows)
false_breakout: close beyond prior-20 extreme, then close back inside within 3 bars
displacement  : range > 2x rolling20 avg range AND |close-open| > 0.6x range
absorption    : volume > 2x rolling20 avg volume AND range < rolling20 avg range
"""
from _lab import *
import numpy as np, pandas as pd

df, meta = load("M15")
df = df.reset_index(drop=True)
o,h,l,c,v = (df[x].values for x in ("open","high","low","close","volume"))
rng = h - l
avgr = pd.Series(rng).rolling(20).mean().values
avgv = pd.Series(v).rolling(20).mean().values
ph = pd.Series(h).rolling(20).max().shift(1).values
pl = pd.Series(l).rolling(20).min().shift(1).values
n = len(df)

ev = {k: np.zeros(n, bool) for k in
      ("compression","sweep","false_breakout","displacement","absorption")}

small = rng < 0.5*avgr
run = 0
for i in range(n):
    if small[i] and avgr[i] == avgr[i]:
        run += 1
        if run == 4: ev["compression"][i] = True   # count once per compression run
    else:
        run = 0

for i in range(n):
    if avgr[i] != avgr[i]: continue
    if (h[i] > ph[i] and c[i] < ph[i]) or (l[i] < pl[i] and c[i] > pl[i]):
        ev["sweep"][i] = True
    if rng[i] > 2*avgr[i] and abs(c[i]-o[i]) > 0.6*rng[i]:
        ev["displacement"][i] = True
    if v[i] > 2*avgv[i] and rng[i] < avgr[i]:
        ev["absorption"][i] = True
    if c[i] > ph[i]:
        if any(c[j] < ph[i] for j in range(i+1, min(i+4, n))): ev["false_breakout"][i] = True
    elif c[i] < pl[i]:
        if any(c[j] > pl[i] for j in range(i+1, min(i+4, n))): ev["false_breakout"][i] = True

df["ym"] = df["dt"].dt.to_period("M").astype(str)
for k, mask in ev.items(): df[k] = mask
g = df.groupby("ym")[list(ev)].sum()
g["TOTAL"] = g.sum(axis=1)
print(f"XAUUSD M15 event census | {meta['n_bars_used']} bars | "
      f"{meta['min_date_used'][:10]} -> {meta['max_date_used'][:10]}\n")
print(g.to_string())
print(f"\nGRAND TOTAL EVENTS: {int(g['TOTAL'].sum())}")
