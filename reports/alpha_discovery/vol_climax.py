"""vol_climax.py — resumption discovery: VOLUME-CLIMAX exhaustion (genuinely-new; distinct from vol-displacement/continuation
and vol-breakout). Hypothesis: an extreme tick-volume SPIKE (vz>=SP) at a fresh local extreme = climactic exhaustion -> reversal.
climax-high -> SHORT, climax-low -> LONG. Causal (vz = volume/trailing-median.shift(1); extreme = rolling max/min over prior N).
Full gate. STRESS, 1.5ATR, rr2. No like_at. Data through 2026-07-27."""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
N=20; V=50; SP=3.0
def run(m, idx, side, atr, label):
    n=len(m); idx=idx[idx<n-1]
    if len(idx)<40: print(f"  {label}: N={len(idx)} thin"); return
    dd=sb.dedup_events(idx,8); idx=idx[np.isin(idx,dd)]; sl=1.5*atr[idx]
    tr=sb.simulate(m,idx,side,sl,rr=2.0,horizon=96,scenario="STRESS"); r=tr["R"].to_numpy()
    yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    if len(r)<40: print(f"  {label}: N={len(r)} thin"); return
    sr=np.sort(r); k1=max(1,len(r)//100); k10=max(1,len(r)//10)
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; o=r[yr>=2025]; ny=sum(1 for y in set(yr) if r[yr==y].mean()<0)
    sv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and o.mean()>0 and sr[:-k10].mean()>0
    print(f"  {label}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} best1rm={sr[:-k1].mean():+.4f} best10rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f} C {cf.mean():+.3f} O {o.mean():+.3f} negyr{ny}/{len(set(yr))} -> {'SURVIVOR' if sv else 'no'}")
def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); atr=m["atr"].to_numpy(); vol=m["volume"].to_numpy()
    vz=vol/pd.Series(vol).rolling(V).median().shift(1).to_numpy()
    ph=pd.Series(h).rolling(N).max().shift(1).to_numpy(); pl=pd.Series(l).rolling(N).min().shift(1).to_numpy()
    ok=np.isfinite(atr)&(atr>0)&np.isfinite(vz)
    climax_hi=ok&(vz>=SP)&(h>ph); climax_lo=ok&(vz>=SP)&(l<pl)
    print(f"VOL-CLIMAX exhaustion (vz>={SP} at extreme). climax-hi={int(climax_hi.sum())} climax-lo={int(climax_lo.sum())}")
    run(m, np.where(climax_hi)[0], -1, atr, "climax-HI -> SHORT(revert)")
    run(m, np.where(climax_lo)[0], 1, atr, "climax-LO -> LONG (revert)")
    print("  continuation control (climax = continuation not exhaustion):")
    run(m, np.where(climax_hi)[0], 1, atr, "climax-HI -> LONG (continue)")
    run(m, np.where(climax_lo)[0], -1, atr, "climax-LO -> SHORT(continue)")
if __name__=="__main__": main()
