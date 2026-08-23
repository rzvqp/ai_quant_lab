"""batch_j.py — BROAD DISCOVERY v2, Batch J. More genuinely-distinct bounded mechanisms (CEO axes not yet tested):
- ASIA_LEAD: does the ASIA session's DIRECTION lead the NY move? (multi-session lead-lag, distinct from Batch D
  session-range breakout — here the signal is Asia's net direction, not a range break).
- DELAYED_MOM: enter 2 DAYS AFTER a big directional day, same direction (DELAYED response / drift, not immediate).
- WEEKLY_REVERT: after a top/bottom-decile WEEKLY move, revert next week (overreaction at the WEEKLY scale — untested).
Causal; M15 execution; positives MUST pass §30 vs S5.
"""
import numpy as np, pandas as pd, bscreen as bs
from batch_a import _mk, _hr_day
from batch_e import _daily, _bcast, _first_ny
from batch_a import swing

def asia_lead(fr, asia_up, side):   # on days Asia closed up(asia_up=1)/down(0), trade `side` at NY open
    hr,day,_=_hr_day(fr); n=len(fr); c=fr["close"].to_numpy(); o=fr["open"].to_numpy()
    asia=(hr>=0)&(hr<7); df=pd.DataFrame({"day":day,"asia":asia,"o":o,"c":c})
    a=df[df["asia"]].groupby("day").agg(ao=("o","first"),ac=("c","last")); aret=(a["ac"]-a["ao"])
    ar=pd.Series(day).map(aret).to_numpy(); fny=_first_ny(fr); hi,lo=swing(fr,8)
    up=ar>0 if asia_up else ar<0
    cond=fny&np.nan_to_num(up.astype(float),nan=0).astype(bool)
    return _mk(cond,fr,(lo if side>0 else hi),side)

def delayed_mom(fr, side):   # 2 days after a big directional day, same direction
    g,day=_daily(fr); fny=_first_ny(fr)
    # need day D-2 range & direction; _daily gives shift1/2/3
    do2=_bcast(g,day,"do2"); dc2=_bcast(g,day,"dc2"); rng2=_bcast(g,day,"rng2"); rngma=_bcast(g,day,"rngma")
    hi,lo=swing(fr,8); big=rng2>1.5*rngma
    if side>0: cond=fny&big&(dc2>do2); stop=lo
    else:      cond=fny&big&(dc2<do2); stop=hi
    return _mk(np.nan_to_num(cond.astype(float),nan=0).astype(bool),fr,stop,side)

def weekly_revert(fr, side):
    hr,day,wk=_hr_day(fr); n=len(fr); o=fr["open"].to_numpy(); c=fr["close"].to_numpy()
    df=pd.DataFrame({"wk":wk,"o":o,"c":c,"i":np.arange(n)})
    w=df.groupby("wk").agg(wo=("o","first"),wc=("c","last")); wret=(w["wc"]-w["wo"]); wretp=wret.shift(1)
    thi=wret.quantile(0.85); tlo=wret.quantile(0.15)
    wp=pd.Series(wk).map(wretp).to_numpy()
    # first bar of week
    firstwk=np.r_[True, wk[1:]!=wk[:-1]]; hi,lo=swing(fr,8)
    if side>0: cond=firstwk&(wp<=tlo); stop=lo   # prev week crashed -> long revert
    else:      cond=firstwk&(wp>=thi); stop=hi
    return _mk(np.nan_to_num(cond.astype(float),nan=0).astype(bool),fr,stop,side)

HYPS=[
 dict(name="ASIA_UP_LONG",info="session-leadlag",side=1,rr=2.0,horizon=48,cool=24,signal=lambda f:asia_lead(f,1,1)),
 dict(name="ASIA_DN_SHORT",info="session-leadlag",side=-1,rr=2.0,horizon=48,cool=24,signal=lambda f:asia_lead(f,0,-1)),
 dict(name="ASIA_UP_SHORT_fade",info="session-leadlag/fade",side=-1,rr=2.0,horizon=48,cool=24,signal=lambda f:asia_lead(f,1,-1)),
 dict(name="DELAYED_MOM_L",info="delayed-response",side=1,rr=2.0,horizon=96,cool=24,signal=lambda f:delayed_mom(f,1)),
 dict(name="DELAYED_MOM_S",info="delayed-response",side=-1,rr=2.0,horizon=96,cool=24,signal=lambda f:delayed_mom(f,-1)),
 dict(name="WEEKLY_REVERT_L",info="weekly-overreaction",side=1,rr=2.0,horizon=96,cool=48,signal=lambda f:weekly_revert(f,1)),
 dict(name="WEEKLY_REVERT_S",info="weekly-overreaction",side=-1,rr=2.0,horizon=96,cool=48,signal=lambda f:weekly_revert(f,-1)),
]

if __name__=="__main__":
    bs.run_batch(HYPS,title="J (lead-lag / delayed / weekly-revert)")
