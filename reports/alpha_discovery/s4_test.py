"""S4 SWEEP REVERSAL — FROZEN deterministic test (EXTERNAL_RULE_MAPPING.md). LONG/SHORT separate.
M5 reclaim; 3 causal >=1-day structural levels (PDH/PDL, H4 10-swing, H1 24-hi/lo); sweep = M5 wick beyond +
close back inside; SL beyond sweep extreme +/-$0.50; RR{1.0,1.5,2.0}; +quality, anti-fade, trend-aligned,
+1-bar delay, invalidation-exit. NO non-causal D1/H4 merge (HTF via close_time). Volume/news excluded (price-only).
"""
import numpy as np, pandas as pd
import m5_data, swing_base as sb, external_common as ec

BUF=0.50; COOL=12; HOR=288; PRESS=12  # $0.50 buffer, 1h dedup, 1-day horizon, 12-bar pressure window

def sim_inval(m5, ev, side, risk, sweep_ext, rr, horizon, scenario="STRESS"):
    o=m5["open"].to_numpy(); h=m5["high"].to_numpy(); l=m5["low"].to_numpy(); c=m5["close"].to_numpy(); t=m5["time"].to_numpy(); n=len(m5)
    cost=sb.COST[scenario]; rows=[]
    for k,i in enumerate(ev):
        ei=i+1
        if ei>=n: continue
        rk=risk[k]
        if not np.isfinite(rk) or rk<=0: continue
        entry=o[ei]; se=sweep_ext[k]
        if side>0: stop=entry-rk; targ=entry+rr*rk
        else: stop=entry+rk; targ=entry-rr*rk
        expx=None
        for j in range(ei,min(ei+horizon+1,n)):
            hitstop=(l[j]<=stop) if side>0 else (h[j]>=stop)
            hittarg=(h[j]>=targ) if side>0 else (l[j]<=targ)
            invalid=(c[j]<se) if side>0 else (c[j]>se)  # M5 close back beyond sweep extreme
            if hitstop: expx=stop; break
            if hittarg: expx=targ; break
            if invalid: expx=c[j]; break
        if expx is None: expx=c[min(ei+horizon,n-1)]
        g=side*(expx-entry); rows.append((g-cost)/rk)
    return np.array(rows)

def report(m5, ev, side, risk, sweep_ext, tag, yrs_all=True):
    if len(ev)<8: print(f"    [{tag}] N={len(ev)} (too few)"); return None
    ps=ec.path_stats(m5,ev,side,risk,HOR)
    tr,m,dc=ec.econ_line(m5,ev,side,risk,1.0,HOR,"STRESS")
    _,m15,_=ec.econ_line(m5,ev,side,risk,1.5,HOR,"STRESS")
    _,md,_=ec.econ_line(m5,ev,side,risk,1.0,HOR,"STRESS",delay=1)  # +1 bar degradation
    inv=sim_inval(m5,ev,side,risk,sweep_ext,1.0,HOR)
    allpos=all(v[0]>0 for v in m["per_year"].values())
    print(f"    [{tag}] N={m['N']:3d} medMFE={ps['medMFE']:.2f} medMAE={ps['medMAE']:.2f} advF={ps['advFirst']:.2f} "
          f"P(+1<-1)={ps['P_1']:.2f} | rr1={m['avgR']:+.3f}(b5 {m['best5']:+.2f} b10 {m['best10']:+.2f}) rr1.5={m15['avgR']:+.3f} "
          f"| DISC{(dc['disc_avgR'] if dc else 0):+.2f}/CONF{(dc['conf_avgR'] if dc else 0):+.2f} yr+={str(allpos)[0]} "
          f"| +1bar={md['avgR']:+.3f} inval={inv.mean():+.3f} medSL={m['med_sl_pips']:.0f}p tpm={m['trades_per_month']:.1f}")
    return m

def levels(m5, tfs):
    """Causal >=1-day structural levels aligned to M5 via close_time."""
    d1=tfs["D1"].copy(); h4=tfs["H4"].copy(); h1=tfs["H1"].copy()
    # D1 prior-day H/L + trend
    d1["d1_up"]=(d1["ema20"]>d1["ema50"]).astype(float)
    m=sb.align_context(m5,d1,["high","low","d1_up"],"_d1")
    # H4 10-bar swing (causal shift1)
    h4["swh"]=pd.Series(h4["high"]).rolling(10).max().shift(1).to_numpy()
    h4["swl"]=pd.Series(h4["low"]).rolling(10).min().shift(1).to_numpy()
    m=sb.align_context(m,h4,["swh","swl"],"_h4")
    # H1 24-bar hi/lo (~1 day, causal shift1)
    h1["h1h"]=pd.Series(h1["high"]).rolling(24).max().shift(1).to_numpy()
    h1["h1l"]=pd.Series(h1["low"]).rolling(24).min().shift(1).to_numpy()
    m=sb.align_context(m,h1,["h1h","h1l"],"_h1")
    return m

def detect(m5df, sup, res):
    """Single-M5-bar sweep+reclaim. LONG: low<sup & close>sup. SHORT: high>res & close<res."""
    l=m5df["low"].to_numpy(); h=m5df["high"].to_numpy(); c=m5df["close"].to_numpy()
    long_sig=(l<sup)&(c>sup)&np.isfinite(sup)
    short_sig=(h>res)&(c<res)&np.isfinite(res)
    return long_sig, short_sig

def run_variant(m5df, name, sup, res, dev_mask, d1_up, atr):
    o=m5df["open"].to_numpy(); l=m5df["low"].to_numpy(); h=m5df["high"].to_numpy(); c=m5df["close"].to_numpy()
    ls,ss=detect(m5df,sup,res)
    print(f"  LEVEL={name}: raw long_sig={int((ls&dev_mask).sum())} short_sig={int((ss&dev_mask).sum())}")
    for side,name2,sig,lvl in ((+1,"LONG",ls,sup),(-1,"SHORT",ss,res)):
        raw=[i for i in np.where(sig)[0] if i+1<len(m5df) and dev_mask[i]]
        ev=sb.dedup_events(np.array(raw),cooldown=COOL)
        if len(ev)<8: print(f"   {name2}: N={len(ev)} (too few)"); continue
        if side>0: swe=l[ev]; risk=np.array([o[i+1]-(l[i]-BUF) for i in ev])
        else:      swe=h[ev]; risk=np.array([(h[i]+BUF)-o[i+1] for i in ev])
        ok=np.isfinite(risk)&(risk>0); ev,risk,swe=ev[ok],risk[ok],swe[ok]
        # BASE
        report(m5df,ev,side,risk,swe,f"{name2} BASE")
        # + reclaim quality
        rng=h[ev]-l[ev]; rng=np.where(rng>0,rng,np.nan)
        q = ((c[ev]-l[ev])/rng>=0.66) if side>0 else ((h[ev]-c[ev])/rng>=0.66)
        if q.sum()>=8: report(m5df,ev[q],side,risk[q],swe[q],f"{name2} +quality")
        # anti-fade: exclude pre-sweep pressure into the level
        press=np.zeros(len(ev),bool)
        for kk,i in enumerate(ev):
            a=max(i-PRESS,0)
            if side>0: press[kk]=(l[i-1]<l[a]) and (np.polyfit(range(PRESS),l[a:a+PRESS],1)[0]<0 if i-a==PRESS else False)
            else:      press[kk]=(h[i-1]>h[a]) and (np.polyfit(range(PRESS),h[a:a+PRESS],1)[0]>0 if i-a==PRESS else False)
        keep=~press
        if keep.sum()>=8: report(m5df,ev[keep],side,risk[keep],swe[keep],f"{name2} anti-fade")
        # TREND-ALIGNED (golden): sweep AGAINST D1 then reclaim WITH D1 trend
        if side>0: ta=(d1_up[ev]>0.5)   # long reclaim in D1 uptrend (swept support against trend)
        else:      ta=(d1_up[ev]<0.5)
        if ta.sum()>=8: report(m5df,ev[ta],side,risk[ta],swe[ta],f"{name2} TREND-ALIGNED")

def main():
    m5,meta=m5_data.load_m5()
    tr=np.maximum(m5["high"]-m5["low"],np.maximum(np.abs(m5["high"]-m5["close"].shift(1)),np.abs(m5["low"]-m5["close"].shift(1))))
    m5["atr"]=tr.rolling(14).mean()
    m5["is_dev"]=m5["dt"]<=m5_data.DEV_END
    tfs=sb.build_frames()
    m5=levels(m5,tfs)
    dev_mask=m5["is_dev"].to_numpy(); d1_up=m5["d1_up_d1"].to_numpy(); atr=m5["atr"].to_numpy()
    print(f"S4 SWEEP REVERSAL (FROZEN)  M5 DEV bars={int(dev_mask.sum())}  STRESS cost")
    run_variant(m5,"PDH_PDL",m5["low_d1"].to_numpy(),m5["high_d1"].to_numpy(),dev_mask,d1_up,atr)
    run_variant(m5,"H4_swing",m5["swl_h4"].to_numpy(),m5["swh_h4"].to_numpy(),dev_mask,d1_up,atr)
    run_variant(m5,"H1_24hilo",m5["h1l_h1"].to_numpy(),m5["h1h_h1"].to_numpy(),dev_mask,d1_up,atr)

if __name__=="__main__":
    main()
