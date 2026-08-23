"""m12_seq.py — M12 EVENT-SEQUENCING (info-first): break -> retest -> HOLD gated sequence vs the bare break (component). Event A:
close>prior-20-bar-high (up-break). Gate: within W bars price retests the level (low<=level) then CLOSES back above (hold).
Event B: the hold bar. §10 test: does the SEQUENCE (forward from hold) beat the COMPONENT (forward from break) AND hold era-robustly?
Pure price, causal (all steps at their close). Data cur_data M15 2011-2026."""
import numpy as np, pandas as pd
import cur_data as CD
from cur_cr2 import fwd
W=24
def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); n=len(m)
    ph=pd.Series(h).rolling(20).max().shift(1).to_numpy()
    brk=(c>ph)&(np.r_[False,~(c[:-1]>ph[:-1])])&np.isfinite(ph)
    up,dn,af=fwd(m); yr=m["dt"].dt.year.to_numpy()
    comp=[]; seq=[]  # break bars ; hold bars
    for i in np.where(brk)[0]:
        if i>=n-2: continue
        comp.append(i); lvl=ph[i]; end=min(i+1+W,n); retested=False; hold=-1
        for j in range(i+1,end):
            if not retested and l[j]<=lvl: retested=True
            elif retested and c[j]>lvl: hold=j; break
        if hold>=0 and hold<n-1: seq.append(hold)
    comp=np.array(comp); seq=np.array(seq)
    def pupasym(idx):
        idx=idx[idx<n-1]; ok=(af[idx]!=0); 
        pu=float((af[idx][ok]==1).mean()) if ok.sum()>=200 else float('nan')
        okk=np.isfinite(up[idx])&np.isfinite(dn[idx])
        asym=np.median(up[idx][okk])-np.median(dn[idx][okk]) if okk.sum()>=200 else float('nan')
        return pu,asym,len(idx)
    print(f"M12 break->retest->hold. breaks(component)={len(comp)} hold(sequence)={len(seq)}")
    for nm,ev in [("COMPONENT (break)",comp),("SEQUENCE (retest-hold)",seq)]:
        pu,asym,nn=pupasym(ev); line=f"  {nm}: n={nn} P(up1st)={pu:.3f} up-dn={asym:+.2f}"
        for pl,ym in [("D",yr<=2018),("C",(yr>=2019)&(yr<=2022)),("O",yr>=2023)]:
            e2=ev[np.isin(ev,np.where(ym)[0])]; pu2,as2,n2=pupasym(e2); line+=f" | {pl} up-dn={as2:+.2f}"
        print(line)
    print("  => M12 edge only if SEQUENCE beats COMPONENT AND is era-robust (up-dn>0 all partitions).")
if __name__=="__main__": main()
