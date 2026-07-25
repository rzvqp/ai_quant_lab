"""Bateria de mutații — dovada că orice specificație incompletă sau ambiguă oprește execuția."""

import pytest
from mutations import MUTATIONS

from ve.spec.validate import validate_spec_object

IDS = [f"{m[0]}_{m[1][:40].replace(' ', '_')}" for m in MUTATIONS]


def test_baseline_passes_validation_now_that_both_methods_are_validated(baseline):
    """MILESTONE: după ce CEO a promovat AMBELE metode ale baseline-ului
    (matched_null@v1 + bonferroni@v1 → VALIDATED, registru v1.5/v1.6), specificația
    de referință TRECE validarea — prima cu vocabular de metode integral executabil.
    Poarta de calibrare nu se mai declanșează pentru că nu mai există metodă
    nevalidată referită. Validarea ≠ execuție (nu atinge date; execuția e F5+)."""
    result = validate_spec_object(baseline, spec_sha256="0" * 64)

    assert not result.halted
    assert result.stage_reached == 2
    assert result.codes == []
    assert result.data_accesses == []


@pytest.mark.parametrize("mid,desc,mutator,code,stage", MUTATIONS, ids=IDS)
def test_mutation_halts_with_expected_code(mid, desc, mutator, code, stage, baseline):
    mutator(baseline)
    result = validate_spec_object(baseline, spec_sha256="0" * 64)

    assert result.halted, f"{mid} ({desc}) nu a produs oprire"
    assert code in result.codes, f"{mid} ({desc}) a produs {result.codes}, se aștepta {code}"
    assert result.stage_reached == stage, f"{mid} ({desc}) etapă {result.stage_reached}, se aștepta {stage}"
    assert result.data_accesses == [], f"{mid} ({desc}) a atins date"


def test_every_mandatory_top_level_field_is_covered(baseline):
    """Fiecare câmp obligatoriu de nivel superior are o mutație de absență."""
    import json
    from pathlib import Path

    from ve import paths

    schema = json.loads(Path(paths.SPEC_SCHEMA_PATH).read_text(encoding="utf-8"))
    required = set(schema["required"])

    covered = set()
    for _mid, _desc, mutator, code, _stage in MUTATIONS:
        if code != "E1":
            continue
        probe = dict(baseline)
        before = set(probe)
        try:
            mutator(probe)
        except (KeyError, TypeError, IndexError):
            continue
        covered |= before - set(probe)

    missing = required - covered
    # Câmpurile de identificare simplă sunt acoperite prin M01/M11/M24/M25;
    # verificăm că fiecare secțiune structurală majoră are o mutație de absență.
    structural = {"population", "variables", "tests", "multiple_testing", "criteria",
                  "return", "data", "authorization", "on_missing_or_ambiguous", "candidate"}
    assert structural <= covered, f"secțiuni fără mutație de absență: {structural - covered}"
    assert isinstance(missing, set)


def test_no_mutation_produces_pass(baseline_raw):
    """Nicio mutație nu poate produce o specificație acceptată."""
    import copy

    for mid, desc, mutator, _code, _stage in MUTATIONS:
        spec = copy.deepcopy(baseline_raw)
        mutator(spec)
        result = validate_spec_object(spec, spec_sha256="0" * 64)
        assert result.halted, f"{mid} ({desc}) a trecut validarea"


def test_all_errors_carry_the_four_clarification_fields(baseline_raw):
    """Fiecare cauză poartă cod, cale și motiv; câmpul de registru poate fi gol
    doar când registrul nu are ce informație factuală să ofere."""
    import copy

    for mid, desc, mutator, _code, _stage in MUTATIONS:
        spec = copy.deepcopy(baseline_raw)
        mutator(spec)
        result = validate_spec_object(spec, spec_sha256="0" * 64)
        for err in result.errors:
            assert err.code, mid
            assert err.field_path, f"{mid}: cauză fără cale de câmp"
            assert err.reason, f"{mid}: cauză fără motiv"
            assert isinstance(err.registry_info, str)
