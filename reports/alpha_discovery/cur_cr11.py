"""cur_cr11.py — FRONTIER CR-11 (current-regime): DIRECTION-AGNOSTIC volatility-expansion (two-sided coil breakout). The
evidence-driven pivot after 8 representation classes converged on the ~0.54 DIRECTIONAL ordering ceiling — consistent with
R26 (predictable VOLATILITY, unpredictable DIRECTION). So stop betting on direction: after a volatility CONTRACTION coil,
arm a TWO-SIDED breakout and take whichever side breaks FIRST (long on up-break / short on down-break), tiny mid-coil stop,
measured-move target (asymmetric RR ~2). The direction coinflip becomes IRRELEVANT — we ride the expansion whichever way it
resolves. This monetizes the PREDICTABLE quantity (vol clustering: contraction precedes expansion), not the unpredictable one.

Preregistered. Full skepticism gate: per-year, partition (DISC/CONF/OOS all>0), best-10%-removed tail test, BOTH-SIDES
contribute (not a one-directional artifact), and neighbor stability across L in {18,24,32}. Ratified sb.simulate, STRESS.
Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
from cur_screen import like_at

def straddle_entries(m, L, W=None):
    if W is None: W=2*L
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    hh=pd.Series(h).rolling(L).max().to_numpy()   # coil high over [t0-L+1..t0] (causal at t0)
    ll=pd.Series(l).rolling(L).min().to_numpy()
    width=hh-ll; mid=(hh+ll)/2.0
    medw=pd.Series(width).rolling(8*L).median().shift(1).to_numpy()
    contr=(width<0.6*medw)&np.isfinite(medw)&np.isfinite(atr)&(atr>0)&(width>0)
    ent_idx=[]; ent_side=[]; ent_sl=[]; ent_rr=[]
    last_used=-10**9
    for t0 in np.where(np.nan_to_num(contr.astype(float),nan=0).astype(bool))[0]:
        if t0-last_used < L: continue           # don't re-arm inside a just-used coil
        ch=hh[t0]; clo=ll[t0]; cm=mid[t0]; wd=width[t0]
        end=min(t0+1+W, n-1)
        for j in range(t0+1, end):
            if c[j]>ch:                          # up-break -> long
                sl=abs(c[j]-cm);
                if sl>0: ent_idx.append(j); ent_side.append(1); ent_sl.append(sl); ent_rr.append(wd/sl); last_used=j
                break
            if c[j]<clo:                         # down-break -> short
                sl=abs(c[j]-cm)
                if sl>0: ent_idx.append(j); ent_side.append(-1); ent_sl.append(sl); ent_rr.append(wd/sl); last_used=j
                break
    return (np.array(ent_idx,int), np.array(ent_side,int), np.array(ent_sl,float), np.array(ent_rr,float))

def run(m, L, verbose=True):
    idx,side,sl,rrv=straddle_entries(m,L)
    if len(idx)==0:
        if verbose: print(f"L={L}: no entries");
        return np.array([]),np.array([]),np.array([])
    rrm=float(np.clip(np.median(rrv),0.5,3.0))
    Rs=[]; sides=[]; ents=[]
    for sd in (1,-1):
        p=side==sd
        if p.sum()==0: continue
        tr=sb.simulate(m,idx[p],sd,sl[p],rr=rrm,horizon=96,scenario="STRESS")
        te=tr["t_entry"].to_numpy(); cl=like_at(te); tr=tr[cl]
        Rs.append(tr["R"].to_numpy()); sides.append(np.full(len(tr),sd)); ents.append(tr["t_entry"].to_numpy())
    r=np.concatenate(Rs); sd=np.concatenate(sides); te=np.concatenate(ents)
    yr=pd.Series(pd.to_datetime(te,unit="s",utc=True)).dt.year.to_numpy()
    if not verbose: return r,yr,sd
    print(f"CR-11 two-sided vol-expansion L={L} (current-like, mid stop, measured-move rr={rrm:.2f}): N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f}")
    print(f"  long N={int((sd==1).sum())} avgR={r[sd==1].mean():+.4f} | short N={int((sd==-1).sum())} avgR={r[sd==-1].mean():+.4f}")
    print("  per-year:", {int(y):(round(float(r[yr==y].mean()),3),int((yr==y).sum())) for y in sorted(set(yr))})
    sr=np.sort(r); k10=max(1,len(r)//10)
    print(f"  best-1%-removed={sr[:-max(1,len(r)//100)].mean():+.4f}  best-10%-removed={sr[:-k10].mean():+.4f}")
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    print(f"  DISC<=2021 {d.mean():+.4f}(n{len(d)}) | CONF 22-24 {cf.mean():+.4f}(n{len(cf)}) | OOS 25+ {oos.mean():+.4f}(n{len(oos)})")
    both = (sd==1).sum()>=20 and (sd==-1).sum()>=20 and r[sd==1].mean()>0 and r[sd==-1].mean()>0
    surv = len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0 and both
    print(f"  -> {'SURVIVOR CANDIDATE (net>0, all partitions>0, tail-robust, BOTH sides>0)' if surv else 'NOT a survivor'}")
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
        print(f"  L={L} N={len(r)} avgR={r.mean():+.4f} best10%rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f} C {cf.mean():+.3f} O {oos.mean():+.3f} | L{r[sd==1].mean():+.3f} S{r[sd==-1].mean():+.3f}")

if __name__=="__main__":
    main()
