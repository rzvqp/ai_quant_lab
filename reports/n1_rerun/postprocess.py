"""Post-process the canonical rerun: NET verdict distribution, BASE/STRESS/MDE eliminations,
cluster ranking + shortlist (<=5 distinct mechanisms, >=2 surviving variants), diffs vs old gross."""
import json, os, sys
from collections import Counter, defaultdict

SP = os.path.dirname(os.path.abspath(__file__))
recs = json.load(open(os.path.join(SP, "canonical_rerun_records.json")))
ALPHA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
old_reg = json.load(open(os.path.join(ALPHA, "edge_research/loop_state/hypothesis_registry.json")))
old_status = {r.get("candidate_id"): r.get("status") for r in old_reg}

SURVIVORS = {"CANONICAL_PROVISIONAL_SURVIVOR", "RECENT_REGIME_NET_PROVISIONAL"}

def rp(r, key="RECENT_PRIMARY_BASE"):
    return (r.get(key) or {})

# ── NET verdict distribution ──────────────────────────────────────────────────────────────────────
dist = Counter(r.get("status") for r in recs)
stress_flip = 0
for r in recs:
    if r.get("status") in SURVIVORS and r.get("stress_status") not in SURVIVORS:
        stress_flip += 1

# BASE/STRESS/MDE eliminations
elim = dict(
    NET_STRUCTURALLY_NEGATIVE_GROSS=dist.get("NET_STRUCTURALLY_NEGATIVE_GROSS", 0),
    COST_BASE_FALSIFIED=dist.get("COST_BASE_FALSIFIED", 0),
    ARCHIVE_INSUFFICIENT_incl_low_power=dist.get("ARCHIVE_INSUFFICIENT", 0),
    NET_FAT_TAIL_DEPENDENT=dist.get("NET_FAT_TAIL_DEPENDENT", 0),
    RERUN_BLOCKED_UNRESOLVED_SPEC=dist.get("RERUN_BLOCKED_UNRESOLVED_SPEC", 0),
    RERUN_ERROR=dist.get("RERUN_ERROR", 0),
    survive_BASE=sum(dist.get(s, 0) for s in SURVIVORS),
    survive_BASE_but_die_STRESS=stress_flip,
)

# ── cluster ranking ───────────────────────────────────────────────────────────────────────────────
clusters = defaultdict(list)
for r in recs:
    mc = r.get("mechanism_cluster")
    if mc: clusters[mc].append(r)
cluster_rank = []
for mc, variants in clusters.items():
    surv = [v for v in variants if v.get("status") in SURVIVORS and rp(v).get("trimmed_avg_R") is not None]
    if not surv: continue
    surv.sort(key=lambda v: rp(v)["trimmed_avg_R"], reverse=True)
    rep = surv[0]
    cluster_rank.append(dict(mechanism_id=mc, n_variants=len(variants), n_surviving=len(surv),
                             surviving_frac=round(len(surv)/len(variants), 2), representative=rep["candidate_id"],
                             rep_recent_trimmed_BASE=rp(rep).get("trimmed_avg_R"),
                             rep_recent_EV_BASE=rp(rep).get("EV_net_avg_R"),
                             rep_recent_EV_STRESS=(rep.get("RECENT_PRIMARY_STRESS") or {}).get("EV_net_avg_R"),
                             rep_walk_forward=rp(rep).get("walk_forward_folds"),
                             rep_max_dd=rp(rep).get("max_drawdown_R"),
                             rep_best_episode_share=rp(rep).get("best_episode_share"),
                             rep_mde_BASE=rep.get("mde_BASE"),
                             rep_hist_transfer_BASE=(rep.get("HISTORICAL_TRANSFER_BASE") or {}).get("EV_net_avg_R")))
cluster_rank.sort(key=lambda c: c["rep_recent_trimmed_BASE"], reverse=True)
# shortlist: >=2 surviving variants (robust mechanism), <=5 distinct
shortlist = [c for c in cluster_rank if c["n_surviving"] >= 2][:5]

# ── diff vs old gross/noncanonical ────────────────────────────────────────────────────────────────
cross = Counter()
for r in recs:
    o = old_status.get(r.get("candidate_id"), "UNKNOWN"); nnew = r.get("status")
    cross[(o, nnew)] += 1
# summarize: old survivors that no longer survive
old_surv = {"GROSS_EPISODE_SURVIVOR_AWAITING_COST", "RECENT_GROSS_SIGNAL_AWAITING_COST"}
old_surv_ids = [r["candidate_id"] for r in recs if old_status.get(r["candidate_id"]) in old_surv]
old_surv_still = [cid for cid in old_surv_ids if next(x for x in recs if x["candidate_id"] == cid).get("status") in SURVIVORS]

out = dict(
    total=len(recs),
    net_verdict_distribution=dict(dist),
    eliminations=elim,
    shortlist=shortlist,
    cluster_rank_full=cluster_rank,
    diff_vs_old_gross=dict(
        old_gross_survivors=len(old_surv_ids),
        old_gross_survivors_still_canonical=len(old_surv_still),
        old_gross_survivors_lost=len(old_surv_ids) - len(old_surv_still),
        crosstab_old_to_new={f"{o} -> {n}": c for (o, n), c in sorted(cross.items(), key=lambda kv: -kv[1])},
    ),
)
json.dump(out, open(os.path.join(SP, "canonical_rerun_summary.json"), "w"), indent=2, default=float)
print(json.dumps({k: out[k] for k in ("total", "net_verdict_distribution", "eliminations")}, indent=2, default=float))
print("\nSHORTLIST (<=5 distinct mechanisms, >=2 surviving variants):")
for c in shortlist:
    print(f"  {c['mechanism_id']:28s} rep={c['representative']:12s} trimBASE={c['rep_recent_trimmed_BASE']} "
          f"EV_BASE={c['rep_recent_EV_BASE']} EV_STRESS={c['rep_recent_EV_STRESS']} surv={c['n_surviving']}/{c['n_variants']}")
print("\nDIFF vs old gross:", json.dumps(out["diff_vs_old_gross"], indent=1, default=float))
