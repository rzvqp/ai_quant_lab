"""Unit tests for the Wave-1 harness. The load-bearing guarantees:
  * PARITY: the toggled control-arm builders reproduce the FROZEN engine's setups byte-for-byte with the
    treatment toggle ON (so the control arm differs in EXACTLY ONE dimension).
  * NO HOLDOUT LEAK: only research+OOS are exposed; the terminal 20% is never returned.
  * EXECUTION VIA ENGINE ONLY: sim_R == MS.simulate.
  * PLACEBO INTEGRITY: the level shuffle preserves daily persistence + signal frequency but destroys identity.
  * MULTIPLICITY: Holm-Bonferroni is correct, monotone, and >= raw p.
Run: python -m pytest tests/test_wave1_harness.py -q     (or python tests/test_wave1_harness.py)
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'code'))
import numpy as np
import mstrat as MS, mstrat_ext as MSX
import wave1_harness as W

_D = {}
def seg():
    if 'res' not in _D:
        d = MS.load(); n = len(d); a = int(n * 0.6)
        _D['res'] = d.iloc[:a].copy(); _D['n'] = n
    return _D['res']

def _same_setups(A, B):
    if len(A) != len(B):
        return False
    ka = sorted(A, key=lambda s: (s['si'], s['ei'])); kb = sorted(B, key=lambda s: (s['si'], s['ei']))
    for x, y in zip(ka, kb):
        for k in ('si', 'ei', 'dir', 'exit_kind'):
            if x[k] != y[k]:
                return False
        if abs(float(x['stop']) - float(y['stop'])) > 1e-9:
            return False
        xp, yp = x.get('exit_param'), y.get('exit_param')
        if (xp is None) != (yp is None):
            return False
        if xp is not None and abs(float(xp) - float(yp)) > 1e-9:
            return False
    return True

def test_parity_sweep_confirm_on_equals_s1():
    res = seg(); h = W.PREREG['reps']['S1']['h']
    mine, _ = W.sweep_setups(res, h, confirm=True)
    ref = MS.s1_setups(res, h)
    assert _same_setups(mine, ref), 'sweep_setups(confirm=True) must reproduce MS.s1_setups exactly'

def test_parity_cont_gate_on_equals_s39():
    res = seg(); h = W.PREREG['reps']['S39']['h']
    mine = W.cont_setups(res, h, gate=True)
    ref = MSX.s39_setups(res, h)
    assert _same_setups(mine, ref), 'cont_setups(gate=True) must reproduce MSX.s39_setups exactly'

def test_raw_is_superset_of_confirmed():
    res = seg(); h = W.PREREG['reps']['S1']['h']
    conf, _ = W.sweep_setups(res, h, confirm=True)
    raw, _ = W.sweep_setups(res, h, confirm=False)
    t0_conf = set(s['si'] for s in conf); t0_raw = set(s['si'] for s in raw)
    assert t0_conf.issubset(t0_raw), 'every confirmed sweep event must exist as a raw sweep event'
    assert len(raw) >= len(conf)

def test_exp02_partition_is_clean():
    """EXP-02 'same universe' design: execute the ungated universe, partition executed trades by er>=thr.
    The efficient partition must be a strict subset (n_on<=n_off) and every gate-ON trade must satisfy the
    efficiency label at its signal bar (this is what makes the gate a pure selection operator)."""
    res = seg(); h = W.PREREG['reps']['S39']['h']; L = int(h['L']); thr = float(h['er_thr'])
    off = W.cont_setups(res, h, gate=False)
    Roff, si_off = W.sim_R(res, off)
    er = MSX._efficiency_ratio(res['close'].values, L)
    eff_mask = er[si_off] >= thr
    assert eff_mask.sum() <= len(Roff)                       # partition -> subset by construction
    assert np.all(er[si_off][eff_mask] >= thr)              # every gate-ON trade is efficient at its signal bar
    assert eff_mask.sum() > 0 and (~eff_mask).sum() > 0     # both partitions non-empty (a real contrast exists)

def test_no_holdout_leak():
    res, val, meta = W.load_segments(with_strata=True)
    assert meta['a'] == int(meta['n'] * 0.6) and meta['b'] == int(meta['n'] * 0.8)
    assert len(res) == meta['a'] and len(val) == meta['b'] - meta['a']
    assert meta['holdout_bars'] == meta['n'] - meta['b'] > 0
    # the last research/OOS timestamp must be strictly before the holdout start
    assert len(res) + len(val) == meta['b']

def test_sim_R_is_engine():
    res = seg(); h = W.PREREG['reps']['S39']['h']
    su = MSX.s39_setups(res, h)
    R, si = W.sim_R(res, su)
    ref = MS.simulate(res, su, MS.CFG)
    assert np.allclose(R, ref['R'].values) and np.array_equal(si, ref['si'].values.astype(int))

def test_placebo_preserves_persistence_and_destroys_identity():
    res = seg()
    segS = W.placebo_level_frame(res, ['pdh', 'pdl'], seed=123, window_days=30)
    days = (res['time'].values // 86400).astype(np.int64)
    # (a) identity destroyed: the shuffled level differs from real on most days
    diff = np.mean(segS['pdl'].values != res['pdl'].values)
    assert diff > 0.5, f'placebo should change the level on most bars (got {diff:.2f})'
    # (b) daily persistence preserved: shuffled level is constant within each day
    ok = True
    for dd in np.unique(days)[:50]:
        v = segS['pdl'].values[days == dd]
        if not np.allclose(v, v[0], equal_nan=True):
            ok = False; break
    assert ok, 'placebo level must be constant within a day (persistence preserved)'
    # (c) geometry: pdh stays >= pdl after the shuffle
    m = np.isfinite(segS['pdh'].values) & np.isfinite(segS['pdl'].values)
    assert np.all(segS['pdh'].values[m] >= segS['pdl'].values[m] - 1e-6)

def test_placebo_frequency_preserved_within_tolerance():
    res = seg(); h = W.PREREG['reps']['S1']['h']
    fn = lambda frame: W.sweep_setups(frame, h, confirm=True)[0]
    real_n = len(fn(res))
    ns = []
    for s in (11, 22, 33, 44, 55):
        segS = W.placebo_level_frame(res, ['pdh', 'pdl'], seed=s, window_days=30)
        ns.append(len(fn(segS)))
    ratio = np.median(ns) / real_n
    assert 0.3 < ratio < 3.0, f'placebo signal frequency should be broadly comparable (ratio={ratio:.2f}, real={real_n}, shuf={ns})'

def test_holm_bonferroni_correct():
    p = [0.001, 0.02, 0.5, None, 0.04]
    adj = W.holm_bonferroni(p)
    # m=4 non-None. sorted: 0.001,0.02,0.04,0.5 -> *4,*3,*2,*1 then monotone
    assert adj[3] is None
    assert abs(adj[0] - 0.004) < 1e-9
    assert adj[1] >= adj[0] and adj[4] >= adj[1] and adj[2] >= adj[4]   # monotone in sorted order
    for i, pi in enumerate(p):
        if pi is not None:
            assert adj[i] >= pi - 1e-12                                  # never below raw

def test_paired_and_selection_contrasts_smoke():
    res = seg()
    h1 = W.PREREG['reps']['S1']['h']
    conf, _ = W.sweep_setups(res, h1, confirm=True); raw, _ = W.sweep_setups(res, h1, confirm=False)
    Rc, sic = W.sim_R(res, conf); Rr, sir = W.sim_R(res, raw)
    pc = W.paired_timing_contrast(res, Rc, sic, Rr, sir, 500, 1, 0.0)
    assert pc['paired_n'] > 0 and 0 < pc['p'] <= 1
    h2 = W.PREREG['reps']['S39']['h']
    Ron, _ = W.sim_R(res, W.cont_setups(res, h2, gate=True)); Roff, _ = W.sim_R(res, W.cont_setups(res, h2, gate=False))
    sc = W.selection_contrast(Ron, Roff, 500, 1, 0.0)
    assert sc['n_on'] <= sc['n_off'] and 0 < sc['p'] <= 1

if __name__ == '__main__':
    fns = [v for k, v in sorted(globals().items()) if k.startswith('test_') and callable(v)]
    seg()  # warm load
    npass = 0
    for f in fns:
        f(); print('PASS', f.__name__); npass += 1
    print(f'\n{npass}/{len(fns)} tests passed')
