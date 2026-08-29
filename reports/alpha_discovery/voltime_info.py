"""voltime_info.py — NON_DIRECTIONAL_VOLATILITY_TIMING_DISCOVERY_V1 (CEO mandate 2026-08-24), INFORMATION-FIRST pass.
Question is NOT up/down but: WHEN is a tradeable move likely, how LARGE, how FAST, and what causal state precedes it. Direction is
NOT the target. All features causal (bars<=T); forward NON-DIRECTIONAL targets measured over next K bars (magnitude/timing only, no
direction). Chronological 2020+; report by era (D<=2018/C19-22/O23+) — here full history for max power, era-partitioned.
Targets: fwd_range_atr = (max high - min low over T+1..T+K)/ATR_T (expansion magnitude); p_move(X) = P(one-sided |move from close_T|
>= X*ATR within K, EITHER direction); t2move(X) = median bars to first X*ATR move. Conditioned on causal COMPRESSION state:
atr_ratio=ATR/ATR_ma, comp_dur=consecutive bars ATR<ATR_ma, dcw=Donchian20 width/ATR. Baseline = unconditional. If compression
predicts larger/faster expansion above baseline & cross-era-stable -> foundation for a breakout (direction-supplied) strategy."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
K=32  # forward horizon (8h) for expansion timing
def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); atr_ma=m["atr_ma"].to_numpy(); n=len(m); yr=m["dt"].dt.year.to_numpy(); hr=m["dt"].dt.hour.to_numpy()
    # causal compression features
    atr_ratio=np.where(atr_ma>0, atr/atr_ma, np.nan)
    comp=(atr<atr_ma).astype(int); comp_dur=np.zeros(n,int)
    for i in range(1,n): comp_dur[i]=comp_dur[i-1]+1 if comp[i] else 0
    dcw=np.where(atr>0,(pd.Series(h).rolling(20).max()-pd.Series(l).rolling(20).min()).to_numpy()/atr,np.nan)
    # forward NON-DIRECTIONAL targets
    fwd_hi=pd.Series(h).rolling(K).max().shift(-K).to_numpy(); fwd_lo=pd.Series(l).rolling(K).min().shift(-K).to_numpy()
    fwd_range=np.where(atr>0,(fwd_hi-fwd_lo)/atr,np.nan)
    # p_move / t2move via bounded scan (either direction)
    def move_metrics(X):
        p=np.zeros(n); tt=np.full(n,np.nan)
        for i in range(n-K-1):
            if not np.isfinite(atr[i]) or atr[i]<=0: continue
            tgt=X*atr[i]; sh=h[i+1:i+1+K]-c[i]; sl=c[i]-l[i+1:i+1+K]
            up=np.where(sh>=tgt)[0]; dn=np.where(sl>=tgt)[0]
            fu=up[0] if len(up) else 10**9; fd=dn[0] if len(dn) else 10**9
            f=min(fu,fd)
            if f<10**9: p[i]=1; tt[i]=f
        return p,tt
    p2,t2=move_metrics(2.0); p3,t3=move_metrics(3.0)
    valid=np.isfinite(fwd_range)&np.isfinite(atr_ratio)&(atr>0); valid[:250]=False; valid[n-K-1:]=False
    era=np.where(yr<=2018,"D",np.where(yr<=2022,"C","O"))
    def summ(mask):
        idx=np.where(mask&valid)[0]
        if len(idx)<200: return f"n={len(idx)}(thin)"
        return (f"n={len(idx):6d} fwdRange={np.mean(fwd_range[idx]):.2f}ATR P(2R)={np.mean(p2[idx]):.3f} "
                f"medT2R={np.nanmedian(t2[idx]):.0f}b P(3R)={np.mean(p3[idx]):.3f}")
    print(f"VOLTIME INFO (K={K} bars): non-directional expansion magnitude+timing conditioned on causal compression.")
    print("UNCONDITIONAL baseline: "+summ(np.ones(n,bool)))
    for e in ["D","C","O"]: print(f"  era {e}: "+summ(era==e))
    # atr_ratio quintiles (compression = low ratio)
    print("\nBy ATR_ratio (ATR/ATR_ma) quintile [low=compressed]:")
    qs=np.nanquantile(atr_ratio[valid],[0.2,0.4,0.6,0.8])
    labs=["Q1<%.2f"%qs[0],"Q2","Q3","Q4","Q5>%.2f"%qs[3]]
    bins=[atr_ratio<qs[0],(atr_ratio>=qs[0])&(atr_ratio<qs[1]),(atr_ratio>=qs[1])&(atr_ratio<qs[2]),(atr_ratio>=qs[2])&(atr_ratio<qs[3]),atr_ratio>=qs[3]]
    for lab,b in zip(labs,bins):
        print(f"  {lab:10s}: "+summ(b))
        # cross-era stability for the extreme compressed bin
    print("\nCompressed bin (Q1) cross-era stability:")
    for e in ["D","C","O"]: print(f"  {e}: "+summ((atr_ratio<qs[0])&(era==e)))
    # comp_dur bands
    print("\nBy compression DURATION (consecutive ATR<ATR_ma):")
    for lo,hi in [(0,1),(1,4),(4,10),(10,25),(25,10**9)]:
        print(f"  dur[{lo},{hi}): "+summ((comp_dur>=lo)&(comp_dur<hi)))
    # dcw (Donchian width) tertiles
    print("\nBy Donchian20 width/ATR (tight range = compressed):")
    dq=np.nanquantile(dcw[valid],[0.33,0.66])
    for lab,b in [("tight<%.1f"%dq[0],dcw<dq[0]),("mid",(dcw>=dq[0])&(dcw<dq[1])),("wide>%.1f"%dq[1],dcw>=dq[1])]:
        print(f"  {lab:10s}: "+summ(b))
    print("\n=> tradeable-relevant: does a compressed state raise fwdRange/P(2R) & shorten medT2R vs baseline, CROSS-ERA? If yes,")
    print("   a breakout from that state (direction supplied by the break) is the candidate mechanism. Info-first; no direction predicted.")
if __name__=="__main__": main()
