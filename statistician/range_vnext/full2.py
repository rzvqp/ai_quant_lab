from __future__ import annotations
import sys, os, json, time, collections
import pandas as pd, numpy as np
WP=r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b"; sys.path.insert(0, os.path.join(WP,"ve_n1_replay"))
from ve_n1_replay import Bar
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay.range_engine_v4_4 import RangeSemanticEngineV44
from ve_n1_replay.range_engine_vnext import RangeSemanticEngineVNext
from ve_n1_replay.range_semantic_v4_4 import ConfigV44
from ve_n1_replay.range_semantic_vnext import ConfigVNext
KW=dict(symbol="XAUUSD",timeframe="15m",bar_interval_seconds=900,implementation_commit=IC)
OUT=r"C:\Users\MEDION~1\AppData\Local\Temp\vnext"
def rec(st):
    return dict(sid=int(st.structure_id), start=getattr(st,"start_ts",None), conf=getattr(st,"confirm_ts",None),
        end=getattr(st,"end_ts",None), reason=getattr(st,"end_reason",None),
        bu=getattr(st,"boundary_upper",None), bl=getattr(st,"boundary_lower",None),
        confirmed=bool(getattr(st,"reached_confirmed",False)),
        cont=getattr(st,"continued_from_id",None), pred=getattr(st,"predecessor_id",None))
def go(which):
    d=pd.read_csv(os.path.join(WP,"data","market","OANDA_XAUUSD_M15.csv"))
    tt=d["time"].to_numpy();o=d["open"].to_numpy();h=d["high"].to_numpy();l=d["low"].to_numpy();c=d["close"].to_numpy()
    if which=="v44": eng=RangeSemanticEngineV44(range_config=ConfigV44(),acknowledge_construction_only=True,**KW)
    else: eng=RangeSemanticEngineVNext(range_config=ConfigVNext(),acknowledge_construction_only=True,**KW)
    prod=eng._range
    seen={}
    t0=time.perf_counter()
    for k in range(len(d)):
        bar=Bar(symbol="XAUUSD",ts_open=int(tt[k]),ts_close=int(tt[k])+900,open=float(o[k]),high=float(h[k]),low=float(l[k]),close=float(c[k]),volume=100.0)
        eng.observe_closed_bar(bar)
        # cheap capture: raw objects, attribute reads only, no snapshot serialization
        for st in prod._macro_history:
            sid=int(st.structure_id)
            if sid not in seen or seen[sid].get("end") is None: seen[sid]=rec(st)
        act = prod._active_macros.values() if which=="vnext" else ([prod._active_macro] if getattr(prod,"_active_macro",None) else [])
        for st in act:
            sid=int(st.structure_id)
            if sid not in seen: seen[sid]=rec(st)
            elif seen[sid].get("end") is None: seen[sid]=rec(st)
        if k and k%80000==0: print(f"[{which}] {k} {time.perf_counter()-t0:.0f}s", flush=True)
    json.dump(list(seen.values()), open(os.path.join(OUT,f"S_{which}.json"),"w"), indent=1, default=str)
    print(f"[{which}] DONE {time.perf_counter()-t0:.0f}s structures={len(seen)} confirmed={sum(1 for v in seen.values() if v['confirmed'])}", flush=True)
go(sys.argv[1])
