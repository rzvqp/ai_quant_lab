"""state_regime_discover2.py — UP/CHOP LONG within-regime states + regime-TRANSITION family (§27).
Same-regime / same-transition cross-era gate (DEV vs b0/b1). Causal, price-only. Regime-conditional baselines.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd
from state_validate import passage, P
from state_regime import regime
from state_regime_discover import feats

def states_long(F):
    return {
      "pullback_mid(0.3<pos<0.6)": (F["pos"]>0.3)&(F["pos"]<0.6),
      "near_low(pos<0.35)+upeff":  (F["pos"]<0.35)&(F["eff"]>0.3),
      "deep_above_ema(dist>1.5)":  F["dist"]>1.5,
      "rising_vol(vc>1.15)":       F["vc"]>1.15,
      "falling_vol(vc<0.9)":       F["vc"]<0.9,
      "fresh_up_imp(imp>1)":       F["imp"]>1.0,
      "persist_up(persist>3)":     F["persist"]>3,
    }

def screen_long(regime_name):
    tfs=sb.build_frames(); h1=tfs["H1"]; dev=h1["is_dev"].to_numpy(); yr=h1["dt"].dt.year.to_numpy()
    lab=regime(h1); up,dn=passage(h1); F=feats(h1); St=states_long(F)
    reg=dev&(lab==regime_name); base,_=P(up,dn,100,70,'L',48,reg)
    idx=np.where(dev)[0]; cut=idx[int(len(idx)*0.6)]; disc=dev&(np.arange(len(h1))<cut); conf=dev&(np.arange(len(h1))>=cut)
    hh=hd.load()["H1"]; lab2=regime(hh); up2,dn2=passage(hh); F2=feats(hh); St2=states_long(F2)
    b0=hh["is_b0"].to_numpy(); b1=hh["is_b1"].to_numpy(); rb0=b0&(lab2==regime_name); rb1=b1&(lab2==regime_name)
    bb0,_=P(up2,dn2,100,70,'L',48,rb0); bb1,_=P(up2,dn2,100,70,'L',48,rb1)
    print(f"\n== REGIME={regime_name} LONG == base DEV={base:.3f}(n{int(reg.sum())}) b0={bb0:.3f} b1={bb1:.3f}")
    for name in St:
        cond=np.nan_to_num(St[name].astype(float),nan=0).astype(bool); cond2=np.nan_to_num(St2[name].astype(float),nan=0).astype(bool)
        c,nc=P(up,dn,100,70,'L',48,reg&cond)
        if nc<50: print(f"  {name}: N={nc}(thin)"); continue
        lift=c-base
        dl=P(up,dn,100,70,'L',48,disc&(lab==regime_name)&cond)[0]-P(up,dn,100,70,'L',48,disc&(lab==regime_name))[0]
        cl=P(up,dn,100,70,'L',48,conf&(lab==regime_name)&cond)[0]-P(up,dn,100,70,'L',48,conf&(lab==regime_name))[0]
        l0=(P(up2,dn2,100,70,'L',48,rb0&cond2)[0]-bb0) if (rb0&cond2).sum()>=50 else None
        l1=(P(up2,dn2,100,70,'L',48,rb1&cond2)[0]-bb1) if (rb1&cond2).sum()>=50 else None
        xok=[v for v in (l0,l1) if v is not None]
        stable=(abs(lift)>=0.04 and np.sign(dl)==np.sign(lift) and np.sign(cl)==np.sign(lift) and len(xok)>=1 and all(np.sign(v)==np.sign(lift) and abs(v)>=0.02 for v in xok))
        print(f"  {name}: DEVlift={lift:+.3f}(n{nc}) DISC={dl:+.2f} CONF={cl:+.2f} | same-regime b0={('%.3f'%l0) if l0 is not None else 'thin'} b1={('%.3f'%l1) if l1 is not None else 'thin'}"+(" <== STABLE" if stable else ""))

def onset(lab,A,B):
    o=np.zeros(len(lab),bool); o[1:]=(lab[1:]==B)&(lab[:-1]==A); return o

def screen_transitions():
    tfs=sb.build_frames(); h1=tfs["H1"]; dev=h1["is_dev"].to_numpy(); lab=regime(h1); up,dn=passage(h1)
    hh=hd.load()["H1"]; lab2=regime(hh); up2,dn2=passage(hh); hb=(hh["is_b0"]|hh["is_b1"]).to_numpy()
    TR=[("TRANSITION","UP",'L'),("QUIET","UP",'L'),("CHOP","UP",'L'),
        ("TRANSITION","DOWN",'S'),("QUIET","DOWN",'S'),("CHOP","DOWN",'S'),
        ("UP","TRANSITION",'S'),("DOWN","TRANSITION",'L')]
    print("\n== REGIME-TRANSITION family (onset A->B, forward path vs destination-regime base) ==")
    for A,B,side in TR:
        o=onset(lab,A,B); dstbase,_=P(up,dn,100,70,side,48,dev&(lab==B)); c,nc=P(up,dn,100,70,side,48,dev&o)
        if nc<40: print(f"  {A}->{B} {side}: N={nc}(thin)"); continue
        lift=c-dstbase
        o2=onset(lab2,A,B); db2,_=P(up2,dn2,100,70,side,48,hb&(lab2==B)); c2,nc2=P(up2,dn2,100,70,side,48,hb&o2)
        l2=(c2-db2) if nc2>=40 else None
        stable=abs(lift)>=0.04 and l2 is not None and np.sign(l2)==np.sign(lift) and abs(l2)>=0.02
        print(f"  {A}->{B} {side}: DEVlift={lift:+.3f}(n{nc}, dstbase={dstbase:.2f}) | b0b1 lift={('%.3f'%l2) if l2 is not None else 'thin'}(n{nc2})"+(" <== STABLE" if stable else ""))

def main():
    for r in ("UP","CHOP"): screen_long(r)
    screen_transitions()

if __name__=="__main__":
    main()
