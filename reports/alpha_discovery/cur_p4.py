"""cur_p4.py — CURRENT-REGIME Phase 4: down-correction SHORT-RALLY specialist. In a down-context (EMA20<EMA50), fade a
bounce that rallies up to EMA20 but closes back below it (counter-trend rally rejected at resistance). Trend-aligned
short, better entry than a breakdown. Re-screened on CURRENT_LIKE_POPULATION_V1 (DISC/CONF/OOS partition), STRESS.
Also a variant requiring the rally to reach EMA50 (deeper resistance). Continues Phase 4 from the short-continuation lead.
"""
import numpy as np, pandas as pd
from cur_screen import rescreen
from batch_a import _mk

def short_rally(fr, ref="ema20"):
    c=fr["close"].to_numpy(); h=fr["high"].to_numpy(); e20=fr["ema20"].to_numpy(); e50=fr["ema50"].to_numpy()
    r=e20 if ref=="ema20" else e50
    down=e20<e50; ev=down&(h>=r)&(c<r)   # in downtrend, bar rallied to the EMA but closed back below (rejection)
    return _mk(np.nan_to_num(ev.astype(float),nan=0).astype(bool),fr,h,-1)

if __name__=="__main__":
    print("CURRENT-REGIME Phase 4: SHORT-RALLY (fade counter-trend bounce to EMA in down-context). current-like partition.")
    rescreen("SHORT_RALLY_ema20_rr2", lambda f:short_rally(f,"ema20"), -1, 2.0, 48)
    rescreen("SHORT_RALLY_ema20_rr3", lambda f:short_rally(f,"ema20"), -1, 3.0, 64)
    rescreen("SHORT_RALLY_ema50_rr2", lambda f:short_rally(f,"ema50"), -1, 2.0, 48)
    rescreen("SHORT_RALLY_ema50_rr3", lambda f:short_rally(f,"ema50"), -1, 3.0, 64)
