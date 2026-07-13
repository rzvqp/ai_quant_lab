"""Fast calibration REGRESSION guard (not the full gate — that is code/mn_calibration.py with 120 series).
30 synthetic NULL series, B=500: asserts no p==0, mean p near 0.5, and FPR(0.05) not grossly inflated.
Run: venv/Scripts/python tests/test_matched_null_calibration.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))
import numpy as np, synth_price as SP, matched_null as MN

def test_fast_calibration():
    rng = np.random.default_rng(999)
    ps = []
    for s in range(30):
        seed = int(rng.integers(1, 2**31))
        df = SP.gen_series(n=5000, seed=seed, vol_clustering=0.85)
        bars, dirs = SP.exo_signals(df, n_sig=int(rng.integers(120, 260)), seed=seed, side='long')
        su = SP.make_setups(df, bars, dirs, exit_kind='rr', exit_param=2.0)
        rec = MN.matched_null_p(df, su, B=500, seed=seed ^ 0x5eed)
        ps.append(rec['p'])
    ps = np.array(ps)
    assert (ps > 0).all(), "no p may be exactly 0"
    assert 0.30 <= ps.mean() <= 0.70, f"mean p should be ~0.5 under null, got {ps.mean():.3f}"
    fpr05 = float((ps < 0.05).mean())
    assert fpr05 <= 0.20, f"FPR(0.05) grossly inflated: {fpr05:.3f}"
    print(f"PASS test_fast_calibration (n=30, mean_p={ps.mean():.3f}, FPR05={fpr05:.3f}, min_p={ps.min():.4f})")

if __name__ == "__main__":
    test_fast_calibration()
    print("FAST CALIBRATION GUARD PASSED")
