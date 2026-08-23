"""m05_liq.py — MODULAR_DISCOVERY_V1, M05 LIQUIDITY (info-first, ratified MK-02). Strict pool->sweep->reclaim: build_pools (swing
liquidity), detect_sweeps(require_close_back_inside=True). Hypothesis: a swept-and-reclaimed pool REVERSES — sell-side pool (lows
swept + reclaimed) -> UP; buy-side pool (highs swept) -> DOWN. INFO: forward reversal asym by pool side, partitioned DISC<=2018/
CONF19-22/OOS23+. Causal (sweep at its bar). Data cur_data M15 2011-2026."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD, liquidity_mechanics as LM
from market_structure import detect_swings, label_structure, Block
def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); t=m["time"].to_numpy(); n=len(m)
    gaps=np.where(np.diff(t)>72*3600)[0]; blocks=[]; s=0
    for g in gaps: blocks.append(Block(s,g+1)); s=g+1
    blocks.append(Block(s,n))
    swings=label_structure(detect_swings(h,l,blocks))
    pools=LM.build_pools(swings, LM.PoolTier.EXTERNAL)
    sweeps=LM.detect_sweeps(h,l,c,pools,blocks,require_close_back_inside=True)
    BELOW=LM.PoolSide.BELOW
    fmax=pd.Series(h).rolling(96).max().shift(-96).to_numpy(); fmin=pd.Series(l).rolling(96).min().shift(-96).to_numpy()
    up=(fmax-c)/atr; dn=(c-fmin)/atr; yr=m["dt"].dt.year.to_numpy()
    ev_long=[]; ev_short=[]
    for e in sweeps:
        i=e.idx
        if i is None or i>=n-1 or not np.isfinite(atr[i]) or atr[i]<=0: continue
        # sell-side pool (below, at lows) swept+reclaimed -> bullish reversal LONG; buy-side -> SHORT
        (ev_long if e.pool.side==BELOW else ev_short).append(int(i))
    print(f"M05 info: pools={len(pools)} sweeps(reclaimed)={len(sweeps)} SELLside(->LONG)={len(ev_long)} BUYside(->SHORT)={len(ev_short)} (BELOW->LONG)")
    def row(idx,ln):
        idx=np.array(sorted(set(idx)),int); idx=idx[idx<n-1]; ok=np.isfinite(up[idx])&np.isfinite(dn[idx]); idx=idx[ok]
        if len(idx)<120: return f"n={len(idx)}(thin)"
        a=np.median(up[idx])-np.median(dn[idx]) if ln>0 else np.median(dn[idx])-np.median(up[idx])
        return f"n={len(idx):5d} reversal-asym={a:+.2f}"
    for nm,ev,ln in [("BELOW-pool sweep -> LONG(up)",ev_long,1),("ABOVE-pool sweep -> SHORT(dn)",ev_short,-1)]:
        line=f"  {nm}: {row(ev,ln)}"
        for pl,ym in [("D",yr<=2018),("C",(yr>=2019)&(yr<=2022)),("O",yr>=2023)]:
            ii=[x for x in ev if ym[x]]; line+=f" | {pl} {row(ii,ln)}"
        print(line)
    print("  => M05 supports tradeable only if reversal-asym robustly>0 across partitions (sweep truly reverses, not era-trend).")
if __name__=="__main__": main()
