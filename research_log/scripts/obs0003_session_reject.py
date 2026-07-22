"""OBS-0003 (NRQ-1): Is prior-day-extreme sweep-REJECT reversion a SESSION phenomenon (NY)?
Pre-reg: for reject interactions, continuation-excess = s*(fwd_K - drift). Reversion => excess<0.
 Claim (from OBS-0001 residue): up-reject reverses in NY. Confirmed only if NY CI95 < 0 AND
 other sessions do not, i.e. genuine session specificity (not one cell of many by chance).
"""
from _lab import *

df, meta = load("H1"); df, daily = add_prior_day(df)
recs = []  # (dir, session, i)
for day, g in df.groupby("day"):
    ph, pl = g["pdh"].iloc[0], g["pdl"].iloc[0]
    if not (ph == ph and pl == pl):
        continue
    idx = list(g.index)
    up = next((i for i in idx if df["high"].iat[i] > ph), None)
    if up is not None and df["close"].iat[up] < ph:  # up-reject
        recs.append(("up", df["session"].iat[up], up))
    dn = next((i for i in idx if df["low"].iat[i] < pl), None)
    if dn is not None and df["close"].iat[dn] > pl:  # down-reject
        recs.append(("down", df["session"].iat[dn], dn))
print("OBS-0003 | reject interactions:", len(recs))
for K in (6, 12):
    d = drift(df, K)
    print(f"\nK={K} drift={d:+.2f}  (continuation-excess; reversion = NEGATIVE)")
    for bd in ("up", "down"):
        for ss in ("asia", "london", "ny", "late"):
            s = 1 if bd == "up" else -1
            vals = [s * (fwd(df, i, K) - d) for (b, x, i) in recs
                    if b == bd and x == ss and fwd(df, i, K) is not None]
            if len(vals) >= 20:
                st = summ(vals); lo, hi = boot_ci(vals)
                flag = "  <-- reversion CI<0" if hi < 0 else ("  <-- continuation CI>0" if lo > 0 else "")
                print(line(f"{bd}-reject/{ss}", st, f"CI95=[{lo:+.2f},{hi:+.2f}]{flag}"))
