"""cur_cr14.py — FRONTIER CR-14 (current-regime): CROSS-SCALE divergence LONG (complement of CRS-1). Motivated by the CRS-1
diagnostic: shorting WITH the H4 downtrend in current-like LOSES (-0.075) -> extended H4 down-legs don't reliably continue
-> the M15 LONG that fades an extended H4 down-leg may have a divergence edge. Genuinely new identity (opposite side, opposite
H4 state; NOT mining CRS-1, NOT generic reversion — it is H4-state-conditioned). If it survives the full skepticism gate the
current-regime portfolio becomes TWO-SIDED (CRS-1 short + CRS-2 long).

Activation: current-like AND known(causal) H4-trend DOWN (ema20<ema50). Side LONG. 1.5ATR stop, rr2, H96, STRESS, dedup16.
Full gate: per-year, partition (DISC/CONF/OOS all>0), best-10%-removed tail, neighbor (stop,rr), entry-timing (dedup), and
regime/mechanism diagnostics. Ratified sb.simulate. Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
from cur_screen import like_at
from cur_cr13_trade import h4_up_map

def entries(m):
    h4d=h4_up_map(m); atr=m["atr"].to_numpy(); n=len(m)
    ev=(h4d==1)&np.isfinite(atr)&(atr>0)   # H4 DOWN
    idx=np.where(np.nan_to_num(ev.astype(float),nan=0).astype(bool))[0]; idx=idx[idx<n-1]
    return idx, atr

def run(m, stopmult, rr, sp=16, verbose=True):
    idx,atr=entries(m); dd=sb.dedup_events(idx,sp); idx=idx[np.isin(idx,dd)]; sl=stopmult*atr[idx]
    tr=sb.simulate(m,idx,1,sl,rr=rr,horizon=96,scenario="STRESS")   # LONG
    te=tr["t_entry"].to_numpy(); cl=like_at(te); tr=tr[cl]
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    if not verbose: return r,yr
    print(f"CR-14 H4-down-fade LONG (current-like, {stopmult}ATR stop, rr{rr}): N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f}")
    print("  per-year:", {int(y):(round(float(r[yr==y].mean()),2),int((yr==y).sum())) for y in sorted(set(yr))})
    sr=np.sort(r); k10=max(1,len(r)//10)
    print(f"  best-1%-removed={sr[:-max(1,len(r)//100)].mean():+.4f}  best-10%-removed={sr[:-k10].mean():+.4f}")
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    print(f"  DISC<=2021 {d.mean():+.4f}(n{len(d)}) | CONF 22-24 {cf.mean():+.4f}(n{len(cf)}) | OOS 25+ {oos.mean():+.4f}(n{len(oos)})")
    surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0
    print(f"  -> {'SURVIVOR CANDIDATE' if surv else 'NOT a survivor'}")
    return r,yr

def main():
    m=CD.load_m15()
    print("=== PRIMARY: 1.5ATR stop, rr2 ===")
    run(m,1.5,2.0)
    print("\n=== NEIGHBORS (stop,rr) and entry-timing ===")
    for sm,rr in [(1.5,1.0),(2.0,2.0),(1.0,3.0)]:
        r,yr=run(m,sm,rr,verbose=False); sr=np.sort(r); k10=max(1,len(r)//10)
        d=r[yr<=2021].mean(); c=r[(yr>=2022)&(yr<=2024)].mean(); o=r[yr>=2025].mean()
        print(f"  stop{sm} rr{rr}: N={len(r)} avgR={r.mean():+.4f} best10%rm={sr[:-k10].mean():+.4f} | D {d:+.3f} C {c:+.3f} O {o:+.3f}")
    for sp in (8,24,32):
        r,yr=run(m,1.5,2.0,sp=sp,verbose=False); sr=np.sort(r); k10=max(1,len(r)//10)
        d=r[yr<=2021].mean(); c=r[(yr>=2022)&(yr<=2024)].mean(); o=r[yr>=2025].mean()
        print(f"  dedup{sp}: N={len(r)} avgR={r.mean():+.4f} best10%rm={sr[:-k10].mean():+.4f} | D {d:+.3f} C {c:+.3f} O {o:+.3f}")

if __name__=="__main__":
    main()
