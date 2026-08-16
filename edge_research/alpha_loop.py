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


def _window_stats(res_sub, elig, trades_sub, years, wmask):
    """EPISODE-PRIMARY stats for one window. wmask = per-bar bool of the window. Episodes are contiguous
    runs of (elig AND window). Reports eligible bars/episodes, per-episode net_R, best-episode share,
    walk-forward folds, and NOT_APPLICABLE_YEAR / ELIGIBLE_YEAR_NEGATIVE labels."""
    from edge_research._screen import metrics
    import numpy as np
    elig_w = np.asarray(elig) & np.asarray(wmask)
    eps = episodes_of(elig_w)
    def ep_idx(si):
        for k, (s, e) in enumerate(eps):
            if s <= si < e:
                return k
        return None
    n_elig_bars = int(elig_w.sum()); n_elig_eps = len(eps)
    used = {ep_idx(t.signal_idx) for t in trades_sub}; used.discard(None); k_eps = len(used)
    if not res_sub:
        return dict(n=0, n_eligible_bars=n_elig_bars, n_eligible_episodes=n_elig_eps, k_episodes_with_trades=k_eps)
    ordered = sorted(res_sub, key=lambda z: z["signal_idx"])
    m = metrics(res_sub)
    byep, byyear = {}, {}
    for x in ordered:
        byep.setdefault(ep_idx(x["signal_idx"]), []).append(x["r"])
        byyear.setdefault(int(years[x["signal_idx"]]), []).append(x["r"])
    ep_R = {str(k): round(sum(v), 2) for k, v in sorted(byep.items(), key=lambda kv: (kv[0] is None, kv[0]))}
    tot = m["total_R"]
    best_ep_share = round(max(abs(sum(v)) for v in byep.values()) / abs(tot), 3) if tot else None
    loo = round(min(tot - sum(v) for v in byep.values()), 2) if len(byep) >= 2 else None
    dd = _max_dd_R([x["r"] for x in ordered])
    # walk-forward: 3 time-ordered folds within the window (stability, not optimization)
    rs = [x["r"] for x in ordered]; f = max(1, len(rs) // 3)
    wf = [round(sum(rs[i:i+f]) / max(1, len(rs[i:i+f])), 3) for i in range(0, len(rs), f)][:3]
    # year diagnostics with NOT_APPLICABLE labels
    yr_elig = {}
    yidx = np.asarray(years)
    for y in sorted(set(int(v) for v in yidx[wmask])) if np.any(wmask) else []:
        eb = int((elig_w & (yidx == y)).sum())
        if eb == 0:
            yr_elig[str(y)] = "NOT_APPLICABLE_YEAR"
        else:
            avg = sum(byyear.get(y, [0])) / max(1, len(byyear.get(y, [])))
            yr_elig[str(y)] = ("ELIGIBLE_YEAR_NEGATIVE" if avg <= 0 else round(avg, 3)) if y in byyear else "ELIGIBLE_NO_TRADE"
    return dict(n=m["n"], n_eligible_bars=n_elig_bars, n_eligible_episodes=n_elig_eps,
                k_episodes_with_trades=k_eps, EV_net_avg_R=m["avg_R"], PF=m["profit_factor"],
                win_rate=m["win_rate"], median_R=m["median_R"], best_share=m.get("best_share_of_total"),
                best_episode_share=best_ep_share, trimmed_avg_R=m.get("trimmed_top1pct", {}).get("avg_R"),
                max_drawdown_R=dd, leave_one_episode_out_total_R=loo, walk_forward_folds=wf,
                per_episode_R=ep_R, year_diag=yr_elig)


def classify(res, elig, trades, years, dt):
    """RECENT-PRIMARY classification. Reports RECENT_PRIMARY (the estimand), HISTORICAL_TRANSFER (stress),
    COMBINED_DIAGNOSTIC (never decides). Decision is on RECENT: EV_net>0, >=5 recent episodes, not
    single-trade, trimmed-top-1% not inverting. Older losses do NOT auto-eliminate."""
    import pandas as pd, numpy as np
    rs_ = pd.Timestamp(RECENT_START, tz="UTC"); re_ = pd.Timestamp(RECENT_END, tz="UTC")
    di = pd.DatetimeIndex(dt)
    is_recent = np.asarray((di >= rs_) & (di < re_))
    is_hist = np.asarray(di < rs_)              # 2011-2021 same-regime (elig already gates regime)
    recent = [x for x in res if is_recent[x["signal_idx"]]]
    hist = [x for x in res if is_hist[x["signal_idx"]]]
    tr_recent = [t for t in trades if is_recent[t.signal_idx]]
    tr_hist = [t for t in trades if is_hist[t.signal_idx]]
    R = _window_stats(recent, elig, tr_recent, years, is_recent)   # PRIMARY (episode unit)
    H = _window_stats(hist, elig, tr_hist, years, is_hist)         # HISTORICAL_REGIME_TRANSFER
    C = _window_stats(res, elig, trades, years, np.ones(len(elig), bool))  # DIAGNOSTIC only

    k = R.get("n_eligible_episodes", 0); kt = R.get("k_episodes_with_trades", 0)
    ev = R.get("EV_net_avg_R"); bs = R.get("best_share"); ta = R.get("trimmed_avg_R")
    bes = R.get("best_episode_share")
    h_ev = H.get("EV_net_avg_R")
    # GROSS-ONLY labels: NET is UNEVALUATED (no ratified cost), so the confirmed 'survivor/provisional'
    # verdicts are FORBIDDEN. These are GROSS gates awaiting the ratified cost model.
    if R.get("n", 0) == 0:
        st, rs = "GROSS_STRUCTURALLY_FALSIFIED", "GATE1: no RECENT-window signals"
    elif kt < 5:
        st, rs = "ARCHIVE_INSUFFICIENT", f"recent episodes-with-trades={kt}<5 (0.5^k not significant)"
    elif ev is None or ev <= 0:
        st, rs = "GROSS_STRUCTURALLY_FALSIFIED", f"GATE1 recent GROSS EV<=0 (avg_R={ev})"
    elif bs is not None and bs > 0.5:
        st, rs = "GROSS_STRUCTURALLY_FALSIFIED", f"recent single-trade dependence (best_share={bs})"
    elif (bs is not None and bs > 0.30) or (ta is not None and ta <= 0) or (bes is not None and bes > 0.5):
        st, rs = "GROSS_FAT_TAIL_DEPENDENT", f"recent GROSS+ but concentrated (best_trade={bs}, best_episode={bes}, trimmed={ta})"
    elif h_ev is not None and h_ev > 0:
        st, rs = "GROSS_EPISODE_SURVIVOR_AWAITING_COST", f"recent GROSS EV>0 robust + historical same-regime GROSS transfer +{h_ev}; NET UNEVALUATED → AWAITING_COST_QUEUE"
    else:
        st, rs = "RECENT_GROSS_SIGNAL_AWAITING_COST", f"recent GROSS EV>0 robust; historical GROSS transfer weak (EV={h_ev}); NET UNEVALUATED → AWAITING_COST_QUEUE"
    return dict(status=st, reason=rs, RECENT_PRIMARY=R, HISTORICAL_REGIME_TRANSFER=H, COMBINED_DIAGNOSTIC=C,
                estimand="RECENT_PRIMARY episodes (2022-12→2025-10)", position_at_regime_end="HOLD_UNTIL_STRATEGY_EXIT")


SURVIVOR_STATUSES = ("GROSS_EPISODE_SURVIVOR_AWAITING_COST", "RECENT_GROSS_SIGNAL_AWAITING_COST")


def build_shortlist_and_clusters(reg):
    """Two rankings. A mechanism CLUSTER = (family, regime, entry) — variants differing only by
    stop/hold/exit are ONE mechanism, not N edges. Shortlist = <=5 ECONOMICALLY DISTINCT mechanisms,
    one representative each (best surviving variant by recent trimmed). NET UNEVALUATED → all AWAITING_COST."""
    import statistics
    from edge_research.flowb_generator import cluster_of
    clusters = {}
    for r in reg:
        sp = r.get("spec") or {}
        mech = r.get("mechanism_cluster") or cluster_of(r.get("family"), r.get("regime"), sp.get("entry"))
        clusters.setdefault(mech, []).append(r)
    cluster_rank = []
    for mech, variants in clusters.items():
        surv = [v for v in variants if v.get("status") in SURVIVOR_STATUSES
                and v.get("RECENT_PRIMARY", {}).get("trimmed_avg_R") is not None]
        if not surv:
            continue
        surv.sort(key=lambda v: v["RECENT_PRIMARY"]["trimmed_avg_R"], reverse=True)
        rep = surv[0]; weakest = surv[-1]
        evs = [v["RECENT_PRIMARY"]["EV_net_avg_R"] for v in variants if v.get("RECENT_PRIMARY", {}).get("EV_net_avg_R") is not None]
        cluster_rank.append(dict(mechanism_id=mech, n_variants=len(variants), n_surviving=len(surv),
                                 surviving_frac=round(len(surv) / len(variants), 2),
                                 representative=rep["candidate_id"], rep_recent_trimmed=rep["RECENT_PRIMARY"]["trimmed_avg_R"],
                                 rep_recent_gross_EV=rep["RECENT_PRIMARY"]["EV_net_avg_R"],
                                 weakest=weakest["candidate_id"],
                                 EV_dispersion=round(statistics.pstdev(evs), 3) if len(evs) > 1 else 0.0))
    cluster_rank.sort(key=lambda c: c["rep_recent_trimmed"], reverse=True)
    # SHORTLIST: <=5 DISTINCT mechanisms, one representative each (never 5 pullback3 variants)
    shortlist = [dict(mechanism_id=c["mechanism_id"], representative=c["representative"],
                      recent_trimmed=c["rep_recent_trimmed"], recent_gross_EV=c["rep_recent_gross_EV"],
                      status="GROSS_ONLY_AWAITING_COST", surviving_frac=c["surviving_frac"])
                 for c in cluster_rank[:5]]
    return shortlist, cluster_rank


def process_spec(cid, spec, ctx, years, dt):
    """PHASE A per-hypothesis loop (generator-driven). GATE 0 (determinism/lookahead) + GATE 1 (GROSS,
    cost=0) + episode count + fat-tail on GROSS. NET is UNEVALUATED (Phase B / ratified cost model)."""
    from edge_research.flowb_generator import gen_signals, semantic_fingerprint, evaluation_run_hash
    from edge_research._screen import canonical_evaluate
    # RUN CONTEXT = the exact evaluation identity (NOT the economic hypothesis). Changing any of these =>
    # new evaluation_run_hash, SAME hypothesis_semantic_fingerprint + SAME m.
    run_context = dict(data_identity="M15_v2/pre_holdout/4-block/2011-2025",
                       evaluator="mstrat.simulate", cost_model="GROSS(spread=0)_AWAITING_RATIFIED",
                       engine_snapshot="canonical@f0d3b34", ratified_snapshot="5443077",
                       measurement_contract="episode_primary_v2", classifier_version="alpha_swing_regime_v1",
                       n1_contract="NONCANONICAL_alpha_swing", router_version="NONE_not_routed",
                       eligibility_version="alpha_swing_regime_v1")
    hsf = spec.get("hypothesis_semantic_fingerprint", spec["run_hash"])
    base = dict(candidate_id=cid, cell=spec["cell"], family=spec["family"], regime=spec["regime"],
                hypothesis_semantic_fingerprint=hsf, run_hash=hsf,
                evaluation_run_hash=evaluation_run_hash(hsf, run_context), run_context=run_context,
                configuration_fingerprint=spec["run_hash"],
                mechanism_cluster=spec.get("mechanism_cluster"), generator_version=spec.get("generator_version"),
                economic_rationale=spec.get("economic_rationale"), direction=spec.get("direction"),
                parameter_neighborhood=spec.get("parameter_neighborhood"),
                semantic_fingerprint=semantic_fingerprint(spec["family"], spec["regime"], spec["entry"], spec.get("direction", "")),
                position_at_regime_end=spec.get("position_at_regime_end"),
                spec={k: spec[k] for k in ("entry", "stop", "hold", "exit_label")},
                preregistration_ts=now(), ts=now(), cost_version="PENDING_AI_TRADER_SHADOW_COST_MODEL_v1",
                net_status="UNEVALUATED_PENDING_RATIFIED_COST",
                MARK="GROSS_GATED · NET UNEVALUATED · AWAITING_COST")
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
        (st["failed_ids"] if rec["status"] in ("GROSS_STRUCTURALLY_FALSIFIED", "ARCHIVE_INSUFFICIENT")
         else st["completed_ids"]).append(cid)
        if rec["status"] in ("GROSS_EPISODE_SURVIVOR_AWAITING_COST", "RECENT_GROSS_SIGNAL_AWAITING_COST"):
            st.setdefault("AWAITING_COST_QUEUE", []).append(cid)
        st["last_checkpoint_ts"] = now()
        _save(F_STATE, st); _save(F_REG, reg)          # CHECKPOINT after every hypothesis
        batch_records.append(rec); processed += 1
        watchdog(current_candidate=cid, current_phase="checkpointed")
        if processed % 25 == 0:                          # report per 25 — WITHOUT stopping
            _save(os.path.join(STATE_DIR, "reports", f"batch_{now()}_{processed}.json"),
                  dict(processed=processed, m_total=st["m_total"]))

    shortlist, clusters = build_shortlist_and_clusters(reg)
    st["ACTIVE_PROVISIONAL_SHORTLIST"] = shortlist
    remaining = sum(1 for s in grid if s["run_hash"] not in done_hashes)
    # AUTO-REFILL: catalog with work -> ACTIVE. Catalog fully enumerated -> GENERATOR_EXHAUSTED +
    # IMPLEMENTATION_QUEUE (mechanisms needing NEW declarative logic, not arbitrary runtime code).
    if remaining > 0:
        st["loop_state"] = "ALPHA_LOOP_ACTIVE"; status = "ALPHA_LOOP_ACTIVE"
    else:
        st["loop_state"] = "GENERATOR_EXHAUSTED"; status = "ALPHA_LOOP_IDLE_NO_WORK"
        st["IMPLEMENTATION_QUEUE"] = ["EXIT_ON_REGIME_INVALIDATION (needs dynamic regime-exit in simulator)",
                                     "session-conditioned continuation (needs session eligibility x trend)",
                                     "volatility-conditioned trend (needs vol-regime gate)",
                                     "acceptance/value-area entries (needs new detector)"]
    st["snapshot_provenance"] = dict(vendor="C:/Users/MEDION GAMING/.alpha_vendor",
        ratified_source="alpha1/discovery-mk-matrix-v1", ratified_commit="5443077",
        canonical_commit="f0d3b34", note="changing a snapshot => new run_hash, results NON_COMPARABLE")
    _save(F_STATE, st)
    from collections import Counter
    sc = Counter(r.get("status") for r in reg)
    report = dict(status=status, wave=st.get("wave_id", 1), phase="A (GROSS-gated; NET UNEVALUATED; regime-episode-primary)",
                  m_total=st["m_total"], processed_this_run=processed, grid_total=len(grid),
                  grid_remaining=remaining, n_distinct_mechanisms=len(clusters),
                  ACTIVE_PROVISIONAL_SHORTLIST=shortlist, MECHANISM_CLUSTER_RANKING=clusters[:8],
                  AWAITING_COST_QUEUE_n=len(st.get("AWAITING_COST_QUEUE", [])),
                  ROUTER_PARITY=st.get("ROUTER_PARITY", "PENDING (official N1/StrategyRouter not yet fixtured)"),
                  OOS_access_count=len(_load(F_OOS, [])),
                  status_counts=dict(sc), primary_estimand="RECENT_PRIMARY episodes 2022-12→2025-10 (GROSS)",
                  batch=[dict(id=r["candidate_id"], cell=r.get("cell"), status=r["status"],
                              recent_gross=r.get("RECENT_PRIMARY", {}).get("EV_net_avg_R"),
                              recent_trimmed=r.get("RECENT_PRIMARY", {}).get("trimmed_avg_R"),
                              recent_eps=r.get("RECENT_PRIMARY", {}).get("k_episodes_with_trades"),
                              hist=r.get("HISTORICAL_REGIME_TRANSFER", {}).get("EV_net_avg_R")) for r in batch_records])
    _save(os.path.join(STATE_DIR, "reports", f"report_{now()}.json"), report)
    return report


if __name__ == "__main__":
    args = sys.argv[1:]
    mx = None
    if "--max" in args:
        mx = int(args[args.index("--max") + 1])
    rep = run(max_candidates=mx)
    print(json.dumps(rep, indent=2, default=float))
