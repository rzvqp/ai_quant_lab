"""HF5 (historical) — counter-trend LONG mean-reversion (genuinely different from bearish-short & trend-beta):
 A) capitulation LONG: oversold flush (close far below H4 EMA20 in ATR units) then first up-close -> long bounce.
 B) down-spike reversion LONG: big down expansion bar (close lower-third) faded long (F6 showed 2021-23 spikes REVERT).
Tested on b0/b1 (incl 2013 bear, deeper flushes than 2021-23). Path-first (§15). Causal hist_data. NOT validation.
"""
import numpy as np, pandas as pd
import hist_data as hd, swing_base as sb
from frontier_hist1 import refeat
from frontier_hist3 import emit

def main():
    tfs=hd.load(); h4=refeat(tfs["H4"]); d1=refeat(tfs["D1"]).copy(); d1["d1_dn"]=(d1["ema20"]<d1["ema50"]).astype(float)
    d1_dn=(hd.align_causal(h4,d1,["d1_dn"],"")["d1_dn"].to_numpy()>0.5)
    o=h4["open"].to_numpy(); h=h4["high"].to_numpy(); l=h4["low"].to_numpy(); c=h4["close"].to_numpy()
    e20=h4["ema20"].to_numpy(); atr=h4["atr"].to_numpy(); atr_ma=h4["atr_ma"].to_numpy()
    disc=h4["is_disc"].to_numpy(); seg=h4["seg"].to_numpy()
    same=np.zeros(len(h4),bool); same[3:]=(seg[3:]==seg[:-3])
    ll3=pd.Series(l).rolling(3).min().to_numpy()
    ext=(c-e20)/atr
    tr_=np.maximum(h-l,np.maximum(np.abs(h-np.roll(c,1)),np.abs(l-np.roll(c,1))))
    rng=h-l; closepos=np.where(rng>0,(c-l)/rng,0.5)
    print(f"HF5 counter-trend LONG reversion  H4 DISC bars={int(disc.sum())} (b0+b1)")

    # A) capitulation LONG: oversold + up-close reversal
    for E in (2.0,2.5):
        osold=np.isfinite(ext)&(ext<-E)
        sig=osold&(c>o)&disc&same
        for tag,ctx in (("ALL",np.ones(len(h4),bool)),("D1down",d1_dn)):
            cond=sig&ctx
            raw=[i for i in np.where(cond)[0] if i+1<len(h4)]
            ev=sb.dedup_events(np.array(raw),cooldown=3)
            risk=np.array([o[i+1]-(ll3[i]-0.3*atr[i]) for i in ev]); ok=np.isfinite(risk)&(risk>0); ev,risk=ev[ok],risk[ok]
            print(f"  A capitulation-LONG E={E} [{tag}]: events={len(ev)}")
            emit(h4,ev,+1,risk,f"A-capLONG E={E} [{tag}]")

    # B) down-spike reversion LONG
    sigB=(tr_>1.8*atr_ma)&(c<o)&(closepos<0.33)&disc&same
    raw=[i for i in np.where(sigB)[0] if i+1<len(h4)]
    evB=sb.dedup_events(np.array(raw),cooldown=3)
    riskB=np.array([o[i+1]-(l[i]-0.3*atr[i]) for i in evB]); ok=np.isfinite(riskB)&(riskB>0); evB,riskB=evB[ok],riskB[ok]
    print(f"  B down-spike-reversion-LONG: events={len(evB)}")
    emit(h4,evB,+1,riskB,"B down-spike-rev-LONG")

if __name__=="__main__":
    main()
