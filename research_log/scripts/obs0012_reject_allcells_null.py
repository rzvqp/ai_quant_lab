"""OBS-0012: Selection correction for the OBS-0008 lead. Run the matched-null reversion test on
ALL session x direction reject cells simultaneously, so the NY-up result is judged against how
many cells were examined. Pre-reg: for each cell, continuation-excess vs that session's baseline
drift; matched null from same-session bars (3000 resamples); left-tail p (reversion). Bonferroni
threshold = 0.05 / (#cells tested). NY-up is 'uniquely special' only if it is the sole cell below
the corrected threshold.
"""
from _lab import *
import numpy as np

df, meta = load("H1"); df, daily = add_prior_day(df)
rej = {}  # (dir, session) -> list of indices
for day, g in df.groupby("day"):
    ph, pl = g["pdh"].iloc[0], g["pdl"].iloc[0]
    idx = list(g.index)
    if ph == ph:
        up = next((i for i in idx if df["high"].iat[i] > ph), None)
        if up is not None and df["close"].iat[up] < ph:
            rej.setdefault(("up", df["session"].iat[up]), []).append(up)
    if pl == pl:
        dn = next((i for i in idx if df["low"].iat[i] < pl), None)
        if dn is not None and df["close"].iat[dn] > pl:
            rej.setdefault(("down", df["session"].iat[dn]), []).append(dn)

sess_idx = {s: df.index[df["session"] == s].tolist() for s in ("asia", "london", "ny", "late")}
rng = np.random.default_rng(7)
K = 6
cells = [(d, s) for (d, s) in rej if len(rej[(d, s)]) >= 25]
thr = 0.05 / len(cells)
print(f"OBS-0012 | K={K} | cells tested={len(cells)} | Bonferroni thr={thr:.4f}")
results = []
for (d, s) in cells:
    base = np.mean([fwd(df, i, K) for i in sess_idx[s] if fwd(df, i, K) is not None])
    sgn = 1 if d == "up" else -1
    ex = [sgn * (fwd(df, i, K) - base) for i in rej[(d, s)] if fwd(df, i, K) is not None]
    pool = np.array([sgn * (fwd(df, i, K) - base) for i in sess_idx[s] if fwd(df, i, K) is not None])
    m = float(np.mean(ex))
    null = np.array([pool[rng.integers(0, len(pool), len(ex))].mean() for _ in range(3000)])
    p_left = float((null <= m).mean())
    results.append((d, s, len(ex), m, p_left))
for d, s, n_, m, p in sorted(results, key=lambda r: r[4]):
    mark = "  *** < Bonferroni" if p < thr else ("  (nominal<0.05)" if p < 0.05 else "")
    print(f"  {d}-reject/{s:7s} n={n_:3d} excess={m:+7.2f} null_left_p={p:.4f}{mark}")
