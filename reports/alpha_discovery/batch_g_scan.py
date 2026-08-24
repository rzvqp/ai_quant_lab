"""batch_g_scan.py — BROAD DISCOVERY v2, Batch G: OBSERVATIONAL information-first scan (CEO: OBSERVE->HYPOTHESIZE).
For a panel of NOVEL CAUSAL state variables, measure the forward-path DIRECTIONAL ASYMMETRY
asym = P(+70/-50 LONG) - P(+70/-50 SHORT) per tercile, cross-era (b0/b1/DEV/CAL). A state whose asym is MATERIAL
(|asym|>=0.05) and SAME-SIGN across eras = a directional-lean mechanism candidate to predeclare+test. Causal states
only; NO P&L clustering, NO outcome mining. Info measure only (not a strategy).
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_m15_data as m15d
from state_path_m15 import passage_m15, Pm
from batch_a import _hr_day
H=32

def features(fr):
    c=fr["close"].to_numpy(); atr=fr["atr"].to_numpy(); h=fr["high"].to_numpy(); l=fr["low"].to_numpy(); n=len(fr)
    sma50=pd.Series(c).rolling(50).mean().shift(1).to_numpy(); ext=(c-sma50)/atr
    net=c-pd.Series(c).shift(20).to_numpy(); path=pd.Series(np.abs(np.diff(c,prepend=c[0]))).rolling(20).sum().shift(1).to_numpy()
    eff=np.where(path>0,net/path,np.nan)
    hr,day,_=_hr_day(fr); dfd=pd.DataFrame({"day":day,"h":h,"l":l})
    dhi=dfd.groupby("day")["h"].cummax().to_numpy(); dlo=dfd.groupby("day")["l"].cummin().to_numpy()
    daypos=(c-dlo)/np.where((dhi-dlo)>0,(dhi-dlo),np.nan)
    hh=pd.Series(h).rolling(20).max().shift(1).to_numpy(); newhigh=h>hh
    age=np.zeros(n); cnt=0
    for i in range(n):
        cnt=0 if newhigh[i] else cnt+1; age[i]=cnt
    return {"ext":ext,"eff":eff,"daypos":daypos,"agehigh":age}

def main():
    print(f"Batch G OBSERVATIONAL info-scan. asym=P(+70/-50 L)-P(+70/-50 S) per tercile, cross-era. H={H//4}h. Material=|asym|>=0.05 same-sign all eras.")
    hm=m15d.build(verbose=False)["M15"]; sm=sb.build_frames()["M15"]
    FR={"hist":hm,"sb":sm}; PSG={k:passage_m15(v) for k,v in FR.items()}; FT={k:features(v) for k,v in FR.items()}
    eras=[("b0","hist","is_b0"),("b1","hist","is_b1"),("DEV","sb","is_dev"),("CAL","sb","is_cal")]
    for fname in ["ext","eff","daypos","agehigh"]:
        allv=np.concatenate([FT[k][fname][np.isfinite(FT[k][fname])] for k in FR])
        q=np.nanquantile(allv,[0.33,0.66]); bins=[("lo",-np.inf,q[0]),("mid",q[0],q[1]),("hi",q[1],np.inf)]
        print(f"\n=== {fname} (terciles @ {q[0]:.2f},{q[1]:.2f}) ===")
        for bn,lo,hi in bins:
            cells=[]; stable=None
            for tag,fk,mk in eras:
                fr=FR[fk]; ou,od,_,_=PSG[fk]; v=FT[fk][fname]; m=fr[mk].to_numpy()&(v>=lo)&(v<hi)&np.isfinite(v)
                nE=int(m.sum())
                if nE<40: cells.append(f"{tag}:n{nE}(thin)"); continue
                L=Pm(ou,od,70,50,'L',H,m)[0]; S=Pm(ou,od,70,50,'S',H,m)[0]; a=L-S
                cells.append(f"{tag}:{a:+.2f}(L{L:.2f}/S{S:.2f})")
                stable=a if stable is None else (a if (np.sign(a)==np.sign(stable) and abs(a)<abs(stable)) else stable)
            flag=" <== MATERIAL+STABLE" if (stable is not None and abs(stable)>=0.05) else ""
            print(f"  {bn:4s}: "+"  ".join(cells)+flag)

if __name__=="__main__":
    main()
