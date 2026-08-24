"""cur_cr15.py — FRONTIER CR-15 (current-regime): extend the CRS-1 cross-scale-divergence-SHORT principle to the M15xH1
scale pair, and decompose for REDUNDANCY vs CRS-1 (H4) — the §30 discipline that killed Batch D. M15 short when known(causal)
H1-trend is UP, in current-like. Decomposition:
  - H1-up & H4-up   = SAME episode as CRS-1 (redundant confirmation).
  - H1-up & H4-DOWN = a FASTER divergence (H1 bounces while H4 still down) -> genuinely INDEPENDENT of CRS-1.
If the INDEPENDENT subset (H1-up & H4-down short) survives the gate AND is material -> a second edge (CRS-2 / divergence
family, more opportunities). If negative/thin -> CRS-1 captures the divergence singularly. Full gate on each subset.
1.5ATR stop, rr2, H96, STRESS, dedup16. Ratified sb.simulate. Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
from cur_screen import like_at
from cur_cr13_trade import h4_up_map

def h1_up_map(m):
    h1=CD.agg(m,"H1"); td=(h1["ema20"].to_numpy()<h1["ema50"].to_numpy())
    hm=pd.DataFrame({"close_time":h1["close_time"].to_numpy(),"h1_down":td.astype(int)}).sort_values("close_time")
    mm=pd.DataFrame({"time":m["time"].to_numpy()}).sort_values("time")
    j=pd.merge_asof(mm,hm,left_on="time",right_on="close_time",direction="backward").sort_index()
    return j["h1_down"].to_numpy()

def gate(name, m, mask):
    atr=m["atr"].to_numpy(); n=len(m)
    idx=np.where(mask&np.isfinite(atr)&(atr>0))[0]; idx=idx[idx<n-1]
    if len(idx)<40: print(f"  {name}: n={len(idx)} (thin)"); return
    dd=sb.dedup_events(idx,16); idx=idx[np.isin(idx,dd)]; sl=1.5*atr[idx]
    tr=sb.simulate(m,idx,-1,sl,rr=2.0,horizon=96,scenario="STRESS")
    te=tr["t_entry"].to_numpy(); cl=like_at(te); tr=tr[cl]
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    sr=np.sort(r); k10=max(1,len(r)//10)
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    surv=len(r)>=60 and len(d)>0 and len(cf)>0 and len(oos)>0 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0
    print(f"  {name}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} best10%rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f}(n{len(d)}) C {cf.mean():+.3f}(n{len(cf)}) O {oos.mean():+.3f}(n{len(oos)}) -> {'SURVIVOR' if surv else 'no'}")

def main():
    m=CD.load_m15(); h1d=h1_up_map(m); h4d=h4_up_map(m)
    print("FRONTIER CR-15: M15xH1 cross-scale divergence short + redundancy decomposition vs CRS-1 (H4).")
    gate("H1-up ALL (M15xH1 short)      ", m, (h1d==0))
    gate("H1-up & H4-up  (=CRS-1 episode)", m, (h1d==0)&(h4d==0))
    gate("H1-up & H4-DOWN (INDEPENDENT)  ", m, (h1d==0)&(h4d==1))
    print("  (independent subset survivor+material => CRS-2 divergence family; else CRS-1 captures it singularly)")

if __name__=="__main__":
    main()
