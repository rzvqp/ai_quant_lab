"""morph_features.py — CAUSAL morphology feature dictionary (ALPHA-XAUUSD-CAUSAL-MORPHOLOGY-DISCOVERY-001).
Event-time (per bar), price-derived, ATR-normalized, ZERO future information (firewall §1). Space A = intraday
short structure, lookback K bars on M15. Bounded & interpretable (§16), NOT a feature soup. Each feature named.
"""
import numpy as np, pandas as pd
K=8
NAMES=["disp","effic","pathlen","hi_pos","lo_pos","rng_trend","body_frac","alternation","retr","vol_state"]

def feats(fr, K=K):
    o=fr["open"].to_numpy(); c=fr["close"].to_numpy(); h=fr["high"].to_numpy(); l=fr["low"].to_numpy()
    atr=fr["atr"].to_numpy(); atrm=fr["atr_ma"].to_numpy(); n=len(fr)
    S=lambda a,k: pd.Series(a).shift(k).to_numpy(); R=lambda a,w: pd.Series(a).rolling(w)
    disp=(c-S(c,K))/atr
    dc=np.abs(c-S(c,1)); pathlen=R(dc,K).sum().to_numpy()/atr
    net=(c-S(c,K)); path=R(dc,K).sum().to_numpy(); effic=np.where(path>1e-9,net/path,0.0)
    hi_pos=R(h,K).apply(np.argmax,raw=True).to_numpy()/(K-1)
    lo_pos=R(l,K).apply(np.argmin,raw=True).to_numpy()/(K-1)
    rng=h-l; rec=R(rng,K//2).mean().to_numpy(); old=S(R(rng,K//2).mean().to_numpy(),K//2)
    rng_trend=np.where(old>1e-9,rec/old,1.0)
    body=np.abs(c-o); body_frac=R(body,K).mean().to_numpy()/np.maximum(R(rng,K).mean().to_numpy(),1e-9)
    r=c-S(c,1); sg=np.sign(r); alt=(sg!=S(sg,1)).astype(float); alternation=R(alt,K).mean().to_numpy()
    mx=R(h,K).max().to_numpy(); mn=R(l,K).min().to_numpy()
    retr=np.where(net>=0,(mx-c)/atr,(c-mn)/atr)
    vol_state=atr/atrm
    X=np.column_stack([disp,effic,pathlen,hi_pos,lo_pos,rng_trend,body_frac,alternation,retr,vol_state])
    ok=np.isfinite(X).all(1)
    return X, ok
