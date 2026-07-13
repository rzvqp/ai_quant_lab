"""STRATEGY DEVELOPMENT — candidate registry + deduplication (workstream B, branch strategy-development).
READ-ONLY on the official baseline (commit 1bc0ffb): reads results/FAMILY_RESULTS.parquet and regenerates
the S1-S20 grammars for canonical specs. Does NOT modify mstrat.py / S1-S20 / the screen / any p-engine.
No holdout. No optimization. Groups the 130 Research-Worthy variants by ECONOMIC MECHANISM, dedups tuning
variants, classifies, and writes STRATEGY_CANDIDATE_REGISTRY.parquet + registry_summary.json."""
import sys, os, json, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))
import numpy as np, pandas as pd, mstrat as MS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = ROOT

# Economic-mechanism dimensions per family (direction + reference/mode). All OTHER grammar dims
# (RR/exit, lookback, confirm window, stop variant, imbalance filter, entry type) are TUNING and are
# collapsed by dedup — per CEO: neighbor params / RR / lookback / confirm-window are NOT distinct alpha.
MECH = {
    'S1': ['side', 'liq_ref'],        'S2': ['side', 'ref'],           'S3': ['side', 'ref'],
    # S5 'mode' (breakout/retest) is a DEAD grammar dim — s5_setups never reads it, so both modes produce
    # IDENTICAL trades. Excluded from the mechanism key (would otherwise over-split S5 into phantom twins).
    'S5': ['session', 'side'],        'S6': ['session', 'mode', 'side'],'S8': ['ref', 'side'],
    'S9': ['c4h', 'conf1h'],          'S13': ['fvg', 'mode'],          'S14': ['side'],
    'S16': ['level', 'mode'],         'S17': ['level', 'mode'],        'S18': ['hour', 'side'],
    'S19': ['gap_dir', 'mode'],       'S20': ['ctx', 'trig'],
    # families below have no RW; mechanism keys for completeness
    'S4': ['exp_k'], 'S7': ['htf'], 'S10': ['side'], 'S11': ['htf'], 'S12': ['side', 'target'], 'S15': ['htf'],
}
ECON = MS.ECON

def spec_str(spec):
    order = ['family']
    keys = [k for k in spec if k not in ('id', 'family')]
    return spec['family'] + '{' + ','.join(f"{k}={spec[k]}" for k in sorted(keys)) + '}'

def mech_key(spec):
    fam = spec['family']; dims = MECH.get(fam, [])
    return tuple((k, spec.get(k)) for k in dims)

def mech_label(fam, mk):
    return fam + '/' + '/'.join(f"{k}={v}" for k, v in mk)

def build():
    full = pd.read_parquet(os.path.join(ROOT, "results", "FAMILY_RESULTS.parquet"))
    # id -> spec for every hypothesis in the grammar
    id2spec = {}
    for fam in MS.REGISTRY:
        for h in MS.REGISTRY[fam][0]():
            id2spec[h['id']] = h
    full['mech'] = full['id'].map(lambda i: mech_label(id2spec[i]['family'], mech_key(id2spec[i])) if i in id2spec else None)
    # mechanism-level robustness across the WHOLE family grammar (not just RW):
    # what fraction of ALL variants sharing this mechanism are historically profitable / exp>0
    gm = full.groupby('mech')
    mech_prof_frac = (gm['hist_prof'].mean()).to_dict()
    mech_pos_frac = (gm.apply(lambda s: float((s['exp'] > 0).mean()), include_groups=False)).to_dict()
    mech_count = gm.size().to_dict()

    rw = full[full.research_worthy].copy()
    rows = []
    for (fam, mk), grp in rw.groupby([rw['id'].map(lambda i: id2spec[i]['family']),
                                      rw['id'].map(lambda i: mech_key(id2spec[i]))]):
        lbl = mech_label(fam, mk)
        # representative = least fragile, most temporally stable, most-traded, least top-1 dependent
        g = grp.copy(); g['stab'] = g['pos_months'] / g['months'].clip(lower=1)
        g = g.sort_values(['fragile', 'stab', 'n', 't1'], ascending=[True, False, False, True])
        rep = g.iloc[0]
        cid = 'C_' + hashlib.md5(lbl.encode()).hexdigest()[:8]
        # classification
        stab = rep['pos_months'] / max(rep['months'], 1)
        # neighbor-robustness: fraction of ALL tuning variants sharing this mechanism that are profitable.
        # A knife-edge mechanism (only one narrow param combo works) is fragile, not a research candidate.
        mprof = float(mech_prof_frac.get(lbl, 0.0)); mcount = int(mech_count.get(lbl, 0))
        knife_edge = (mcount >= 4 and mprof < 0.20)
        research_candidate = bool((not rep['fragile']) and rep['t1'] < 0.5 and rep['wo1'] > 0
                                  and rep['years'] >= 2 and rep['months'] >= 6 and stab >= 0.45 and rep['n'] >= 25
                                  and not knife_edge)
        cls = 'B_research_candidate' if research_candidate else 'A_profitable_but_fragile'
        rows.append(dict(
            candidate_id=cid, family_id=fam, mechanism=lbl, economic_mechanism=ECON.get(fam, ''),
            representative_hypothesis_id=rep['id'], canonical_strategy_spec=spec_str(id2spec[rep['id']]),
            n_members_RW=len(grp), member_hypothesis_ids=list(grp['id'].values),
            direction=rep['side'],
            rep_n=int(rep['n']), rep_exp=float(rep['exp']), rep_pf=float(rep['pf']), rep_dd=float(rep['dd']),
            rep_win=float(rep['win']), rep_sumR=float(rep['sumR']), rep_val_exp=(None if pd.isna(rep['val_exp']) else float(rep['val_exp'])),
            rep_median=float(rep['median']), rep_trim5=float(rep['trim5']),
            rep_t1=float(rep['t1']), rep_t3=float(rep['t3']), rep_t5=float(rep['t5']), rep_wo1=float(rep['wo1']),
            rep_months=int(rep['months']), rep_pos_months=int(rep['pos_months']), rep_stability=float(stab),
            rep_years=int(rep['years']), rep_fragile=bool(rep['fragile']),
            mech_grammar_count=int(mech_count.get(lbl, 0)),
            mech_profitable_frac=float(mech_prof_frac.get(lbl, 0.0)),
            mech_posexp_frac=float(mech_pos_frac.get(lbl, 0.0)),
            knife_edge=bool(knife_edge),
            classification=cls))
    reg = pd.DataFrame(rows).sort_values(['family_id', 'rep_stability', 'rep_n'], ascending=[True, False, False])
    # shortlist: research candidates only, capped at 3 per family, ranked by a transparent robustness score
    reg['robustness_score'] = (reg['rep_stability'] + reg['mech_profitable_frac']
                               + np.log10(reg['rep_n']).clip(0) / 3 - reg['rep_t1']
                               - (reg['rep_dd'] / 25).clip(upper=1)
                               + reg['rep_val_exp'].fillna(0).clip(-0.3, 0.3))
    reg['shortlisted'] = False
    B = reg[reg['classification'] == 'B_research_candidate'].sort_values('robustness_score', ascending=False)
    keep = []
    fam_ct = {}
    for _, r in B.iterrows():
        if fam_ct.get(r['family_id'], 0) >= 3:
            continue
        keep.append(r['candidate_id']); fam_ct[r['family_id']] = fam_ct.get(r['family_id'], 0) + 1
    reg.loc[reg['candidate_id'].isin(keep), 'shortlisted'] = True
    reg.to_parquet(os.path.join(OUT, "STRATEGY_CANDIDATE_REGISTRY.parquet"))

    summary = dict(
        rw_total=int(len(rw)), n_distinct_candidates=int(len(reg)),
        duplicates_collapsed=int(len(rw) - len(reg)),
        per_family_rw=rw.assign(fam=rw['id'].map(lambda i: id2spec[i]['family'])).groupby('fam').size().to_dict(),
        per_family_distinct=reg.groupby('family_id').size().to_dict(),
        classification_counts=reg['classification'].value_counts().to_dict(),
        n_shortlisted=int(reg['shortlisted'].sum()),
        shortlist=[{k: r[k] for k in ('candidate_id', 'family_id', 'mechanism', 'representative_hypothesis_id',
                    'rep_n', 'rep_exp', 'rep_pf', 'rep_dd', 'rep_stability', 'rep_val_exp',
                    'mech_profitable_frac', 'robustness_score')}
                   for _, r in reg[reg['shortlisted']].sort_values('robustness_score', ascending=False).iterrows()],
        candidates=[{k: r[k] for k in ('candidate_id', 'family_id', 'mechanism', 'representative_hypothesis_id',
                     'n_members_RW', 'rep_n', 'rep_exp', 'rep_pf', 'rep_dd', 'rep_stability', 'rep_t1',
                     'rep_val_exp', 'mech_profitable_frac', 'mech_grammar_count', 'classification')}
                    for _, r in reg.iterrows()])
    json.dump(summary, open(os.path.join(OUT, "registry_summary.json"), "w"), indent=1, default=str)
    print(json.dumps(summary, indent=1, default=str))

if __name__ == "__main__":
    build()
