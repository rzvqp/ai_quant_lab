"""Dovada că validarea nu atinge date — și că detectorul care o dovedește funcționează.

Un test de tipul „nu s-au înregistrat accesări" este vacuu dacă detectorul e stricat.
De aceea suita conține control pozitiv (detectorul PRINDE o deschidere de fișier de
date) și control de interdicție (garda ABANDONEAZĂ operațiunea), înainte de a
folosi absența accesărilor ca dovadă.
"""

import copy
import json

import pytest
from mutations import MUTATIONS

from ve import paths
from ve.audit import access_audit
from ve.errors import NO_DATA_ACCESS_CODES
from ve.spec import registry_validator, schema_validator
from ve.spec.validate import validate_spec_file, validate_spec_object

IDS = [f"{m[0]}_{m[1][:40].replace(' ', '_')}" for m in MUTATIONS]


# ───────────────────────── control pozitiv al detectorului ────────────────────

def test_detector_catches_a_data_file_open(tmp_path, monkeypatch):
    """Fără această verificare, orice listă goală de accesări ar fi lipsită de valoare."""
    fake_data = tmp_path / "market"
    fake_data.mkdir()
    target = fake_data / "OANDA_FAKE_M15.csv"
    target.write_text("time,open\n1,2\n", encoding="utf-8")
    monkeypatch.setenv("AI_QUANT_DATA_DIR", str(fake_data))

    with access_audit.recording(forbid_data=False) as record:
        with open(target, "r", encoding="utf-8") as fh:
            fh.read()

    assert len(record.data_accesses) == 1
    assert record.data_accesses[0].endswith("OANDA_FAKE_M15.csv")


def test_guard_aborts_a_forbidden_data_open(tmp_path, monkeypatch):
    fake_data = tmp_path / "market"
    fake_data.mkdir()
    target = fake_data / "OANDA_FAKE_H1.csv"
    target.write_text("time,open\n1,2\n", encoding="utf-8")
    monkeypatch.setenv("AI_QUANT_DATA_DIR", str(fake_data))

    with access_audit.recording(forbid_data=True):
        with pytest.raises(access_audit.DataAccessViolation):
            open(target, "r", encoding="utf-8").close()


def test_detector_ignores_non_data_files(tmp_path):
    other = tmp_path / "not_market.txt"
    other.write_text("x", encoding="utf-8")
    with access_audit.recording(forbid_data=True) as record:
        other.read_text(encoding="utf-8")
    assert record.data_accesses == []
    assert any(p.endswith("not_market.txt") for p in record.opened)


def test_real_data_root_is_guarded_even_without_env(monkeypatch):
    monkeypatch.delenv("AI_QUANT_DATA_DIR", raising=False)
    roots = [str(r) for r in paths.data_roots()]
    assert any(r.replace("\\", "/").endswith("/data") for r in roots)


# ───────────────────────── dovada pe bateria de mutații ───────────────────────

@pytest.mark.parametrize("mid,desc,mutator,code,stage", MUTATIONS, ids=IDS)
def test_mutation_touches_no_data(mid, desc, mutator, code, stage, baseline):
    mutator(baseline)
    result = validate_spec_object(baseline, spec_sha256="0" * 64)
    assert result.data_accesses == [], f"{mid} ({desc}) a atins date: {result.data_accesses}"


def test_e1_e2_e3_never_touch_data(baseline_raw):
    """Cerința explicită a contractului: la E1-E3, zero accesări de date."""
    checked = {c: 0 for c in NO_DATA_ACCESS_CODES}
    for mid, desc, mutator, _code, _stage in MUTATIONS:
        spec = copy.deepcopy(baseline_raw)
        mutator(spec)
        result = validate_spec_object(spec, spec_sha256="0" * 64)
        codes = set(result.codes)
        if codes & NO_DATA_ACCESS_CODES:
            assert result.data_accesses == [], f"{mid} ({desc})"
            for c in codes & NO_DATA_ACCESS_CODES:
                checked[c] += 1
    for code, count in checked.items():
        assert count > 0, f"niciun caz observat pentru {code}"


def test_validation_from_file_touches_no_data(tmp_path, baseline):
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(baseline), encoding="utf-8")
    result = validate_spec_file(p)
    assert result.data_accesses == []
    assert result.spec_sha256 and len(result.spec_sha256) == 64


def test_opened_files_are_only_spec_schema_and_registry(tmp_path, baseline):
    """Cu memoriile golite, se vede exact ce deschide validarea."""
    schema_validator.load_schema.cache_clear()
    schema_validator._validator.cache_clear()
    registry_validator.load_registry.cache_clear()
    registry_validator.registry_domains_are_parseable.cache_clear()

    p = tmp_path / "spec.json"
    p.write_text(json.dumps(baseline), encoding="utf-8")
    result = validate_spec_file(p)

    opened = {o.replace("\\", "/") for o in result.files_opened}
    assert any(o.endswith("SPEC_SCHEMA_v1.0.json") for o in opened)
    assert any(o.endswith("capabilities.json") for o in opened)
    assert any(o.endswith("spec.json") for o in opened)
    assert result.data_accesses == []
    for o in opened:
        assert "/data/market/" not in o


def test_yaml_spec_is_refused_without_touching_data(tmp_path):
    p = tmp_path / "spec.yaml"
    p.write_text("spec_id: X\n", encoding="utf-8")
    result = validate_spec_file(p)
    assert result.halted
    assert result.codes == ["E3"]
    assert result.stage_reached == 0
    assert result.data_accesses == []
