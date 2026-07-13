import pandas as pd, numpy as np
D="data_market"; N="data_native"
for name,exp in [('D1',96),('H4',16),('H1',4)]:
    mine=pd.read_csv(f"{D}/OANDA_XAUUSD_{name}.csv"); nat=pd.read_csv(f"{N}/OANDA_XAUUSD_{name}.csv")
    m=nat.merge(mine,on='time',suffixes=('_n','_m'))
    bad=m[(np.abs(m['open_n']-m['open_m'])>0.05)|(np.abs(m['high_n']-m['high_m'])>0.05)|(np.abs(m['low_n']-m['low_m'])>0.05)|(np.abs(m['close_n']-m['close_m'])>0.05)].copy()
    bad['dt']=pd.to_datetime(bad['time'],unit='s',utc=True)
    last_native=pd.to_datetime(nat['time'].max(),unit='s',utc=True)
    edge=(bad['dt']>=last_native-pd.Timedelta(days=10)).sum()
    print(f"\n[{name}] total mismatches={len(bad)}  in last 10 days={edge}  (native last={last_native})")
    print("  mismatch dates + my sub-count:")
    for _,r in bad.sort_values('dt').tail(12).iterrows():
        print(f"    {r['dt']}  sub={int(r['sub'])}  dHLC=({r['high_n']-r['high_m']:.2f},{r['low_n']-r['low_m']:.2f},{r['close_n']-r['close_m']:.2f})")
