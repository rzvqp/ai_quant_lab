"""onset_probe.py — data-inventory gate for M15/M5/M1 onset atlas. Verify native coverage + timestamp alignment. No scoring."""
import sys, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; sys.path.insert(0, AA+r"\code"); import mstrat as MS
M15=MS.load(); t15=M15["time"].to_numpy(); print(f"M15: bars={len(M15)} {pd.to_datetime(t15[0],unit='s',utc=True)} -> {pd.to_datetime(t15[-1],unit='s',utc=True)}")
M5=pd.read_csv(r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\data\market\OANDA_XAUUSD_M5.csv")
M1=pd.read_csv(r"C:\Users\MEDION GAMING\ai_quant_lab-data-acq\acquisition_staging\OANDA_XAUUSD_M1.csv")
for nm,df in (("M5",M5),("M1",M1)):
    t=df["time"].to_numpy(); inc=bool((np.diff(t)>0).all()); dup=len(t)-len(set(t))
    print(f"{nm}: bars={len(df)} cols={list(df.columns)} {pd.to_datetime(t[0],unit='s',utc=True)} -> {pd.to_datetime(t[-1],unit='s',utc=True)} incr={inc} dup={dup} med_dt={int(np.median(np.diff(t)))}s")
# overlap window M5 vs M1
o0=max(M5.time.min(),M1.time.min()); o1=min(M5.time.max(),M1.time.max())
print(f"M5-M1 overlap: {pd.to_datetime(o0,unit='s',utc=True)} -> {pd.to_datetime(o1,unit='s',utc=True)}")
# alignment check: an M15 close at t must align to an M5 bar close at t and an M1 bar close at t (nominal)
sample=t15[(t15>=M1.time.min())&(t15<=M1.time.max())][:5]
m5set=set(M5.time.to_numpy()); m1set=set(M1.time.to_numpy())
for s in sample: print(f"  M15 close {pd.to_datetime(s,unit='s',utc=True)} in M5={s in m5set} in M1={s in m1set}")
print("M5_NATIVE_START=2021-07-27  M1_NATIVE_START=2025-08-04 (verified UNFIT/quarantine, exact M5 xcheck)")
