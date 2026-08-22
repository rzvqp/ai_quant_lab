"""Run FROZEN RANGE v4.4 (3bb61cf, config_id 23d98c07) over M15_v2 through 2023-12-29 to recover CONFIRMED
MACRO range spans + boundaries for the ALPHA authorized window (2021-07-27..2023-12-29, matching native M5 DEV).
Full-history warmup (2011->) establishes correct causal macro state; COLLECT only >=2021-07-27 (Alpha DEV).
CONTEXT ONLY (no MI retuning). Source-only import; config_id verified. NO CALIB(2024+)/holdout/2025+."""
import sys, os, json, time
V44=r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\ve_n1_replay"; ALPHA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; WP5B=r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code"
os.environ.setdefault("RATIFIED_CODE_DIR", WP5B)
for p in (V44, ALPHA, os.path.join(ALPHA,"code"), WP5B):
    if p not in sys.path: sys.path.insert(0,p)
import numpy as np, pandas as pd
from ve_n1_replay.range_engine_v4_4 import RangeSemanticEngineV44
from ve_n1_replay.range_semantic_v4_4 import ConfigV44
from ve_n1_replay import Bar, build_info
from edge_research._common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"v44_alpha")
def log(m): print(f"[{int(time.time())}] {m}",flush=True); open(OUT+".log","a").write(f"{int(time.time())} {m}\n")
cfg=ConfigV44(); assert cfg.config_id()=="23d98c07488913c1c99a7397b2f8791f4727115e04bdefc283fb6bfc4a468969","config_id mismatch"
ALPHA_START=pd.Timestamp("2021-07-27",tz="UTC"); DEV_END=pd.Timestamp("2023-12-29 23:59",tz="UTC")
d,_=load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
d=d[d["dt"]<=DEV_END].reset_index(drop=True)   # warmup from 2011, stop at Alpha DEV end (no CALIB/2024+/2025+)
N=len(d); log(f"START V4.4 alpha-window run: warmup+collect bars={N} span={d['dt'].iloc[0]}..{d['dt'].iloc[-1]}")
n1_commit=build_info()["ai_source_commit"]
eng=RangeSemanticEngineV44(symbol="XAUUSD",timeframe="15m",bar_interval_seconds=900,
                           implementation_commit=n1_commit,range_config=cfg,acknowledge_construction_only=True)
o=d["open"].to_numpy();hi=d["high"].to_numpy();lo=d["low"].to_numpy();cl=d["close"].to_numpy();ts=d["time"].astype("int64").to_numpy();dt=d["dt"]
per_bar=[]; from collections import Counter; scount=Counter(); t0=time.time()
for i in range(N):
    bar=Bar(symbol="XAUUSD",ts_open=int(ts[i]),ts_close=int(ts[i])+900,open=float(o[i]),high=float(hi[i]),low=float(lo[i]),close=float(cl[i]),volume=100.0)
    n1r,rng,events=eng.observe_closed_bar(bar,as_of=None)
    ms=rng.macro_state; scount[str(ms)]+=1
    if ms=="CONFIRMED" and dt.iloc[i]>=ALPHA_START:   # COLLECT only Alpha DEV window
        u,l=rng.macro_boundary_upper,rng.macro_boundary_lower
        per_bar.append(dict(ts=int(ts[i]),upper=u,lower=l,macro_id=rng.macro_id,mid=(u+l)/2 if (u is not None and l is not None) else None))
    if (i+1)%30000==0: log(f"{i+1}/{N} confirmed_alpha={len(per_bar)} states={dict(scount)}")
out=dict(config_id=cfg.config_id(),contract_version="range-hierarchical-v4.4",n1_commit=n1_commit,
         warmup_from=str(d['dt'].iloc[0]),collect_from=str(ALPHA_START),collect_to=str(DEV_END),
         total_bars=N,alpha_confirmed_bars=len(per_bar),confirmed=per_bar,build_seconds=round(time.time()-t0,1))
json.dump(out,open(OUT+".json","w"),default=str)
log(f"SAVED {OUT}.json alpha_confirmed_bars={len(per_bar)} states={dict(scount)}")
log("V44_ALPHA_COMPLETE")
