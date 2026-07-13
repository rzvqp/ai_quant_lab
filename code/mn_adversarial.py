"""Matched-null ADVERSARIAL battery (docs/MATCHED_NULL_SPEC §9). For each stressed scenario, generate
NULL (no-edge) series and confirm the matched-null STAYS calibrated (FPR near nominal). Writes
adversarial.parquet + adversarial_summary.json."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, synth_price as SP, matched_null as MN

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "matched_null_validation")
os.makedirs(OUT, exist_ok=True)
N = 40; B = 1500; MASTER = 20260715

def wilson(k, n, z=1.959963985):
    if n == 0: return (0.0, 1.0)
    p = k/n; d = 1+z*z/n; c = (p+z*z/(2*n))/d; h = (z*np.sqrt(p*(1-p)/n+z*z/(4*n*n)))/d
    return (max(0, c-h), min(1, c+h))

def build(scn, seed, rng):
    """Return (df, bars, dirs, setup_kwargs) for a NULL series stressed per scenario `scn`."""
    sk = dict(risk_kind='atr', risk_mult=1.5, exit_kind='rr', exit_param=2.0); side = 'long'; n_sig = 200
    df = None
    if scn == 'drift_long':      df = SP.gen_series(6000, seed, drift=0.0004, vol_clustering=0.8)
    elif scn == 'trend_short':   df = SP.gen_series(6000, seed, drift=-0.0004, vol_clustering=0.8); side='short'
    elif scn == 'range_ar1':     df = SP.gen_series(6000, seed, ar1=-0.3, vol_clustering=0.5)
    elif scn == 'vol_cluster':   df = SP.gen_series(6000, seed, vol_clustering=0.92)
    elif scn == 'regime_shift':  df = SP.gen_series(6000, seed, vol_clustering=0.7, regimes=[(0.5, 3.0, 0.0002)])
    elif scn == 'heavy_gaps':    df = SP.gen_series(6000, seed, vol_clustering=0.8, gap_rate=0.05, gap_size=5.0)
    elif scn == 'struct_stops':  df = SP.gen_series(6000, seed, vol_clustering=0.8); sk['risk_kind']='struct'
    elif scn == 'exit_time':     df = SP.gen_series(6000, seed, vol_clustering=0.8); sk=dict(risk_kind='atr',risk_mult=1.5,exit_kind='time',exit_param=24)
    elif scn == 'exit_trailing': df = SP.gen_series(6000, seed, vol_clustering=0.8); sk=dict(risk_kind='atr',risk_mult=1.5,exit_kind='trailing',exit_param=None)
    elif scn == 'low_freq':      df = SP.gen_series(6000, seed, vol_clustering=0.8); n_sig=40
    elif scn == 'high_freq_overlap': df = SP.gen_series(6000, seed, vol_clustering=0.8); n_sig=700
    else:                        df = SP.gen_series(6000, seed, vol_clustering=0.8)
    if scn == 'concentrated_year':      # all signals in first third of the series
        bars, dirs = SP.exo_signals(df.iloc[:2000], n_sig=120, seed=seed, side=side)
    elif scn == 'concentrated_session': # single hour only
        bars, dirs = SP.timeofday_signals(df, hour=8, side=side)
    else:
        bars, dirs = SP.exo_signals(df, n_sig=n_sig, seed=seed, side=side)
    return df, bars, dirs, sk

SCENARIOS = ['drift_long','trend_short','range_ar1','vol_cluster','regime_shift','heavy_gaps',
             'struct_stops','exit_time','exit_trailing','low_freq','high_freq_overlap',
             'concentrated_year','concentrated_session']

def run():
    rng = np.random.default_rng(MASTER); rows = []; t0 = time.time()
    for scn in SCENARIOS:
        for s in range(N):
            seed = int(rng.integers(1, 2**31))
            df, bars, dirs, sk = build(scn, seed, rng)
            if len(bars) < 25:
                continue
            su = SP.make_setups(df, bars, dirs, **sk)
            rec = MN.matched_null_p(df, su, B=B, seed=seed ^ 0x5eed)
            rows.append(dict(scenario=scn, series=s, seed=seed, k=rec['k'],
                             obs_mean=rec['obs_mean'], p=rec['p']))
        print(f"  adversarial {scn} done, elapsed {time.time()-t0:.0f}s", flush=True)
    df_out = pd.DataFrame(rows); df_out.to_parquet(os.path.join(OUT, "adversarial.parquet"))
    summ = {"N_per_scenario": N, "B": B, "scenarios": []}
    all_ok = True
    for scn in SCENARIOS:
        sub = df_out[df_out.scenario == scn]; m = len(sub)
        if m == 0: continue
        f05 = float((sub['p'] < 0.05).mean()); f01 = float((sub['p'] < 0.01).mean())
        ci05 = [round(x, 4) for x in wilson(int((sub['p'] < 0.05).sum()), m)]
        ok = bool(ci05[0] <= 0.05 <= ci05[1] or f05 <= 0.10)   # calibrated or at worst mildly loose
        all_ok = all_ok and ok
        summ["scenarios"].append(dict(scenario=scn, n=int(m), mean_p=float(sub['p'].mean()),
                                      fpr05=f05, fpr05_ci=ci05, fpr01=f01, mean_k=float(sub['k'].mean()),
                                      any_zero=bool((sub['p']==0).any()), calibrated=ok))
    summ["ALL_SCENARIOS_CALIBRATED"] = bool(all_ok)
    json.dump(summ, open(os.path.join(OUT, "adversarial_summary.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))

if __name__ == "__main__":
    run()
