"""F5 — `matched_null@v1`: reproducerea calibrării (obs0012) + execuția oficială.

Testele de calibrare/oficial ating date reale de piață (fereastra deschisă).
Holdout NEATINS: dovada e `sealed_window_touched == False`.
"""

import json

import numpy as np
import pytest

from ve import paths
from ve.calibration.reproduce_obs0012 import OBS0012_P, reproduce
from ve.methods import matched_null
from ve.run.f5_run import calibration_bundle, official_bundle
from ve.run.matched_null_official import official_run

pytestmark = pytest.mark.filterwarnings("ignore")


# ───────────────────────── metoda de bază (sintetic) ──────────────────────────

def _cells():
    rng = np.random.default_rng(0)
    return [
        {"cell_id": "A", "ex": rng.normal(-1, 1, 30), "pool": rng.normal(0, 1, 500)},
        {"cell_id": "B", "ex": rng.normal(0, 1, 40), "pool": rng.normal(0, 1, 500)},
    ]


def test_requires_exactly_one_seeding_mode():
    with pytest.raises(ValueError):
        matched_null.run(_cells(), B=100, shared_seed=7, per_cell_seeds={"A": 1, "B": 2})
    with pytest.raises(ValueError):
        matched_null.run(_cells(), B=100)


def test_shared_seed_is_deterministic():
    a = matched_null.run(_cells(), B=500, shared_seed=7)
    b = matched_null.run(_cells(), B=500, shared_seed=7)
    assert [r["p"] for r in a] == [r["p"] for r in b]


def test_per_cell_mode_is_order_independent():
    cells = _cells()
    seeds = {"A": 111, "B": 222}
    forward = matched_null.run(cells, B=500, per_cell_seeds=seeds)
    reverse = matched_null.run(list(reversed(cells)), B=500, per_cell_seeds=seeds)
    fp = {r["cell_id"]: r["p"] for r in forward}
    rp = {r["cell_id"]: r["p"] for r in reverse}
    assert fp == rp


def test_shared_seed_mode_depends_on_order():
    """Modul partajat depinde de ordine — artefact istoric, exact ce reproduce obs."""
    cells = _cells()
    fwd = matched_null.run(cells, B=500, shared_seed=7)
    rev = matched_null.run(list(reversed(cells)), B=500, shared_seed=7)
    fp = {r["cell_id"]: r["p"] for r in fwd}
    rp = {r["cell_id"]: r["p"] for r in rev}
    assert fp != rp  # ordinea contează în modul partajat


def test_left_tail_direction():
    # ex mult sub 0, pool centrat pe 0 => p_left mic
    cells = [{"cell_id": "X", "ex": np.full(20, -5.0), "pool": np.random.default_rng(1).normal(0, 1, 500)}]
    r = matched_null.run(cells, B=1000, shared_seed=1, tail="left")[0]
    assert r["p"] < 0.05


# ───────────────────── CALIBRARE — reproducere exactă obs0012 ─────────────────

def test_calibration_reproduces_obs0012_exactly():
    r = reproduce()
    assert r["all_match"] is True
    assert r["first_divergence"] is None
    by = {c["cell"]: c for c in r["comparison"]}
    for (d, s), obs_p in OBS0012_P.items():
        assert by[f"{d}/{s}"]["ve_p"] == obs_p
    assert r["sealed_window_touched"] is False
    assert r["B"] == 3000 and r["seed"] == 7


def test_calibration_cell_order_matches_obs():
    r = reproduce()
    assert r["cell_order"] == ["up/asia", "down/ny", "down/asia",
                               "up/london", "up/ny", "down/london"]


# ───────────────────── OFICIAL — parametrii DC-0004 ───────────────────────────

def test_official_run_parameters_and_holdout():
    o = official_run()
    assert o["mode"] == "OFFICIAL" and o["official"] is True
    assert o["B"] == 200000
    assert o["method_calibration_status"] == "UNVALIDATED"
    assert o["sealed_window_touched"] is False
    assert len(o["results"]) == 6  # cele 6 celule eligibile n≥25


def test_official_differs_from_obs_within_mc_bounds():
    """Diferența oficial vs obs e mică (B + seed), nu structurală."""
    o = official_run()
    for r in o["results"]:
        d, s = r["cell"].split("/")
        assert abs(r["p"] - OBS0012_P[(d, s)]) < 0.05  # zgomot MC între B/seed, nu diferență de metodă


# ───────────────────── bundle-uri marcate CALIBRATION / OFFICIAL ──────────────

def test_bundles_are_clearly_marked(tmp_path):
    env = dict(runs_dir=tmp_path / "runs", ledger_jsonl=tmp_path / "l.jsonl", ledger_md=tmp_path / "l.md")
    cal = calibration_bundle(**env)
    off = official_bundle(**env)
    cal_m = json.loads((cal / "MANIFEST.json").read_text(encoding="utf-8"))
    off_m = json.loads((off / "MANIFEST.json").read_text(encoding="utf-8"))
    assert cal_m["mode"] == "CALIBRATION" and cal_m["official"] is False
    assert off_m["mode"] == "OFFICIAL" and off_m["official"] is True
    assert "NON-OFFICIAL" in cal_m["warning"]
    assert cal_m["sealed_window_touched"] is False and off_m["sealed_window_touched"] is False


# ───────────────────── invarianții F2 rămân ───────────────────────────────────

def test_method_is_validated_after_ceo_promotion():
    """CEO 2026-07-25: matched_null@v1 promovat la VALIDATED (registru v1.5)."""
    from ve.spec import registry_validator
    reg = registry_validator.load_registry()
    assert reg["test_methods"]["matched_null@v1"]["calibration_status"] == "VALIDATED"
    assert reg["status"] == "PARTIALLY_EXECUTABLE"
