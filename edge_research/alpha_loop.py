"""ALPHA DISCOVERY — PERSISTENT CONTINUOUS-LOOP RUNNER (CEO service mandate).

ALPHA_DISCOVERY_MODE = CONTINUOUS_LOOP · AUTO_CONTINUE = TRUE · WAITING_AFTER_BATCH = FORBIDDEN.

Per candidate: read state → pre-register (ID + regime BEFORE result) → deterministic checks →
rapid falsification → PROVISIONAL screen (canonical evaluator, marked) → classify → save+checkpoint →
update m_total → (report per batch, WITHOUT stopping) → auto-continue. Idempotent: a completed
candidate is never re-run (crash/restart-safe). RANGE families are SKIPPED (TRUE_RANGE_NOT_IDENTIFIABLE).
Statuses: HYPOTHESIS_REGISTERED / STRUCTURALLY_FALSIFIED / ARCHIVE_INSUFFICIENT / PROVISIONAL_SCREENED /
FAT_TAIL_DEPENDENT / QUEUED_FOR_CANONICAL_RERUN. FORBIDDEN: RATIFIED / PROMOTED / LIVE_ELIGIBLE.

Run:  python -m edge_research.alpha_loop [--max N] [--restart-demo]
State persists under edge_research/loop_state/. Re-invoking resumes from the last checkpoint.
"""
from __future__ import annotations
import os, sys, json, time

_HERE = os.path.dirname(os.path.abspath(__file__))
for _c in [os.environ.get("RATIFIED_CODE_DIR"),
           r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\44ba92ba-04ad-40f2-a48e-0ee6a8aca893\scratchpad\ratified_code\code"]:
    if _c and os.path.isdir(_c):
        os.environ["RATIFIED_CODE_DIR"] = _c
        if _c not in sys.path:
            sys.path.insert(0, _c)
        break

STATE_DIR = os.path.join(_HERE, "loop_state")
os.makedirs(os.path.join(STATE_DIR, "reports"), exist_ok=True)
F_STATE = os.path.join(STATE_DIR, "loop_state.json")
F_REG = os.path.join(STATE_DIR, "hypothesis_registry.json")
F_WD = os.path.join(STATE_DIR, "watchdog.json")
F_OOS = os.path.join(STATE_DIR, "oos_access_log.json")

# ── INITIAL QUEUE (cells) + per-family budget. Order = the CEO initial queue. ──
INITIAL_QUEUE = ["CAND-T05", "CAND-T06", "CAND-TD01", "CAND-C01", "CAND-BT01", "CAND-BT02"]
FAMILY_BUDGET = dict(max_candidates_per_cycle=4, max_variants_per_hypothesis=2, max_refine_depth=1,
                     abandon_after_consecutive_falsified=6)
RANGE_CELLS = ["RANGE × mean reversion", "RANGE × level fade", "RANGE × boundary fade",
               "RANGE × center reversion"]  # SKIP: TRUE_RANGE_NOT_IDENTIFIABLE


def _load(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def _save(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, default=float)
    os.replace(tmp, path)   # atomic checkpoint


def now():
    return int(time.time()) if not os.environ.get("ALPHA_FROZEN_TS") else int(os.environ["ALPHA_FROZEN_TS"])


def init_state():
    return dict(loop_state="INIT", queue=list(INITIAL_QUEUE), completed_ids=[], failed_ids=[],
                canonical_rerun_queue=[], m_total=0, family_budget=FAMILY_BUDGET,
                current_candidate=None, last_checkpoint_ts=None, range_cells_skipped=RANGE_CELLS)


def watchdog(**kw):
    wd = _load(F_WD, dict(restart_count=-1))
    wd.update(kw); wd["heartbeat"] = now()
    _save(F_WD, wd)
    return wd


# ── evaluation + classification (PROVISIONAL) ──
def episodes_of(elig):
    out = []; i = 0; n = len(elig)
    while i < n:
        if elig[i]:
            j = i
            while j < n and elig[j]:
                j += 1
            out.append((i, j)); i = j
        else:
            i += 1
    return out


# RECENT-MARKET directive: the primary estimand is the recent window; FIXED now (no retrospective choice).
RECENT_START = "2022-12-01"; RECENT_END = "2025-10-23"


def _max_dd_R(rs_in_order):
    """Max drawdown of the cumulative R curve (trades in time order), in R units."""
    cum = 0.0; peak = 0.0; dd = 0.0
    for r in rs_in_order:
        cum += r; peak = max(peak, cum); dd = min(dd, cum - peak)
    return round(dd, 2)


def _window_stats(res_sub, elig, trades_sub, years):
    """Metrics + episode coverage + DD for a subset of trades (one window)."""
    from edge_research._screen import metrics
    eps = episodes_of(elig)
    def ep_idx(si):
        for k, (s, e) in enumerate(eps):
            if s <= si < e:
                return k
        return None
    used = {ep_idx(t.signal_idx) for t in trades_sub}; used.discard(None)
    k_eps = len(used)
    if not res_sub:
        return dict(n=0, k_episodes=k_eps)
    m = metrics(res_sub)
    byep, byyear = {}, {}
    for x in sorted(res_sub, key=lambda z: z["signal_idx"]):
        byep.setdefault(ep_idx(x["signal_idx"]), []).append(x["r"])
        byyear.setdefault(int(years[x["signal_idx"]]), []).append(x["r"])
    per_year = {str(y): round(sum(v) / len(v), 3) for y, v in sorted(byyear.items())}
    loo = round(min(m["total_R"] - sum(v) for v in byep.values()), 2) if len(byep) >= 2 else None
    dd = _max_dd_R([x["r"] for x in sorted(res_sub, key=lambda z: z["signal_idx"])])
    return dict(n=m["n"], k_episodes=k_eps, EV_net_avg_R=m["avg_R"], PF=m["profit_factor"],
                win_rate=m["win_rate"], median_R=m["median_R"], best_share=m.get("best_share_of_total"),
                trimmed_avg_R=m.get("trimmed_top1pct", {}).get("avg_R"), max_drawdown_R=dd,
                leave_one_episode_out_total_R=loo, per_year_avg_R=per_year)


def classify(res, elig, trades, years, dt):
    """RECENT-PRIMARY classification. Reports RECENT_PRIMARY (the estimand), HISTORICAL_TRANSFER (stress),
    COMBINED_DIAGNOSTIC (never decides). Decision is on RECENT: EV_net>0, >=5 recent episodes, not
    single-trade, trimmed-top-1% not inverting. Older losses do NOT auto-eliminate."""
    import pandas as pd
    rs_ = pd.Timestamp(RECENT_START, tz="UTC"); re_ = pd.Timestamp(RECENT_END, tz="UTC")
    is_recent = (pd.DatetimeIndex(dt) >= rs_) & (pd.DatetimeIndex(dt) < re_)
    recent = [x for x in res if is_recent[x["signal_idx"]]]
    hist = [x for x in res if not is_recent[x["signal_idx"]]]
    tr_recent = [t for t in trades if is_recent[t.signal_idx]]
    tr_hist = [t for t in trades if not is_recent[t.signal_idx]]
    R = _window_stats(recent, elig, tr_recent, years)     # PRIMARY
    H = _window_stats(hist, elig, tr_hist, years)          # TRANSFER / STRESS
    C = _window_stats(res, elig, trades, years)            # DIAGNOSTIC only

    k = R.get("k_episodes", 0); ev = R.get("EV_net_avg_R"); bs = R.get("best_share"); ta = R.get("trimmed_avg_R")
    if R.get("n", 0) == 0:
        st, rs = "STRUCTURALLY_FALSIFIED", "GATE1: no RECENT-window signals"
    elif k < 5:
        st, rs = "ARCHIVE_INSUFFICIENT", f"recent k={k}<5 eligible episodes (0.5^k not significant)"
    elif ev is None or ev <= 0:
        st, rs = "STRUCTURALLY_FALSIFIED", f"GATE1 recent GROSS EV<=0 (avg_R={ev})"
    elif bs is not None and bs > 0.5:
        st, rs = "STRUCTURALLY_FALSIFIED", f"recent single-trade dependence (best_share={bs})"
    elif (bs is not None and bs > 0.30) or (ta is not None and ta <= 0):
        st, rs = "FAT_TAIL_DEPENDENT", f"recent GROSS+ but fat-tail (best_share={bs}, trimmed={ta}); net UNEVALUATED"
    else:
        st, rs = "PROVISIONAL_SCREENED", "recent GROSS EV>0 & trim-robust; net pending ratified cost model"
    return dict(status=st, reason=rs, RECENT_PRIMARY=R, HISTORICAL_TRANSFER=H, COMBINED_DIAGNOSTIC=C,
                estimand="RECENT_PRIMARY (2022-12→2025-10)")


def process_spec(cid, spec, ctx, years, dt):
    """PHASE A per-hypothesis loop (generator-driven). GATE 0 (determinism/lookahead) + GATE 1 (GROSS,
    cost=0) + episode count + fat-tail on GROSS. NET is UNEVALUATED (Phase B / ratified cost model)."""
    from edge_research.flowb_generator import gen_signals
    from edge_research._screen import canonical_evaluate
    base = dict(candidate_id=cid, cell=spec["cell"], family=spec["family"], regime=spec["regime"],
                run_hash=spec["run_hash"], spec={k: spec[k] for k in ("entry", "stop", "hold", "exit_label")},
                ts=now(), cost_version="PENDING_AI_TRADER_SHADOW_COST_MODEL_v1",
                net_status="UNEVALUATED_PENDING_RATIFIED_COST",
                MARK="PROVISIONAL · GROSS-GATED · NET UNEVALUATED · REQUIRES CANONICAL RERUN")
    trades, elig = gen_signals(ctx, spec)
    det = []
    for t in trades:                                     # GATE 0: determinism + lookahead + regime-gate
        if not (0 < t.signal_idx < ctx.n - 1):
            det.append("entry idx out of range")
        if not elig[t.signal_idx]:
            det.append("signal OUTSIDE pre-registered regime")
    if det:
        return dict(**base, status="STRUCTURALLY_FALSIFIED", reason="GATE0: " + ";".join(sorted(set(det))))
    res = canonical_evaluate(ctx.d, trades, gross=True) if trades else []   # GATE 1 GROSS
    cl = classify(res, elig, trades, years, dt)
    return dict(**base, **cl)


def run(max_candidates=None):
    from edge_research._common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
    from edge_research._screen import derive_blocks
    from edge_research.flowb_strategies import Ctx
    wd = _load(F_WD, dict(restart_count=-1))
    wd = watchdog(restart_count=wd.get("restart_count", -1) + 1, current_phase="startup", last_error=None)
    st = _load(F_STATE, None) or init_state()
    reg = _load(F_REG, [])
    _save(F_OOS, _load(F_OOS, []))   # OOS access log stays EMPTY — holdout is sealed by _common.load
    st["loop_state"] = "ACTIVE"

    d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    blocks = derive_blocks(d)                          # R9: manifest 4-block population
    years = d["dt"].dt.year.to_numpy()
    dt = d["dt"]
    ctx = Ctx(d, blocks)
    n_blocks = len(blocks)

    processed = 0
    # PHASE A — generator-driven. Build the grid; process specs whose run_hash is NOT already in the
    # registry (idempotent). m_total continues (NOT reset). T05 (frozen) is untouched.
    from edge_research.flowb_generator import build_grid
    grid = build_grid()
    done_hashes = {r.get("run_hash") for r in reg if r.get("run_hash")}
    seq_start = st.get("gen_seq", 0)
    batch_records = []
    for gi, spec in enumerate(grid):
        if max_candidates is not None and processed >= max_candidates:
            break
        if spec["run_hash"] in done_hashes:
            continue                                    # IDEMPOTENT — never re-run a finalized hypothesis
        seq_start += 1
        cid = f"CAND-G{seq_start:04d}"
        watchdog(current_candidate=cid, current_phase="processing", last_commit=None)
        try:
            rec = process_spec(cid, spec, ctx, years, dt)
        except Exception as e:
            watchdog(current_candidate=cid, current_phase="CANDIDATE_ERROR", last_error=str(e)[:200])
            rec = dict(candidate_id=cid, run_hash=spec["run_hash"], cell=spec["cell"],
                       status="STRUCTURALLY_FALSIFIED", reason=f"error: {str(e)[:120]}", ts=now())
        reg.append(rec); done_hashes.add(spec["run_hash"])
        st["m_total"] += 1; st["gen_seq"] = seq_start
        (st["failed_ids"] if rec["status"] in ("STRUCTURALLY_FALSIFIED", "ARCHIVE_INSUFFICIENT")
         else st["completed_ids"]).append(cid)
        if rec["status"] in ("PROVISIONAL_SCREENED", "FAT_TAIL_DEPENDENT"):
            st["canonical_rerun_queue"].append(cid)
        st["last_checkpoint_ts"] = now()
        _save(F_STATE, st); _save(F_REG, reg)          # CHECKPOINT after every hypothesis
        batch_records.append(rec); processed += 1
        watchdog(current_candidate=cid, current_phase="checkpointed")
        if processed % 25 == 0:                          # report per 25 — WITHOUT stopping
            _save(os.path.join(STATE_DIR, "reports", f"batch_{now()}_{processed}.json"),
                  dict(processed=processed, m_total=st["m_total"]))

    # SHORTLIST: <=5 PROVISIONAL_SCREENED survivors, ranked by recent GROSS trimmed avg_R (robust EV).
    survivors = [r for r in reg if r.get("status") == "PROVISIONAL_SCREENED"
                 and r.get("RECENT_PRIMARY", {}).get("trimmed_avg_R") is not None]
    survivors.sort(key=lambda r: r["RECENT_PRIMARY"]["trimmed_avg_R"], reverse=True)
    shortlist = [r["candidate_id"] for r in survivors[:5]]
    st["ACTIVE_PROVISIONAL_SHORTLIST"] = shortlist
    remaining = sum(1 for s in grid if s["run_hash"] not in done_hashes)
    st["loop_state"] = "ALPHA_LOOP_ACTIVE" if remaining else "GRID_EXHAUSTED"
    _save(F_STATE, st)
    report = dict(status="ALPHA_LOOP_ACTIVE", phase="A (GROSS-gated; net UNEVALUATED)",
                  m_total=st["m_total"], processed_this_run=processed, grid_total=len(grid),
                  grid_remaining=remaining, ACTIVE_PROVISIONAL_SHORTLIST=shortlist,
                  n_provisional=len(survivors), n_fat_tail=sum(1 for r in reg if r.get("status") == "FAT_TAIL_DEPENDENT"),
                  n_falsified=sum(1 for r in reg if r.get("status") == "STRUCTURALLY_FALSIFIED"),
                  n_archive=sum(1 for r in reg if r.get("status") == "ARCHIVE_INSUFFICIENT"),
                  primary_estimand="RECENT_PRIMARY 2022-12→2025-10 (GROSS)",
                  batch=[dict(id=r["candidate_id"], cell=r.get("cell"), status=r["status"],
                              recent_gross=r.get("RECENT_PRIMARY", {}).get("EV_net_avg_R"),
                              recent_trimmed=r.get("RECENT_PRIMARY", {}).get("trimmed_avg_R"),
                              recent_k=r.get("RECENT_PRIMARY", {}).get("k_episodes")) for r in batch_records])
    _save(os.path.join(STATE_DIR, "reports", f"report_{now()}.json"), report)
    return report


if __name__ == "__main__":
    args = sys.argv[1:]
    mx = None
    if "--max" in args:
        mx = int(args[args.index("--max") + 1])
    rep = run(max_candidates=mx)
    print(json.dumps(rep, indent=2, default=float))
