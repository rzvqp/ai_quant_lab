"""Testele F1 (§9). Pozitive si negative, plus cele 13 bare reale acceptate FARA modificare."""
from __future__ import annotations

import math
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "escrow_repro"))

from ohlc_input_contract import (  # noqa: E402
    INPUT_CONTRACT_VERSION, MIN_TICK, OHLC_VALIDATION_EPSILON, InputContractError,
    epsilon_for, validate_bar, validate_window,
)

EPS = OHLC_VALIDATION_EPSILON


def bar(o: float, h: float, l: float, c: float) -> dict[str, float]:
    return {"open": o, "high": h, "low": l, "close": c}


# ─────────────────────────── POZITIVE ───────────────────────────

def test_01_bara_perfect_valida():
    assert validate_bar(bar(10.0, 11.0, 9.0, 10.5), 0) is None


def test_02_open_exact_la_low():
    assert validate_bar(bar(9.0, 11.0, 9.0, 10.0), 0) is None


def test_03_close_exact_la_high():
    assert validate_bar(bar(10.0, 11.0, 9.0, 11.0), 0) is None


def test_04_abatere_0_0005_tolerata():
    ev = validate_bar(bar(10.0, 11.0, 9.0, 11.0005), 7)
    assert ev is not None and ev.kind == "INPUT_OHLC_SUBTICK_TOLERATED"
    assert ev.field == "close" and ev.direction == "above_high" and ev.bar_index == 7
    assert ev.contract_version == INPUT_CONTRACT_VERSION


def test_05_abatere_exact_egala_cu_epsilon_TRECE():
    """Egalitatea la limita trece — cerinta explicita a contractului."""
    ev = validate_bar(bar(10.0, 11.0, 9.0, 11.0 + EPS), 0)
    assert ev is not None and math.isclose(ev.magnitude, EPS, rel_tol=1e-9)


def test_06_abatere_imediat_peste_epsilon_ESUEAZA():
    with pytest.raises(InputContractError) as e:
        validate_bar(bar(10.0, 11.0, 9.0, 11.0 + EPS * 1.0001), 0)
    assert e.value.code == "CLOSE_OUTSIDE_HIGH_LOW"


def test_07_open_sub_low_tolerat_si_refuzat():
    assert validate_bar(bar(9.0 - EPS, 11.0, 9.0, 10.0), 0) is not None
    with pytest.raises(InputContractError) as e:
        validate_bar(bar(9.0 - 2 * EPS, 11.0, 9.0, 10.0), 0)
    assert e.value.code == "OPEN_OUTSIDE_HIGH_LOW"


def test_08_epsilon_e_DERIVAT_nu_literal():
    assert OHLC_VALIDATION_EPSILON == MIN_TICK / 2.0 == 0.005
    assert epsilon_for(0.02) == 0.01 and epsilon_for(0.001) == 0.0005


def test_09_epsilon_sub_un_tick():
    """Garantia de siguranta: o abatere de UN TICK INTREG nu poate fi tolerata niciodata."""
    assert OHLC_VALIDATION_EPSILON < MIN_TICK
    with pytest.raises(InputContractError):
        validate_bar(bar(10.0, 11.0, 9.0, 11.0 + MIN_TICK), 0)


# ─────────────────────────── NEGATIVE ───────────────────────────

def test_10_high_sub_low():
    with pytest.raises(InputContractError) as e:
        validate_bar(bar(10.0, 9.0, 11.0, 10.0), 3)
    assert e.value.code == "HIGH_BELOW_LOW" and e.value.bar_index == 3


def test_11_nan():
    with pytest.raises(InputContractError) as e:
        validate_bar(bar(10.0, float("nan"), 9.0, 10.0), 0)
    assert e.value.code == "NON_FINITE_VALUE"


def test_12_infinit():
    with pytest.raises(InputContractError) as e:
        validate_bar(bar(10.0, float("inf"), 9.0, 10.0), 0)
    assert e.value.code == "NON_FINITE_VALUE"


def test_13_camp_lipsa():
    b = bar(10.0, 11.0, 9.0, 10.0); del b["close"]
    with pytest.raises(InputContractError) as e:
        validate_bar(b, 0)
    assert e.value.code == "MISSING_FIELD"


def test_14_valoare_non_numerica():
    b = bar(10.0, 11.0, 9.0, 10.0); b["close"] = "10.0"          # type: ignore[assignment]
    with pytest.raises(InputContractError) as e:
        validate_bar(b, 0)
    assert e.value.code == "NON_NUMERIC_VALUE"
    b2 = bar(10.0, 11.0, 9.0, 10.0); b2["open"] = True           # type: ignore[assignment]
    with pytest.raises(InputContractError):
        validate_bar(b2, 0)


@pytest.mark.parametrize("bad", [None, 0.0, -0.01, float("nan"), float("inf"), True, "0.01"])
def test_15_tick_absent_zero_negativ_invalid(bad: object):
    with pytest.raises(InputContractError) as e:
        epsilon_for(bad)                                          # type: ignore[arg-type]
    assert e.value.code == "INVALID_MIN_TICK"


# ─────────────────────── DETERMINISM / STRUCTURA ───────────────────────

def test_16_determinism():
    bars = [bar(10.0, 11.0, 9.0, 11.0 + EPS / 2), bar(10.0, 11.0, 9.0, 10.0)]
    a = validate_window(bars); b = validate_window(bars)
    assert [(e.bar_index, e.field, e.magnitude) for e in a] == \
           [(e.bar_index, e.field, e.magnitude) for e in b]


def test_17_chunk_invariance():
    bars = [bar(10.0, 11.0, 9.0, 11.0 + EPS / 2) for _ in range(5)]
    whole = [(e.field, e.direction, e.magnitude) for e in validate_window(bars)]
    parts = [(e.field, e.direction, e.magnitude)
             for chunk in (bars[:2], bars[2:]) for e in validate_window(chunk)]
    assert whole == parts, "contractul e FARA STARE, deci fragmentarea nu poate schimba rezultatul"


def test_18_snapshot_restart_fara_stare():
    b = bar(10.0, 11.0, 9.0, 11.0 + EPS / 2)
    assert validate_bar(b, 0) == validate_bar(b, 0)


def test_19_un_singur_eveniment_per_bara():
    """Si open si close in afara -> UN singur eveniment, cel cu magnitudinea mai mare."""
    evs = validate_window([bar(9.0 - EPS / 4, 11.0, 9.0, 11.0 + EPS / 2)])
    assert len(evs) == 1 and evs[0].field == "close"


def test_20_evenimentul_nu_e_reason_code_semantic():
    from ohlc_input_contract import INPUT_QUALITY_EVENTS
    sys.path.insert(0, os.path.join(os.path.dirname(REPO), "ai_quant_lab", "statistician", "harness"))
    try:
        from range_v42_contract_harness import REASONS         # type: ignore[import-not-found]
    except Exception:
        pytest.skip("harness-ul contractual nu e disponibil in acest checkout")
    assert set(INPUT_QUALITY_EVENTS).isdisjoint(set(REASONS))
    assert len(REASONS) == 29


# ─────────────────── CELE 13 BARE REALE, FARA MODIFICARE ───────────────────

def test_21_cele_13_bare_reale_acceptate_fara_modificare():
    E = os.environ.get("ESCROW_DIR",
                       os.path.join(os.path.expanduser("~"), "escrow_red_team"))
    if not os.path.exists(os.path.join(E, "payload-b7e103a3d9b86f72.bin")):
        pytest.skip("escrow indisponibil")
    from canonical_corpus import build_canonical_corpus
    import verify_range_v43_escrow as V
    c = build_canonical_corpus()
    W = V.open_mapping(os.path.join(E, "payload-b7e103a3d9b86f72.bin"),
                       os.path.join(E, "escrow_key_v3.bin"), os.path.join(E, "escrow_tool.py"))
    tol = 0
    seen = 0
    for w in W:
        bars = [bar(float(c["open"][i]), float(c["high"][i]), float(c["low"][i]), float(c["close"][i]))
                for i in range(w["canonical_index_start"], w["canonical_index_end"])]
        before = [tuple(b.values()) for b in bars]
        evs = validate_window(bars)                 # nu trebuie sa ridice pe niciuna
        assert [tuple(b.values()) for b in bars] == before, "contractul NU are voie sa modifice barele"
        tol += len(evs); seen += len(bars)
    assert seen == 13824
    assert tol == 13, f"asteptat 13 tolerate, gasit {tol}"


def test_22_o_bara_real_invalida_peste_limita_refuzata():
    with pytest.raises(InputContractError):
        validate_bar(bar(10.0, 11.0, 9.0, 11.0 + 0.02), 0)
