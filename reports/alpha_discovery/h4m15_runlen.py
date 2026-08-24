"""h4m15_runlen.py — Mandate ...H4-M15-PATH-SHAPE..., §5-8-10 family 1: M15 directional RUN-LENGTH +
PERSISTENCE-vs-ALTERNATION (windows 4/8) conditional on causal H4 parent state. Lift of P(+70/-50) & P(+100/-70)
vs the SAME-H4-STATE M15 base rate (per era), LONG/SHORT separate, event-deduped, same-H4-state cross-era gate
(DEV DISC/CONF + per-year + b0 + b1). Interpretable descriptors only (§7). Flags material cross-era-stable cells.
Economic hypotheses: UP-state M15 down-run = pullback -> LONG continuation; DOWN-state up-run = pullback -> SHORT;
persistent M15 path aligned w/ H4 = momentum; alternation = avoidance.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_m15_data as m15d
from state_regime import regime
from state_path_m15 import passage_m15, Pm
from state_m15_discover import dedup
from h4_parent import align_h4
COOL=8; H=32
STATES=["UP","DOWN","QUIET","CHOP","TRANSITION"]
TARGETS=[(70,50),(100,70)]

def descr(df):
    c=df["close"].to_numpy(); d=np.sign(np.diff(c,prepend=c[0]))
    run=np.zeros(len(c))
    for i in range(1,len(c)):
        if d[i]==0: run[i]=0
        elif d[i]==d[i-1]: run[i]=run[i-1]+d[i]
        else: run[i]=d[i]
    def pe(W):
        num=c-pd.Series(c).shift(W).to_numpy(); den=pd.Series(np.abs(np.diff(c,prepend=c[0]))).rolling(W).sum().to_numpy()
        return np.where(den>0,num/den,0.0)
    pe8=pe(8); pe4=pe(4)
    return {
      "runUp>=3": run>=3, "runUp>=4": run>=4,
      "runDn>=3": run<=-3, "runDn>=4": run<=-4,
      "persistUp(pe8>.5)": pe8>=0.5, "persistDn(pe8<-.5)": pe8<=-0.5,
      "altern(|pe8|<.2)": np.abs(pe8)<0.2, "cleanUp(pe4>.6)": pe4>=0.6, "cleanDn(pe4<-.6)": pe4<=-0.6,
    }

def base_in_state(ou,od,regc,uniq,mask,r,X,Y,side):
    code=uniq.index(r); sm=mask&(regc==code)&dedup(mask&(regc==code),COOL)
    return Pm(ou,od,X,Y,side,H,sm)[0], int(sm.sum())

def cond_lift(ou,od,regc,uniq,mask,r,cond,X,Y,side):
    code=uniq.index(r); cm=mask&(regc==code)&cond; dd=cm&dedup(cm,COOL); nE=int(dd.sum())
    if nE<40: return None,nE
    return Pm(ou,od,X,Y,side,H,dd)[0], nE

def main():
    print("FAMILY 1: M15 run-length/persistence conditional on H4 state. P lift vs SAME-H4-STATE base, deduped, cross-era.")
    tfs=sb.build_frames(); m=tfs["M15"]; h4=tfs["H4"]; dev=m["is_dev"].to_numpy(); yr=m["dt"].dt.year.to_numpy()
    regc,hidx,uniq=align_h4(m,h4,sb.align_context); ou,od,_,_=passage_m15(m); D=descr(m)
    hh=m15d.build(verbose=False); hm=hh["M15"]; hh4=hh["H4"]; b0=hm["is_b0"].to_numpy(); b1=hm["is_b1"].to_numpy()
    regc2,hidx2,uniq2=align_h4(hm,hh4,m15d.align_causal); ou2,od2,_,_=passage_m15(hm); D2=descr(hm)
    disc=np.zeros(len(m),bool); idx=np.where(dev)[0]; disc[idx[:int(len(idx)*0.6)]]=True; conf=dev&~disc
    for r in STATES:
        if r not in uniq: continue
        printed_hdr=False
        for dname,cond in D.items():
            cond=np.nan_to_num(cond.astype(float),nan=0).astype(bool); cond2=np.nan_to_num(D2[dname].astype(float),nan=0).astype(bool)
            for (X,Y) in TARGETS:
                for side in ('L','S'):
                    base,nb=base_in_state(ou,od,regc,uniq,dev,r,X,Y,side)
                    c,nE=cond_lift(ou,od,regc,uniq,dev,r,cond,X,Y,side)
                    if c is None: continue
                    lift=c-base
                    if abs(lift)<0.03: continue
                    dl=None; cl=None
                    cd,_=cond_lift(ou,od,regc,uniq,disc,r,cond,X,Y,side); bd,_=base_in_state(ou,od,regc,uniq,disc,r,X,Y,side)
                    cc,_=cond_lift(ou,od,regc,uniq,conf,r,cond,X,Y,side); bc,_=base_in_state(ou,od,regc,uniq,conf,r,X,Y,side)
                    dl=(cd-bd) if cd is not None else None; cl=(cc-bc) if cc is not None else None
                    l0=None; l1=None
                    if r in uniq2:
                        c0,n0=cond_lift(ou2,od2,regc2,uniq2,b0,r,cond2,X,Y,side); b0b,_=base_in_state(ou2,od2,regc2,uniq2,b0,r,X,Y,side)
                        c1,n1=cond_lift(ou2,od2,regc2,uniq2,b1,r,cond2,X,Y,side); b1b,_=base_in_state(ou2,od2,regc2,uniq2,b1,r,X,Y,side)
                        l0=(c0-b0b) if c0 is not None else None; l1=(c1-b1b) if c1 is not None else None
                    py=[]
                    for y in (2021,2022,2023):
                        mm=dev&(yr==y); cy,ny=cond_lift(ou,od,regc,uniq,mm,r,cond,X,Y,side); by,_=base_in_state(ou,od,regc,uniq,mm,r,X,Y,side)
                        py.append((cy-by) if cy is not None else None)
                    stable=(abs(lift)>=0.04 and dl is not None and cl is not None and l0 is not None and l1 is not None
                            and np.sign(dl)==np.sign(lift) and np.sign(cl)==np.sign(lift)
                            and np.sign(l0)==np.sign(lift) and np.sign(l1)==np.sign(lift) and abs(l0)>=0.02 and abs(l1)>=0.02)
                    if not printed_hdr: print(f"\n[H4={r}]  (base rates deduped in-state)"); printed_hdr=True
                    pys=" ".join(f"{y}:{('%+.2f'%v) if v is not None else 'na'}" for y,v in zip((2021,2022,2023),py))
                    ds=" ".join(f"{k}={('%+.2f'%v) if v is not None else 'na'}" for k,v in (("D",dl),("C",cl),("b0",l0),("b1",l1)))
                    print(f"   {dname:18s} {side} +{X}/-{Y}: base={base:.2f} lift={lift:+.3f}(EffN {nE}) {ds} yr[{pys}]"+(" <== CROSS_STABLE" if stable else ""))

if __name__=="__main__":
    main()
