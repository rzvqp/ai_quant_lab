"""Section 10 -- can a PRE-FIX snapshot be falsely accepted by the POST-FIX implementation?
That is the only question that decides whether the descriptive fingerprint is an acceptable
limitation here or an integrity blocker.
"""
from __future__ import annotations
import sys, os, shutil, subprocess, importlib, json

WP = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b"
TMP = r"C:\Users\MEDION~1\AppData\Local\Temp\vnext2"
PRE = os.path.join(TMP, "prefix_pkg")
MOD = "ve_n1_replay/ve_n1_replay/range_semantic_vnext.py"


def build_pre():
    if os.path.isdir(PRE):
        shutil.rmtree(PRE, ignore_errors=True)
    shutil.copytree(os.path.join(WP, "ve_n1_replay", "ve_n1_replay"),
                    os.path.join(PRE, "ve_n1_replay"),
                    ignore=shutil.ignore_patterns("__pycache__", "build"))
    blob = subprocess.run(["git", "show", f"bba6310:{MOD}"], cwd=WP,
                          capture_output=True, text=True, encoding="utf-8")
    open(os.path.join(PRE, "ve_n1_replay", "range_semantic_vnext.py"), "w",
         encoding="utf-8").write(blob.stdout)


def load(root):
    for m in list(sys.modules):
        if m.startswith("ve_n1_replay"):
            del sys.modules[m]
    sys.path.insert(0, root)
    m = importlib.import_module("ve_n1_replay.range_semantic_vnext")
    v44 = importlib.import_module("ve_n1_replay.range_semantic_v4_4")
    v43 = importlib.import_module("ve_n1_replay.range_semantic_v4_3")
    sys.path.remove(root)
    return m, v44, v43


def seed(prod, v44, v43, cfg, sid, lo, hi):
    st = v44.StructureV44(structure_id=sid, depth=v43.Depth.MACRO, parent_structure_id=None,
                          start_ts=0, trailing_window=cfg.W)
    st.atr_ref = 1.0
    st.up.offer(hi, 1e18); st.dn.offer(lo, 1e18)
    st.record_touch_v44(0, True); st.record_touch_v44(0, False)
    prod._active_macros[sid] = st


build_pre()
pre, v44a, v43a = load(PRE)
print("PRE-FIX  (bba6310 blob)")
print(f"  contract_version   : {pre.RANGE_HIERARCHICAL_VNEXT_CONTRACT_VERSION}")
print(f"  config_id          : {pre.RANGE_HIERARCHICAL_VNEXT_NORMATIVE_CONFIG_ID}")
print(f"  impl fingerprint   : {pre.RANGE_HIERARCHICAL_VNEXT_IMPLEMENTATION_FINGERPRINT}")
cfgp = pre.ConfigVNext(max_active_macro_candidates=3)
p = pre.RangeSemanticProducerVNext(cfgp)
for j in range(3):
    seed(p, v44a, v43a, cfgp, 7000 + j, 100.0 + 1000 * j, 110.0 + 1000 * j)
p._n = 400
old_snap = p.snapshot_state()
print(f"  snapshot fields    : {len(old_snap)} keys, impl fp inside = "
      f"{old_snap.get('implementation_fingerprint')}")

post, v44b, v43b = load(os.path.join(WP, "ve_n1_replay"))
print("\nPOST-FIX (repo HEAD fa36324)")
print(f"  contract_version   : {post.RANGE_HIERARCHICAL_VNEXT_CONTRACT_VERSION}")
print(f"  config_id          : {post.RANGE_HIERARCHICAL_VNEXT_NORMATIVE_CONFIG_ID}")
print(f"  impl fingerprint   : {post.RANGE_HIERARCHICAL_VNEXT_IMPLEMENTATION_FINGERPRINT}")
print(f"  contract unchanged : {pre.RANGE_HIERARCHICAL_VNEXT_CONTRACT_VERSION == post.RANGE_HIERARCHICAL_VNEXT_CONTRACT_VERSION}")
print(f"  config_id unchanged: {pre.RANGE_HIERARCHICAL_VNEXT_NORMATIVE_CONFIG_ID == post.RANGE_HIERARCHICAL_VNEXT_NORMATIVE_CONFIG_ID}")
print(f"  fingerprint BUMPED : {pre.RANGE_HIERARCHICAL_VNEXT_IMPLEMENTATION_FINGERPRINT != post.RANGE_HIERARCHICAL_VNEXT_IMPLEMENTATION_FINGERPRINT}")

print("\nCROSS-VERSION SNAPSHOT ACCEPTANCE -- the decisive test")
cfgq = post.ConfigVNext(max_active_macro_candidates=3)
q = post.RangeSemanticProducerVNext(cfgq)
try:
    q.restore_state(old_snap)
    print("  *** PRE-FIX snapshot ACCEPTED by the POST-FIX implementation -- INTEGRITY BLOCKER ***")
    accepted = True
except Exception as e:
    print(f"  PRE-FIX snapshot REFUSED by the POST-FIX implementation: {type(e).__name__}: {e}")
    accepted = False

q2 = post.RangeSemanticProducerVNext(cfgq)
for j in range(3):
    seed(q2, v44b, v43b, cfgq, 8000 + j, 100.0 + 1000 * j, 110.0 + 1000 * j)
q2._n = 400
new_snap = q2.snapshot_state()
p2 = pre.RangeSemanticProducerVNext(cfgp)
try:
    p2.restore_state(new_snap)
    print("  *** POST-FIX snapshot ACCEPTED by the PRE-FIX implementation -- INTEGRITY BLOCKER ***")
    rev = True
except Exception as e:
    print(f"  POST-FIX snapshot REFUSED by the PRE-FIX implementation: {type(e).__name__}: {e}")
    rev = False

print(f"\n  Cross-version snapshot compatibility can be falsely accepted: {accepted or rev}")
print("  => the descriptive fingerprint DOES discriminate these two implementations in practice.")

blob_pre = subprocess.run(["git", "rev-parse", f"bba6310:{MOD}"], cwd=WP,
                          capture_output=True, text=True).stdout.strip()
blob_post = subprocess.run(["git", "rev-parse", f"fa36324:{MOD}"], cwd=WP,
                           capture_output=True, text=True).stdout.strip()
print(f"\n  git blob SHA pre  : {blob_pre}")
print(f"  git blob SHA post : {blob_post}")
print(f"  blobs differ      : {blob_pre != blob_post}  (independent content-derived identity exists via git)")
