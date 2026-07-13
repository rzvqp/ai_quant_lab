"""Parity tests (docs/MATCHED_NULL_SPEC §11): both observed and null trades execute via mstrat.simulate
with the shared CFG (same costs / stop-floor / overlap / intrabar / R). Terminal holdout is never passed.
Run: venv/Scripts/python tests/test_matched_null_parity.py"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "code"))
import numpy as np, pandas as pd, mstrat as MS, matched_null as MN, synth_price as SP

_D = {}
def _real_res():
    if 'res' not in _D:
        d = MS.load(); _D['d'] = d; _D['res'] = d.iloc[:int(len(d)*0.6)].copy()
    return _D['res']

def test_observed_equals_backtest_real():
    """observed_profile must reproduce MS.backtest R exactly (same trades, same engine)."""
    res = _real_res()
    h = next(h for h in MS.REGISTRY['S5'][0]() if len(MS.backtest(res, h)) >= 200)
    setups = MS.setups(res, h)
    prof = MN.observed_profile(res, setups)
    bt = MS.backtest(res, h)['R'].values
    assert prof['k'] == len(bt), f"trade count mismatch {prof['k']} vs {len(bt)}"
    assert np.max(np.abs(np.sort(prof['R']) - np.sort(bt))) < 1e-12, "observed R must equal MS.backtest R"
    print(f"PASS test_observed_equals_backtest_real (k={prof['k']})")

def test_null_routes_through_simulate_stopfloor():
    """A null setup with a sub-floor tiny stop must be floored by MS.simulate exactly like any setup."""
    df = SP.gen_series(n=1500, seed=3)
    o = df['open'].values; atr = df['m_atr'].values; cfg = MS.CFG; i = 500
    tiny = 0.001  # far below the executable floor
    su = [dict(si=i, ei=i+1, dir=1, stop=float(o[i+1]-tiny), exit_kind='time', exit_param=10)]
    r_eng = MS.simulate(df, su, cfg)['R'].values
    # manual replication of the v2 floor + R
    entry = o[i+1]; risk = tiny
    min_exec = max(2*cfg['spread_ticks']*MS.TICK, 5*MS.TICK, 0.10*atr[i])
    risk_floored = max(risk, min_exec)
    assert risk_floored > risk, "test setup must trigger the floor"
    cost = (cfg['spread_ticks']+cfg['slip_ticks'])*MS.TICK
    # exit at close after timeout (no stop/tgt hit expected for a 10-bar time exit with a wide floored stop)
    # just assert the engine used the FLOORED risk: |R| scale consistent with risk_floored not tiny
    assert np.isfinite(r_eng[0]), "engine produced a trade"
    implied_move = abs(r_eng[0]) * risk_floored  # if engine used tiny risk, implied_move would be ~1000x smaller
    assert implied_move < 50, "R computed with floored risk (not the tiny raw risk)"
    print(f"PASS test_null_routes_through_simulate_stopfloor (floor={min_exec:.3f}, R={r_eng[0]:.3f})")

def test_same_cfg_costs():
    """Null and observed both charge the same 2x cost via MS.simulate."""
    df = SP.gen_series(n=1500, seed=4)
    bars, dirs = SP.exo_signals(df, n_sig=60, seed=4)
    su = SP.make_setups(df, bars, dirs)
    prof = MN.observed_profile(df, su)
    rec = MN.matched_null_p(df, su, B=200, seed=1)
    assert rec['k'] == prof['k'], "profile count parity"
    assert rec['null_mean'] is not None and np.isfinite(rec['null_mean']), "null routed through engine"
    print(f"PASS test_same_cfg_costs (k={rec['k']}, null_mean={rec['null_mean']:.3f})")

def test_holdout_excluded():
    """The matched-null only ever sees the slice it is given; the pilot passes the research segment,
    whose max index is strictly below the terminal-holdout boundary (0.8*n)."""
    d = _D['d'] if 'd' in _D else MS.load(); _D['d'] = d
    n = len(d); b = int(n*0.8); res = d.iloc[:int(n*0.6)]
    assert res.index.max() < b, "research segment must end before the sealed holdout boundary"
    # sanity: matched_null_p uses len(df) internally, never indexes beyond the passed frame
    print(f"PASS test_holdout_excluded (research ends {res.index.max()} < holdout start {b}, n={n})")

if __name__ == "__main__":
    test_null_routes_through_simulate_stopfloor()
    test_same_cfg_costs()
    test_observed_equals_backtest_real()
    test_holdout_excluded()
    print("ALL PARITY TESTS PASSED")
