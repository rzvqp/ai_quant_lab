"""lowvol_bull_regime.py — FROZEN causal LOWVOL_BULL regime (multi-regime portfolio, regime #3). Structural: LOW causal vol +
positive trend efficiency + EMA-up = a smooth steady bull grind (gold's default accumulation drift). Distinct from
HIGHVOL_BULL_V1 (high vol), RANGE_REGIME_V1 (low |effic|), CRS-1 (down). Hypothesis: low-vol trends are more persistent /
less reversal-prone than blowoff-prone high-vol bulls -> possibly era-consistent up-continuation. REGIME FROZEN BEFORE P&L.

CAUSAL NORMALIZATION PROOF: ema/effic/atr from _feat (causal); vol_ratio = atr/TRAILING rolling-median(atr,W).shift(1) (bars<t);
bounded effic. No global percentile. State machine hysteresis (persistent router state). Params structural, pre-P&L:
W=360, WARM=400, VLO_HI=0.95 (vol below 0.95x trailing norm), E_BULL=0.30, N_ENTER=4. Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD
W=360; WARM=400; VLO_HI=0.95; E_BULL=0.30; N_ENTER=4
FP="LOWVOL_BULL_V1|H4|volratioTRAIL360|VLOhi0.95|Ebull0.30|Nenter4|causal-trailing"

def build_h4(h4):
    e20=h4["ema20"].to_numpy(); e50=h4["ema50"].to_numpy(); eff=h4["effic"].to_numpy(); atr=h4["atr"].to_numpy(); n=len(h4)
    base=pd.Series(atr).rolling(W).median().shift(1).to_numpy(); vr=atr/base
    bull_bar=(e20>e50)&(eff>E_BULL)&(vr<=VLO_HI)
    hold=(e20>e50)&(eff>0)&(vr<=1.05)   # allow vol to tick up modestly before exit
    on=np.zeros(n,bool); state=0; cnt=0
    for t in range(n):
        if t<WARM or not np.isfinite(vr[t]) or not np.isfinite(eff[t]):
            state=0; cnt=0; continue
        if state==0:
            if bull_bar[t]:
                cnt+=1
                if cnt>=N_ENTER: state=1; on[t]=True
            else: cnt=0
        else:
            if hold[t]: on[t]=True
            else: state=0; cnt=0
    return on, vr

def map_to_m15(m, h4, on):
    hm=pd.DataFrame({"close_time":h4["close_time"].to_numpy(),"on":on.astype(float)}).sort_values("close_time")
    mm=pd.DataFrame({"time":m["time"].to_numpy()}).sort_values("time")
    return pd.merge_asof(mm,hm,left_on="time",right_on="close_time",direction="backward").sort_index()["on"].to_numpy()

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
    m=CD.load_m15(); h4=CD.agg(m,"H4"); on,vr=build_h4(h4); yr=h4["dt"].dt.year.to_numpy()
    n=len(h4); c=int(on.sum()); nep,ml=episodes(on)
    print(f"FROZEN LOWVOL_BULL regime V1  fp={FP}")
    print(f"  H4 on bars: {c}/{n} ({100*c/n:.1f}%) | episodes {nep} | median episode {ml} H4 bars (~{ml/6:.1f} days)")
    print(f"  recency: %2024+ {100*float(((yr>=2024)&on).sum())/max(1,c):.1f}%  %2025+ {100*float(((yr>=2025)&on).sum())/max(1,c):.1f}%")
    print("  on% by year:", {int(y):int(100*((yr==y)&on).sum()/max(1,(yr==y).sum())) for y in range(2012,2027) if (yr==y).sum()>50})

if __name__=="__main__":
    main()
