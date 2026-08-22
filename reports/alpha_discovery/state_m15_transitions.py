"""state_m15_transitions.py — M15 TRANSITION family (§8). Causal A(t-8)->B(t) -> P(+70/-50) 8h lift, event-deduped,
with per-year + DISC/CONF + cross-era b0/b1 gate from the outset. Price-only, causal. Flags material cross-stable.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_m15_data as m15d
from state_path_m15 import passage_m15, Pm
from state_m15_discover import dedup
K=8
def feats(df):
    c=df["close"].to_numpy(); atr=df["atr"].to_numpy(); e20=df["ema20"].to_numpy(); atr_ma=df["atr_ma"].to_numpy(); eff=df["effic"].to_numpy()
    vr=atr/atr_ma; dist=(c-e20)/atr
    def lag(a): return pd.Series(a).shift(K).to_numpy()
    return dict(eff=eff,vr=vr,dist=dist,eff8=lag(eff),vr8=lag(vr),dist8=lag(dist))

def trans(F):
    e,v,d,e8,v8,d8=F["eff"],F["vr"],F["dist"],F["eff8"],F["vr8"],F["dist8"]
    return {
     "lowvol->exp":        ((v8<0.8)&(v>1.2),'L'),
     "lowvol->exp_S":      ((v8<0.8)&(v>1.2),'S'),
     "ineff->dirUp":       ((np.abs(e8)<0.15)&(e>0.4),'L'),
     "ineff->dirDn":       ((np.abs(e8)<0.15)&(e<-0.4),'S'),
     "dirUp->collapse":    ((e8>0.4)&(e<0.1),'S'),
     "dirDn->collapse":    ((e8<-0.4)&(e>-0.1),'L'),
     "highvol->stab":      ((v8>1.3)&(v<0.9),'L'),
     "highvol->stab_S":    ((v8>1.3)&(v<0.9),'S'),
     "extUp->pullback":    ((d8>1.5)&(d<0.8),'S'),
     "extDn->pullback":    ((d8<-1.5)&(d>-0.8),'L'),
    }

def main():
    m=sb.build_frames()["M15"]; dev=m["is_dev"].to_numpy(); yr=m["dt"].dt.year.to_numpy()
    ou,od,_,_=passage_m15(m); F=feats(m); T=trans(F)
    bL,_=Pm(ou,od,70,50,'L',32,dev&dedup(np.ones(len(m),bool))); bS,_=Pm(ou,od,70,50,'S',32,dev&dedup(np.ones(len(m),bool)))
    disc=(np.arange(len(m))< np.where(dev)[0][int(dev.sum()*0.6)]); conf=~disc
    h=m15d.build(verbose=False)["M15"]; b0=h["is_b0"].to_numpy(); b1=h["is_b1"].to_numpy()
    ou2,od2,_,_=passage_m15(h); F2=feats(h); T2=trans(F2)
    bb0={'L':Pm(ou2,od2,70,50,'L',32,b0&dedup(np.ones(len(h),bool)))[0],'S':Pm(ou2,od2,70,50,'S',32,b0&dedup(np.ones(len(h),bool)))[0]}
    bb1={'L':Pm(ou2,od2,70,50,'L',32,b1&dedup(np.ones(len(h),bool)))[0],'S':Pm(ou2,od2,70,50,'S',32,b1&dedup(np.ones(len(h),bool)))[0]}
    print(f"M15 TRANSITION family: P(+70/-50) 8h lift, event-deduped. DEV base L={bL:.3f} S={bS:.3f}")
    for name,(cond,side) in T.items():
        base=bL if side=='L' else bS; cond=np.nan_to_num(cond.astype(float),nan=0).astype(bool)
        cond2=np.nan_to_num(T2[name][0].astype(float),nan=0).astype(bool)
        dd=dev&dedup(cond); nE=int(dd.sum())
        if nE<40: print(f"  {name} {side}: EffN={nE}(thin)"); continue
        c,_=Pm(ou,od,70,50,side,32,dd); lift=c-base
        dl=Pm(ou,od,70,50,side,32,dev&disc&dedup(cond))[0]-Pm(ou,od,70,50,side,32,dev&disc&dedup(np.ones(len(m),bool)))[0]
        cl=Pm(ou,od,70,50,side,32,dev&conf&dedup(cond))[0]-Pm(ou,od,70,50,side,32,dev&conf&dedup(np.ones(len(m),bool)))[0]
        l0=Pm(ou2,od2,70,50,side,32,b0&dedup(cond2))[0]-bb0[side]; l1=Pm(ou2,od2,70,50,side,32,b1&dedup(cond2))[0]-bb1[side]
        py=[]
        for y in (2021,2022,2023):
            mm=dev&(yr==y); ee=mm&dedup(cond&mm); py.append(Pm(ou,od,70,50,side,32,ee)[0]-Pm(ou,od,70,50,side,32,mm&dedup(mm))[0] if ee.sum()>=25 else None)
        stable=(abs(lift)>=0.04 and np.sign(dl)==np.sign(lift) and np.sign(cl)==np.sign(lift) and np.sign(l0)==np.sign(lift) and np.sign(l1)==np.sign(lift) and abs(l0)>=0.02 and abs(l1)>=0.02)
        pys=" ".join(f"{y}:{('%.2f'%v) if v is not None else 'na'}" for y,v in zip((2021,2022,2023),py))
        print(f"  {name} {side}: lift={lift:+.3f}(EffN {nE}) DISC={dl:+.2f} CONF={cl:+.2f} yr[{pys}] | b0={l0:+.3f} b1={l1:+.3f}"+(" <== CROSS_STABLE" if stable else ""))

if __name__=="__main__":
    main()
