"""Matched-null POWER battery (docs/MATCHED_NULL_SPEC §8).
>=5 edge magnitudes {0,tiny,small,moderate,large} x >=3 signal frequencies x >=50 series. Paired design:
one base NULL series+signals per (freq,series); inject each magnitude; compute matched-null p. Power must
rise monotonically with edge; power at edge=0 == FPR. Writes power_curve.parquet + power_summary.json."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, synth_price as SP, matched_null as MN

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "matched_null_validation")
os.makedirs(OUT, exist_ok=True)

MAGS = [0.0, 0.1, 0.25, 0.5, 1.0]     # edge_atr: none / tiny / small / moderate / large
FREQS = [80, 200, 400]                 # n_sig: low / mid / high frequency
N_SERIES = 50
B = 1000
HORIZON = 8
MASTER = 20260714

def run():
    rng = np.random.default_rng(MASTER)
    rows = []; t0 = time.time(); done = 0; total = len(FREQS) * N_SERIES
    for freq in FREQS:
        for s in range(N_SERIES):
            seed = int(rng.integers(1, 2**31))
            df = SP.gen_series(n=6000, seed=seed, vol_base=0.0009, vol_clustering=0.85)
            bars, dirs = SP.exo_signals(df, n_sig=freq, seed=seed, side='long')
            for mag in MAGS:
                dfe = SP.inject_edge(df, bars, dirs, edge_atr=mag, horizon=HORIZON, seed=seed ^ 0xed)
                su = SP.make_setups(dfe, bars, dirs, risk_kind='atr', risk_mult=1.5,
                                    exit_kind='rr', exit_param=2.0)
                rec = MN.matched_null_p(dfe, su, B=B, seed=seed ^ 0x5eed)
                rows.append(dict(freq=freq, series=s, seed=seed, edge_atr=mag,
                                 k=rec['k'], obs_mean=rec['obs_mean'], p=rec['p'],
                                 null_mean=rec.get('null_mean')))
            done += 1
            if done % 25 == 0:
                print(f"  power {done}/{total} series, elapsed {time.time()-t0:.0f}s", flush=True)
    df_out = pd.DataFrame(rows)
    df_out.to_parquet(os.path.join(OUT, "power_curve.parquet"))
    # summary: power at 0.05 / 0.01 by (freq,edge)
    summ = {"MAGS": MAGS, "FREQS": FREQS, "N_SERIES": N_SERIES, "B": B, "horizon": HORIZON, "cells": []}
    for freq in FREQS:
        curve05 = []; curve01 = []
        for mag in MAGS:
            sub = df_out[(df_out.freq == freq) & (df_out.edge_atr == mag)]
            pw05 = float((sub['p'] < 0.05).mean()); pw01 = float((sub['p'] < 0.01).mean())
            bias = float((sub['obs_mean'] - sub['null_mean']).mean())
            curve05.append(pw05); curve01.append(pw01)
            summ["cells"].append(dict(freq=freq, edge_atr=mag, power05=pw05, power01=pw01,
                                      mean_k=float(sub['k'].mean()), mean_obs=float(sub['obs_mean'].mean()),
                                      edge_vs_null_gap=bias))
        summ[f"monotonic05_freq{freq}"] = bool(all(curve05[i] <= curve05[i+1] + 1e-9 for i in range(len(curve05)-1)))
        summ[f"monotonic01_freq{freq}"] = bool(all(curve01[i] <= curve01[i+1] + 1e-9 for i in range(len(curve01)-1)))
    summ["power_at_zero_ok"] = bool(all(c["power05"] <= 0.15 for c in summ["cells"] if c["edge_atr"] == 0.0))
    summ["monotonic_all05"] = all(summ[f"monotonic05_freq{f}"] for f in FREQS)
    summ["high_edge_power_ok"] = bool(all(c["power05"] >= 0.6 for c in summ["cells"] if c["edge_atr"] == 1.0))
    json.dump(summ, open(os.path.join(OUT, "power_summary.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))

if __name__ == "__main__":
    run()
