"""m5_f1.py — Frontier M5-1 (mandate NATIVE_M5, info-first §7). HIGHER-TF SETUP: H1-downtrend + M15 counter-trend bounce (a
trend-continuation SHORT setup that historically fails on adverse-first / stop-before-move). M5 HYPOTHESIS: entering only after
M5 confirms down-momentum onset (M5 close breaks the recent M5 low) reduces adverse-first ordering. INFO TEST: adverse-first &
P(target-before-stop) measured on the fine M5 path, from the M15-setup bar (BASE) vs from the M5-confirmation bar (M5-COND).
Barriers = +/-1.5*M15-ATR (structural, M15-scale, NOT micro). Causal alignment via m5_data (strict nominal-close). Coverage
2021-2026 single macro-era (disclosed). Partitions within window: DISC<=2023 / CONF 2024 / OOS 2025-26."""
import numpy as np, pandas as pd
import cur_data as CD, m5_data as M5D
Wtrig=24; Hbars=288  # trigger window 2h; forward horizon 288 M5 bars = 24h
def first_passage(hi, lo, entry_i, p, up, dn, H):
    end=min(entry_i+1+H, len(hi))
    for j in range(entry_i+1, end):
        hitU=hi[j]>=up; hitD=lo[j]<=dn
        if hitD and hitU: return -1  # stop-wins-ties (adverse for short = up first) -> conservative: treat as adverse
        if hitU: return 0            # up (adverse) first
        if hitD: return 1            # down (target) first
    return -9                        # neither within H
def main():
    m5=M5D.load_m5(); H1=M5D.htf_at_m5(m5,"H1"); M15=M5D.htf_at_m5(m5,"M15")
    t5=m5["time"].to_numpy(); hi=m5["high"].to_numpy(); lo=m5["low"].to_numpy(); c5=m5["close"].to_numpy(); n=len(m5)
    h1dn=(H1["h1_ema20"].to_numpy()<H1["h1_ema50"].to_numpy())
    m15c=M15["m15_close"].to_numpy(); m15atr=M15["m15_atr"].to_numpy(); m15e20=M15["m15_ema20"].to_numpy(); m15e50=M15["m15_ema50"].to_numpy()
    # M15 counter-trend bounce (causal, from mapped M15 state): M15 short-term up within H1-down = m15 close above m15 ema20 (bounce up)
    bounce=h1dn&(m15c>m15e20)&np.isfinite(m15atr)&(m15atr>0)
    # setup 'bar' = first M5 bar where bounce state turns ON (fresh) -> the M15 setup moment
    setup=bounce&~np.r_[False,bounce[:-1]]
    yr=m5["dt"].dt.year.to_numpy()
    # M5 down-confirmation: m5 close < min(prior 6 m5 lows)
    m5low6=pd.Series(lo).rolling(6).min().shift(1).to_numpy(); m5break=(c5<m5low6)
    base_af=[]; base_yr=[]; cond_af=[]; cond_yr=[]
    for i in np.where(setup)[0]:
        if i>=n-2: continue
        p=c5[i]; a=m15atr[i]
        if not (np.isfinite(a) and a>0): continue
        up=p+1.5*a; dn=p-1.5*a
        base_af.append(first_passage(hi,lo,i,p,up,dn,Hbars)); base_yr.append(yr[i])
        # M5 trigger within Wtrig
        end=min(i+1+Wtrig,n); tj=-1
        for j in range(i+1,end):
            if m5break[j]: tj=j; break
        if tj<0: continue
        pj=c5[tj]; upj=pj+1.5*a; dnj=pj-1.5*a
        cond_af.append(first_passage(hi,lo,tj,pj,upj,dnj,Hbars)); cond_yr.append(yr[tj])
    base_af=np.array(base_af); base_yr=np.array(base_yr); cond_af=np.array(cond_af); cond_yr=np.array(cond_yr)
    def pdown(af): 
        r=af[(af==0)|(af==1)]; return float((r==1).mean()) if len(r) else float('nan'), int(len(af))
    print(f"FRONTIER M5-1 info: H1-down + M15-bounce SHORT. setups={len(base_af)} M5-triggered={len(cond_af)}")
    print("  P(target-before-stop) [down first], BASE (M15 setup entry) vs M5-COND (M5 down-break entry):")
    for lab,ym in [("ALL",None),("DISC<=2023",lambda y:y<=2023),("CONF 2024",lambda y:y==2024),("OOS 2025-26",lambda y:y>=2025)]:
        bm=base_af if ym is None else base_af[ym(base_yr)]; cm=cond_af if ym is None else cond_af[ym(cond_yr)]
        pb,nb=pdown(bm); pc,nc=pdown(cm)
        print(f"    {lab:12s}: BASE P(down1st)={pb:.3f}(n{nb})  M5-COND P(down1st)={pc:.3f}(n{nc})  delta={pc-pb:+.3f}")
    print("  => M5 adds info only if M5-COND P(down1st) robustly > BASE across partitions.")
if __name__=="__main__": main()
