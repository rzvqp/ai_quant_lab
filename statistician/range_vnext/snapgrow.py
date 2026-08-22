from __future__ import annotations
import sys, os, json, dataclasses as _d
import pandas as pd
WP=r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b"; sys.path.insert(0, os.path.join(WP,"ve_n1_replay"))
from ve_n1_replay import Bar
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay.range_engine_vnext import RangeSemanticEngineVNext
from ve_n1_replay.range_engine_v4_4 import RangeSemanticEngineV44
from ve_n1_replay.range_semantic_vnext import ConfigVNext
from ve_n1_replay.range_semantic_v4_4 import ConfigV44
KW=dict(symbol="XAUUSD",timeframe="15m",bar_interval_seconds=900,implementation_commit=IC)
d=pd.read_csv(os.path.join(WP,"data","market","OANDA_XAUUSD_M15.csv")).iloc[:60000]
tt=d["time"].to_numpy();o=d["open"].to_numpy();h=d["high"].to_numpy();l=d["low"].to_numpy();c=d["close"].to_numpy()
def mk(k): return Bar(symbol="XAUUSD",ts_open=int(tt[k]),ts_close=int(tt[k])+900,open=float(o[k]),high=float(h[k]),low=float(l[k]),close=float(c[k]),volume=100.0)
def size(e):
    s=e.snapshot(); return len(json.dumps(_d.asdict(s), default=str))
res={}
for nm,eng in (("vnext",RangeSemanticEngineVNext(range_config=ConfigVNext(),acknowledge_construction_only=True,**KW)),
               ("v4_4", RangeSemanticEngineV44(range_config=ConfigV44(),acknowledge_construction_only=True,**KW))):
    pts={}
    for k in range(60000):
        eng.observe_closed_bar(mk(k))
        if (k+1) in (10000,20000,30000,40000,50000,60000):
            pts[k+1]=size(eng)
            prod=eng._range
            pts[f"{k+1}_dead"]=len(getattr(prod._registry,"_dead",[]) or [])
            pts[f"{k+1}_awaiting"]=len(getattr(prod,"_awaiting_role",{}) or {})
            pts[f"{k+1}_active"]=len(getattr(prod,"_active_macros",{}) or {}) if nm=="vnext" else (1 if getattr(prod,"_active_macro",None) else 0)
    res[nm]=pts
print(f"  {'bars':>7} | {'vNext bytes':>12} {'dead':>6} {'awaiting':>9} {'active':>7} | {'v4.4 bytes':>11} {'dead':>6} {'awaiting':>9}")
for k in (10000,20000,30000,40000,50000,60000):
    a=res["vnext"]; b=res["v4_4"]
    print(f"  {k:7d} | {a[k]:12,d} {a[f'{k}_dead']:6d} {a[f'{k}_awaiting']:9d} {a[f'{k}_active']:7d} | {b[k]:11,d} {b[f'{k}_dead']:6d} {b[f'{k}_awaiting']:9d}")
gv=(res['vnext'][60000]-res['vnext'][10000])/50000; g4=(res['v4_4'][60000]-res['v4_4'][10000])/50000
print(f"\n  growth per bar: vNext {gv:.2f} B/bar   v4.4 {g4:.2f} B/bar   ratio {gv/max(g4,1e-9):.1f}x")
print(f"  extrapolated to 355,696 bars: vNext ~{res['vnext'][10000]+gv*345696:,.0f} B   v4.4 ~{res['v4_4'][10000]+g4*345696:,.0f} B")
