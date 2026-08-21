"""Run frozen V4.4 (3bb61cf, config_id 23d98c07) over the DEVELOPMENT partition (blocks 1-2, <2018-05) to
collect CONFIRMED MACRO range spans + boundaries for H08. Source-only import; acknowledge_construction_only.
DEVELOPMENT only (no VALIDATION/SEALED). Low-memory streaming; saves compact JSON."""
import sys, os, json, time, hashlib
V44 = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\ve_n1_replay"
ALPHA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; WP5B = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code"
os.environ.setdefault("RATIFIED_CODE_DIR", WP5B)
for p in (V44, ALPHA, os.path.join(ALPHA, "code"), WP5B):
    if p not in sys.path: sys.path.insert(0, p)
try:
    import ctypes; ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
except Exception: pass
import numpy as np, pandas as pd
from ve_n1_replay.range_engine_v4_4 import RangeSemanticEngineV44
from ve_n1_replay.range_semantic_v4_4 import ConfigV44
from edge_research._common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "v44_dev")
def log(m):
    print(f"[{int(time.time())}] {m}", flush=True); open(OUT + ".log", "a").write(f"{int(time.time())} {m}\n")

cfg = ConfigV44(); assert cfg.config_id() == "23d98c07488913c1c99a7397b2f8791f4727115e04bdefc283fb6bfc4a468969", "config_id mismatch"
log(f"START V4.4 dev run config_id={cfg.config_id()[:16]}")
d, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
dev = d[d["dt"] < pd.Timestamp("2018-05-01", tz="UTC")].reset_index(drop=True)   # DEVELOPMENT = blocks 1-2
N = len(dev); log(f"DEVELOPMENT bars={N} span={dev['dt'].iloc[0]}..{dev['dt'].iloc[-1]}")
# N1 implementation commit pin (from ve_n1_replay build_info)
import ve_n1_replay as R; n1_commit = R.build_info()["ai_source_commit"]
eng = RangeSemanticEngineV44(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900,
                             implementation_commit=n1_commit, range_config=cfg, acknowledge_construction_only=True)
# import the engine's Bar type expectation: it takes ts_close, open_, high, low, close, atr, trend_context
# Use the wrapper's observe_closed_bar with the N1-provided ATR (engine composes N1 -> do not feed own ATR).
from ve_n1_replay import Bar
o = dev["open"].to_numpy(); hi = dev["high"].to_numpy(); lo = dev["low"].to_numpy(); cl = dev["close"].to_numpy()
ts = dev["time"].astype("int64").to_numpy()
confirmed_bars = []; states = {}; per_bar = []   # per_bar: (idx, ts, macro_state, upper, lower, macro_id)
from collections import Counter
scount = Counter(); t0 = time.time()
for i in range(N):
    bar = Bar(symbol="XAUUSD", ts_open=int(ts[i]), ts_close=int(ts[i]) + 900, open=float(o[i]), high=float(hi[i]),
              low=float(lo[i]), close=float(cl[i]), volume=100.0)
    n1r, rng, events = eng.observe_closed_bar(bar, as_of=None)
    ms = rng.macro_state; scount[str(ms)] += 1
    if ms == "CONFIRMED":
        confirmed_bars.append(i)
        per_bar.append(dict(idx=i, ts=int(ts[i]), upper=rng.macro_boundary_upper, lower=rng.macro_boundary_lower,
                            macro_id=rng.macro_id, mid=(rng.macro_boundary_upper + rng.macro_boundary_lower) / 2
                            if (rng.macro_boundary_upper is not None and rng.macro_boundary_lower is not None) else None))
    if (i + 1) % 20000 == 0:
        log(f"{i+1}/{N} ({(time.time()-t0)/(i+1)*1000:.2f} ms/bar) confirmed_bars={len(confirmed_bars)} states={dict(scount)}")
out = dict(config_id=cfg.config_id(), contract_version="range-hierarchical-v4.4", n1_commit=n1_commit,
           dev_bars=N, dev_span=[str(dev["dt"].iloc[0]), str(dev["dt"].iloc[-1])],
           state_counts=dict(scount), n_confirmed_bars=len(confirmed_bars),
           confirmed_frac=round(len(confirmed_bars) / N, 6), confirmed=per_bar, build_seconds=round(time.time() - t0, 1))
json.dump(out, open(OUT + ".json", "w"), indent=1, default=str)
log(f"SAVED {OUT}.json confirmed_bars={len(confirmed_bars)}/{N} ({out['confirmed_frac']}) states={dict(scount)}")
log("V44_DEV_COMPLETE")
