"""frontier_l.py — FRONTIER L: FAILED-AUCTION REJECTION at a fresh extreme (R26 lens: direction-RESOLVING structural
event with path-survival). PREREGISTERED: event = price prints a NEW N-bar high but the bar CLOSES in the bottom 30%
of its range (rejection wick) with a meaningful range -> SHORT (auction failed at the fresh high; liquidity swept, path
behind). Mirror: new N-bar low + close in top 30% -> LONG. Direction resolved by the rejection STRUCTURE, not predicted
from state. Structural stop = the rejected extreme (bar high/low). Distinct from streak-fade (close-dir) / ACCEL_EXH
(expanding-range) / prior-day fade (Batch A). Ratified sb screen, STRESS, cross-era b0/b1/DEV/CAL. Info-first + tradeable.
Predeclared bar: SURVIVOR = all eras (N>=25) poolR>0, best1>0.02, no sign reversal (bscreen). Else BOUNDED_NEGATIVE.
"""
import numpy as np, pandas as pd, bscreen as bs
from batch_a import _mk
N=20

def rejection(fr, side):
    h=fr["high"].to_numpy(); l=fr["low"].to_numpy(); c=fr["close"].to_numpy(); atr=fr["atr"].to_numpy(); rng=h-l
    hh=pd.Series(h).rolling(N).max().to_numpy(); ll=pd.Series(l).rolling(N).min().to_numpy()
    cloc=(c-l)/np.maximum(rng,1e-9); big=rng>0.8*atr
    if side<0: ev=(h>=hh)&(cloc<0.30)&big; stop=h            # fresh high rejected -> short, stop = the high
    else:      ev=(l<=ll)&(cloc>0.70)&big; stop=l            # fresh low rejected -> long, stop = the low
    return _mk(np.nan_to_num(ev.astype(float),nan=0).astype(bool),fr,stop,side)

HYPS=[
 dict(name="REJECT_newhigh_S",info="failed-auction/rejection",side=-1,rr=2.0,horizon=48,signal=lambda f:rejection(f,-1)),
 dict(name="REJECT_newlow_L",info="failed-auction/rejection",side=1,rr=2.0,horizon=48,signal=lambda f:rejection(f,1)),
]

if __name__=="__main__":
    bs.run_batch(HYPS,title="L (failed-auction rejection at fresh extreme)")
