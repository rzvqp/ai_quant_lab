"""hazard.py — Frontier B: HAZARD/SURVIVAL. Does directional continuation change with time-since-structural-break (causal
elapsed time)? A fresh 20-bar-high break starts a potential up-leg; measure forward up-dn excursion + P(upFirst) vs
bars-since-break (fresh vs mature). Info-first: does hazard/continuation change MATERIALLY with age? Only then tradeable.
Causal: age = bars since last new 20-bar high (past-only). No like_at. Data thru 2026-07-27."""
import numpy as np, pandas as pd
import cur_data as CD
N=20; H=96; KA=1.5
def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    ph=pd.Series(h).rolling(N).max().shift(1).to_numpy()
    newhi=np.isfinite(ph)&(h>ph)
    # causal bars-since-last-new-high
    age=np.full(n,10**6); k=10**6
    for t in range(n):
        if newhi[t]: k=0
        elif k<10**6: k+=1
        age[t]=k
    fmax=pd.Series(h).rolling(H).max().shift(-H).to_numpy(); fmin=pd.Series(l).rolling(H).min().shift(-H).to_numpy()
    up=(fmax-c)/atr; dn=(c-fmin)/atr; yr=m["dt"].dt.year.to_numpy(); ok=np.isfinite(up)&np.isfinite(dn)&(atr>0)
    print("FRONTIER B: continuation vs time-since-new-high (hazard, info-first). up-dn = up-continuation strength.")
    def row(msk):
        nn=int(msk.sum())
        if nn<300: return f"n={nn}(thin)"
        return f"n={nn:6d} up-dn={np.nanmedian(up[msk])-np.nanmedian(dn[msk]):+.2f}"
    for lab,am in [("age 0-4 (fresh)",(age<=4)),("age 5-24",(age>=5)&(age<=24)),("age 25-96",(age>=25)&(age<=96)),("age 97+",(age>=97))]:
        line=f"  {lab:16s}: {row(ok&am)}"
        for pl,ym in [("D",yr<=2021),("C",(yr>=2022)&(yr<=2024)),("O",yr>=2025)]:
            line+=f" | {pl} {row(ok&am&ym)}"
        print(line)
    print("  => hazard material only if up-dn changes robustly with age ACROSS partitions (not era-split).")
if __name__=="__main__": main()
