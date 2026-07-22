"""OBS-0005 (new perspective): Is the prior-day CLOSE (PDC) an intraday magnet / mean-reversion
pivot? Pre-reg: at each H1 bar, side = sign(close - PDC). Magnet hypothesis: forward K-bar move is
biased TOWARD PDC (negative when above, positive when below), i.e. detrended reversion.
Measure detrended forward move conditioned on side; a magnet => above-PDC mean<0 and below-PDC mean>0.
Control: also condition on distance-to-PDC in ATR units (stronger magnet when far?).
"""
from _lab import *
import numpy as np

df, meta = load("H1"); df, daily = add_prior_day(df)
df = df[df["pdc"].notna() & df["atr14"].notna() & (df["atr14"] > 0)].reset_index(drop=True)
print("OBS-0005 |", len(df), "H1 bars with PDC+ATR")
dist = (df["close"] - df["pdc"]) / df["atr14"]   # + = above PDC
for K in (6, 12):
    d = drift(df, K)
    fwdv = df["close"].shift(-K) - df["close"] - d   # detrended forward move (+=up)
    above = fwdv[(dist > 0.25)].dropna()
    below = fwdv[(dist < -0.25)].dropna()
    near = fwdv[(dist.abs() <= 0.25)].dropna()
    print(f"\nK={K} drift={d:+.2f} (magnet => above:mean<0, below:mean>0)")
    for lab, a in (("above PDC", above), ("near PDC", near), ("below PDC", below)):
        st = summ(a.tolist()); lo, hi = boot_ci(a.tolist())
        print(line(f"  {lab}", st, f"CI95=[{lo:+.2f},{hi:+.2f}]"))
    # correlation: distance vs forward move; magnet => negative
    both = pd.concat([dist, fwdv], axis=1).dropna()
    c = np.corrcoef(both.iloc[:, 0], both.iloc[:, 1])[0, 1]
    print(f"  corr(distance_to_PDC, forward move) = {c:+.3f}  (magnet => NEGATIVE)")
