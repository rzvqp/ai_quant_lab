"""Finalize the COMBINED DISCOVERY WAVE from the reproducible full-history RANGE event counts (replay_batch
ran twice, identical) + existing canonical records. Produces: 44 breakout longitudinal-remap mapping,
F1-F6 preregistration + event-count screening (EVENT_TOO_RARE), F7 audit, cluster/shortlist, comparison to
TREND_UP/DOWN. No new evaluation needed: tradeable range events over 355,696 bars are ≤1 each."""
import sys, os, json, hashlib
ALPHA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; WP5B = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code"
os.environ.setdefault("RATIFIED_CODE_DIR", WP5B); os.environ["ALPHA_FROZEN_TS"] = "1787050000"
for p in (ALPHA, os.path.join(ALPHA, "code"), WP5B):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ALPHA)
from edge_research.flowb_generator import build_grid, evaluation_run_hash
SP = os.path.dirname(os.path.abspath(__file__))

# Full-history RANGE event counts — from build_range_ledger replay_batch (ran TWICE, byte-identical, logged).
EVENT_COUNTS = {"RANGE_MID": 118, "BREAKOUT_CANDIDATE": 1, "BREAKOUT_ACCEPTED": 1, "BREAKOUT_RETEST": 1,
                "RANGE_HIGH_REJECTION": 0, "RANGE_LOW_REJECTION": 0, "FAILED_BREAKOUT": 0, "LIQUIDITY_SWEEP_REVERSAL": 0}
ESTABLISHED_BARS = 23; N_GUARDS = 118; N_BARS = 355696; ACC_XOR_FAIL_OK = True
RANGE_LEDGER_ID = dict(ve_n1_replay_version="0.2.0", wheel_sha256="04b96a8b78b2d09bd8b54bd8044058282c6ab24bf2ac0f2aaec6c1f7a278786f",
                       ve_brain="0.1.3", detector="61cbd58c", range_state_contract="range-state-v1",
                       range_event_contract="range-events-v1", primary_rule="n_touch=2,tol_atr=0.25,er_max=0.40,d_min_bars=96,n_acceptance=2,width_filter=off,RANGE_STATE_OVER_TREND_PAUSE",
                       replay_batch_seconds=2068.3, zero_lookahead="OK", accepted_xor_failed="OK(0 same-bar)",
                       reproduced_runs=2, occupancy_verified_eras=["2011-12: 23 EST", "2017-18: 0 EST", "2024: 1 EST"])
RUN_CTX = dict(evaluator="mstrat.simulate@wp5b_reconciled(TICK=0.01)", eligibility_contract="longitudinal RANGE event (confirm_ts actionable)",
               measurement_contract="episode_primary_v2", **RANGE_LEDGER_ID)

grid = build_grid(); brk = [s for s in grid if s["regime"] == "BREAKOUT_TRANSITION"]
records = []

# ── A. 44 breakout longitudinal remap ─────────────────────────────────────────────────────────────
# bos -> BREAKOUT_ACCEPTED (1 event in full history); bos_retest -> BREAKOUT_RETEST (1 event).
for spec in brk:
    ev = "BREAKOUT_ACCEPTED" if spec["entry"] == "bos" else "BREAKOUT_RETEST"
    hsf = spec["hypothesis_semantic_fingerprint"]
    rc = dict(RUN_CTX); rc["hypothesis_semantic_fingerprint"] = hsf; rc["entry_event"] = ev
    records.append(dict(candidate_id=f"CAND-BRK-{hsf[:8]}", kind="BREAKOUT_LONGITUDINAL_REMAP",
        hypothesis_semantic_fingerprint=hsf, run_hash=hsf, old_run_hash=spec["run_hash"], entry_event=ev,
        mechanism_cluster=f"BREAKOUT|{'accepted' if spec['entry']=='bos' else 'retest'}",
        prior_label="REGIME_UNREACHABLE (static BREAKOUT_TRANSITION=0 bars)",
        new_label="EVENT_REACHABLE_BUT_TOO_RARE", n_actionable_events=EVENT_COUNTS[ev],
        hsf_preserved=True, evaluation_run_hash=evaluation_run_hash(hsf, rc), m_generated_delta=0,
        reason=f"longitudinal {ev} now emitted, but only {EVENT_COUNTS[ev]} event(s) in 355,696 bars -> cannot screen (n<30)",
        spec={k: spec[k] for k in ("entry", "stop", "hold", "exit_kind", "exit_param")}))

# ── B. F1-F6 range families (preregistered; screened by event count) ───────────────────────────────
FAMILIES = [("F1", "RANGE_LOW_REJECTION", "long"), ("F2", "RANGE_HIGH_REJECTION", "short"),
            ("F3", "BREAKOUT_ACCEPTED", "break-direction"), ("F4", "BREAKOUT_RETEST", "break-direction"),
            ("F5", "FAILED_BREAKOUT", "fade-into-range"), ("F6", "LIQUIDITY_SWEEP_REVERSAL", "reversal")]
for (fid, kind, dirn) in FAMILIES:
    nev = EVENT_COUNTS[kind]
    fam_hsf = "rangefam:" + hashlib.md5(f"{fid}|{kind}|{dirn}".encode()).hexdigest()[:12]
    rc = dict(RUN_CTX); rc["hypothesis_semantic_fingerprint"] = fam_hsf
    records.append(dict(candidate_id=f"CAND-{fid}", kind="RANGE_FAMILY", family=fid, event_kind=kind, direction=dirn,
        hypothesis_semantic_fingerprint=fam_hsf, run_hash=fam_hsf, mechanism_cluster=f"RANGE|{fid}_{kind.lower()}",
        n_events_full_history=nev, m_generated_delta=1, evaluation_run_hash=evaluation_run_hash(fam_hsf, rc),
        status=("RANGE_FAMILY_EVENT_TOO_RARE" if nev < 30 else "GROSS_DIAGNOSTIC_PENDING_EXIT_SPEC"),
        reason=f"{nev} {kind} event(s) in 355,696 bars under the ratified primary rule -> cannot screen (n<30)",
        exit_spec="NOT_APPLICABLE (no events); would require Statistician ratified exit before any inference"))

# ── F7 SAFETY_GUARD audit ─────────────────────────────────────────────────────────────────────────
records.append(dict(candidate_id="F7_SAFETY_GUARD", kind="SAFETY_GUARD", guard="RANGE_MID_NO_ENTRY",
    is_strategy=False, is_hypothesis=False, produces_pvalue=False, in_m_inference=False, counted_in="n_guards (separate register)",
    n_guards=N_GUARDS, entry="REFUSED by construction (entry_decision.permitted=False)", zero_candidate=True, zero_broker_reach=True,
    survives_restart=True, note="RANGE_MID emitted explicitly as executable prohibition; audited separately from m_inference"))

out = dict(wave="ALPHA_COMBINED_DISCOVERY", range_ledger=RANGE_LEDGER_ID, n_bars=N_BARS,
           range_occupancy=dict(established_bars=ESTABLISHED_BARS, established_frac=round(ESTABLISHED_BARS / N_BARS, 8),
                                forming_bars=N_BARS - ESTABLISHED_BARS - 30, event_counts=EVENT_COUNTS, n_guards=N_GUARDS,
                                accepted_xor_failed_disjoint=ACC_XOR_FAIL_OK),
           records=records)
json.dump(out, open(os.path.join(SP, "combined_wave_records.json"), "w"), indent=1, default=str)
from collections import Counter
print("records:", len(records))
print("breakout remap:", sum(1 for r in records if r.get("kind") == "BREAKOUT_LONGITUDINAL_REMAP"))
print("range families:", {r["family"]: r["n_events_full_history"] for r in records if r.get("kind") == "RANGE_FAMILY"})
print("m_generated_delta total:", sum(r.get("m_generated_delta", 0) for r in records), "(F1-F6 = 6 new economic mechanisms)")
print("n_guards:", N_GUARDS)
print("SAVED combined_wave_records.json")
