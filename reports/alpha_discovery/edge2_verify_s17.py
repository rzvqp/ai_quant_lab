import sys, os; sys.path.insert(0,'code'); sys.path.insert(0,'reports/alpha_discovery')
import mstrat, edge2_null as EN, numpy as np, pandas as pd
from alpha_lab import CFG
d=EN.d; yr=pd.to_datetime(d['time'],unit='s',utc=True).dt.year.to_numpy()
mstrat.TICK=0.01
def scfg(rt): c=dict(CFG); c['spread_ticks']=rt/(2*mstrat.TICK); c['slip_ticks']=0.0; return c
h=dict(level='pw_high',mode='breakout',stop='atr',exit='rr3',family='S17')
su=mstrat.s17_setups(d,h)
trb=mstrat.simulate(d,su,scfg(0.05)); trs=mstrat.simulate(d,su,scfg(0.24))
rb=trb.R.to_numpy(); rs=trs.R.to_numpy(); ei=trb.ei.to_numpy(); y=yr[ei]; N=len(rb)
pf=rs[rs>0].sum()/(abs(rs[rs<=0].sum())+1e-9); wr=(rs>0).mean()
# tail
S=np.sort(rs)[::-1]; k5=max(1,int(N*0.05)); k10=max(1,int(N*0.10))
db5=(rs.sum()-S[:k5].sum())/(N-k5); db10=(rs.sum()-S[:k10].sum())/(N-k10)
# 400-rep null
m=EN.matched_null(su,0.025,reps=400)
# yearly (STRESS)
yy=pd.Series(rs).groupby(y).agg(['size','mean','sum'])
posyr=(yy['mean']>0).sum(); totyr=len(yy)
print('=== S17 pw_high / ATR / rr3  (weekly-high breakout LONG) — real cost ===')
print(f'N={N} ({N/15:.0f}/yr) WR={wr:.3f} BASE={rb.mean():+.4f} STRESS={rs.mean():+.4f} PF={pf:.3f}')
print(f'tail: drop-best-5%={db5:+.4f} drop-best-10%={db10:+.4f}  (both should stay >~0 for non-outlier edge)')
print(f'matched-timing null (400 reps): real={m["real_rr_mean"]:+.4f} null={m["null_mean"]:+.4f} excess={m["excess"]:+.4f} null_captures={m["null_captures_pct"]:.0f}% p={m["p"]:.4f}')
print(f'STRESS eras: 2011-16={rs[y<=2016].mean():+.4f}  2017-21={rs[(y>=2017)&(y<=2021)].mean():+.4f}  2022-26={rs[y>=2022].mean():+.4f}')
print(f'STRESS positive years: {posyr}/{totyr}')
print('year | n | mean STRESS R:')
for yv,row in yy.iterrows(): print(f'  {int(yv)}: n={int(row["size"]):4d} mean={row["mean"]:+.4f}')
