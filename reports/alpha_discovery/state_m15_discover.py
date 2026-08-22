"""state_m15_discover.py — M15 univariate state information map (§6-7). Causal M15 states -> P(+70/-50) 8h lift,
LONG/SHORT separate, EVENT-DEDUP (raw vs effective-N, §15), per-year + DISC/CONF + cross-era b0/b1 stability.
Uses state_path_m15 engine. Price-only, causal. Flags material (|lift|>=0.04) cross-era-stable states.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_m15_data as m15d
from state_path_m15 import passage_m15, Pm

COOL=8  # ~2h event-dedup window
def feats(df):
    c=df["close"].to_numpy(); h=df["high"].to_numpy(); l=df["low"].to_numpy(); o=df["open"].to_numpy()
    atr=df["atr"].to_numpy(); e20=df["ema20"].to_numpy(); atr_ma=df["atr_ma"].to_numpy(); eff=df["effic"].to_numpy()
    hh=pd.Series(h).rolling(20).max().shift(1).to_numpy(); ll=pd.Series(l).rolling(20).min().shift(1).to_numpy()
    disp=(c-pd.Series(c).shift(6).to_numpy())/atr; vr=atr/atr_ma; vc=atr/pd.Series(atr).shift(8).to_numpy()
    body=np.where((h-l)>0,(c-o)/(h-l),0.0); pb=(hh-c)/atr; pos=np.where((hh-ll)>0,(c-ll)/(hh-ll),0.5)
    box=hh-ll; boxma=pd.Series(box).rolling(50).mean().shift(1).to_numpy()
    pl=pd.Series(np.abs(np.diff(c,prepend=c[0]))).rolling(20).sum().to_numpy()
    reff=np.where(pl>0,(c-pd.Series(c).shift(20).to_numpy())/pl,0.0)
    return dict(eff=eff,disp=disp,vr=vr,vc=vc,body=body,pb=pb,pos=pos,box=box,boxma=boxma,reff=reff)

def states(F):
    return {
     "eff_hi(>.4)":F["eff"]>0.4, "eff_lo(<-.4)":F["eff"]<-0.4,
     "disp_up(>1)":F["disp"]>1, "disp_dn(<-1)":F["disp"]<-1,
     "vol_hi(>1.3)":F["vr"]>1.3, "vol_lo(<0.8)":F["vr"]<0.8,
     "vc_rise(>1.2)":F["vc"]>1.2, "vc_fall(<0.85)":F["vc"]<0.85,
     "compress":(F["box"]<F["boxma"])&(F["vr"]<0.9),
     "body_up(>.5)":F["body"]>0.5, "body_dn(<-.5)":F["body"]<-0.5,
     "pb_deep(>1.5)":F["pb"]>1.5, "pos_hi(>.75)":F["pos"]>0.75, "pos_lo(<.25)":F["pos"]<0.25,
     "clean_up(reff>.5)":F["reff"]>0.5, "clean_dn(reff<-.5)":F["reff"]<-0.5,
    }

def dedup(mask,cool=COOL):
    idx=np.where(mask)[0]; out=[]; last=-10**9
    for i in idx:
        if i-last>=cool: out.append(i); last=i
    m=np.zeros(len(mask),bool); m[out]=True; return m

def main():
    m=sb.build_frames()["M15"]; dev=m["is_dev"].to_numpy(); yr=m["dt"].dt.year.to_numpy()
    ou,od,_,_=passage_m15(m); F=feats(m); St=states(F)
    baseL,_=Pm(ou,od,70,50,'L',32,dev&dedup(np.ones(len(m),bool)))
    baseS,_=Pm(ou,od,70,50,'S',32,dev&dedup(np.ones(len(m),bool)))
    idx=np.where(dev)[0]; cut=idx[int(len(idx)*0.6)]; disc=(np.arange(len(m))<cut); conf=(np.arange(len(m))>=cut)
    h=m15d.build(verbose=False)["M15"]; b0=h["is_b0"].to_numpy(); b1=h["is_b1"].to_numpy()
    ou2,od2,_,_=passage_m15(h); F2=feats(h); St2=states(F2)
    bb0L,_=Pm(ou2,od2,70,50,'L',32,b0&dedup(np.ones(len(h),bool))); bb0S,_=Pm(ou2,od2,70,50,'S',32,b0&dedup(np.ones(len(h),bool)))
    bb1L,_=Pm(ou2,od2,70,50,'L',32,b1&dedup(np.ones(len(h),bool))); bb1S,_=Pm(ou2,od2,70,50,'S',32,b1&dedup(np.ones(len(h),bool)))
    print(f"M15 STATE INFO MAP: P(+70/-50) 8h, event-deduped. DEV base L={baseL:.3f} S={baseS:.3f}  b0 L/S={bb0L:.2f}/{bb0S:.2f} b1 L/S={bb1L:.2f}/{bb1S:.2f}")
    for name in St:
        cd=np.nan_to_num(St[name].astype(float),nan=0).astype(bool); cd2=np.nan_to_num(St2[name].astype(float),nan=0).astype(bool)
        for side,base,b0b,b1b in (('L',baseL,bb0L,bb1L),('S',baseS,bb0S,bb1S)):
            dd=dev&dedup(cd); nE=int(dd.sum()); nRaw=int((dev&cd).sum())
            if nE<40: continue
            c,_=Pm(ou,od,70,50,side,32,dd); lift=c-base
            if abs(lift)<0.04: continue
            dl=Pm(ou,od,70,50,side,32,dev&disc&dedup(cd))[0]-Pm(ou,od,70,50,side,32,dev&disc&dedup(np.ones(len(m),bool)))[0]
            cl=Pm(ou,od,70,50,side,32,dev&conf&dedup(cd))[0]-Pm(ou,od,70,50,side,32,dev&conf&dedup(np.ones(len(m),bool)))[0]
            l0=Pm(ou2,od2,70,50,side,32,b0&dedup(cd2))[0]-b0b; l1=Pm(ou2,od2,70,50,side,32,b1&dedup(cd2))[0]-b1b
            py=[]
            for y in (2021,2022,2023):
                mm=dev&(yr==y); ee=mm&dedup(cd&mm)
                py.append(Pm(ou,od,70,50,side,32,ee)[0]-Pm(ou,od,70,50,side,32,mm&dedup(mm))[0] if ee.sum()>=25 else None)
            stable=(np.sign(dl)==np.sign(lift) and np.sign(cl)==np.sign(lift) and np.sign(l0)==np.sign(lift) and np.sign(l1)==np.sign(lift) and abs(l0)>=0.02 and abs(l1)>=0.02)
            pys=" ".join(f"{y}:{('%.2f'%v) if v is not None else 'na'}" for y,v in zip((2021,2022,2023),py))
            print(f"  {name} {side}: lift={lift:+.3f} (Eff-N={nE}/raw{nRaw}) DISC={dl:+.2f} CONF={cl:+.2f} yr[{pys}] | b0={l0:+.3f} b1={l1:+.3f}"+(" <== CROSS_STABLE" if stable else ""))

if __name__=="__main__":
    main()
