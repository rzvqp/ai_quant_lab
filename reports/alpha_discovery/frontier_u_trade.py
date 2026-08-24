"""frontier_u_trade.py — tradeability of the Frontier U finding: cross-era-stable 1-bar mean-reversion after 3-bar runs
(DDD->long, UUU->short). Structural stop = the 3-bar run extreme; short horizon; rr1 (mean-reversion, small targets).
Ratified sb screen, STRESS, cross-era. Determines if the real cross-era-stable signal survives cost (likely sub-cost).
"""
import numpy as np, pandas as pd, bscreen as bs
from batch_a import _mk

def run3(fr, side):
    c=fr["close"].to_numpy(); h=fr["high"].to_numpy(); l=fr["low"].to_numpy()
    up=np.r_[False,c[1:]>c[:-1]]; dn=np.r_[False,c[1:]<c[:-1]]
    def three(x): s=pd.Series(x.astype(int)); return (s.rolling(3).sum()>=3).to_numpy()
    if side>0:  # 3 down bars -> long, stop = min low of last 3
        ev=three(dn); stop=pd.Series(l).rolling(3).min().to_numpy()
    else:       # 3 up bars -> short, stop = max high of last 3
        ev=three(up); stop=pd.Series(h).rolling(3).max().to_numpy()
    return _mk(np.nan_to_num(ev.astype(float),nan=0).astype(bool),fr,stop,side)

HYPS=[
 dict(name="DDD_long_rr1",info="U:3run-meanrev",side=1,rr=1.0,horizon=4,cool=2,signal=lambda f:run3(f,1)),
 dict(name="UUU_short_rr1",info="U:3run-meanrev",side=-1,rr=1.0,horizon=4,cool=2,signal=lambda f:run3(f,-1)),
 dict(name="DDD_long_rr1.5",info="U:3run-meanrev",side=1,rr=1.5,horizon=8,cool=2,signal=lambda f:run3(f,1)),
]

if __name__=="__main__":
    bs.run_batch(HYPS,title="U-trade (3-bar-run mean-reversion)")
