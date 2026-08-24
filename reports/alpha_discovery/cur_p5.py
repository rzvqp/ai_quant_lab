"""cur_p5.py — CURRENT-REGIME Phase 4 (new discovery on FROZEN current-like; NO signature refinement/rescue).
Test aligned-SHORT structural events on the full frozen CURRENT_LIKE_POPULATION_V1: S5's own SHORT mirror (NY
opening-range BREAKDOWN short), London-open breakdown, and a wide-stop opening-range breakdown (survive high-vol chop).
A down-correction regime should favor aligned shorts IF the structure supplies a path-surviving direction. Exact defs,
STRESS, current-like DISC/CONF/OOS partition. Robust across full current-like DISC+CONF (+OOS) = current-regime survivor.
"""
import numpy as np, pandas as pd
from cur_screen import rescreen
from batch_a import orb, _mk, _hr_day

def orb_wide(fr, start_h, end_h, side, k=1.5):
    # opening-range breakdown/breakout with a WIDER stop (k*range beyond the opposite boundary) to survive high-vol chop
    orh,orl,bpos=__import__('batch_a').opening_range(fr,start_h,end_h); c=fr["close"].to_numpy(); inwin=(bpos>=4)&(bpos<=20)
    rng=orh-orl
    if side<0: ev=inwin&(c<orl); stop=orh+ (k-1.0)*rng
    else:      ev=inwin&(c>orh); stop=orl-(k-1.0)*rng
    return _mk(np.nan_to_num(ev.astype(float),nan=0).astype(bool),fr,stop,side)

if __name__=="__main__":
    print("CURRENT-REGIME Phase 4: aligned-SHORT structural events on FROZEN current-like (no rescue).")
    rescreen("ORB_NY_S (S5 short mirror) rr3", lambda f:orb(f,13,21,-1), -1, 3.0, 48)
    rescreen("ORB_NY_S rr2", lambda f:orb(f,13,21,-1), -1, 2.0, 48)
    rescreen("ORB_LON_S rr2", lambda f:orb(f,7,13,-1), -1, 2.0, 48)
    rescreen("ORB_NY_S_wide rr3", lambda f:orb_wide(f,13,21,-1,1.5), -1, 3.0, 48)
