"""F6.2 — suportul de drift în generator (verificări deterministe).

Bateria completă (regimuri de drift × celule × ~1000 serii) e în `F6_2_CALIBRATION_RECORD.json`;
aici doar proprietățile deterministe ale generatorului de drift.
"""

import numpy as np
import pytest

from ve.calibration import synthetic_matched_null as SMN

pytestmark = pytest.mark.filterwarnings("ignore")


def test_drift_measured_constant_matches_real():
    """Driftul e calibrat pe real (~0.139 $/bară H1), nu ales arbitrar."""
    assert abs(SMN.DRIFT_H1 - 0.13889) < 1e-4


def test_positive_drift_produces_uptrend():
    df = SMN.generate_price(np.random.default_rng(0), 8000, drift=SMN.DRIFT_H1)
    # panta medie ≈ drift; prețul final peste cel inițial cu marjă mare
    assert df["close"].iloc[-1] > df["close"].iloc[0] + 500


def test_negative_drift_produces_downtrend():
    df = SMN.generate_price(np.random.default_rng(0), 8000, drift=-SMN.DRIFT_H1)
    assert df["close"].iloc[-1] < df["close"].iloc[0] - 500


def test_regime_shift_flips_drift_at_midpoint():
    """Prima jumătate urcă, a doua coboară → maxim aproape de mijloc."""
    n = 8000
    df = SMN.generate_price(np.random.default_rng(0), n, drift=SMN.DRIFT_H1, regime_shift=True)
    c = df["close"].to_numpy()
    peak = int(np.argmax(c))
    assert n * 0.3 < peak < n * 0.7           # vârful în zona de mijloc
    assert c[n // 2] > c[0] and c[-1] < c[n // 2]


def test_drift_has_no_event_conditioned_level_effect():
    """Driftul e o tendință globală: media randamentelor ≈ drift, nu condiționată de eveniment."""
    df = SMN.generate_price(np.random.default_rng(0), 12000, drift=SMN.DRIFT_H1)
    ret = np.diff(df["close"].to_numpy())
    assert abs(ret.mean() - SMN.DRIFT_H1) < 0.2   # media ≈ drift
