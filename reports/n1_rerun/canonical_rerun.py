"""ALPHA CANONICAL RERUN — rerun the 355 existing hypotheses on the canonical N1/Router regime
(ve_n1_replay 0.1.1 ledger) + official RATIFIED cost (AI_TRADER_SHADOW_COST_MODEL_v1) BASE & STRESS + MDE,
episode-primary. m NOT increased; hsf preserved; evaluation_run_hash changes. Checkpointed/idempotent.
SEALED 2025-11+ never touched (official loader), OOS access stays 0."""
import sys, os, json, time, math, hashlib
import numpy as np

ALPHA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
WP5B_CODE = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code"
COST_MANIFEST = r"C:\Users\MEDION GAMING\ai_quant_lab-research-main\AI_TRADER_SHADOW_COST_MODEL_v1.json"
os.environ.setdefault("RATIFIED_CODE_DIR", WP5B_CODE)
os.environ["ALPHA_FROZEN_TS"] = os.environ.get("ALPHA_FROZEN_TS", "1787000000")
for p in (ALPHA, os.path.join(ALPHA, "code"), WP5B_CODE):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ALPHA)

try:
    import ctypes; ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
except Exception: pass

import pandas as pd
from edge_research._common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
from edge_research._screen import derive_blocks, _canonical, trades_to_setups
from edge_research.flowb_strategies import Ctx
from edge_research.flowb_generator import gen_signals, build_grid, cluster_of, evaluation_run_hash
from edge_research.alpha_loop import _window_stats, RECENT_START, RECENT_END
import mstrat

SP = os.path.dirname(os.path.abspath(__file__))
LEDGER_NPZ = os.path.join(SP, "n1_ledger.npz"); LEDGER_META = os.path.join(SP, "n1_ledger_meta.json")
OUT = os.path.join(SP, "canonical_rerun_records.json")
PROG = os.path.join(SP, "canonical_rerun_progress.json")
def log(m):
    print(f"[{int(time.time())}] {m}", flush=True)
    open(os.path.join(SP, "canonical_rerun.log"), "a").write(f"{int(time.time())} {m}\n")

# ── cost model (official, RATIFIED) ───────────────────────────────────────────────────────────────
CM = json.load(open(COST_MANIFEST))
assert CM["calibration_status"] == "RATIFIED", "cost model not RATIFIED"
BASE_RT = CM["base_ratified"]["round_trip_total"]      # 0.05
STRESS_RT = CM["stress_ratified"]["round_trip_total"]  # 0.24
TICK = mstrat.TICK                                     # reconciled 0.01 (RT-CODE-A-0007)
# mstrat deducts 2*cost = 2*(spread_ticks+slip_ticks)*TICK. Put cost in slip_ticks, spread_ticks=0, so the
# executable-stop floor max(2*spread*TICK, 5*TICK, 0.10*atr) stays max(0.05,0.10*atr) — identical to gross
# and identical across BASE/STRESS. slip = round_trip/(2*TICK).
def cost_cfg(round_trip):
    _, CFG = _canonical(); cfg = dict(CFG)
    cfg["spread_ticks"] = 0.0; cfg["slip_ticks"] = round_trip / (2.0 * TICK)
    return cfg
COST_ID = dict(version=CM["shadow_cost_model_version"], calibration_status=CM["calibration_status"],
               configuration_fingerprint=CM["configuration_fingerprint"], content_hash=CM["content_hash"],
               cost_provenance_window=CM["cost_provenance_window"]["observed_calendar_days_utc"],
               n_observations=CM["data_identity"]["n_clean_observations"], spread_iqr=CM["spread_dispersion_iqr"],
               standard_error="UNAVAILABLE", base_round_trip=BASE_RT, stress_round_trip=STRESS_RT,
               tick=TICK, mapping="slip_ticks=round_trip/(2*TICK); spread_ticks=0; floor=max(0.05,0.10*atr) invariant")

def evaluate(d, trades, round_trip):
    sim, _ = _canonical(); cfg = cost_cfg(round_trip)
    dd = d.copy()
    if "m_atr" not in dd.columns: dd["m_atr"] = dd["atr14"]
    setups = trades_to_setups(trades)
    led = sim(dd, setups, cfg)
    return [dict(r=float(r), signal_idx=int(si)) for r, si in zip(led["R"].to_numpy(), led["si"].to_numpy())]

# ── load data (official loader → pre-holdout, SEALED excluded) ────────────────────────────────────
log("loading pre-holdout M15_v2 via official loader (SEALED excluded)")
d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
blocks = derive_blocks(d)
years = d["dt"].dt.year.to_numpy(); dt = d["dt"]
n = len(d); log(f"d rows={n} blocks={len(blocks)} span={d['dt'].iloc[0]}..{d['dt'].iloc[-1]}")
assert d["dt"].max() < pd.Timestamp(RESEARCH_HOLDOUT_CUTOFF_UTC), "SEALED leak!"

# ── canonical N1 regime from the ledger, aligned by ts ────────────────────────────────────────────
Z = np.load(LEDGER_NPZ, allow_pickle=True); LM = json.load(open(LEDGER_META))
VOCAB = list(LM["vocab"]); bit = {name: 1 << i for i, name in enumerate(VOCAB)}
led_ts = Z["ts_open"].astype(np.int64); led_mask = Z["mask"]
d_ts = d["time"].astype(np.int64).to_numpy()
pos = np.searchsorted(led_ts, d_ts)
assert (pos < len(led_ts)).all() and (led_ts[pos] == d_ts).all(), "d timestamps not all in ledger"
mask_d = led_mask[pos]                                   # canonical applicable-regime bitmask per d-bar
reg_canonical = np.where((mask_d & bit["TREND_UP"]) != 0, "TREND_UP",
                 np.where((mask_d & bit["TREND_DOWN"]) != 0, "TREND_DOWN", "NONE")).astype(object)
log(f"canonical regime aligned; TREND_UP bars={int(((mask_d&bit['TREND_UP'])!=0).sum())} "
    f"TREND_DOWN={int(((mask_d&bit['TREND_DOWN'])!=0).sum())} "
    f"COMPRESSION={int(((mask_d&bit['COMPRESSION'])!=0).sum())} "
    f"BREAKOUT={int(((mask_d&bit['BREAKOUT_TRANSITION'])!=0).sum())}")

# canonical Ctx: entry primitives (sh/sl/exp/breaks) stay the alpha lineage; ONLY regime becomes canonical
ctx = Ctx(d, blocks)
ctx.reg = list(reg_canonical)

# ── run context / evaluation identity (everything that makes this evaluation reproducible) ─────────
RUN_CONTEXT_BASE = dict(
    data_identity=LM["data_identity"], evaluator="mstrat.simulate@wp5b_reconciled(TICK=0.01,RT-CODE-A-0007)",
    ve_n1_replay_version=LM["ve_n1_replay_version"], ve_n1_replay_wheel_sha256="2cff7e7be1f9401c10753f751a1189a512f5be39946dfada4260b9c5e1cd29ab",
    ve_brain_version=LM["build_info"]["ve_brain_version"], ve_brain_wheel_sha256=LM["build_info"]["ve_brain_wheel_sha256"],
    n1_contract_version=LM["n1_contract_version"], router_version=LM["router_version"],
    detector_submodule_commit=LM["build_info"]["detector_submodule_commit"],
    detector_configuration=LM["ledger_key"], snapshot_schema=LM["build_info"]["snapshot_schema_version"],
    ledger_key=LM["ledger_key"], ledger_eval_identity=LM["evaluation_identity_fingerprint"],
    history_horizon=LM["history_horizon"], history_horizon_version=LM["history_horizon_version"],
    eligibility_contract="applicable_regimes(RawAxes) membership @ signal bar",
    regime_episode_definition="maximal runs where hypothesis.regime in applicable_regimes (episode-primary v2)",
    measurement_contract="episode_primary_v2", classifier_version="ve_n1_replay_canonical_0.1.1",
    exit_policy="HOLD_UNTIL_STRATEGY_EXIT (hypothesis spec)", cost_model=COST_ID)

# ── verdict (mandate 6) ───────────────────────────────────────────────────────────────────────────
Z_A, Z_P = 1.6449, 0.8416   # one-sided alpha=0.05, power=0.80
def mde_of(res_recent, n):
    if n < 2: return None
    rs = np.array([x["r"] for x in res_recent], float); sd = rs.std(ddof=1)
    return float((Z_A + Z_P) * sd / math.sqrt(n))

def classify_canonical(res_base, res_stress, res_gross, elig, trades, years, dt):
    rs_ = pd.Timestamp(RECENT_START, tz="UTC"); re_ = pd.Timestamp(RECENT_END, tz="UTC")
    di = pd.DatetimeIndex(dt); is_recent = np.asarray((di >= rs_) & (di < re_)); is_hist = np.asarray(di < rs_)
    def split(res): return [x for x in res if is_recent[x["signal_idx"]]], [x for x in res if is_hist[x["signal_idx"]]]
    rb, hb = split(res_base); rs2, hs = split(res_stress); rg, hg = split(res_gross)
    tr_recent = [t for t in trades if is_recent[t.signal_idx]]; tr_hist = [t for t in trades if is_hist[t.signal_idx]]
    RB = _window_stats(rb, elig, tr_recent, years, is_recent); HB = _window_stats(hb, elig, tr_hist, years, is_hist)
    CB = _window_stats(res_base, elig, trades, years, np.ones(len(elig), bool))
    RS = _window_stats(rs2, elig, tr_recent, years, is_recent)
    RG = _window_stats(rg, elig, tr_recent, years, is_recent)
    n = RB.get("n", 0); kt = RB.get("k_episodes_with_trades", 0)
    ev_base = RB.get("EV_net_avg_R"); ev_stress = RS.get("EV_net_avg_R"); ev_gross = RG.get("EV_net_avg_R")
    bs = RB.get("best_share"); ta = RB.get("trimmed_avg_R"); bes = RB.get("best_episode_share")
    h_ev = HB.get("EV_net_avg_R"); mde = mde_of(rb, n)
    def verdict(ev, ev_g, mde_):
        if n == 0 or kt < 5: return "ARCHIVE_INSUFFICIENT", f"recent episodes-with-trades={kt}<5 or n=0"
        if ev_g is not None and ev_g <= 0: return "NET_STRUCTURALLY_NEGATIVE_GROSS", f"gross recent EV<=0 ({ev_g}) — not a cost effect"
        if ev is None: return "ARCHIVE_INSUFFICIENT", "no recent net estimate"
        if ev <= 0:
            if mde_ is not None and abs(ev) >= mde_: return "COST_BASE_FALSIFIED", f"net EV={ev}<=0, |EV|>=MDE={round(mde_,4)}, gross>0 → cost kills it"
            return "ARCHIVE_INSUFFICIENT", f"net EV={ev}<=0 but |EV|<MDE={round(mde_,4) if mde_ else None} — insufficient power"
        if (bs is not None and bs > 0.30) or (ta is not None and ta <= 0) or (bes is not None and bes > 0.5):
            return "NET_FAT_TAIL_DEPENDENT", f"net>0 but concentrated (best_trade={bs}, best_episode={bes}, trimmed={ta})"
        if h_ev is not None and h_ev > 0: return "CANONICAL_PROVISIONAL_SURVIVOR", f"recent net BASE EV={ev}>0 robust + historical same-regime transfer +{h_ev}; PROVISIONAL, PENDING_REVIEW"
        return "RECENT_REGIME_NET_PROVISIONAL", f"recent net BASE EV={ev}>0 robust; historical transfer weak (EV={h_ev})"
    st_base, rs_base = verdict(ev_base, ev_gross, mde)
    st_stress, _ = verdict(ev_stress, ev_gross, mde_of(rs2, RS.get("n", 0)))
    turnover = round(n / max(1, RB.get("n_eligible_bars", 1)), 5)
    return dict(status=st_base, reason=rs_base, stress_status=st_stress,
                RECENT_PRIMARY_BASE=RB, RECENT_PRIMARY_STRESS=RS, RECENT_PRIMARY_GROSS=RG,
                HISTORICAL_TRANSFER_BASE=HB, COMBINED_DIAGNOSTIC_BASE=CB,
                mde_BASE=round(mde, 5) if mde else None, ev_gross=ev_gross, ev_base=ev_base, ev_stress=ev_stress,
                turnover_recent=turnover, estimand="RECENT_PRIMARY episodes (2022-12→2025-10)",
                position_at_regime_end="HOLD_UNTIL_STRATEGY_EXIT")

# ── build the 355-hypothesis worklist (registry + grid backfill; UNRESOLVED → RERUN_BLOCKED) ───────
reg = json.load(open(os.path.join(ALPHA, "edge_research/loop_state/hypothesis_registry.json")))
grid = build_grid(); by_rh = {s["run_hash"]: s for s in grid if "run_hash" in s}
def spec_of(rec):
    sp = rec.get("spec"); rh = rec.get("run_hash")
    if sp and rec.get("regime") and all(k in sp for k in ("entry", "stop", "hold")):
        g = by_rh.get(rh, {})
        return dict(regime=rec["regime"], entry=sp["entry"], stop=sp["stop"], hold=sp["hold"],
                    exit_kind=g.get("exit_kind", sp.get("exit_kind", "time")),
                    exit_param=g.get("exit_param", sp.get("exit_param", float(sp["hold"]))),
                    run_hash=rh, hypothesis_semantic_fingerprint=g.get("hypothesis_semantic_fingerprint", rh),
                    mechanism_cluster=rec.get("mechanism_cluster") or g.get("mechanism_cluster"),
                    position_at_regime_end="HOLD_UNTIL_STRATEGY_EXIT")
    g = by_rh.get(rh)
    if g:
        return dict(regime=g["regime"], entry=g["entry"], stop=g["stop"], hold=g["hold"], exit_kind=g["exit_kind"],
                    exit_param=g["exit_param"], run_hash=rh, hypothesis_semantic_fingerprint=g["hypothesis_semantic_fingerprint"],
                    mechanism_cluster=g["mechanism_cluster"], position_at_regime_end="HOLD_UNTIL_STRATEGY_EXIT")
    return None

# resume support
done = {}
if os.path.exists(OUT):
    for r in json.load(open(OUT)): done[r["candidate_id"]] = r
records = list(done.values())
log(f"worklist: {len(reg)} hypotheses; already done {len(done)}")

t0 = time.time(); processed = 0
for idx, rec in enumerate(reg):
    cid = rec.get("candidate_id")
    if cid in done: continue
    spec = spec_of(rec)
    if spec is None:
        records.append(dict(candidate_id=cid, status="RERUN_BLOCKED_UNRESOLVED_SPEC",
                            reason="compact record; run_hash not in grid; not reconstructable without guessing",
                            old_status=rec.get("status"), ts=int(time.time())))
        processed += 1; continue
    try:
        trades_all, _ = gen_signals(ctx, spec)
        # CANONICAL N1/Router eligibility gate: keep a signal only if the hypothesis regime is applicable there
        b = bit.get(spec["regime"], 0)
        elig = (mask_d & b) != 0
        trades = [t for t in trades_all if 0 < t.signal_idx < n - 1 and elig[t.signal_idx]]
        res_base = evaluate(d, trades, BASE_RT)
        res_stress = evaluate(d, trades, STRESS_RT)
        res_gross = evaluate(d, trades, 0.0)
        cl = classify_canonical(res_base, res_stress, res_gross, elig, trades, years, dt)
        hsf = spec["hypothesis_semantic_fingerprint"]
        run_context = dict(RUN_CONTEXT_BASE); run_context["hypothesis_semantic_fingerprint"] = hsf
        rec_out = dict(candidate_id=cid, hypothesis_semantic_fingerprint=hsf, run_hash=hsf,
                       mechanism_cluster=spec.get("mechanism_cluster") or cluster_of(None, spec["regime"], spec["entry"]),
                       regime=spec["regime"], spec={k: spec[k] for k in ("entry", "stop", "hold", "exit_kind", "exit_param")},
                       evaluation_run_hash=evaluation_run_hash(hsf, run_context),
                       old_noncanonical_status=rec.get("status"), old_noncanonical_marked="SUPERSEDED_NONCANONICAL_N1",
                       n_signals_canonical=len(trades), ts=int(time.time()), **cl)
        records.append(rec_out)
    except Exception as e:
        import traceback
        records.append(dict(candidate_id=cid, status="RERUN_ERROR", reason=str(e)[:200], old_status=rec.get("status"), ts=int(time.time())))
        log(f"{cid} ERROR: {str(e)[:160]}")
    processed += 1
    if processed % 25 == 0 or idx == len(reg) - 1:
        tmp = OUT + ".tmp"; json.dump(records, open(tmp, "w"), indent=1, default=float); os.replace(tmp, OUT)
        from collections import Counter
        dist = Counter(r.get("status") for r in records)
        prog = dict(evaluated=len(records), remaining=len(reg) - len([r for r in records]), processed_this_run=processed,
                    elapsed_s=round(time.time() - t0, 1), status_distribution=dict(dist), oos_access=0)
        json.dump(prog, open(PROG, "w"), indent=2)
        log(f"CHECKPOINT {len(records)}/{len(reg)}  dist={dict(dist)}")

# final save
json.dump(records, open(OUT, "w"), indent=1, default=float)
log(f"CANONICAL_RERUN_COMPLETE evaluated={len(records)} in {round(time.time()-t0,1)}s")
