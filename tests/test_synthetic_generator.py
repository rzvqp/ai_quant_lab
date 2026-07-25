"""Tests for the synthetic price generator (code/synth_price.py). Run: venv/Scripts/python tests/test_synthetic_generator.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))
import numpy as np, synth_price as SP, matched_null as MN

def test_ohlc_valid():
    df = SP.gen_series(n=3000, seed=1, vol_clustering=0.85, gap_rate=0.02)
    o, h, l, c = df['open'].values, df['high'].values, df['low'].values, df['close'].values
    assert np.all(h >= np.maximum(o, c) - 1e-9), "high must bracket open/close"
    assert np.all(l <= np.minimum(o, c) + 1e-9), "low must bracket open/close"
    assert np.all(l > 0), "prices positive"
    assert np.all(np.isfinite(df['m_atr'].values)) and np.all(df['m_atr'].values > 0), "atr finite>0"
    for col in ('session', 'month', 'atrq'):
        assert col in df.columns, f"missing stratum col {col}"
    print("PASS test_ohlc_valid")

def test_reproducible():
    a = SP.gen_series(n=2000, seed=42, vol_clustering=0.7)
    b = SP.gen_series(n=2000, seed=42, vol_clustering=0.7)
    assert np.allclose(a['close'].values, b['close'].values), "same seed must reproduce"
    c = SP.gen_series(n=2000, seed=43, vol_clustering=0.7)
    assert not np.allclose(a['close'].values, c['close'].values), "different seed must differ"
    print("PASS test_reproducible")

def test_inject_zero_is_noop():
    df = SP.gen_series(n=2000, seed=5)
    bars, dirs = SP.exo_signals(df, n_sig=100, seed=5)
    df0 = SP.inject_edge(df, bars, dirs, edge_atr=0.0)
    assert np.allclose(df['close'].values, df0['close'].values), "edge=0 must be a no-op"
    print("PASS test_inject_zero_is_noop")

def test_edge_raises_expectancy():
    df = SP.gen_series(n=6000, seed=7, vol_clustering=0.85)
    bars, dirs = SP.exo_signals(df, n_sig=200, seed=7, side='long')
    su0 = SP.make_setups(df, bars, dirs); m0 = MN.observed_profile(df, su0)['mean']
    dfe = SP.inject_edge(df, bars, dirs, edge_atr=1.0, horizon=8, seed=7)
    sue = SP.make_setups(dfe, bars, dirs); m1 = MN.observed_profile(dfe, sue)['mean']
    assert m1 > m0 + 0.1, f"injected edge must raise expectancy ({m0:.3f} -> {m1:.3f})"
    print(f"PASS test_edge_raises_expectancy (null {m0:.3f} -> edge {m1:.3f})")

def test_edge_monotone():
    df = SP.gen_series(n=6000, seed=9, vol_clustering=0.85)
    bars, dirs = SP.exo_signals(df, n_sig=250, seed=9, side='long')
    means = []
    for mag in (0.0, 0.25, 0.5, 1.0):
        dfe = SP.inject_edge(df, bars, dirs, edge_atr=mag, horizon=8, seed=9)
        means.append(MN.observed_profile(dfe, SP.make_setups(dfe, bars, dirs))['mean'])
    assert all(means[i] <= means[i+1] + 1e-6 for i in range(len(means)-1)), f"expectancy must rise with edge: {means}"
    print(f"PASS test_edge_monotone {[round(m,3) for m in means]}")

if __name__ == "__main__":
    test_ohlc_valid(); test_reproducible(); test_inject_zero_is_noop()
    test_edge_raises_expectancy(); test_edge_monotone()
    print("ALL SYNTHETIC-GENERATOR TESTS PASSED")
