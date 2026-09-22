import sys, os; sys.path.insert(0,'code'); sys.path.insert(0,'reports/alpha_discovery')
import mstrat, mstrat_ext as ME, edge2_null as EN, numpy as np, pandas as pd
from alpha_lab import CFG
OUT=r"reports/alpha_discovery"
d=EN.d; yr=pd.to_datetime(d['time'],unit='s',utc=True).dt.year.to_numpy()
mstrat.TICK=0.01
def scfg(rt): c=dict(CFG); c['spread_ticks']=rt/(2*mstrat.TICK); c['slip_ticks']=0.0; return c
def eval1(su,label):
    if not su or len(su)<150: print(f'{label}: thin ({0 if not su else len(su)})'); return
    trb=mstrat.simulate(d,su,scfg(0.05)); trs=mstrat.simulate(d,su,scfg(0.24))
    rb=trb.R.to_numpy(); rs=trs.R.to_numpy(); ei=trb.ei.to_numpy(); y=yr[ei]
    def eras(r): return [round(float(r[y<=2016].mean()),3),round(float(r[(y>=2017)&(y<=2021)].mean()),3),round(float(r[y>=2022].mean()),3)]
    m=EN.matched_null(su,0.025,reps=200)
    pf=rs[rs>0].sum()/(abs(rs[rs<=0].sum())+1e-9)
    print(f'{label}: N={len(rb)} BASE={rb.mean():+.4f} STRESS={rs.mean():+.4f} PF={pf:.2f} | BASEeras={eras(rb)} STRESSeras={eras(rs)} | null_capt={m["null_captures_pct"]:.0f}% p={m["p"]:.3f}')
print('=== S17 pw_high breakout NEIGHBORHOOD (robustness) ===')
for stop in ['atr','level']:
    for ex in ['rr2','rr3','time']:
        h=dict(level='pw_high',mode='breakout',stop=stop,exit=ex,family='S17')
        try: eval1(mstrat.s17_setups(d,h),f'S17 pw_high/{stop}/{ex}')
        except Exception as e: print('S17',stop,ex,'ERR',e)
print('\n=== NEAR-MISSES from full-hist screen (non-S49): top by worst calendar era ===')
R=pd.read_csv(OUT+r'/EDGE2_FULLHIST_SCREEN.csv')
R=R[~R.family.eq('S49')]
# near-miss = STRESS>0, PF>=1.15, N>=200, all-eras>=-0.02 (allow marginal), ranked by worst
nm=R[(R.STRESS>0)&(R.PF>=1.15)&(R.N>=200)].copy().sort_values('worst',ascending=False)
print(nm.head(18)[['hid','family','N','BASE','STRESS','PF','e1','e2','e3','worst','db5']].to_string(index=False))
