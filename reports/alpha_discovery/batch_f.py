"""batch_f.py — BROAD DISCOVERY v2, Batch F. NOVEL state/sequence mechanisms distinct from immediate
momentum/reversal (CEO axes: DELAYED RESPONSE, FAILED FOLLOW-THROUGH, EVENT ORDERING, TIME-SINCE-EVENT):
- FAILED_FT: a breakout that STALLS (no follow-through within K bars) -> DELAYED reversal (distinct from S2 immediate).
- ACCEL_EXH: 3 consecutive EXPANDING-range same-dir bars (climax/acceleration) -> exhaustion fade (distinct from streak-fade which used close-direction only).
- DELAYED_RETEST: breakout then a DELAYED pullback that holds the level -> resume (S3 with an explicit delayed retest, not immediate).
All causal (decision after the observation window). M15, ratified engine. Positives MUST pass §30 vs S5.
"""
import numpy as np, pandas as pd, bscreen as bs
from batch_a import _mk

def failed_ft(fr, side, K=6, W=20):
    h=fr["high"].to_numpy(); l=fr["low"].to_numpy(); c=fr["close"].to_numpy(); o=fr["open"].to_numpy(); atr=fr["atr"].to_numpy(); n=len(fr)
    sig=[]; st=[]
    if side<0:
        lvl=pd.Series(h).rolling(W).max().shift(1).to_numpy(); brk=np.where(np.nan_to_num((c>lvl).astype(float),nan=0).astype(bool))[0]
        for i in brk:
            j=min(i+K,n-1)
            if j<=i: continue
            if h[i+1:j+1].max() < c[i]+0.5*atr[i]: sig.append(j); st.append(h[i:j+1].max())
    else:
        lvl=pd.Series(l).rolling(W).min().shift(1).to_numpy(); brk=np.where(np.nan_to_num((c<lvl).astype(float),nan=0).astype(bool))[0]
        for i in brk:
            j=min(i+K,n-1)
            if j<=i: continue
            if l[i+1:j+1].min() > c[i]-0.5*atr[i]: sig.append(j); st.append(l[i:j+1].min())
    sig=np.array(sig,int); st=np.array(st,float)
    if len(sig)==0: return np.array([],int),np.array([],float)
    keep=sig<n-1; sig=sig[keep]; st=st[keep]; entry=o[sig+1]; return sig,np.abs(entry-st)

def accel_exh(fr, side):
    h=fr["high"].to_numpy(); l=fr["low"].to_numpy(); c=fr["close"].to_numpy(); o=fr["open"].to_numpy()
    rng=h-l; exp=rng>np.roll(rng,1); up=c>o; dn=c<o
    run3=lambda m: (pd.Series(m.astype(int)).rolling(3).sum()>=3).to_numpy()
    if side<0: cond=run3(exp&up); stop=pd.Series(h).rolling(3).max().to_numpy()
    else:      cond=run3(exp&dn); stop=pd.Series(l).rolling(3).min().to_numpy()
    return _mk(np.nan_to_num(cond.astype(float),nan=0).astype(bool),fr,stop,side)

def delayed_retest(fr, side, K=8, W=12):
    h=fr["high"].to_numpy(); l=fr["low"].to_numpy(); c=fr["close"].to_numpy(); o=fr["open"].to_numpy(); atr=fr["atr"].to_numpy(); n=len(fr)
    sig=[]; st=[]
    if side>0:
        lvl=pd.Series(h).rolling(W).max().shift(1).to_numpy(); brk=np.where(np.nan_to_num((c>lvl).astype(float),nan=0).astype(bool))[0]
        for i in brk:
            for j in range(i+1,min(i+K,n-1)+1):
                if l[j]<=lvl[i] and c[j]>lvl[i]: sig.append(j); st.append(lvl[i]-0.5*atr[i]); break
    else:
        lvl=pd.Series(l).rolling(W).min().shift(1).to_numpy(); brk=np.where(np.nan_to_num((c<lvl).astype(float),nan=0).astype(bool))[0]
        for i in brk:
            for j in range(i+1,min(i+K,n-1)+1):
                if h[j]>=lvl[i] and c[j]<lvl[i]: sig.append(j); st.append(lvl[i]+0.5*atr[i]); break
    sig=np.array(sig,int); st=np.array(st,float)
    if len(sig)==0: return np.array([],int),np.array([],float)
    keep=sig<n-1; sig=sig[keep]; st=st[keep]; entry=o[sig+1]; return sig,np.abs(entry-st)

HYPS=[
 dict(name="FAILED_FT_S",info="failed-follow-through",side=-1,rr=2.0,horizon=48,signal=lambda f:failed_ft(f,-1)),
 dict(name="FAILED_FT_L",info="failed-follow-through",side=1,rr=2.0,horizon=48,signal=lambda f:failed_ft(f,1)),
 dict(name="ACCEL_EXH_S",info="acceleration-exhaustion",side=-1,rr=2.0,horizon=48,signal=lambda f:accel_exh(f,-1)),
 dict(name="ACCEL_EXH_L",info="acceleration-exhaustion",side=1,rr=2.0,horizon=48,signal=lambda f:accel_exh(f,1)),
 dict(name="DELAYED_RETEST_L",info="delayed-retest",side=1,rr=2.0,horizon=48,signal=lambda f:delayed_retest(f,1)),
 dict(name="DELAYED_RETEST_S",info="delayed-retest",side=-1,rr=2.0,horizon=48,signal=lambda f:delayed_retest(f,-1)),
]

if __name__=="__main__":
    bs.run_batch(HYPS,title="F (novel state/sequence mechanisms)")
