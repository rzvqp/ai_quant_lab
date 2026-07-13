"""LAB KNOWLEDGE SYSTEM builder (branch family-implementation-s21-s40). READ-ONLY on the engine/strategies:
reads results parquets, reconstructs specs from the frozen grammars, and re-runs MS.simulate (read-only) on
the DISTINCT candidates only, to recover missing fields (yearly, risk/ATR, monthly streams). Does NOT modify
mstrat.py / mstrat_ext.py / S1-S40 / screen / holdout. Produces STRATEGY_REGISTRY.parquet + JSON intermediates
consumed by the .md reports. Authoritative counts: S1-S40 = 2300 hyps / 375 profitable / 139 RW."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import mstrat as MS, mstrat_ext as EXT
from alpha_lab import CFG
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = ROOT

# economic-mechanism keys per family (direction + reference/mode); tuning dims collapsed
MECH = {
 'S1': ['side', 'liq_ref'], 'S2': ['side', 'ref'], 'S3': ['side', 'ref'], 'S4': ['exp_k'],
 'S5': ['session', 'side'], 'S6': ['session', 'mode', 'side'], 'S7': ['htf'], 'S8': ['ref', 'side'],
 'S9': ['c4h', 'conf1h'], 'S10': ['side'], 'S11': ['htf'], 'S12': ['side', 'target'], 'S13': ['fvg', 'mode'],
 'S14': ['side'], 'S15': ['htf'], 'S16': ['level', 'mode'], 'S17': ['level', 'mode'], 'S18': ['hour', 'side'],
 'S19': ['gap_dir', 'mode'], 'S20': ['ctx', 'trig'],
 'S21': ['side'], 'S22': ['mode'], 'S23': ['htf'], 'S24': ['sess', 'mode'], 'S25': ['mode'],
 'S26': ['mode'], 'S27': ['htf'], 'S28': ['anchor', 'mode'], 'S29': ['dow', 'side'], 'S30': ['zone', 'mode'],
 'S31': ['window', 'side'], 'S38': ['zone'], 'S39': ['er_thr'], 'S40': ['er_thr'],
}
# mechanism CLASS + causal tag per family (economic hypothesis)
ECON_ALL = dict(MS.ECON); ECON_ALL.update(EXT.EXT_ECON)

def build_specs():
    id2spec = {}; id2reg = {}
    for fam in MS.REGISTRY:
        for h in MS.REGISTRY[fam][0]():
            id2spec[h['id']] = h; id2reg[h['id']] = 'S1-S20'
    for fam in EXT.EXT_REGISTRY:
        for h in EXT.EXT_REGISTRY[fam][0]():
            id2spec[h['id']] = h; id2reg[h['id']] = 'S21-S40'
    return id2spec, id2reg

def mech_key(spec):
    fam = spec['family']; dims = MECH.get(fam, [])
    return tuple((k, spec.get(k)) for k in dims)

def mech_label(fam, mk):
    return fam + ('/' + '/'.join(f"{k}={v}" for k, v in mk) if mk else '')

def find_setups(spec, d):
    fam = spec['family']
    if fam in MS.REGISTRY:
        return MS.REGISTRY[fam][1](d, spec)
    return EXT.EXT_REGISTRY[fam][1](d, spec)

def load_all():
    s = pd.read_parquet(os.path.join(ROOT, 'results', 'FAMILY_RESULTS.parquet'))
    e = pd.read_parquet(os.path.join(ROOT, 'results', 'ext_families', 'EXT_FAMILY_RESULTS.parquet'))
    return pd.concat([s, e], ignore_index=True)

def status_of(r):
    if r['research_worthy']:
        return 'RESEARCH WORTHY'
    if r['hist_prof'] and r['fragile']:
        return 'FRAGILE'
    if r['hist_prof']:
        return 'HISTORICALLY PROFITABLE'
    return 'NEGATIVE'

def main():
    id2spec, id2reg = build_specs()
    alld = load_all()
    alld = alld[alld['id'].isin(id2spec)].copy()
    alld['family'] = alld['id'].map(lambda i: id2spec[i]['family'])
    alld['engine'] = alld['id'].map(id2reg)
    alld['mechanism'] = alld['id'].map(lambda i: mech_label(id2spec[i]['family'], mech_key(id2spec[i])))
    alld['economic_mechanism'] = alld['family'].map(ECON_ALL)
    alld['status'] = alld.apply(status_of, axis=1)
    alld['strict_validation'] = 'STRICT VALIDATION PENDING'
    # STRATEGY_REGISTRY = every hist-profitable OR research-worthy hypothesis
    reg = alld[alld['hist_prof'] | alld['research_worthy']].copy()
    reg['canonical_spec'] = reg['id'].map(lambda i: MS._grid.__self__ if False else None)  # placeholder
    reg['canonical_spec'] = reg['id'].map(lambda i: str({k: v for k, v in id2spec[i].items() if k not in ('id',)}))
    keep_cols = ['id', 'family', 'engine', 'mechanism', 'economic_mechanism', 'canonical_spec', 'side',
                 'n', 'exp', 'pf', 'dd', 'win', 'sumR', 'val_exp', 'median', 'trim5', 't1', 't3', 't5', 'wo1',
                 'months', 'pos_months', 'years', 'hist_prof', 'research_worthy', 'fragile', 'status', 'strict_validation']
    reg[keep_cols].rename(columns={'id': 'hypothesis_id'}).to_parquet(os.path.join(OUT, 'STRATEGY_REGISTRY.parquet'))

    # ---- DEDUP: cluster the RESEARCH-WORTHY by (family, mechanism_key) ----
    rw = alld[alld['research_worthy']].copy()
    clusters = []
    for (fam, mk), grp in rw.groupby([rw['id'].map(lambda i: id2spec[i]['family']),
                                      rw['id'].map(lambda i: mech_key(id2spec[i]))]):
        lbl = mech_label(fam, mk)
        g = grp.copy(); g['stab'] = g['pos_months'] / g['months'].clip(lower=1)
        # representative: robustness rank (per Codex: not expectancy) — non-fragile, stable, low-t1, +OOS, more n
        g['rob'] = (g['stab'] + g['val_exp'].fillna(0).clip(-0.3, 0.3) + np.log10(g['n']).clip(0) / 3
                    - g['t1'] - (g['dd'] / 25).clip(upper=1) - g['fragile'].astype(float) * 0.5)
        g = g.sort_values('rob', ascending=False); rep = g.iloc[0]
        clusters.append(dict(cluster_id='K_' + lbl.replace('/', '_'), family=fam, mechanism=lbl,
                             n_members=len(grp), member_ids=list(grp['id'].values),
                             representative_id=rep['id'], rep_n=int(rep['n']), rep_exp=float(rep['exp']),
                             rep_pf=float(rep['pf']), rep_dd=float(rep['dd']), rep_win=float(rep['win']),
                             rep_val=(None if pd.isna(rep['val_exp']) else float(rep['val_exp'])),
                             rep_t1=float(rep['t1']), rep_stab=float(rep['pos_months'] / max(rep['months'], 1)),
                             rep_years=int(rep['years']), rep_side=rep['side'], rep_fragile=bool(rep['fragile'])))
    dedup = pd.DataFrame(clusters)

    # ---- re-backtest each representative (READ-ONLY) for yearly + risk/ATR + monthly stream ----
    d = MS.load(); n = len(d); a = int(n * 0.6); b = int(n * 0.8)
    res = d.iloc[:a].copy(); val = d.iloc[a:b].copy(); rt = res['time'].values
    o_res = res['open'].values; atr_res = res['m_atr'].values
    monthly = {}; extra = {}
    for _, c in dedup.iterrows():
        spec = id2spec[c['representative_id']]
        su = find_setups(spec, res); tr = MS.simulate(res, su, CFG)
        R = tr['R'].values; ei = tr['ei'].astype(int).values
        by_ei = {s['ei']: s for s in su}
        risks = np.array([abs(o_res[e] - by_ei[e]['stop']) for e in ei]) if len(ei) else np.array([])
        ratr = (risks / atr_res[[by_ei[e]['si'] for e in ei]]) if len(ei) else np.array([])
        ratr = ratr[np.isfinite(ratr)]
        ts = pd.to_datetime(rt[ei], unit='s', utc=True)
        yr = {int(Y): round(float(R[ts.year.values == Y].mean()), 3) for Y in sorted(set(ts.year.values))} if len(R) else {}
        mon = pd.Series(R, index=ts).groupby(pd.Grouper(freq='ME')).sum(); mon.index = mon.index.astype(str)
        monthly[c['cluster_id']] = mon
        sv = find_setups(spec, val); mv = MS.simulate(val, sv, CFG)['R'].values
        long_R = R[np.array([by_ei[e]['dir'] for e in ei]) > 0] if len(ei) else np.array([])
        short_R = R[np.array([by_ei[e]['dir'] for e in ei]) < 0] if len(ei) else np.array([])
        extra[c['cluster_id']] = dict(yearly=yr,
            risk_atr_pct={q: round(float(np.percentile(ratr, q)), 3) for q in (5, 50, 95)} if len(ratr) else {},
            long_n=int(len(long_R)), long_exp=round(float(long_R.mean()), 3) if len(long_R) else None,
            short_n=int(len(short_R)), short_exp=round(float(short_R.mean()), 3) if len(short_R) else None,
            val_n=int(len(mv)), val_exp=round(float(mv.mean()), 3) if len(mv) >= 5 else None)
    # pairwise monthly correlations among distinct candidates (over/under-clustering + portfolio diagnostics)
    cids = list(monthly.keys())
    def corr_ci(a_, b_, nb=1500, seed=0):
        m = pd.concat([monthly[a_], monthly[b_]], axis=1).dropna()
        if len(m) < 6: return None, None, None, len(m)
        x = m.iloc[:, 0].values; y = m.iloc[:, 1].values; r = float(np.corrcoef(x, y)[0, 1])
        rng = np.random.default_rng(seed); bs = []
        for _ in range(nb):
            idx = rng.integers(0, len(x), len(x))
            if np.std(x[idx]) > 0 and np.std(y[idx]) > 0: bs.append(np.corrcoef(x[idx], y[idx])[0, 1])
        return r, (float(np.percentile(bs, 2.5)) if bs else None), (float(np.percentile(bs, 97.5)) if bs else None), len(m)
    pairs = []
    for i, aa in enumerate(cids):
        for bb in cids[i + 1:]:
            r, lo, hi, nm = corr_ci(aa, bb, seed=(hash((aa, bb)) & 0xffff))
            if r is not None: pairs.append(dict(a=aa, b=bb, r=round(r, 2), lo=round(lo, 2), hi=round(hi, 2), nm=nm))

    dedup_out = []
    for _, c in dedup.iterrows():
        row = c.to_dict(); row['member_ids'] = list(row['member_ids']); row.update(extra[c['cluster_id']]); dedup_out.append(row)
    json.dump(dict(n_distinct=len(dedup_out), clusters=dedup_out), open(os.path.join(OUT, 'kb_dedup.json'), 'w'), indent=1, default=str)
    json.dump(dict(pairs=pairs, month_streams={k: {i: round(float(v), 3) for i, v in monthly[k].items()} for k in cids}),
              open(os.path.join(OUT, 'kb_correlations.json'), 'w'), indent=1, default=str)
    # mechanism aggregates
    magg = {}
    for fam in sorted(alld['family'].unique(), key=lambda f: int(f[1:])):
        s = alld[alld['family'] == fam]; sp = s[s['n'] > 0]
        magg[fam] = dict(econ=ECON_ALL.get(fam), engine=id2reg.get(s['id'].iloc[0]), hyps=len(s),
                         profitable=int(s['hist_prof'].sum()), rw=int(s['research_worthy'].sum()),
                         bestExp=round(float(sp['exp'].max()), 3) if len(sp) else None,
                         bestOOS=round(float(sp['val_exp'].max()), 3) if len(sp) and sp['val_exp'].notna().any() else None)
    json.dump(dict(totals=dict(hyps=int(len(alld)), profitable=int(alld['hist_prof'].sum()), rw=int(alld['research_worthy'].sum())),
                   per_family=magg), open(os.path.join(OUT, 'kb_mechanism_agg.json'), 'w'), indent=1, default=str)
    print('n_distinct_candidates', len(dedup_out))
    print('registry_rows', len(reg))
    print('totals hyps/prof/rw', len(alld), int(alld['hist_prof'].sum()), int(alld['research_worthy'].sum()))

if __name__ == '__main__':
    main()
