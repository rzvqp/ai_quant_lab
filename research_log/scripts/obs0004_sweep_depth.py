"""OBS-0004 (NRQ-2): Does sweep DEPTH (ATR-normalized penetration) predict reversion better than
the binary close-inside rule? Pre-reg: penetration = (high-PDH)/ATR14 (up) or (PDL-low)/ATR14 (down).
Among REJECT interactions, test whether deeper penetration -> stronger reversion (continuation-excess
more negative). Falsified if penetration is uncorrelated with forward continuation-excess.
"""
from _lab import *
import numpy as np

df, meta = load("H1"); df, daily = add_prior_day(df)
rows = []  # (pen, cont_excess_K6, cont_excess_K12)
d6, d12 = drift(df, 6), drift(df, 12)
for day, g in df.groupby("day"):
    ph, pl = g["pdh"].iloc[0], g["pdl"].iloc[0]
    if not (ph == ph and pl == pl):
        continue
    idx = list(g.index)
    up = next((i for i in idx if df["high"].iat[i] > ph), None)
    if up is not None and df["close"].iat[up] < ph:  # up-reject
        atr = df["atr14"].iat[up]
        if atr and atr == atr and atr > 0 and fwd(df, up, 12) is not None:
            pen = (df["high"].iat[up] - ph) / atr
            rows.append((pen, 1 * (fwd(df, up, 6) - d6), 1 * (fwd(df, up, 12) - d12)))
    dn = next((i for i in idx if df["low"].iat[i] < pl), None)
    if dn is not None and df["close"].iat[dn] > pl:  # down-reject
        atr = df["atr14"].iat[dn]
        if atr and atr == atr and atr > 0 and fwd(df, dn, 12) is not None:
            pen = (pl - df["low"].iat[dn]) / atr
            rows.append((pen, -1 * (fwd(df, dn, 6) - d6), -1 * (fwd(df, dn, 12) - d12)))

pen = np.array([r[0] for r in rows]); e6 = np.array([r[1] for r in rows]); e12 = np.array([r[2] for r in rows])
print("OBS-0004 | reject interactions with ATR:", len(rows))
print(f"penetration (ATR units): median={np.median(pen):.2f} p90={np.percentile(pen,90):.2f}")
for name, e in (("K6", e6), ("K12", e12)):
    c = np.corrcoef(pen, e)[0, 1]
    print(f"\n{name}: corr(penetration, continuation-excess) = {c:+.3f}  (reversion => want NEGATIVE)")
    q = np.quantile(pen, [0, 1/3, 2/3, 1.0])
    for lab, lo, hi in (("shallow", q[0], q[1]), ("mid", q[1], q[2]), ("deep", q[2], q[3] + 1e9)):
        m = (pen >= lo) & (pen < hi if lab != "deep" else pen >= lo)
        st = summ(e[m].tolist()); loci, hici = boot_ci(e[m].tolist())
        print(line(f"  {lab}", st, f"CI95=[{loci:+.2f},{hici:+.2f}]"))
