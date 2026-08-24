"""rs3_pullback.py — RANGE-regime specialist candidate RS-3: D1-ALIGNED in-range pullback fade ('buy the flag-dip / sell the
flag-rally'). Leverages the RS-2 confirmed lever (D1 alignment materially matters) applied to the DENSE in-range population
(every boundary rejection, not just terminal breakouts). Explains RS-1's failure: it faded BOTH sides incl. counter-trend.
Here: in RANGE_REGIME_V1, D1-trend-UP -> LONG at lower-boundary rejection only; D1-trend-DOWN -> SHORT at upper-boundary
rejection only. Stop beyond that boundary + 0.5ATR floor, target = range mid. Preregistered, distinct identity.

Skepticism gate: per-year, DISC/CONF/OOS all>0, best & worst-10%-removed, neighbor, both directions, regime+alignment
specificity (counter-aligned control must be worse), effective N. STRESS, dedup 8. Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
import range_regime as RR, range_fade as RF
from rs2_continuation import d1_trend_map

def run(m,i,lo_,hi_,mid_,d1up,counter=False,verbose=True):
    (S,slS,tgS),(Lg,slL,tgL)=RF.entries(m,i,lo_,hi_,mid_,gated=True)
    def filt(idx,sl,tg,want):
        keep=d1up[idx]==want; return idx[keep],sl[keep],tg[keep]
    if not counter:
        S,slS,tgS=filt(S,slS,tgS,0)     # shorts only when D1 DOWN
        Lg,slL,tgL=filt(Lg,slL,tgL,1)   # longs only when D1 UP
    else:
        S,slS,tgS=filt(S,slS,tgS,1)     # counter control: shorts when D1 UP
        Lg,slL,tgL=filt(Lg,slL,tgL,0)
    rS,yS=RF.sim_side(m,S,slS,tgS,-1); rL,yL=RF.sim_side(m,Lg,slL,tgL,1)
    r=np.concatenate([rS,rL]); yr=np.concatenate([yS,yL]); sd=np.concatenate([np.full(len(rS),-1),np.full(len(rL),1)])
    if not verbose: return r,yr,sd
    if len(r)<40: print(f"  {'COUNTER' if counter else 'ALIGNED'}: N={len(r)} thin"); return r,yr,sd
    sr=np.sort(r); k10=max(1,len(r)//10); d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    both=len(rS)>=20 and len(rL)>=20 and rS.mean()>0 and rL.mean()>0
    surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0 and sr[k10:].mean()>0 and both
    print(f"  {'COUNTER(control)' if counter else 'ALIGNED'}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} | short {rS.mean():+.3f}(n{len(rS)}) long {rL.mean():+.3f}(n{len(rL)})")
    print(f"    best10%rm={sr[:-k10].mean():+.4f} worst10%rm={sr[k10:].mean():+.4f} | D {d.mean():+.3f}(n{len(d)}) C {cf.mean():+.3f}(n{len(cf)}) O {oos.mean():+.3f}(n{len(oos)}) -> {'SURVIVOR' if surv else 'no'}")
    return r,yr,sd

def main():
    m=CD.load_m15(); i,lo_,hi_,mid_=RF.build(m); d1up=d1_trend_map(m)
    print(f"RS-3 D1-aligned in-range pullback fade (gated to {RR.FP})")
    run(m,i,lo_,hi_,mid_,d1up,counter=False)
    run(m,i,lo_,hi_,mid_,d1up,counter=True)
    print("  (aligned should beat counter => D1 conditioning materially matters on the dense in-range population)")

if __name__=="__main__":
    main()
