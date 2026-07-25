"""Invarianții artefactelor F1 și comportamentul celor două etape de validare."""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from ve import paths
from ve.spec import domains, registry_validator, schema_validator


# ───────────────────────────── invarianți de schemă ───────────────────────────

def test_schema_is_a_valid_draft202012_schema():
    Draft202012Validator.check_schema(schema_validator.load_schema())


def test_schema_declares_no_defaults():
    """Un singur `default` ar readuce comportamentul interzis de contract §1.7."""
    raw = Path(paths.SPEC_SCHEMA_PATH).read_text(encoding="utf-8")
    assert '"default"' not in raw


def test_schema_forbids_extra_fields_everywhere():
    schema = schema_validator.load_schema()

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "object" and "properties" in node:
                assert node.get("additionalProperties") is False, node.get("title", node)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(schema)


def test_halt_clause_has_a_single_admissible_value():
    schema = schema_validator.load_schema()
    assert schema["properties"]["on_missing_or_ambiguous"]["const"] == "halt_and_request_clarification"


def test_criteria_threshold_is_numeric_by_construction():
    schema = schema_validator.load_schema()
    crit = schema["properties"]["criteria"]["items"]["properties"]
    assert crit["threshold"] == {"type": "number"}


def test_criteria_evaluation_is_absent_pending_p1():
    schema = schema_validator.load_schema()
    ret = schema["properties"]["return"]
    assert "criteria_evaluation" not in ret["properties"]
    assert ret["additionalProperties"] is False


# ──────────────────────────── invarianți de registru ──────────────────────────

def test_registry_domain_grammar_covers_every_descriptor():
    ok, bad = registry_validator.registry_domains_are_parseable()
    assert ok, f"descriptori neacoperiți: {bad}"


def test_only_the_ceo_promoted_methods_are_executable():
    """CEO 2026-07-25: matched_null@v1 (S1/S3/S4) + bonferroni@v1 (S7) -> VALIDATED.
    Exact două metode; restul rămân locked."""
    reg = registry_validator.load_registry()
    validated = []
    for section in ("test_methods", "correction_methods"):
        for mid, meta in reg[section].items():
            if meta["calibration_status"] == "VALIDATED":
                validated.append(mid)
            else:
                assert meta["calibration_status"] == "UNVALIDATED", mid
    assert set(validated) == {"matched_null@v1", "bonferroni@v1"}
    assert reg["status"] == "PARTIALLY_EXECUTABLE"


# ─────────────────────── registrul v1.2 (golurile G3, G4, G5) ─────────────────

def test_g7_first_in_scope_persists_across_versions():
    """first_in_scope@v1 (G7) rămâne disponibil după revizuirile ulterioare."""
    reg = registry_validator.load_registry()
    assert "first_in_scope@v1" in reg["population_predicates"]


def test_g7_first_in_scope_predicate_exists():
    reg = registry_validator.load_registry()
    fis = reg["population_predicates"]["first_in_scope@v1"]
    assert set(fis["required_params"]) == {"scope", "predicate"}
    assert fis["required_params"]["predicate"] == "predicate"
    assert set(fis["required_params"]["scope"]) == {"day", "session", "week"}


def test_day_scope_boundary_is_documented_as_utc():
    reg = registry_validator.load_registry()
    assert "day_scope_boundary" in reg["rules"]
    assert "00:00 UTC" in reg["rules"]["day_scope_boundary"]


# ─────────────────────── registrul v1.4 (golul G8) ────────────────────────────

def test_registry_is_v1_6_with_a_declared_revision():
    reg = registry_validator.load_registry()
    assert reg["registry_version"] == "1.6"
    assert reg["revision"]["supersedes"] == "1.5"
    assert "bonferroni@v1" in " ".join(reg["revision"]["changes"])


def test_g8_whitelist_contains_only_pre_outcome_fields():
    """REGULA DE AUR R3: lista albă NU conține niciun câmp de rezultat."""
    reg = registry_validator.load_registry()
    wl = reg["member_eligibility_fields"]
    assert set(wl) == {"n", "denominator", "event_count"}
    forbidden = {"p_hat", "p_value", "observed", "effect", "statistic", "p_adjusted",
                 "sharpe", "profit_factor"}
    assert not (set(wl) & forbidden)


def test_g8_bonferroni_and_bh_require_member_eligibility():
    reg = registry_validator.load_registry()
    for m in ("bonferroni@v1", "benjamini_hochberg@v1"):
        assert reg["correction_methods"][m]["required_params"]["member_eligibility"] == "eligibility_rule"
    # none@v1 nu are corecție de familie, deci nu cere eligibilitate
    assert "member_eligibility" not in reg["correction_methods"]["none@v1"]["required_params"]


def test_g8_empty_family_halt_is_documented():
    reg = registry_validator.load_registry()
    assert "empty_eligible_family_halts" in reg["rules"]


def test_g8_eligibility_rule_type_in_grammar():
    assert "eligibility_rule" in domains.REFERENCE_TYPES


def test_g8_result_fields_are_rejected_fail_closed():
    """Dovada structurală R3: eligibilitatea nu poate NUMI un rezultat.

    Familia nu poate depinde sintactic de p — o regulă care referă p_hat/observed/
    effect/statistic se oprește la validare, înainte de orice date.
    """
    from ve.spec.validate import validate_spec_object
    import copy, json
    from pathlib import Path
    from ve import paths

    base = json.loads((paths.VE_ROOT / "tests" / "fixtures" / "fixture_baseline_spec.json").read_text(encoding="utf-8"))
    for bad_field in ("p_hat", "p_adjusted", "observed", "effect", "statistic"):
        spec = copy.deepcopy(base)
        spec["multiple_testing"]["params"]["member_eligibility"] = {"field": bad_field, "op": "<", "value": 0.05}
        r = validate_spec_object(spec, spec_sha256="0" * 64)
        assert r.halted, bad_field
        assert "E2" in r.codes, bad_field
        assert r.data_accesses == [], bad_field
        # motivul menționează explicit interdicția de rezultat
        msgs = " ".join(e.reason for e in r.errors)
        assert "rezultate" in msgs or "pre-rezultat" in msgs


def test_g3_indicator_primitive_exists():
    reg = registry_validator.load_registry()
    ind = reg["variable_primitives"]["indicator@v1"]
    assert set(ind["required_params"]) == {"predicate"}
    assert ind["required_params"]["predicate"] == "predicate"


def test_g4_predicate_list_semantics_are_documented():
    reg = registry_validator.load_registry()
    for rule in ("predicate_list_conjunction", "empty_predicate_lists",
                 "per_criterion_denominator", "indicator_availability"):
        assert rule in reg["rules"], rule
    assert "conjunction" in reg["rules"]["predicate_list_conjunction"].lower()


def test_g5_no_reference_parameter_remains_a_plain_string():
    """Testul de inventar: niciun parametru cu semantică de referință nu mai e `string`."""
    reg = registry_validator.load_registry()
    offenders = []
    for section in ("variable_primitives", "population_predicates", "statistics",
                    "test_methods", "correction_methods"):
        for eid, meta in reg[section].items():
            for pname, dom in (meta.get("required_params") or {}).items():
                if pname.endswith("_ref") and dom == "string":
                    offenders.append(f"{section}.{eid}.{pname}")
    assert offenders == [], offenders


def test_g5_reference_types_distribution():
    reg = registry_validator.load_registry()
    variable_ref = test_ref = predicate_ref = 0
    for section in ("variable_primitives", "population_predicates", "statistics",
                    "test_methods", "correction_methods"):
        for meta in reg[section].values():
            for pname, dom in (meta.get("required_params") or {}).items():
                if not pname.endswith("_ref"):
                    continue
                variable_ref += dom == "variable_ref"
                test_ref += dom == "test_ref"
                predicate_ref += dom == "predicate_ref"
    assert test_ref == 2       # placebo_control, multiverse
    assert predicate_ref == 1  # proportion
    assert variable_ref >= 10


def test_g5_new_reference_types_in_grammar():
    assert "test_ref" in domains.REFERENCE_TYPES
    assert "predicate_ref" in domains.REFERENCE_TYPES


def test_no_test_or_correction_method_added_since_v1_1():
    """Revizuirea a atins doar vocabularul de referință și o primitivă de variabilă."""
    reg = registry_validator.load_registry()
    assert len(reg["test_methods"]) == 12
    assert len(reg["correction_methods"]) == 3
    assert len(reg["variable_primitives"]) == 16  # 15 (v1.1) + indicator@v1


def test_g1_raw_series_exists_and_is_field_constrained():
    reg = registry_validator.load_registry()
    rs = reg["variable_primitives"]["raw_series@v1"]
    assert set(rs["required_params"]) == {"source_id", "field"}
    assert set(rs["required_params"]["field"]) == {"open", "high", "low", "close", "volume", "sub"}


def test_g2_every_statistic_parameter_is_a_parameterised_call():
    reg = registry_validator.load_registry()
    users = {"matched_null@v1", "block_bootstrap@v1", "iid_bootstrap@v1", "permutation_test@v1"}
    for mid in users:
        assert reg["test_methods"][mid]["required_params"]["statistic"] == "statistic_call"
    assert reg["test_methods"]["descriptive_measurement@v1"]["required_params"]["statistics"] == "list[statistic_call]"


def test_g2_statistic_id_is_no_longer_used_by_any_entry():
    """Rămâne definit în gramatică, dar nicio intrare din registru nu îl mai folosește."""
    import json as _json

    reg = registry_validator.load_registry()
    for section in ("variable_primitives", "population_predicates", "statistics",
                    "test_methods", "correction_methods"):
        blob = _json.dumps(reg[section])
        assert '"statistic_id"' not in blob, section
    assert "statistic_id" in domains.REFERENCE_TYPES


def test_g2_statistic_variable_references_are_resolvable():
    """Un parametru de tip referință nu poate rămâne un simplu șir de caractere."""
    reg = registry_validator.load_registry()
    for sid, meta in reg["statistics"].items():
        for param in ("variable_ref", "group_ref"):
            if param in meta["required_params"]:
                assert meta["required_params"][param] == "variable_ref", f"{sid}.{param}"


def test_schema_file_was_not_touched_by_the_registry_revisions():
    """Extinderea vocabularului (v1.1 și v1.2) nu cere versiune nouă de schemă — invariantul F1."""
    schema = schema_validator.load_schema()
    assert schema["title"] == "Validation Engine Specification v1.0"
    assert schema["properties"]["tests"]["items"]["properties"]["params"] == {"type": "object"}


# ─────────────────────────── decizia JSON-only (A1) ───────────────────────────

def test_documentation_no_longer_promises_yaml():
    doc = Path(paths.VE_ROOT / "SPEC_SCHEMA_v1.0.md").read_text(encoding="utf-8")
    assert "exclusiv în JSON" in doc
    assert "YAML sau JSON" not in doc


def test_no_yaml_template_remains():
    assert not (paths.VE_ROOT / "SPEC_TEMPLATE_v1.0.yaml").exists()
    assert (paths.VE_ROOT / "SPEC_TEMPLATE_v1.4.json").exists()


def test_registry_declares_no_optional_parameters():
    reg = registry_validator.load_registry()
    for section in ("variable_primitives", "population_predicates", "statistics",
                    "test_methods", "correction_methods"):
        for eid, entry in reg[section].items():
            assert set(entry) <= {
                "required_params", "calibration_status", "acceptance_suites",
                "purpose", "outputs", "note", "validation",
            }, f"{section}.{eid} conține chei neașteptate"
            assert "optional_params" not in entry


def test_sealed_boundary_is_single_and_marked_provisional():
    reg = registry_validator.load_registry()
    sealed = reg["sealed_registry"]
    assert sealed["status"] == "PROVISIONAL_AWAITING_CEO_RATIFICATION"
    assert sealed["boundary_utc"] == "2025-10-23T09:15:00Z"
    assert set(sealed["windows"]) == set(reg["data_sources"])


# ─────────────────────────── gramatica domeniilor ─────────────────────────────

@pytest.mark.parametrize("descriptor,value,expect_ok", [
    ("integer>=1", 1, True),
    ("integer>=1", 0, False),
    ("integer>=1", 1.5, False),
    ("integer>=1", True, False),
    ("number>0", 0.1, True),
    ("number>0", 0, False),
    ("number in (0,1)", 0.05, True),
    ("number in (0,1)", 0, False),
    ("number in (0,1)", 1, False),
    ("number in [0,0.5)", 0.0, True),
    ("number in [0,0.5)", 0.5, False),
    ("string", "x", True),
    ("string", 3, False),
    ("boolean", True, True),
    ("boolean", 1, False),
    ("object", {}, True),
    ("object", [], False),
    ("list[string]", ["a"], True),
    ("list[string]", ["a", 2], False),
    ("list[integer>=1]", [1, 2], True),
    ("list[integer>=1]", [1, 0], False),
    ("list[predicate] of length 1", [], False),
    (["a", "b"], "a", True),
    (["a", "b"], "c", False),
    ("list[{name,start_utc,end_utc}]", [{"name": "x", "start_utc": "a", "end_utc": "b"}], True),
    ("list[{name,start_utc,end_utc}]", [{"name": "x"}], False),
    ("list[[variable_ref,variable_ref]]", [["a", "b"]], True),
    ("list[[variable_ref,variable_ref]]", [["a"]], False),
])
def test_domain_checks(descriptor, value, expect_ok):
    dom = domains.parse(descriptor)
    reason = domains.check(dom, value, resolver=lambda kind, v: None)
    assert (reason is None) is expect_ok, reason


def test_unsupported_descriptor_is_refused_not_ignored():
    with pytest.raises(domains.UnsupportedDomain):
        domains.parse("orice_altceva_neacoperit")


def test_union_domain_accepts_either_side():
    dom = domains.parse("variable_ref|number")

    def resolver(kind, value):
        return None if value == "known_var" else "necunoscută"

    assert domains.check(dom, "known_var", resolver) is None
    assert domains.check(dom, 2.5, resolver) is None
    assert domains.check(dom, "other_var", resolver) is not None


# ───────────────────────── comportamentul celor două etape ────────────────────

def test_stage2_does_not_run_when_stage1_fails(baseline):
    from ve.spec.validate import validate_spec_object

    del baseline["population"]
    baseline["tests"][0]["method"] = "inexistent@v1"
    result = validate_spec_object(baseline)
    assert result.stage_reached == 1
    assert set(result.codes) == {"E1"}


def test_registry_is_the_single_source_of_truth_for_methods():
    """Schema nu conține lista de metode; altfel ar exista două surse de adevăr."""
    raw = json.loads(Path(paths.SPEC_SCHEMA_PATH).read_text(encoding="utf-8"))
    assert raw["properties"]["tests"]["items"]["properties"]["method"] == {"type": "string"}
