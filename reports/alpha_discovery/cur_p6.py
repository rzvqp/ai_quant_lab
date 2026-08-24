"""cur_p6.py — CURRENT-REGIME SHORT specialist from the measured down-asymmetry (frequency 52% + down-excursion ~0.5
ATR bigger, sign-robust DISC/CONF/OOS). Tradeable form: in the current-like regime, SHORT with an ASYMMETRIC payoff
(stop 1.5*ATR up, target rr2 = 3*ATR down, capturing the larger down-excursion; rr motivated by the MEASURED asymmetry,
not fitted). Entry = mild down-context (close<ema20) so we short into the regime's direction, deduped. The regime itself
(current-like OFF-switch) is the primary condition. Re-screened partitioned DISC/CONF/OOS + S5-independence.
"""
import numpy as np
import cur_data as CD
from cur_screen import rescreen

def short_regime(fr, ctx="ema20"):
    c=fr["close"].to_numpy(); atr=fr["atr"].to_numpy(); n=len(fr)
    e=fr["ema20"].to_numpy() if ctx=="ema20" else fr["ema50"].to_numpy()
    ev=(c<e)&np.isfinite(atr)&(atr>0); idx=np.where(ev)[0]; idx=idx[idx<n-1]
    sl=1.5*atr[idx]
    return idx, sl

def short_plain(fr):  # no context filter: pure regime short (regime = the signal)
    c=fr["close"].to_numpy(); atr=fr["atr"].to_numpy(); n=len(fr)
    ok=np.isfinite(atr)&(atr>0); idx=np.where(ok)[0]; idx=idx[idx<n-1]; sl=1.5*atr[idx]
    return idx, sl

if __name__=="__main__":
    print("CURRENT-REGIME SHORT specialist (asymmetric payoff from measured down-excursion). current-like partition.")
    rescreen("SHORT_regime_ema20 rr2 (1.5ATR stop)", lambda f:short_regime(f,"ema20"), -1, 2.0, 96, cool=24)
    rescreen("SHORT_regime_ema20 rr2.5", lambda f:short_regime(f,"ema20"), -1, 2.5, 96, cool=24)
    rescreen("SHORT_regime_ema50 rr2", lambda f:short_regime(f,"ema50"), -1, 2.0, 96, cool=24)
    rescreen("SHORT_plain rr2 (regime=signal)", short_plain, -1, 2.0, 96, cool=24)
