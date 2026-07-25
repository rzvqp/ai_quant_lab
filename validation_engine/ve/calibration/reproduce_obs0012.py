"""CALIBRATION ONLY — reproduce EXACT obs0012 (matched-null, K6) pe fereastra deschisă.

NON-OFFICIAL. Rulează pe intrările materializate în F4. Reconstruiește ordinea
celulelor și consumul generatorului EXACT ca `obs0012_reject_allcells_null.py`:
un singur `default_rng(7)`, B=3000, tail=left, pool per sesiune. Criteriul de
acceptare: reproducerea valorilor p raportate de obs0012, la precizia scriptului.

Acesta NU este un rezultat oficial de protocol; verifică doar fidelitatea metodei.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..data import sealing
from ..data.access_journal import AccessJournal
from ..data.sources import load_open_window
from ..methods import matched_null
from ..variables import materialize as var_mat

H1 = "OANDA_XAUUSD_H1@v1"
H1_HASH = "5ff7420ac6698e639ecd4f7afa5c526e74ca99d12ef34fb7df8149ff18868baa"

# Valorile raportate de obs0012 (K=6), la precizia scriptului (4 zecimale).
OBS0012_P = {
    ("up", "ny"): 0.0253, ("down", "london"): 0.3620, ("down", "asia"): 0.3640,
    ("down", "ny"): 0.4123, ("up", "london"): 0.6570, ("up", "asia"): 0.9593,
}
SESSIONS_UTC = [
    {"name": "asia", "start_utc": "00:00:00", "end_utc": "08:00:00"},
    {"name": "london", "start_utc": "08:00:00", "end_utc": "13:00:00"},
    {"name": "ny", "start_utc": "13:00:00", "end_utc": "21:00:00"},
    {"name": "late", "start_utc": "21:00:00", "end_utc": "24:00:00"},
]
K = 6
B = 3000
SEED = 7


def _load_frame():
    j = AccessJournal()
    s = load_open_window(H1, H1_HASH, 0, sealing.boundary_epoch() - 1, "[)", j)
    base = var_mat.series_to_frame(s)
    # variabile ca în DC-0004: pdh/pdl din H1 pe zi UTC, session UTC, forward K6, baseline per sesiune
    variables = [
        {"id": "pdh", "primitive": "prior_period_extreme@v1",
         "params": {"source_id": H1, "extreme": "high", "periods_back": 1,
                    "availability_rule": "next_bar_open", "availability_delay_seconds": 0},
         "availability": {"anchor": "event_time", "offset_bars": -1, "source_id": H1}, "role": "exposure"},
        {"id": "pdl", "primitive": "prior_period_extreme@v1",
         "params": {"source_id": H1, "extreme": "low", "periods_back": 1,
                    "availability_rule": "next_bar_open", "availability_delay_seconds": 0},
         "availability": {"anchor": "event_time", "offset_bars": -1, "source_id": H1}, "role": "exposure"},
        {"id": "session", "primitive": "session_label@v1", "params": {"boundaries": SESSIONS_UTC},
         "availability": {"anchor": "event_time", "offset_bars": 0, "source_id": H1}, "role": "stratifier"},
        {"id": "fwd", "primitive": "forward_return@v1",
         "params": {"source_id": H1, "horizon_bars": K, "basis": "close_to_close", "units": "price"},
         "availability": {"anchor": "event_time", "offset_bars": K, "source_id": H1}, "role": "outcome"},
    ]
    vals, _ = var_mat.materialize(variables, base, {}, base_source_id=H1)
    base = base.copy()
    base["pdh"] = vals["pdh"].values
    base["pdl"] = vals["pdl"].values
    base["session"] = vals["session"].values
    base["fwd"] = vals["fwd"].values
    return base, j


def _build_cells_obs_order(base: pd.DataFrame):
    """Reconstruiește dicționarul `rej` în ordinea de inserție a obs0012."""
    high = base["high"].to_numpy(); low = base["low"].to_numpy()
    close = base["close"].to_numpy(); sess = base["session"].to_numpy()
    rej = {}  # (dir, session) -> list of row positions, în ordinea obs
    for _day, g in base.groupby("day", sort=True):
        ph = g["pdh"].iloc[0]; pl = g["pdl"].iloc[0]
        idx = list(g.index)
        if ph == ph:  # not NaN
            up = next((i for i in idx if high[i] > ph), None)
            if up is not None and close[up] < ph:
                rej.setdefault(("up", sess[up]), []).append(up)
        if pl == pl:
            dn = next((i for i in idx if low[i] < pl), None)
            if dn is not None and close[dn] > pl:
                rej.setdefault(("down", sess[dn]), []).append(dn)
    return rej


def build_open_cells():
    """Construiește celulele eligibile (n≥25) din intrările F4 (fereastra deschisă).

    Întoarce (cells_by_key, obs_order, journal). Ex/pool sunt identice indiferent de
    ordine; ordinea de iterație (obs vs. spec) e alegerea apelantului.
    """
    base, journal = _load_frame()
    fwd = base["fwd"].to_numpy()
    sess = base["session"].to_numpy()

    rej = _build_cells_obs_order(base)
    session_base = {}
    for s in ("asia", "london", "ny", "late"):
        vals = fwd[(sess == s) & ~np.isnan(fwd)]
        session_base[s] = float(vals.mean()) if len(vals) else float("nan")

    obs_order = [(d, s) for (d, s) in rej if len(rej[(d, s)]) >= 25]
    cells_by_key = {}
    for (d, s) in obs_order:
        sgn = 1.0 if d == "up" else -1.0
        b = session_base[s]
        ex = np.array([sgn * (fwd[i] - b) for i in rej[(d, s)] if not np.isnan(fwd[i])])
        pool_idx = np.where((sess == s) & ~np.isnan(fwd))[0]
        pool = sgn * (fwd[pool_idx] - b)
        cells_by_key[(d, s)] = {"cell_id": f"{d}/{s}", "dir": d, "session": s, "ex": ex, "pool": pool}
    return cells_by_key, obs_order, journal


def reproduce() -> dict:
    cells_by_key, obs_order, journal = build_open_cells()
    cells = [cells_by_key[k] for k in obs_order]  # ORDINEA obs
    # mod REPRODUCERE: generator partajat seed=7, consumat în ordinea obs (artefact istoric)
    results = matched_null.run(cells, B=B, tail="left", statistic="mean", shared_seed=SEED)

    # comparație cu obs0012 (4 zecimale)
    comparison = []
    first_divergence = None
    for r, c in zip(results, cells):
        key = (c["dir"], c["session"])
        obs_p = OBS0012_P.get(key)
        ve_p = round(r["p"], 4)
        match = (obs_p is not None and abs(ve_p - obs_p) < 5e-5)
        comparison.append({"cell": c["cell_id"], "n": r["n"], "ve_p": ve_p,
                           "obs_p": obs_p, "match": match})
        if not match and first_divergence is None:
            first_divergence = {"cell": c["cell_id"], "ve_p": ve_p, "obs_p": obs_p}

    return {
        "mode": "CALIBRATION",
        "official": False,
        "B": B, "seed": SEED, "tail": "left",
        "cell_order": [c["cell_id"] for c in cells],
        "comparison": comparison,
        "all_match": all(x["match"] for x in comparison) and len(comparison) == len(OBS0012_P),
        "first_divergence": first_divergence,
        "max_ts_read": journal.max_ts_by_source(),
        "sealed_window_touched": journal.sealed_window_touched(),
    }
