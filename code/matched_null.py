"""Matched-null engine (Test B, primary alpha-existence test) — docs/MATCHED_NULL_SPEC.md.
Both observed and null trades are executed by mstrat.simulate (ENGINE v2) with the shared CFG — this module
does NOT re-implement execution. It only (a) extracts the realized (risk,dir,exit) profile of the observed
executed trades, (b) manufactures counterfactual setups with random entry timing that preserve that profile,
and (c) routes them through MS.simulate. p = (k_ge+1)/(B+1), one-sided H0: mean_R <= 0."""
import numpy as np, pandas as pd
import mstrat as MS

TICK = MS.TICK

# ---------- observed profile extraction ----------
def observed_profile(d, setups, cfg=MS.CFG):
    """Run the observed setups through MS.simulate and extract the per-executed-trade profile.
    Risk is stored as a RATIO to local ATR (risk/ATR[si]); the null rescales it to the ATR at the
    counterfactual entry bar. This preserves the strategy's risk-in-ATR-units profile and its local-
    volatility scaling (real stops are 1.5*ATR or structural ~local range) — WITHOUT it, the null
    mismatches risk to local vol and inflates FPR under level-drifting/trending series (adversarial finding)."""
    o = d['open'].values; atr = d['m_atr'].values
    tr = MS.simulate(d, setups, cfg)
    ei = tr['ei'].astype(int).values; R = tr['R'].values
    by_ei = {s['ei']: s for s in setups}
    risks = np.empty(len(ei)); risk_over_atr = np.empty(len(ei)); dirs = np.empty(len(ei), dtype=int); enc = []
    for j, e in enumerate(ei):
        s = by_ei[e]; entry = o[e]; risk = abs(entry - s['stop'])
        si = s['si']; a = atr[si] if (si < len(atr) and np.isfinite(atr[si]) and atr[si] > 0) else np.nan
        risk_over_atr[j] = (risk / a) if np.isfinite(a) else np.nan
        risks[j] = risk; dirs[j] = s['dir']
        ek = s['exit_kind']; ep = s.get('exit_param')
        if ek in ('opp_liq', 'opp_struct'):
            rr_eff = abs(float(ep) - entry) / risk if (risk > 0 and ep is not None and np.isfinite(ep)) else 2.0
            enc.append(('rr', float(np.clip(rr_eff, 0.25, 10.0))))
        elif ek == 'rr':
            enc.append(('rr', float(ep)))
        elif ek == 'time':
            enc.append(('time', int(ep)))
        elif ek == 'trailing':
            enc.append(('trailing', None))
        else:
            enc.append(('rr', 2.0))
    # fill any non-finite risk/ATR ratio with the median (rare: signal bar with bad ATR)
    if len(risk_over_atr):
        med = np.nanmedian(risk_over_atr)
        risk_over_atr = np.where(np.isfinite(risk_over_atr), risk_over_atr, med if np.isfinite(med) else 1.5)
    return dict(R=R, mean=float(R.mean()) if len(R) else float('nan'), k=len(R),
                risks=risks, risk_over_atr=risk_over_atr, dirs=dirs, enc=enc, ei=ei)

# ---------- eligibility pool (optionally stratified) ----------
def eligibility_pool(d, strata=None):
    atr = d['m_atr'].values; n = len(d)
    valid = np.where(np.isfinite(atr) & (atr > 0))[0]
    valid = valid[(valid > 2) & (valid < n - 2)]
    if not strata:
        return {'_all': valid}
    keys = np.array(list(zip(*[d[s].values for s in strata])), dtype=object) if len(strata) > 1 \
        else d[strata[0]].values
    pool = {}
    if len(strata) > 1:
        keyv = [tuple(d[s].values[i] for s in strata) for i in valid]
        for i, kk in zip(valid, keyv):
            pool.setdefault(kk, []).append(i)
    else:
        kv = d[strata[0]].values
        for i in valid:
            pool.setdefault(kv[i], []).append(i)
    return {k: np.asarray(v) for k, v in pool.items()}

def _strata_key(d, ei, strata):
    if not strata:
        return np.full(len(ei), '_all', dtype=object)
    if len(strata) == 1:
        kv = d[strata[0]].values; return np.array([kv[e] for e in ei], dtype=object)
    return np.array([tuple(d[s].values[e] for s in strata) for e in ei], dtype=object)

# ---------- one null replicate (routes through MS.simulate) ----------
def _null_mean(d, prof, pool, strata_keys, rng, cfg):
    o = d['open'].values; atr = d['m_atr'].values; k = prof['k']
    idx = rng.integers(0, k, size=k)                       # bootstrap the (risk/ATR,dir,exit,stratum) profile
    setups = []
    for j in idx:
        key = strata_keys[j] if strata_keys is not None else '_all'
        cand = pool.get(key, pool.get('_all'))
        if cand is None or len(cand) == 0:
            cand = next(iter(pool.values()))
        i = int(cand[rng.integers(0, len(cand))])
        dirn = int(prof['dirs'][j]); ek, ep = prof['enc'][j]
        risk = float(prof['risk_over_atr'][j]) * float(atr[i])   # rescale risk to LOCAL ATR at the null entry
        if not np.isfinite(risk) or risk <= 0:
            risk = float(prof['risks'][j])
        setups.append(dict(si=i, ei=i + 1, dir=dirn,
                           stop=float(o[i + 1] - dirn * risk), exit_kind=ek, exit_param=ep))
    r = MS.simulate(d, setups, cfg)['R'].values
    return float(r.mean()) if len(r) else float('nan')

# ---------- full matched-null p-value ----------
def matched_null_p(d, setups, cfg=MS.CFG, B=2000, seed=0, strata=None, min_k=25):
    prof = observed_profile(d, setups, cfg)
    k = prof['k']
    rec = dict(k=k, obs_mean=prof['mean'], B=B, seed=seed, strata=strata)
    if k < min_k or not np.isfinite(prof['mean']):
        rec.update(p=1.0, k_ge=None, null_mean=None, null_sd=None, ci=(None, None),
                   note='k<min_k or non-finite observed mean'); return rec
    pool = eligibility_pool(d, strata)
    skeys = _strata_key(d, prof['ei'], strata) if strata else None
    rng = np.random.default_rng(seed)
    means = np.empty(B)
    for b in range(B):
        means[b] = _null_mean(d, prof, pool, skeys, rng, cfg)
    means = means[np.isfinite(means)]
    Beff = len(means)
    k_ge = int(np.sum(means >= prof['mean']))
    p = (k_ge + 1) / (Beff + 1)
    # Wilson 95% CI on the p proportion
    z = 1.959963985; phat = k_ge / Beff; denom = 1 + z*z/Beff
    center = (phat + z*z/(2*Beff)) / denom
    half = (z * np.sqrt(phat*(1-phat)/Beff + z*z/(4*Beff*Beff))) / denom
    rec.update(p=p, k_ge=k_ge, B=Beff, null_mean=float(means.mean()), null_sd=float(means.std(ddof=1)),
               ci=(float(max(0.0, center-half)), float(min(1.0, center+half))),
               null_q=[float(np.quantile(means, q)) for q in (0.5, 0.9, 0.95, 0.99)])
    return rec
