"""dxy_transitions.py — §20 bounded DXY TRANSITIONS (completes the frontier order). DXY state A(4h ago)->B(now)
sequences: USD impulse-exhaustion (strong push fading) + USD reversal (direction flip). -> XAUUSD path P(+70/-50)
lift vs XAUUSD era base, directed side (§13), cross-era b0/b1/y2123, event-deduped. Interpretable, predeclared
(no mining). Uses the lagged DXY features {l0,l4} already in the aligned frames.
"""
import numpy as np, pandas as pd
import dxy_data as dd
from state_path_m15 import passage_m15, Pm
from state_m15_discover import dedup
COOL=6; H=24
ERAS=["b0","b1","y2123"]

def trans(m):
    i0=m["d_imp_l0"].to_numpy(); i4=m["d_imp_l4"].to_numpy(); r1=m["d_ret1_l0"].to_numpy()
    return {
      "usdUpExhaust->L": ((i4>1.0)&(i0<0.3), 'L'),    # USD up-push fading -> XAUUSD reversal up
      "usdDnExhaust->S": ((i4<-1.0)&(i0>-0.3), 'S'),  # USD down-push fading -> XAUUSD reversal down
      "usdRevUp->S":     ((i4<-0.5)&(r1>0), 'S'),      # USD turning up -> XAUUSD short
      "usdRevDn->L":     ((i4>0.5)&(r1<0), 'L'),       # USD turning down -> XAUUSD long
    }

def main():
    print(f"§20 DXY TRANSITIONS: DXY A(4h)->B(now) -> XAUUSD P(+70/-50) lift vs era base (H={H}h, dedup {COOL}h).")
    frames=dd.build(verbose=False); pas={}; base={}
    for era in ERAS:
        m=frames[era]; ou,od,_,_=passage_m15(m,Hmax=H); pas[era]=(m,ou,od)
        allm=dedup(np.ones(len(m),bool),COOL)
        base[era]={s:Pm(ou,od,70,50,s,H,allm)[0] for s in ('L','S')}
    for tname in trans(frames["b0"]):
        row=[]; vals=[]
        for era in ERAS:
            m,ou,od=pas[era]; cond,side=trans(m)[tname]
            cond=np.nan_to_num(cond.astype(float),nan=0).astype(bool); dd_=cond&dedup(cond,COOL); nE=int(dd_.sum())
            if nE<40: row.append(f"{era}:thin(n{nE})"); vals.append(None); continue
            lift=Pm(ou,od,70,50,side,H,dd_)[0]-base[era][side]; row.append(f"{era}:{lift:+.3f}(n{nE})"); vals.append(lift)
        side=trans(frames['b0'])[tname][1]
        v=[x for x in vals if x is not None]
        flag=" <== CROSS_STABLE" if (len(v)==3 and all(abs(x)>=0.02 for x in v) and len(set(np.sign(v)))==1) else ""
        print(f"  {tname:16s}: "+"  ".join(row)+flag)

if __name__=="__main__":
    main()
