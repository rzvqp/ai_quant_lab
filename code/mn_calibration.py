"""Matched-null CALIBRATION battery (docs/MATCHED_NULL_SPEC §7).
>=100 independent synthetic NULL price series (no injected edge). For each: build a structured hypothesis,
compute matched-null p. Under H0 (no edge) p must be ~Uniform(0,1). Writes null_calibration.parquet +
calibration_summary.json. Run: venv/Scripts/python code/mn_calibration.py"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, synth_price as SP, matched_null as MN

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "matched_null_validation")
os.makedirs(OUT, exist_ok=True)

N_SERIES = 120
B = 2000
MASTER = 20260713

def wilson(k, n, z=1.959963985):
    if n == 0: return (0.0, 1.0)
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d; h = (z*np.sqrt(p*(1-p)/n + z*z/(4*n*n))) / d
    return (max(0, c-h), min(1, c+h))

def ks_uniform(ps):
    x = np.sort(np.asarray(ps)); n = len(x); i = np.arange(1, n+1)
    d = np.max(np.maximum(i/n - x, x - (i-1)/n))
    return float(d), float(np.exp(-2*n*d*d))  # asymptotic p (conservative)

def run():
    rng = np.random.default_rng(MASTER)
    rows = []; t0 = time.time()
    # vary structure: vol clustering on/off, n_sig, side, exit rule, risk kind — all under ZERO edge
    templates = [
        dict(exit_kind='rr', exit_param=2.0, risk_kind='atr',  side='long'),
        dict(exit_kind='rr', exit_param=3.0, risk_kind='atr',  side='short'),
        dict(exit_kind='time', exit_param=24, risk_kind='atr', side='long'),
        dict(exit_kind='rr', exit_param=2.0, risk_kind='struct', side='long'),
    ]
    for s in range(N_SERIES):
        seed = int(rng.integers(1, 2**31))
        tpl = templates[s % len(templates)]
        vc = 0.85 if (s % 2 == 0) else 0.0
        n_sig = int(rng.integers(120, 320))
        df = SP.gen_series(n=6000, seed=seed, vol_base=0.0009, vol_clustering=vc)
        bars, dirs = SP.exo_signals(df, n_sig=n_sig, seed=seed, side=tpl['side'])
        su = SP.make_setups(df, bars, dirs, risk_kind=tpl['risk_kind'], risk_mult=1.5,
                            exit_kind=tpl['exit_kind'], exit_param=tpl['exit_param'])
        rec = MN.matched_null_p(df, su, B=B, seed=seed ^ 0x5eed)
        rows.append(dict(series=s, seed=seed, vc=vc, n_sig=n_sig, **{k: tpl[k] for k in tpl},
                         k=rec['k'], obs_mean=rec['obs_mean'], p=rec['p'], k_ge=rec['k_ge'],
                         null_mean=rec.get('null_mean'), null_sd=rec.get('null_sd')))
        if (s+1) % 20 == 0:
            print(f"  calib {s+1}/{N_SERIES} elapsed {time.time()-t0:.0f}s", flush=True)
    df_out = pd.DataFrame(rows)
    df_out.to_parquet(os.path.join(OUT, "null_calibration.parquet"))
    ps = df_out['p'].values
    ks_d, ks_p = ks_uniform(ps)
    summary = dict(n_series=len(ps), B=B, master_seed=MASTER,
                   mean_p=float(ps.mean()), min_p=float(ps.min()), any_zero=bool((ps == 0).any()),
                   ks_d=ks_d, ks_p=ks_p,
                   fpr={lvl: dict(rate=float((ps < lvl).mean()),
                                  ci=[round(x, 4) for x in wilson(int((ps < lvl).sum()), len(ps))],
                                  nominal=lvl)
                        for lvl in (0.10, 0.05, 0.01)})
    # split-half stability
    half = len(ps)//2
    summary['split_half_fpr05'] = [float((ps[:half] < 0.05).mean()), float((ps[half:] < 0.05).mean())]
    # criteria
    f05 = summary['fpr']['0.05']; f01 = summary['fpr']['0.01']; f10 = summary['fpr']['0.10']
    summary['criteria'] = dict(
        ks_ok=ks_p > 0.05, no_zero=not summary['any_zero'],
        fpr05_ok=(f05['ci'][0] <= 0.05 <= f05['ci'][1]),
        fpr01_ok=(f01['ci'][0] <= 0.01 <= f01['ci'][1]),
        fpr10_ok=(f10['ci'][0] <= 0.10 <= f10['ci'][1]))
    summary['CALIBRATED'] = all(summary['criteria'].values())
    json.dump(summary, open(os.path.join(OUT, "calibration_summary.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print("CALIBRATED:", summary['CALIBRATED'])

if __name__ == "__main__":
    run()
