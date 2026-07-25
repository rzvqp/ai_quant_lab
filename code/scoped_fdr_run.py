"""SCOPED GLOBAL-FDR on the pre-registered ATR-stop subset (docs/SCOPED_FDR_PREREGISTRATION_v1.0.md).
Runs AFTER the pre-registration commit. Uses the validated matched_null internals exactly; adds
sequential never-BH-rejected stopping (p>0.05) at MC-1. Research primary; validation separate.
NO threshold tuning, NO universe change. Holdout never loaded."""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "matched_null_validation")
ENUM = json.load(open(os.path.join(OUT, "subset_prereg_enumeration.json")))
VALID_IDS = sorted(set(ENUM["atr_subset_valid_ids"]))
M = len(VALID_IDS)
ALPHA = 0.05
BH1 = ALPHA / M                       # rank-1 BH threshold
B_MC1 = 20000; B_MC2 = 200000; B_MC3 = 1000000; B_VAL = 10000
SEED_RES = 0xA11CE; SEED_VAL = 0xB0B
KGE_STOP = 1000                       # k_ge>=1000 => p>=1001/20001>0.05 => never BH-rejected

# ---- per-worker globals ----
_G = {}
def _init():
    import mstrat as MS
    from matched_null import observed_profile, eligibility_pool, _strata_key, _null_mean
    d = MS.load(); n = len(d); a = int(n*0.6); b = int(n*0.8)
    res = d.iloc[:a].copy(); val = d.iloc[a:b].copy()   # holdout d[b:] never loaded into a run
    idmap = {}
    for fam in MS.REGISTRY:
        for h in MS.REGISTRY[fam][0]():
            idmap[h['id']] = h
    _G.update(MS=MS, op=observed_profile, epool=eligibility_pool, nmean=_null_mean,
              res=res, val=val, idmap=idmap,
              pool_res=eligibility_pool(res, None))

def _seq_null_p(d, prof, pool, B, seed, kge_stop=None):
    """Replicates matched_null_p's null loop exactly (same rng seq), with optional early stop."""
    nmean = _G['nmean']; cfg = _G['MS'].CFG; obs = prof['mean']
    rng = np.random.default_rng(seed)
    k_ge = 0; Beff = 0; used = 0; stopped = False
    for _ in range(B):
        m = nmean(d, prof, pool, None, rng, cfg)   # exact cfg=MS.CFG, same as matched_null_p
        used += 1
        if np.isfinite(m):
            Beff += 1
            if m >= obs: k_ge += 1
        if kge_stop is not None and k_ge >= kge_stop:
            stopped = True; break
    p = (k_ge + 1) / (Beff + 1) if Beff > 0 else 1.0
    z = 1.959963985
    if Beff > 0:
        phat = k_ge / Beff; den = 1 + z*z/Beff
        c = (phat + z*z/(2*Beff))/den; hw = (z*np.sqrt(phat*(1-phat)/Beff + z*z/(4*Beff*Beff)))/den
        ci = (max(0.0, c-hw), min(1.0, c+hw))
    else:
        ci = (0.0, 1.0)
    return dict(p=float(p), k_ge=int(k_ge), Beff=int(Beff), used=int(used), stopped=bool(stopped), ci=[float(ci[0]), float(ci[1])])

def _mc1(hid):
    MS = _G['MS']; h = _G['idmap'][hid]; res = _G['res']
    su = _G['MS'].setups(res, h)
    prof = _G['op'](res, su)
    k = prof['k']
    if k < 25 or not np.isfinite(prof['mean']):
        return dict(id=hid, family=h['family'], k=int(k), obs_mean=float(prof['mean']) if np.isfinite(prof['mean']) else None,
                    p=1.0, k_ge=None, Beff=0, used=0, stopped=False, ci=[0.0,1.0], note='k<25 or non-finite')
    r = _seq_null_p(res, prof, _G['pool_res'], B_MC1, SEED_RES, kge_stop=KGE_STOP)
    r.update(id=hid, family=h['family'], k=int(k), obs_mean=float(prof['mean']))
    return r

def _escalate(hid, B):
    MS = _G['MS']; h = _G['idmap'][hid]; res = _G['res']
    su = _G['MS'].setups(res, h); prof = _G['op'](res, su)
    r = _seq_null_p(res, prof, _G['pool_res'], B, SEED_RES, kge_stop=None)  # full B, no early stop
    r.update(id=hid, family=h['family'], k=int(prof['k']), obs_mean=float(prof['mean']), B=B)
    return r

def _val(hid):
    MS = _G['MS']; h = _G['idmap'][hid]; val = _G['val']
    su = _G['MS'].setups(val, h); prof = _G['op'](val, su)
    if prof['k'] < 25 or not np.isfinite(prof['mean']):
        return dict(id=hid, val_k=int(prof['k']), val_p=None, note='val k<25')
    pool = _G['epool'](val, None)
    r = _seq_null_p(val, prof, pool, B_VAL, SEED_VAL, kge_stop=None)
    return dict(id=hid, val_k=int(prof['k']), val_obs_mean=float(prof['mean']), val_p=r['p'], val_ci=r['ci'], val_Beff=r['Beff'])

def bh_reject(pvals_by_id):
    """Benjamini-Hochberg step-up at ALPHA over M. Returns set of rejected ids + the cutoff."""
    items = sorted(pvals_by_id.items(), key=lambda kv: kv[1])
    kstar = 0; cutoff_p = 0.0
    for i, (hid, p) in enumerate(items, start=1):
        if p <= i*ALPHA/M:
            kstar = i; cutoff_p = i*ALPHA/M
    rejected = set(hid for hid,_ in items[:kstar])
    return rejected, kstar, cutoff_p

def main():
    t0 = time.time()
    log = open(os.path.join(OUT, "scoped_fdr_run.log"), "w")
    def lg(*a):
        s = " ".join(str(x) for x in a); print(s, flush=True); log.write(s+"\n"); log.flush()
    lg(f"[scoped-FDR] M={M} BH1={BH1:.3e} B_MC1={B_MC1} KGE_STOP={KGE_STOP} workers=10")
    recs = {}
    with ProcessPoolExecutor(max_workers=10, initializer=_init) as ex:
        futs = {ex.submit(_mc1, hid): hid for hid in VALID_IDS}
        done = 0
        for fut in as_completed(futs):
            r = fut.result(); recs[r['id']] = r; done += 1
            if done % 40 == 0:
                lg(f"  MC-1 {done}/{M} elapsed {time.time()-t0:.0f}s")
    lg(f"MC-1 complete in {time.time()-t0:.0f}s")
    # research BH over MC-1 p's
    pmc1 = {hid: recs[hid]['p'] for hid in VALID_IDS}
    rejected, kstar, cutoff = bh_reject(pmc1)
    # sort for reporting
    order = sorted(pmc1.items(), key=lambda kv: kv[1])
    lg(f"MC-1 BH: kstar={kstar} rejected={len(rejected)} cutoff_p={cutoff:.3e}")
    lg("smallest 10 MC-1 research p:")
    for hid, p in order[:10]:
        rc = recs[hid]; lg(f"  {hid} {rc['family']} k={rc['k']} obs={rc['obs_mean']:.4f} p={p:.3e} k_ge={rc['k_ge']} used={rc['used']} stopped={rc['stopped']} ci={rc['ci']}")
    # escalation: any hyp not eliminated whose MC-1 p or CI is near/below the most permissive relevant threshold
    # trigger = MC-1 p <= 10*BH1 OR CI lower <= BH1 (generous net; usually empty)
    esc_ids = [hid for hid in VALID_IDS if (recs[hid]['p'] <= 10*BH1) or (recs[hid]['ci'][0] <= BH1)]
    lg(f"escalation candidates (MC-2/MC-3): {len(esc_ids)} -> {esc_ids[:20]}")
    mc23 = {}
    if esc_ids:
        with ProcessPoolExecutor(max_workers=min(10,len(esc_ids)), initializer=_init) as ex:
            for fut in as_completed({ex.submit(_escalate, hid, B_MC2): hid for hid in esc_ids}):
                r = fut.result(); mc23[r['id']] = {'mc2': r}; lg(f"  MC-2 {r['id']} p={r['p']:.3e} ci={r['ci']} k_ge={r['k_ge']}")
        # MC-3 for those still <= 10*BH1 after MC-2
        mc3_ids = [hid for hid in esc_ids if mc23[hid]['mc2']['p'] <= 10*BH1]
        if mc3_ids:
            with ProcessPoolExecutor(max_workers=min(10,len(mc3_ids)), initializer=_init) as ex:
                for fut in as_completed({ex.submit(_escalate, hid, B_MC3): hid for hid in mc3_ids}):
                    r = fut.result(); mc23[r['id']]['mc3'] = r; lg(f"  MC-3 {r['id']} p={r['p']:.3e} ci={r['ci']}")
    # final research p per escalated hyp = deepest MC available
    final_p = {}
    for hid in VALID_IDS:
        if hid in mc23 and 'mc3' in mc23[hid]: final_p[hid] = mc23[hid]['mc3']['p']
        elif hid in mc23: final_p[hid] = mc23[hid]['mc2']['p']
        else: final_p[hid] = recs[hid]['p']
    rej_final, kstar_f, cutoff_f = bh_reject(final_p)
    # UNRESOLVED: escalated hyp whose deepest CI straddles its BH threshold
    unresolved = []
    for hid in esc_ids:
        deepest = mc23[hid].get('mc3') or mc23[hid].get('mc2')
        rank = [i for i,(h,_) in enumerate(sorted(final_p.items(), key=lambda kv: kv[1]), start=1) if h==hid][0]
        thr = rank*ALPHA/M
        if deepest['ci'][0] <= thr <= deepest['ci'][1]:
            unresolved.append(dict(id=hid, thr=thr, ci=deepest['ci'], p=deepest['p']))
    survivors = sorted(rej_final)
    lg(f"FINAL research BH: kstar={kstar_f} survivors={len(survivors)} unresolved={len(unresolved)}")
    # validation ONLY for research survivors (reported separately, never combined)
    val_out = {}
    if survivors:
        with ProcessPoolExecutor(max_workers=min(10,len(survivors)), initializer=_init) as ex:
            for fut in as_completed({ex.submit(_val, hid): hid for hid in survivors}):
                r = fut.result(); val_out[r['id']] = r; lg(f"  VAL {r['id']} val_p={r.get('val_p')}")
    # write outputs
    df = pd.DataFrame([recs[h] for h in VALID_IDS])
    df['final_p'] = df['id'].map(final_p)
    df.to_parquet(os.path.join(OUT, "scoped_fdr_research.parquet"))
    best_id, best_p = order[0]
    summary = dict(
        m=M, alpha=ALPHA, bh_rank1_threshold=BH1, config="unstratified + ATR-scaled",
        segment="research (60%)", B_MC1=B_MC1, kge_stop=KGE_STOP, seed_research=SEED_RES,
        excluded_total=int(ENUM['total']-M),
        excluded_breakdown=dict(structural_level=int(ENUM['regime_counts'].get('structural_excluded',0)),
                                ema_ambiguous=int(ENUM['regime_counts'].get('ambiguous_excluded',0)),
                                atr_but_n_lt_25=int(ENUM['regime_counts'].get('atr_indomain',0)-M)),
        tested=M,
        best_research=dict(id=best_id, family=recs[best_id]['family'], p=best_p,
                           k=recs[best_id]['k'], obs_mean=recs[best_id]['obs_mean'],
                           k_ge=recs[best_id]['k_ge'], used=recs[best_id]['used']),
        smallest10=[dict(id=h, family=recs[h]['family'], p=p, k=recs[h]['k'], obs_mean=recs[h]['obs_mean']) for h,p in order[:10]],
        bh_kstar=kstar_f, bh_cutoff_p=cutoff_f, survivors=survivors, n_survivors=len(survivors),
        unresolved=unresolved, n_unresolved=len(unresolved),
        escalated=esc_ids, validation=val_out,
        elapsed_sec=round(time.time()-t0,1),
        VERDICT=("ZERO SURVIVORS" if not survivors and not unresolved else
                 ("UNRESOLVED" if unresolved and not survivors else f"{len(survivors)} SURVIVOR(S)")),
    )
    json.dump(summary, open(os.path.join(OUT, "scoped_fdr_summary.json"), "w"), indent=1, default=str)
    json.dump(dict(seed_research=SEED_RES, seed_validation=SEED_VAL, B_MC1=B_MC1, B_MC2=B_MC2,
                   B_MC3=B_MC3, B_VAL=B_VAL, kge_stop=KGE_STOP, m=M, ids=VALID_IDS),
              open(os.path.join(OUT, "scoped_fdr_seeds.json"), "w"), indent=1)
    lg("VERDICT:", summary['VERDICT'], f"(best research p={best_p:.3e} vs BH1={BH1:.3e}) elapsed {summary['elapsed_sec']}s")
    lg("wrote scoped_fdr_{research.parquet,summary.json,seeds.json}")

if __name__ == "__main__":
    main()
