"""batch_i_scan.py — BROAD DISCOVERY v2, Batch I: OBSERVATIONAL event-ordering / conditional-path-shape scan.
For the last K=6 bars, characterize the micro-path causally by WHERE its extreme formed (early vs late) crossed with
recent drift, then measure forward directional asymmetry asym=P(+70/-50 L)-P(+70/-50 S) per archetype, cross-era.
Tests whether ORDERING carries directional info beyond drift/state (R20 said single states don't). Info-only; causal;
no P&L clustering. A material+stable archetype -> predeclare a strategy.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_m15_data as m15d
from state_path_m15 import passage_m15, Pm
H=32; K=6

def pathfeat(fr):
    c=fr["close"].to_numpy(); atr=fr["atr"].to_numpy(); h=fr["high"].to_numpy(); l=fr["low"].to_numpy()
    drift=(c-pd.Series(c).shift(K).to_numpy())/atr
    amax=pd.Series(h).rolling(K).apply(np.argmax,raw=True).to_numpy()   # 0=oldest .. K-1=newest: where window high formed
    amin=pd.Series(l).rolling(K).apply(np.argmin,raw=True).to_numpy()
    return drift, amax, amin

# archetypes: (name, predicate(drift,amax,amin))
ARCH=[
 ("up_high_late",   lambda d,ax,an: (d>0.5)&(ax>=K-2)),   # momentum up, high still forming
 ("up_high_early",  lambda d,ax,an: (d>0.5)&(ax<=1)),     # up drift but high formed early -> stalling (ordering)
 ("dn_low_late",    lambda d,ax,an: (d<-0.5)&(an>=K-2)),  # momentum down
 ("dn_low_early",   lambda d,ax,an: (d<-0.5)&(an<=1)),    # down drift but low formed early -> stalling
 ("up_low_late",    lambda d,ax,an: (d>0.5)&(an>=K-2)),   # up drift but freshest bar made the low -> deep pullback in uptrend
 ("dn_high_late",   lambda d,ax,an: (d<-0.5)&(ax>=K-2)),  # down drift but freshest bar made the high -> bounce in downtrend
]

def main():
    print(f"Batch I OBSERVATIONAL event-ordering scan. asym=P(+70/-50 L)-P(+70/-50 S) per archetype, cross-era. H={H//4}h. Material=|asym|>=0.05 same-sign all eras.")
    hm=m15d.build(verbose=False)["M15"]; sm=sb.build_frames()["M15"]
    FR={"hist":hm,"sb":sm}; PSG={k:passage_m15(v) for k,v in FR.items()}; PF={k:pathfeat(v) for k,v in FR.items()}
    eras=[("b0","hist","is_b0"),("b1","hist","is_b1"),("DEV","sb","is_dev"),("CAL","sb","is_cal")]
    for name,pred in ARCH:
        cells=[]; signs=[]
        for tag,fk,mk in eras:
            fr=FR[fk]; ou,od,_,_=PSG[fk]; d,ax,an=PF[fk]
            m=fr[mk].to_numpy()&np.nan_to_num(pred(d,ax,an).astype(float),nan=0).astype(bool)&np.isfinite(d)
            nE=int(m.sum())
            if nE<40: cells.append(f"{tag}:n{nE}(thin)"); signs.append(0); continue
            L=Pm(ou,od,70,50,'L',H,m)[0]; S=Pm(ou,od,70,50,'S',H,m)[0]; a=L-S
            cells.append(f"{tag}:{a:+.2f}(n{nE})"); signs.append(np.sign(a) if abs(a)>=0.05 else 0)
        nz=[s for s in signs if s!=0]; stable=" <== MATERIAL+STABLE" if (len(nz)>=3 and len(set(nz))==1) else ""
        print(f"  {name:14s}: "+"  ".join(cells)+stable)

if __name__=="__main__":
    main()
