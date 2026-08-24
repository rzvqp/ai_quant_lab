"""range_smoke.py — de-risk the read-only RANGE vNext integration: import, contract-guard, run ~3000 bars of my
authorized gated M15, print event-kind counts + timing. NO modification of ve_n1_replay.
"""
import sys, os, time
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\ve_n1_replay")
_HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,_HERE)
import numpy as np, pandas as pd
from collections import Counter
from ve_n1_replay import Bar
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay.range_engine_vnext import RangeSemanticEngineVNext
from ve_n1_replay.range_semantic_vnext import ConfigVNext, RANGE_HIERARCHICAL_VNEXT_NORMATIVE_CONFIG_ID
import swing_base as sb

def make_engine():
    assert ConfigVNext().config_id()==RANGE_HIERARCHICAL_VNEXT_NORMATIVE_CONFIG_ID, "RANGE vNext config_id MISMATCH"
    return RangeSemanticEngineVNext(symbol="XAUUSD",timeframe="15m",bar_interval_seconds=900,
        implementation_commit=IC, range_config=ConfigVNext(), acknowledge_construction_only=True)

def main():
    print("config_id GUARD:", ConfigVNext().config_id()==RANGE_HIERARCHICAL_VNEXT_NORMATIVE_CONFIG_ID, "| IC=",IC[:12])
    m=sb.build_frames()["M15"]; sub=m[m["is_dev"].to_numpy()].head(3000).reset_index(drop=True)
    hasv="volume" in sub.columns
    t=sub["time"].to_numpy(); o=sub["open"].to_numpy(); h=sub["high"].to_numpy(); l=sub["low"].to_numpy(); c=sub["close"].to_numpy()
    v=sub["volume"].to_numpy() if hasv else None
    eng=make_engine(); cnt=Counter(); states=Counter(); nev=0; maxcand=0; t0=time.time()
    for k in range(len(sub)):
        bar=Bar(symbol="XAUUSD",ts_open=int(t[k]),ts_close=int(t[k])+900,open=float(o[k]),high=float(h[k]),
                low=float(l[k]),close=float(c[k]),volume=float(v[k]) if hasv else 100.0)
        n1,res,events=eng.observe_closed_bar(bar)
        for e in events: cnt[e.kind]+=1; nev+=1
        if res.macro_state is not None: states[res.macro_state]+=1
        if res.active_macro_count>maxcand: maxcand=res.active_macro_count
    dt=time.time()-t0
    print(f"bars={len(sub)} secs={dt:.1f} ({1000*dt/len(sub):.2f} ms/bar) totalEvents={nev} maxActiveCand={maxcand}")
    print("EVENT KINDS:", dict(cnt.most_common()))
    print("MACRO STATES:", dict(states.most_common()))

if __name__=="__main__":
    main()
