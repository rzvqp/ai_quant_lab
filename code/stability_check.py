"""STEP 1 — STABILITY GATE (Mandate 1.1). Two independent reads + sha256 of the three derived-context
files, compared to each other, to the manifest v2.4.2 ratified values, and the manifest content_hash.
Also reports derived-context coverage (discovery blocks + gaps). Any failure -> STOP (exit 2)."""
import os, sys, json, hashlib, time
import numpy as np, pandas as pd

AA = os.environ.get("AA_ROOT", r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation")
DM = os.path.join(AA, "data", "market")
MAN = os.path.join(AA, "config", "split_manifest.json")
CTX = {"H1_from_M15_v2": "OANDA_XAUUSD_H1_from_M15_v2.csv",
       "H4_from_M15_v2": "OANDA_XAUUSD_H4_from_M15_v2.csv",
       "D1_from_M15_v2": "OANDA_XAUUSD_D1_from_M15_v2.csv"}
BAR_S = {"H1_from_M15_v2": 3600, "H4_from_M15_v2": 4*3600, "D1_from_M15_v2": 86400}

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""): h.update(c)
    return h.hexdigest()

def read_all():
    return {k: sha(os.path.join(DM, v)) for k, v in CTX.items()}

def fail(msg):
    print("STABILITY GATE: FAIL ->", msg); sys.exit(2)

# manifest content_hash
if not os.path.exists(MAN): fail(f"manifest missing {MAN}")
raw = open(MAN, encoding="utf-8").read(); M = json.loads(raw)
print("manifest version:", M.get("version"))
ch = M.get("content_hash", {}).get("value", "")
got_ch = hashlib.sha256(raw.replace(ch, "").encode("utf-8")).hexdigest() if ch else ""
print(f"content_hash match: {got_ch == ch}  ({ch[:16]}...)")
if got_ch != ch: fail("manifest content_hash mismatch")

# expected context sha from manifest (derived-HTF live under context_derived_htf.entries, NOT timeframes)
ent = M.get("context_derived_htf", {}).get("entries", {})
exp = {}
for k in CTX:
    e = ent.get(k, {})
    s = e.get("data_file_sha256"); s = s.get("value") if isinstance(s, dict) else s
    exp[k] = s
    print(f"  {k}: status={e.get('status')} manifest_sha={str(s)[:16]}... file_path={e.get('file_path')}")
    if e.get("status") != "CONTEXT_DERIVED_VALIDATED":
        fail(f"{k} status != CONTEXT_DERIVED_VALIDATED ({e.get('status')})")
    if "staging" in str(e.get("file_path", "")).lower() or "unregistered" in str(e.get("file_path", "")).lower():
        fail(f"{k} file_path points at staging/unregistered: {e.get('file_path')}")

# READ A, wait, READ B
for k, v in CTX.items():
    if not os.path.exists(os.path.join(DM, v)): fail(f"context file absent: {v}")
A = read_all(); print("READ A done"); time.sleep(3.0); B = read_all(); print("READ B done (after 3s)")

ok = True
for k in CTX:
    a, b, e = A[k], B[k], exp[k]
    cond = (a == b) and (a == e)
    ok = ok and cond
    print(f"  {k}: A==B {a==b} | ==manifest {a==e} | {'OK' if cond else 'FAIL'}  ({a[:16]}...)")
if not ok: fail("read A/B or manifest sha mismatch")

# coverage: discovery blocks + gaps
print("\n=== derived-context COVERAGE (blocks + gaps; NOT continuous) ===")
for k, v in CTX.items():
    df = pd.read_csv(os.path.join(DM, v)); t = df["time"].values.astype("int64")
    d = np.diff(t); step = BAR_S[k]
    breaks = np.where(d > step * 1.5)[0]
    blocks = []; start = 0
    for br in breaks:
        blocks.append(br - start + 1); start = br + 1
    blocks.append(len(t) - start)
    tt = pd.to_datetime(t, unit="s")
    print(f"  {k}: {len(t)} bars, {len(blocks)} blocks {blocks}  span {tt.min().date()}..{tt.max().date()}")

print("\nSTABILITY GATE: PASS")
