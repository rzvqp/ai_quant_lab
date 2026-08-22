"""VERIFY: frozen RANGE v4.4 CONFIRMED-macro count BY YEAR (warmup 2020-06 -> 2023-12-29). Confirms whether
the Alpha window (2021-2023) genuinely has zero CONFIRMED ranges or the prior collection had a bug."""
import sys, os, time, json
V44=r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\ve_n1_replay"; ALPHA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; WP5B=r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code"
os.environ.setdefault("RATIFIED_CODE_DIR", WP5B)
for p in (V44, ALPHA, os.path.join(ALPHA,"code"), WP5B):
    if p not in sys.path: sys.path.insert(0,p)
import pandas as pd
from ve_n1_replay.range_engine_v4_4 import RangeSemanticEngineV44
from ve_n1_replay.range_semantic_v4_4 import ConfigV44
from ve_n1_replay import Bar, build_info
from edge_research._common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"v44_years")
def log(m): print(f"[{int(time.time())}] {m}",flush=True); open(OUT+".log","a").write(f"{int(time.time())} {m}\n")
cfg=ConfigV44(); assert cfg.config_id().startswith("23d98c07")
d,_=load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
d=d[(d["dt"]>=pd.Timestamp("2020-06-01",tz="UTC"))&(d["dt"]<=pd.Timestamp("2023-12-29 23:59",tz="UTC"))].reset_index(drop=True)
N=len(d); log(f"VERIFY warmup+collect bars={N} span={d['dt'].iloc[0]}..{d['dt'].iloc[-1]}")
eng=RangeSemanticEngineV44(symbol="XAUUSD",timeframe="15m",bar_interval_seconds=900,
                           implementation_commit=build_info()["ai_source_commit"],range_config=cfg,acknowledge_construction_only=True)
o=d["open"].to_numpy();hi=d["high"].to_numpy();lo=d["low"].to_numpy();cl=d["close"].to_numpy();ts=d["time"].astype("int64").to_numpy();dt=d["dt"]
from collections import Counter
conf_by_year=Counter(); state_by_year={}; samples=[]
for i in range(N):
    bar=Bar(symbol="XAUUSD",ts_open=int(ts[i]),ts_close=int(ts[i])+900,open=float(o[i]),high=float(hi[i]),low=float(lo[i]),close=float(cl[i]),volume=100.0)
    _,rng,_=eng.observe_closed_bar(bar,as_of=None)
    y=dt.iloc[i].year; state_by_year.setdefault(y,Counter())[str(rng.macro_state)]+=1
    if rng.macro_state=="CONFIRMED":
        conf_by_year[y]+=1
        if dt.iloc[i]>=pd.Timestamp("2021-01-01",tz="UTC") and len(samples)<5:
            samples.append((str(dt.iloc[i]),rng.macro_boundary_upper,rng.macro_boundary_lower,rng.macro_id))
    if (i+1)%30000==0: log(f"{i+1}/{N} conf_by_year={dict(conf_by_year)}")
log(f"DONE conf_by_year={dict(conf_by_year)}")
for y in sorted(state_by_year): log(f"  {y}: {dict(state_by_year[y])}")
log(f"samples(2021+ confirmed): {samples}")
json.dump(dict(conf_by_year=dict(conf_by_year),state_by_year={y:dict(v) for y,v in state_by_year.items()},samples=samples),open(OUT+".json","w"),default=str)
log("VERIFY_COMPLETE")
