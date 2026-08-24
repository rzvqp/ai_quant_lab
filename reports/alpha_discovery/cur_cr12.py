"""cur_cr12.py — FRONTIER CR-12 (current-regime): FADE the coil breakout (evidence-derived inverse of CR-11, which showed
coil breakouts FAIL, WR 0.341). On an up-break -> SHORT back toward the coil; on a down-break -> LONG back toward the coil.
Target = coil MID (revert into the coil); STOP = one coil-height beyond the breakout (thesis wrong = it really ran). This is
a SHORT-VOLATILITY / mean-reversion structure: wins small often, loses big rarely. Therefore the skepticism gate is FLIPPED
to a LEFT-TAIL / catastrophe test (worst-10%-removed, worst single trade, max consecutive damage) — a fade that only 'works'
by luckily avoiding a big run is not robust.

Preregistered. Survivor requires: net>0 AND all partitions (DISC/CONF/OOS)>0 AND positive EVEN with the single worst trade
removed is NOT the point — instead require the strategy is not one-bad-trade-from-ruin: report worst trade, worst-10% mean,
and that OOS>0. BOTH sides must contribute. Neighbor stability L in {18,24,32}. Ratified sb.simulate, STRESS. Data thru 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
from cur_screen import like_at

def breakout_bars(m, L, W=None):
    if W is None: W=2*L
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    hh=pd.Series(h).rolling(L).max().to_numpy(); ll=pd.Series(l).rolling(L).min().to_numpy()
    width=hh-ll; mid=(hh+ll)/2.0
    medw=pd.Series(width).rolling(8*L).median().shift(1).to_numpy()
    contr=(width<0.6*medw)&np.isfinite(medw)&np.isfinite(atr)&(atr>0)&(width>0)
    idx=[]; fol=[]; wdl=[]; midl=[]; last=-10**9
    for t0 in np.where(np.nan_to_num(contr.astype(float),nan=0).astype(bool))[0]:
        if t0-last<L: continue
        ch=hh[t0]; clo=ll[t0]; end=min(t0+1+W,n-1)
        for j in range(t0+1,end):
            if c[j]>ch: idx.append(j); fol.append(1); wdl.append(width[t0]); midl.append(mid[t0]); last=j; break
            if c[j]<clo: idx.append(j); fol.append(-1); wdl.append(width[t0]); midl.append(mid[t0]); last=j; break
    return np.array(idx,int),np.array(fol,int),np.array(wdl,float),np.array(midl,float)

def run(m, L, verbose=True):
    idx,fol,wd,mid=breakout_bars(m,L)
    if len(idx)==0: return np.array([]),np.array([]),np.array([])
    c=m["close"].to_numpy(); ce=c[idx]
    fade=-fol
    stop=1.0*wd                                   # one coil-height beyond breakout
    tgt=np.abs(ce-mid)                            # distance back to coil mid
    rrv=np.clip(tgt/np.maximum(stop,1e-9),0.2,2.0)
    rrm=float(np.median(rrv))
    Rs=[]; sd=[]; ents=[]
    for s in (1,-1):
        p=fade==s
        if p.sum()==0: continue
        tr=sb.simulate(m,idx[p],s,stop[p],rr=rrm,horizon=96,scenario="STRESS")
        te=tr["t_entry"].to_numpy(); cl=like_at(te); tr=tr[cl]
        Rs.append(tr["R"].to_numpy()); sd.append(np.full(len(tr),s)); ents.append(tr["t_entry"].to_numpy())
    r=np.concatenate(Rs); sd=np.concatenate(sd); te=np.concatenate(ents)
    yr=pd.Series(pd.to_datetime(te,unit="s",utc=True)).dt.year.to_numpy()
    if not verbose: return r,yr,sd
    print(f"CR-12 FADE coil-breakout L={L} (current-like, stop=coil-height, target=mid, rr={rrm:.2f}): N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f}")
    print(f"  long N={int((sd==1).sum())} avgR={r[sd==1].mean():+.4f} | short N={int((sd==-1).sum())} avgR={r[sd==-1].mean():+.4f}")
    print("  per-year:", {int(y):(round(float(r[yr==y].mean()),3),int((yr==y).sum())) for y in sorted(set(yr))})
    sr=np.sort(r); k10=max(1,len(r)//10)
    print(f"  LEFT-TAIL: worst={sr[0]:+.2f} worst-10%-mean={sr[:k10].mean():+.3f} worst-10%-REMOVED={sr[k10:].mean():+.4f} | best-10%-removed={sr[:-k10].mean():+.4f}")
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    print(f"  DISC<=2021 {d.mean():+.4f}(n{len(d)}) | CONF 22-24 {cf.mean():+.4f}(n{len(cf)}) | OOS 25+ {oos.mean():+.4f}(n{len(oos)})")
    both=(sd==1).sum()>=20 and (sd==-1).sum()>=20 and r[sd==1].mean()>0 and r[sd==-1].mean()>0
    surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and both
    print(f"  -> {'SURVIVOR CANDIDATE (net>0, all partitions>0, both sides>0)' if surv else 'NOT a survivor'}")
    return r,yr,sd

def main():
    m=CD.load_m15()
    print("=== PRIMARY: coil L=24 ===")
    run(m,24)
    print("\n=== NEIGHBOR STABILITY: L=18 and L=32 ===")
    for L in (18,32):
        r,yr,sd=run(m,L,verbose=False)
        if len(r)==0: continue
        sr=np.sort(r); k10=max(1,len(r)//10); d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
        print(f"  L={L} N={len(r)} avgR={r.mean():+.4f} worst10%rm={sr[k10:].mean():+.4f} | D {d.mean():+.3f} C {cf.mean():+.3f} O {oos.mean():+.3f} | L{r[sd==1].mean():+.3f} S{r[sd==-1].mean():+.3f}")

if __name__=="__main__":
    main()
