"""Specificațiile de referință — dovada că vocabularul v1.2 exprimă designuri reale.

Surse transcrise:
  - `statistician/reviews/DC-0004/STATISTICIAN_PHASE1_DC-0004.md` (§3, §11, §13-15)
  - `statistician/reviews/DC-0008/STATISTICIAN_PHASE1_DC-0008.md` (§2-5, §10-12)

ATENȚIE: fixturile sunt artefacte de inginerie, NU specificații oficiale ale
Statisticianului. Punctele Q1/Q2/Q3 rămân DESCHISE (răspunsurile propuse sunt
contrazise de scripturile in-sample — vezi `SCRIPT_VERIFICATION_Q1_Q3.md`); valorile
legate de ele în fixturi sunt substituenți nenormativi, marcați `_nonnormative`.
"""

import json

import pytest

from ve import paths
from ve.spec.validate import validate_spec_object

FIXTURES = paths.VE_ROOT / "tests" / "fixtures"


def _load(name: str) -> dict:
    spec = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    spec.pop("_nonnormative", None)  # marcaj de fixtură, respins de schemă
    return spec


# ═══════════════════════════ DC-0004 (15/15 structural) ═══════════════════════

@pytest.fixture
def dc4() -> dict:
    return _load("reference_spec_dc0004.json")


@pytest.fixture
def dc4_result(dc4):
    return validate_spec_object(dc4, spec_sha256="b" * 64)


def test_dc4_halts_only_on_calibration_gate(dc4_result):
    assert dc4_result.halted
    assert dc4_result.stage_reached == 2
    assert set(dc4_result.codes) == {"E3"}
    assert all("/method" in e.field_path for e in dc4_result.errors)


def test_dc4_touches_no_data(dc4_result):
    assert dc4_result.data_accesses == []


def test_dc4_sealed_window_is_declared_not_stumbled_into(dc4_result, dc4):
    assert dc4["population"]["window"]["start"] == "2025-10-23T09:15:00Z"
    assert dc4["authorization"]["required"] is True
    assert "E5" not in dc4_result.codes


def test_dc4_removing_authorization_reveals_the_sealed_window(dc4):
    dc4["authorization"] = {"required": False, "ceo_token_id": None, "resource_class": None}
    r = validate_spec_object(dc4, spec_sha256="b" * 64)
    assert "E5" in r.codes
    assert r.data_accesses == []


def test_dc4_pathA_event_is_first_breach_via_first_in_scope(dc4):
    """Calea A / G7: evenimentul = PRIMA bară a zilei care depășește nivelul.

    Exprimat prin first_in_scope@v1 (scope day = 00:00 UTC), verificând doar acea bară.
    """
    variables = {v["id"]: v for v in dc4["variables"]}
    for raw in ("bar_high", "bar_low", "bar_close"):
        assert variables[raw]["primitive"] == "raw_series@v1"
    # populația de evenimente reject folosește first_in_scope pe scope day
    root = dc4["population"]["include"][0]
    assert root["predicate"] == "or@v1"
    firsts = [n for op in root["params"]["operands"]
              for n in op["params"]["operands"] if n["predicate"] == "first_in_scope@v1"]
    assert len(firsts) == 2  # up-breach și down-breach
    for f in firsts:
        assert f["params"]["scope"] == "day"


def test_dc4_pathA_four_fixed_utc_sessions(dc4):
    """Calea A / Q3 DECIS: 4 sesiuni fixe UTC, inclusiv 'late'."""
    session = next(v for v in dc4["variables"] if v["primitive"] == "session_label@v1")
    names = [b["name"] for b in session["params"]["boundaries"]]
    assert names == ["asia", "london", "ny", "late"]
    ny = next(b for b in session["params"]["boundaries"] if b["name"] == "ny")
    assert ny["start_utc"] == "13:00:00" and ny["end_utc"] == "21:00:00"  # UTC fix, fără DST


def test_dc4_pathA_eight_cells_and_k6_decisive(dc4):
    """8 celule (4 sesiuni × 2 direcții); K6 decisiv, K12 secundar."""
    t1 = next(t for t in dc4["tests"] if t["test_id"] == "T1_matched_null_k6")
    assert len(t1["cells"]) == 8
    assert t1["params"]["tail"] == "left"          # one-sided (reversie)
    assert t1["params"]["min_n"] == 25             # n≥25


def test_dc4_pathA_baseline_per_session(dc4):
    baselines = [v for v in dc4["variables"] if v["primitive"] == "baseline_forward_mean@v1"]
    assert len(baselines) == 2
    for b in baselines:
        assert b["params"]["strata"] == ["session"]


def test_dc4_pathA_prereg_criteria_numeric(dc4):
    for c in dc4["criteria"]:
        assert isinstance(c["threshold"], (int, float)) and not isinstance(c["threshold"], bool)


def test_dc4_pathA_leakage_consistent_with_roles(dc4):
    for v in dc4["variables"]:
        if v["role"] in {"exposure", "control", "stratifier"}:
            assert v["availability"]["offset_bars"] <= 0, v["id"]
        if v["role"] == "outcome":
            assert v["availability"]["offset_bars"] > 0, v["id"]


def test_dc4_pathA_no_vocabulary_gap_remains_only_calibration(dc4_result):
    """Toate opririle sunt porți de calibrare; niciun gol de vocabular la validare."""
    assert set(dc4_result.codes) == {"E3"}
    non_calibration = [e for e in dc4_result.errors
                       if "calibrare" not in e.reason and "statusul" not in e.reason]
    assert non_calibration == []


def test_dc4_pathA_family_is_empirical_n25(dc4):
    """G8 REZOLVAT: familia Bonferroni empirică n≥25, declarată prin member_eligibility."""
    mt = dc4["multiple_testing"]
    assert mt["method"] == "bonferroni@v1"
    assert len(mt["members"]) == 8                          # cei 8 candidați enumerați
    elig = mt["params"]["member_eligibility"]
    assert elig == {"field": "n", "op": ">=", "value": 25}  # regula declarată, nu dedusă
    assert "STATIC" not in mt["family_id"]                  # substituentul a fost eliminat


def test_dc4_pathA_is_fully_normative_no_placeholder(dc4):
    """Q1/Q2/Q3 decise + G8 rezolvat + seed decis → nimic nenormativ rămas."""
    assert "_nonnormative" not in dc4


def test_dc4_pathA_seed_is_derived_not_literal_seven(dc4):
    """Tensiune consemnată: seed=7 literal nu e exprimabil; schema fixează derived_from_spec_hash."""
    for t in dc4["tests"]:
        assert t["seed_policy"] == "derived_from_spec_hash"


# ═══════════════════ DC-0008 (grad de exprimare + golul G6) ═══════════════════

@pytest.fixture
def dc8() -> dict:
    return _load("reference_spec_dc0008.json")


@pytest.fixture
def dc8_result(dc8):
    return validate_spec_object(dc8, spec_sha256="c" * 64)


def test_dc8_statistical_machinery_is_fully_expressible(dc8_result):
    """Toată mașinăria statistică validează; opririle sunt doar porți de calibrare."""
    assert dc8_result.halted
    assert dc8_result.stage_reached == 2
    assert set(dc8_result.codes) == {"E3"}
    assert dc8_result.data_accesses == []


def test_dc8_bimodality_battery_is_expressible(dc8):
    """§11a: dip test + GMM + changepoint pe variabila de expunere."""
    methods = {t["method"] for t in dc8["tests"]}
    assert {"dip_test@v1", "gaussian_mixture@v1", "changepoint@v1"} <= methods


def test_dc8_threshold_measurement_and_classification(dc8):
    """§11b + clasificarea: măsurare descriptivă + indicator pe prag preînregistrat."""
    methods = {t["method"] for t in dc8["tests"]}
    assert "descriptive_measurement@v1" in methods
    ind = next(v for v in dc8["variables"] if v["primitive"] == "indicator@v1")
    assert ind["id"] == "class_concentrated"


def test_dc8_classification_predicts_outcome_controlling_volatility(dc8):
    """§12: regresia clasei pe outcome, controlând pentru volatilitate."""
    reg = next(t for t in dc8["tests"] if t["method"] == "regression_control@v1")
    assert reg["params"]["exposure_ref"] == "class_concentrated"
    assert reg["params"]["controls"] == ["vol_hour"]


def test_dc8_true_exposure_R_is_a_nonnormative_standin_gap_G6(dc8):
    """G6: variabila de expunere reală R (raport de volum sub-bară) NU e exprimabilă.

    Fixtura folosește `bar_range_ratio@v1` pe M15 ca substituent structural — nu R.
    Nu există sursă M1/M5 și nicio primitivă de agregare sub-bară.
    """
    standin = next(v for v in dc8["variables"] if v["id"] == "r_ratio_standin")
    assert standin["primitive"] == "bar_range_ratio@v1"
    # nu există nicio primitivă de agregare sub-bară în registru
    from ve.spec import registry_validator
    prims = registry_validator.load_registry()["variable_primitives"]
    assert not any("sub" in p or "M1" in p or "M5" in p for p in prims)
