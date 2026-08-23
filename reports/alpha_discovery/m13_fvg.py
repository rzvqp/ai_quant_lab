"""m13_fvg.py — MODULAR_DISCOVERY_V1, M13 IMBALANCE/FVG (info-first §8/§9). Uses the RATIFIED MK-03 primitive (wp5b/code
imbalance_mechanics: detect_fvgs 3-bar gap low[i+1]>high[i-1], detect_fvg_reactions CE50 touch). Economic hypothesis: on revisit
to a Fair Value Gap's CE50, price reacts in the gap's polarity (bull-FVG=demand→up, bear-FVG=supply→down). INFO TEST: forward
path (up-dn excursion, P(target-first) at +/-1.5ATR) from the CE50-touch bar, bull vs bear, partitioned DISC<=2018/CONF 2019-22/
OOS 2023+. Only if info supports -> tradeable (CAND-0003 DEMO geometry). Causal (reaction uses only bars up to ce50_touch).
Blocks = >72h-gap segments (ratified convention). Data cur_data M15 2011-2026."""
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
    fvgs=IM.detect_fvgs(h,l,blocks); reacts=IM.detect_fvg_reactions(h,l,c,fvgs,blocks)
    # forward path helper
    fmax=pd.Series(h).rolling(96).max().shift(-96).to_numpy(); fmin=pd.Series(l).rolling(96).min().shift(-96).to_numpy()
    up=(fmax-c)/atr; dn=(c-fmin)/atr; yr=m["dt"].dt.year.to_numpy()
    BULL=IM.FVGKind.BULLISH if hasattr(IM.FVGKind,'BULLISH') else list(IM.FVGKind)[0]
    ev_bull=[]; ev_bear=[]
    for r in reacts:
        i=r.ce50_touch_idx
        if i is None or i<0 or i>=n-1 or not np.isfinite(atr[i]) or atr[i]<=0: continue
        (ev_bull if r.kind==BULL else ev_bear).append(i)
    ev_bull=np.array(ev_bull,int); ev_bear=np.array(ev_bear,int)
    print(f"M13 FVG info: fvgs={len(fvgs)} reactions(CE50-touch)={len(reacts)} bull={len(ev_bull)} bear={len(ev_bear)} (BULL={BULL})")
    def row(idx, lens):  # lens=+1 long(want up), -1 short(want dn)
        idx=idx[(idx<n-1)]; ok=np.isfinite(up[idx])&np.isfinite(dn[idx]); idx=idx[ok]
        if len(idx)<150: return f"n={len(idx)}(thin)"
        asym=np.median(up[idx])-np.median(dn[idx]) if lens>0 else np.median(dn[idx])-np.median(up[idx])
        return f"n={len(idx):5d} favorable-excursion-asym={asym:+.2f}"
    for nm,ev,ln in [("BULL-FVG -> LONG(up)",ev_bull,1),("BEAR-FVG -> SHORT(dn)",ev_bear,-1)]:
        line=f"  {nm}: {row(ev,ln)}"
        for pl,ym in [("DISC<=2018",yr<=2018),("CONF19-22",(yr>=2019)&(yr<=2022)),("OOS23+",yr>=2023)]:
            line+=f" | {pl} {row(ev[np.isin(ev,np.where(ym)[0])],ln)}"
        print(line)
    print("  => M13 info supports a tradeable test only if favorable-asym robustly>0 across partitions (polarity predicts direction).")
if __name__=="__main__": main()
