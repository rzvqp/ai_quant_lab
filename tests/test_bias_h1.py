"""Teste pentru nivelul 2 — bias_h1 (v2.0 SEMANTICĂ DIRECȚIONALĂ, STAT-SPEC3-N2, doc 404b6c8).

Acoperă: cei patru factori sub `FactorDirection` (LONG/SHORT/UNKNOWN), contractul LevelOutput (UNKNOWN măsurat = Ok;
necalculabil = Unavailable), mulțimea necesară {structure_run_h1}, momentum PERMANENT Unavailable în afara ei,
polaritatea DECLARATĂ a lui liquidity_above, non-lookahead (§7.1), falsificabilitatea (§7.2), inspecția statică (§7.4),
constantele H1 (§7.5) și regula de retragere (§7.3). Sintetic + serie reală (se sare dacă lipsește). Fără MT5/rețea.
"""

from __future__ import annotations

import math
import os
import sys
from typing import Sequence

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))

from level_output import Ok, Unavailable  # noqa: E402
from bias_h1 import (  # noqa: E402
    ASSUMPTION_LIQ_ABOVE, DAY_H1, K_ATR, N_MIN_BARS, SCHEMA_VERSION, WEEK_H1, BiasState, Direction,
    FactorDirection, compute_bias, default_paths, ratified_vocabulary, redundancy_by_static_inspection,
    schema_payload,
)

H1_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "data", "market", "OANDA_XAUUSD_H1_from_M15_v2.csv")

STRUCT, DISP, LIQ, MOM = 0, 1, 2, 3          # ordinea fixă a factorilor în tuplu


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


def _state(out: object) -> BiasState:
    assert isinstance(out, Ok)                                   # mulțimea necesară disponibilă ⇒ Ok
    assert out.valid_until == out.as_of + 1 and out.schema_hash and len(out.schema_hash) == 16
    return out.value


def _fd(out: object) -> FactorDirection:
    assert isinstance(out, Ok)
    return out.value


# ── cei patru factori, sub FactorDirection ────────────────────────────────────────────────────

def test_emits_four_factors_in_order_struct_disp_liq_mom() -> None:
    st = _state(compute_bias(*_synthetic(400), 400))
    assert len(st.factors) == 4
    assert _fd(st.factors[STRUCT]).name == "structure_run_h1"
    assert _fd(st.factors[DISP]).name == "displacement_h1"
    assert _fd(st.factors[LIQ]).name == "liquidity_above"
    assert isinstance(st.factors[MOM], Unavailable)              # momentum: fără nume (contract) — poziția 3


def test_directions_are_enum_not_raw_numbers() -> None:
    """Corecția defectului de ROL: direcția e un enum, nu un număr cu semn."""
    st = _state(compute_bias(*_synthetic(400), 400))
    for idx in (STRUCT, DISP, LIQ):
        assert isinstance(_fd(st.factors[idx]).direction, Direction)
    # `raw` rămâne disponibil pentru AUDIT, sub contract
    assert isinstance(_fd(st.factors[STRUCT]).raw, Ok)


def test_does_not_emit_any_probability_or_aggregate() -> None:
    """§1: N2 emite FACTORI, nu procent/scor — agregarea e a lui N6."""
    st = _state(compute_bias(*_synthetic(400), 400))
    fields = set(BiasState.__dataclass_fields__)
    assert not any("prob" in f or "score" in f for f in fields)
    assert "direction_share_long" in fields and "direction_share_short" in fields
    assert schema_payload()["emits_probability"] is False


def test_shares_are_descriptive_and_bounded() -> None:
    st = _state(compute_bias(*_synthetic(400), 400))
    assert st.direction_share_long is not None and st.direction_share_short is not None
    assert 0.0 <= st.direction_share_long <= 1.0 and 0.0 <= st.direction_share_short <= 1.0
    assert st.direction_share_long + st.direction_share_short <= 1.0 + 1e-9


def test_structure_sign_maps_to_direction() -> None:
    st = _state(compute_bias(*_synthetic(400), 400))
    fd = _fd(st.factors[STRUCT])
    raw = fd.raw
    assert isinstance(raw, Ok)
    expect = Direction.LONG if raw.value > 0 else Direction.SHORT if raw.value < 0 else Direction.UNKNOWN
    assert fd.direction is expect


# ── contract: UNKNOWN măsurat = Ok; necalculabil = Unavailable ──────────────────────────────────

def test_momentum_is_permanently_unavailable_outside_required_set() -> None:
    """§2/§4: momentum ABSENT → Unavailable PERMANENT, în afara mulțimii necesare (altfel N2 = fail-mort)."""
    st = _state(compute_bias(*_synthetic(400), 400))
    mom = st.factors[MOM]
    assert isinstance(mom, Unavailable) and mom.reason == "ABSENT_NO_RATIFIED_PRIMITIVE"
    assert not hasattr(mom, "value")                             # contractul: Unavailable nu are payload
    assert schema_payload()["factors_ordered"][MOM]["in_required_set"] is False
    assert schema_payload()["required_set"] == ["structure_run_h1"]


def test_zero_displacement_is_unknown_ok_not_unavailable() -> None:
    """§2: 0,0 (nicio expansiune) e MĂSURAT-și-neutru → Ok(UNKNOWN), NU Unavailable (lecția Z4-L1)."""
    # o serie plată forțează expansion=False pe ultima bară → disp=0.0
    n = N_MIN_BARS + 5
    flat_o = [2000.0] * n; flat_h = [2000.5] * n; flat_l = [1999.5] * n; flat_c = [2000.0] * n
    st = _state(compute_bias(flat_o, flat_h, flat_l, flat_c, n))
    disp = _fd(st.factors[DISP])
    assert disp.direction is Direction.UNKNOWN
    raw = disp.raw
    assert isinstance(raw, Ok) and raw.value == 0.0             # 0,0 e REZULTAT sub Ok, nu absență


# ── liquidity: prag (nu rang) + polaritate DECLARATĂ ────────────────────────────────────────────

def test_liquidity_counts_only_unswept_under_threshold() -> None:
    """§3: doar bazine neconsumate, filtru de PRAG — un prag mai larg nu poate reduce numărul."""
    def liq_raw(out: object) -> float:
        fd = _fd(_state(out).factors[LIQ]); r = fd.raw
        assert isinstance(r, Ok); return r.value
    n_narrow = liq_raw(compute_bias(*_synthetic(500), 500, k_atr=0.5))
    n_wide = liq_raw(compute_bias(*_synthetic(500), 500, k_atr=4.0))
    assert n_wide >= n_narrow


def test_threshold_filter_can_return_empty_set_direction_unknown() -> None:
    """§3: un PRAG poate produce mulțimea vidă (falsificabilitate); atunci direcția = UNKNOWN, nu SHORT."""
    st = _state(compute_bias(*_synthetic(500), 500, k_atr=1e-9))
    fd = _fd(st.factors[LIQ])
    r = fd.raw
    assert isinstance(r, Ok) and r.value == 0.0
    assert fd.direction is Direction.UNKNOWN


def test_liquidity_polarity_is_a_declared_assumption_in_schema() -> None:
    """§3: liquidity_above>0 → SHORT prin ASUMPȚIE, marcată și hash-uită (ATACABILĂ, nu rezolvată)."""
    st = _state(compute_bias(*_synthetic(500), 500, k_atr=4.0))   # prag larg ⇒ probabil >0 bazine
    fd = _fd(st.factors[LIQ])
    assert fd.assumption is True and fd.assumption_id == ASSUMPTION_LIQ_ABOVE
    for idx in (STRUCT, DISP):                                   # NUMAI liquidity poartă asumpție
        assert _fd(st.factors[idx]).assumption is False
    liq_schema = schema_payload()["factors_ordered"][LIQ]["params"]
    assert liq_schema["polarity"] == "SHORT" and liq_schema["assumption"] is True
    assert liq_schema["assumption_id"] == ASSUMPTION_LIQ_ABOVE   # intră în schema_hash


# ── fail-closed → Unavailable (nu o valoare presupusă), §6 ──────────────────────────────────────

def test_incomplete_window_is_unavailable() -> None:
    out = compute_bias(*_synthetic(400), N_MIN_BARS - 1)
    assert isinstance(out, Unavailable) and out.reason == "incomplete_window"


def test_empty_series_is_unavailable() -> None:
    out = compute_bias([], [], [], [], 0)
    assert isinstance(out, Unavailable)


def test_regime_all_axes_unavailable_cascades() -> None:
    """§6: RegimeState (N1) toate axele UNAVAILABLE → Unavailable prin cascadă."""
    out = compute_bias(*_synthetic(400), 400, regime_axes_status=["unavailable"] * 4)
    assert isinstance(out, Unavailable) and out.reason == "cascade_regime_all_axes_unavailable"


def test_single_unavailable_regime_axis_is_excluded_not_fatal() -> None:
    out = compute_bias(*_synthetic(400), 400,
                       regime_axes_status=["available", "unavailable", "unavailable", "unavailable"])
    assert isinstance(out, Ok)


def test_news_axis_alone_unavailable_does_not_block() -> None:
    out = compute_bias(*_synthetic(400), 400,
                       regime_axes_status=["available", "available", "available", "unavailable"])
    assert isinstance(out, Ok)


def test_no_status_field_on_biasstate() -> None:
    assert "status" not in BiasState.__dataclass_fields__       # statusul = constructorul Ok/Unavailable


# ── non-lookahead, §7.1 ──────────────────────────────────────────────────────────────────────

def _perturb(seq: Sequence[float], frm: int, delta: float) -> list[float]:
    out = list(seq)
    for j in range(frm, len(out)):
        out[j] += delta
    return out


def test_no_lookahead_perturbing_current_and_future_bars_changes_nothing() -> None:
    o, h, lo, c = _synthetic(600)
    i = 500
    base = compute_bias(o, h, lo, c, i)
    for delta in (+50.0, -50.0):
        pert = compute_bias(_perturb(o, i, delta), _perturb(h, i, delta),
                            _perturb(lo, i, delta), _perturb(c, i, delta), i)
        assert pert == base, f"factorii la i s-au schimbat la perturbarea barelor >= i (delta={delta})"


def test_no_lookahead_truncating_after_i_changes_nothing() -> None:
    o, h, lo, c = _synthetic(600)
    i = 400
    assert compute_bias(o, h, lo, c, i) == compute_bias(o[:i], h[:i], lo[:i], c[:i], i)


def test_reads_exactly_i_closed_bars() -> None:
    st = _state(compute_bias(*_synthetic(600), 420))
    assert st.n_closed_bars == 420 and st.as_of_index == 420


# ── falsificabilitate, §7.2 ──────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not os.path.exists(H1_CSV), reason="H1_from_M15_v2 absent")
def test_zero_eligible_fraction_is_materially_above_zero_on_real_series() -> None:
    st = _state(compute_bias(*_real(), 3000))
    assert st.zero_eligible_fraction is not None
    assert st.zero_eligible_fraction > 0.0, "saturație: factorul ar fi nefalsificabil"
    assert st.zero_eligible_fraction >= 0.836, "sub precedentul măsurat al primitivei B"


# ── constante, §7.5 ──────────────────────────────────────────────────────────────────────────

def test_constants_are_in_h1_units_and_no_foreign_constant_appears() -> None:
    assert DAY_H1 == 23 and WEEK_H1 == 115
    src_path, _ = default_paths()
    with open(src_path, "r", encoding="utf-8") as fh:
        body = [ln for ln in fh.read().splitlines()
                if not ln.strip().startswith("#") and "măsurat" not in ln]
    joined = "\n".join(body)
    for foreign in ("= 92", "= 460", "= 30\n"):
        assert foreign not in joined, f"constantă străină în corp: {foreign!r}"


def test_h1_trend_up_is_not_used() -> None:
    src_path, _ = default_paths()
    with open(src_path, "r", encoding="utf-8") as fh:
        assert "h1_trend_up" not in fh.read().split('"""', 2)[-1]


# ── inspecție statică / dezvăluire, §7.4 (mecanism păstrat ca interogare de sine stătătoare) ───

def test_redundancy_is_derived_from_source_not_from_a_list() -> None:
    src_path, cand_path = default_paths()
    if not os.path.exists(cand_path):
        pytest.skip("phase1_screening.py absent")
    mapping = redundancy_by_static_inspection(src_path, cand_path)
    assert mapping, "inspecția statică n-a găsit nicio primitivă partajată — improbabil, deci suspect"
    for prim, users in mapping.items():
        assert all(u.startswith("gen_cand") or u.startswith("MODULE_LEVEL_INJECTED") for u in users), prim


def test_vocabulary_excludes_data_structures_and_stdlib() -> None:
    vocab = ratified_vocabulary()
    for noise in ("float", "len", "max", "min", "range", "Block", "PoolSide", "BreakKind"):
        assert noise not in vocab, noise
    for real in ("detect_breaks", "detect_swings", "build_pools", "detect_sweeps", "expansion"):
        assert real in vocab, real


def test_schema_payload_is_ordered_and_declares_assumption_and_required_set() -> None:
    p = schema_payload()
    assert p["schema_version"] == SCHEMA_VERSION
    assert [f["name"] for f in p["factors_ordered"]] == [
        "structure_run_h1", "displacement_h1", "liquidity_above", "momentum"]
    assert p["windows_h1_units"] == {"day": DAY_H1, "week": WEEK_H1, "n_min_bars": N_MIN_BARS}
    assert p["required_set"] == ["structure_run_h1"]
    assert p["directional_semantics"]["zero_is"] == "unknown_measured"
    liq = p["factors_ordered"][LIQ]["params"]
    assert liq["unswept_only"] is True and liq["filter"] == "threshold_not_rank" and liq["k_atr"] == K_ATR


# ── regula de retragere, §7.3 ────────────────────────────────────────────────────────────────

def test_withdrawal_rule_is_expressible_and_fires_on_a_restatement() -> None:
    def agreement(a: Sequence[int], b: Sequence[int]) -> float:
        pairs = [(x, y) for x, y in zip(a, b) if x != 0 and y != 0]
        return sum(1 for x, y in pairs if (x > 0) == (y > 0)) / len(pairs) if pairs else 0.0

    def withdraw(agr: float) -> bool:
        return agr > 0.95

    identical = [1, -1, 1, 1, -1, -1, 1]
    assert agreement(identical, identical) == 1.0 and withdraw(agreement(identical, identical)) is True
    partial = [1, -1, 1, -1, -1, 1, 1]
    assert withdraw(agreement(identical, partial)) is False
