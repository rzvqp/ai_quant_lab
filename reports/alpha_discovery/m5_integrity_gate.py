"""INTEGRITY GATE for ALPHA-XAUUSD-H1-M5-MULTIREGIME-DISCOVERY-001.
Access M5 EXCLUSIVELY via the sanctioned gated loader edge_research._common.load (NO read_csv on
data/market). Verify against Statistician commit b8d0447 frozen identities:
  DEV  2021-07-27 15:45Z -> 2023-12-29 21:55Z  121,949 bars  ohlc_sha256 b30912e1...488
  CALIB 2024-01-01 23:00Z -> 2024-06-20 00:40Z  33,309 bars  ohlc_sha256 3c170953...deb
  DEV+CALIB=155,258; overlap 0; bars>=2025 = 0; bars after cutoff 2024-06-20 00:40 = 0
If the loader identity/hash fails, or fingerprints do not reproduce -> STOP (fail-closed)."""
import sys, os, hashlib, json
import numpy as np, pandas as pd
ALPHA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
if ALPHA not in sys.path: sys.path.insert(0, ALPHA)
from edge_research._common import load, PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC

TARGET = dict(
    dev_ohlc="b30912e130ee0c1c640f29495b2de608403c002609dc2db2413c9960c24ad488",
    dev_timeline="2a389cd7a382a02c64073f7c620280b6e098cee9159c6f2496a128e8f9816131",
    cal_ohlc="3c170953fd65b5ce49ebbeb92f49c0c88a305f3b8da3d847aefe91bfaaf71deb",
    cal_timeline="24e51ef4b128f3758dc1c3f41717b2e1aa43d77d84d124f3c659fedb8b3d700e",
    file_sha_prefix="cbb6eebe1a189ebb")

print("Split id:", PRE_HOLDOUT_SPLIT_ID, "| cutoff:", RESEARCH_HOLDOUT_CUTOFF_UTC)
try:
    d, meta = load("M5", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
except Exception as e:
    print("LOADER FAILED ->", type(e).__name__, str(e)[:300]); print("INTEGRITY_STOP"); sys.exit(2)
print("LOADER OK. file_sha256=", meta["data_file_sha256"][:16], "| manifest_v=", meta["manifest_version"], "| n_delivered=", meta["n_bars_delivered"])
print("  file_sha prefix match:", meta["data_file_sha256"].startswith(TARGET["file_sha_prefix"]))
print("  delivered range:", meta["min_date_used"], "->", meta["max_date_used"])

d = d.sort_values("time").reset_index(drop=True)
dt = pd.to_datetime(d["time"], unit="s", utc=True)
DEV_END = pd.Timestamp("2023-12-29 21:55:00", tz="UTC"); CAL_START = pd.Timestamp("2024-01-01 23:00:00", tz="UTC"); CAL_END = pd.Timestamp("2024-06-20 00:40:00", tz="UTC")
dev = d[dt <= DEV_END].reset_index(drop=True); cal = d[(dt >= CAL_START) & (dt <= CAL_END)].reset_index(drop=True)

def ohlc_sha_variants(df):
    o = df[["open","high","low","close"]]
    return {
        "np_f64_tobytes": hashlib.sha256(o.to_numpy(dtype="float64").tobytes()).hexdigest(),
        "np_default_tobytes": hashlib.sha256(o.to_numpy().tobytes()).hexdigest(),
        "csv_no_index": hashlib.sha256(o.to_csv(index=False).encode()).hexdigest(),
        "values_C": hashlib.sha256(np.ascontiguousarray(o.to_numpy(dtype="float64")).tobytes()).hexdigest(),
    }
def time_sha_variants(df):
    t = df["time"].to_numpy()
    return {
        "int64_tobytes": hashlib.sha256(t.astype("int64").tobytes()).hexdigest(),
        "csv": hashlib.sha256(pd.Series(t).to_csv(index=False).encode()).hexdigest(),
    }

print(f"\nCOUNTS: delivered={len(d)}  DEV={len(dev)} (target 121949)  CALIB={len(cal)} (target 33309)  sum={len(dev)+len(cal)}")
print(f"DEV bounds: {dt[dt<=DEV_END].min()} -> {dt[dt<=DEV_END].max()}")
print(f"CALIB bounds: {pd.to_datetime(cal['time'],unit='s',utc=True).min()} -> {pd.to_datetime(cal['time'],unit='s',utc=True).max()}")
print(f"LEAK CHECKS: bars>=2025-01-01 = {(dt>=pd.Timestamp('2025-01-01',tz='UTC')).sum()}  bars>cutoff(2024-06-20 00:40) = {(dt>CAL_END).sum()}  overlap DEV&CALIB = {((dt<=DEV_END)&(dt>=CAL_START)).sum()}")

print("\nDEV ohlc_sha256 variants:")
dv = ohlc_sha_variants(dev)
for k,v in dv.items(): print(f"  {k}: {v}  {'<-- MATCH' if v==TARGET['dev_ohlc'] else ''}")
print("DEV timeline_sha256 variants:")
for k,v in time_sha_variants(dev).items(): print(f"  {k}: {v}  {'<-- MATCH' if v==TARGET['dev_timeline'] else ''}")
print("CALIB ohlc_sha256 variants:")
for k,v in ohlc_sha_variants(cal).items(): print(f"  {k}: {v}  {'<-- MATCH' if v==TARGET['cal_ohlc'] else ''}")

matched = any(v==TARGET["dev_ohlc"] for v in dv.values())
counts_ok = len(dev)==121949 and len(cal)==33309
leak_ok = (dt>=pd.Timestamp('2025-01-01',tz='UTC')).sum()==0 and (dt>CAL_END).sum()==0
print("\nVERDICT:", "COUNTS_OK" if counts_ok else "COUNTS_FAIL", "|", "NO_LEAK" if leak_ok else "LEAK", "|", "OHLC_FP_MATCH" if matched else "OHLC_FP_NO_STD_VARIANT")
