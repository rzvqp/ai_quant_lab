"""gap_behavior.py — resumption discovery (post causal-repair, verified infra): GAP behavior, a genuinely-new mechanism
(untested in this campaign; distinct from S5 breakout). At a bar whose OPEN gaps from the prior bar's CLOSE by >=G*ATR
(session/weekend gap), does price FILL the gap (revert to prior close) or CONTINUE in the gap direction? Test both hypotheses
both directions. Causal (uses only the gap bar's open + prior close, both known at bar open). Full gate: DISC/CONF/OOS, tail,
per-year. STRESS. No like_at anywhere (pure OHLC). Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
G=0.5

def run(m, idx, side, atr, label):
    n=len(m); idx=idx[idx<n-1]
    if len(idx)<40: print(f"  {label}: N={len(idx)} thin"); return
    dd=sb.dedup_events(idx,4); idx=idx[np.isin(idx,dd)]; sl=1.5*atr[idx]
    tr=sb.simulate(m,idx,side,sl,rr=2.0,horizon=96,scenario="STRESS")
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    if len(r)<40: print(f"  {label}: N={len(r)} thin"); return
    sr=np.sort(r); k1=max(1,len(r)//100); k10=max(1,len(r)//10)
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]; negyr=sum(1 for y in set(yr) if r[yr==y].mean()<0)
    surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0
    print(f"  {label}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} best1rm={sr[:-k1].mean():+.4f} best10rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f} C {cf.mean():+.3f} O {oos.mean():+.3f} negyr{negyr}/{len(set(yr))} -> {'SURVIVOR' if surv else 'no'}")

def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy()
    pc=pd.Series(c).shift(1).to_numpy(); gap=(o-pc)/atr; ok=np.isfinite(gap)&np.isfinite(atr)&(atr>0)
    gap_up=ok&(gap>=G); gap_dn=ok&(gap<=-G)
    # gap size in minutes-between-bars (detect session/weekend gaps vs normal)
    dt=m["time"].to_numpy(); dbar=dt-pd.Series(dt).shift(1).to_numpy()
    print(f"GAP behavior. gap-up(>= {G}ATR)={int(gap_up.sum())} gap-dn={int(gap_dn.sum())} | median bar-gap={np.nanmedian(dbar):.0f}s, >900s bars={int((dbar>900).sum())}")
    print("  CONTINUATION hypothesis (go WITH gap):")
    run(m, np.where(gap_up)[0], 1, atr, "gap-UP  -> LONG (continue) ")
    run(m, np.where(gap_dn)[0], -1, atr, "gap-DN  -> SHORT(continue) ")
    print("  FILL hypothesis (fade the gap):")
    run(m, np.where(gap_up)[0], -1, atr, "gap-UP  -> SHORT(fill)     ")
    run(m, np.where(gap_dn)[0], 1, atr, "gap-DN  -> LONG (fill)     ")
    # weekend/session gaps only (bar spacing > 900s)
    wk=ok&(dbar>900)
    print("  SESSION/WEEKEND gaps only (bar-gap>900s):")
    run(m, np.where(gap_up&wk)[0], -1, atr, "wknd gap-UP -> SHORT(fill) ")
    run(m, np.where(gap_dn&wk)[0], 1, atr, "wknd gap-DN -> LONG (fill) ")

if __name__=="__main__":
    main()
