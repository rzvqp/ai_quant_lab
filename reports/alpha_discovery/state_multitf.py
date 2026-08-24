"""state_multitf.py — multi-TF state family. Causal HIGHER-TF state (H4/D1 trend/efficiency/extension) aligned to
H1 (close_time<=decision) conditioning the H1 forward path P(+100/-70) L/S. Cross-population b0/b1 as a FIRST-CLASS
gate (in-screen), per the regime-conditional lesson. Price-only, causal. Flag CROSS_STABLE = within-DEV stable AND
same-sign lift on BOTH b0 and b1. Redundancy note: 'HTF-uptrend->H1 LONG' = trend-beta (REDUNDANT_EXISTING_ALPHA).
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd
from state_validate import passage, P

def htf_cols(h4, d1):
    h4=h4.copy(); d1=d1.copy()
    h4["h4_up"]=(h4["ema20"]>h4["ema50"]).astype(float); h4["h4_ext"]=((h4["ema20"]-h4["ema50"])/h4["atr"]); h4["h4_eff"]=h4["effic"]
    d1["d1_up"]=(d1["ema20"]>d1["ema50"]).astype(float); d1["d1_eff"]=d1["effic"]
    return h4,d1

def states_from(aligned):
    h4u=aligned["h4_up"].to_numpy(); h4e=aligned["h4_eff"].to_numpy(); h4x=aligned["h4_ext"].to_numpy()
    d1u=aligned["d1_up"].to_numpy(); d1e=aligned["d1_eff"].to_numpy()
    return {
      "H4_up":            h4u>0.5,
      "H4_down":          h4u<0.5,
      "H4_effUp(>.3)":    h4e>0.3,
      "H4_effDn(<-.3)":   h4e<-0.3,
      "H4_extended(>1)":  h4x>1.0,
      "D1_up":            d1u>0.5,
      "D1_down":          d1u<0.5,
    }

def lift(up,dn,side,base_mask,cond_mask):
    b,_=P(up,dn,100,70,side,48,base_mask); c,nc=P(up,dn,100,70,side,48,cond_mask); return c-b,nc

def main():
    # ---- DEV 2021-2023 ----
    tfs=sb.build_frames(); h1=tfs["H1"]; dev=h1["is_dev"].to_numpy(); yr=h1["dt"].dt.year.to_numpy()
    h4,d1=htf_cols(tfs["H4"],tfs["D1"])
    a=sb.align_context(h1,h4,["h4_up","h4_ext","h4_eff"],""); a=sb.align_context(a,d1,["d1_up","d1_eff"],"")
    St=states_from(a); up,dn=passage(h1)
    idx=np.where(dev)[0]; cut=idx[int(len(idx)*0.6)]; disc=dev&(np.arange(len(h1))<cut); conf=dev&(np.arange(len(h1))>=cut)
    # ---- b0/b1 ----
    hh1=hd.load()["H1"]; hh4,hd1=htf_cols(hd.load()["H4"],hd.load()["D1"])
    ha=hd.align_causal(hh1,hh4,["h4_up","h4_ext","h4_eff"],""); ha=hd.align_causal(ha,hd1,["d1_up","d1_eff"],"")
    St2=states_from(ha); up2,dn2=passage(hh1); b0=hh1["is_b0"].to_numpy(); b1=hh1["is_b1"].to_numpy()
    print("multi-TF state screen: HTF state -> H1 P(+100/-70) H48 lift. DEV(per-year,DISC,CONF) + CROSS-POP b0/b1.")
    for name in St:
        cond=np.nan_to_num(St[name].astype(float),nan=0).astype(bool); cond2=np.nan_to_num(St2[name].astype(float),nan=0).astype(bool)
        print(f"  {name}: N_dev={int((dev&cond).sum())}")
        for side in ("L","S"):
            ld,nc=lift(up,dn,side,dev,dev&cond)
            dl,_=lift(up,dn,side,disc,disc&cond); cl,_=lift(up,dn,side,conf,conf&cond)
            py=[]
            for y in (2021,2022,2023):
                m=dev&(yr==y)&cond
                py.append(lift(up,dn,side,dev&(yr==y),m)[0] if m.sum()>=40 else None)
            lb0,_=lift(up2,dn2,side,b0,b0&cond2); lb1,_=lift(up2,dn2,side,b1,b1&cond2)
            devstable=(abs(ld)>=0.03 and np.sign(dl)==np.sign(ld) and np.sign(cl)==np.sign(ld)
                       and all(np.sign(v)==np.sign(ld) for v in py if v is not None))
            crossstable=devstable and np.sign(lb0)==np.sign(ld) and np.sign(lb1)==np.sign(ld) and abs(lb0)>=0.02 and abs(lb1)>=0.02
            pys=" ".join(f"{y}:{('%.2f'%v) if v is not None else 'na'}" for y,v in zip((2021,2022,2023),py))
            flag=" <== CROSS_STABLE" if crossstable else (" (dev-stable)" if devstable else "")
            print(f"     {side}: DEVlift={ld:+.3f}(n{nc}) DISC={dl:+.2f} CONF={cl:+.2f} yr[{pys}] | b0={lb0:+.3f} b1={lb1:+.3f}{flag}")

if __name__=="__main__":
    main()
