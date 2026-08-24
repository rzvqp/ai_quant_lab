"""batch_c.py — BROAD DISCOVERY v2, Batch C. TIMEFRAME study (§23): the near-breakeven CONTINUATION/BREAKOUT
mechanisms from Batch A/B, re-run at H1 and H4 where the fixed 0.24 USD cost is negligible vs much larger moves.
Tests whether timeframe ownership converts the residual continuation signal to net-positive. Same ratified engine.
"""
import numpy as np, pandas as pd, bscreen as bs
from batch_a import _mk, swing
from batch_b import sb_break, vol_onset

def _ema(fr,span): return pd.Series(fr["close"].to_numpy()).ewm(span=span,adjust=True).mean().shift(1).to_numpy()

def trend_break(fr,side,K=10):   # trend-filtered Donchian continuation (ema20>ema50 & breakout)
    c=fr["close"].to_numpy(); e20=_ema(fr,20); e50=_ema(fr,50)
    dhi=pd.Series(fr["high"].to_numpy()).rolling(K).max().shift(1).to_numpy(); dlo=pd.Series(fr["low"].to_numpy()).rolling(K).min().shift(1).to_numpy()
    if side>0: return _mk((e20>e50)&(c>dhi),fr,dlo,side)
    else:      return _mk((e20<e50)&(c<dlo),fr,dhi,side)

def mech_set(tf,H,cool):
    return [
     dict(name=f"SB_break_L@{tf}",info="structure-break",side=1,rr=2.0,horizon=H,cool=cool,signal=lambda f:sb_break(f,1,10)),
     dict(name=f"SB_break_S@{tf}",info="structure-break",side=-1,rr=2.0,horizon=H,cool=cool,signal=lambda f:sb_break(f,-1,10)),
     dict(name=f"TREND_break_L@{tf}",info="trend/continuation",side=1,rr=2.0,horizon=H,cool=cool,signal=lambda f:trend_break(f,1)),
     dict(name=f"TREND_break_S@{tf}",info="trend/continuation",side=-1,rr=2.0,horizon=H,cool=cool,signal=lambda f:trend_break(f,-1)),
     dict(name=f"VOLonset_L@{tf}",info="volatility-onset",side=1,rr=2.0,horizon=H,cool=cool,signal=lambda f:vol_onset(f,1)),
     dict(name=f"VOLonset_S@{tf}",info="volatility-onset",side=-1,rr=2.0,horizon=H,cool=cool,signal=lambda f:vol_onset(f,-1)),
    ]

if __name__=="__main__":
    bs.run_batch(mech_set("H4",12,3), eras=bs.build_eras_tf("H4"), title="C-H4 (timeframe)")
    bs.run_batch(mech_set("H1",24,6), eras=bs.build_eras_tf("H1"), title="C-H1 (timeframe)")
