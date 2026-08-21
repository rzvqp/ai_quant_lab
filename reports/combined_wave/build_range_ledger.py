"""Build the RANGE_STATE + longitudinal-event ledger ONCE for all 355,696 M15 bars (ve_n1_replay 0.2.0).
Captures per-bar range state, boundaries, F7 safety-guard, and every longitudinal event with its confirm_ts
(actionable causality). Verifies: build time, ledger identity, zero-lookahead, snapshot/restart guard
persistence, accepted-XOR-failed disjointness. Neutral cwd; hermetic vendored _ai."""
import sys, os, json, time, hashlib
import numpy as np, pandas as pd
import ve_n1_replay as R
try:
    import ctypes; ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
except Exception: pass

CSV = sys.argv[1] if len(sys.argv) > 1 else "m15.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "range_ledger"
SYM, TF, IVAL, IMPL = "XAUUSD", "M15", 900, "21ae632"

def log(m):
    print(f"[{int(time.time())}] {m}", flush=True)
    open(OUT + ".log", "a").write(f"{int(time.time())} {m}\n")

log(f"START range ledger ve_n1_replay={R.VE_N1_REPLAY_VERSION}")
d = pd.read_csv(CSV)
data_identity = "M15_v2/pre_holdout/4-block/2011-2025:sha256=" + hashlib.sha256(open(CSV, 'rb').read()).hexdigest()[:16]
rows = list(zip(d['time'].astype('int64').tolist(), d['open'].tolist(), d['high'].tolist(),
                d['low'].tolist(), d['close'].tolist(), d['volume'].tolist()))
N = len(rows)
bars = [R.Bar(symbol=SYM, ts_open=r[0], ts_close=r[0] + IVAL, open=r[1], high=r[2], low=r[3], close=r[4], volume=r[5]) for r in rows]
cfg = R.RangeConfig()   # DEFAULT = the pre-registered primary rule (n_touch=2, tol_atr=0.25, er_max=0.40,
                        # d_min_bars=96, n_acceptance=2, width_filter=off, RANGE_STATE_OVER_TREND_PAUSE)
eng = R.RangeStateReplayEngine(symbol=SYM, timeframe=TF, bar_interval_seconds=IVAL, implementation_commit=IMPL, range_config=cfg)
t0 = time.time(); led = eng.replay_batch(bars); build_s = time.time() - t0
recs = led.records
log(f"range replay_batch: {N} bars in {build_s:.1f}s ({build_s/N*1000:.3f} ms/bar)")

# per-bar arrays
CONS = {"None": 0, "FORMING": 1, "ESTABLISHED": 2, "CANDIDATE": 3, "ACCEPTED": 4, "VIOLATED": 5}
ts_close = np.empty(N, np.int64); cons = np.zeros(N, np.int8); upper = np.full(N, np.nan); lower = np.full(N, np.nan)
guard = np.zeros(N, bool); trendctx = np.empty(N, object); n1dir = np.empty(N, object); rng_avail = np.zeros(N, bool)
events = []                      # (bar_index, kind, confirm_ts, boundary, range_spec_id)
from collections import Counter
evc = Counter(); n_guards = 0; established_bars = 0
both_acc_fail = 0
for i, rec in enumerate(recs):
    ts_close[i] = rec.ts_close
    cs = str(rec.consolidation_state); cons[i] = CONS.get(cs, 0)
    if cs == "ESTABLISHED": established_bars += 1
    upper[i] = rec.upper if rec.upper is not None else np.nan
    lower[i] = rec.lower if rec.lower is not None else np.nan
    guard[i] = bool(rec.safety_guard); n_guards += 1 if rec.safety_guard else 0
    trendctx[i] = rec.trend_context; n1dir[i] = rec.n1_direction; rng_avail[i] = bool(rec.range_available)
    kinds_here = set()
    for e in rec.events:
        k = (e['kind'] if isinstance(e, dict) else e.kind); ks = str(k).split('.')[-1]
        cts = (e['confirm_ts'] if isinstance(e, dict) else e.confirm_ts)
        bnd = (e.get('boundary') if isinstance(e, dict) else getattr(e, 'boundary', None))
        rsid = (e.get('range_spec_id') if isinstance(e, dict) else getattr(e, 'range_spec_id', None))
        events.append((i, ks, cts, bnd, rsid)); evc[ks] += 1; kinds_here.add(ks)
    if "BREAKOUT_ACCEPTED" in kinds_here and "FAILED_BREAKOUT" in kinds_here: both_acc_fail += 1

log(f"event counts: {dict(evc)} | ESTABLISHED bars={established_bars} | n_guards={n_guards} | accepted&failed same bar={both_acc_fail}")

# SAVE FIRST (before verification) so the ledger persists even if a later verify step is interrupted.
np.savez_compressed(OUT + ".npz", ts_close=ts_close, cons=cons, upper=upper, lower=lower, guard=guard,
                    trendctx=trendctx, n1dir=n1dir, rng_avail=rng_avail,
                    ev_bar=np.array([e[0] for e in events], np.int64),
                    ev_kind=np.array([e[1] for e in events], object),
                    ev_confirm_ts=np.array([e[2] if e[2] is not None else -1 for e in events], np.int64),
                    ev_boundary=np.array([e[3] if e[3] is not None else np.nan for e in events], float),
                    ev_spec_id=np.array([e[4] for e in events], object))
def write_meta(lookahead, snap):
    meta = dict(ve_n1_replay_version=R.VE_N1_REPLAY_VERSION, build_info=R.build_info(),
                range_state_contract=R.RANGE_STATE_CONTRACT_VERSION, range_event_contract=R.RANGE_EVENT_CONTRACT_VERSION,
                range_ledger_schema=R.RANGE_LEDGER_SCHEMA_VERSION, safety_guards=list(R.SAFETY_GUARDS_REGISTER),
                range_config=dict(n_touch=cfg.n_touch, tol_atr=cfg.tol_atr, er_max=cfg.er_max, d_min_bars=cfg.d_min_bars,
                                  n_acceptance=cfg.n_acceptance, width_filter=cfg.width_filter, precedence_rule=cfg.precedence_rule,
                                  range_window=cfg.range_window, retest_window_bars=cfg.retest_window_bars),
                data_identity=data_identity, bar_count=N, build_seconds=round(build_s, 1),
                event_counts=dict(evc), established_bars=established_bars, n_guards=n_guards,
                accepted_and_failed_same_bar=both_acc_fail, verify_zero_lookahead=lookahead, verify_snapshot_restart=snap)
    json.dump(meta, open(OUT + "_meta.json", "w"), indent=2, default=str)
write_meta("PENDING", "PENDING")
log(f"SAVED {OUT}.npz + preliminary meta BEFORE verification; events={len(events)}")

# VERIFY zero-lookahead (event/state prefix stability) — non-fatal
def prefix_ok(k):
    e2 = R.RangeStateReplayEngine(symbol=SYM, timeframe=TF, bar_interval_seconds=IVAL, implementation_commit=IMPL, range_config=cfg)
    l2 = e2.replay_batch(bars[:k])
    return all(str(l2.records[j].consolidation_state) == str(recs[j].consolidation_state)
               and l2.records[j].n1_output_fingerprint == recs[j].n1_output_fingerprint for j in range(k))
try:
    lookahead_ok = all(prefix_ok(k) for k in (2000, 20000))
except Exception as _e:
    lookahead_ok = False; log(f"lookahead check errored (non-fatal): {_e}")
log(f"zero-lookahead prefix check: {'OK' if lookahead_ok else 'FAIL'}")

# VERIFY snapshot/restart preserves state + guard (F7 persists) — smaller K, non-fatal
cont_ok = False
try:
    K = 20000
    es = R.RangeStateReplayEngine(symbol=SYM, timeframe=TF, bar_interval_seconds=IVAL, implementation_commit=IMPL, range_config=cfg)
    es.replay_batch(bars[:K]); snap = es.snapshot()
    er = R.RangeStateReplayEngine(symbol=SYM, timeframe=TF, bar_interval_seconds=IVAL, implementation_commit=IMPL, range_config=cfg)
    er.restore(snap)
    cont_ok = all(er.observe_closed_bar(bars[K + j]).n1_output_fingerprint == recs[K + j].n1_output_fingerprint for j in range(1000))
except Exception as _e:
    log(f"snapshot check errored (non-fatal): {_e}")
log(f"snapshot/restart preservation: {'OK' if cont_ok else 'FAIL'}")

meta = dict(ve_n1_replay_version=R.VE_N1_REPLAY_VERSION, build_info=R.build_info(),
            range_state_contract=R.RANGE_STATE_CONTRACT_VERSION, range_event_contract=R.RANGE_EVENT_CONTRACT_VERSION,
            range_ledger_schema=R.RANGE_LEDGER_SCHEMA_VERSION, safety_guards=list(R.SAFETY_GUARDS_REGISTER),
            range_config=dict(n_touch=cfg.n_touch, tol_atr=cfg.tol_atr, er_max=cfg.er_max, d_min_bars=cfg.d_min_bars,
                              n_acceptance=cfg.n_acceptance, width_filter=cfg.width_filter, precedence_rule=cfg.precedence_rule,
                              range_window=cfg.range_window, retest_window_bars=cfg.retest_window_bars),
            data_identity=data_identity, bar_count=N, build_seconds=round(build_s, 1),
            event_counts=dict(evc), established_bars=established_bars, n_guards=n_guards,
            accepted_and_failed_same_bar=both_acc_fail,
            verify_zero_lookahead=lookahead_ok, verify_snapshot_restart=cont_ok)
json.dump(meta, open(OUT + "_meta.json", "w"), indent=2, default=str)
log(f"SAVED {OUT}.npz + meta  events={len(events)}")
log("RANGE_LEDGER_BUILD_COMPLETE " + ("PASS" if (lookahead_ok and cont_ok and both_acc_fail == 0) else "VERIFY_FAIL"))
