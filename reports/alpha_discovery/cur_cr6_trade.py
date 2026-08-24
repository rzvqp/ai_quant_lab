"""cur_cr6_trade.py — tradeable + MANDATORY SKEPTICISM GATE for CR-6's robust intraday ordering finding.

CR-6 info result: in current-like, the 12-16 UTC (US macro) window has P(down 1.5ATR before up 1.5ATR) = 0.541 robust
across ALL partitions (DISC 0.53 / CONF 0.55 / OOS 0.59, strengthening). This is a PATH-ORDERING edge, not a payoff-tail
edge. A SYMMETRIC bracket (stop 1.5ATR, target 1.5ATR = rr1) realizes exactly this ordering as win/loss -> bounded wins
and losses -> NON-tail-dependent BY CONSTRUCTION. Test whether it survives realistic costs + the full skepticism gate.

Design: ONE short per current-like day at the 12:00 UTC bar (independent obs, no intra-window overlap), 1.5ATR stop, rr1,
H96, STRESS (ratified sb.simulate). Skepticism gate: per-year concentration, best-1%/best-10%-removed tail test,
partition robustness (DISC & CONF & OOS all > 0), S5-independence (S5 is a LONG NY-open breakout; this is a session short),
and neighbor stability across entry hours 12/13/14 UTC. Survivor only if net>0 AND all partitions>0 AND tail-robust.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
from cur_screen import like_at

def entries_at_hour(m, H):
    hr=m["dt"].dt.hour.to_numpy(); mn=m["dt"].dt.minute.to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    ev=(hr==H)&(mn==0)&np.isfinite(atr)&(atr>0)
    idx=np.where(ev)[0]; idx=idx[idx<n-1]; return idx

def run(m, H, verbose=True):
    idx=entries_at_hour(m,H); atr=m["atr"].to_numpy(); sl=1.5*atr[idx]
    tr=sb.simulate(m,idx,-1,sl,rr=1.0,horizon=96,scenario="STRESS")
    te=tr["t_entry"].to_numpy(); cl=like_at(te); tr=tr[cl]
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    if not verbose: return r,yr
    print(f"CR-6 session-short @ {H:02d}:00 UTC (current-like, 1.5ATR sym bracket rr1): N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f}")
    print("  per-year:", {int(y):(round(float(r[yr==y].mean()),3),int((yr==y).sum())) for y in sorted(set(yr))})
    sr=np.sort(r); k1=max(1,len(r)//100); k10=max(1,len(r)//10)
    print(f"  best-1%-removed={sr[:-k1].mean():+.4f}  best-10%-removed={sr[:-k10].mean():+.4f}")
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    print(f"  DISC<=2021 {d.mean():+.4f}(n{len(d)}) | CONF 22-24 {cf.mean():+.4f}(n{len(cf)}) | OOS 25+ {oos.mean():+.4f}(n{len(oos)})")
    surv = len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0
    print(f"  -> {'SURVIVOR CANDIDATE (net>0, all partitions>0, tail-robust)' if surv else 'NOT a survivor'}")
    return r,yr

def main():
    m=CD.load_m15()
    print("=== PRIMARY: entry 12:00 UTC ===")
    run(m,12)
    print("\n=== NEIGHBOR STABILITY (skepticism): same short at 13:00 and 14:00 UTC ===")
    for H in (13,14):
        r,yr=run(m,H,verbose=False)
        sr=np.sort(r); k10=max(1,len(r)//10)
        d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
        print(f"  @{H}:00 N={len(r)} avgR={r.mean():+.4f} best10%rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f} C {cf.mean():+.3f} O {oos.mean():+.3f}")

if __name__=="__main__":
    main()
