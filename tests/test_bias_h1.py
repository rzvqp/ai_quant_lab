"""Teste pentru nivelul 2 — bias_h1 (STAT-LEVEL2-BIAS-H1-SPEC-v1.0, `1b2933c`).

Acoperă: cei patru factori, fiecare convenție de fail-closed din §6, demonstrația de non-lookahead
din §7.1 (perturbare), falsificabilitatea din §7.2, inspecția statică din §7.4, interdicția de
constante străine din §7.5, și regula de retragere la ~95% acord din §7.3.

Datele sunt SINTETICE și deterministe unde ajunge; testele care cer serie reală o citesc din
`H1_from_M15_v2` și se sar dacă fișierul lipsește. Fără MT5, fără rețea.
"""

from __future__ import annotations

import math
import os
import sys
from typing import Sequence

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))

from bias_h1 import (  # noqa: E402
    DAY_H1, K_ATR, N_MIN_BARS, SCHEMA_VERSION, WEEK_H1, BiasState, Status, attach_redundancy,
    compute_bias, default_paths, ratified_vocabulary, redundancy_by_static_inspection, schema_payload,
)

H1_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "data", "market", "OANDA_XAUUSD_H1_from_M15_v2.csv")


def _synthetic(n: int) -> tuple[list[float], list[float], list[float], list[float]]:
    """Serie deterministă cu structură alternantă — suficientă ca factorii să existe, fără aleator."""
    o: list[float] = []
    h: list[float] = []
    lo: list[float] = []
    c: list[float] = []
    price = 2000.0
    for i in range(n):
        step = 6.0 * math.sin(i / 7.0) + 0.35 * (i % 11) - 1.5
        op = price
        cl = price + step
        hi = max(op, cl) + 1.2 + 0.6 * ((i * 5) % 4)
        low = min(op, cl) - 1.2 - 0.6 * ((i * 3) % 4)
        o.append(op); c.append(cl); h.append(hi); lo.append(low)
        price = cl
    return o, h, lo, c


def _real() -> tuple[list[float], list[float], list[float], list[float]]:
    import csv
    o: list[float] = []
    h: list[float] = []
    lo: list[float] = []
    c: list[float] = []
    with open(H1_CSV, "r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            o.append(float(row["open"])); h.append(float(row["high"]))
            lo.append(float(row["low"])); c.append(float(row["close"]))
    return o, h, lo, c


def _names(state: BiasState) -> list[str]:
    return [f.name for f in state.factors]


# ── cei patru factori ────────────────────────────────────────────────────────────────────────

def test_emits_exactly_the_four_specified_factors_in_order() -> None:
    o, h, lo, c = _synthetic(400)
    st = compute_bias(o, h, lo, c, 400)
    assert _names(st) == ["structure_run_h1", "displacement_h1", "liquidity_above", "momentum"]


def test_does_not_emit_any_probability_field() -> None:
    """§1: nivelul 2 emite FACTORI. Un câmp de probabilitate ar fi al doilea estimator."""
    o, h, lo, c = _synthetic(400)
    st = compute_bias(o, h, lo, c, 400)
    fields = set(st.__dataclass_fields__)
    assert not any("prob" in f for f in fields)
    assert "direction_share_long" in fields and "direction_share_short" in fields
    assert schema_payload()["emits_probability"] is False


def test_shares_are_descriptive_and_bounded() -> None:
    o, h, lo, c = _synthetic(400)
    st = compute_bias(o, h, lo, c, 400)
    assert st.direction_share_long is not None and st.direction_share_short is not None
    assert 0.0 <= st.direction_share_long <= 1.0
    assert 0.0 <= st.direction_share_short <= 1.0
    assert st.direction_share_long + st.direction_share_short <= 1.0 + 1e-9


def test_momentum_is_unavailable_never_zero_never_neutral() -> None:
    """§6: `momentum` cerut dar neconstruit → UNAVAILABLE, NU zero, NU neutru."""
    o, h, lo, c = _synthetic(400)
    st = compute_bias(o, h, lo, c, 400)
    mom = next(f for f in st.factors if f.name == "momentum")
    assert mom.status == Status.UNAVAILABLE.value
    assert mom.value is None
    assert mom.primitive == "ABSENT_NO_RATIFIED_PRIMITIVE"


def test_value_is_none_exactly_when_status_is_unavailable() -> None:
    o, h, lo, c = _synthetic(400)
    st = compute_bias(o, h, lo, c, 400)
    for f in st.factors:
        assert (f.value is None) == (f.status == Status.UNAVAILABLE.value), f.name


def test_liquidity_factor_counts_only_unswept_pools_under_a_threshold() -> None:
    """§3: doar bazine neconsumate, filtru de PRAG. Un prag mai larg nu poate reduce numărul."""
    o, h, lo, c = _synthetic(500)
    narrow = compute_bias(o, h, lo, c, 500, k_atr=0.5)
    wide = compute_bias(o, h, lo, c, 500, k_atr=4.0)
    n_narrow = next(f for f in narrow.factors if f.name == "liquidity_above").value
    n_wide = next(f for f in wide.factors if f.name == "liquidity_above").value
    assert n_narrow is not None and n_wide is not None
    assert n_wide >= n_narrow


def test_threshold_filter_can_return_the_empty_set() -> None:
    """§3: un PRAG poate produce mulțimea vidă; un RANG nu ar putea niciodată. Asta e falsificabilitatea."""
    o, h, lo, c = _synthetic(500)
    st = compute_bias(o, h, lo, c, 500, k_atr=1e-9)
    liq = next(f for f in st.factors if f.name == "liquidity_above")
    assert liq.value == 0.0


# ── fail-closed, §6 ──────────────────────────────────────────────────────────────────────────

def test_incomplete_window_is_unavailable_not_an_assumed_value() -> None:
    o, h, lo, c = _synthetic(400)
    st = compute_bias(o, h, lo, c, N_MIN_BARS - 1)
    assert st.status == Status.UNAVAILABLE.value
    assert st.factors == ()
    assert st.direction_share_long is None


def test_empty_series_is_unavailable() -> None:
    st = compute_bias([], [], [], [], 0)
    assert st.status == Status.UNAVAILABLE.value


def test_regime_unavailable_cascades_to_bias_unavailable() -> None:
    """§6: RegimeState de la nivelul 1 UNAVAILABLE → BiasState UNAVAILABLE."""
    o, h, lo, c = _synthetic(400)
    st = compute_bias(o, h, lo, c, 400, regime_axes_status=["unavailable"] * 4)
    assert st.status == Status.UNAVAILABLE.value


def test_a_single_unavailable_regime_axis_is_excluded_not_fatal() -> None:
    """§6: o axă indisponibilă se EXCLUDE din cheie; doar cheia goală invalidează."""
    o, h, lo, c = _synthetic(400)
    st = compute_bias(o, h, lo, c, 400,
                      regime_axes_status=["available", "unavailable", "unavailable", "unavailable"])
    assert st.status == Status.AVAILABLE.value


def test_news_axis_alone_unavailable_does_not_block() -> None:
    """Știrile sunt permanent UNAVAILABLE până la calendar; nu trebuie să blocheze nivelul 2."""
    o, h, lo, c = _synthetic(400)
    st = compute_bias(o, h, lo, c, 400,
                      regime_axes_status=["available", "available", "available", "unavailable"])
    assert st.status == Status.AVAILABLE.value


# ── non-lookahead, §7.1 ──────────────────────────────────────────────────────────────────────

def _perturb(seq: Sequence[float], frm: int, delta: float) -> list[float]:
    out = list(seq)
    for j in range(frm, len(out)):
        out[j] += delta
    return out


def test_no_lookahead_perturbing_the_current_and_future_bars_changes_nothing() -> None:
    """§7.1: factorii la bara i citesc EXCLUSIV bare <= i-1. Perturbăm de la i încolo."""
    o, h, lo, c = _synthetic(600)
    i = 500
    base = compute_bias(o, h, lo, c, i)
    for delta in (+50.0, -50.0):
        pert = compute_bias(_perturb(o, i, delta), _perturb(h, i, delta),
                            _perturb(lo, i, delta), _perturb(c, i, delta), i)
        assert pert == base, f"factorii la i s-au schimbat la perturbarea barelor >= i (delta={delta})"


def test_no_lookahead_truncating_after_i_changes_nothing() -> None:
    """Dacă barele >= i nici măcar nu există, rezultatul la i trebuie să fie identic."""
    o, h, lo, c = _synthetic(600)
    i = 400
    full = compute_bias(o, h, lo, c, i)
    cut = compute_bias(o[:i], h[:i], lo[:i], c[:i], i)
    assert full == cut


def test_reads_exactly_i_closed_bars() -> None:
    o, h, lo, c = _synthetic(600)
    st = compute_bias(o, h, lo, c, 420)
    assert st.n_closed_bars == 420
    assert st.as_of_index == 420


# ── falsificabilitate, §7.2 ──────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not os.path.exists(H1_CSV), reason="H1_from_M15_v2 absent")
def test_zero_eligible_fraction_is_materially_above_zero_on_real_series() -> None:
    """§7.2, cu referința pre-declarată: primitiva B a ajuns la 83,6% la k=1,0×ATR."""
    o, h, lo, c = _real()
    st = compute_bias(o, h, lo, c, 3000)
    assert st.zero_eligible_fraction is not None
    assert st.zero_eligible_fraction > 0.0, "saturație: factorul ar fi nefalsificabil"
    assert st.zero_eligible_fraction >= 0.836, "sub precedentul măsurat al primitivei B"


# ── constante, §7.5 ──────────────────────────────────────────────────────────────────────────

def test_constants_are_in_h1_units_and_no_foreign_constant_appears() -> None:
    """§7.5: nicio constantă în unități M15 (92/460) sau H4 (6/30) în corpul nivelului 2."""
    assert DAY_H1 == 23 and WEEK_H1 == 115
    src_path, _ = default_paths()
    with open(src_path, "r", encoding="utf-8") as fh:
        body = [ln for ln in fh.read().splitlines()
                if not ln.strip().startswith("#") and "măsurat" not in ln]
    joined = "\n".join(body)
    for foreign in ("= 92", "= 460", "= 30\n"):
        assert foreign not in joined, f"constantă străină în corp: {foreign!r}"


def test_h1_trend_up_is_not_used() -> None:
    """§5: `h1_trend_up` e SCOS ca insuficient."""
    src_path, _ = default_paths()
    with open(src_path, "r", encoding="utf-8") as fh:
        assert "h1_trend_up" not in fh.read().split('"""', 2)[-1]


# ── inspecție statică / dezvăluire, §7.4 ─────────────────────────────────────────────────────

def test_redundancy_is_derived_from_source_not_from_a_list() -> None:
    src_path, cand_path = default_paths()
    if not os.path.exists(cand_path):
        pytest.skip("phase1_screening.py absent")
    mapping = redundancy_by_static_inspection(src_path, cand_path)
    assert mapping, "inspecția statică n-a găsit nicio primitivă partajată — improbabil, deci suspect"
    for prim, users in mapping.items():
        assert all(u.startswith("gen_cand") or u.startswith("MODULE_LEVEL_INJECTED") for u in users), prim


def test_vocabulary_excludes_data_structures_and_stdlib() -> None:
    """Fără restricție, `float`/`len`/`Block` ar apărea drept primitive partajate — adevărat și vid."""
    vocab = ratified_vocabulary()
    for noise in ("float", "len", "max", "min", "range", "Block", "PoolSide", "BreakKind"):
        assert noise not in vocab, noise
    for real in ("detect_breaks", "detect_swings", "build_pools", "detect_sweeps", "expansion"):
        assert real in vocab, real


def test_injected_primitive_edge_is_not_lost() -> None:
    """`gen_cand0002` PRIMEȘTE `exp` ca parametru — `expansion()` e apelat de runner, nu în generator.
    Inspecția intra-funcție e OARBĂ la muchia asta; tier-ul la nivel de modul trebuie s-o recupereze,
    altfel redundanța de displacement pe care spec §4 o afirmă ar dispărea tăcut din dezvăluire."""
    src_path, cand_path = default_paths()
    if not os.path.exists(cand_path):
        pytest.skip("phase1_screening.py absent")
    mapping = redundancy_by_static_inspection(src_path, cand_path)
    assert "expansion" in mapping, "muchia expansion a dispărut din dezvăluire"
    assert mapping["expansion"][0].startswith("MODULE_LEVEL_INJECTED")


def test_every_available_factor_carries_its_redundancy_disclosure() -> None:
    src_path, cand_path = default_paths()
    if not os.path.exists(cand_path):
        pytest.skip("phase1_screening.py absent")
    o, h, lo, c = _synthetic(400)
    st = attach_redundancy(compute_bias(o, h, lo, c, 400),
                           redundancy_by_static_inspection(src_path, cand_path))
    shared = [f for f in st.factors if f.redundant_with]
    assert shared, "niciun factor n-a primit avertisment; §4 spune că ZERO sunt independenți"


def test_schema_payload_is_ordered_and_complete() -> None:
    """Moștenirea 2: lista ORDONATĂ a factorilor, primitiva, pragurile, ferestrele, versiunea."""
    p = schema_payload()
    assert p["schema_version"] == SCHEMA_VERSION
    assert [f["name"] for f in p["factors_ordered"]] == [
        "structure_run_h1", "displacement_h1", "liquidity_above", "momentum"]
    assert p["windows_h1_units"] == {"day": DAY_H1, "week": WEEK_H1, "n_min_bars": N_MIN_BARS}
    liq = p["factors_ordered"][2]["params"]
    assert liq["unswept_only"] is True and liq["filter"] == "threshold_not_rank" and liq["k_atr"] == K_ATR


# ── regula de retragere, §7.3 ────────────────────────────────────────────────────────────────

def test_withdrawal_rule_is_expressible_and_fires_on_a_restatement() -> None:
    """§7.3: un factor care depășește ~95% acord cu direcția nivelului 1 e o reformulare și se retrage."""
    def agreement(a: Sequence[int], b: Sequence[int]) -> float:
        pairs = [(x, y) for x, y in zip(a, b) if x != 0 and y != 0]
        return sum(1 for x, y in pairs if (x > 0) == (y > 0)) / len(pairs) if pairs else 0.0

    def withdraw(agr: float) -> bool:
        return agr > 0.95

    identical = [1, -1, 1, 1, -1, -1, 1]
    assert agreement(identical, identical) == 1.0
    assert withdraw(agreement(identical, identical)) is True
    partial = [1, -1, 1, -1, -1, 1, 1]
    assert withdraw(agreement(identical, partial)) is False
