"""cur_cr9.py — FRONTIER CR-9 (current-regime): RANGE-MIGRATION / coil-breakdown with STRUCTURAL stop. NEW representation
class (the ordering route is closed with a quantified bound; every ATR-symmetric bracket inherits the coinflip). Here the
geometry is different: enter on a breakdown from a CONTRACTION COIL, stop at the RANGE HIGH (structural invalidation, not
ATR), target a MEASURED MOVE (one coil-height down). New causal elements vs closed frontiers: (1) a vol/range-CONTRACTION
precondition (coil tighter than recent norm) -> distinct from raw short-breakdown and from CR-3 expansion-onset; (2) a
STRUCTURAL stop tied to a real level, so wins/losses are NOT governed by the +/-1.5ATR ordering coinflip. Hypothesis: in a
down-correction, coils resolve downward and migrate to a lower range -> structural edge not confined to the tail.

Preregistered before scoring. Full skepticism gate: per-year, partition (DISC/CONF/OOS all>0), best-10%-removed tail test,
neighbor stability across coil length L in {18,24,32}. Survivor only if net>0 AND all partitions>0 AND tail-robust AND
stable. Ratified sb.simulate, STRESS. Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
from cur_screen import like_at

def coil_breakdown(m, L):
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    hh=pd.Series(h).rolling(L).max().shift(1).to_numpy()   # range high over prior L bars (causal)
    ll=pd.Series(l).rolling(L).min().shift(1).to_numpy()   # range low over prior L bars
    width=hh-ll
    medw=pd.Series(width).rolling(8*L).median().shift(1).to_numpy()  # recent typical width
    contraction=(width < 0.6*medw)                          # coil tighter than recent norm
    brk=(c<ll)                                              # closes below the coil low = breakdown
    ev=contraction & brk & np.isfinite(hh) & (hh>c) & np.isfinite(atr) & (atr>0)
    idx=np.where(np.nan_to_num(ev.astype(float),nan=0).astype(bool))[0]; idx=idx[idx<n-1]
    sl=hh[idx]-c[idx]                                       # STRUCTURAL stop = distance to range high
    wd=width[idx]                                           # coil height (measured move)
    return idx, sl, wd

def run(m, L, verbose=True):
    idx,sl,wd=coil_breakdown(m,L)
    dd=sb.dedup_events(idx,L); p=np.isin(idx,dd); idx=idx[p]; sl=sl[p]; wd=wd[p]
    rr=np.clip(wd/np.maximum(sl,1e-9),0.5,3.0)              # measured-move target as R multiple of the structural stop
    # sb.simulate takes scalar rr; approximate with the median rr (report it) — structural stop already encodes geometry
    rrm=float(np.median(rr))
    tr=sb.simulate(m,idx,-1,sl,rr=rrm,horizon=96,scenario="STRESS")
    te=tr["t_entry"].to_numpy(); cl=like_at(te); tr=tr[cl]
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    if not verbose: return r,yr
    print(f"CR-9 coil-breakdown-short L={L} (current-like, structural stop, measured-move rr={rrm:.2f}): N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f}")
    print("  per-year:", {int(y):(round(float(r[yr==y].mean()),3),int((yr==y).sum())) for y in sorted(set(yr))})
    sr=np.sort(r); k10=max(1,len(r)//10)
    print(f"  best-1%-removed={sr[:-max(1,len(r)//100)].mean():+.4f}  best-10%-removed={sr[:-k10].mean():+.4f}")
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    print(f"  DISC<=2021 {d.mean():+.4f}(n{len(d)}) | CONF 22-24 {cf.mean():+.4f}(n{len(cf)}) | OOS 25+ {oos.mean():+.4f}(n{len(oos)})")
    surv = len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0
    print(f"  -> {'SURVIVOR CANDIDATE (net>0, all partitions>0, tail-robust)' if surv else 'NOT a survivor'}")
    return r,yr

def main():
    m=CD.load_m15()
    print("=== PRIMARY: coil length L=24 (6h) ===")
    run(m,24)
    print("\n=== NEIGHBOR STABILITY (skepticism): L=18 and L=32 ===")
    for L in (18,32):
        r,yr=run(m,L,verbose=False)
        sr=np.sort(r); k10=max(1,len(r)//10); d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
        print(f"  L={L} N={len(r)} avgR={r.mean():+.4f} best10%rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f} C {cf.mean():+.3f} O {oos.mean():+.3f}")

if __name__=="__main__":
    main()
