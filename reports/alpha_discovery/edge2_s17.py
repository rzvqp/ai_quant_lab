import sys, os; sys.path.insert(0,'code'); sys.path.insert(0,'reports/alpha_discovery')
import mstrat, edge2_null as EN, numpy as np, pandas as pd
from alpha_lab import CFG
d=EN.d; yr=pd.to_datetime(d['time'],unit='s',utc=True).dt.year.to_numpy()
print('S17_DIMS=', getattr(mstrat,'S17_DIMS',None))
def stress_cfg():
    c=dict(CFG); c['spread_ticks']=0.24/(2*mstrat.TICK); c['slip_ticks']=0.0; return c
for lvl in ['pw_high','pw_low']:
    h=dict(level=lvl,mode='breakout',stop='atr',exit='rr2',family='S17')
    try:
        su=mstrat.s17_setups(d,h)
        m=EN.matched_null(su,0.025,reps=300)
        tr=mstrat.simulate(d,su,stress_cfg()); r=tr.R.to_numpy(); ei=tr.ei.to_numpy(); y=yr[ei]
        e=[round(float(r[y<=2016].mean()),3),round(float(r[(y>=2017)&(y<=2021)].mean()),3),round(float(r[y>=2022].mean()),3)]
        rec=r[y>=2025]
        v='EDGE' if (m['p']<0.05 and m['excess']>0) else 'long-timing-beta'
        print('S17 %s breakout: N=%d real=%+.4f null=%+.4f excess=%+.4f null_capt=%.0f%% p=%.4f | STRESS eras=%s recent2025=%+.3f(n%d) -> %s' % (
            lvl, m['N'], m['real_rr_mean'], m['null_mean'], m['excess'], m['null_captures_pct'], m['p'], e, (rec.mean() if len(rec) else float('nan')), len(rec), v))
    except Exception as ex:
        import traceback; print(lvl,'ERR',ex); traceback.print_exc()
