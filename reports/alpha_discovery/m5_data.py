"""FIREWALL-COMPLIANT data layer for ALPHA-XAUUSD-H1-M5-MULTIREGIME-DISCOVERY-001.
M5 accessed EXCLUSIVELY via edge_research._common.load (NO read_csv on data/market).
H1 loader key is SEALED (AWAITING_REGIME_MAP) -> build M15/H1/H4 by CAUSAL aggregation from the gated M5.
DEV (2021-07-27->2023-12-29, 121,949) for features/selection; CALIB (2024-01->2024-06-20, 33,309) robustness only.
NO N4 (zone_confirmation/market_bus.confirmations), NO shadow_driver. Cost: tick 0.01, STRESS RT 0.24."""
import sys, os
import numpy as np, pandas as pd
ALPHA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
if ALPHA not in sys.path: sys.path.insert(0, ALPHA)
from edge_research._common import load, PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC

TICK = 0.01
DEV_END = pd.Timestamp("2023-12-29 21:55:00", tz="UTC")
CAL_START = pd.Timestamp("2024-01-01 23:00:00", tz="UTC")
CAL_END = pd.Timestamp("2024-06-20 00:40:00", tz="UTC")

def load_m5():
    d, meta = load("M5", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    d = d.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    d["dt"] = pd.to_datetime(d["time"], unit="s", utc=True)
    return d, meta

_FREQ = {"M15": "15min", "H1": "1h", "H4": "4h"}
_MINSUB = {"M15": 2, "H1": 6, "H4": 24}  # min M5 sub-bars to accept an aggregated HTF bar

def aggregate(m5, tf):
    """Causal OHLC aggregation of gated M5 -> tf. Bucket by floor(dt). HTF bar 'time' = bucket start epoch,
    'close_time' = last M5 time in bucket (when the bar is actually complete/known). Keep bars with >= min sub-bars."""
    if tf == "M5":
        x = m5.copy(); x["nsub"] = 1; x["close_time"] = x["time"]; return x.reset_index(drop=True)
    g = m5.assign(bucket=m5["dt"].dt.floor(_FREQ[tf])).groupby("bucket")
    agg = g.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"),
                volume=("volume", "sum"), nsub=("open", "size"), open_time=("time", "first"),
                close_time=("time", "last")).reset_index()
    agg = agg[agg["nsub"] >= _MINSUB[tf]].reset_index(drop=True)
    agg["dt"] = agg["bucket"]; agg["time"] = agg["open_time"].astype("int64")  # genuine first-M5 epoch (not tz-astype)
    return agg[["time", "dt", "open", "high", "low", "close", "volume", "nsub", "close_time"]]

def add_features(df):
    """Causal features (no lookahead). ATR14, EMA20/50, rolling 20/50 high/low (shifted), body/range, dir."""
    o, h, l, c = df["open"].to_numpy(), df["high"].to_numpy(), df["low"].to_numpy(), df["close"].to_numpy()
    tr = np.maximum(h - l, np.maximum(np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1)))); tr[0] = h[0] - l[0]
    df["atr"] = pd.Series(tr).rolling(14).mean().to_numpy()
    df["ema20"] = pd.Series(c).ewm(span=20, adjust=True).mean().to_numpy()
    df["ema50"] = pd.Series(c).ewm(span=50, adjust=True).mean().to_numpy()
    for w in (20, 50):
        df[f"hh{w}"] = pd.Series(h).rolling(w).max().shift(1).to_numpy()
        df[f"ll{w}"] = pd.Series(l).rolling(w).min().shift(1).to_numpy()
    # directional efficiency over 20 (net/path) -> range vs trend
    net = c - pd.Series(c).shift(20).to_numpy()
    path = pd.Series(np.abs(np.diff(c, prepend=c[0]))).rolling(20).sum().shift(1).to_numpy()
    df["effic"] = np.where(path > 0, net / path, np.nan)
    df["atr_ma"] = pd.Series(df["atr"]).rolling(30).mean().shift(1).to_numpy()
    return df

def regime_label(df):
    """Causal regime label from this TF's own features (mechanically defined; DEV-only calibration not needed
    since rules are structural). TREND_UP/DOWN via EMA20 vs EMA50 + efficiency; RANGE via |effic| low +
    ATR-compression; TRANSITION via compression->expansion or fresh EMA cross."""
    e20, e50, eff, atr, atr_ma = (df[k].to_numpy() for k in ("ema20", "ema50", "effic", "atr", "atr_ma"))
    up = (e20 > e50) & (eff > 0.30)
    dn = (e20 < e50) & (eff < -0.30)
    rng = (np.abs(eff) < 0.20)
    cross = np.zeros(len(df), bool); c20 = (e20 > e50)
    cross[1:] = c20[1:] != c20[:-1]
    expansion = (atr > 1.3 * atr_ma)
    trans = cross | (rng & expansion)
    lab = np.full(len(df), "REGIME_INDEPENDENT", dtype=object)
    lab[rng] = "RANGE"; lab[up] = "TREND_UP"; lab[dn] = "TREND_DOWN"; lab[trans] = "TRANSITION"
    df["regime"] = lab
    return df

def build():
    m5, meta = load_m5()
    tfs = {}
    for tf in ("M5", "M15", "H1", "H4"):
        x = aggregate(m5, tf); x = add_features(x)
        if tf in ("H1", "H4"): x = regime_label(x)
        x["is_dev"] = x["dt"] <= DEV_END; x["is_cal"] = (x["dt"] >= CAL_START) & (x["dt"] <= CAL_END)
        tfs[tf] = x
    return tfs, meta

if __name__ == "__main__":
    tfs, meta = build()
    print("loader file_sha:", meta["data_file_sha256"][:16], "manifest_v:", meta["manifest_version"])
    for tf, x in tfs.items():
        dev = x[x["is_dev"]]; cal = x[x["is_cal"]]
        rc = dev["regime"].value_counts().to_dict() if "regime" in x else {}
        print(f"{tf}: total={len(x)} DEV={len(dev)} CALIB={len(cal)} range={x['dt'].min()}..{x['dt'].max()}"
              + (f" nsub[min/med/max]={x['nsub'].min()}/{int(x['nsub'].median())}/{x['nsub'].max()}" if tf!='M5' else ""))
        if rc: print(f"     DEV regimes: {rc}")
    # leak assertions
    for tf, x in tfs.items():
        assert (x["dt"] <= CAL_END).all(), f"{tf} LEAK past cutoff"
        assert (x["dt"] < pd.Timestamp("2025-01-01", tz="UTC")).all(), f"{tf} LEAK 2025+"
    print("LEAK ASSERTIONS PASSED (no bar > 2024-06-20 00:40, none >= 2025).")
