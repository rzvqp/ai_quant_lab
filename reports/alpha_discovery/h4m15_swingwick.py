"""h4m15_swingwick.py — Family 4: M15 structural SWING-SEQUENCE (HH/HL vs LH/LL block relationship) + WICK/BODY
sequence asymmetry, conditional on causal H4 state (§5). Microstructure class distinct from F1-F3. Recent 8-bar
block vs prior 8-bar block: HH_HL=uptrend structure, LH_LL=downtrend, HH_LL=expansion, LH_HL=contraction; wick
asymmetry = cumulative upper vs lower wick (rejection of highs=bearish / lows=bullish). P(+70/-50 & +100/-70)
lift vs SAME-H4-STATE base, L/S separate, event-deduped, same-H4-state cross-era gate. Interpretable only (§7).
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_m15_data as m15d
from state_path_m15 import passage_m15
from h4_parent import align_h4
from h4m15_runlen import base_in_state, cond_lift, STATES, TARGETS, H, COOL

def descr(df):
    h=df["high"]; l=df["low"]; o=df["open"].to_numpy(); c=df["close"].to_numpy(); W=8
    hh_r=h.rolling(W).max().to_numpy(); ll_r=l.rolling(W).min().to_numpy()
    hh_p=h.shift(W).rolling(W).max().to_numpy(); ll_p=l.shift(W).rolling(W).min().to_numpy()
    hv=h.to_numpy(); lv=l.to_numpy()
    uw=hv-np.maximum(o,c); lw=np.minimum(o,c)-lv
    uwS=pd.Series(uw).rolling(W).sum().to_numpy(); lwS=pd.Series(lw).rolling(W).sum().to_numpy()
    wa=np.where((uwS+lwS)>0,(uwS-lwS)/(uwS+lwS),0.0)
    return {
      "HH_HL(uptrend)":  (hh_r>hh_p)&(ll_r>ll_p),
      "LH_LL(downtrend)":(hh_r<hh_p)&(ll_r<ll_p),
      "HH_LL(expand)":   (hh_r>hh_p)&(ll_r<ll_p),
      "LH_HL(contract)": (hh_r<hh_p)&(ll_r>ll_p),
      "uwDom(sell-rej)": wa>0.3,
      "lwDom(buy-rej)":  wa<-0.3,
    }

def main():
    print("FAMILY 4: M15 swing-sequence (HH/HL) + wick asymmetry conditional on H4 state. P lift vs SAME-H4-STATE base, deduped, cross-era.")
    tfs=sb.build_frames(); m=tfs["M15"]; h4=tfs["H4"]; dev=m["is_dev"].to_numpy(); yr=m["dt"].dt.year.to_numpy()
    regc,hidx,uniq=align_h4(m,h4,sb.align_context); ou,od,_,_=passage_m15(m); D=descr(m)
    hh=m15d.build(verbose=False); hm=hh["M15"]; hh4=hh["H4"]; b0=hm["is_b0"].to_numpy(); b1=hm["is_b1"].to_numpy()
    regc2,_,uniq2=align_h4(hm,hh4,m15d.align_causal); ou2,od2,_,_=passage_m15(hm); D2=descr(hm)
    disc=np.zeros(len(m),bool); idx=np.where(dev)[0]; disc[idx[:int(len(idx)*0.6)]]=True; conf=dev&~disc
    for r in STATES:
        if r not in uniq: continue
        hdr=False
        for dname,cond in D.items():
            cond=np.nan_to_num(cond.astype(float),nan=0).astype(bool); cond2=np.nan_to_num(D2[dname].astype(float),nan=0).astype(bool)
            for (X,Y) in TARGETS:
                for side in ('L','S'):
                    base,_=base_in_state(ou,od,regc,uniq,dev,r,X,Y,side)
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
                    print(f"   {dname:16s} {side} +{X}/-{Y}: base={base:.2f} lift={lift:+.3f}(EffN {nE}) {ds} yr[{pys}]"+(" <== CROSS_STABLE" if stable else ""))

if __name__=="__main__":
    main()
