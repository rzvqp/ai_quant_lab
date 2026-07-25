"""F6.3 — suportul de reversie (AR1) în generator (verificări deterministe).

Bateria completă (curbă de sensibilitate + G-FPR + G-PLACEBO) e în
`F6_3_CALIBRATION_RECORD.json`; aici doar proprietățile deterministe.
"""

import numpy as np
import pytest

from ve.calibration import synthetic_matched_null as SMN

pytestmark = pytest.mark.filterwarnings("ignore")


def test_ar1_real_measured():
    assert abs(SMN.AR1_REAL - (-0.0182)) < 1e-3


def test_negative_ar1_produces_negative_lag1_autocorrelation():
    """φ<0 în generator → autocorelație lag-1 negativă a randamentelor (reversie)."""
    df = SMN.generate_price(np.random.default_rng(0), 20000, ar1=-0.3)
    r = np.diff(df["close"].to_numpy())
    lag1 = np.corrcoef(r[:-1], r[1:])[0, 1]
    assert lag1 < -0.15          # reversie clară (față de ~0 la random-walk)


def test_zero_ar1_is_uncorrelated():
    df = SMN.generate_price(np.random.default_rng(0), 20000, ar1=0.0)
    r = np.diff(df["close"].to_numpy())
    assert abs(np.corrcoef(r[:-1], r[1:])[0, 1]) < 0.05


def test_ar1_preserves_scale():
    """AR(1) păstrează varianța unitară a componentei de noise (scală neschimbată)."""
    a = SMN.generate_price(np.random.default_rng(1), 12000, ar1=0.0)
    b = SMN.generate_price(np.random.default_rng(1), 12000, ar1=-0.3)
    ra = np.diff(a["close"].to_numpy()); rb = np.diff(b["close"].to_numpy())
    assert 0.7 < rb.std() / ra.std() < 1.3   # aceeași scală aproximativ
