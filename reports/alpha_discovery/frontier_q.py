"""frontier_q.py — FRONTIER Q: combine the TWO cross-era-stable findings. R26 (compression -> expansion, cross-era) =
movement potential; R29 (NY-afternoon long drift, cross-era) = direction; R27 (NY path-survival). Hypothesis: a
COMPRESSION event in the NY AFTERNOON (15-21 UTC) -> LONG (fixed direction from the drift, NOT the break direction).
Structural stop = compression low. Distinct from S5 (OR-breakout @13:00) and from generic compression breakout
(direction fixed by R29 drift, not the break). Ratified sb screen, STRESS, cross-era. SURVIVOR -> S5-independence.
"""
import numpy as np, pandas as pd, bscreen as bs
from batch_a import _mk, _hr_day
NB=8

def ny_pm_comp_long(fr, lo=15, hi=21):
    hr,_,_=_hr_day(fr); h=fr["high"]; l=fr["low"]; atr=fr["atr"].to_numpy(); atrm=fr["atr_ma"].to_numpy()
    box_hi=h.rolling(NB).max().shift(1).to_numpy(); box_lo=l.rolling(NB).min().shift(1).to_numpy()
    box=box_hi-box_lo; box_ma=pd.Series(box).rolling(50).mean().shift(1).to_numpy(); vr=atr/atrm
    comp=(box<0.7*box_ma)&(vr<0.9)&np.isfinite(box_ma)&(hr>=lo)&(hr<hi)
    return _mk(np.nan_to_num(comp.astype(float),nan=0).astype(bool),fr,box_lo,1)

HYPS=[
 dict(name="NYpm_comp_L(15-21)",info="R26xR29-combo",side=1,rr=2.0,horizon=48,signal=lambda f:ny_pm_comp_long(f,15,21)),
 dict(name="NYpm_comp_L(13-21)",info="R26xR29-combo",side=1,rr=2.0,horizon=48,signal=lambda f:ny_pm_comp_long(f,13,21)),
 dict(name="NYpm_comp_L_rr3(15-21)",info="R26xR29-combo-rr3",side=1,rr=3.0,horizon=64,signal=lambda f:ny_pm_comp_long(f,15,21)),
]

if __name__=="__main__":
    bs.run_batch(HYPS,title="Q (R26xR29 combo: NY-afternoon compression long)")
