"""Unit tests for the canonical EARLY-TRAP-E1 signal (mandate ALPHA-EARLY-TRAP-E1-CANONICAL-FREEZE-001, S7).
Runnable directly (python test_early_trap_e1.py) or under pytest. Data-backed tests build the frozen
DEV parent once. Pure-rule tests need no data."""
import os, sys
import numpy as np, pandas as pd
SP = os.path.dirname(os.path.abspath(__file__))
if SP not in sys.path: sys.path.insert(0, SP)
import early_trap_e1_signal as S

# ---- pure-rule tests (no data) ----
def test_03_close_below_and_bearish_fires():
    assert S.early_trap_e1_fires(e1_open=100.0, e1_close=98.0, asia_high=99.0) is True

def test_04_close_below_but_bullish_no_signal():
    assert S.early_trap_e1_fires(e1_open=97.0, e1_close=98.0, asia_high=99.0) is False

def test_05_bearish_but_close_above_no_signal():
    assert S.early_trap_e1_fires(e1_open=101.0, e1_close=100.0, asia_high=99.0) is False

def test_06_doji_deterministic_no_signal():
    # close == open -> not a (strict) bearish body -> no fire, deterministically
    assert S.early_trap_e1_fires(e1_open=98.0, e1_close=98.0, asia_high=99.0) is False

def test_07_exact_equality_close_eq_asiahigh_no_signal():
    # close == asia_high -> not strictly below -> no fire
    assert S.early_trap_e1_fires(e1_open=100.0, e1_close=99.0, asia_high=99.0) is False

def test_08_missing_bar_fail_closed():
    # NaN inputs (e.g. missing/incomplete E1 bar) -> fail-closed False
    assert S.early_trap_e1_fires(np.nan, 98.0, 99.0) is False
    assert S.early_trap_e1_fires(100.0, np.nan, 99.0) is False
    assert S.early_trap_e1_fires(100.0, 98.0, np.nan) is False

def test_10_dst_boundary_preserved():
    # summer (DST) vs winter for London/NY; Tokyo has none
    idx = pd.to_datetime([1625000000, 1640000000], unit="s", utc=True)  # 2021-06, 2021-12
    assert str(idx[0].tz_convert("Europe/London").utcoffset()) == "1:00:00"
    assert str(idx[1].tz_convert("Europe/London").utcoffset()) == "0:00:00"
    assert idx[0].tz_convert("America/New_York").utcoffset() != idx[1].tz_convert("America/New_York").utcoffset()
    assert idx[0].tz_convert("Asia/Tokyo").utcoffset() == idx[1].tz_convert("Asia/Tokyo").utcoffset()

# ---- data-backed tests (build frozen parent once) ----
_TFS = None
def _tfs():
    global _TFS
    if _TFS is None: _TFS, _ = S.D.build()
    return _TFS

def test_01_asia_high_known_before_sweep():
    parents, P = S.build_parent(_tfs())
    dt = P["dt"]; uh = dt.hour.to_numpy()
    # every sweep occurs at utc_hour >= 7 (Asia window 00:00-07:00 complete before the sweep)
    assert all(uh[p["sweep_index"]] >= 7 for p in parents)

def test_02_e1_exactly_one_completed_bar_after_sweep():
    episodes, _ = S.evaluate(_tfs())
    assert episodes and all(e["e1_index"] == e["sweep_index"] + 1 for e in episodes)
    # signal_time is E1 close_time; earliest execution strictly after
    assert all(e["earliest_execution_time"] > e["signal_time"] for e in episodes)

def test_09_invalid_session_fail_closed():
    parents, _ = S.build_parent(_tfs())
    # only London / NY / Overlap sweeps become parents; Asia-only or dead hours never do
    assert all(p["session"] in ("LONDON", "NY", "OVERLAP") for p in parents)

def test_11_duplicate_evaluation_same_identity():
    fp1, ep1, _ = S.fingerprints(_tfs())
    fp2, ep2, _ = S.fingerprints(_tfs())
    assert fp1["episode_set_identity"] == fp2["episode_set_identity"]
    assert fp1["implementation_fingerprint"] == fp2["implementation_fingerprint"]
    assert fp1["parent_population_identity"] == fp2["parent_population_identity"]

def test_00_reproduction_exact():
    ok, got, exp, _ = S.reproduction_check(_tfs())
    assert ok, f"reproduction mismatch: got={got} exp={exp}"

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for t in tests:
        try:
            t(); print(f"PASS  {t.__name__}"); passed += 1
        except Exception as e:
            print(f"FAIL  {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
    sys.exit(0 if passed == len(tests) else 1)
