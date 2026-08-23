"""m10_m11_struct.py — MODULAR_DISCOVERY_V1. M10 transition-EVENTS + M11 survival-without-invalidation. Ratified MK-01
market_structure (detect_swings -> label_structure -> detect_breaks; body-close BOS/CHoCH). CAUSAL (breaks use confirmed
swings < c; excursion strictly forward). Data cur_data M15 2011-2026. Partitions D<=2018 / C19-22 / O23+.

M10 (transition-event direction): after a CHoCH (change-of-character = reversal signal) does price move in the CHoCH
direction? after a BOS (continuation) does it continue? forward excursion-asym by break kind. Info-positive only if the
structural event carries directional info robustly across eras (not era-trend).

M11 (survival-no-invalidation): while bullish structure is ACTIVE (last break bullish, no bearish break yet), does
continuation (P up-1.5ATR-first) rise with survival age vs a bearish-active baseline? If flat across age bands & eras,
structural survival carries no ordering edge (non-directional negative)."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
import market_structure as MS
from market_structure import Block
def build_blocks(t):
    gaps=np.where(np.diff(t)>72*3600)[0]; bs=[]; start=0
    for g in gaps: bs.append(Block(start,g+1)); start=g+1
    bs.append(Block(start,len(t))); return bs
def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); t=m["time"].to_numpy(); n=len(m)
    blocks=build_blocks(t)
    swings=MS.label_structure(MS.detect_swings(h,l,blocks))
    breaks=MS.detect_breaks(c,swings,blocks)
    fmax=pd.Series(h).rolling(96).max().shift(-96).to_numpy(); fmin=pd.Series(l).rolling(96).min().shift(-96).to_numpy()
    up=(fmax-c)/atr; dn=(c-fmin)/atr; yr=m["dt"].dt.year.to_numpy()
    BK=MS.BreakKind
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
    # ---- M10 transition events ----
    ev={BK.CHOCH_BULL:[],BK.CHOCH_BEAR:[],BK.BOS_BULL:[],BK.BOS_BEAR:[]}
    for b in breaks:
        i=b.idx
        if 0<=i<n-1 and np.isfinite(atr[i]) and atr[i]>0: ev[b.kind].append(i)
    print(f"M10: breaks total={len(breaks)} CHoCH_bull={len(ev[BK.CHOCH_BULL])} CHoCH_bear={len(ev[BK.CHOCH_BEAR])} BOS_bull={len(ev[BK.BOS_BULL])} BOS_bear={len(ev[BK.BOS_BEAR])}")
    report("CHoCH-bull -> LONG",ev[BK.CHOCH_BULL],1)
    report("CHoCH-bear -> SHORT",ev[BK.CHOCH_BEAR],-1)
    report("BOS-bull   -> LONG",ev[BK.BOS_BULL],1)
    report("BOS-bear   -> SHORT",ev[BK.BOS_BEAR],-1)
    # ---- M11 survival-no-invalidation ----
    # build active-structure state + age from breaks (bull on bull break, bear on bear break)
    state=np.zeros(n,dtype=np.int8); age=np.zeros(n,dtype=np.int32)
    order=sorted(breaks,key=lambda b:b.idx); bi=0; cur=0; last_flip=0
    for i in range(n):
        while bi<len(order) and order[bi].idx==i:
            k=order[bi].kind
            s=1 if k in (BK.BOS_BULL,BK.CHOCH_BULL) else -1
            if s!=cur: cur=s; last_flip=i
            bi+=1
        state[i]=cur; age[i]=i-last_flip
    # P(up 1.5ATR first) via bounded 96-bar path scan
    def p_up_first(idx):
        idx=np.array(idx,int); wins=0; tot=0
        for i in idx:
            if i>=n-1 or not np.isfinite(atr[i]) or atr[i]<=0: continue
            tgt=1.5*atr[i]; hi=lo=None
            seg_h=h[i+1:i+97]; seg_l=l[i+1:i+97]
            uu=np.where(seg_h-c[i]>=tgt)[0]; dd=np.where(c[i]-seg_l>=tgt)[0]
            fu=uu[0] if len(uu) else 10**9; fd=dd[0] if len(dd) else 10**9
            if fu==fd==10**9: continue
            wins+= (fu<fd); tot+=1
        return wins/tot if tot else float('nan'), tot
    bull=np.where(state==1)[0]
    print("M11 survival (P up-1.5ATR-first | bull-structure-active, by age band):")
    for lo,hi in [(0,10),(10,30),(30,80),(80,200),(200,10**9)]:
        band=[i for i in bull if lo<=age[i]<hi]
        p,tot=p_up_first(band[:20000])  # cap for speed
        line=f"  age[{lo},{hi}): "+(f"P(up1st)={p:.3f} n={tot}" if tot>=150 else f"n={tot}(thin)")
        print(line)
    pb,tb=p_up_first(list(np.where(state==-1)[0])[:20000])
    print(f"  bear-active baseline: P(up1st)={pb:.3f} n={tb}")
    print("  => survival edge only if P(up1st) RISES materially with age above baseline & holds across eras.")
if __name__=="__main__": main()
