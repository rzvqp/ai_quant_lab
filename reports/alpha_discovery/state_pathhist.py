"""state_pathhist.py — PATH-HISTORY state family (§5, §7F). Causal states from the REALIZED path before the
decision (bars <= t): recent MFE/MAE-so-far, realized efficiency, pullback-depth-from-recent-extreme,
position-in-recent-range, up/down excursion asymmetry, time-since-new-extreme. Screen each for P(+100/-70) H48
lift LONG/SHORT with per-year + DISC/CONF stability IN the screen. Causal, price-only, 2021-2023 native H1 DEV.
"""
import numpy as np, pandas as pd
import swing_base as sb
from state_validate import passage, P
from state_transitions import stability

W=24
def main():
    tfs=sb.build_frames(); h1=tfs["H1"]; dev=h1["is_dev"].to_numpy(); yr=h1["dt"].dt.year.to_numpy()
    c=h1["close"].to_numpy(); h=h1["high"].to_numpy(); l=h1["low"].to_numpy(); atr=h1["atr"].to_numpy()
    rhh=pd.Series(h).rolling(W).max().to_numpy(); rll=pd.Series(l).rolling(W).min().to_numpy()
    cW=pd.Series(c).shift(W).to_numpy()
    pathlen=pd.Series(np.abs(np.diff(c,prepend=c[0]))).rolling(W).sum().to_numpy()
    reff=np.where(pathlen>0,(c-cW)/pathlen,0.0)                 # realized directional efficiency (signed)
    pb_hi=(rhh-c)/atr                                            # pullback depth below recent high (>=0)
    pos=np.where((rhh-rll)>0,(c-rll)/(rhh-rll),0.5)             # position in recent range [0..1]
    tmfe=(rhh-cW)/atr; tmae=(cW-rll)/atr; asym=tmfe-tmae        # trailing up vs down excursion
    # new W-high flag + bars since
    nh=h>=pd.Series(h).rolling(W).max().shift(1).to_numpy(); bsh=np.zeros(len(c))
    for i in range(1,len(c)): bsh[i]=0 if nh[i] else bsh[i-1]+1
    up,dn=passage(h1)
    idx=np.where(dev)[0]; cut=idx[int(len(idx)*0.6)]
    disc=dev&(np.arange(len(h1))<cut); conf=dev&(np.arange(len(h1))>=cut)
    C={
     "clean_up (reff>.5)":            reff>0.5,
     "clean_dn (reff<-.5)":           reff<-0.5,
     "shallowPB_up (reff>.3&pb<.5)":  (reff>0.3)&(pb_hi<0.5),
     "deepPB_up (reff>.2&pb>2)":      (reff>0.2)&(pb_hi>2.0),
     "lowMAE_up (reff>.3&tmae<1)":    (reff>0.3)&(tmae<1.0),
     "highAsym_up (asym>2)":          asym>2.0,
     "freshHigh (new 24h high)":      nh,
     "stale_up (reff>.2&bsh>18)":     (reff>0.2)&(bsh>18),
     "bounce_dn (reff<-.2&pos>.8)":   (reff<-0.2)&(pos>0.8),
     "cleanDn_lowMFE (reff<-.3&tmfe<1)": (reff<-0.3)&(tmfe<1.0),
    }
    print("PATH-HISTORY state screen (2021-2023 H1 DEV, P(+100/-70) H48). STABLE=|lift|>=.03 & per-year same-sign & DISC/CONF same-sign.")
    for name,cond in C.items():
        cond=np.nan_to_num(cond.astype(float),nan=0.0).astype(bool)
        print(f"  {name}: N={int((dev&cond).sum())}")
        for side in ("L","S"):
            lift,nc,py,dl,cl,stable=stability(up,dn,side,cond,dev,yr,disc,conf)
            pys=" ".join(f"{y}:{('%.3f'%v) if v is not None else 'na'}" for y,v in py.items())
            print(f"     {side}: lift={lift:+.3f}(n{nc}) DISC={dl:+.3f} CONF={cl:+.3f} | yr[{pys}]"+(" <== STABLE" if stable else ""))

if __name__=="__main__":
    main()
