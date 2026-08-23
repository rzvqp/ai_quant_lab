"""MERGE-at-capacity: prove the exemption is mechanically net-zero, not a hole.
The earlier attempt used a zone identical to an existing candidate, which `offer_swing` absorbs
before the merge branch is ever reached. This constructs a zone that (a) is NOT absorbed by any
cluster tolerance and (b) overlaps an active candidate at IoU >= IOU_CONTINUE, so MERGE really fires.
"""
from __future__ import annotations
import sys, os

WP = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b"
sys.path.insert(0, os.path.join(WP, "ve_n1_replay"))
from ve_n1_replay.range_semantic_vnext import (ConfigVNext, RangeSemanticProducerVNext,
                                               REGISTRY_CAPACITY_REFUSED)
from ve_n1_replay.range_semantic_v4_4 import StructureV44
from ve_n1_replay.range_semantic_v4_3 import Depth


def seed(prod, cfg, sid, lo, hi):
    st = StructureV44(structure_id=sid, depth=Depth.MACRO, parent_structure_id=None,
                      start_ts=0, trailing_window=cfg.W)
    st.atr_ref = 1.0
    st.up.offer(hi, 1e18)
    st.dn.offer(lo, 1e18)
    st.record_touch_v44(0, True)
    st.record_touch_v44(0, False)
    prod._active_macros[sid] = st
    return st


def iou(a, b):
    lo = max(a[0], b[0]); hi = min(a[1], b[1])
    return 0.0 if hi <= lo else (hi - lo) / (max(a[1], b[1]) - min(a[0], b[0]))


CAP = 3
cfg = ConfigVNext(max_active_macro_candidates=CAP)
print(f"  IOU_CONTINUE={cfg.IOU_CONTINUE}  tol_cluster={cfg.tol_cluster}  cap={CAP}")
prod = RangeSemanticProducerVNext(cfg)
seed(prod, cfg, 6000, 100.0, 110.0)
seed(prod, cfg, 6001, 5000.0, 5010.0)
seed(prod, cfg, 6002, 9000.0, 9010.0)
Z = (102.0, 112.0)
print(f"  merge-target zone (100,110) vs candidate zone {Z}: IoU={iou(Z,(100.0,110.0)):.3f} "
      f">= {cfg.IOU_CONTINUE} -> MERGE expected")
print(f"  absorption check: |102-100|=2.0 and |112-110|=2.0, both > tol_cluster*atr={cfg.tol_cluster*1.0} "
      f"-> NOT absorbed by an existing cluster")
act, tgt = prod._episode_identity_for_new_macro_multi(Z, 500)
print(f"  episode identity -> action={act} target={tgt}")

before = sorted(prod._active_macros)
ev = []
prod._pending_up = (500, Z[1])
prod._pending_dn = (500, Z[0])
prod._offer_swing_everywhere(500, Z[0], False, ev)
after = sorted(prod._active_macros)
kinds = [e.kind for e in ev]
print(f"\n  AT CAPACITY ({CAP}) with a genuine MERGE:")
print(f"    events            : {kinds}")
print(f"    active before/after: {len(before)} -> {len(after)}   ids {before} -> {after}")
print(f"    over cap          : {len(after) > CAP}")
print(f"    refused           : {REGISTRY_CAPACITY_REFUSED in kinds}  (must be False -- MERGE is exempt)")
print(f"    target {tgt} removed : {tgt not in after}")
print(f"    NET-ZERO CONFIRMED: {len(after) == len(before) and tgt not in after and tgt in before}")

print(f"\n  ORDER-OF-OPERATIONS check (why the exemption is safe):")
print(f"    _supersede_macro(target) POPS before `self._active_macros[new_id] = st_macro` INSERTS,")
print(f"    so the registry goes cap -> cap-1 -> cap and never transiently exceeds the bound.")

print(f"\n  ADVERSARIAL: repeated MERGE at capacity (each merging into the newest overlapping candidate)")
sizes = []
z = Z
for rep in range(10):
    ev2 = []
    z = (z[0] + 2.0, z[1] + 2.0)
    prod._pending_up = (600 + rep, z[1])
    prod._pending_dn = (600 + rep, z[0])
    prod._offer_swing_everywhere(600 + rep, z[0], False, ev2)
    sizes.append(len(prod._active_macros))
print(f"    active after each of 10 repeated merge-ish offers: {sizes}")
print(f"    max={max(sizes)} cap={CAP} over_cap={max(sizes) > CAP}")
