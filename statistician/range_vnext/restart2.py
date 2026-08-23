"""Section 9 -- restart determinism at fa36324, including near-capacity and at-capacity registry state."""
from __future__ import annotations
import sys, os, json
import pandas as pd

WP = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b"
sys.path.insert(0, os.path.join(WP, "ve_n1_replay"))
from ve_n1_replay import Bar
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay.range_engine_vnext import RangeSemanticEngineVNext
from ve_n1_replay.range_semantic_vnext import ConfigVNext, RangeSemanticProducerVNext
from ve_n1_replay.range_semantic_v4_4 import StructureV44
from ve_n1_replay.range_semantic_v4_3 import Depth

KW = dict(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900, implementation_commit=IC)
d = pd.read_csv(os.path.join(WP, "data", "market", "OANDA_XAUUSD_M15.csv")).iloc[:12000]
tt = d["time"].to_numpy(); o = d["open"].to_numpy(); h = d["high"].to_numpy()
l = d["low"].to_numpy(); c = d["close"].to_numpy()


def mk(k):
    return Bar(symbol="XAUUSD", ts_open=int(tt[k]), ts_close=int(tt[k]) + 900, open=float(o[k]),
               high=float(h[k]), low=float(l[k]), close=float(c[k]), volume=100.0)


def eng():
    return RangeSemanticEngineVNext(range_config=ConfigVNext(), acknowledge_construction_only=True, **KW)


def sig(res, ev):
    return (getattr(res, "macro_id", None), getattr(res, "macro_state", None),
            getattr(res, "macro_reason", None), getattr(res, "active_macro_count", None),
            tuple(sorted(getattr(res, "active_macro_ids", ()) or ())),
            getattr(res, "macro_boundary_upper", None), getattr(res, "macro_boundary_lower", None),
            getattr(res, "regime", None),
            tuple(sorted((e.kind, e.depth, e.structure_id) for e in ev)))


print("=" * 88)
print("SECTION 9 -- RESTART DETERMINISM at fa36324 (real data, normal registry state)")
print("=" * 88)
N, CUT = 12000, 7000
A = eng(); outA = []
for k in range(N):
    _, r, e = A.observe_closed_bar(mk(k)); outA.append(sig(r, e))
B = eng(); outB = []
for k in range(CUT):
    _, r, e = B.observe_closed_bar(mk(k)); outB.append(sig(r, e))
snap = B.snapshot()
C = eng(); C.restore(snap)
for k in range(CUT, N):
    _, r, e = C.observe_closed_bar(mk(k)); outB.append(sig(r, e))
mism = [i for i in range(N) if outA[i] != outB[i]]
print(f"  continuous vs snapshot@{CUT} -> restore -> resume, {N} bars: mismatching bars = {len(mism)}")

D = eng()
for k in range(3000):
    D.observe_closed_bar(mk(k))
E = eng(); E.restore(D.snapshot())
for k in range(3000, 6500):
    E.observe_closed_bar(mk(k))
F = eng(); F.restore(E.snapshot()); outF = []
for k in range(6500, N):
    _, r, e = F.observe_closed_bar(mk(k)); outF.append(sig(r, e))
mism2 = [i for i in range(N - 6500) if outA[6500 + i] != outF[i]]
print(f"  DOUBLE restart (3000 -> 6500 -> {N}): mismatching bars = {len(mism2)}")

print()
print("=" * 88)
print("SECTION 9b -- RESTART at NEAR-CAPACITY and AT-CAPACITY registry state")
print("=" * 88)


def seed(prod, cfg, sid, lo, hi):
    st = StructureV44(structure_id=sid, depth=Depth.MACRO, parent_structure_id=None, start_ts=0,
                      trailing_window=cfg.W)
    st.atr_ref = 1.0
    st.up.offer(hi, 1e18); st.dn.offer(lo, 1e18)
    st.record_touch_v44(0, True); st.record_touch_v44(0, False)
    prod._active_macros[sid] = st


def arrange_cont(prod, zone, i, tid):
    prod._last_terminated_macro_zone = zone
    prod._last_terminated_macro_end_reason = "ZONES_DEGENERATE"
    prod._last_terminated_macro_end_ts = i - 1
    prod._last_terminated_macro_id = tid


def offer(prod, i, z):
    ev = []
    prod._pending_up = (i, z[1]); prod._pending_dn = (i, z[0])
    prod._offer_swing_everywhere(i, z[0], False, ev)
    return [e.kind for e in ev]


CAP = 4
for label, n_seed in (("NEAR-capacity (cap-1)", CAP - 1), ("AT-capacity (cap)", CAP)):
    cfg = ConfigVNext(max_active_macro_candidates=CAP)
    P = RangeSemanticProducerVNext(cfg)
    for j in range(n_seed):
        seed(P, cfg, 9000 + j, 100.0 + 1000 * j, 110.0 + 1000 * j)
    P._n = 500
    ops = [(600, (50000.0, 50010.0), 901), (603, (52000.0, 52010.0), 902),
           (606, (54000.0, 54010.0), 903)]
    cont = RangeSemanticProducerVNext(cfg)
    cont.__dict__ = RangeSemanticProducerVNext(cfg).__dict__
    cont.restore_state(P.snapshot_state())
    trace_cont = []
    for (i, z, tid) in ops:
        arrange_cont(cont, z, i, tid)
        trace_cont.append((offer(cont, i, z), len(cont._active_macros), sorted(cont._active_macros)))
    R = RangeSemanticProducerVNext(cfg)
    R.restore_state(P.snapshot_state())
    arrange_cont(R, ops[0][1], ops[0][0], ops[0][2])
    first = (offer(R, ops[0][0], ops[0][1]), len(R._active_macros), sorted(R._active_macros))
    snap_mid = R.snapshot_state()
    R2 = RangeSemanticProducerVNext(cfg)
    R2.restore_state(snap_mid)
    trace_rest = [first]
    for (i, z, tid) in ops[1:]:
        arrange_cont(R2, z, i, tid)
        trace_rest.append((offer(R2, i, z), len(R2._active_macros), sorted(R2._active_macros)))
    same = trace_cont == trace_rest
    over = any(sz > CAP for _, sz, _ in trace_cont + trace_rest)
    print(f"  {label:24} seeded={n_seed} cap={CAP}")
    print(f"    continuous trace : {trace_cont}")
    print(f"    restarted trace  : {trace_rest}")
    print(f"    IDENTICAL: {same}   any over-cap: {over}")
