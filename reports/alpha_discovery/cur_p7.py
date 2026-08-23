"""cur_p7.py — capture the current-like down-asymmetry with PATH SURVIVAL: wide-stop / time-exit SHORT. Tight stops
died on the ~4.25 ATR up-bounces (R27). Here: short in current-like, WIDE stop (3-4 ATR, survives bounces), far target
(rarely hit) so most trades exit at the 24h horizon = net down-drift capture. If net-short return robustly positive
across DISC/CONF/OOS after STRESS -> current-regime short-drift specialist; else down-asymmetry is real-but-untradeable.
"""
import numpy as np
import cur_data as CD
from cur_screen import rescreen

def short_wide(fr, katr):
    c=fr["close"].to_numpy(); atr=fr["atr"].to_numpy(); n=len(fr); e20=fr["ema20"].to_numpy()
    ev=(c<e20)&np.isfinite(atr)&(atr>0); idx=np.where(ev)[0]; idx=idx[idx<n-1]; sl=katr*atr[idx]
    return idx, sl

if __name__=="__main__":
    print("CURRENT-REGIME wide-stop/time-exit SHORT (capture net down-drift with path survival). current-like partition.")
    rescreen("SHORT_wide 3ATR rr3 H96", lambda f:short_wide(f,3.0), -1, 3.0, 96, cool=24)
    rescreen("SHORT_wide 4ATR rr3 H96", lambda f:short_wide(f,4.0), -1, 3.0, 96, cool=24)
    rescreen("SHORT_wide 3ATR rr3 H192(2day)", lambda f:short_wide(f,3.0), -1, 3.0, 192, cool=48)
    rescreen("SHORT_wide 4ATR rr4 H192", lambda f:short_wide(f,4.0), -1, 4.0, 192, cool=48)
