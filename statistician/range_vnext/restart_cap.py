from __future__ import annotations
import sys, os, json, pickle, hashlib
import pandas as pd, numpy as np
WP=r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b"
sys.path.insert(0, os.path.join(WP,"ve_n1_replay"))
from ve_n1_replay import Bar
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay.range_engine_vnext import RangeSemanticEngineVNext
from ve_n1_replay.range_semantic_vnext import (ConfigVNext, RangeSemanticProducerVNext,
    REGISTRY_CAPACITY_REFUSED, CANDIDATE_ABANDONED_PRICE_MOVED_ON, CANDIDATE_SUPERSEDED_BY_MERGE)
from ve_n1_replay.range_semantic_v4_4 import StructureV44
from ve_n1_replay.range_semantic_v4_3 import Depth
KW = dict(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900, implementation_commit=IC)
d = pd.read_csv(os.path.join(WP,"data","market","OANDA_XAUUSD_M15.csv")).iloc[:12000]
tt=d["time"].to_numpy(); o=d["open"].to_numpy(); h=d["high"].to_numpy(); l=d["low"].to_numpy(); c=d["close"].to_numpy()
def mk(k): return Bar(symbol="XAUUSD",ts_open=int(tt[k]),ts_close=int(tt[k])+900,open=float(o[k]),
                      high=float(h[k]),low=float(l[k]),close=float(c[k]),volume=100.0)
def eng(): return RangeSemanticEngineVNext(range_config=ConfigVNext(), acknowledge_construction_only=True, **KW)
def sig(res, ev):
    return (getattr(res,"macro_id",None), getattr(res,"macro_state",None), getattr(res,"macro_reason",None),
            getattr(res,"active_macro_count",None), tuple(sorted(getattr(res,"active_macro_ids",()) or ())),
            getattr(res,"macro_boundary_upper",None), getattr(res,"macro_boundary_lower",None),
            getattr(res,"regime",None), tuple(sorted((e.kind,e.depth,e.structure_id) for e in ev)))
print("="*78); print("SECTION 16 — RESTART / DETERMINISM"); print("="*78)
CUT=7000; N=12000
A=eng(); outA=[]
for k in range(N):
    _,r_,e_=A.observe_closed_bar(mk(k)); outA.append(sig(r_,e_))
B=eng(); outB=[]
for k in range(CUT):
    _,r_,e_=B.observe_closed_bar(mk(k)); outB.append(sig(r_,e_))
snap=B.snapshot()
import dataclasses as _d
blob=json.dumps(_d.asdict(snap) if _d.is_dataclass(snap) else str(snap), default=str, sort_keys=True)
print(f"  snapshot at bar {CUT}: serialized {len(blob):,} bytes  sha {hashlib.sha256(blob.encode()).hexdigest()[:16]}")
C=eng(); C.restore(snap)
for k in range(CUT,N):
    _,r_,e_=C.observe_closed_bar(mk(k)); outB.append(sig(r_,e_))
same=[i for i in range(N) if outA[i]!=outB[i]]
print(f"  continuous vs snapshot->restore->resume over {N} bars: mismatching bars = {len(same)}")
if same[:5]:
    for i in same[:5]: print("    first mismatch @",i,"\n      cont:",outA[i],"\n      rest:",outB[i])
print(f"  bars_observed cont={A.bars_observed} restored={C.bars_observed}")
# double restart
D=eng(); 
for k in range(3000): D.observe_closed_bar(mk(k))
s1=D.snapshot(); E=eng(); E.restore(s1)
for k in range(3000,6500): E.observe_closed_bar(mk(k))
s2=E.snapshot(); F=eng(); F.restore(s2); outF=[]
for k in range(6500,N):
    _,r_,e_=F.observe_closed_bar(mk(k)); outF.append(sig(r_,e_))
same2=[i for i in range(N-6500) if outA[6500+i]!=outF[i]]
print(f"  DOUBLE restart (3000 -> 6500 -> {N}): mismatching bars = {len(same2)}")

print("\n"+"="*78); print("SECTION 12 — HARD CAP ENFORCEMENT (adversarial, deterministic)"); print("="*78)
for cap in (1,2,3,16):
    cfg=ConfigVNext(max_active_macro_candidates=cap)
    prod=RangeSemanticProducerVNext(cfg)
    # seed cap non-overlapping candidates directly (same convention the repo's own tests use)
    for j in range(cap):
        st=StructureV44(structure_id=1000+j, depth=Depth.MACRO, parent_structure_id=None, start_ts=0, trailing_window=cfg.W)
        st.atr_ref=1.0; base=100.0+1000*j
        st.up.offer(base+10,1e18); st.dn.offer(base,1e18); st.record_touch_v44(0,True); st.record_touch_v44(0,False)
        prod._active_macros[1000+j]=st
    ev=[]
    # propose a brand-new, spatially DISJOINT candidate -> must be a REPLACEMENT
    far=100.0+1000*(cap+5)
    prod._pending_up=(1, far+10); prod._pending_dn=(1, far)
    prod._offer_swing_everywhere(2, far, False, ev)
    kinds=[e.kind for e in ev]
    print(f"  cap={cap:2d}: seeded {cap} active -> propose 1 more | events={kinds} | active_after={len(prod._active_macros)} | refused={'REGISTRY_CAPACITY_REFUSED' in kinds} | over_cap={len(prod._active_macros)>cap}")
