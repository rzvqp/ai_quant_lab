"""m13_rem.py — MODULAR_DISCOVERY_V1, M13 remaining branches: BPR (balanced price range) + FVG-stack/density.
Ratified MK-03 (imbalance_mechanics). BRANCH-3 BPR: an overlapping bullish×bearish FVG (same block, formed within 3 bars,
strict overlap tol=0) forms a balanced zone; ICT convention = the SECOND-forming gap's polarity is the active one. Info test:
does BPR active-polarity predict forward direction (excursion-asym) robustly across eras? BRANCH-4 FVG-STACK: net FVG density in
a trailing K=20 window (bull_count - bear_count, |net|>=2); does net-density polarity predict forward direction across eras?
Both CAUSAL: density/overlap measured on bars <= i, excursion strictly forward from i. Partitions DISC<=2018/CONF19-22/OOS23+."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
import imbalance_mechanics as IM
from market_structure import Block
def build_blocks(t):
    gaps=np.where(np.diff(t)>72*3600)[0]; bs=[]; start=0
    for g in gaps: bs.append(Block(start,g+1)); start=g+1
    bs.append(Block(start,len(t))); return bs
def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); t=m["time"].to_numpy(); n=len(m)
    blocks=build_blocks(t)
    fvgs=IM.detect_fvgs(h,l,blocks)
    fmax=pd.Series(h).rolling(96).max().shift(-96).to_numpy(); fmin=pd.Series(l).rolling(96).min().shift(-96).to_numpy()
    up=(fmax-c)/atr; dn=(c-fmin)/atr; yr=m["dt"].dt.year.to_numpy()
    BULL=IM.FVGKind.BULLISH
    def row(idx,ln):
        idx=np.array(sorted(set(int(x) for x in idx)),int); idx=idx[(idx>=0)&(idx<n-1)]
        ok=np.isfinite(up[idx])&np.isfinite(dn[idx]); idx=idx[ok]
        if len(idx)<150: return f"n={len(idx)}(thin)"
        a=np.median(up[idx])-np.median(dn[idx]) if ln>0 else np.median(dn[idx])-np.median(up[idx])
        return f"n={len(idx):5d} asym={a:+.2f}"
    def report(name,ev,ln):
        line=f"  {name}: {row(ev,ln)}"
        for pl,ym in [("D",yr<=2018),("C",(yr>=2019)&(yr<=2022)),("O",yr>=2023)]:
            ii=[x for x in ev if 0<=x<n and ym[x]]; line+=f" | {pl} {row(ii,ln)}"
        print(line)
    # ---- BRANCH-3 BPR ----
    bulls=[f for f in fvgs if f.kind is BULL]; bears=[f for f in fvgs if f.kind is not BULL]
    from collections import defaultdict
    bears_by_blk=defaultdict(list)
    for b in bears: bears_by_blk[b.block_index].append(b)
    bpr_bull=[]; bpr_bear=[]  # active polarity = second-forming gap
    for a in bulls:
        for b in bears_by_blk.get(a.block_index,()):
            if abs(a.formed_idx-b.formed_idx)>3: continue
            gap=max(a.lower,b.lower)-min(a.upper,b.upper)
            if gap>0: continue  # strict overlap tol=0
            # active polarity = later-forming gap
            if a.formed_idx>=b.formed_idx: bpr_bull.append(a.formed_idx)   # bull formed second -> bullish BPR
            else: bpr_bear.append(b.formed_idx)
    print(f"M13-BPR: fvgs={len(fvgs)} bull={len(bulls)} bear={len(bears)} BPR bull={len(bpr_bull)} bear={len(bpr_bear)}")
    report("BPR-bull -> LONG(up)",bpr_bull,1)
    report("BPR-bear -> SHORT(dn)",bpr_bear,-1)
    # ---- BRANCH-4 FVG-STACK/DENSITY ----
    K=20; bull_at=np.zeros(n); bear_at=np.zeros(n)
    for f in fvgs:
        j=f.formed_idx
        if 0<=j<n: (bull_at if f.kind is BULL else bear_at)[j]+=1
    bull_roll=pd.Series(bull_at).rolling(K).sum().to_numpy(); bear_roll=pd.Series(bear_at).rolling(K).sum().to_numpy()
    net=bull_roll-bear_roll
    stack_up=[i for i in range(K,n-1) if np.isfinite(net[i]) and net[i]>=2 and np.isfinite(atr[i]) and atr[i]>0]
    stack_dn=[i for i in range(K,n-1) if np.isfinite(net[i]) and net[i]<=-2 and np.isfinite(atr[i]) and atr[i]>0]
    print(f"M13-STACK (K={K}, |net|>=2): up-density n={len(stack_up)} dn-density n={len(stack_dn)}")
    report("STACK-up(net>=2) -> LONG",stack_up,1)
    report("STACK-dn(net<=-2) -> SHORT",stack_dn,-1)
    print("  => tradeable only if active-polarity asym robustly>0 across ALL partitions (predicts direction, not era-trend).")
if __name__=="__main__": main()
