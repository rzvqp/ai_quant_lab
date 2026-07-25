"""S7 — suita de acceptare DETERMINISTĂ pentru bonferroni@v1 (metodă de corecție).

bonferroni@v1 poartă în registru exclusiv S7, disjunctă de suitele stocastice
S1/S3/S4. Nu are distribuție null, putere sau FPR de calibrat — garanția FWER ≤ α
e inegalitatea Boole (teoremă). Verificarea e aritmetică + contabilitate de familie
+ comportamente de graniță. Cele șase verificări cerute de CEO 2026-07-25:

  1. aritmetica pe fixturi cu răspuns cunoscut
  2. contabilitatea familiei realizate
  3. oprirea la familie eligibilă vidă
  4. independența de rezultat (R3) la stratul de execuție
  5. „fără filtrare" declarat explicit
  6. determinism / idempotență
"""

import copy
import json

import pandas as pd
import pytest

from ve import paths
from ve.errors import SpecHalt
from ve.methods import bonferroni
from ve.population import eligibility


# ─────────────────────── frame sintetic pentru contabilitate ──────────────────
def _frame():
    """30 bare. v: 4 valori =0, 16 în [1,99], 10 = 100.

    → predicat v>=0 : 30 (eligibil la n>=25)
    → predicat v>=1 : 26 (eligibil la n>=25)
    → predicat v>=100: 10 (respins la n>=25)
    """
    v = [0, 0, 0, 0] + list(range(1, 17)) + [100] * 10
    assert len(v) == 30
    base = pd.DataFrame({"v": v}, index=range(30))
    values = {"v": pd.Series(v, index=base.index)}
    return base, values


def _spec(rule):
    """multiple_testing + tests cu 3 celule (A: v>=0, B: v>=1, C: v>=100)."""
    def cell(cid, thr):
        return {"id": cid, "predicates": [
            {"predicate": "compare@v1", "params": {"left": "v", "op": ">=", "right": thr}}]}
    tests = [{"test_id": "T1", "cells": [cell("A", 0), cell("B", 1), cell("C", 100)]}]
    mt = {"method": "bonferroni@v1", "members": [
        {"test_id": "T1", "cell": "A"}, {"test_id": "T1", "cell": "B"},
        {"test_id": "T1", "cell": "C"}], "params": {"alpha": 0.05, "member_eligibility": rule}}
    return mt, tests


def _family(rule):
    base, values = _frame()
    mt, tests = _spec(rule)
    return eligibility.realized_family(mt, tests, list(base.index), values, base)


# ───────────────────────── 1. ARITMETICĂ (răspuns cunoscut) ────────────────────

def test_s7_1_arithmetic_threshold_and_adjusted():
    realized = {"m_realized": 4, "eligible_cells": ["a", "b", "c", "d"],
                "dropped_cells": [], "eligibility_rule": None}
    p = {"a": 0.01, "b": 0.03, "c": 0.20, "d": 0.001}
    out = bonferroni.correct(0.05, realized, p)
    assert out["threshold_per_test"] == 0.05 / 4          # 0.0125
    assert out["family_size"] == 4 and out["m_realized"] == 4
    assert out["p_adjusted"] == {"a": 0.04, "b": 0.12, "c": 0.80, "d": 0.004}
    # decizia: respinge H0 unde p_adjusted <= alpha  ⇔  p <= alpha/m
    rejected = {k for k, pa in out["p_adjusted"].items() if pa <= 0.05}
    assert rejected == {"a", "d"}


def test_s7_1_capping_at_one():
    cells = [f"c{i}" for i in range(10)]                  # m coerent cu |eligible|
    realized = {"m_realized": 10, "eligible_cells": cells, "dropped_cells": []}
    p = {c: 0.001 for c in cells}
    p["c0"] = 0.5
    out = bonferroni.correct(0.05, realized, p)
    assert out["p_adjusted"]["c0"] == 1.0                 # min(1, 0.5×10=5.0)


def test_s7_1_m1_is_a_noop_correction():
    realized = {"m_realized": 1, "eligible_cells": ["only"], "dropped_cells": []}
    out = bonferroni.correct(0.05, realized, {"only": 0.03})
    assert out["threshold_per_test"] == 0.05              # alpha/1
    assert out["p_adjusted"] == {"only": 0.03}            # p×1


# ───────────────────────── 2. CONTABILITATEA FAMILIEI ──────────────────────────

def test_s7_2_realized_family_membership_exact():
    fam = _family({"field": "n", "op": ">=", "value": 25})
    assert fam["per_cell"]["T1::A"]["n"] == 30
    assert fam["per_cell"]["T1::B"]["n"] == 26
    assert fam["per_cell"]["T1::C"]["n"] == 10
    assert set(fam["eligible_cells"]) == {"T1::A", "T1::B"}
    assert fam["m_realized"] == 2
    dropped_keys = {d["cell"] for d in fam["dropped_cells"]}
    assert dropped_keys == {"T1::C"}


def test_s7_2_correction_uses_realized_m():
    fam = _family({"field": "n", "op": ">=", "value": 25})           # m=2
    out = bonferroni.correct(0.05, fam, {"T1::A": 0.02, "T1::B": 0.04})
    assert out["m_realized"] == 2
    assert out["threshold_per_test"] == 0.025                        # 0.05/2
    assert out["p_adjusted"] == {"T1::A": 0.04, "T1::B": 0.08}


# ───────────────────────── 3. FAMILIE ELIGIBILĂ VIDĂ ───────────────────────────

def test_s7_3_empty_family_halts_at_accounting():
    fam = _family({"field": "n", "op": ">=", "value": 1000})         # niciuna
    assert fam["m_realized"] == 0
    with pytest.raises(SpecHalt) as exc:
        bonferroni.correct(0.05, fam, {})
    assert exc.value.errors[0].code == "E6"


def test_s7_3_empty_family_direct():
    with pytest.raises(SpecHalt) as exc:
        bonferroni.correct(0.05, {"m_realized": 0, "eligible_cells": []}, {})
    assert exc.value.errors[0].code == "E6"
    assert "vidă" in exc.value.errors[0].reason


# ───────────────── 4. INDEPENDENȚĂ DE REZULTAT (R3), STRAT DE EXECUȚIE ──────────

def test_s7_4_eligibility_engine_knows_only_pre_outcome_fields():
    # motorul de execuție al eligibilității nu cunoaște niciun câmp de rezultat
    forbidden = {"p_hat", "p_value", "observed", "effect", "statistic", "p_adjusted"}
    assert not (eligibility._PRE_OUTCOME & forbidden)


def test_s7_4_result_field_rule_rejected_before_execution():
    """O regulă care referă un rezultat e respinsă la validare (E2), fără date."""
    from ve.spec.validate import validate_spec_object
    base = json.loads((paths.VE_ROOT / "tests" / "fixtures" /
                       "fixture_baseline_spec.json").read_text(encoding="utf-8"))
    for bad in ("p_hat", "observed", "effect", "statistic", "p_adjusted"):
        spec = copy.deepcopy(base)
        spec["multiple_testing"]["params"]["member_eligibility"] = {
            "field": bad, "op": "<", "value": 0.05}
        r = validate_spec_object(spec, spec_sha256="0" * 64)
        assert r.halted and "E2" in r.codes, bad
        assert r.data_accesses == [], bad


# ───────────────────────── 5. „FĂRĂ FILTRARE" EXPLICIT ─────────────────────────

def test_s7_5_trivial_rule_keeps_whole_family():
    fam = _family({"field": "n", "op": ">=", "value": 1})            # trivial adevărat
    assert set(fam["eligible_cells"]) == {"T1::A", "T1::B", "T1::C"}
    assert fam["m_realized"] == 3
    assert fam["dropped_cells"] == []


def test_s7_5_eligibility_is_a_required_param_not_optional():
    from ve.spec import registry_validator
    reg = registry_validator.load_registry()
    assert reg["correction_methods"]["bonferroni@v1"]["required_params"][
        "member_eligibility"] == "eligibility_rule"


# ───────────────────────── 6. DETERMINISM / IDEMPOTENȚĂ ────────────────────────

def test_s7_6_correction_is_deterministic():
    realized = {"m_realized": 3, "eligible_cells": ["a", "b", "c"], "dropped_cells": []}
    p = {"a": 0.001, "b": 0.02, "c": 0.30}
    assert bonferroni.correct(0.05, realized, p) == bonferroni.correct(0.05, realized, p)


def test_s7_6_family_accounting_is_deterministic():
    rule = {"field": "n", "op": ">=", "value": 25}
    a, b = _family(rule), _family(rule)
    assert a["eligible_cells"] == b["eligible_cells"]
    assert a["m_realized"] == b["m_realized"]
    assert a["per_cell"] == b["per_cell"]


# ───────────────────────── graniță: alpha invalid ─────────────────────────────

@pytest.mark.parametrize("bad_alpha", [0.0, 1.0, -0.1, 1.5])
def test_s7_alpha_out_of_range_halts(bad_alpha):
    realized = {"m_realized": 2, "eligible_cells": ["a", "b"], "dropped_cells": []}
    with pytest.raises(SpecHalt) as exc:
        bonferroni.correct(bad_alpha, realized, {"a": 0.01, "b": 0.02})
    assert exc.value.errors[0].code == "E6"
