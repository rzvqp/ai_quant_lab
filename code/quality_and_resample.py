"""PHASE 1 (resample) + PHASE 2 (Quality Gate) for OANDA:XAUUSD.
Base = M15 (replay-built). Build H1/H4/D1 by controlled UTC resampling (all TFs sync-derived
from the same M15 -> guaranteed consistency). Then run the Quality Gate and report PASS/FAIL."""
import numpy as np, pandas as pd, os
D=r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\344b31d3-785f-43a4-b73b-d80a24bc18df\scratchpad\phaseb\alpha\data_market"
m15=pd.read_csv(D+r"\OANDA_XAUUSD_M15.csv").drop_duplicates('time').sort_values('time').reset_index(drop=True)
m15['dt']=pd.to_datetime(m15['time'],unit='s',utc=True)
m15=m15[m15['dt']>=pd.Timestamp('2023-01-01',tz='UTC')].reset_index(drop=True)

def resample(df, rule):
    g=df.set_index('dt').resample(rule,label='left',closed='left',origin='epoch')
    o=g['open'].first(); h=g['high'].max(); l=g['low'].min(); c=g['close'].last()
    v=g['volume'].sum(); cnt=g['close'].count()
    out=pd.DataFrame(dict(open=o,high=h,low=l,close=c,volume=v,sub=cnt)).dropna(subset=['open']).reset_index()
    out['time']=((out['dt']-pd.Timestamp('1970-01-01',tz='UTC'))//pd.Timedelta(seconds=1)).astype('int64'); return out

tfs={'M15':m15.copy()}
tfs['H1']=resample(m15,'1h'); tfs['H4']=resample(m15,'4h'); tfs['D1']=resample(m15,'1D')
for k in tfs:
    if 'sub' not in tfs[k]: tfs[k]['sub']=1
    tfs[k].to_csv(D+rf"\OANDA_XAUUSD_{k}.csv",index=False,columns=['time','open','high','low','close','volume','sub'])

print("="*74); print("PHASE 2 — QUALITY GATE  (OANDA:XAUUSD, base M15 via Replay)"); print("="*74)
def gate(name,df,expected_sub=None,step=None):
    dt=pd.to_datetime(df['time'],unit='s',utc=True)
    dups=int(df['time'].duplicated().sum())
    mono=bool((np.diff(df['time'].values)>0).all())
    ohlc_bad=int(((df['high']<df[['open','close']].max(axis=1))|(df['low']>df[['open','close']].min(axis=1))|(df['high']<df['low'])).sum())
    zerorange=int((df['high']==df['low']).sum())
    # gaps
    diffs=np.diff(df['time'].values);
    gaps=int((diffs>1.8*step).sum()) if step else 0
    maxgap_h=float(diffs.max()/3600) if len(diffs) else 0
    # sub-bar consistency
    sub_bad=0
    if expected_sub: sub_bad=int((df['sub']>expected_sub).sum())
    coverage_ok = dt.min()<=pd.Timestamp('2023-01-05',tz='UTC')
    verdict = (dups==0 and mono and ohlc_bad==0 and (expected_sub is None or sub_bad==0) and coverage_ok)
    print(f"\n[{name}] first={dt.min()}  last={dt.max()}  bars={len(df)}")
    print(f"    duplicates={dups}  monotonic_utc={mono}  ohlc_invalid={ohlc_bad}  zero_range={zerorange}")
    print(f"    gaps(> {1.8 if step else '-'}x step)={gaps}  max_gap={maxgap_h:.1f}h  sub>{expected_sub}={sub_bad}")
    print(f"    coverage_from_2023={coverage_ok}   VERDICT: {'PASS' if verdict else 'FAIL'}")
    return verdict
v1=gate('M15',tfs['M15'],step=900)
v2=gate('H1', tfs['H1'], expected_sub=4, step=3600)
v3=gate('H4', tfs['H4'], expected_sub=16, step=4*3600)
v4=gate('D1', tfs['D1'], expected_sub=96, step=86400)

# cross-TF sync check: H1 high == max of its M15 highs (sample)
def sync_check():
    m=tfs['M15'].copy(); m['h1']=pd.to_datetime(m['time'],unit='s',utc=True).dt.floor('1h')
    agg=m.groupby('h1')['high'].max().reset_index()
    h1=tfs['H1'].copy(); h1['h1']=pd.to_datetime(h1['time'],unit='s',utc=True)
    merged=h1.merge(agg,on='h1',how='inner',suffixes=('_h1','_m15'))
    bad=int((np.abs(merged['high_h1']-merged['high_m15'])>1e-6).sum())
    return bad
sb=sync_check()
print(f"\n[SYNC] H1.high vs max(M15.high) mismatches: {sb}")
allpass=all([v1,v2,v3,v4]) and sb==0
print("\n"+"="*74); print(f"QUALITY GATE OVERALL: {'PASS' if allpass else 'FAIL'}"); print("="*74)
