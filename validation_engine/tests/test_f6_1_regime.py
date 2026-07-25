"""F6.1 — calibrarea sub structură de volatilitate realistă (nulul principal al lab).

Verificări deterministe ale generatorului (vol pe sesiune + cozi grele) + o versiune
mică a bateriei. Bateria completă (120 serii × 3 regimuri) e în `F6_1_CALIBRATION_RECORD.json`.
"""

import numpy as np
import pytest

from ve.calibration import synthetic_matched_null as SMN

pytestmark = pytest.mark.filterwarnings("ignore")


def test_session_vol_produces_differentiated_volatility():
    """NY vol 2.5x → barele NY au deviație a randamentului mai mare (determinist)."""
    df = SMN.generate_price(np.random.default_rng(0), 24000, session_vol={"ny": 2.5})
    hour = (df["time"].to_numpy() % 86400) // 3600
    ret = np.diff(df["close"].to_numpy())
    ny = ret[np.isin(hour[1:], range(13, 21))]
    asia = ret[np.isin(hour[1:], range(0, 8))]
    assert ny.std() > 2.0 * asia.std()   # ~2.5x, cu marjă


def test_heavy_tails_increase_kurtosis():
    """Student-t(4) → kurtoză mult peste normal (cozi grele, determinist)."""
    rng = np.random.default_rng(0)
    normal = np.diff(SMN.generate_price(rng, 30000)["close"].to_numpy())
    heavy = np.diff(SMN.generate_price(rng, 30000, tail_df=4.0)["close"].to_numpy())
    def kurt(x):
        z = (x - x.mean()) / x.std()
        return (z ** 4).mean()
    assert kurt(heavy) > kurt(normal) + 1.0   # normal~3; t(4) mult mai mare


def test_ny_high_vol_yields_enough_ny_events():
    """Vol NY mai mare mută breach-urile în NY → celula NY atinge n≥25 (condiție de test)."""
    df = SMN.generate_price(np.random.default_rng(3), 12000, session_vol={"ny": 2.5})
    cells = SMN.pipeline_cells(df)
    assert ("up", "ny") in cells or ("down", "ny") in cells


def test_no_level_effect_returns_are_mean_zero():
    """Sub structura de vol pură, randamentele au medie ≈ 0 în fiecare sesiune."""
    df = SMN.generate_price(np.random.default_rng(0), 24000, session_vol={"ny": 2.5}, tail_df=4.0)
    hour = (df["time"].to_numpy() % 86400) // 3600
    ret = np.diff(df["close"].to_numpy())
    for lo, hi in [(0, 8), (13, 21)]:
        seg = ret[np.isin(hour[1:], range(lo, hi))]
        assert abs(seg.mean()) < 0.5   # ≈0 față de σ~5-13


def test_small_f61_battery_structure_and_no_gross_rejection():
    rec = SMN.run_f61(n_series=20, n_bars=12000, B=400)
    assert set(rec) >= {"null_regimes", "power_under_ny_high_vol", "verdict"}
    assert len(rec["null_regimes"]) == 3
    # sub structura de vol pură, FPR nu trebuie să explodeze (prag generos la n mic)
    for r in rec["null_regimes"]:
        assert r["fpr"] < 0.25, r["regime"]
