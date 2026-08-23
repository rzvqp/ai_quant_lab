"""batch_b.py — BROAD DISCOVERY v2, Batch B. Untested information classes (§19/§32), NOT Batch-A clones:
structure-break (BOS/Donchian), range-rotation fade, HOLD-confirmed displacement continuation (R6 — the one
component that carried real info in S10), MTF-alignment, streak exhaustion (S14), volatility-onset (S25),
narrow-range breakout (S48/49). Mechanism-owned structural stops, causal. LONG/SHORT separate (§22).
Runs through bscreen (ratified sb engine, STRESS 0.24, eras b0/b1/DEV/CAL, cross-era sign).
"""
import numpy as np, pandas as pd, bscreen as bs
from batch_a import _mk, swing, sma

def _sh(a,k):  # causal shift by k
    return pd.Series(a).shift(k).to_numpy()

def sb_break(fr,side,K=12):   # structure break / Donchian continuation
    c=fr["close"].to_numpy(); dhi=pd.Series(fr["high"].to_numpy()).rolling(K).max().shift(1).to_numpy()
    dlo=pd.Series(fr["low"].to_numpy()).rolling(K).min().shift(1).to_numpy()
    if side>0: return _mk(c>dhi,fr,dlo,side)
    else:      return _mk(c<dlo,fr,dhi,side)

def range_fade(fr,side,K=20):  # range rotation: fade the extreme in a calm/non-trend regime
    h=fr["high"].to_numpy(); l=fr["low"].to_numpy(); c=fr["close"].to_numpy(); atr=fr["atr"].to_numpy(); vr=(fr["atr"]/fr["atr_ma"]).to_numpy()
    rhi=pd.Series(h).rolling(K).max().shift(1).to_numpy(); rlo=pd.Series(l).rolling(K).min().shift(1).to_numpy()
    calm=vr<1.0
    if side>0: return _mk((l<=rlo)&(c>rlo)&calm,fr,rlo-0.3*atr,side)
    else:      return _mk((h>=rhi)&(c<rhi)&calm,fr,rhi+0.3*atr,side)

def hold_disp(fr,side):  # displacement that HOLDS its origin -> continuation (R6). enter bar AFTER the hold-confirm bar.
    o=fr["open"].to_numpy(); c=fr["close"].to_numpy(); h=fr["high"].to_numpy(); l=fr["low"].to_numpy()
    atr=fr["atr"].to_numpy(); rng=h-l; n=len(fr)
    if side>0: disp=((c-o)>0.7*atr)&(c>l+0.75*rng)&(rng>1.2*atr); origin=l
    else:      disp=((o-c)>0.7*atr)&(c<l+0.25*rng)&(rng>1.2*atr); origin=h
    disp=np.nan_to_num(disp.astype(float),nan=0).astype(bool); di=np.where(disp)[0]; di=di[di<n-2]
    cN=c[di+1]  # confirm bar close
    hold = (cN>origin[di]) if side>0 else (cN<origin[di])
    di=di[hold]; sig=di+1  # entry = open[di+2]
    entry=o[sig+1] if False else o[sig+1] if (sig+1<n).all() else None
    keep=sig<n-1; sig=sig[keep]; di=di[keep]
    entry=o[sig+1]; sl=np.abs(entry-origin[di]); return sig,sl

def mtf_align(fr,side,K=12):  # H4-trend proxy (SMA200 rising) + SMA50>SMA200 + fresh breakout; long only
    c=fr["close"].to_numpy(); s200=sma(fr,200); s50=sma(fr,50); dhi=pd.Series(fr["high"].to_numpy()).rolling(K).max().shift(1).to_numpy()
    _,lo=swing(fr,8)
    rising=s200>_sh(s200,20); align=rising&(s50>s200)&(c>dhi)
    return _mk(align,fr,lo,side)

def streak_fade(fr,side,ns=3):  # exhaustion: fade after ns consecutive same-dir closes (S14)
    c=fr["close"].to_numpy(); up=np.r_[False,c[1:]>c[:-1]]; dn=np.r_[False,c[1:]<c[:-1]]
    def run(x,k):
        s=pd.Series(x.astype(int)); r=s.rolling(k).sum().to_numpy(); return r>=k
    hi,lo=swing(fr,4)
    if side<0: return _mk(run(up,ns),fr,pd.Series(fr["high"].to_numpy()).rolling(ns).max().to_numpy()+0.0,side)
    else:      return _mk(run(dn,ns),fr,pd.Series(fr["low"].to_numpy()).rolling(ns).min().to_numpy()+0.0,side)

def vol_onset(fr,side):  # atr crosses above atr_ma -> trade direction of the onset bar (S25)
    o=fr["open"].to_numpy(); c=fr["close"].to_numpy(); vr=(fr["atr"]/fr["atr_ma"]).to_numpy(); _,lo=swing(fr,6); hi,_=swing(fr,6)
    onset=(vr>1.0)&(_sh(vr,1)<=1.0)
    if side>0: return _mk(onset&(c>o),fr,lo,side)
    else:      return _mk(onset&(c<o),fr,hi,side)

def nr_break(fr,side):  # narrow-range bar then breakout (S48/49)
    o=fr["open"].to_numpy(); c=fr["close"].to_numpy(); h=fr["high"].to_numpy(); l=fr["low"].to_numpy(); atr=fr["atr"].to_numpy()
    rng=h-l; nr_prev=_sh(rng,1)<0.6*_sh(atr,1)
    if side>0: return _mk(nr_prev&(c>_sh(h,1)),fr,_sh(l,1),side)
    else:      return _mk(nr_prev&(c<_sh(l,1)),fr,_sh(h,1),side)

HYPS=[
 dict(name="SB_break_L",info="structure-break/BOS",side=1,rr=2.0,horizon=48,signal=lambda f:sb_break(f,1)),
 dict(name="SB_break_S",info="structure-break/BOS",side=-1,rr=2.0,horizon=48,signal=lambda f:sb_break(f,-1)),
 dict(name="RANGE_fade_L",info="range-rotation",side=1,rr=2.0,horizon=48,signal=lambda f:range_fade(f,1)),
 dict(name="RANGE_fade_S",info="range-rotation",side=-1,rr=2.0,horizon=48,signal=lambda f:range_fade(f,-1)),
 dict(name="HOLDdisp_L(R6)",info="momentum/hold-displacement",side=1,rr=2.0,horizon=48,signal=lambda f:hold_disp(f,1)),
 dict(name="HOLDdisp_S(R6)",info="momentum/hold-displacement",side=-1,rr=2.0,horizon=48,signal=lambda f:hold_disp(f,-1)),
 dict(name="MTF_align_L",info="multi-timeframe",side=1,rr=2.0,horizon=48,signal=lambda f:mtf_align(f,1)),
 dict(name="STREAKfade_S",info="exhaustion",side=-1,rr=2.0,horizon=48,signal=lambda f:streak_fade(f,-1)),
 dict(name="STREAKfade_L",info="exhaustion",side=1,rr=2.0,horizon=48,signal=lambda f:streak_fade(f,1)),
 dict(name="VOLonset_L",info="volatility-onset",side=1,rr=2.0,horizon=48,signal=lambda f:vol_onset(f,1)),
 dict(name="VOLonset_S",info="volatility-onset",side=-1,rr=2.0,horizon=48,signal=lambda f:vol_onset(f,-1)),
 dict(name="NR_break_L",info="narrow-range breakout",side=1,rr=2.0,horizon=48,signal=lambda f:nr_break(f,1)),
 dict(name="NR_break_S",info="narrow-range breakout",side=-1,rr=2.0,horizon=48,signal=lambda f:nr_break(f,-1)),
]

if __name__=="__main__":
    bs.run_batch(HYPS,title="B (untested classes)")
