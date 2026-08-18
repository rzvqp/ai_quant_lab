"""Build the canonical N1 incremental ledger ONCE for all 355,696 M15 bars (ve_n1_replay 0.1.1).
Verifies: build time, ledger identity, zero-lookahead (prefix stability), and unbounded-structure
preservation across snapshot/restore. Saves a compact durable ledger for the rerun to consume.
Run from a NEUTRAL cwd so no stray ai_trader shadows ve_n1_replay's hermetic vendored _ai."""
import sys, os, json, time, hashlib
import numpy as np
import pandas as pd
import ve_n1_replay as R

# BELOW_NORMAL priority so AI Trader LIVE_SHADOW keeps CPU priority (Step 10, niced).
try:
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)  # BELOW_NORMAL_PRIORITY_CLASS
except Exception:
    pass

CSV = sys.argv[1] if len(sys.argv) > 1 else "m15.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "n1_ledger"
SYM, TF, IVAL, HORIZON, IMPL = "XAUUSD", "M15", 900, 460, "21ae632"

def log(m):
    print(f"[{int(time.time())}] {m}", flush=True)
    with open(OUT + ".log", "a") as f: f.write(f"{int(time.time())} {m}\n")

log(f"START ledger build ve_n1_replay={R.VE_N1_REPLAY_VERSION}")
d = pd.read_csv(CSV)
data_identity = "M15_v2/pre_holdout/4-block/2011-2025:sha256=" + hashlib.sha256(open(CSV,'rb').read()).hexdigest()[:16]
rows = list(zip(d['time'].astype('int64').tolist(), d['open'].tolist(), d['high'].tolist(),
                d['low'].tolist(), d['close'].tolist(), d['volume'].tolist()))
N = len(rows)
log(f"loaded {N} bars; data_identity={data_identity}")

def mkbar(r):
    return R.Bar(symbol=SYM, ts_open=r[0], ts_close=r[0]+IVAL, open=r[1], high=r[2], low=r[3], close=r[4], volume=r[5])
bars = [mkbar(r) for r in rows]

# ── build the full ledger (O(n) incremental) ────────────────────────────────────────────────────
eng = R.N1IncrementalReplayEngine(symbol=SYM, timeframe=TF, bar_interval_seconds=IVAL, implementation_commit=IMPL, horizon=HORIZON)
t0 = time.time()
led = eng.replay_batch(bars)
build_s = time.time() - t0
log(f"replay_batch done: {N} bars in {build_s:.1f}s ({build_s/N*1000:.3f} ms/bar); ledger_key={led.ledger_key} eval_fp={led.evaluation_identity_fingerprint}")

recs = led.records
assert len(recs) == N, f"ledger records {len(recs)} != {N}"

# ── regime vocabulary -> per-bar bitmask (membership; overlaps allowed) ──────────────────────────
VOCAB = ["TREND_UP", "TREND_DOWN", "COMPRESSION", "BREAKOUT_TRANSITION", "UNCERTAIN"]
seen = set()
for r in recs:
    for x in r.applicable_regimes: seen.add(str(x))
extra = sorted(seen - set(VOCAB))
VOCAB = VOCAB + extra  # append any unforeseen labels rather than dropping them
bit = {name: 1 << i for i, name in enumerate(VOCAB)}

ts_open = np.empty(N, dtype=np.int64)
mask = np.zeros(N, dtype=np.uint16)
structure = np.empty(N, dtype=object)
direction = np.empty(N, dtype=object)
is_comp = np.zeros(N, dtype=np.int8)   # -1 None, 0 False, 1 True
is_disp = np.zeros(N, dtype=bool)
out_fp = np.empty(N, dtype=object)
brk = np.empty(N, dtype=object)
for i, r in enumerate(recs):
    ts_open[i] = r.ts_open
    m = 0
    for x in r.applicable_regimes: m |= bit[str(x)]
    mask[i] = m
    structure[i] = r.structure
    direction[i] = r.direction
    is_comp[i] = -1 if r.is_compressed is None else (1 if r.is_compressed else 0)
    is_disp[i] = bool(r.is_displacement)
    out_fp[i] = r.output_fingerprint
    brk[i] = r.latest_break_kind

# ── VERIFY 1: zero lookahead (prefix stability) — a fresh ledger on bars[:k] must match records[:k] ──
def prefix_ok(k):
    e2 = R.N1IncrementalReplayEngine(symbol=SYM, timeframe=TF, bar_interval_seconds=IVAL, implementation_commit=IMPL, horizon=HORIZON)
    l2 = e2.replay_batch(bars[:k])
    return all(l2.records[j].output_fingerprint == recs[j].output_fingerprint for j in range(k))
look_pts = [1000, 20000]
lookahead_ok = all(prefix_ok(k) for k in look_pts)
log(f"zero-lookahead prefix check at {look_pts}: {'OK' if lookahead_ok else 'FAIL'}")

# ── VERIFY 2: unbounded-structure preserved across snapshot/restore ──────────────────────────────
# Feed to a point PAST a confirmed break older than the 460 horizon, snapshot, restore into a fresh
# engine, continue — the continued fingerprints must equal the straight-through ledger. This proves the
# incremental builder carries the confirmed structure forward even though raw history is bounded to 460.
K = 100000
es = R.N1IncrementalReplayEngine(symbol=SYM, timeframe=TF, bar_interval_seconds=IVAL, implementation_commit=IMPL, horizon=HORIZON)
es.replay_batch(bars[:K])
snap = es.snapshot()
er = R.N1IncrementalReplayEngine(symbol=SYM, timeframe=TF, bar_interval_seconds=IVAL, implementation_commit=IMPL, horizon=HORIZON)
er.restore(snap)
cont = [er.observe_closed_bar(bars[K+j]).output_fingerprint for j in range(2000)]
straight = [recs[K+j].output_fingerprint for j in range(2000)]
snap_restore_ok = (cont == straight)
log(f"snapshot/restore unbounded-structure preservation: {'OK' if snap_restore_ok else 'FAIL'}")

# ── save durable ledger ─────────────────────────────────────────────────────────────────────────
np.savez_compressed(OUT + ".npz", ts_open=ts_open, mask=mask, structure=structure, direction=direction,
                    is_comp=is_comp, is_disp=is_disp, out_fp=out_fp, brk=brk, vocab=np.array(VOCAB, dtype=object))
meta = dict(
    ledger_key=led.ledger_key, evaluation_identity_fingerprint=led.evaluation_identity_fingerprint,
    history_horizon=led.history_horizon, history_horizon_version=led.history_horizon_version,
    ledger_schema_version=led.ledger_schema_version, ve_n1_replay_version=led.ve_n1_replay_version,
    data_identity=data_identity, bar_count=led.bar_count, last_closed_bar_id=led.last_closed_bar_id,
    build_seconds=round(build_s, 1), build_info=R.build_info(), vocab=VOCAB,
    verify_zero_lookahead=lookahead_ok, verify_snapshot_restore_unbounded=snap_restore_ok,
    n1_contract_version=recs[-1].input_data_identity if False else "n1-additive-raw-axes-v1",
    router_version="router-v1",
    regime_bar_counts={name: int(((mask & bit[name]) != 0).sum()) for name in VOCAB},
)
json.dump(meta, open(OUT + "_meta.json", "w"), indent=2)
log(f"SAVED {OUT}.npz + {OUT}_meta.json  regime_counts={meta['regime_bar_counts']}")
log("LEDGER_BUILD_COMPLETE " + ("PASS" if (lookahead_ok and snap_restore_ok) else "VERIFY_FAIL"))
