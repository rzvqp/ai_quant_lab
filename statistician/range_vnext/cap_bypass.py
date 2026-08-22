from __future__ import annotations
import sys, os
WP=r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b"; sys.path.insert(0, os.path.join(WP,"ve_n1_replay"))
from ve_n1_replay.range_semantic_vnext import ConfigVNext, RangeSemanticProducerVNext
from ve_n1_replay.range_semantic_v4_4 import StructureV44, BREAKOUT_ACCEPTED
from ve_n1_replay.range_semantic_v4_3 import Depth
print("="*80); print("SECTION 12b — CAN THE CAP BE BYPASSED?  (cap is tested ONLY on the REPLACEMENT branch)")
print("="*80)
print("  range_semantic_vnext.py: `if action == \"REPLACEMENT\" and len(self._active_macros) >= cap:`")
print("  MERGE removes one candidate and adds one -> net zero, cannot grow the registry.")
print("  CONTINUATION adds a candidate and removes NONE. Testing whether that can exceed the cap.\n")
CAP=3
cfg=ConfigVNext(max_active_macro_candidates=CAP)
prod=RangeSemanticProducerVNext(cfg)
def seed(sid, base):
    st=StructureV44(structure_id=sid, depth=Depth.MACRO, parent_structure_id=None, start_ts=0, trailing_window=cfg.W)
    st.atr_ref=1.0; st.up.offer(base+10,1e18); st.dn.offer(base,1e18)
    st.record_touch_v44(0,True); st.record_touch_v44(0,False)
    prod._active_macros[sid]=st
for j in range(CAP): seed(2000+j, 100.0+1000*j)
print(f"  seeded {len(prod._active_macros)} active candidates at cap={CAP}")
# Arrange a CONTINUATION: a recently terminated macro whose zone the new candidate overlaps,
# terminated for a reason other than BREAKOUT_ACCEPTED, within GAP_MAX bars.
ZONE=(50000.0, 50010.0)
prod._last_terminated_macro_zone=ZONE
prod._last_terminated_macro_end_reason="ZONES_DEGENERATE"
prod._last_terminated_macro_end_ts=10
prod._last_terminated_macro_id=999
i=10+cfg.GAP_MAX-1
act,tid = prod._episode_identity_for_new_macro_multi(ZONE, i)
print(f"  episode identity for a zone overlapping the terminated one -> action={act} target={tid}")
ev=[]
prod._pending_up=(i, ZONE[1]); prod._pending_dn=(i, ZONE[0])
prod._offer_swing_everywhere(i, ZONE[0], False, ev)
kinds=[e.kind for e in ev]
n_after=len(prod._active_macros)
print(f"  events={kinds}")
print(f"  active BEFORE={CAP}  active AFTER={n_after}  cap={CAP}")
if n_after>CAP:
    print(f"  *** CAP EXCEEDED via the {act} branch: {n_after} > {CAP} — REGISTRY_CAPACITY_REFUSED not emitted ***")
else:
    print(f"  cap held.")
# how far can it be pushed?
extra=0
for rep in range(30):
    z=(50000.0+ (rep+1)*0.0, 50010.0)  # same zone -> would MERGE now; use fresh disjoint zones per continuation
    prod._last_terminated_macro_zone=(60000.0+rep*1000, 60010.0+rep*1000)
    prod._last_terminated_macro_end_reason="ZONES_DEGENERATE"
    prod._last_terminated_macro_end_ts=i+rep*2
    prod._last_terminated_macro_id=5000+rep
    j=i+rep*2+1
    zz=prod._last_terminated_macro_zone
    prod._pending_up=(j, zz[1]); prod._pending_dn=(j, zz[0])
    ev2=[]
    prod._offer_swing_everywhere(j, zz[0], False, ev2)
    if any(e.kind=="EPISODE_CONTINUATION" for e in ev2): extra+=1
print(f"  after 30 further engineered CONTINUATION offers: active={len(prod._active_macros)}  (cap={CAP})  continuations_admitted={extra}")
print(f"  => maximum registry size reachable while cap={CAP}: {len(prod._active_macros)}")
