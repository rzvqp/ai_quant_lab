"""state_transitions.py — causal state-TRANSITION information screen (§8). A(t-6)->B(t) -> forward path lift.
Applies the ST-TREND-EXH lesson: evaluate per-year + DISC/CONF stability IN THE SAME screen (a transition is
'promising' ONLY if the lift is material AND same-sign across years AND holds DISC->CONF). Headline P(+100/-70)
H=48, LONG/SHORT. Causal, price-only, 2021-2023 native H1 DEV. Flagged transitions get cross-pop next.
"""
import numpy as np, pandas as pd
import swing_base as sb
from state_validate import passage, P

K=6
def stability(up,dn,side,cond,dev,yr,disc,conf):
    b,_=P(up,dn,100,70,side,48,dev); c,nc=P(up,dn,100,70,side,48,dev&cond)
    lift=c-b
    py={}
    for y in (2021,2022,2023):
        m=dev&(yr==y)&cond
        if m.sum()>=40:
            cy,_=P(up,dn,100,70,side,48,m); by,_=P(up,dn,100,70,side,48,dev&(yr==y)); py[y]=cy-by
        else: py[y]=None
    ld,_=P(up,dn,100,70,side,48,disc&cond); bd,_=P(up,dn,100,70,side,48,disc); dlift=ld-bd
    lc,_=P(up,dn,100,70,side,48,conf&cond); bc,_=P(up,dn,100,70,side,48,conf); clift=lc-bc
    pv=[v for v in py.values() if v is not None]
    stable=(abs(lift)>=0.03 and nc>=60 and len(pv)>=2 and all(np.sign(v)==np.sign(lift) for v in pv)
            and np.sign(dlift)==np.sign(lift) and np.sign(clift)==np.sign(lift))
    return lift,nc,py,dlift,clift,stable

def main():
    tfs=sb.build_frames(); h1=tfs["H1"]; dev=h1["is_dev"].to_numpy(); yr=h1["dt"].dt.year.to_numpy()
    tr=((h1["ema20"]-h1["ema50"])/h1["atr"]).to_numpy(); vr=(h1["atr"]/h1["atr_ma"]).to_numpy(); eff=h1["effic"].to_numpy()
    def lag(a,k): return pd.Series(a).shift(k).to_numpy()
    trK,vrK,effK=lag(tr,K),lag(vr,K),lag(eff,K)
    up,dn=passage(h1)
    idx=np.where(dev)[0]; cut=idx[int(len(idx)*0.6)]
    disc=dev&(np.arange(len(h1))<cut); conf=dev&(np.arange(len(h1))>=cut)
    T={
     "T1_comp->exp":     (vrK<0.9)&(vr>1.1),
     "T2_exp->stab":     (vrK>1.2)&(vr<1.0),
     "T3_upEff->drop":   (effK>0.4)&(eff<0.1),
     "T4_dnEff->drop":   (effK<-0.4)&(eff>-0.1),
     "T5_accept_up":     (np.abs(effK)<0.2)&(eff>0.4),
     "T6_accept_dn":     (np.abs(effK)<0.2)&(eff<-0.4),
     "T7_flip_dn->up":   (effK<-0.2)&(eff>0.2),
     "T8_flip_up->dn":   (effK>0.2)&(eff<-0.2),
     "T9_trend_weaken":  (trK>1.0)&(tr<trK-0.3),
    }
    print("state-TRANSITION screen (2021-2023 H1 DEV, headline P(+100/-70) H48). STABLE = |lift|>=.03 & per-year same-sign & DISC/CONF same-sign.")
    for name,cond in T.items():
        cond=np.where(np.isfinite(cond.astype(float)),cond,False)
        n=int((dev&cond).sum())
        print(f"  {name}: N={n}")
        for side in ("L","S"):
            lift,nc,py,dl,cl,stable=stability(up,dn,side,cond,dev,yr,disc,conf)
            pys=" ".join(f"{y}:{('%.3f'%v) if v is not None else 'na'}" for y,v in py.items())
            flag=" <== STABLE" if stable else ""
            print(f"     {side}: lift={lift:+.3f}(n{nc}) DISC={dl:+.3f} CONF={cl:+.3f} | yr[{pys}]{flag}")

if __name__=="__main__":
    main()
