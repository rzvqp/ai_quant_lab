"""cur_cr3_trade.py — tradeable + skepticism test of CR-3: does entering the wide-stop short at the VOL-EXPANSION-DOWN
ignition (which concentrates the down-PAYOFF, dn-up +0.95) make the down-capture NON-tail-dependent, unlike the rejected
regime-short? Wide 4ATR stop (survive bounces), rr3, H96, STRESS, current-like. Reports per-year + best-10%-removed
(the tail test that rejected the prior short) + partition. Survivor only if robust AND best-10%-removed positive.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
from cur_screen import like_at

def sig(m):
    o=m["open"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); vr=(m["atr"]/m["atr_ma"]).to_numpy(); n=len(m)
    ev=(vr>1.0)&(pd.Series(vr).shift(1).to_numpy()<=1.0)&(c<o)&np.isfinite(atr)&(atr>0)
    idx=np.where(np.nan_to_num(ev.astype(float),nan=0).astype(bool))[0]; idx=idx[idx<n-1]; sl=4.0*atr[idx]
    return idx, sl

def main():
    m=CD.load_m15(); idx,sl=sig(m)
    o=np.argsort(idx); idx=idx[o]; sl=sl[o]; dd=sb.dedup_events(idx,12); p=np.isin(idx,dd); idx=idx[p]; sl=sl[p]
    tr=sb.simulate(m,idx,-1,sl,rr=3.0,horizon=96,scenario="STRESS")
    te=tr["t_entry"].to_numpy(); cl=like_at(te); tr=tr[cl]
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    print(f"CR-3 VOLEXP-DN wide-short (current-like): N={len(r)} avgR={r.mean():+.3f} PF={sb._pf(r):.2f} WR={(r>0).mean():.2f}")
    print("  per-year:", {int(y):(round(float(r[yr==y].mean()),3),int((yr==y).sum())) for y in sorted(set(yr))})
    sr=np.sort(r); k10=max(1,len(r)//10)
    print(f"  best-1%-removed={sr[:-max(1,len(r)//100)].mean():+.3f}  best-10%-removed={sr[:-k10].mean():+.3f}")
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    print(f"  DISC<=2021 {d.mean():+.3f}(n{len(d)}) | CONF 22-24 {cf.mean():+.3f}(n{len(cf)}) | OOS 25+ {oos.mean():+.3f}(n{len(oos)})")
    surv = len(d)>=25 and len(cf)>=25 and d.mean()>0 and cf.mean()>0 and sr[:-k10].mean()>0
    print(f"  -> {'CURRENT_REGIME_SURVIVOR (passes tail test)' if surv else 'NOT a survivor (tail-dependent or partition-negative)'}")

if __name__=="__main__":
    main()
