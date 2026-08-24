"""m5_f3.py — Frontier M5-3: same H1-down+M15-bounce SHORT setup, but M5 entry = PULLBACK-COMPLETION (M5 micro lower-high then
break of its micro-low = bounce failing) with a TIGHT M5-STRUCTURAL stop (just above the M5 micro-high). Targets M5-1's failure
(delayed momentum-break entry gave worse RR). Target = rr2 on the M5 stop. Full skepticism gate + §7 guard: if it 'wins' only via
tighter fitted stops it must still pass tail-removal + all-partitions + not be worse than a same-tightness ATR-stop control.
Causal via m5_data. 2021-2026 single-era (disclosed). Partitions DISC<=2023/CONF 2024/OOS 2025-26."""
import numpy as np, pandas as pd
import cur_data as CD, m5_data as M5D, swing_base as sb
Wtrig=24; H=288
def main():
    m5=M5D.load_m5(); H1=M5D.htf_at_m5(m5,"H1"); M15=M5D.htf_at_m5(m5,"M15")
    hi=m5["high"].to_numpy(); lo=m5["low"].to_numpy(); c5=m5["close"].to_numpy(); n=len(m5)
    h1dn=(H1["h1_ema20"].to_numpy()<H1["h1_ema50"].to_numpy())
    m15c=M15["m15_close"].to_numpy(); m15atr=M15["m15_atr"].to_numpy(); m15e20=M15["m15_ema20"].to_numpy()
    bounce=h1dn&(m15c>m15e20)&np.isfinite(m15atr)&(m15atr>0); setup=bounce&~np.r_[False,bounce[:-1]]
    m5hi6=pd.Series(hi).rolling(6).max().shift(1).to_numpy(); m5lo3=pd.Series(lo).rolling(3).min().shift(1).to_numpy()
    idx=[]; sl=[]; slw=[]
    for i in np.where(setup)[0]:
        if i>=n-2: continue
        a=m15atr[i]
        if not (np.isfinite(a) and a>0): continue
        end=min(i+1+Wtrig,n); tj=-1
        for j in range(i+1,end):
            # pullback-completion: micro lower-high present then break micro-low
            if np.isfinite(m5hi6[j]) and (hi[j]<m5hi6[j]) and np.isfinite(m5lo3[j]) and (c5[j]<m5lo3[j]): tj=j; break
        if tj<0 or tj>=n-1: continue
        stop=(m5hi6[tj]-c5[tj])  # M5-structural stop = micro-high above entry
        if stop<=0: continue
        idx.append(tj); sl.append(stop); slw.append(1.5*a)  # slw = wide ATR-stop control (same entry)
    idx=np.array(idx); sl=np.array(sl); slw=np.array(slw)
    def rep(sl_,label,rr=2.0):
        dd=sb.dedup_events(idx,Wtrig); p=np.isin(idx,dd); I=idx[p]; S=sl_[p]
        tr=sb.simulate(m5,I,-1,S,rr=rr,horizon=H,scenario="STRESS")
        r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
        sr=np.sort(r); k10=max(1,len(r)//10); d=r[yr<=2023]; cf=r[yr==2024]; o=r[yr>=2025]
        surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and o.mean()>0 and sr[:-k10].mean()>0
        print(f"  {label}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} medStop={np.median(S):.2f}USD best10rm={sr[:-k10].mean():+.4f} | DISC {d.mean():+.3f} CONF {cf.mean():+.3f} OOS {o.mean():+.3f} -> {'SURVIVOR' if surv else 'no'}")
    print(f"FRONTIER M5-3: pullback-completion entry + M5-structural stop. triggers={len(idx)}")
    rep(sl,"M5-structural-stop short ")
    rep(slw,"same-entry ATR-stop control")
    print("  §7 guard: M5-structural stop must beat the ATR-stop control AND pass tail/partition, else = tighter-fitting not info.")
if __name__=="__main__": main()
