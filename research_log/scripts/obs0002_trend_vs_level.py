"""OBS-0002 (NRQ-3): Is prior-day break-and-hold 'continuation' a LEVEL effect or TREND-conditioning?
Pre-reg: continuation-excess = s*(fwd_K - drift_K), s=+1 up-break / -1 down-break.
 Level hypothesis: continuation-excess > 0 in ALL trend regimes (incl. break AGAINST trend).
 Trend hypothesis: continuation-excess > 0 only when break ALIGNS with trend (EMA200), <=0 against.
Falsified level-effect if the 'against-trend' cells are <= 0 (CI not above 0).
"""
from _lab import *

df, meta = load("H1")
df, daily = add_prior_day(df)
df["ema200"] = ema(df["close"], 200)
print("OBS-0002 |", meta["n_bars_used"], "H1 bars", meta["min_date_used"][:10], "->", meta["max_date_used"][:10])

recs = []  # (break_dir, regime, i)
for day, g in df.groupby("day"):
    ph, pl = g["pdh"].iloc[0], g["pdl"].iloc[0]
    if not (ph == ph and pl == pl):
        continue
    idx = list(g.index)
    up = next((i for i in idx if df["high"].iat[i] > ph), None)
    if up is not None and df["close"].iat[up] > ph:
        recs.append(("up", "up" if df["close"].iat[up] > df["ema200"].iat[up] else "down", up))
    dn = next((i for i in idx if df["low"].iat[i] < pl), None)
    if dn is not None and df["close"].iat[dn] < pl:
        recs.append(("down", "up" if df["close"].iat[dn] > df["ema200"].iat[dn] else "down", dn))

for K in (6, 12):
    d = drift(df, K)
    print(f"\nK={K}  drift={d:+.2f}   (continuation-excess; + = continues in break dir beyond drift)")
    for bd in ("up", "down"):
        for reg in ("up", "down"):
            s = 1 if bd == "up" else -1
            vals = [s * (fwd(df, i, K) - d) for (b, r, i) in recs
                    if b == bd and r == reg and fwd(df, i, K) is not None]
            st = summ(vals); lo, hi = boot_ci(vals)
            aligned = "ALIGNED" if bd == reg else "AGAINST"
            print(line(f"{bd}-break/{reg}-trend[{aligned}]", st, f"CI95=[{lo:+.2f},{hi:+.2f}]"))
