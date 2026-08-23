"""cur_cr4.py — FRONTIER CR-4 (current-regime, info-first, LONG direction): capitulation-bounce. After an EXTREME fast
down-move (price fell >=2.5 ATR over 6 bars = capitulation) in current-like, is the forward UP-path robustly
concentrated (reliable bounce)? Distinct from generic reversion (this is capitulation-timed) and from the exhausted
short direction. If the bounce is robust (high-median up, low adverse-first-for-long) across current-like partitions ->
a current-regime LONG specialist. Info-first (no P&L). Data through 2026-07-27 (CEO: sufficient).
"""
import numpy as np, pandas as pd
import cur_data as CD
from cur_screen import like_at
from cur_cr2 import fwd

def main():
    m=CD.load_m15(); up,dn,af=fwd(m)  # af: +1 = up 1.5ATR first (favorable for LONG), -1 = down first (adverse for LONG)
    c=m["close"].to_numpy(); atr=m["atr"].to_numpy()
    drop6=(c-pd.Series(c).shift(6).to_numpy())/atr
    ev=drop6<=-2.5   # capitulation: fell >=2.5 ATR in 6 bars
    t=m["time"].to_numpy(); cl=like_at(t); yr=m["dt"].dt.year.to_numpy(); ok=np.isfinite(up)&np.isfinite(dn)&np.isfinite(drop6)
    ev=np.nan_to_num(ev.astype(float),nan=0).astype(bool)
    print("FRONTIER CR-4: CAPITULATION (fell>=2.5ATR/6bar) in current-like -> forward path (info-first, LONG bounce).")
    def row(msk):
        n=int(msk.sum())
        if n<40: return f"n={n}(thin)"
        afr=af[msk]; pup=float((afr[afr!=0]==1).mean()) if (afr!=0).sum() else float('nan')  # P(up 1.5ATR first) = bounce
        return f"n={n:5d} up={np.median(up[msk]):.2f} dn={np.median(dn[msk]):.2f} up-dn={np.median(up[msk])-np.median(dn[msk]):+.2f} P(upFirst)={pup:.3f}"
    print("  [current-like BASELINE]      :", row(cl&ok))
    print("  [CAPITULATION x current-like]:", row(cl&ok&ev))
    for lab,ym in [("DISC<=2021",yr<=2021),("CONF 22-24",(yr>=2022)&(yr<=2024)),("OOS 25-26",yr>=2025)]:
        print(f"    CAP {lab:10s}:", row(cl&ok&ev&ym))
    print("  [CAPITULATION x NON-cur DIAG]:", row((~cl)&ok&ev))

if __name__=="__main__":
    main()
