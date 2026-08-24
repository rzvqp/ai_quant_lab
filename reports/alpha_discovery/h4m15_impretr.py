"""h4m15_impretr.py — Family 2: M15 IMPULSE -> RETRACEMENT geometry conditional on causal H4 state (§5).
Descriptors = recent impulse magnitude (ATR-normalized, W=8/16) x retracement depth (where close sits in the
window range): shallow retrace (close near window extreme, continuation geometry) vs deep retrace (close pulled
back past the move, reversal/dip geometry). P(+70/-50 & +100/-70) lift vs SAME-H4-STATE base, L/S separate,
event-deduped, same-H4-state cross-era gate (DISC/CONF + per-year + b0 + b1). Interpretable only (§7). Reuses
the Family-1 harness (base_in_state, cond_lift, align_h4).
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_m15_data as m15d
from state_path_m15 import passage_m15
from h4_parent import align_h4
from h4m15_runlen import base_in_state, cond_lift, STATES, TARGETS, H, COOL

def descr(df):
    c=df["close"].to_numpy(); atr=df["atr"].to_numpy(); hi=df["high"]; lo=df["low"]
    def win(W):
        hh=hi.rolling(W).max().to_numpy(); ll=lo.rolling(W).min().to_numpy()
        imp=(c-pd.Series(c).shift(W).to_numpy())/atr; rng=np.maximum(hh-ll,1e-9)
        return imp,(hh-c)/rng,(c-ll)/rng   # imp, retrace-from-top (0=at high), retrace-from-bottom (0=at low)
    i8,ru8,rd8=win(8); i16,ru16,rd16=win(16)
    return {
      "impUp8&shallow":  (i8>1.0)&(ru8<0.30),   # up impulse, close near high -> continuation geom
      "impUp8&deep":     (i8>1.0)&(ru8>0.60),    # up impulse but deep pullback -> reversal/dip geom
      "impDn8&shallow":  (i8<-1.0)&(rd8<0.30),   # down impulse, close near low -> continuation geom
      "impDn8&deep":     (i8<-1.0)&(rd8>0.60),    # down impulse but bounced -> reversal/dip geom
      "impUp16&shallow": (i16>1.5)&(ru16<0.30),
      "impUp16&deep":    (i16>1.5)&(ru16>0.60),
      "impDn16&shallow": (i16<-1.5)&(rd16<0.30),
      "impDn16&deep":    (i16<-1.5)&(rd16>0.60),
    }

def main():
    print("FAMILY 2: M15 impulse->retracement geometry conditional on H4 state. P lift vs SAME-H4-STATE base, deduped, cross-era.")
    tfs=sb.build_frames(); m=tfs["M15"]; h4=tfs["H4"]; dev=m["is_dev"].to_numpy(); yr=m["dt"].dt.year.to_numpy()
    regc,hidx,uniq=align_h4(m,h4,sb.align_context); ou,od,_,_=passage_m15(m); D=descr(m)
    hh=m15d.build(verbose=False); hm=hh["M15"]; hh4=hh["H4"]; b0=hm["is_b0"].to_numpy(); b1=hm["is_b1"].to_numpy()
    regc2,hidx2,uniq2=align_h4(hm,hh4,m15d.align_causal); ou2,od2,_,_=passage_m15(hm); D2=descr(hm)
    disc=np.zeros(len(m),bool); idx=np.where(dev)[0]; disc[idx[:int(len(idx)*0.6)]]=True; conf=dev&~disc
    for r in STATES:
        if r not in uniq: continue
        hdr=False
        for dname,cond in D.items():
            cond=np.nan_to_num(cond.astype(float),nan=0).astype(bool); cond2=np.nan_to_num(D2[dname].astype(float),nan=0).astype(bool)
            for (X,Y) in TARGETS:
                for side in ('L','S'):
                    base,nb=base_in_state(ou,od,regc,uniq,dev,r,X,Y,side)
                    c,nE=cond_lift(ou,od,regc,uniq,dev,r,cond,X,Y,side)
                    if c is None: continue
                    lift=c-base
                    if abs(lift)<0.03: continue
                    cd,_=cond_lift(ou,od,regc,uniq,disc,r,cond,X,Y,side); bd,_=base_in_state(ou,od,regc,uniq,disc,r,X,Y,side)
                    cc,_=cond_lift(ou,od,regc,uniq,conf,r,cond,X,Y,side); bc,_=base_in_state(ou,od,regc,uniq,conf,r,X,Y,side)
                    dl=(cd-bd) if cd is not None else None; cl=(cc-bc) if cc is not None else None
                    l0=l1=None
                    if r in uniq2:
                        c0,_=cond_lift(ou2,od2,regc2,uniq2,b0,r,cond2,X,Y,side); b0b,_=base_in_state(ou2,od2,regc2,uniq2,b0,r,X,Y,side)
                        c1,_=cond_lift(ou2,od2,regc2,uniq2,b1,r,cond2,X,Y,side); b1b,_=base_in_state(ou2,od2,regc2,uniq2,b1,r,X,Y,side)
                        l0=(c0-b0b) if c0 is not None else None; l1=(c1-b1b) if c1 is not None else None
                    py=[]
                    for y in (2021,2022,2023):
                        mm=dev&(yr==y); cy,_=cond_lift(ou,od,regc,uniq,mm,r,cond,X,Y,side); by,_=base_in_state(ou,od,regc,uniq,mm,r,X,Y,side)
                        py.append((cy-by) if cy is not None else None)
                    stable=(abs(lift)>=0.04 and dl is not None and cl is not None and l0 is not None and l1 is not None
                            and np.sign(dl)==np.sign(lift) and np.sign(cl)==np.sign(lift)
                            and np.sign(l0)==np.sign(lift) and np.sign(l1)==np.sign(lift) and abs(l0)>=0.02 and abs(l1)>=0.02)
                    if not hdr: print(f"\n[H4={r}]"); hdr=True
                    pys=" ".join(f"{y}:{('%+.2f'%v) if v is not None else 'na'}" for y,v in zip((2021,2022,2023),py))
                    ds=" ".join(f"{k}={('%+.2f'%v) if v is not None else 'na'}" for k,v in (("D",dl),("C",cl),("b0",l0),("b1",l1)))
                    print(f"   {dname:17s} {side} +{X}/-{Y}: base={base:.2f} lift={lift:+.3f}(EffN {nE}) {ds} yr[{pys}]"+(" <== CROSS_STABLE" if stable else ""))

if __name__=="__main__":
    main()
