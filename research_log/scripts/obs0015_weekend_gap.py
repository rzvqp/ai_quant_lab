"""OBS-0015 (new perspective): do weekend gaps fill? Pre-reg: weekend gap = first bar's open of a
new week - prior week's last close (>1 calendar-day time jump). 'Fill' = price trades back to the
prior close within the next 24 H1 bars. Belief: gaps fill. Report fill rate + bootstrap CI, and
whether up-gaps and down-gaps differ. Also gap-size in ATR units.
"""
from _lab import *
import numpy as np

df, meta = load("H1")
dt = df["dt"].values
gaps = []  # (i, gap, atr)
for i in range(1, len(df)):
    jump = (df["dt"].iat[i] - df["dt"].iat[i - 1]).total_seconds() / 3600.0
    if jump > 24:  # weekend / holiday gap
        gap = df["open"].iat[i] - df["close"].iat[i - 1]
        atr = df["atr14"].iat[i - 1]
        if atr and atr == atr and atr > 0:
            gaps.append((i, gap, atr))
print("OBS-0015 | weekend/holiday gaps:", len(gaps))
print(f"  median |gap| = {np.median([abs(g)/a for _,g,a in gaps]):.2f} ATR")

def fill_rate(subset):
    fills = []
    for i, gap, atr in subset:
        prev_close = df["close"].iat[i - 1]
        window = df["close"].iloc[i:i + 24].values
        lo = df["low"].iloc[i:i + 24].values; hi = df["high"].iloc[i:i + 24].values
        if gap > 0:      # up-gap fills if price trades back DOWN to prev_close
            filled = np.any(lo <= prev_close)
        else:
            filled = np.any(hi >= prev_close)
        fills.append(1.0 if filled else 0.0)
    return fills

allf = fill_rate(gaps); upf = fill_rate([g for g in gaps if g[1] > 0]); dnf = fill_rate([g for g in gaps if g[1] < 0])
for lab, f in (("all gaps", allf), ("up-gaps", upf), ("down-gaps", dnf)):
    a = np.array(f); lo, hi = boot_ci(a.tolist())
    print(f"  {lab:10s} n={len(a):3d} fill_rate(24h)={a.mean():.3f} CI95=[{lo:.3f},{hi:.3f}]")
