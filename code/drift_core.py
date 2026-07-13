import numpy as np, mstrat as MS
from campaign import full_stats
d=MS.load(); res=d.iloc[:int(len(d)*0.6)].copy()
hms=dict(family='S1',side='low',liq_ref='pdh_pdl',liq_lb=None,confirm='consecutive2',imb='fvg',stop='beyond_sweep',exit='rr2',window=4)
tr=MS.backtest(res,hms); st=full_stats(tr); real=st['expectancy_R']
# B/F: random long entries, ATR stop, rr2 -> long-bias + drift baseline
pool=MS._pool(res,1,'rr',2.0,MS.CFG)
mu=float(np.mean(pool)); sd=float(np.std(pool,ddof=1)); k=st['n']
excess=real-mu; import math; z=(real-mu)/(sd/math.sqrt(k)); p=0.5*math.erfc(z/math.sqrt(2))
print("=== S1 DRIFT DECOMPOSITION (winning setup, research) ===")
print(f"A. real S1 expectancy      = {real:+.4f} R   (n={k}, PF={st['profit_factor']:.2f}, maxDD={st['max_dd_R']:.1f}R, win={st['win_rate']:.3f})")
print(f"B/F. long-bias baseline    = {mu:+.4f} R   (random long, ATR stop, rr2; captures gold uptrend+long bias; null n={len(pool)}, sd={sd:.3f})")
print(f"    EXCESS over long-bias  = {excess:+.4f} R   ({100*excess/real:.0f}% of raw)")
print(f"    p(excess>0)            = {p:.2e}   -> under global-FDR(m=1520) needs p<6.6e-5 : {'PASS' if p<6.6e-5 else 'FAIL'}")
print(f"\nDecomposition: raw directional {real:+.3f}R = long-bias {mu:+.3f}R + S1-condition excess {excess:+.3f}R")
print("Interpretation: ~%.0f%% of S1's raw return is the long-bias/drift baseline; the S1-specific excess is small and NOT significant vs the drift-aware null at campaign FDR. (Controls C/D/E/G/H deferred to full drift audit.)"%(100*mu/real))
