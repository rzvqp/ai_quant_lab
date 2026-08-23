"""m12_sweep_retest.py — MODULAR_DISCOVERY_V1, M12 branch sweep->reclaim->retest->hold (§10 incremental vs bare sweep).
Ratified MK-02 pools/sweeps (as in m05_liq). After a BELOW-pool sweep+reclaim at bar i (level p=pool.price), a RETEST-HOLD =
first later bar j in [i+1,i+R] whose low returns near p (l[j]<=p+0.2*ATR) but HOLDS above the sweep extreme (l[j]>=sweep_low)
and closes back above p (c[j]>p). Measure forward reversal-asym from the RETEST bar j; compare to the bare-sweep baseline (from
m05). §10: the sequence adds edge only if retest-hold reversal-asym robustly BEATS bare sweep across eras. CAUSAL. cur_data M15."""
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
    R=48
    bare_long=[]; bare_short=[]; rt_long=[]; rt_short=[]
    for e in sweeps:
        i=e.idx
        if i is None or i>=n-1 or not np.isfinite(atr[i]) or atr[i]<=0: continue
        p=e.pool.price; below=(e.pool.side==BELOW)
        (bare_long if below else bare_short).append(int(i))
        sweep_ext = l[i] if below else h[i]
        found=None
        for j in range(i+1, min(i+R, n-1)):
            if not np.isfinite(atr[j]) or atr[j]<=0: continue
            if below:
                if l[j]<=p+0.2*atr[j] and l[j]>=sweep_ext and c[j]>p: found=j; break
            else:
                if h[j]>=p-0.2*atr[j] and h[j]<=sweep_ext and c[j]<p: found=j; break
        if found is not None:
            (rt_long if below else rt_short).append(int(found))
    def row(idx,ln):
        idx=np.array(sorted(set(idx)),int); idx=idx[(idx>=0)&(idx<n-1)]; ok=np.isfinite(up[idx])&np.isfinite(dn[idx]); idx=idx[ok]
        if len(idx)<120: return f"n={len(idx)}(thin)"
        a=np.median(up[idx])-np.median(dn[idx]) if ln>0 else np.median(dn[idx])-np.median(up[idx])
        return f"n={len(idx):5d} rev-asym={a:+.2f}"
    def report(name,ev,ln):
        line=f"  {name}: {row(ev,ln)}"
        for pl,ym in [("D",yr<=2018),("C",(yr>=2019)&(yr<=2022)),("O",yr>=2023)]:
            ii=[x for x in ev if 0<=x<n and ym[x]]; line+=f" | {pl} {row(ii,ln)}"
        print(line)
    print(f"M12 sweep->retest: sweeps={len(sweeps)} BELOW bare={len(bare_long)} retest-hold={len(rt_long)} | ABOVE bare={len(bare_short)} retest-hold={len(rt_short)}")
    report("BELOW bare-sweep      -> LONG",bare_long,1)
    report("BELOW sweep+RETEST    -> LONG",rt_long,1)
    report("ABOVE bare-sweep      -> SHORT",bare_short,-1)
    report("ABOVE sweep+RETEST    -> SHORT",rt_short,-1)
    print("  => §10: retest-hold adds edge only if rev-asym robustly BEATS bare sweep across ALL eras.")
if __name__=="__main__": main()
