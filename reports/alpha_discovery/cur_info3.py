"""cur_info3.py — current-regime PAYOFF asymmetry (magnitude, not frequency). On CURRENT_LIKE_POPULATION_V1, are
forward DOWN-excursions systematically larger than UP-excursions (in ATR)? If down-magnitude > up-magnitude robustly
across DISC/CONF/OOS, a short with asymmetric payoff could be profitable even at ~52% frequency = current-regime short
specialist foundation. Info-first, causal. Data through 2026-07-27 (disclosed stale).
"""
import numpy as np, pandas as pd
import cur_data as CD
from cur_screen import like_at
H=96

def main():
    m=CD.load_m15(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy()
    fmax=pd.Series(m["high"].to_numpy()).rolling(H).max().shift(-H).to_numpy()
    fmin=pd.Series(m["low"].to_numpy()).rolling(H).min().shift(-H).to_numpy()
    up=(fmax-c)/atr; dn=(c-fmin)/atr; ok=np.isfinite(up)&np.isfinite(dn)&np.isfinite(atr)&(atr>0)
    t=m["time"].to_numpy(); cl=like_at(t); yr=m["dt"].dt.year.to_numpy()
    print(f"Forward {H//4}h excursion (ATR): median UP vs DOWN, and down-minus-up. current-like partitioned. >0 = down bigger.")
    def med(msk):
        return (int(msk.sum()), float(np.median(up[msk])), float(np.median(dn[msk])))
    parts={"CUR-LIKE(all)":cl&ok,"  DISC<=2021":cl&ok&(yr<=2021),"  CONF 22-24":cl&ok&(yr>=2022)&(yr<=2024),
           "  OOS 25-26":cl&ok&(yr>=2025),"DIAG non-cur":(~cl)&ok}
    for k,msk in parts.items():
        n,u,d=med(msk); print(f"  {k:16s}: n={n:6d} up={u:.2f} down={d:.2f} down-up={d-u:+.3f}")

if __name__=="__main__":
    main()
