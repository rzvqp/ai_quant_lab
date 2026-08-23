"""frontier_p.py — FRONTIER P: can the R29 NY-afternoon cross-era-stable LONG drift be AMPLIFIED into a tradeable,
S5-independent edge by a NON-opening-range trigger? S5 amplifies the drift via the OR breakout at NY OPEN (13:00);
this tests a distinct amplifier = a MOMENTUM (up-displacement) entry in the NY AFTERNOON (15-21 UTC) itself. Long only
(drift is long). Structural stop = displacement bar low. Ratified sb screen, STRESS, cross-era. If SURVIVOR ->
§30 S5-independence (S5 fires 13:00 OR-break; this fires 15-21 displacement -> plausibly different events/bars).
"""
import numpy as np, pandas as pd, bscreen as bs
from batch_a import _mk, _hr_day

def ny_pm_disp(fr, lo=15, hi=21):
    hr,_,_=_hr_day(fr); o=fr["open"].to_numpy(); c=fr["close"].to_numpy(); h=fr["high"].to_numpy(); l=fr["low"].to_numpy(); atr=fr["atr"].to_numpy(); rng=h-l
    up=((c-o)>0.7*atr)&(c>l+0.75*rng)&(rng>1.2*atr)&(hr>=lo)&(hr<hi)
    return _mk(np.nan_to_num(up.astype(float),nan=0).astype(bool),fr,l,1)

HYPS=[
 dict(name="NYpm_disp_L(15-21)",info="session-drift-amplifier",side=1,rr=2.0,horizon=48,signal=lambda f:ny_pm_disp(f,15,21)),
 dict(name="NYpm_disp_L(13-21)",info="session-drift-amplifier",side=1,rr=2.0,horizon=48,signal=lambda f:ny_pm_disp(f,13,21)),
]

if __name__=="__main__":
    bs.run_batch(HYPS,title="P (NY-afternoon drift amplifier)")
