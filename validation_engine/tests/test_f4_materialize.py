"""F4 — stratul de date + populație + variabile. Fereastra DESCHISĂ; holdout neatins.

Aceste teste ating date reale de piață (fereastra deschisă) — sunt marcate `data`.
Holdout-ul (post 2025-10-23T09:15:00Z) nu este niciodată încărcat: dovada e
`max_ts_read < granița sigilată` în fiecare test.
"""

import copy
import json
from pathlib import Path

import pytest

from ve import paths
from ve.data import sealing
from ve.data.access_journal import AccessJournal
from ve.data.integrity import DataIntegrityError, resolve_and_verify
from ve.data.sources import DataLoadError, load_open_window
from ve.run.materializer import materialize_run

FIX = paths.VE_ROOT / "tests" / "fixtures"
DEV = FIX / "dev_spec_open_window.json"
H1_HASH = "5ff7420ac6698e639ecd4f7afa5c526e74ca99d12ef34fb7df8149ff18868baa"

pytestmark = pytest.mark.filterwarnings("ignore")


@pytest.fixture
def env(tmp_path):
    return {"runs_dir": tmp_path / "runs",
            "ledger_jsonl": tmp_path / "l.jsonl", "ledger_md": tmp_path / "l.md"}


def _mat(env, spec_path=DEV, rid="VE-MAT-T"):
    return materialize_run(spec_path, run_id=rid, timestamp="2026-07-25T00:00:00Z", **env)


# ───────────────────────── materializarea reușită ─────────────────────────────

def test_materialization_builds_population(env):
    r = _mat(env)
    assert r.status == "MATERIALIZED"
    pop = json.loads((r.bundle_dir / "POPULATION.json").read_text(encoding="utf-8"))
    assert pop["n_after_cooldown"] > 0
    assert "per_criterion_denominator" in pop


def test_empirical_family_drops_low_support_cells(env):
    """Familia empirică n≥25 exclude celulele cu suport mic (ex. 'late')."""
    r = _mat(env)
    fam = json.loads((r.bundle_dir / "REALIZED_FAMILY.json").read_text(encoding="utf-8"))
    assert fam["eligibility_rule"] == {"field": "n", "op": ">=", "value": 25}
    # fiecare celulă eligibilă are n≥25; cele excluse au n<25
    for cell in fam["eligible_cells"]:
        assert fam["per_cell"][cell]["n"] >= 25
    for d in fam["dropped_cells"]:
        assert d["n"] < 25
    assert fam["m_realized"] == len(fam["eligible_cells"])


def test_variables_materialized_without_statistics(env):
    r = _mat(env)
    mat = json.loads((r.bundle_dir / "MATERIALIZATION.json").read_text(encoding="utf-8"))
    for vid, s in mat.items():
        assert "materialized" in s or "note" in s
        # niciun câmp de statistică/rezultat
        assert not any(k in s for k in ("p_value", "mean", "p_hat", "effect", "statistic"))


# ───────────────────── dovada că holdout-ul NU e atins ────────────────────────

def test_holdout_is_never_touched(env):
    r = _mat(env)
    assert r.sealed_window_touched is False
    aj = json.loads((r.bundle_dir / "ACCESS_JOURNAL.json").read_text(encoding="utf-8"))
    for src, max_ts in aj["max_ts_by_source"].items():
        assert max_ts < sealing.SEALED_BOUNDARY_EPOCH, src
    assert aj["sealed_window_touched"] is False


def test_spec_targeting_holdout_halts(env):
    """O fereastră care atinge granița sigilată se oprește; F4 nu deschide holdout-ul.

    `required=true` (autorizat) → trece de verificarea E5 din F2, deci oprirea vine de
    la refuzul F4 la nivel de strat de date (assert_open_window)."""
    spec = json.loads(DEV.read_text(encoding="utf-8"))
    spec["population"]["window"]["end"] = "2026-01-01T00:00:00Z"  # în holdout
    spec["authorization"] = {"required": True, "ceo_token_id": "FIXTURE", "resource_class": "sealed_holdout"}
    p = env["runs_dir"].parent / "holdout_spec.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(spec), encoding="utf-8")
    r = _mat(env, spec_path=p, rid="VE-MAT-HO")
    assert r.status == "HALTED"
    assert "Holdout" in (r.halt_reason or "")
    assert r.sealed_window_touched is False
    assert (r.bundle_dir / "MANIFEST.json").exists()


def test_loader_stops_at_boundary():
    """Loader-ul se oprește la graniță: max_ts < boundary, chiar cerând tot deschisul."""
    j = AccessJournal()
    s = load_open_window("OANDA_XAUUSD_H1@v1", H1_HASH, 0,
                         sealing.boundary_epoch() - 1, "[)", j)
    assert max(s.time) < sealing.SEALED_BOUNDARY_EPOCH
    assert len(s) == 16623   # exact barele deschise H1


# ───────────────────────── fail-closed pe anomalii ────────────────────────────

def test_hash_mismatch_halts(env):
    spec = json.loads(DEV.read_text(encoding="utf-8"))
    spec["data"][0]["sha256"] = "0" * 64
    p = env["runs_dir"].parent / "badhash.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(spec), encoding="utf-8")
    r = _mat(env, spec_path=p, rid="VE-MAT-BH")
    # hash declarat ≠ hash înregistrat: se oprește (la F2, ca E2 de vocabular, sau la F4)
    assert r.status == "HALTED"


def test_integrity_direct_hash_mismatch():
    with pytest.raises(DataIntegrityError):
        resolve_and_verify("OANDA_XAUUSD_H1@v1", "0" * 64)


def test_uncovered_window_halts(env):
    spec = json.loads(DEV.read_text(encoding="utf-8"))
    spec["population"]["window"] = {"start": "2019-01-01T00:00:00Z",
                                    "end": "2019-02-01T00:00:00Z", "bounds": "[)"}
    p = env["runs_dir"].parent / "uncov.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(spec), encoding="utf-8")
    r = _mat(env, spec_path=p, rid="VE-MAT-UC")
    assert r.status == "HALTED"   # nicio bară în fereastră


# ─────────────────── fără execuție de metode / fără p-values ──────────────────

def test_no_method_executed(env):
    r = _mat(env)
    man = json.loads((r.bundle_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    assert man["execution"]["methods_executed"] == 0


def test_no_pvalue_anywhere_in_bundle(env):
    """Artefactele PRODUSE de F4 nu conțin p-values/efecte/corecții.

    Se scanează doar ieșirile F4 (populație, familie, materializare, manifest), NU
    SPEC_RECEIVED (care e o copie a intrării și conține referințe declarate ca `p_hat`
    ca ținte de membru — acelea sunt vocabular de specificație, nu rezultate calculate).
    """
    r = _mat(env)
    outputs = ("POPULATION.json", "REALIZED_FAMILY.json", "MATERIALIZATION.json",
               "MANIFEST.json", "ACCESS_JOURNAL.json")
    blob = ""
    for name in outputs:
        f = r.bundle_dir / name
        if f.exists():
            blob += f.read_text(encoding="utf-8").lower()
    for banned in ("p_value", "p_hat", "significant", "corrected_threshold", "bonferroni_threshold"):
        assert banned not in blob, banned


# ───────────────── invarianții F2 rămân + integritate ─────────────────────────

def test_f4_leaves_registry_unexecutable(env):
    from ve.spec import registry_validator
    _mat(env)
    reg = registry_validator.load_registry()
    # Statusul e stabilit de CEO (PARTIALLY_EXECUTABLE din 2026-07-25); F4 nu îl modifică.
    assert reg["status"] == "PARTIALLY_EXECUTABLE"
    # F4 nu modifică niciun status de calibrare: matched_null@v1 rămâne VALIDATED (CEO), restul UNVALIDATED.
    for s in ("test_methods", "correction_methods"):
        for mid, m in reg[s].items():
            expected = "VALIDATED" if mid == "matched_null@v1" else "UNVALIDATED"
            assert m["calibration_status"] == expected, mid


def test_external_writes_zero(env):
    r = _mat(env)
    assert r.external_writes == 0
