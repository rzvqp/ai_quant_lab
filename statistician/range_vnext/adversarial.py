"""STAT-RANGE-VNEXT-HARD-CAP-REVALIDATION-001 -- independent adversarial reproducer.
Read-only: the repo working tree is never modified. The PRE-FIX implementation is materialised
from the git blob of bba6310 into a throwaway copy of the package.
"""
from __future__ import annotations
import sys, os, shutil, subprocess, importlib, json, dataclasses as _d

WP = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b"
TMP = r"C:\Users\MEDION~1\AppData\Local\Temp\vnext2"
PREFIX_ROOT = os.path.join(TMP, "prefix_pkg")

MOD = "ve_n1_replay/ve_n1_replay/range_semantic_vnext.py"


def materialise_prefix() -> str:
    """Copy the package to a temp root and overwrite the one file with bba6310's blob."""
    if os.path.isdir(PREFIX_ROOT):
        shutil.rmtree(PREFIX_ROOT, ignore_errors=True)
    shutil.copytree(os.path.join(WP, "ve_n1_replay", "ve_n1_replay"),
                    os.path.join(PREFIX_ROOT, "ve_n1_replay"),
                    ignore=shutil.ignore_patterns("__pycache__", "build"))
    blob = subprocess.run(["git", "show", f"bba6310:{MOD}"], cwd=WP,
                          capture_output=True, text=True, encoding="utf-8")
    assert blob.returncode == 0 and blob.stdout, blob.stderr
    with open(os.path.join(PREFIX_ROOT, "ve_n1_replay", "range_semantic_vnext.py"), "w",
              encoding="utf-8") as f:
        f.write(blob.stdout)
    return PREFIX_ROOT


def load(which: str):
    """which='prefix' -> bba6310 module; which='postfix' -> repo HEAD (fa36324)."""
    for m in list(sys.modules):
        if m.startswith("ve_n1_replay"):
            del sys.modules[m]
    root = materialise_prefix() if which == "prefix" else os.path.join(WP, "ve_n1_replay")
    sys.path.insert(0, root)
    mod = importlib.import_module("ve_n1_replay.range_semantic_vnext")
    v44 = importlib.import_module("ve_n1_replay.range_semantic_v4_4")
    v43 = importlib.import_module("ve_n1_replay.range_semantic_v4_3")
    sys.path.remove(root)
    return mod, v44, v43


def seed(prod, v44, v43, cfg, sid, base):
    st = v44.StructureV44(structure_id=sid, depth=v43.Depth.MACRO, parent_structure_id=None,
                          start_ts=0, trailing_window=cfg.W)
    st.atr_ref = 1.0
    st.up.offer(base + 10, 1e18)
    st.dn.offer(base, 1e18)
    st.record_touch_v44(0, True)
    st.record_touch_v44(0, False)
    prod._active_macros[sid] = st
    return st


def arrange_continuation(prod, zone, i, term_id=999):
    prod._last_terminated_macro_zone = zone
    prod._last_terminated_macro_end_reason = "ZONES_DEGENERATE"
    prod._last_terminated_macro_end_ts = i - 1
    prod._last_terminated_macro_id = term_id


def offer(prod, i, zone):
    ev = []
    prod._pending_up = (i, zone[1])
    prod._pending_dn = (i, zone[0])
    prod._offer_swing_everywhere(i, zone[0], False, ev)
    return ev


def run_case(which, cap, action_kind, repeats=1):
    mod, v44, v43 = load(which)
    cfg = mod.ConfigVNext(max_active_macro_candidates=cap)
    prod = mod.RangeSemanticProducerVNext(cfg)
    seeded_ids = []
    for j in range(cap):
        seed(prod, v44, v43, cfg, 2000 + j, 100.0 + 1000 * j)
        seeded_ids.append(2000 + j)
    before = set(prod._active_macros)
    kinds, sizes = [], []
    for rep in range(repeats):
        i = 500 + rep * 3
        if action_kind == "CONTINUATION":
            z = (50000.0 + rep * 1000, 50010.0 + rep * 1000)
            arrange_continuation(prod, z, i, term_id=900 + rep)
        elif action_kind == "REPLACEMENT":
            z = (70000.0 + rep * 1000, 70010.0 + rep * 1000)
            prod._last_terminated_macro_zone = None
        elif action_kind == "MERGE":
            tgt = prod._active_macros[seeded_ids[0]]
            z = (tgt.boundary_lower, tgt.boundary_upper)
            prod._last_terminated_macro_zone = None
        ev = offer(prod, i, z)
        kinds += [e.kind for e in ev]
        sizes.append(len(prod._active_macros))
    after = set(prod._active_macros)
    return dict(active_after=len(prod._active_macros), max_seen=max(sizes) if sizes else cap,
                over_cap=max(sizes) > cap if sizes else False,
                refused="REGISTRY_CAPACITY_REFUSED" in kinds, kinds=kinds,
                removed_unrelated=sorted(before - after), added=sorted(after - before))


print("=" * 92)
print("SECTION 3 -- REPRODUCE THE ORIGINAL BLOCKER against the PRE-FIX implementation (bba6310 blob)")
print("=" * 92)
r = run_case("prefix", 3, "CONTINUATION", repeats=31)
print(f"  PRE-FIX  cap=3, 31 CONTINUATION offers -> active={r['active_after']}  over_cap={r['over_cap']}  "
      f"refused={r['refused']}")
print(f"    reference failure was: active reached 34, zero REGISTRY_CAPACITY_REFUSED")
print(f"    harness still detects the original defect: {r['over_cap'] and not r['refused']}")

print()
print("=" * 92)
print("SECTION 4 -- HARD-CAP INVARIANT against fa36324 (post-fix)")
print("=" * 92)
print(f"  {'cap':>4} {'action':>13} {'reps':>5} | {'max active':>11} {'over cap':>9} {'refused':>8} | events")
rows = []
for cap in (1, 2, 3):
    for action in ("REPLACEMENT", "CONTINUATION", "MERGE"):
        reps = 5 if action == "CONTINUATION" else 1
        r = run_case("postfix", cap, action, repeats=reps)
        rows.append((cap, action, r))
        print(f"  {cap:4d} {action:>13} {reps:5d} | {r['max_seen']:11d} {str(r['over_cap']):>9} "
              f"{str(r['refused']):>8} | {sorted(set(r['kinds']))}")
        if r["removed_unrelated"]:
            print(f"       *** unrelated candidates removed: {r['removed_unrelated']} ***")
worst = max(r["max_seen"] - cap for cap, a, r in rows)
print(f"\n  INVARIANT len(active) <= cap held in every case: {all(not r['over_cap'] for _, _, r in rows)}"
      f"   (worst overshoot {worst})")

print()
print("=" * 92)
print("SECTION 4b -- MIXED SEQUENCE with a per-operation invariant check (post-fix)")
print("=" * 92)
mod, v44, v43 = load("postfix")
CAP = 3
cfg = mod.ConfigVNext(max_active_macro_candidates=CAP)
prod = mod.RangeSemanticProducerVNext(cfg)
for j in range(CAP):
    seed(prod, v44, v43, cfg, 3000 + j, 100.0 + 1000 * j)
seq = ["CONTINUATION", "REPLACEMENT", "MERGE", "CONTINUATION", "CONTINUATION", "REPLACEMENT",
       "MERGE", "CONTINUATION", "REPLACEMENT", "MERGE", "CONTINUATION", "CONTINUATION"]
viol = 0
for n, act in enumerate(seq):
    i = 1000 + n * 3
    if act == "CONTINUATION":
        z = (80000.0 + n * 500, 80010.0 + n * 500)
        arrange_continuation(prod, z, i, term_id=700 + n)
    elif act == "REPLACEMENT":
        z = (90000.0 + n * 500, 90010.0 + n * 500)
        prod._last_terminated_macro_zone = None
    else:
        tgt = prod._active_macros[sorted(prod._active_macros)[0]]
        z = (tgt.boundary_lower, tgt.boundary_upper)
        prod._last_terminated_macro_zone = None
    ev = offer(prod, i, z)
    sz = len(prod._active_macros)
    if sz > CAP:
        viol += 1
    print(f"    op{n:2d} {act:13} -> active={sz} {'*** VIOLATION ***' if sz > CAP else 'ok'} "
          f"{[e.kind for e in ev]}")
print(f"  per-operation invariant violations: {viol}")

print()
print("=" * 92)
print("SECTION 4c -- SNAPSHOT/RESTORE AT CAPACITY + POST-RESTORE INSERTION (post-fix)")
print("=" * 92)
mod, v44, v43 = load("postfix")
cfg = mod.ConfigVNext(max_active_macro_candidates=3)
prod = mod.RangeSemanticProducerVNext(cfg)
for j in range(3):
    seed(prod, v44, v43, cfg, 4000 + j, 100.0 + 1000 * j)
prod._n = 600
snap = prod.snapshot_state()
print(f"  snapshot taken at capacity: active={len(prod._active_macros)} serialized="
      f"{len(json.dumps(snap, default=str)):,} bytes")
p2 = mod.RangeSemanticProducerVNext(cfg)
p2.restore_state(snap)
print(f"  after restore: active={len(p2._active_macros)} ids={sorted(p2._active_macros)}  "
      f"at capacity: {len(p2._active_macros) == 3}")
arrange_continuation(p2, (50000.0, 50010.0), 700, term_id=888)
ev = offer(p2, 700, (50000.0, 50010.0))
print(f"  post-restore CONTINUATION at capacity -> active={len(p2._active_macros)} "
       f"events={[e.kind for e in ev]}  over_cap={len(p2._active_macros) > 3}")
prod2 = mod.RangeSemanticProducerVNext(cfg)
prod2.restore_state(snap)
ev2 = offer(prod2, 700, (70000.0, 70010.0))
print(f"  post-restore REPLACEMENT at capacity -> active={len(prod2._active_macros)} "
       f"events={[e.kind for e in ev2]}  over_cap={len(prod2._active_macros) > 3}")

print()
print("=" * 92)
print("SECTION 5 -- FAILURE SEMANTICS (post-fix, cap=3, CONTINUATION at capacity)")
print("=" * 92)
mod, v44, v43 = load("postfix")
cfg = mod.ConfigVNext(max_active_macro_candidates=3)
prod = mod.RangeSemanticProducerVNext(cfg)
for j in range(3):
    seed(prod, v44, v43, cfg, 5000 + j, 100.0 + 1000 * j)
before_ids = sorted(prod._active_macros)
before_bounds = {m: (prod._active_macros[m].boundary_lower, prod._active_macros[m].boundary_upper)
                 for m in before_ids}
arrange_continuation(prod, (50000.0, 50010.0), 700, term_id=777)
ev = offer(prod, 700, (50000.0, 50010.0))
after_ids = sorted(prod._active_macros)
after_bounds = {m: (prod._active_macros[m].boundary_lower, prod._active_macros[m].boundary_upper)
                for m in after_ids}
print(f"  candidate inserted?          {after_ids != before_ids}  (ids before {before_ids} after {after_ids})")
print(f"  unrelated candidate removed? {sorted(set(before_ids) - set(after_ids))}")
print(f"  boundaries mutated?          {before_bounds != after_bounds}")
print(f"  reason emitted:              {[e.kind for e in ev]}")
print(f"  event structure_id:          {[e.structure_id for e in ev]}  (None = no victim selected)")
runs = []
for _ in range(3):
    p = mod.RangeSemanticProducerVNext(cfg)
    for j in range(3):
        seed(p, v44, v43, cfg, 5000 + j, 100.0 + 1000 * j)
    arrange_continuation(p, (50000.0, 50010.0), 700, term_id=777)
    e = offer(p, 700, (50000.0, 50010.0))
    runs.append((sorted(p._active_macros), tuple(x.kind for x in e)))
print(f"  deterministic across 3 identical runs: {len(set(map(str, runs))) == 1}")
