"""Re-anchor H4/D1 to OANDA session boundary 17:00 America/New_York (DST-aware).
H1 = UTC hour (matches native). Then CROSS-CHECK vs native TradingView bars."""
import numpy as np, pandas as pd
D=r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\344b31d3-785f-43a4-b73b-d80a24bc18df\scratchpad\phaseb\alpha\data_market"
N=r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\344b31d3-785f-43a4-b73b-d80a24bc18df\scratchpad\phaseb\alpha\data_native"
m15=pd.read_csv(D+r"\OANDA_XAUUSD_M15.csv").drop_duplicates('time').sort_values('time').reset_index(drop=True)
m15['dt']=pd.to_datetime(m15['time'],unit='s',utc=True)
m15=m15[m15['dt']>=pd.Timestamp('2023-01-01',tz='UTC')].reset_index(drop=True)

def agg_by(df,key):
    df=df.assign(_k=key)
    g=df.groupby('_k')
    out=pd.DataFrame(dict(open=g['open'].first(),high=g['high'].max(),low=g['low'].min(),
                          close=g['close'].last(),volume=g['volume'].sum(),sub=g['close'].count())).reset_index()
    out=out.rename(columns={'_k':'dt'}).sort_values('dt').reset_index(drop=True)
    out['time']=((out['dt']-pd.Timestamp('1970-01-01',tz='UTC'))//pd.Timedelta(seconds=1)).astype('int64')
    return out

ny=m15['dt'].dt.tz_convert('America/New_York').dt.tz_localize(None)   # NY wall clock, naive
shift=ny-pd.Timedelta(hours=17)
def to_utc(naive_ny):
    return naive_ny.dt.tz_localize('America/New_York',ambiguous=True,nonexistent='shift_forward').dt.tz_convert('UTC')
d1key=to_utc(shift.dt.floor('D')+pd.Timedelta(hours=17))
h4key=to_utc(shift.dt.floor('4h')+pd.Timedelta(hours=17))
h1key=m15['dt'].dt.floor('1h')

H1=agg_by(m15,h1key); H4=agg_by(m15,h4key); D1=agg_by(m15,d1key)
# drop final incomplete/live bar per TF (M15 snapshot ends mid-period) — keep only fully-closed bars
m15_end=int(m15['time'].max())+900
H1=H1[H1['time']+3600<=m15_end].reset_index(drop=True)
H4=H4[H4['time']+4*3600<=m15_end].reset_index(drop=True)
D1=D1[D1['time']+23*3600<=m15_end].reset_index(drop=True)
for k,df in [('H1',H1),('H4',H4),('D1',D1)]:
    df.to_csv(D+rf"\OANDA_XAUUSD_{k}.csv",index=False,columns=['time','open','high','low','close','volume','sub'])
    print(f"re-anchored {k}: {len(df)} bars {df['dt'].min()} -> {df['dt'].max()}")

print("\n"+"="*70); print("CROSS-CHECK vs native TradingView bars (10 each, distributed incl DST)"); print("="*70)
def load_native(name):
    n=pd.read_csv(N+rf"\OANDA_XAUUSD_{name}.csv"); n['dt']=pd.to_datetime(n['time'],unit='s',utc=True); return n
def cross(name,mine,tol=0.05):
    nat=load_native(name)
    mrg=nat.merge(mine,on='time',how='inner',suffixes=('_n','_m'))
    if len(mrg)==0: print(f"[{name}] NO OVERLAP on timestamps -> anchoring mismatch"); return False,0
    # sample 10 distributed across the overlap (different months/years)
    idx=np.linspace(0,len(mrg)-1,10).astype(int)
    smp=mrg.iloc[idx]
    bad=0
    print(f"\n[{name}] overlap bars={len(mrg)}  sampled 10:")
    for _,r in smp.iterrows():
        do=abs(r['open_n']-r['open_m']); dh=abs(r['high_n']-r['high_m']); dl=abs(r['low_n']-r['low_m']); dc=abs(r['close_n']-r['close_m'])
        ok=max(do,dh,dl,dc)<=tol; bad+= 0 if ok else 1
        dt=pd.to_datetime(r['time'],unit='s',utc=True)
        print(f"   {dt}  O{r['open_n']:.2f}/{r['open_m']:.2f} H{r['high_n']:.2f}/{r['high_m']:.2f} L{r['low_n']:.2f}/{r['low_m']:.2f} C{r['close_n']:.2f}/{r['close_m']:.2f}  {'OK' if ok else 'MISMATCH'}")
    # full-overlap OHLC agreement rate
    allbad=int(((np.abs(mrg['open_n']-mrg['open_m'])>tol)|(np.abs(mrg['high_n']-mrg['high_m'])>tol)|(np.abs(mrg['low_n']-mrg['low_m'])>tol)|(np.abs(mrg['close_n']-mrg['close_m'])>tol)).sum())
    print(f"   full overlap OHLC mismatches (>{tol}): {allbad}/{len(mrg)}")
    return (allbad==0 and len(mrg)>=50), allbad
r1,_=cross('H1',H1); r2,_=cross('H4',H4); r3,_=cross('D1',D1)
print("\n"+"="*70); print(f"CROSS-CHECK VERDICT: {'PASS' if (r1 and r2 and r3) else 'FAIL'}"); print("="*70)
