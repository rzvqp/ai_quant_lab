"""ob_m5.py — §24 M5 execution refinement on the SURVIVING bull OB candidate (disp>=1.5, LN+NY, 2R), native-M5 window only (2021+).
Baseline = M15 resting limit at block high, stop below block low. M5-refined = tighten stop to the M5 swing-low observed during the
retest bar (same entry level), giving more R per unit risk. Report N, net-R, WR, median stop (pips), MAE, %missed. Classify M5.
No pullback-chase (that failed before); this is a stop-tightening refinement on an already-filled limit.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import ob_core as OB, htf_core as HC
from ob_contrast import limit_fill
from htf_m5 import load_m5

def main():
    m,H1,H4,P=OB.build(); yr=m["dt"].dt.year.values; hr=m["dt"].dt.hour.values
    mt=m["time"].values.astype("int64")
    t5,o5,h5,l5,c5=load_m5(); m5start=t5.min()
    ev=OB.detect_obs(P,1.5,"bull")
    base=[]; refi=[]; missed=0; used=0; stop_b=[]; stop_r=[]
    for e in ev:
        d=1; i=e["i"]; a=P["atr"][i]
        lvl=e["bhi"]; stopb=e["blo"]-OB.FLOOR_ATR*a
        if abs(lvl-stopb)<0.5*a: stopb=lvl-0.5*a
        k=limit_fill(P,e,lvl,d,i)
        if k is None: continue
        H_=hr[k]
        if not (8<=H_<20): continue                 # LN+NY
        tk=mt[k]                                     # M15 retest bar open time (unix s)
        if tk< m5start: continue                     # native M5 only
        used+=1
        ob=OB.retest_outcome(P,lvl,stopb,d,k,2.0,resolve_from=k)
        if ob is None: continue
        base.append(ob["net_R"]); stop_b.append(abs(lvl-stopb))
        # M5 window = the M15 retest bar [tk, tk+900): find M5 swing low there
        j0=np.searchsorted(t5,tk,side="left"); j1=np.searchsorted(t5,tk+900,side="left")
        if j1<=j0: missed+=1; continue
        m5low=l5[j0:j1].min()
        stopr=m5low-0.05
        if lvl-stopr<0.2*a:                          # too tight -> skip refinement (keep baseline)
            missed+=1; continue
        orf=OB.retest_outcome(P,lvl,stopr,d,k,2.0,resolve_from=k)
        if orf is None: missed+=1; continue
        refi.append(orf["net_R"]); stop_r.append(abs(lvl-stopr))
    base=np.array(base); refi=np.array(refi)
    print(f"bull candidate native-M5 (2021+) LN+NY: used={used}")
    print(f"BASELINE   N={len(base):4d} net={base.mean():+.3f} WR n/a  median_stop={np.median(stop_b)/HC.PIP:.0f}pip")
    if len(refi)>=30:
        print(f"M5-REFINED N={len(refi):4d} net={refi.mean():+.3f}  median_stop={np.median(stop_r)/HC.PIP:.0f}pip  refined_rate={len(refi)/max(used,1):.2f}")
        d=refi.mean()-base.mean()
        cls="VALUE_ADD" if d>0.05 else ("HARMFUL" if d<-0.05 else "NEUTRAL")
        print(f"M5 net-R delta={d:+.3f} -> {cls}")
    else:
        print(f"M5-REFINED N={len(refi)} too small; refinement rarely applicable")

if __name__=="__main__":
    main()
