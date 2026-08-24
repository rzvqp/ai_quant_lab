"""sweep_reversal.py — candidate SWR-1: LIQUIDITY-SWEEP REVERSAL (stop-run), a genuinely-distinct microstructure event.
Sweep-high = a bar whose HIGH exceeds the prior-N-bar swing high (grabs liquidity above) but CLOSES back below it (failed
breakout / wick rejection) -> SHORT. Sweep-low mirror -> LONG. Distinct from acceptance (continuation) and range-fade (boundary).
Stop beyond the sweep wick (structural), target rr2. Causal: prior extreme = rolling max/min over [t-N..t-1]. Test all-context +
D1-aligned (short if D1-down / long if D1-up) + high-vol; full gate (DISC/CONF/OOS, tail, per-year). STRESS. Data thru 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
from rs2_continuation import d1_trend_map
N=20

def sweep_events(m):
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); nn=len(m)
    ph=pd.Series(h).rolling(N).max().shift(1).to_numpy(); pl=pd.Series(l).rolling(N).min().shift(1).to_numpy()
    sweep_hi=(h>ph)&(c<ph)&np.isfinite(ph)   # wicked above prior high, closed back below -> short
    sweep_lo=(l<pl)&(c>pl)&np.isfinite(pl)   # wicked below prior low, closed back above -> long
    return sweep_hi, sweep_lo, ph, pl

def run(m, idx, side, sl, label, rr=2.0, verbose=True):
    n=len(m); keep=idx<n-1; idx=idx[keep]; sl=sl[keep]
    good=np.isfinite(sl)&(sl>0); idx=idx[good]; sl=sl[good]
    dd=sb.dedup_events(idx,8); p=np.isin(idx,dd); idx=idx[p]; sl=sl[p]
    tr=sb.simulate(m,idx,side,sl,rr=rr,horizon=96,scenario="STRESS")
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    if not verbose: return r,yr
    if len(r)<40: print(f"  {label}: N={len(r)} thin"); return r,yr
    sr=np.sort(r); k1=max(1,len(r)//100); k10=max(1,len(r)//10)
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]; negyr=sum(1 for y in set(yr) if r[yr==y].mean()<0)
    surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0
    print(f"  {label}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} best1rm={sr[:-k1].mean():+.4f} best10rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f} C {cf.mean():+.3f} O {oos.mean():+.3f} negyr{negyr}/{len(set(yr))} -> {'SURVIVOR' if surv else 'no'}")
    return r,yr

def main():
    m=CD.load_m15(); shi,slo,ph,pl=sweep_events(m); atr=m["atr"].to_numpy(); c=m["close"].to_numpy(); d1=d1_trend_map(m)
    ok=np.isfinite(atr)&(atr>0)
    Shi=np.where(shi&ok)[0]; Slo=np.where(slo&ok)[0]
    slS=m["high"].to_numpy()[Shi]-c[Shi]   # stop above the sweep wick (short)
    slL=c[Slo]-m["low"].to_numpy()[Slo]    # stop below the sweep wick (long)
    print(f"SWR-1 liquidity-sweep reversal. sweep-hi={len(Shi)} sweep-lo={len(Slo)}")
    run(m, Shi, -1, np.maximum(slS,0.5*atr[Shi]), "sweep-HI SHORT all      ")
    run(m, Slo, 1, np.maximum(slL,0.5*atr[Slo]), "sweep-LO LONG  all      ")
    # D1-aligned: short-sweep-hi when D1-down; long-sweep-lo when D1-up
    mS=d1[Shi]==0; mL=d1[Slo]==1
    run(m, Shi[mS], -1, np.maximum(slS[mS],0.5*atr[Shi[mS]]), "sweep-HI SHORT D1-down  ")
    run(m, Slo[mL], 1, np.maximum(slL[mL],0.5*atr[Slo[mL]]), "sweep-LO LONG  D1-up    ")
    # counter-aligned controls
    run(m, Shi[~mS], -1, np.maximum(slS[~mS],0.5*atr[Shi[~mS]]), "sweep-HI SHORT D1-up(ctl)")
    run(m, Slo[~mL], 1, np.maximum(slL[~mL],0.5*atr[Slo[~mL]]), "sweep-LO LONG  D1-dn(ctl)")

if __name__=="__main__":
    main()
