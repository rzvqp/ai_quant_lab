"""cur_cr13_verify.py — FULL SKEPTICISM GATE for the CR-13 H4-up-fade survivor candidate (current-like & H4-trend-up -> M15
short, 1.5ATR stop, rr2, STRESS). A survivor this clean after 12 negatives demands maximum scrutiny. Checks:
  (1) S5-INDEPENDENCE: entry hour-of-day histogram; fraction at NY open (13-14 UTC) and in the 12-16 window. S5 is a
      NY-open LONG; if these shorts are broadly distributed (not NY-open-timed) they are independent.
  (2) LEAVE-ONE-YEAR-OUT: does removing any single year flip avgR negative or the min-partition negative?
  (3) EPISODE CLUSTERING: how many DISTINCT contiguous H4-up episodes do the trades span (effective independent N)?
  (4) COST ROBUSTNESS: re-run at 2x STRESS round-turn cost.
  (5) DIAGNOSTIC: same short when NOT current-like (should be weaker if the regime label matters) and when H4-DOWN
      (the closed downtrend short — should be much worse, proving this is the DIVERGENCE not the trend).
Ratified sb.simulate. Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
from cur_screen import like_at
from cur_cr13_trade import h4_up_map

def entries(m, h4_state):  # h4_state: 0=up,1=down
    h4d=h4_up_map(m); atr=m["atr"].to_numpy(); n=len(m)
    ev=(h4d==h4_state)&np.isfinite(atr)&(atr>0)
    idx=np.where(np.nan_to_num(ev.astype(float),nan=0).astype(bool))[0]; idx=idx[idx<n-1]
    dd=sb.dedup_events(idx,16); p=np.isin(idx,dd); return idx[p], atr

def sim(m, idx, atr, cur=True, stress=1.0):
    sl=1.5*atr[idx]
    tr=sb.simulate(m,idx,-1,sl,rr=2.0,horizon=96,scenario="STRESS",cost_mult=stress) if _supports_costmult() else sb.simulate(m,idx,-1,sl,rr=2.0,horizon=96,scenario="STRESS")
    te=tr["t_entry"].to_numpy(); cl=like_at(te)
    tr=tr[cl] if cur else tr[~cl]
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    hh=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.hour.to_numpy()
    return r,yr,hh,tr["t_entry"].to_numpy()

def _supports_costmult():
    import inspect; return "cost_mult" in inspect.signature(sb.simulate).parameters

def main():
    m=CD.load_m15()
    idx,atr=entries(m,0)  # H4 up
    r,yr,hh,te=sim(m,idx,atr,cur=True)
    print(f"BASE (current-like & H4-up short): N={len(r)} avgR={r.mean():+.4f} WR={(r>0).mean():.3f}")
    # (1) S5-independence
    import collections; hist=collections.Counter((hh//2*2).tolist())
    print("  (1) entry hour (2h buckets):", {int(k):int(v) for k,v in sorted(hist.items())})
    print(f"      frac 13-14 UTC (NY open)={np.mean((hh>=13)&(hh<14)):.2f}  frac 12-16 UTC={np.mean((hh>=12)&(hh<16)):.2f}")
    # (2) leave-one-year-out
    ys=sorted(set(yr)); worst=None
    for y in ys:
        rr=r[yr!=y]; a=rr.mean()
        d=rr[pd.Series(yr[yr!=y]<=2021).to_numpy()] if False else None
        if worst is None or a<worst[1]: worst=(y,a)
    print(f"  (2) leave-one-year-out: worst-case avgR={worst[1]:+.4f} (dropping {int(worst[0])}); all-years avgR={r.mean():+.4f}")
    # partitions leave-one-out on the min partition
    def parts(mask):
        rr=r[mask]; return rr
    mins=[]
    for y in ys:
        keep=yr!=y; rk=r[keep]; yk=yr[keep]
        d=rk[yk<=2021].mean() if (yk<=2021).any() else 0; c=rk[(yk>=2022)&(yk<=2024)].mean() if ((yk>=2022)&(yk<=2024)).any() else 0; o=rk[yk>=2025].mean() if (yk>=2025).any() else 0
        mins.append(min(d,c,o))
    print(f"      worst min-partition over all year-drops={min(mins):+.4f} (stays>0 => partition-robust to year removal)")
    # (3) episode clustering
    order=np.argsort(idx); ids=idx[order]
    gaps=np.diff(ids); nep=1+int((gaps>16*4).sum())  # new episode if >4 H4 bars apart
    print(f"  (3) distinct H4-up episodes spanned (>4 H4-bar gap): {nep} (effective independent clusters)")
    # (4) cost robustness
    if _supports_costmult():
        r2,_,_,_=sim(m,idx,atr,cur=True,stress=2.0); print(f"  (4) 2x STRESS cost: avgR={r2.mean():+.4f}")
    else:
        print("  (4) cost_mult not supported by sb.simulate; STRESS already the adverse ratified scenario")
    # (5) diagnostics
    rn,_,_,_=sim(m,idx,atr,cur=False)
    idd,atd=entries(m,1); rd,ydd,_,_=sim(m,idd,atd,cur=True)
    print(f"  (5) DIAGNOSTIC same short NOT-current-like: avgR={rn.mean():+.4f} (N={len(rn)}) | H4-DOWN current-like (closed trend short): avgR={rd.mean():+.4f} (N={len(rd)})")
    print("      -> edge should be strong only in current-like & H4-UP (divergence), weak elsewhere.")

if __name__=="__main__":
    main()
