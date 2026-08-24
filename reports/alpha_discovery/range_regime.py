"""range_regime.py — FROZEN causal RANGE regime for the multi-regime portfolio (mandate 2026-08-23). Selected by evidence
(cur_regime.py): RANGE ~50% of H4 history = the largest population and the clearest PORTFOLIO GAP (S5=breakout/trend,
CRS-1=high-vol correction; neither covers 'market goes nowhere'). REGIME FROZEN BEFORE ANY P&L. No strategy P&L influenced
its construction.

CAUSAL NORMALIZATION PROOF (every value at H4 bar t uses ONLY bars <= t):
- effic, atr, ema from _feat (ewm/rolling+shift). |effic| is a bounded causal trend-efficiency in [-1,1] — NO global stat.
- The range state machine is a forward scan: entering/updating/exiting a range at bar t reads only c[..t], high[..t], low[..t].
- range_high/low = trailing rolling extremes over the last L bars (bars <= t). No future data, no global percentile.
State machine (hysteresis -> persistent episodes, clear activation/deactivation contract):
  OUT -> count consecutive |effic|<R_LOW bars; at N_ENTER consecutive, RANGE turns ON with box = [min(low),max(high)] over
         the establishing window; box updated each in-range bar as trailing L-bar extremes.
  IN  -> EXIT (RANGE OFF) when close breaks beyond box by MARGIN*width (breakout) OR |effic|>=E_EXIT (trend ignition).
Outputs per H4 bar: in_range(bool), rlo, rhi, rmid. Mapped to M15 causally (merge_asof backward on H4 close_time).
Params are STRUCTURAL (not tuned to P&L): R_LOW .15, N_ENTER 6 (~1 day), L 12, MARGIN .25, E_EXIT .40. Data thru 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD
R_LOW=0.15; N_ENTER=6; L=12; MARGIN=0.25; E_EXIT=0.40; WARM=200
FP="RANGE_REGIME_V1|H4|Rlow0.15|Nenter6|L12|margin0.25|Eexit0.40|causal-trailing"

def build_h4_range(h4):
    c=h4["close"].to_numpy(); hi=h4["high"].to_numpy(); lo=h4["low"].to_numpy(); eff=h4["effic"].to_numpy(); n=len(h4)
    rmax=pd.Series(hi).rolling(L).max().to_numpy(); rmin=pd.Series(lo).rolling(L).min().to_numpy()
    in_range=np.zeros(n,bool); rlo=np.full(n,np.nan); rhi=np.full(n,np.nan)
    state=0; cnt=0; box_lo=np.nan; box_hi=np.nan
    for t in range(n):
        e=eff[t]
        if not np.isfinite(e) or t<WARM:
            state=0; cnt=0; continue
        if state==0:
            if abs(e)<R_LOW:
                cnt+=1
                if cnt>=N_ENTER and np.isfinite(rmax[t]) and np.isfinite(rmin[t]):
                    state=1; box_lo=rmin[t]; box_hi=rmax[t]
            else:
                cnt=0
        if state==1:
            # update box as trailing extremes (causal)
            if np.isfinite(rmax[t]): box_hi=rmax[t]
            if np.isfinite(rmin[t]): box_lo=rmin[t]
            wid=box_hi-box_lo
            brk = wid>0 and (c[t]>box_hi+MARGIN*wid or c[t]<box_lo-MARGIN*wid)
            trend = abs(e)>=E_EXIT
            if brk or trend:
                state=0; cnt=0; continue
            in_range[t]=True; rlo[t]=box_lo; rhi[t]=box_hi
    return in_range, rlo, rhi

def map_to_m15(m, h4, in_range, rlo, rhi):
    rmid=(rlo+rhi)/2.0
    hm=pd.DataFrame({"close_time":h4["close_time"].to_numpy(),"inr":in_range.astype(float),
                     "rlo":rlo,"rhi":rhi,"rmid":rmid}).sort_values("close_time")
    mm=pd.DataFrame({"time":m["time"].to_numpy()}).sort_values("time")
    j=pd.merge_asof(mm,hm,left_on="time",right_on="close_time",direction="backward").sort_index()
    return j["inr"].to_numpy(), j["rlo"].to_numpy(), j["rhi"].to_numpy(), j["rmid"].to_numpy()

def episodes(mask):
    idx=np.where(mask)[0]
    if len(idx)==0: return 0,0
    lens=[]; start=idx[0]; prev=idx[0]
    for i in idx[1:]:
        if i-prev>1: lens.append(prev-start+1); start=i
        prev=i
    lens.append(prev-start+1)
    return len(lens), int(np.median(lens))

def main():
    m=CD.load_m15(); h4=CD.agg(m,"H4"); inr,rlo,rhi=build_h4_range(h4)
    yr=h4["dt"].dt.year.to_numpy(); n=len(h4); c=int(inr.sum())
    nep,ml=episodes(inr)
    print(f"FROZEN RANGE REGIME V1  fp={FP}")
    print(f"  H4 in-range bars: {c}/{n} ({100*c/n:.1f}%) | episodes {nep} | median episode {ml} H4 bars (~{ml*4}h = {ml/6:.1f} days)")
    print(f"  recency: %2024+ {100*float(((yr>=2024)&inr).sum())/c:.1f}%  %2025+ {100*float(((yr>=2025)&inr).sum())/c:.1f}%")
    # per-year coverage
    print("  in-range % by year:", {int(y):int(100*((yr==y)&inr).sum()/max(1,(yr==y).sum())) for y in range(2012,2027) if (yr==y).sum()>50})
    # widths (structural, for later)
    wid=(rhi-rlo)[inr]; atr=h4["atr"].to_numpy()[inr]
    print(f"  box width median {np.nanmedian(wid):.1f} USD (~{np.nanmedian(wid/atr):.1f} ATR) — for context only, no P&L")

if __name__=="__main__":
    main()
