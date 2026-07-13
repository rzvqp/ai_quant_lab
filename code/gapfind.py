import pandas as pd, numpy as np
m=pd.read_csv("data_market/OANDA_XAUUSD_M15.csv").drop_duplicates('time').sort_values('time').reset_index(drop=True)
m['dt']=pd.to_datetime(m['time'],unit='s',utc=True)
d=np.diff(m['time'].values)
# intra-session gap = >15min but < weekend(2d), excluding the daily ~1h break window
gapidx=np.where((d>900)&(d<2*86400))[0]
gaps=[]
for i in gapidx:
    t0=m['dt'].iloc[i]; t1=m['dt'].iloc[i+1]; mins=d[i]/60
    # skip the regular daily break: 21:00-22:00 UTC region with ~1h gap
    if mins<=75 and t0.hour in (20,21): continue
    gaps.append((t0,t1,int(mins)))
print(f"M15 bars={len(m)}  intra-session gaps(>15m, excl weekend & daily break)={len(gaps)}")
# cluster gaps into date windows to re-pull
gd=sorted(set(g[0].date() for g in gaps))
print(f"distinct gap dates={len(gd)}")
for g in gaps[:25]: print(f"  gap {g[0]} -> {g[1]}  ({g[2]} min)")
# missing bar estimate
miss=sum((g[2]//15 -1) for g in gaps)
print(f"estimated missing M15 bars ~ {miss}")
import json; json.dump([str(x) for x in gd], open("gap_dates.json","w"))
