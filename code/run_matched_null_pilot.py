"""Matched-null PILOT on REAL hypotheses (docs/MATCHED_NULL_SPEC §6, §8-pilot). Runs ONLY after synthetic
calibration+power pass. Hypothesis ids are pre-registered (deterministic selection rule) and written BEFORE
any p is computed. Research and validation p reported SEPARATELY. NO strategy verdict. Terminal holdout NEVER
touched. Adaptive MC: B=20k triage on research; refine to 200k only if research p<0.05.
Writes pilot_prereg.json, pilot_real_hypotheses.parquet, pilot_summary.json."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, mstrat as MS, matched_null as MN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "matched_null_validation"); os.makedirs(OUT, exist_ok=True)
BASE_PARQUET = os.path.join(ROOT, "results", "FAMILY_RESULTS.parquet")
B_TRIAGE = 20000; B_REFINE = 200000; B_VAL = 10000; STRATA = ('session', 'atrq')

def select_prereg():
    df = pd.read_parquet(BASE_PARQUET)
    picks = []  # (label, id, rule)
    def top(sub, by, n=1, asc=False):
        return sub.sort_values(by, ascending=asc).head(n)
    for fam in ['S1', 'S5', 'S9']:
        sub = df[(df.fam == fam) & df.research_worthy]
        if len(sub) == 0: sub = df[(df.fam == fam) & df.hist_prof]
        r = top(sub, 'n').iloc[0]; picks.append((f'{fam}_representative', r['id'], f'{fam} research-worthy, largest n'))
    if (df.id == '7a86a38610f8').any():
        picks.append(('S6_extreme', '7a86a38610f8', 'known tiny-stop/outlier extreme (maxDD 89.8R)'))
    else:
        r = top(df[df.fam == 'S6'], 'exp').iloc[0]; picks.append(('S6_extreme', r['id'], 'S6 highest exp'))
    for _, r in df[df.n >= 100].sort_values('exp').head(2).iterrows():
        picks.append((f'unprofitable_{r.fam}', r['id'], 'clearly unprofitable, n>=100, lowest exp'))
    for _, r in df[df.hist_prof & df.fragile & (df.n >= 50)].sort_values('exp', ascending=False).head(2).iterrows():
        picks.append((f'fragile_profitable_{r.fam}', r['id'], 'hist-profitable but fragile, n>=50'))
    used = {p[1] for p in picks}
    for _, r in df[df.research_worthy & ~df.fam.isin(['S1', 'S5', 'S9'])].sort_values('n', ascending=False).iterrows():
        if r['id'] in used: continue
        picks.append((f'research_worthy_{r.fam}', r['id'], 'research-worthy, other family, largest n')); used.add(r['id'])
        if sum(1 for p in picks if p[0].startswith('research_worthy')) >= 2: break
    # dedup preserving order
    seen = set(); out = []
    for lab, hid, rule in picks:
        if hid in seen: continue
        seen.add(hid); out.append(dict(label=lab, id=hid, rule=rule))
    return df, out

def find_h(hid):
    for fam in MS.REGISTRY:
        for h in MS.REGISTRY[fam][0]():
            if h['id'] == hid: return h
    return None

def run():
    df_base, prereg = select_prereg()
    # PRE-REGISTER before any p
    json.dump({'strata': STRATA, 'B_triage': B_TRIAGE, 'B_refine': B_REFINE, 'B_val': B_VAL,
               'selected': prereg, 'note': 'ids fixed before p computation; no verdict issued'},
              open(os.path.join(OUT, 'pilot_prereg.json'), 'w'), indent=1)
    print("PRE-REGISTERED:", json.dumps([p['label']+':'+p['id'] for p in prereg]))

    d = MS.load(); n = len(d); a = int(n*0.6); b = int(n*0.8)
    res = d.iloc[:a].copy(); val = d.iloc[a:b].copy()   # holdout d[b:] SEALED, never loaded into a run
    for seg in (res, val):
        seg['atrq'] = pd.qcut(seg['m_atr'].rank(method='first'), 5, labels=False)
    rows = []; t0 = time.time()
    for p in prereg:
        h = find_h(p['id'])
        if h is None:
            rows.append(dict(**p, error='hypothesis id not found in grammar')); continue
        base = df_base[df_base.id == p['id']].iloc[0]
        su_res = MS.setups(res, h)
        rec_r = MN.matched_null_p(res, su_res, B=B_TRIAGE, seed=0xA11CE, strata=STRATA)
        refined = False
        if rec_r.get('p') is not None and rec_r['p'] < 0.05 and rec_r['k'] >= 25:
            rec_r = MN.matched_null_p(res, su_res, B=B_REFINE, seed=0xA11CE, strata=STRATA); refined = True
        su_val = MS.setups(val, h)
        rec_v = MN.matched_null_p(val, su_val, B=B_VAL, seed=0xB0B, strata=STRATA)
        rows.append(dict(label=p['label'], id=p['id'], family=h['family'], rule=p['rule'],
                         base_n=int(base['n']), base_exp=float(base['exp']), base_pf=float(base['pf']),
                         base_dd=float(base['dd']), base_hist_prof=bool(base['hist_prof']),
                         base_research_worthy=bool(base['research_worthy']), base_fragile=bool(base['fragile']),
                         res_k=rec_r['k'], res_obs_mean=rec_r['obs_mean'], res_p=rec_r.get('p'),
                         res_k_ge=rec_r.get('k_ge'), res_B=rec_r.get('B'), res_ci=rec_r.get('ci'),
                         res_null_mean=rec_r.get('null_mean'), res_refined_200k=refined,
                         val_k=rec_v['k'], val_obs_mean=rec_v['obs_mean'], val_p=rec_v.get('p'),
                         val_B=rec_v.get('B'), val_ci=rec_v.get('ci')))
        pd.DataFrame(rows).to_parquet(os.path.join(OUT, 'pilot_real_hypotheses.parquet'))
        print(f"  [{p['label']}] {p['id']} res_p={rec_r.get('p')} (k={rec_r['k']}, B={rec_r.get('B')}) "
              f"val_p={rec_v.get('p')} elapsed {time.time()-t0:.0f}s", flush=True)
    summ = dict(n_hyps=len(rows), strata=STRATA, B_triage=B_TRIAGE,
                note='NO strategy verdict — engine-validation pilot only; holdout SEALED',
                results=[{k: r.get(k) for k in ('label','id','family','base_exp','res_k','res_obs_mean','res_p','res_ci','val_p')} for r in rows])
    json.dump(summ, open(os.path.join(OUT, 'pilot_summary.json'), 'w'), indent=1, default=str)
    print(json.dumps(summ, indent=1, default=str))

if __name__ == "__main__":
    run()
