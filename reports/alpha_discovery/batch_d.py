"""batch_d.py — BROAD DISCOVERY v2, Batch D. Genuinely-new mechanism (§18): SESSION-RANGE INHERITANCE.
The PRIOR session forms a coil (its full high-low range); the NEXT session breaks it directionally. Distinct from
S5 (own-session first-4-bar opening range) and from reference-levels (prev-day/week). Causal (coil completes
before trade session, same calendar day). Motivated by R13/R17 (session-open momentum STRUCTURE is the one edge).
Stop = opposite coil extreme (or_opp-style). LONG/SHORT separate. M15 eras, ratified sb engine.
"""
import numpy as np, pandas as pd, bscreen as bs
from batch_a import _mk, _hr_day

def session_range_break(fr, coil, trade, side, hold=False):
    hr,day,_=_hr_day(fr); clo,chi=coil; tlo,thi=trade
    incoil=(hr>=clo)&(hr<chi); intrade=(hr>=tlo)&(hr<thi); n=len(fr)
    df=pd.DataFrame({"day":day,"in":incoil,"high":fr["high"].to_numpy(),"low":fr["low"].to_numpy()})
    g=df[df["in"]].groupby("day").agg(h=("high","max"),l=("low","min"))
    dd=pd.Series(day); coilH=dd.map(g["h"]).to_numpy(); coilL=dd.map(g["l"]).to_numpy()
    c=fr["close"].to_numpy(); o=fr["open"].to_numpy()
    if side>0: mask=intrade&(c>coilH)&np.isfinite(coilH); stoplvl=coilL
    else:      mask=intrade&(c<coilL)&np.isfinite(coilL); stoplvl=coilH
    if hold:  # require the breakout bar to close in the breakout direction beyond by >0.1*range (acceptance)
        rngc=(coilH-coilL); ok=((c-coilH)>0.1*rngc) if side>0 else ((coilL-c)>0.1*rngc)
        mask=mask&np.nan_to_num(ok.astype(float),nan=0).astype(bool)
    return _mk(mask,fr,stoplvl,side)

ASIA=(0,7); LON=(7,13); NY=(13,21)
HYPS=[
 dict(name="ASIArange_LONbreak_L",info="session-range-inherit",side=1,rr=2.0,horizon=48,signal=lambda f:session_range_break(f,ASIA,LON,1)),
 dict(name="ASIArange_LONbreak_S",info="session-range-inherit",side=-1,rr=2.0,horizon=48,signal=lambda f:session_range_break(f,ASIA,LON,-1)),
 dict(name="LONrange_NYbreak_L",info="session-range-inherit",side=1,rr=2.0,horizon=48,signal=lambda f:session_range_break(f,LON,NY,1)),
 dict(name="LONrange_NYbreak_S",info="session-range-inherit",side=-1,rr=2.0,horizon=48,signal=lambda f:session_range_break(f,LON,NY,-1)),
 dict(name="ASIArange_NYbreak_L",info="session-range-inherit",side=1,rr=2.0,horizon=48,signal=lambda f:session_range_break(f,ASIA,NY,1)),
 dict(name="ASIArange_NYbreak_S",info="session-range-inherit",side=-1,rr=2.0,horizon=48,signal=lambda f:session_range_break(f,ASIA,NY,-1)),
 # acceptance (HOLD) variants of the strongest structural pair
 dict(name="ASIArange_LONbreak_L_acc",info="session-range-inherit/acc",side=1,rr=2.0,horizon=48,signal=lambda f:session_range_break(f,ASIA,LON,1,hold=True)),
 dict(name="LONrange_NYbreak_L_acc",info="session-range-inherit/acc",side=1,rr=2.0,horizon=48,signal=lambda f:session_range_break(f,LON,NY,1,hold=True)),
]

if __name__=="__main__":
    bs.run_batch(HYPS,title="D (session-range inheritance)")
