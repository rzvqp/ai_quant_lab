"""OBS-0017 VALIDATION of an observation made in TradingView Replay (XAUUSD H4, 2025-03-09):
a swing high (~2954.96) was MARGINALLY overshot (2956.31, +0.05%) then violently reversed (-124pt)
with a failed retest. Observation-originated question: at H4 structural swing highs, does a MARGINAL
overshoot precede reversal more than a DECISIVE break?

Pre-reg: swing high = pivot high (higher than +/-3 bars). First later bar j with high_j > SH is the
'exceed' event; overshoot = (high_j - SH)/ATR14_j. continuation-excess = (fwd_K - drift_K) [up dir].
Marginal-sweep hypothesis: small overshoots -> reversal (excess<0); decisive -> continuation (excess>0),
so corr(overshoot, excess) > 0 and marginal tercile CI<0. Falsify if overshoot is uninformative.
Symmetric test on swing lows.
"""
from _lab import *
import numpy as np

df, meta = load("H4")
n = len(df)
hi = df["high"].values; lo = df["low"].values; cl = df["close"].values; atr = df["atr14"].values
P = 3  # pivot half-width

def pivots_high():
    out = []
    for i in range(P, n - P):
        if hi[i] == max(hi[i - P:i + P + 1]):
            out.append(i)
    return out

def pivots_low():
    out = []
    for i in range(P, n - P):
        if lo[i] == min(lo[i - P:i + P + 1]):
            out.append(i)
    return out

def events(pivs, side):
    ev = []  # (overshoot_atr, cont_excess_K6, cont_excess_K12, closed_back)
    d6, d12 = drift(df, 6), drift(df, 12)
    for pi in pivs:
        level = hi[pi] if side == "high" else lo[pi]
        j = None
        for k in range(pi + P + 1, min(pi + 60, n)):   # first exceedance within ~60 bars
            if (side == "high" and hi[k] > level) or (side == "low" and lo[k] < level):
                j = k; break
        if j is None or atr[j] != atr[j] or atr[j] <= 0 or j + 12 >= n:
            continue
        over = ((hi[j] - level) if side == "high" else (level - lo[j])) / atr[j]
        s = 1 if side == "high" else -1
        e6 = s * ((cl[j + 6] - cl[j]) - (d6 if side == "high" else -d6))
        e12 = s * ((cl[j + 12] - cl[j]) - (d12 if side == "high" else -d12))
        closed_back = (cl[j] < level) if side == "high" else (cl[j] > level)
        ev.append((over, e6, e12, closed_back))
    return ev

for side, pivs in (("high", pivots_high()), ("low", pivots_low())):
    ev = events(pivs, side)
    over = np.array([e[0] for e in ev]); e6 = np.array([e[1] for e in ev]); e12 = np.array([e[2] for e in ev])
    cb = np.array([e[3] for e in ev])
    print(f"\n=== swing {side}s: {len(ev)} first-exceedance events | median overshoot={np.median(over):.2f} ATR "
          f"| closed-back-inside rate={cb.mean():.2f} ===")
    for name, e in (("K6", e6), ("K12", e12)):
        c = np.corrcoef(over, e)[0, 1]
        print(f"  {name}: corr(overshoot, continuation-excess)={c:+.3f}  (marginal-reversal => POSITIVE corr)")
        q = np.quantile(over, [0, 1/3, 2/3, 1.0])
        for lab, a, b in (("marginal", q[0], q[1]), ("mid", q[1], q[2]), ("decisive", q[2], 1e9)):
            m = (over >= a) & (over < b) if lab != "decisive" else (over >= a)
            st = summ(e[m].tolist()); loci, hici = boot_ci(e[m].tolist())
            print(line(f"    {lab}", st, f"CI95=[{loci:+.2f},{hici:+.2f}]"))
