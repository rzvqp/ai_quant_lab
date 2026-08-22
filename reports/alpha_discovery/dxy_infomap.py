"""dxy_infomap.py — Stage A DXY information map (§5/§6/§9/§12/§13). Causal DXY state -> XAUUSD future-path
P(+X/-Y) lift vs XAUUSD era-global base, LONG/SHORT separate, lag curve {0,1,2,4}H, cross-era b0/b1/y2123,
event-deduped. Directed hypotheses (§6/§13): USD strengthening (impUp/effUp/accUp) -> XAUUSD SHORT path;
USD weakening (impDn/effDn/accDn) -> XAUUSD LONG path. No forced symmetry (both sides reported). NO threshold
mining (predeclared states). Incremental-over-price-only test (§7) follows for any material cross-era state.
"""
import numpy as np, pandas as pd
import dxy_data as dd
from state_path_m15 import passage_m15, Pm   # TF-agnostic first-passage; applied to XAUUSD H1
from state_m15_discover import dedup
COOL=6; H=24  # H1: 6h event-dedup, 24h outcome horizon (predeclared)
LABELS=[(50,50),(70,50),(100,70),(100,100),(150,75)]
ERAS=["b0","b1","y2123"]

def dxy_states(m, L):
    imp=m[f"d_imp_l{L}"].to_numpy(); acc=m[f"d_accel_l{L}"].to_numpy(); eff=m[f"d_eff_l{L}"].to_numpy()
    return {
      "dxyImpUp":  (imp>1.0, 'S'),   "dxyImpDn":  (imp<-1.0, 'L'),
      "dxyAccUp":  (acc>0.5, 'S'),   "dxyAccDn":  (acc<-0.5, 'L'),
      "dxyEffUp":  (eff>0.4, 'S'),   "dxyEffDn":  (eff<-0.4, 'L'),
    }

def main():
    print(f"STAGE A: DXY state -> XAUUSD path P(+70/-50) lift vs era base (H={H}h, dedup {COOL}h). Directed hypothesis side shown.")
    frames=dd.build(verbose=False)
    pas={}; base={}
    for era in ERAS:
        m=frames[era]; ou,od,mfe,mae=passage_m15(m,Hmax=H); pas[era]=(m,ou,od)
        allm=dedup(np.ones(len(m),bool),COOL)
        base[era]={(X,Y,s):Pm(ou,od,X,Y,s,H,allm)[0] for (X,Y) in LABELS for s in ('L','S')}
    # primary: lag0, hypothesized side, cross-era
    print("\n[LAG 0] DXY state (hypothesized side) -> XAUUSD P(+70/-50) & P(+100/-70) lift vs era base:")
    for sname in dxy_states(frames["b0"],0):
        row=[]
        stable70=[];
        for era in ERAS:
            m,ou,od=pas[era]; cond,side=dxy_states(m,0)[sname]
            cond=np.nan_to_num(cond.astype(float),nan=0).astype(bool); dd_=cond&dedup(cond,COOL); nE=int(dd_.sum())
            if nE<40: row.append(f"{era}:thin(n{nE})"); stable70.append(None); continue
            l70=Pm(ou,od,70,50,side,H,dd_)[0]-base[era][(70,50,side)]
            l100=Pm(ou,od,100,70,side,H,dd_)[0]-base[era][(100,70,side)]
            row.append(f"{era}:{l70:+.3f}/{l100:+.3f}(n{nE})"); stable70.append(l70)
        side=dxy_states(frames['b0'],0)[sname][1]
        vals=[v for v in stable70 if v is not None]
        flag=" <== CROSS_STABLE" if (len(vals)==3 and all(abs(v)>=0.02 for v in vals) and len(set(np.sign(vals)))==1) else ""
        print(f"  {sname:9s}->{side}: "+"  ".join(row)+flag)
    # lag curve for the two core impulse states (X1) — b0/b1/y2123 P(+70/-50) lift by lag
    print("\n[LAG CURVE] XAUUSD P(+70/-50) lift by DXY lag {0,1,2,4}H (impulse states, hypothesized side):")
    for sname in ("dxyImpUp","dxyImpDn"):
        for era in ERAS:
            m,ou,od=pas[era]; cells=[]
            for L in dd.LAGS:
                cond,side=dxy_states(m,L)[sname]; cond=np.nan_to_num(cond.astype(float),nan=0).astype(bool)
                dd_=cond&dedup(cond,COOL); nE=int(dd_.sum())
                cells.append(f"l{L}:{Pm(ou,od,70,50,side,H,dd_)[0]-base[era][(70,50,side)]:+.3f}(n{nE})" if nE>=40 else f"l{L}:thin")
            print(f"  {sname}->{side} {era}: "+" ".join(cells))

if __name__=="__main__":
    main()
