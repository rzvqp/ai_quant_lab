"""batch_e.py — BROAD DISCOVERY v2, Batch E. NOVEL-MECHANISM discovery (CEO 2026-08-23): economic behaviors at a
DIFFERENT economic level (MULTI-DAY / DAY-LEVEL) not represented by the intraday M15/H1/H4 families. Axes: LEVEL
MIGRATION (multi-day HH/HL), MULTI-DAY STRUCTURE (inside-day breakout), VOLATILITY MEMORY (large-range-day
continuation), daily OVERREACTION (multi-day mean reversion), trend-day PERSISTENCE (open-drive continuation).
All CAUSAL: features use PREVIOUS COMPLETED days only (no D1-feature defect, §24-safe). Decision once/day at NY open
(prev day complete + liquid entry); execution on authorized M15 frame; multi-day horizon. Every positive MUST pass
§30 independence vs S5 (Batch D lesson: novelty at ECONOMIC-EVENT level, not trigger level).
"""
import numpy as np, pandas as pd, bscreen as bs
from batch_a import _mk, _hr_day

def _daily(fr):
    hr,day,_=_hr_day(fr)
    df=pd.DataFrame({"day":day,"o":fr["open"].to_numpy(),"h":fr["high"].to_numpy(),"l":fr["low"].to_numpy(),"c":fr["close"].to_numpy()})
    g=df.groupby("day").agg(do=("o","first"),dh=("h","max"),dl=("l","min"),dc=("c","last"))
    g["rng"]=g["dh"]-g["dl"]; g["rngma"]=g["rng"].rolling(20).mean().shift(1)
    for k in ["do","dh","dl","dc","rng"]:
        g[k+"1"]=g[k].shift(1); g[k+"2"]=g[k].shift(2); g[k+"3"]=g[k].shift(3)
    return g, np.array(day)

def _bcast(g, day, col):
    return pd.Series(day).map(g[col]).to_numpy()

def _first_ny(fr):
    hr,day,_=_hr_day(fr); m=hr>=13; idxs=np.arange(len(fr))
    df=pd.DataFrame({"day":day,"m":m,"i":idxs})
    first=df[df["m"]].groupby("day")["i"].first().to_numpy()
    out=np.zeros(len(fr),bool); out[first]=True; return out

def multiday_mom(fr, side):
    g,day=_daily(fr); fny=_first_ny(fr)
    dh1=_bcast(g,day,"dh1"); dh2=_bcast(g,day,"dh2"); dl1=_bcast(g,day,"dl1"); dl2=_bcast(g,day,"dl2")
    if side>0: cond=fny&(dh1>dh2)&(dl1>dl2); stop=dl1        # multi-day higher-high & higher-low -> long
    else:      cond=fny&(dh1<dh2)&(dl1<dl2); stop=dh1
    return _mk(np.nan_to_num(cond.astype(float),nan=0).astype(bool),fr,stop,side)

def inside_day_break(fr, side):
    g,day=_daily(fr); dh1=_bcast(g,day,"dh1"); dh2=_bcast(g,day,"dh2"); dl1=_bcast(g,day,"dl1"); dl2=_bcast(g,day,"dl2")
    inside=(dh1<dh2)&(dl1>dl2); c=fr["close"].to_numpy()
    if side>0: cond=inside&(c>dh1); stop=dl1                 # prev inside day -> break its high today
    else:      cond=inside&(c<dl1); stop=dh1
    return _mk(np.nan_to_num(cond.astype(float),nan=0).astype(bool),fr,stop,side)

def volmemory_cont(fr, side):
    g,day=_daily(fr); fny=_first_ny(fr)
    rng1=_bcast(g,day,"rng1"); rngma=_bcast(g,day,"rngma"); do1=_bcast(g,day,"do1"); dc1=_bcast(g,day,"dc1"); dl1=_bcast(g,day,"dl1"); dh1=_bcast(g,day,"dh1")
    big=rng1>1.5*rngma
    if side>0: cond=fny&big&(dc1>do1); stop=dl1              # large up-range day -> continue up
    else:      cond=fny&big&(dc1<do1); stop=dh1
    return _mk(np.nan_to_num(cond.astype(float),nan=0).astype(bool),fr,stop,side)

def multiday_revert(fr, side):
    g,day=_daily(fr); fny=_first_ny(fr)
    dc1=_bcast(g,day,"dc1"); dc2=_bcast(g,day,"dc2"); dc3=_bcast(g,day,"dc3"); dl1=_bcast(g,day,"dl1"); dh1=_bcast(g,day,"dh1"); dl2=_bcast(g,day,"dl2"); dh2=_bcast(g,day,"dh2")
    if side>0: cond=fny&(dc1<dc2)&(dc2<dc3); stop=np.minimum(dl1,dl2)   # 3 declining daily closes -> long reversion
    else:      cond=fny&(dc1>dc2)&(dc2>dc3); stop=np.maximum(dh1,dh2)
    return _mk(np.nan_to_num(cond.astype(float),nan=0).astype(bool),fr,stop,side)

def opendrive_cont(fr, side):
    g,day=_daily(fr); fny=_first_ny(fr)
    dh1=_bcast(g,day,"dh1"); dl1=_bcast(g,day,"dl1"); dc1=_bcast(g,day,"dc1"); rng1=_bcast(g,day,"rng1"); rngma=_bcast(g,day,"rngma")
    loc=(dc1-dl1)/np.where((dh1-dl1)>0,(dh1-dl1),np.nan)   # close location in prev day range
    if side>0: cond=fny&(loc>0.8)&(rng1>rngma); stop=dl1    # strong trend-up close -> continue
    else:      cond=fny&(loc<0.2)&(rng1>rngma); stop=dh1
    return _mk(np.nan_to_num(cond.astype(float),nan=0).astype(bool),fr,stop,side)

HYPS=[
 dict(name="MULTIDAY_MOM_L",info="level-migration/multiday",side=1,rr=2.0,horizon=96,cool=24,signal=lambda f:multiday_mom(f,1)),
 dict(name="MULTIDAY_MOM_S",info="level-migration/multiday",side=-1,rr=2.0,horizon=96,cool=24,signal=lambda f:multiday_mom(f,-1)),
 dict(name="INSIDE_DAY_BREAK_L",info="multiday-structure",side=1,rr=2.0,horizon=96,cool=16,signal=lambda f:inside_day_break(f,1)),
 dict(name="INSIDE_DAY_BREAK_S",info="multiday-structure",side=-1,rr=2.0,horizon=96,cool=16,signal=lambda f:inside_day_break(f,-1)),
 dict(name="VOLMEM_CONT_L",info="volatility-memory",side=1,rr=2.0,horizon=96,cool=24,signal=lambda f:volmemory_cont(f,1)),
 dict(name="VOLMEM_CONT_S",info="volatility-memory",side=-1,rr=2.0,horizon=96,cool=24,signal=lambda f:volmemory_cont(f,-1)),
 dict(name="MULTIDAY_REVERT_L",info="daily-overreaction",side=1,rr=2.0,horizon=96,cool=24,signal=lambda f:multiday_revert(f,1)),
 dict(name="MULTIDAY_REVERT_S",info="daily-overreaction",side=-1,rr=2.0,horizon=96,cool=24,signal=lambda f:multiday_revert(f,-1)),
 dict(name="OPENDRIVE_CONT_L",info="trend-day-persistence",side=1,rr=2.0,horizon=96,cool=24,signal=lambda f:opendrive_cont(f,1)),
 dict(name="OPENDRIVE_CONT_S",info="trend-day-persistence",side=-1,rr=2.0,horizon=96,cool=24,signal=lambda f:opendrive_cont(f,-1)),
]

if __name__=="__main__":
    bs.run_batch(HYPS,title="E (novel multi-day / day-level mechanisms)")
