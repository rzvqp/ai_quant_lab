"""batch_a.py — BROAD DISCOVERY v2, Batch A. Intentionally CROSS-INFORMATION-CLASS (§32): opening-range breakout
(incl. the S5 mechanism as a CALIBRATION anchor), session variant, previous-day levels (break + fade), previous-week
level break (= CAND-0037 mechanism, tested under modern multi-era governance), mean-reversion extension, trend
pullback, time-of-day. Each hypothesis = mechanism-owned structural stop, causal signal. LONG/SHORT separate (§22).
Runs through bscreen (ratified sb engine, STRESS cost, eras b0/b1/DEV/CAL, cross-era sign-consistency).
"""
import numpy as np, pandas as pd, bscreen as bs

# ---------------- causal feature helpers ----------------
def _hr_day(fr):
    t=pd.Series(pd.to_datetime(fr["time"].to_numpy(),unit="s",utc=True))
    return t.dt.hour.to_numpy(), t.dt.floor("D").astype("int64").to_numpy(), t.dt.to_period("W").astype(str).to_numpy()

def opening_range(fr,start_h,end_h,or_bars=4):
    hr,day,_=_hr_day(fr); insess=(hr>=start_h)&(hr<end_h); n=len(fr)
    or_h=np.full(n,np.nan); or_l=np.full(n,np.nan); bpos=np.full(n,-1)
    df=pd.DataFrame({"day":day,"in":insess,"high":fr["high"].to_numpy(),"low":fr["low"].to_numpy()})
    for _,g in df[df["in"]].groupby("day"):
        gi=g.index.to_numpy(); or_h[gi]=g["high"].iloc[:or_bars].max(); or_l[gi]=g["low"].iloc[:or_bars].min(); bpos[gi]=np.arange(len(gi))
    return or_h,or_l,bpos

def prev_levels(fr,period):  # period 'D' or 'W' -> previous-period high/low broadcast to bars, causal
    _,day,wk=_hr_day(fr); key=day if period=="D" else wk
    df=pd.DataFrame({"k":key,"high":fr["high"].to_numpy(),"low":fr["low"].to_numpy()})
    agg=df.groupby("k").agg(h=("high","max"),l=("low","min"))
    ph=agg["h"].shift(1); pl=agg["l"].shift(1)   # previous period
    m={k:(ph.loc[k],pl.loc[k]) for k in agg.index}
    PH=np.array([m[k][0] for k in key]); PL=np.array([m[k][1] for k in key])
    return PH,PL

def swing(fr,k=8):
    lo=pd.Series(fr["low"].to_numpy()).rolling(k).min().shift(1).to_numpy()
    hi=pd.Series(fr["high"].to_numpy()).rolling(k).max().shift(1).to_numpy()
    return hi,lo

def sma(fr,k):
    return pd.Series(fr["close"].to_numpy()).rolling(k).mean().shift(1).to_numpy()

# ---------------- signal builders (return idx, sl_usd; entry=open[idx+1]) ----------------
def _mk(mask,fr,stoplvl,side):
    n=len(fr); o=fr["open"].to_numpy()
    idx=np.where(np.nan_to_num(mask.astype(float),nan=0).astype(bool))[0]; idx=idx[idx<n-1]
    entry=o[idx+1]; sl=np.abs(entry-stoplvl[idx]); return idx,sl

def orb(fr,start_h,end_h,side):
    orh,orl,bpos=opening_range(fr,start_h,end_h); c=fr["close"].to_numpy(); inwin=(bpos>=4)&(bpos<=20)
    if side>0: return _mk(inwin&(c>orh),fr,orl,side)
    else:      return _mk(inwin&(c<orl),fr,orh,side)

def pd_break(fr,side):
    PH,PL=prev_levels(fr,"D"); c=fr["close"].to_numpy(); hi,lo=swing(fr,8)
    if side>0: return _mk((c>PH),fr,lo,side)      # accepted break above PDH, stop=recent swing low
    else:      return _mk((c<PL),fr,hi,side)

def pd_fade(fr,side):   # reaction/mean-revert AT prev-day level
    PH,PL=prev_levels(fr,"D"); h=fr["high"].to_numpy(); l=fr["low"].to_numpy(); c=fr["close"].to_numpy(); atr=fr["atr"].to_numpy()
    if side<0:  # short: tag PDH from below and close back under it
        return _mk((h>=PH)&(c<PH)&(c< (fr["open"].to_numpy())),fr,PH+0.5*atr,side)
    else:       # long: tag PDL and close back above
        return _mk((l<=PL)&(c>PL)&(c> (fr["open"].to_numpy())),fr,PL-0.5*atr,side)

def pw_break(fr,side):  # previous-week level break continuation (CAND-0037 mechanism)
    PH,PL=prev_levels(fr,"W"); c=fr["close"].to_numpy(); hi,lo=swing(fr,12)
    if side>0: return _mk((c>PH),fr,lo,side)
    else:      return _mk((c<PL),fr,hi,side)

def mr_ext(fr,side):    # mean reversion: stretched vs SMA100
    s=sma(fr,100); c=fr["close"].to_numpy(); atr=fr["atr"].to_numpy(); hi,lo=swing(fr,6)
    if side>0: return _mk((c<s-2.0*atr),fr,lo,side)     # stretched down -> long, stop recent low
    else:      return _mk((c>s+2.0*atr),fr,hi,side)

def pb_trend(fr,side):  # trend pullback continuation (long only, uptrend)
    s50=sma(fr,50); s20=sma(fr,20); c=fr["close"].to_numpy(); l=fr["low"].to_numpy(); _,lo=swing(fr,6)[0],swing(fr,6)[1]
    up=(s20>s50); pull=(l<=s20); resume=(c>s20)
    return _mk(up&pull&resume,fr,lo,side)

def tod(fr,hr_lo,hr_hi,side):  # fixed time-of-day entry, stop = recent swing
    hr,_,_=_hr_day(fr); hi,lo=swing(fr,8); mask=(hr>=hr_lo)&(hr<hr_hi)
    return _mk(mask,fr,(lo if side>0 else hi),side)

# ---------------- Batch A registry ----------------
HYPS=[
 dict(name="ORB_NY_L(S5-anchor)",info="breakout/opening-range",side=1,rr=3.0,horizon=48,signal=lambda f:orb(f,13,21,1)),
 dict(name="ORB_NY_S",info="breakout/opening-range",side=-1,rr=3.0,horizon=48,signal=lambda f:orb(f,13,21,-1)),
 dict(name="ORB_LON_L",info="session/breakout",side=1,rr=2.0,horizon=48,signal=lambda f:orb(f,7,13,1)),
 dict(name="ORB_LON_S",info="session/breakout",side=-1,rr=2.0,horizon=48,signal=lambda f:orb(f,7,13,-1)),
 dict(name="PDH_break_L",info="ref-level/prev-day",side=1,rr=2.0,horizon=48,signal=lambda f:pd_break(f,1)),
 dict(name="PDL_break_S",info="ref-level/prev-day",side=-1,rr=2.0,horizon=48,signal=lambda f:pd_break(f,-1)),
 dict(name="PDH_fade_S",info="ref-level/reaction",side=-1,rr=2.0,horizon=48,signal=lambda f:pd_fade(f,-1)),
 dict(name="PDL_fade_L",info="ref-level/reaction",side=1,rr=2.0,horizon=48,signal=lambda f:pd_fade(f,1)),
 dict(name="PWH_break_L(CAND37)",info="ref-level/weekly",side=1,rr=2.0,horizon=48,signal=lambda f:pw_break(f,1)),
 dict(name="PWL_break_S(CAND37)",info="ref-level/weekly",side=-1,rr=2.0,horizon=48,signal=lambda f:pw_break(f,-1)),
 dict(name="MR_ext_L",info="mean-reversion",side=1,rr=2.0,horizon=48,signal=lambda f:mr_ext(f,1)),
 dict(name="MR_ext_S",info="mean-reversion",side=-1,rr=2.0,horizon=48,signal=lambda f:mr_ext(f,-1)),
 dict(name="PB_trend_L",info="trend/pullback",side=1,rr=2.0,horizon=48,signal=lambda f:pb_trend(f,1)),
 dict(name="TOD_NYopen_L",info="time-of-day",side=1,rr=2.0,horizon=48,signal=lambda f:tod(f,13,15,1)),
]

if __name__=="__main__":
    bs.run_batch(HYPS,title="A (cross-class)")
