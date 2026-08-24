"""cur_cr13_trade.py — tradeable + MANDATORY SKEPTICISM GATE for CR-13's one positive info signal: within current-like, when
the known (causal) H4 trend is UP (a counter-trend bounce inside the down-correction), M15 down-first ordering = 0.600 and
dn-up excursion = +2.25 — the ONLY tested condition to clear the ~0.54 ordering ceiling. Economic reading: fade the
counter-trend bounce. SKEPTICAL PRIOR: 'H4-up inside a high-vol down-correction' may select the bounces right before crash
resumption -> the +2.25 excursion could be crash-TAIL-concentrated. Decisive test = best-1%/best-10%-removed tail gate +
partition robustness (DISC/CONF/OOS all>0) + per-year + neighbor stability across stop/rr.

Entry: M15 bars in current-like with H4 known-trend UP, deduped ~1 per H4 bar (16 M15 bars), SHORT, 1.5ATR stop, rr2 primary
(matches the large excursion). Ratified sb.simulate, STRESS. Survivor only if net>0 AND all partitions>0 AND best-10%-removed>0.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
from cur_screen import like_at

def h4_up_map(m):
    h4=CD.agg(m,"H4"); td=(h4["ema20"].to_numpy()<h4["ema50"].to_numpy())
    h4map=pd.DataFrame({"close_time":h4["close_time"].to_numpy(),"h4_down":td.astype(int)}).sort_values("close_time")
    mm=pd.DataFrame({"time":m["time"].to_numpy()}).sort_values("time")
    j=pd.merge_asof(mm,h4map,left_on="time",right_on="close_time",direction="backward").sort_index()
    return j["h4_down"].to_numpy()

def run(m, stopmult, rr, verbose=True):
    h4d=h4_up_map(m); atr=m["atr"].to_numpy(); n=len(m)
    ev=(h4d==0)&np.isfinite(atr)&(atr>0)
    idx=np.where(np.nan_to_num(ev.astype(float),nan=0).astype(bool))[0]; idx=idx[idx<n-1]
    dd=sb.dedup_events(idx,16); p=np.isin(idx,dd); idx=idx[p]; sl=stopmult*atr[idx]
    tr=sb.simulate(m,idx,-1,sl,rr=rr,horizon=96,scenario="STRESS")
    te=tr["t_entry"].to_numpy(); cl=like_at(te); tr=tr[cl]
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    if not verbose: return r,yr
    print(f"CR-13 H4-up-fade short (current-like, {stopmult}ATR stop, rr{rr}): N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f}")
    print("  per-year:", {int(y):(round(float(r[yr==y].mean()),2),int((yr==y).sum())) for y in sorted(set(yr))})
    sr=np.sort(r); k1=max(1,len(r)//100); k10=max(1,len(r)//10)
    print(f"  best-1%-removed={sr[:-k1].mean():+.4f}  best-10%-removed={sr[:-k10].mean():+.4f}")
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    print(f"  DISC<=2021 {d.mean():+.4f}(n{len(d)}) | CONF 22-24 {cf.mean():+.4f}(n{len(cf)}) | OOS 25+ {oos.mean():+.4f}(n{len(oos)})")
    surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0
    print(f"  -> {'SURVIVOR CANDIDATE (net>0, all partitions>0, tail-robust best-10%-removed>0)' if surv else 'NOT a survivor'}")
    return r,yr

def main():
    m=CD.load_m15()
    print("=== PRIMARY: 1.5ATR stop, rr2 ===")
    run(m,1.5,2.0)
    print("\n=== NEIGHBOR STABILITY (skepticism): (stop,rr) in {(1.5,1),(2.0,2),(1.0,3)} ===")
    for sm,rr in [(1.5,1.0),(2.0,2.0),(1.0,3.0)]:
        r,yr=run(m,sm,rr,verbose=False)
        sr=np.sort(r); k10=max(1,len(r)//10); d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
        print(f"  stop{sm} rr{rr}: N={len(r)} avgR={r.mean():+.4f} best10%rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f} C {cf.mean():+.3f} O {oos.mean():+.3f}")

if __name__=="__main__":
    main()
