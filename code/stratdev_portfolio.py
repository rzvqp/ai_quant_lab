"""Exploratory portfolio diagnostics for the shortlist (workstream B, Etapa 6). READ-ONLY: re-runs the
official MS.backtest on the RESEARCH segment for each shortlisted representative to derive monthly return
streams, inter-strategy correlations WITH bootstrap CIs, trade overlap, and exposures. Diagnostic only —
NO weight optimization, NO validated-portfolio claim, holdout untouched."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))
import numpy as np, pandas as pd, mstrat as MS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def find_h(hid):
    for fam in MS.REGISTRY:
        for h in MS.REGISTRY[fam][0]():
            if h['id'] == hid:
                return h
    return None

def run():
    reg = pd.read_parquet(os.path.join(ROOT, "STRATEGY_CANDIDATE_REGISTRY.parquet"))
    sl = reg[reg['shortlisted']].copy()
    d = MS.load(); res = d.iloc[:int(len(d)*0.6)].copy()
    tvals = res['time'].values
    monthly = {}; yearly = {}; ledgers = {}; exposure = {}
    for _, r in sl.iterrows():
        cid = r['candidate_id']; h = find_h(r['representative_hypothesis_id'])
        tr = MS.backtest(res, h); ei = tr['ei'].astype(int).values; R = tr['R'].values
        ts = pd.to_datetime(tvals[ei], unit='s', utc=True)
        mon = pd.Series(R, index=ts).groupby(pd.Grouper(freq='ME')).sum()   # monthly summed R
        yr = pd.Series(R, index=ts).groupby(ts.year).mean()
        monthly[cid] = mon; yearly[cid] = {int(k): round(float(v), 3) for k, v in yr.items()}
        setups = MS.setups(res, h)
        # active-bar set for overlap (entry..exit approx via next 48 or exit — use holding proxy = ei..ei+median_hold)
        dirs = [s['dir'] for s in setups]
        exposure[cid] = dict(mechanism=r['mechanism'], n=int(len(R)),
                             long_frac=float(np.mean(np.array([s['dir'] for s in setups]) > 0)) if setups else None,
                             active_months=int((mon != 0).sum()),
                             temporal_concentration_top_year=max(
                                 {int(y): float((R[ts.year.values == y]).sum()) for y in set(ts.year)}.values()) /
                                 (R.sum() if R.sum() != 0 else 1))
        ledgers[cid] = pd.DataFrame({'month': mon.index.astype(str), 'R': mon.values})
    # align monthly streams
    allm = pd.DataFrame(monthly).sort_index()
    allm.index = allm.index.astype(str)
    allm.to_parquet(os.path.join(ROOT, "exploratory_monthly_returns.parquet"))
    cids = list(monthly.keys())

    def corr_ci(a, b, nboot=2000, seed=0):
        m = pd.concat([monthly[a], monthly[b]], axis=1).dropna()
        if len(m) < 6:
            return None, None, None, len(m)
        x = m.iloc[:, 0].values; y = m.iloc[:, 1].values
        r = float(np.corrcoef(x, y)[0, 1])
        rng = np.random.default_rng(seed); bs = []
        for _ in range(nboot):
            idx = rng.integers(0, len(x), len(x))
            if np.std(x[idx]) > 0 and np.std(y[idx]) > 0:
                bs.append(np.corrcoef(x[idx], y[idx])[0, 1])
        lo, hi = (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))) if bs else (None, None)
        return r, lo, hi, len(m)

    cmat = {}; pairs = []
    for i, a in enumerate(cids):
        for b in cids[i+1:]:
            r, lo, hi, nm = corr_ci(a, b, seed=hash((a, b)) & 0xffff)
            pairs.append(dict(a=a, b=b, mech_a=reg.set_index('candidate_id').loc[a, 'mechanism'],
                              mech_b=reg.set_index('candidate_id').loc[b, 'mechanism'],
                              r=r, ci_lo=lo, ci_hi=hi, common_months=nm))
    out = dict(n_shortlist=len(cids), common_month_range=[allm.index.min(), allm.index.max()],
               exposures=exposure, yearly=yearly, pairwise_correlations=pairs)
    json.dump(out, open(os.path.join(ROOT, "exploratory_correlation.json"), "w"), indent=1, default=str)
    # concise print
    print(f"shortlist={len(cids)} months={allm.index.min()}..{allm.index.max()}")
    print("Most NEGATIVE (complementary) pairs (r, 95%CI):")
    for p in sorted([p for p in pairs if p['r'] is not None], key=lambda z: z['r'])[:8]:
        print(f"  r={p['r']:+.2f} [{p['ci_lo']:+.2f},{p['ci_hi']:+.2f}] n={p['common_months']}  {p['mech_a']}  vs  {p['mech_b']}")
    print("Most POSITIVE (redundant) pairs:")
    for p in sorted([p for p in pairs if p['r'] is not None], key=lambda z: -z['r'])[:6]:
        print(f"  r={p['r']:+.2f} [{p['ci_lo']:+.2f},{p['ci_hi']:+.2f}] n={p['common_months']}  {p['mech_a']}  vs  {p['mech_b']}")

if __name__ == "__main__":
    run()
