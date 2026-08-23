"""batch_h.py — BROAD DISCOVERY v2, Batch H. Frontier: NEW STRUCTURAL/TIMING EVENTS that supply their own
direction (like S5) and are candidates for INDEPENDENCE from S5 (different timing anchor / structural trigger).
- WOR_break: WEEKLY opening-range breakout (first 6h of the week's range; break during the week). Timing anchor =
  week-open, distinct from S5's day-open -> may fire on different days/weeks.
- NEW20D: break of the 20-trading-day high/low = structural transition into fresh territory (not continuous Donchian).
- ROUND_break: price crosses a psychological $50 level with momentum (structural/psychological, non-session).
All causal, own-direction structural events. Screened on the ratified engine; positives MUST pass §30 vs S5.
"""
import numpy as np, pandas as pd, bscreen as bs
from batch_a import _mk, _hr_day

def wor(fr, side):
    hr,day,wk=_hr_day(fr); n=len(fr)
    df=pd.DataFrame({"wk":wk,"high":fr["high"].to_numpy(),"low":fr["low"].to_numpy(),"i":np.arange(n)})
    worh=np.full(n,np.nan); worl=np.full(n,np.nan); wpos=np.full(n,-1)
    for w,g in df.groupby("wk"):
        gi=g["i"].to_numpy(); worh[gi]=g["high"].iloc[:24].max(); worl[gi]=g["low"].iloc[:24].min(); wpos[gi]=np.arange(len(gi))
    c=fr["close"].to_numpy(); inwin=(wpos>=24)
    if side>0: return _mk(inwin&(c>worh),fr,worl,side)
    else:      return _mk(inwin&(c<worl),fr,worh,side)

def new20d(fr, side, D=1920):
    c=fr["close"].to_numpy(); dhi=pd.Series(fr["high"].to_numpy()).rolling(D).max().shift(1).to_numpy(); dlo=pd.Series(fr["low"].to_numpy()).rolling(D).min().shift(1).to_numpy()
    slo=pd.Series(fr["low"].to_numpy()).rolling(20).min().shift(1).to_numpy(); shi=pd.Series(fr["high"].to_numpy()).rolling(20).max().shift(1).to_numpy()
    if side>0: return _mk(c>dhi,fr,slo,side)
    else:      return _mk(c<dlo,fr,shi,side)

def round_break(fr, side, mult=50.0):
    c=fr["close"].to_numpy(); cp=np.roll(c,1); cp[0]=c[0]; fl=np.floor(c/mult); flp=np.floor(cp/mult)
    if side>0: return _mk(fl>flp,fr,fl*mult,side)
    else:      return _mk(fl<flp,fr,(flp)*mult,side)

HYPS=[
 dict(name="WOR_break_L",info="weekly-opening-range",side=1,rr=2.0,horizon=48,signal=lambda f:wor(f,1)),
 dict(name="WOR_break_S",info="weekly-opening-range",side=-1,rr=2.0,horizon=48,signal=lambda f:wor(f,-1)),
 dict(name="NEW20D_L",info="structural-transition/new-territory",side=1,rr=2.0,horizon=48,signal=lambda f:new20d(f,1)),
 dict(name="NEW20D_S",info="structural-transition/new-territory",side=-1,rr=2.0,horizon=48,signal=lambda f:new20d(f,-1)),
 dict(name="ROUND_break_L",info="psychological-level",side=1,rr=2.0,horizon=48,signal=lambda f:round_break(f,1)),
 dict(name="ROUND_break_S",info="psychological-level",side=-1,rr=2.0,horizon=48,signal=lambda f:round_break(f,-1)),
]

if __name__=="__main__":
    bs.run_batch(HYPS,title="H (new structural/timing events)")
