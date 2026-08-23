"""m5_f2.py — Frontier M5-2 (info-first, CAUSAL/no-circularity fix). M15 breakout (close above prior-20-M15-bar high). M5
ACCEPTANCE = price holds above the broken level for Wr=24 M5 bars. CRITICAL FIX: entry/outcome measured strictly AFTER the
acceptance window (from bar i+Wr), NOT from the breakout bar i — the previous version overlapped the acceptance window with the
outcome window (circular, gave a spurious 0.93). BASE = enter at breakout bar i, outcome forward from i. M5-ACCEPTED = enter at
i+Wr (only breakouts that held), outcome forward from i+Wr. Barriers +/-1.5*M15-ATR. Causal via m5_data. 2021-2026 disclosed."""
import numpy as np, pandas as pd
import cur_data as CD, m5_data as M5D
Wr=24; H=288
def fwd_up1st(hi,lo,i,p,a,H,n):
    up=p+1.5*a; dn=p-1.5*a; end=min(i+1+H,n)
    for j in range(i+1,end):
        hu=hi[j]>=up; hd=lo[j]<=dn
        if hu and hd: return 0
        if hu: return 1
        if hd: return 0
    return -9
def main():
    m5=M5D.load_m5(); M15=M5D.htf_at_m5(m5,"M15")
    hi=m5["high"].to_numpy(); lo=m5["low"].to_numpy(); c5=m5["close"].to_numpy(); n=len(m5)
    m15atr=M15["m15_atr"].to_numpy()
    m15=CD.load_m15(); ph=pd.Series(m15["high"].to_numpy()).rolling(20).max().shift(1)
    m15f=m15[["time"]].copy(); m15f["ph"]=ph.to_numpy()
    j=pd.merge_asof(pd.DataFrame({"time":m5["time"].to_numpy()}).sort_values("time"),
                    m15f.sort_values("time").rename(columns={"time":"m15t"}),
                    left_on="time",right_on="m15t",direction="backward").sort_index()
    PH=j["ph"].to_numpy()
    brk=(c5>PH)&(np.r_[False,~(c5[:-1]>PH[:-1])])&np.isfinite(m15atr)&(m15atr>0)&np.isfinite(PH)
    base=[]; acc=[]  # (bar, up1st, year)
    yr=m5["dt"].dt.year.to_numpy()
    for i in np.where(brk)[0]:
        if i>=n-2: continue
        a=m15atr[i]
        if not (np.isfinite(a) and a>0): continue
        base.append((i, fwd_up1st(hi,lo,i,c5[i],a,H,n), yr[i]))
        # acceptance: held above PH[i] for Wr bars (no close below level in i+1..i+Wr)
        lvl=PH[i]; end=min(i+1+Wr,n); held=True
        for jx in range(i+1,end):
            if c5[jx]<lvl: held=False; break
        if held and (i+Wr)<n-1:
            k=i+Wr; acc.append((k, fwd_up1st(hi,lo,k,c5[k],a,H,n), yr[k]))
    base=np.array(base); acc=np.array(acc)
    def pup(sub):
        if len(sub)==0: return float('nan'),0
        v=sub[:,1][(sub[:,1]==0)|(sub[:,1]==1)]; return (float((v==1).mean()) if len(v) else float('nan')), len(sub)
    pb,nb=pup(base); pa,na=pup(acc)
    print(f"FRONTIER M5-2 (causal fix): M15 breakout + M5 acceptance. breakouts={nb} accepted-held={na}")
    print(f"  P(up-target first) forward-from-entry: BASE(breakout bar)={pb:.3f}(n{nb})  M5-ACCEPTED(after {Wr}-bar hold)={pa:.3f}(n{na})")
    for lab,ym in [("DISC<=2023",lambda y:y<=2023),("CONF 2024",lambda y:y==2024),("OOS 2025-26",lambda y:y>=2025)]:
        b2=base[ym(base[:,2])]; a2=acc[ym(acc[:,2])]; pb2,nb2=pup(b2); pa2,na2=pup(a2)
        print(f"    {lab}: BASE={pb2:.3f}(n{nb2})  ACCEPTED={pa2:.3f}(n{na2})  delta={pa2-pb2:+.3f}")
    print("  => M5 acceptance informs only if ACCEPTED P(up1st) robustly > BASE across partitions (no circularity now).")
if __name__=="__main__": main()
