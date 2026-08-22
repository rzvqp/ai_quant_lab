"""h4m15_trans_interact.py — §21 completion: bounded M15 path-shape TRANSITION/sequence map + a small set of
interpretable INTERACTIONS conditional on causal H4 state. Transitions: squeeze->release (contraction 8 bars ago
-> expansion now), pullback->resume (mid-leg counter then resume in H4 dir). Interactions: H4 + 2 M15 descriptors
(momentum+clean; structure+decel) to test whether two descriptors unlock a cross-era-tradeable directional edge
single descriptors could not. Lift vs SAME-H4-STATE base, L/S separate, event-deduped, cross-era gate. Bounded (§21).
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_m15_data as m15d
from state_path_m15 import passage_m15
from h4_parent import align_h4
from h4m15_runlen import base_in_state, cond_lift, STATES, TARGETS, H, COOL

def feats(df):
    c=df["close"].to_numpy(); atr=df["atr"].to_numpy(); h=df["high"]; l=df["low"]; W=8
    hh_r=h.rolling(W).max().to_numpy(); ll_r=l.rolling(W).min().to_numpy()
    hh_p=h.shift(W).rolling(W).max().to_numpy(); ll_p=l.shift(W).rolling(W).min().to_numpy()
    contract=(hh_r<hh_p)&(ll_r>ll_p); expand=(hh_r>hh_p)&(ll_r<ll_p)
    contract_prev=pd.Series(contract).shift(8).fillna(False).to_numpy().astype(bool)
    s4=pd.Series(c).shift(4).to_numpy(); s8=pd.Series(c).shift(8).to_numpy()
    v_rec=(c-s4)/atr; v_pri=(s4-s8)/atr
    freshHigh=h.to_numpy()>=hh_r; freshLow=l.to_numpy()<=ll_r
    den4=pd.Series(np.abs(np.diff(c,prepend=c[0]))).rolling(4).sum().to_numpy(); pe4=np.where(den4>0,(c-s4)/den4,0.0)
    return dict(expand=expand, contract=contract, contract_prev=contract_prev, v_rec=v_rec, v_pri=v_pri,
                freshHigh=freshHigh, freshLow=freshLow, pe4=pe4,
                LH_LL=(hh_r<hh_p)&(ll_r<ll_p))

def build_cells(F):
    sq=F["contract_prev"]&F["expand"]                       # squeeze (8 ago) -> release now
    pru=(F["v_pri"]<-0.2)&(F["v_rec"]>0.3)                   # mid-leg down -> resume up
    prd=(F["v_pri"]>0.2)&(F["v_rec"]<-0.3)                   # mid-leg up -> resume down
    # (cell name, cond, restrict-to-H4-state or None, side)
    return {
      "sqRelease@UP->L":   (sq, "UP", 'L'),
      "sqRelease@DOWN->S": (sq, "DOWN", 'S'),
      "sqRelease@QUIET->L":(sq, "QUIET", 'L'),
      "sqRelease@QUIET->S":(sq, "QUIET", 'S'),
      "pullResume@UP->L":  (pru, "UP", 'L'),
      "pullResume@DOWN->S":(prd, "DOWN", 'S'),
      # interactions (2 descriptors)
      "IX freshHi&clean@UP->L": (F["freshHigh"]&(F["pe4"]>0.5), "UP", 'L'),
      "IX LH_LL&decel@DOWN->S": (F["LH_LL"]&(F["v_rec"]<-0.3)&(F["v_rec"]>F["v_pri"]), "DOWN", 'S'),
    }

def main():
    print("§21 completion: M15 path-shape TRANSITIONS + INTERACTIONS conditional on H4. Lift vs SAME-H4-STATE base, deduped, cross-era.")
    tfs=sb.build_frames(); m=tfs["M15"]; h4=tfs["H4"]; dev=m["is_dev"].to_numpy(); yr=m["dt"].dt.year.to_numpy()
    regc,hidx,uniq=align_h4(m,h4,sb.align_context); ou,od,_,_=passage_m15(m); C=build_cells(feats(m))
    hh=m15d.build(verbose=False); hm=hh["M15"]; hh4=hh["H4"]; b0=hm["is_b0"].to_numpy(); b1=hm["is_b1"].to_numpy()
    regc2,_,uniq2=align_h4(hm,hh4,m15d.align_causal); ou2,od2,_,_=passage_m15(hm); C2=build_cells(feats(hm))
    disc=np.zeros(len(m),bool); idx=np.where(dev)[0]; disc[idx[:int(len(idx)*0.6)]]=True; conf=dev&~disc
    for name,(cond,r,side) in C.items():
        if r not in uniq: continue
        cond=np.nan_to_num(cond.astype(float),nan=0).astype(bool); cond2=np.nan_to_num(C2[name][0].astype(float),nan=0).astype(bool)
        for (X,Y) in TARGETS:
            base,_=base_in_state(ou,od,regc,uniq,dev,r,X,Y,side)
            c,nE=cond_lift(ou,od,regc,uniq,dev,r,cond,X,Y,side)
            if c is None:
                print(f"  {name} +{X}/-{Y}: thin"); continue
            lift=c-base
            cd,_=cond_lift(ou,od,regc,uniq,disc,r,cond,X,Y,side); bd,_=base_in_state(ou,od,regc,uniq,disc,r,X,Y,side)
            cc,_=cond_lift(ou,od,regc,uniq,conf,r,cond,X,Y,side); bc,_=base_in_state(ou,od,regc,uniq,conf,r,X,Y,side)
            dl=(cd-bd) if cd is not None else None; cl=(cc-bc) if cc is not None else None
            l0=l1=None
            if r in uniq2:
                c0,_=cond_lift(ou2,od2,regc2,uniq2,b0,r,cond2,X,Y,side); b0b,_=base_in_state(ou2,od2,regc2,uniq2,b0,r,X,Y,side)
                c1,_=cond_lift(ou2,od2,regc2,uniq2,b1,r,cond2,X,Y,side); b1b,_=base_in_state(ou2,od2,regc2,uniq2,b1,r,X,Y,side)
                l0=(c0-b0b) if c0 is not None else None; l1=(c1-b1b) if c1 is not None else None
            stable=(abs(lift)>=0.04 and None not in (dl,cl,l0,l1)
                    and np.sign(dl)==np.sign(lift) and np.sign(cl)==np.sign(lift)
                    and np.sign(l0)==np.sign(lift) and np.sign(l1)==np.sign(lift) and abs(l0)>=0.02 and abs(l1)>=0.02)
            ds=" ".join(f"{k}={('%+.2f'%v) if v is not None else 'na'}" for k,v in (("D",dl),("C",cl),("b0",l0),("b1",l1)))
            print(f"  {name} +{X}/-{Y}: base={base:.2f} lift={lift:+.3f}(EffN {nE}) {ds}"+(" <== CROSS_STABLE" if stable else ""))

if __name__=="__main__":
    main()
