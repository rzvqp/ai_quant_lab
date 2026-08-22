"""state_regime_discover.py — within-regime STATE discovery (regime-conditional). For a priority regime, screen
causal states for MATERIAL SHORT P(+100/-70) lift over the SAME-REGIME base, validate across the SAME regime in
b0/b1 (same-regime cross-era gate). Within-regime DISC/CONF + per-year + sample honesty. Causal, price-only.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd
from state_validate import passage, P
from state_regime import regime

def feats(df):
    c=df["close"].to_numpy(); h=df["high"].to_numpy(); l=df["low"].to_numpy()
    e20=df["ema20"].to_numpy(); atr=df["atr"].to_numpy(); eff=df["effic"].to_numpy()
    hh=pd.Series(h).rolling(20).max().shift(1).to_numpy(); ll=pd.Series(l).rolling(20).min().shift(1).to_numpy()
    dist=(c-e20)/atr; pos=np.where((hh-ll)>0,(c-ll)/(hh-ll),0.5)
    vc=atr/pd.Series(atr).shift(12).to_numpy(); imp=(c-pd.Series(c).shift(6).to_numpy())/atr
    up=(c>np.roll(c,1)).astype(int); run=np.zeros(len(c))
    for i in range(1,len(c)): run[i]=run[i-1]+1 if up[i]==up[i-1] else 1
    persist=run*np.where(c>np.roll(c,1),1,-1)
    return dict(dist=dist,pos=pos,vc=vc,imp=imp,persist=persist,eff=eff)

def states_short(F):
    return {  # states hypothesized to help SHORT within a bearish/quiet regime
      "deep_below_ema(dist<-1.5)": F["dist"]<-1.5,
      "bounced_top(pos>0.7)":      F["pos"]>0.7,
      "strong_downeff(eff<-0.6)":  F["eff"]<-0.6,
      "rising_vol(vc>1.15)":       F["vc"]>1.15,
      "falling_vol(vc<0.9)":       F["vc"]<0.9,
      "fresh_down_imp(imp<-1)":    F["imp"]<-1.0,
      "persist_down(persist<-3)":  F["persist"]<-3,
      "near_top+downeff":          (F["pos"]>0.6)&(F["eff"]<-0.3),
    }

def screen(regime_name):
    tfs=sb.build_frames(); h1=tfs["H1"]; dev=h1["is_dev"].to_numpy(); yr=h1["dt"].dt.year.to_numpy()
    lab=regime(h1); up,dn=passage(h1); F=feats(h1); St=states_short(F)
    reg=dev&(lab==regime_name); base,_=P(up,dn,100,70,'S',48,reg)
    idx=np.where(dev)[0]; cut=idx[int(len(idx)*0.6)]
    disc=dev&(np.arange(len(h1))<cut); conf=dev&(np.arange(len(h1))>=cut)
    # b0/b1 same-regime
    hh=hd.load()["H1"]; lab2=regime(hh); up2,dn2=passage(hh); F2=feats(hh); St2=states_short(F2)
    b0=hh["is_b0"].to_numpy(); b1=hh["is_b1"].to_numpy()
    rb0=b0&(lab2==regime_name); rb1=b1&(lab2==regime_name)
    bb0,_=P(up2,dn2,100,70,'S',48,rb0); bb1,_=P(up2,dn2,100,70,'S',48,rb1)
    print(f"\n===== REGIME={regime_name} SHORT within-regime state discovery =====")
    print(f"  same-regime SHORT base: DEV={base:.3f}(n{int(reg.sum())}) b0={bb0:.3f}(n{int(rb0.sum())}) b1={bb1:.3f}(n{int(rb1.sum())})")
    for name in St:
        cond=np.nan_to_num(St[name].astype(float),nan=0).astype(bool); cond2=np.nan_to_num(St2[name].astype(float),nan=0).astype(bool)
        c,nc=P(up,dn,100,70,'S',48,reg&cond)
        if nc<50: print(f"  {name}: N={nc} (thin)"); continue
        lift=c-base
        dl=P(up,dn,100,70,'S',48,disc&(lab==regime_name)&cond)[0]-P(up,dn,100,70,'S',48,disc&(lab==regime_name))[0]
        cl=P(up,dn,100,70,'S',48,conf&(lab==regime_name)&cond)[0]-P(up,dn,100,70,'S',48,conf&(lab==regime_name))[0]
        py=[]
        for y in (2021,2022,2023):
            m=reg&(yr==y)&cond
            py.append(P(up,dn,100,70,'S',48,m)[0]-P(up,dn,100,70,'S',48,reg&(yr==y))[0] if m.sum()>=30 else None)
        l0=(P(up2,dn2,100,70,'S',48,rb0&cond2)[0]-bb0) if (rb0&cond2).sum()>=50 else None
        l1=(P(up2,dn2,100,70,'S',48,rb1&cond2)[0]-bb1) if (rb1&cond2).sum()>=50 else None
        xok=[v for v in (l0,l1) if v is not None]
        crossstable=(abs(lift)>=0.04 and np.sign(dl)==np.sign(lift) and np.sign(cl)==np.sign(lift)
                     and len(xok)>=1 and all(np.sign(v)==np.sign(lift) and abs(v)>=0.02 for v in xok))
        pys=" ".join(f"{y}:{('%.2f'%v) if v is not None else 'na'}" for y,v in zip((2021,2022,2023),py))
        xs=f"b0={('%.3f'%l0) if l0 is not None else 'thin'} b1={('%.3f'%l1) if l1 is not None else 'thin'}"
        print(f"  {name}: DEVlift={lift:+.3f}(n{nc}) DISC={dl:+.2f} CONF={cl:+.2f} yr[{pys}] | same-regime {xs}"+(" <== SAME_REGIME_STABLE" if crossstable else ""))

def main():
    for r in ("DOWN","QUIET"): screen(r)

if __name__=="__main__":
    main()
