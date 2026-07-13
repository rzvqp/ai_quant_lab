"""Build GC 15-min OHLCV bars from local GCQ6 MBO (trades), 11 sessions."""
import databento as db, numpy as np, pandas as pd, glob, os
D2=r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\344b31d3-785f-43a4-b73b-d80a24bc18df\scratchpad\phaseb\data2"
OUTC=r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\344b31d3-785f-43a4-b73b-d80a24bc18df\scratchpad\phaseb\alpha\gc_15m.csv"
GCQ6=42011464; TICK=1e-1; BAR_NS=15*60*1_000_000_000
rows=[]
for f in sorted(glob.glob(D2+r"\glbx-mdp3-*.mbo.dbn.zst")):
    day=os.path.basename(f).split('-mdp3-')[1][:8]
    arr=db.DBNStore.from_file(f).to_ndarray()
    sel=arr[(arr['instrument_id']==GCQ6)&(arr['action']==b'T')]
    if len(sel)==0: continue
    ts=sel['ts_event'].astype(np.int64)
    px=sel['price'].astype(np.float64)/1e9      # to price units
    sz=sel['size'].astype(np.float64)
    bucket=(ts//BAR_NS)*BAR_NS
    dfd=pd.DataFrame({'bucket':bucket,'px':px,'sz':sz,'ts':ts})
    g=dfd.groupby('bucket')
    bars=pd.DataFrame({
        'ts': g['bucket'].first(),
        'open': g['px'].first(), 'high': g['px'].max(),
        'low': g['px'].min(), 'close': g['px'].last(),
        'volume': g['sz'].sum(), 'ntrades': g['px'].count(),
    }).reset_index(drop=True)
    bars['day']=day
    rows.append(bars)
allbars=pd.concat(rows,ignore_index=True).sort_values('ts').reset_index(drop=True)
# drop ultra-thin bars (need OHLC meaningful)
allbars=allbars[allbars['ntrades']>=5].reset_index(drop=True)
allbars['dt']=pd.to_datetime(allbars['ts'],unit='ns',utc=True)
allbars.to_csv(OUTC,index=False)
print("bars:",len(allbars)," span:",allbars['dt'].min(),"->",allbars['dt'].max())
print("per-day counts:"); print(allbars.groupby('day').size().to_string())
print(allbars[['dt','open','high','low','close','volume','ntrades']].head(4).to_string())
print("price range:",allbars['close'].min(),allbars['close'].max())
