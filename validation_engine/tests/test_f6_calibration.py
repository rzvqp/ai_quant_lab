"""F6 — bateria sintetică de calibrare pentru `matched_null@v1`.

Testul de fidelitate (deterministic) e poarta principală: pipeline-ul sintetic
reproduce EXACT numărătorile reale de evenimente — deci seriile sintetice trec
prin ACEEAȘI cale ca datele reale. Bateria completă (120 serii) rulează separat
și e înregistrată în `F6_CALIBRATION_RECORD.json`; aici se rulează o versiune mică.
"""

import pandas as pd
import pytest

from ve import paths
from ve.calibration import synthetic_matched_null as SMN
from ve.data.access_journal import AccessJournal
from ve.data.sources import load_open_window
from ve.data import sealing

pytestmark = pytest.mark.filterwarnings("ignore")
H1_HASH = "5ff7420ac6698e639ecd4f7afa5c526e74ca99d12ef34fb7df8149ff18868baa"


def test_synthetic_pipeline_reproduces_real_event_counts():
    """FIDELITATE: pipeline-ul sintetic pe date REALE dă exact 135/34/42/114/40/47."""
    s = load_open_window("OANDA_XAUUSD_H1@v1", H1_HASH, 0, sealing.boundary_epoch() - 1,
                         "[)", AccessJournal())
    df = pd.DataFrame({"time": s.time, "open": s.open, "high": s.high,
                       "low": s.low, "close": s.close, "volume": s.volume})
    counts = {f"{d}/{ss}": len(c["ex"]) for (d, ss), c in SMN.pipeline_cells(df).items()}
    assert counts["up/asia"] == 135 and counts["up/london"] == 34 and counts["up/ny"] == 42
    assert counts["down/asia"] == 114 and counts["down/london"] == 40 and counts["down/ny"] == 47


def test_series_are_price_at_real_scale():
    """Seriile sunt PREȚ (nu R), la scala XAUUSD — cauza eșecului istoric evitată."""
    import numpy as np
    df = SMN.generate_price(np.random.default_rng(1), 2000)
    assert df["close"].mean() > 1000            # scală de preț, nu ±1 (R)
    # OHLC valid
    assert (df["high"] >= df[["open", "close"]].max(axis=1)).all()
    assert (df["low"] <= df[["open", "close"]].min(axis=1)).all()


def test_reproducibility_same_seed_same_p():
    a = SMN.one_p(777, 8000, 2.0, 500, ("up", "asia"))
    b = SMN.one_p(777, 8000, 2.0, 500, ("up", "asia"))
    assert a == b


def test_small_battery_runs_and_power_increases():
    """Versiune mică a bateriei: structură + puterea crește cu edge-ul injectat."""
    rec = SMN.run_battery(n_series=20, n_bars=8000, B=400, deltas=(0.0, 8.0))
    assert set(rec) >= {"null", "power_curve", "reproducibility", "verdict"}
    assert rec["reproducibility"]["identical"] is True
    # la n mic, uniformitatea e zgomotoasă; verificăm doar semnalul robust de putere
    assert rec["power_curve"][-1]["reject_rate"] > rec["power_curve"][0]["reject_rate"]


def test_ks_and_wilson_helpers():
    import numpy as np
    u = np.linspace(0.01, 0.99, 200)     # aproape uniform
    d, p = SMN.ks_uniform(u)
    assert p > 0.05
    lo, hi = SMN.wilson_ci(5, 100)
    assert lo < 0.05 < hi
