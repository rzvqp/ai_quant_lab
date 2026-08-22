"""HF4 (historical, bearish) — TRANSITION-onset SHORT: first H4 bar flipping to TREND_DOWN (structural regime
transition, not continuation), in a causal D1 non-up context, on b0/b1. Distinct mechanism class (§8 transition).
Structural stop above recent swing high. Path-first (§15). Causal hist_data. DISCOVERY_CONSUMED -> NOT validation.
"""
import numpy as np, pandas as pd
import hist_data as hd, swing_base as sb
from frontier_hist1 import refeat
from frontier_hist3 import emit

H=42; WSTOP=10
def onset(reg,target):
    r=np.asarray(reg,object); on=np.zeros(len(r),bool); on[1:]=(r[1:]==target)&(r[:-1]!=target); return on

def main():
    tfs=hd.load(); h4=refeat(tfs["H4"]); d1=refeat(tfs["D1"]).copy()
    d1["d1_dn"]=(d1["ema20"]<d1["ema50"]).astype(float); d1["d1_up"]=(d1["ema20"]>d1["ema50"]).astype(float)
    al=hd.align_causal(h4,d1,["d1_dn","d1_up"],""); d1_dn=(al["d1_dn"].to_numpy()>0.5); d1_up=(al["d1_up"].to_numpy()>0.5)
    o=h4["open"].to_numpy(); h=h4["high"].to_numpy(); l=h4["low"].to_numpy(); atr=h4["atr"].to_numpy()
    reg=h4["regime"].to_numpy(); disc=h4["is_disc"].to_numpy(); seg=h4["seg"].to_numpy()
    sameW=np.zeros(len(h4),bool); sameW[WSTOP:]=(seg[WSTOP:]==seg[:-WSTOP])
    swh=pd.Series(h).rolling(WSTOP).max().to_numpy(); swl=pd.Series(l).rolling(WSTOP).min().to_numpy()
    print(f"HF4 transition-onset  H4 DISC bars={int(disc.sum())} (b0+b1)")
    # SHORT: TREND_DOWN onset while D1 not-up
    sigS=onset(reg,"TREND_DOWN") & (~d1_up) & disc & sameW
    rawS=[i for i in np.where(sigS)[0] if i+1<len(h4)]
    evS=sb.dedup_events(np.array(rawS),cooldown=WSTOP)
    riskS=np.array([(swh[i]+0.2*atr[i])-o[i+1] for i in evS]); ok=np.isfinite(riskS)&(riskS>0); evS,riskS=evS[ok],riskS[ok]
    print(f"  SHORT TREND_DOWN onset (D1 not-up): events={len(evS)}")
    emit(h4,evS,-1,riskS,"HF4 transition-short")
    # LONG ref: TREND_UP onset while D1 not-down
    sigL=onset(reg,"TREND_UP") & (~d1_dn) & disc & sameW
    rawL=[i for i in np.where(sigL)[0] if i+1<len(h4)]
    evL=sb.dedup_events(np.array(rawL),cooldown=WSTOP)
    riskL=np.array([o[i+1]-(swl[i]-0.2*atr[i]) for i in evL]); ok=np.isfinite(riskL)&(riskL>0); evL,riskL=evL[ok],riskL[ok]
    print(f"  LONG TREND_UP onset (ref only): events={len(evL)}")
    emit(h4,evL,+1,riskL,"HF4 transition-long(ref)")

if __name__=="__main__":
    main()
