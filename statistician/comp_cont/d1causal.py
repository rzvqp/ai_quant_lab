"""STAT-COMP-CONT-L-RR2-INDEPENDENT-VALIDATION-001 -- Section 3: D1 causality determination.
Read-only. Measures the real temporal margin between the D1 bar used as context and the H4 bar it is
attached to, and contrasts it with the known legacy defect (merge_asof on bar-OPEN stamps).
"""
from __future__ import annotations
import sys, os
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AD = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
sys.path.insert(0, AD)
os.chdir(AD)
import swing_base as sb

tfs = sb.build_frames()
h4, d1 = tfs["H4"], tfs["D1"]
print(f"  H4 bars={len(h4)}  D1 bars={len(d1)}")
print(f"  H4 span {h4['dt'].min()} .. {h4['dt'].max()}")
print(f"  D1 span {d1['dt'].min()} .. {d1['dt'].max()}")

print("\n  COLUMN SEMANTICS (verified against m5_data.aggregate / swing_base._agg_d1):")
r = d1.iloc[5]
print(f"    D1 row 5: dt={r['dt']}  time(open)={pd.Timestamp(int(r['time']),unit='s',tz='UTC')}  "
      f"close_time={pd.Timestamp(int(r['close_time']),unit='s',tz='UTC')}")
r = h4.iloc[20]
print(f"    H4 row20: dt={r['dt']}  time(open)={pd.Timestamp(int(r['time']),unit='s',tz='UTC')}  "
      f"close_time={pd.Timestamp(int(r['close_time']),unit='s',tz='UTC')}")

d1 = d1.copy()
d1["d1_up"] = (d1["ema20"] > d1["ema50"]).astype(float)
h4c = sb.align_context(h4, d1, ["d1_up"], "_d1")
idx = h4c["_hidx"].to_numpy()
ok = idx >= 0
h4t = h4["time"].to_numpy().astype(np.int64)
d1ct = d1["close_time"].to_numpy().astype(np.int64)
margin = np.full(len(h4), np.nan)
margin[ok] = h4t[ok] - d1ct[idx[ok]]

print("\n" + "=" * 84)
print("  SECTION 3 -- CAUSAL MARGIN  (H4 bar OPEN time)  minus  (D1 context bar CLOSE time)")
print("=" * 84)
m = margin[np.isfinite(margin)]
print(f"    n={len(m)}  min={m.min()/3600:.2f}h  p1={np.percentile(m,1)/3600:.2f}h  "
      f"median={np.median(m)/3600:.2f}h  max={m.max()/3600:.2f}h")
print(f"    NEGATIVE margins (context from the FUTURE): {int((m < 0).sum())}")
print(f"    ZERO margins (context bar still forming) : {int((m == 0).sum())}")
print(f"    margins < 300s (last M5 candle of the D1 bar not yet closed): {int((m < 300).sum())}")
print(f"    => strictly causal at every H4 bar: {bool((m >= 300).all())}")

print("\n  CONTRAST WITH THE KNOWN LEGACY DEFECT (merge_asof on bar-OPEN stamps, as in econ_campaign.py):")
leg = pd.merge_asof(h4[["time"]].sort_values("time"),
                    d1[["time", "d1_up"]].rename(columns={"time": "av"}).sort_values("av"),
                    left_on="time", right_on="av", direction="backward")
legacy_up = leg["d1_up"].to_numpy() > 0.5
lidx = np.searchsorted(d1["time"].to_numpy().astype(np.int64), h4t, side="right") - 1
lok = lidx >= 0
lmargin = np.full(len(h4), np.nan)
lmargin[lok] = h4t[lok] - d1ct[lidx[lok]]
lm = lmargin[np.isfinite(lmargin)]
print(f"    legacy margin: min={lm.min()/3600:.2f}h  median={np.median(lm)/3600:.2f}h  "
      f"NEGATIVE (future) = {int((lm < 0).sum())} of {len(lm)} = {(lm < 0).mean():.1%}")

causal_up = h4c["d1_up_d1"].to_numpy() > 0.5
diff = causal_up != legacy_up
print(f"\n    bars where the CAUSAL flag differs from the LEGACY flag: {int(diff.sum())} of {len(h4)} "
      f"= {diff.mean():.3%}")
print(f"    => COMP-CONT uses the CAUSAL path; the legacy defect would have changed {int(diff.sum())} bars.")

np.save(r"C:\Users\MEDION~1\AppData\Local\Temp\cc\d1_up_causal.npy", causal_up)
np.save(r"C:\Users\MEDION~1\AppData\Local\Temp\cc\d1_up_legacy.npy", legacy_up)

print("\n" + "=" * 84)
print("  CACHE INTEGRITY -- build_frames(use_cache=True) reads parquet; is the cache stale?")
print("=" * 84)
CACHE = sb.CACHE
print(f"    cache dir: {CACHE}  exists={os.path.isdir(CACHE)}")
if os.path.isdir(CACHE):
    for f in sorted(os.listdir(CACHE)):
        p = os.path.join(CACHE, f)
        print(f"      {f:16} {os.path.getsize(p):>10,} bytes")
fresh = sb.build_frames(use_cache=False)
for tf in ("H4", "D1"):
    a, b = tfs[tf], fresh[tf]
    same_shape = a.shape == b.shape
    cols = [c for c in ("time", "open", "high", "low", "close", "close_time") if c in a.columns and c in b.columns]
    same_vals = all(np.allclose(a[c].to_numpy(dtype=float), b[c].to_numpy(dtype=float), equal_nan=True)
                    for c in cols) if same_shape else False
    print(f"    {tf}: cached shape {a.shape} vs fresh {b.shape}  identical OHLC/time: {same_shape and same_vals}")
