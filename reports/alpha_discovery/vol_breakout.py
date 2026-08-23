"""vol_breakout.py — resumption discovery (verified causal infra): VOLUME-FILTERED structural breakout. Synthesizes the only
working edge class (breakout structure, cf. S5) with the causally-validated VOL-1 finding (volume ranks continuation quality,
high>low). Hypothesis: a breakout of a prior N-bar extreme WITH high tick-volume = real participation -> continuation; with low
volume = fakeout. Distinct from S5 (any-time, not NY-session) and from VOL-1 (structural-level breakout, not a raw big bar).
Causal: prior extreme = rolling max/min over [t-N..t-1]; vol_z = volume/TRAILING rolling-median(volume,V).shift(1). Full gate +
low-vol control + S5-redundancy hour-histogram. STRESS, 1.5ATR, rr2. No like_at (pure OHLCV). Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
N=20; V=50

def run(m, idx, side, atr, label, verbose=True):
    n=len(m); idx=idx[idx<n-1]; dd=sb.dedup_events(idx,8); idx=idx[np.isin(idx,dd)]; sl=1.5*atr[idx]
    tr=sb.simulate(m,idx,side,sl,rr=2.0,horizon=96,scenario="STRESS")
    r=tr["R"].to_numpy(); te=tr["t_entry"].to_numpy(); yr=pd.Series(pd.to_datetime(te,unit="s",utc=True)).dt.year.to_numpy()
    if not verbose: return r,yr,te
    if len(r)<40: print(f"  {label}: N={len(r)} thin"); return r,yr,te
    sr=np.sort(r); k1=max(1,len(r)//100); k10=max(1,len(r)//10)
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]; negyr=sum(1 for y in set(yr) if r[yr==y].mean()<0)
    surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0
    print(f"  {label}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} best1rm={sr[:-k1].mean():+.4f} best10rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f} C {cf.mean():+.3f} O {oos.mean():+.3f} negyr{negyr}/{len(set(yr))} -> {'SURVIVOR' if surv else 'no'}")
    return r,yr,te

def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); vol=m["volume"].to_numpy()
    ph=pd.Series(h).rolling(N).max().shift(1).to_numpy(); pl=pd.Series(l).rolling(N).min().shift(1).to_numpy()
    vz=vol/pd.Series(vol).rolling(V).median().shift(1).to_numpy()
    ok=np.isfinite(atr)&(atr>0)&np.isfinite(vz)
    bo_up=ok&(c>ph); bo_dn=ok&(c<pl); hv=vz>=1.5; lv=vz<=0.8
    print(f"VOL-BREAKOUT. up-breakouts={int(bo_up.sum())} (hv {int((bo_up&hv).sum())}) dn-breakouts={int(bo_dn.sum())} (hv {int((bo_dn&hv).sum())})")
    r,yr,te=run(m, np.where(bo_up&hv)[0], 1, atr, "HIGH-vol UP-breakout LONG ")
    run(m, np.where(bo_dn&hv)[0], -1, atr, "HIGH-vol DN-breakout SHORT")
    print("  controls (low-vol breakout, should be worse if volume filters):")
    run(m, np.where(bo_up&lv)[0], 1, atr, "LOW-vol  UP-breakout LONG ")
    run(m, np.where(bo_dn&lv)[0], -1, atr, "LOW-vol  DN-breakout SHORT")
    # S5-redundancy: entry-hour histogram of the high-vol up-breakout (S5 = NY open 13-14 UTC)
    if len(te)>40:
        hh=pd.Series(pd.to_datetime(te,unit="s",utc=True)).dt.hour.to_numpy()
        print(f"  S5-redundancy (HV up-breakout hours): frac 13-14 UTC={np.mean((hh>=13)&(hh<14)):.2f} frac 12-16={np.mean((hh>=12)&(hh<16)):.2f}")

if __name__=="__main__":
    main()
