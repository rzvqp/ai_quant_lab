"""READ-ONLY state-transition audit of FROZEN RANGE v4.4 over 2020-01 -> 2022-06 (M15). Pins the last
CONFIRMED / last FORMING transition and the post-2020 candidate-slot behavior (single-active-macro slot).
Diagnosis only (S7). NO modification. config_id verified."""
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
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"v44_state_audit")
def log(m): print(f"[{int(time.time())}] {m}",flush=True); open(OUT+".log","a").write(f"{int(time.time())} {m}\n")
cfg=ConfigV44(); assert cfg.config_id().startswith("23d98c07")
d,_=load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
d=d[(d["dt"]>=pd.Timestamp("2020-01-01",tz="UTC"))&(d["dt"]<=pd.Timestamp("2022-06-30",tz="UTC"))].reset_index(drop=True)
N=len(d); log(f"AUDIT bars={N} span={d['dt'].iloc[0]}..{d['dt'].iloc[-1]}")
eng=RangeSemanticEngineV44(symbol="XAUUSD",timeframe="15m",bar_interval_seconds=900,
                           implementation_commit=build_info()["ai_source_commit"],range_config=cfg,acknowledge_construction_only=True)
o=d["open"].to_numpy();hi=d["high"].to_numpy();lo=d["low"].to_numpy();cl=d["close"].to_numpy();ts=d["time"].astype("int64").to_numpy();dt=d["dt"]
prev=None; transitions=[]; last_conf=None; last_form=None; conf_ids=set(); cand_ids_2021p=[]; cur_cand_id=None; cand_span={}
for i in range(N):
    bar=Bar(symbol="XAUUSD",ts_open=int(ts[i]),ts_close=int(ts[i])+900,open=float(o[i]),high=float(hi[i]),low=float(lo[i]),close=float(cl[i]),volume=100.0)
    _,rng,_=eng.observe_closed_bar(bar,as_of=None)
    ms=str(rng.macro_state); mid=rng.macro_id; day=str(dt.iloc[i])
    if ms=="CONFIRMED": last_conf=(day,mid); conf_ids.add(mid)
    if ms=="FORMING": last_form=(day,mid)
    if ms!=prev:
        transitions.append((day,prev,ms,mid)); prev=ms
    # track macro_id lifetime for post-2021 (candidate slot behavior)
    if dt.iloc[i]>=pd.Timestamp("2021-01-01",tz="UTC") and mid is not None:
        cand_span.setdefault(mid,[day,day,set()]); cand_span[mid][1]=day; cand_span[mid][2].add(ms)
    if (i+1)%40000==0: log(f"{i+1}/{N} last_conf={last_conf} last_form={last_form}")
# post-2021 candidate slot: how many distinct macro_ids, how long each persists, what states
post21=sorted(cand_span.items(), key=lambda kv:kv[0] if kv[0] else -1)
log(f"last_CONFIRMED transition: {last_conf}")
log(f"last_FORMING  transition: {last_form}")
log(f"distinct CONFIRMED macro_ids (whole audit): {len(conf_ids)}")
log(f"post-2021 distinct macro_ids (slot occupants): {len(post21)}")
for mid,(a,b,states) in post21[:12]:
    log(f"   macro_id={mid}: {a} -> {b} states={sorted(states)}")
log(f"transition tail (last 15): {transitions[-15:]}")
json.dump(dict(last_conf=last_conf,last_form=last_form,n_conf_ids=len(conf_ids),
               post21_ids=[(m,a,b,sorted(list(s))) for m,(a,b,s) in post21],
               transitions=transitions),open(OUT+".json","w"),default=str)
log("STATE_AUDIT_COMPLETE")
