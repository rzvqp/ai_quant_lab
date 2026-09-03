"""srz_probe.py — de-risk: wire canonical OB (ob_core.detect_obs) + FVG (imbalance_mechanics.detect_fvgs) onto the bound mstrat panel,
confirm the V1 level universe binds, and count zones of each anchor class. No scoring."""
import os, sys, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
sys.path.insert(0, os.path.join(AA,"code")); sys.path.insert(0, OUT); sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import mstrat as MS, ob_core as OB
d=MS.load(); O=d["open"].to_numpy(float); H=d["high"].to_numpy(float); L=d["low"].to_numpy(float); C=d["close"].to_numpy(float); ATR=d["m_atr"].to_numpy(float); T=d["time"].to_numpy(); n=len(d)
EV1=pd.read_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_EVENTS.parquet")
print("IDENTITY:", len(EV1)==102458, int(EV1.accepted.sum())==72103)
# build ob_core P-dict from mstrat panel (same index as level universe)
K=20; DL=10
swH=pd.Series(H).rolling(K).max().shift(1).values; swL=pd.Series(L).rolling(K).min().shift(1).values
P=dict(o=O,h=H,l=L,c=C,atr=ATR,swH=swH,swL=swL,n=n)
ob_bull=OB.detect_obs(P,0.75,"bull"); ob_bear=OB.detect_obs(P,0.75,"bear")
print(f"OB bull={len(ob_bull)} bear={len(ob_bear)} | sample bull={ {k:round(v,2) if isinstance(v,float) else v for k,v in ob_bull[0].items()} if ob_bull else None}")
# FVG via canonical primitive
try:
    import imbalance_mechanics as IM
    from market_structure import Block
    gaps=np.where(np.diff(T)>72*3600)[0]; blocks=[]; start=0
    for g in gaps: blocks.append(Block(start,g+1)); start=g+1
    blocks.append(Block(start,n))
    fvgs=IM.detect_fvgs(H,L,blocks)
    bull=[f for f in fvgs if f.kind==IM.FVGKind.BULLISH]; bear=[f for f in fvgs if f.kind==IM.FVGKind.BEARISH]
    print(f"FVG total={len(fvgs)} bull={len(bull)} bear={len(bear)} | sample bull lower={bull[0].lower:.2f} upper={bull[0].upper:.2f} formed={bull[0].formed_idx} conf={bull[0].confirmed_idx}")
    print("FVG_AVAILABLE=YES")
except Exception as e:
    print("FVG_AVAILABLE=NO", repr(e))
# causal zigzag swings (for S/R + breakout-retest), theta 1.0 ATR (as lvl_v1)
def swings(theta):
    swh=np.full(n,np.nan); swl=np.full(n,np.nan); mode=0; hp=H[0]; lp=L[0]; csh=np.nan; csl=np.nan; conf_h=[]; conf_l=[]
    for j in range(1,n):
        th=theta*(ATR[j] if ATR[j]>0 else 1.0)
        if mode>=0:
            if H[j]>hp: hp=H[j]
            if hp-L[j]>=th: csh=hp; mode=-1; lp=L[j]; conf_h.append((j,csh))
        if mode<=0:
            if L[j]<lp: lp=L[j]
            if H[j]-lp>=th: csl=lp; mode=1; hp=H[j]; conf_l.append((j,csl))
        swh[j]=csh; swl[j]=csl
    return conf_h, conf_l
ch,cl=swings(1.0)
print(f"causal swings confirmed: highs={len(ch)} lows={len(cl)} (S/R + breakout-retest anchors)")
