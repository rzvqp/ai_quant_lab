"""Cererea de clarificare: patru câmpuri, zero recomandări."""

import copy

import pytest
from mutations import MUTATIONS

from ve import clarification
from ve.spec.validate import validate_spec_object

FIXED_TS = "2026-07-24T00:00:00Z"

#: Vocabular care ar transforma o constatare într-o sugestie. Contractul §1.7
#: interzice alegerea unei valori implicite; o recomandare este o alegere deghizată.
FORBIDDEN = [
    "recomand", "sugerez", "propun", "ar trebui să folosiți", "valoare implicită",
    "vă sugerăm", "alegeți", "setați la", "încercați",
]

#: Vocabular de verdict, interzis în orice artefact produs de VE.
VERDICT_WORDS = [
    "semnificativ", "confirmat", "respins statistic", "robust", "promițător",
]


def _halted_result(mutator, baseline_raw):
    spec = copy.deepcopy(baseline_raw)
    mutator(spec)
    return validate_spec_object(spec, spec_sha256="a" * 64)


def test_renders_four_fields_per_cause(baseline_raw):
    result = _halted_result(MUTATIONS[0][2], baseline_raw)
    text = clarification.render(result, spec_id="STAT-SPEC-FIXTURE-F2", generated_at=FIXED_TS)

    assert text.startswith("# CERERE DE CLARIFICARE")
    for label in ("**1. Cod:**", "**2. Câmp:**", "**3. Motiv:**", "**4. În registru:**"):
        assert text.count(label) == len(result.errors), label


def test_reports_zero_data_accesses(baseline_raw):
    result = _halted_result(MUTATIONS[0][2], baseline_raw)
    text = clarification.render(result, generated_at=FIXED_TS)
    assert "**Accesări de date:** 0" in text
    assert "nu a atins date de piață" in text


def _causes_section(text: str) -> str:
    """Doar secțiunile de cauze, fără antet/disclaimer/subsol.

    Disclaimerul conține prin construcție cuvântul „recomandate" (ca negație:
    „nu conține valori recomandate"), deci scanarea lexicală se aplică exclusiv
    conținutului generat pentru fiecare cauză.
    """
    parts = text.split("\n---\n")
    assert len(parts) >= 3, "structura cererii de clarificare s-a schimbat"
    return "\n---\n".join(parts[1:-1]).lower()


@pytest.mark.parametrize("mid,desc,mutator,code,stage", MUTATIONS,
                         ids=[m[0] for m in MUTATIONS])
def test_no_recommendation_and_no_verdict_language(mid, desc, mutator, code, stage, baseline_raw):
    result = _halted_result(mutator, baseline_raw)
    body = _causes_section(clarification.render(result, generated_at=FIXED_TS))
    for word in FORBIDDEN:
        assert word not in body, f"{mid}: cererea conține o sugestie ({word})"
    for word in VERDICT_WORDS:
        assert word not in body, f"{mid}: cererea conține limbaj de verdict ({word})"


def test_rendering_is_deterministic(baseline_raw):
    a = clarification.render(_halted_result(MUTATIONS[3][2], baseline_raw), generated_at=FIXED_TS)
    b = clarification.render(_halted_result(MUTATIONS[3][2], baseline_raw), generated_at=FIXED_TS)
    assert a == b


def test_registry_info_is_factual_listing(baseline_raw):
    """La un ID inexistent, câmpul 4 listează ce există — informație, nu alegere."""
    mutator = next(m[2] for m in MUTATIONS if m[0] == "M31")  # metodă inexistentă
    result = _halted_result(mutator, baseline_raw)
    text = clarification.render(result, generated_at=FIXED_TS)
    assert "ID-uri existente în registru" in text
    assert "matched_null@v1" in text
