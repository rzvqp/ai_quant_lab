"""vol_predict.py — Frontier K: forward-VOLATILITY predictability (information-first, NON-directional). Direction is
era-trend (R20); this asks whether the VOLATILITY dimension is cross-era-stable. Causal vol-state (vr=atr/atr_ma,
compression) -> forward realized volatility (max favorable/adverse excursion over next H bars, from passage). Two tests:
(1) does current vr-tercile rank-order forward range cross-era? (vol persistence/clustering)
(2) after a COMPRESSION event, is the forward expansion magnitude reliable + large cross-era? (compression->expansion timing)
Reports cross-era stability of vol prediction vs the known direction instability. Info only; honest tradeability note.
"""
import numpy as np, pandas as pd
import bscreen as bs
from state_path_m15 import passage_m15
from batch_a import _hr_day
HB=48; NB=8; PIP=0.10

def comp_mask(fr):
    h=fr["high"]; l=fr["low"]; atr=fr["atr"].to_numpy(); atrm=fr["atr_ma"].to_numpy()
    box_hi=h.rolling(NB).max().shift(1).to_numpy(); box_lo=l.rolling(NB).min().shift(1).to_numpy()
    box=box_hi-box_lo; box_ma=pd.Series(box).rolling(50).mean().shift(1).to_numpy(); vr=atr/atrm
    comp=(box<0.7*box_ma)&(vr<0.9)&np.isfinite(box_ma)
    return np.nan_to_num(comp.astype(float),nan=0).astype(bool), box, atr

def main():
    print(f"Frontier K: forward-VOL predictability (non-directional). H={HB//4}h. fwd range/exc in ATR units. Cross-era.")
    eras=bs.build_eras()
    # passage per underlying frame
    frames={}
    for tag,fr,mask in eras: frames.setdefault(id(fr),fr)
    PSG={k:passage_m15(v,Hmax=HB) for k,v in frames.items()}
    print("\n[Test 1] current vr-tercile -> median forward RANGE (mfe+mae, in ATR). Does vol persist cross-era?")
    for tag,fr,mask in eras:
        ou,od,mfe,mae=PSG[id(fr)]; atr=fr["atr"].to_numpy(); vr=(fr["atr"]/fr["atr_ma"]).to_numpy()
        fwd=(mfe+mae)*PIP/atr   # forward total range in ATR units
        m=mask&np.isfinite(vr)&np.isfinite(fwd)
        q=np.nanquantile(vr[m],[0.33,0.66])
        lo=m&(vr<q[0]); mid=m&(vr>=q[0])&(vr<q[1]); hi=m&(vr>=q[1])
        print(f"  {tag:4s}: vr_lo->{np.nanmedian(fwd[lo]):.2f}  vr_mid->{np.nanmedian(fwd[mid]):.2f}  vr_hi->{np.nanmedian(fwd[hi]):.2f}  (monotone={np.nanmedian(fwd[lo])<np.nanmedian(fwd[mid])<np.nanmedian(fwd[hi])})")
    print("\n[Test 2] COMPRESSION event -> forward MAX one-directional excursion (ATR units) + P(>1.5 ATR). Reliable expansion?")
    for tag,fr,mask in eras:
        ou,od,mfe,mae=PSG[id(fr)]; atr=fr["atr"].to_numpy(); comp,box,_=comp_mask(fr)
        maxexc=np.maximum(mfe,mae)*PIP/atr; m=mask&comp&np.isfinite(maxexc)
        idx=np.where(m)[0];
        if len(idx)<30: print(f"  {tag:4s}: n{len(idx)} thin"); continue
        # also expansion vs the compressed box width
        exc_pips=np.maximum(mfe,mae)[idx]; bw=(box[idx]/PIP)
        ratio=exc_pips/np.maximum(bw,1e-9)
        print(f"  {tag:4s}: nComp={len(idx)} medMaxExc={np.nanmedian(maxexc[idx]):.2f}ATR P(>1.5ATR)={np.nanmean(maxexc[idx]>1.5):.2f} medExc/boxW={np.nanmedian(ratio):.2f} medExc={np.nanmedian(exc_pips):.0f}p")
    print("\n[Baseline] unconditional forward MAX excursion (ATR) for reference:")
    for tag,fr,mask in eras:
        ou,od,mfe,mae=PSG[id(fr)]; atr=fr["atr"].to_numpy(); maxexc=np.maximum(mfe,mae)*PIP/atr; m=mask&np.isfinite(maxexc)
        print(f"  {tag:4s}: medMaxExc={np.nanmedian(maxexc[m]):.2f}ATR P(>1.5ATR)={np.nanmean(maxexc[m]>1.5):.2f}")

if __name__=="__main__":
    main()
