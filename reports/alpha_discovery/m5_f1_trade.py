"""m5_f1_trade.py — Frontier M5-1 tradeable (§7 ablation): BASE (M15-setup short) vs M5-COND (M5 down-break short), SAME
structural bracket (1.5*M15-ATR stop, rr2, 288 M5-bar horizon, STRESS). M5 must incrementally improve avgR AND M5-COND must
be a positive tradeable edge (not just less-bad). Higher-TF-setup ablation = BASE; M5-condition ablation = compare. Coverage
2021-2026 single macro-era (disclosed); partitions DISC<=2023/CONF 2024/OOS 2025-26. Causal alignment via m5_data."""
import numpy as np, pandas as pd
import cur_data as CD, m5_data as M5D, swing_base as sb
Wtrig=24; H=288
def events(m5):
    H1=M5D.htf_at_m5(m5,"H1"); M15=M5D.htf_at_m5(m5,"M15")
    c5=m5["close"].to_numpy(); lo=m5["low"].to_numpy(); n=len(m5)
    h1dn=(H1["h1_ema20"].to_numpy()<H1["h1_ema50"].to_numpy())
    m15c=M15["m15_close"].to_numpy(); m15atr=M15["m15_atr"].to_numpy(); m15e20=M15["m15_ema20"].to_numpy()
    bounce=h1dn&(m15c>m15e20)&np.isfinite(m15atr)&(m15atr>0)
    setup=bounce&~np.r_[False,bounce[:-1]]
    m5low6=pd.Series(lo).rolling(6).min().shift(1).to_numpy(); m5break=(c5<m5low6)
    base_i=[]; base_sl=[]; cond_i=[]; cond_sl=[]
    for i in np.where(setup)[0]:
        if i>=n-2: continue
        a=m15atr[i]
        if not (np.isfinite(a) and a>0): continue
        base_i.append(i); base_sl.append(1.5*a)
        end=min(i+1+Wtrig,n); tj=-1
        for j in range(i+1,end):
            if m5break[j]: tj=j; break
        if tj>=0 and tj<n-1: cond_i.append(tj); cond_sl.append(1.5*a)
    return (np.array(base_i),np.array(base_sl)),(np.array(cond_i),np.array(cond_sl))
def rep(m5, idx, sl, label):
    dd=sb.dedup_events(idx,Wtrig); p=np.isin(idx,dd); idx=idx[p]; sl=sl[p]
    tr=sb.simulate(m5,idx,-1,sl,rr=2.0,horizon=H,scenario="STRESS")
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    sr=np.sort(r); k10=max(1,len(r)//10); d=r[yr<=2023]; cf=r[yr==2024]; o=r[yr>=2025]
    surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and o.mean()>0 and sr[:-k10].mean()>0
    print(f"  {label}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} best10rm={sr[:-k10].mean():+.4f} | DISC {d.mean():+.3f}(n{len(d)}) CONF {cf.mean():+.3f}(n{len(cf)}) OOS {o.mean():+.3f}(n{len(o)}) -> {'SURVIVOR' if surv else 'no'}")
    return r.mean()
def main():
    m5=M5D.load_m5(); (bi,bs),(ci,cs)=events(m5)
    print(f"FRONTIER M5-1 tradeable (structural 1.5ATR/rr2, STRESS). BASE setups={len(bi)} M5-COND={len(ci)}")
    b=rep(m5,bi,bs,"BASE (M15-setup short)   ")
    c=rep(m5,ci,cs,"M5-COND (M5-trigger short)")
    print(f"  incremental M5 value: avgR {b:+.4f} -> {c:+.4f} (delta {c-b:+.4f})")
if __name__=="__main__": main()
