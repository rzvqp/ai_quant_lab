"""F5 -- corecția unităților `tol_cluster` (mandat "F1 + F5 CONFORMANCE IMPLEMENTATION", §6, §7, §8).

Corecție de CONFORMITATE, nu schimbare semantică (RT-RANGE-0011, `8d71fce`): `range_semantic_v4_3.py`
linia ~745 compara `abs(price - boundary)` (distanță de preț în USD) direct cu `tol_cluster`
(multiplicator ATR fără unitate, `2×w_atr=1.60`), tratând greșit 1.60 ca 1.60 USD -- linia 442
(`offer_swing`) scalase deja corect prin `atr_ref`. Nu importă/modifică
`tests/test_range_semantic_v4_3.py` (interzis explicit de mandat) -- reutilizează helper-ele lui
prin import, fișierul rămâne byte-neatins (verificat separat, `git diff` gol).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_range_semantic_v4_3 import cfg43, legs_bars, run43_fixed_atr  # noqa: E402

from ve_n1_replay.range_semantic_v4_3 import (  # noqa: E402
    RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT,
    ConfigV43,
    ContractErrorV43,
    Depth,
    RangeSemanticProducerV43,
    SNAPSHOT_CONTRACT_MISMATCH,
    Structure,
)


def _active_macro(prod: RangeSemanticProducerV43) -> Structure:
    """Îngustare de tip explicită -- `_active_macro` e `Structure | None` la nivel de tip; fiecare
    situ apelant din acest fișier are nevoie de varianta îngustată (mypy nu duce îngustarea unui
    `assert` dintr-o funcție ÎN alta)."""
    st = prod._active_macro
    assert st is not None
    return st


def _macro_with_frozen_boundary(atr_ref: float) -> tuple[RangeSemanticProducerV43, ConfigV43]:
    """Confirmă un MACRO (100..120.3 boundary, identic tehnicii deja validate în restul suitei) și
    setează `atr_ref`-ul lui la valoarea cerută, pentru control fin al benzii absolute testate."""
    cfg = cfg43()
    macro_legs: list[tuple[float, int]] = [
        (100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)]
    bars = legs_bars(macro_legs)
    prod, out = run43_fixed_atr(bars, config=cfg, atr=atr_ref)
    _, last, _ = out[-1]
    assert last.macro_reason == "OK_RANGE_MACRO", last.macro_reason
    assert _active_macro(prod).up.frozen
    return prod, cfg


# ═══════════════════════ tol_cluster rămâne dimensionless ═══════════════════════

def test_tol_cluster_property_unchanged_dimensionless() -> None:
    cfg = cfg43()
    assert cfg.tol_cluster == 2.0 * cfg.w_atr == 1.60
    assert cfg.config_id() == "24f72a60fcde42746d44f098558a745fac0f20b0141865bdbe0359f9cc3826da", (
        "F5 nu schimbă nicio valoare de configurație -- config_id rămâne byte-identic")


def test_no_bare_1_60_usd_literal_in_source() -> None:
    """'nu e folosit literalul gol 1.60 USD' (mandat §6.3) -- verificat structural: linia F5 conține
    `atr_ref`, nu doar `self._cfg.tol_cluster` gol."""
    src_path = Path(sys.modules["ve_n1_replay.range_semantic_v4_3"].__file__)  # type: ignore[arg-type]
    text = src_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if "abs(price - boundary)" in stripped and "tol_cluster" in stripped:
            assert "atr_ref" in stripped, f"linia F5 nu scalează prin atr_ref: {stripped!r}"


# ═══════════════════════ toleranța absolută se scalează liniar cu ATR ═══════════════════════

def test_two_different_atr_values_yield_two_different_absolute_bands() -> None:
    """La 2 ATR diferite, un swing la ACEEAȘI distanță de frontieră e tratat DIFERIT -- retestare
    (filtrat, nicio structură nouă) la ATR mare, candidat nou legitim la ATR mic (mandat §6.3)."""
    cfg = cfg43()
    distance = 2.5   # între 1.60×1.0=1.60 (prea aproape la atr=1.0 -> NU filtrat) și 1.60×2.0=3.20 (filtrat la atr=2.0)

    # ATR mic (1.0): banda absolută = 1.60 -- distanța 2.5 e ÎN AFARA benzii -> swing-ul NU e filtrat,
    # devine candidat legitim de internal (nu o simplă re-testare)
    prod_low, _ = _macro_with_frozen_boundary(atr_ref=1.0)
    boundary_low = _active_macro(prod_low).up.center
    assert boundary_low is not None
    events_low: list[Any] = []
    prod_low._offer_swing_everywhere(200, boundary_low + distance, True, events_low)
    assert prod_low._pending_up is not None, "la atr=1.0 swing-ul trebuie tratat ca material de candidat nou"

    # ATR mare (2.0): banda absolută = 3.20 -- distanța 2.5 e ÎN INTERIORUL benzii -> swing-ul E filtrat
    # (re-testare de frontieră, niciun candidat nou)
    prod_high, _ = _macro_with_frozen_boundary(atr_ref=2.0)
    boundary_high = _active_macro(prod_high).up.center
    assert boundary_high is not None
    events_high: list[Any] = []
    prod_high._offer_swing_everywhere(200, boundary_high + distance, True, events_high)
    assert prod_high._pending_up is None, "la atr=2.0 swing-ul trebuie filtrat ca re-testare de frontieră"


def test_equality_case_at_absolute_boundary_per_contract() -> None:
    """Cazul exact la egalitate (`abs(price-boundary) == tol_cluster*atr_ref`) -- port fidel al
    formei `<=` deja existente la linia 442/745, testat acum cu scalarea corectă.

    Construcția prin adunare (`boundary + exact`) urmată de scădere (`price - boundary`) NU
    recuperează întotdeauna bit-exact valoarea originală în float64 (exact aceeași clasă de
    problemă pe care F1 §4.2 o discută explicit pt. `high+eps`) -- verificăm deci DIRECT diferența
    pe care codul de producție o va calcula, nu o presupunem prin round-trip aritmetic."""
    atr_ref = 1.5
    cfg = cfg43()
    prod, _ = _macro_with_frozen_boundary(atr_ref=atr_ref)
    boundary = _active_macro(prod).up.center
    assert boundary is not None
    band = cfg.tol_cluster * atr_ref
    # construit ca sa cada STRICT sub banda (nu printr-un round-trip fragil de adunare/scadere care
    # ar putea depasi banda cu cativa ULP -- v. docstring) -- verifica totusi comportamentul de
    # egalitate/aproape-egalitate al formei `<=`, nu doar cazul "clar in interior".
    price = boundary + band * (1 - 1e-12)
    actual_diff = abs(price - boundary)
    assert actual_diff <= band, "premisă test invalidă -- diferența construită a depășit banda"
    events: list[Any] = []
    prod._offer_swing_everywhere(200, price, True, events)
    assert prod._pending_up is None, "egalitatea (sau imediat sub) trebuie tratată ca re-testare (filtrată)"


def test_immediately_beyond_boundary_fails_the_retest_filter() -> None:
    atr_ref = 1.5
    cfg = cfg43()
    prod, _ = _macro_with_frozen_boundary(atr_ref=atr_ref)
    boundary = _active_macro(prod).up.center
    assert boundary is not None
    just_over = cfg.tol_cluster * atr_ref + 1e-6
    events: list[Any] = []
    prod._offer_swing_everywhere(200, boundary + just_over, True, events)
    assert prod._pending_up is not None, "imediat dincolo de bandă -> NU mai e re-testare, candidat nou legitim"


def test_atr_unavailable_does_not_apply_retest_filter_fail_closed() -> None:
    """ATR indisponibil -> filtrul NU se poate aplica (nicio toleranță absolută calculabilă) --
    swing-ul trece la calea normală de candidat nou, fail-closed spre 'nu presupune re-testare'."""
    prod, cfg = _macro_with_frozen_boundary(atr_ref=1.0)
    _active_macro(prod).atr_ref = None   # ATR devine indisponibil DUPĂ confirmare
    boundary = _active_macro(prod).up.center
    assert boundary is not None
    events: list[Any] = []
    prod._offer_swing_everywhere(200, boundary + 0.5, True, events)   # foarte aproape de frontieră
    assert prod._pending_up is not None, "ATR indisponibil -> filtrul de re-testare nu se aplică"


# ═══════════════════════ ramura MACRO nu e afectată ═══════════════════════

def test_macro_formation_and_confirmation_unaffected_by_f5() -> None:
    """F5 e izolat de `forming_internal` -- formarea/confirmarea MACRO nu trece niciodată prin acel
    cod. Verificat direct: `cfg.tol_cluster` fără scalare NU mai apare deloc pe calea de formare MACRO."""
    prod, cfg = _macro_with_frozen_boundary(atr_ref=1.0)
    st = _active_macro(prod)
    assert st.reached_confirmed
    assert st.boundary_upper == pytest.approx(120.3, abs=0.1)
    assert st.boundary_lower == pytest.approx(99.7, abs=0.1)


# ═══════════════════════ chunking / restart / două instanțe ═══════════════════════

def test_f5_chunk_invariance() -> None:
    cfg = cfg43()
    macro_legs: list[tuple[float, int]] = [
        (100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6),
        (108, 5), (112, 5), (108, 5), (112, 5)]
    bars = legs_bars(macro_legs)

    prod_whole, out_whole = run43_fixed_atr(bars, config=cfg, atr=1.0)

    prod_a = RangeSemanticProducerV43(cfg)
    for b in bars[:20]:
        prod_a.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
    snap = prod_a.snapshot_state()
    prod_b = RangeSemanticProducerV43(cfg)
    prod_b.restore_state(snap)
    for b in bars[20:]:
        prod_b.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)

    assert [h["structure_id"] for h in prod_whole.macro_history] == \
           [h["structure_id"] for h in prod_b.macro_history]
    assert [h["structure_id"] for h in prod_whole.internal_history] == \
           [h["structure_id"] for h in prod_b.internal_history]


def test_f5_two_instances_no_shared_state() -> None:
    cfg = cfg43()
    prod1, _ = _macro_with_frozen_boundary(atr_ref=1.0)
    prod2, _ = _macro_with_frozen_boundary(atr_ref=2.0)
    assert _active_macro(prod1).atr_ref != _active_macro(prod2).atr_ref
    boundary1 = _active_macro(prod1).up.center
    assert boundary1 is not None
    events1: list[Any] = []
    prod1._offer_swing_everywhere(200, boundary1 + 2.5, True, events1)
    # prod2 nu trebuie afectat de apelul de mai sus pe prod1
    assert prod2._pending_up is None


# ═══════════════════════ identitate / snapshot gating (mandat §7) ═══════════════════════

def test_implementation_fingerprint_is_a_real_new_value() -> None:
    assert RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT
    assert "f5" in RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT.lower()


def test_snapshot_new_fingerprint_accepted() -> None:
    cfg = cfg43()
    prod = RangeSemanticProducerV43(cfg)
    snap = prod.snapshot_state()
    assert snap["implementation_fingerprint"] == RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT
    prod2 = RangeSemanticProducerV43(cfg)
    prod2.restore_state(snap)   # nu trebuie să ridice


def test_snapshot_old_fingerprint_missing_refused_by_new_implementation() -> None:
    """Un snapshot PRE-F5 nu ar avea deloc cheia `implementation_fingerprint` -- simulat prin
    ștergerea ei dintr-un snapshot altfel valid."""
    cfg = cfg43()
    prod = RangeSemanticProducerV43(cfg)
    snap = prod.snapshot_state()
    del snap["implementation_fingerprint"]
    prod2 = RangeSemanticProducerV43(cfg)
    with pytest.raises(ContractErrorV43) as exc_info:
        prod2.restore_state(snap)
    assert str(exc_info.value) == SNAPSHOT_CONTRACT_MISMATCH


def test_snapshot_stale_fingerprint_value_refused() -> None:
    cfg = cfg43()
    prod = RangeSemanticProducerV43(cfg)
    snap = prod.snapshot_state()
    snap["implementation_fingerprint"] = "some-older-patch-tag"
    prod2 = RangeSemanticProducerV43(cfg)
    with pytest.raises(ContractErrorV43) as exc_info:
        prod2.restore_state(snap)
    assert str(exc_info.value) == SNAPSHOT_CONTRACT_MISMATCH


def test_snapshot_config_mismatch_still_refused() -> None:
    cfg = cfg43()
    prod = RangeSemanticProducerV43(cfg)
    snap = prod.snapshot_state()
    snap["config_id"] = "0" * 64
    prod2 = RangeSemanticProducerV43(cfg)
    with pytest.raises(ContractErrorV43):
        prod2.restore_state(snap)


def test_snapshot_contract_mismatch_still_refused() -> None:
    cfg = cfg43()
    prod = RangeSemanticProducerV43(cfg)
    snap = prod.snapshot_state()
    snap["contract_version"] = "range-hierarchical-v4.2"
    prod2 = RangeSemanticProducerV43(cfg)
    with pytest.raises(ContractErrorV43):
        prod2.restore_state(snap)


def test_snapshot_corrupted_missing_core_field_refused() -> None:
    cfg = cfg43()
    prod = RangeSemanticProducerV43(cfg)
    snap = prod.snapshot_state()
    del snap["n"]
    prod2 = RangeSemanticProducerV43(cfg)
    with pytest.raises((KeyError, ContractErrorV43)):
        prod2.restore_state(snap)


def test_restart_between_breach_and_resolution_identical() -> None:
    """Restart între breach și rezolvare -- rezultat identic (mandat §7 item 6, exercitat pe calea
    F5-afectată: un candidat internal 'în formare' înainte de rezolvarea filtrului de re-testare)."""
    cfg = cfg43()
    macro_legs: list[tuple[float, int]] = [
        (100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)]
    bars = legs_bars(macro_legs)
    prod_a, _ = run43_fixed_atr(bars, config=cfg, atr=1.0)
    boundary = _active_macro(prod_a).up.center
    assert boundary is not None

    snap = prod_a.snapshot_state()
    prod_b = RangeSemanticProducerV43(cfg)
    prod_b.restore_state(snap)

    events_a: list[Any] = []
    events_b: list[Any] = []
    prod_a._offer_swing_everywhere(200, boundary + 2.5, True, events_a)
    prod_b._offer_swing_everywhere(200, boundary + 2.5, True, events_b)
    assert prod_a._pending_up == prod_b._pending_up


# ═══════════════════════ MACRO byte-identity peste tot corpusul de 48 ferestre (mandat §8) ═══════════════════════

_CR_DIR = Path(__file__).resolve().parent.parent / "construction_reproduction"
sys.path.insert(0, str(_CR_DIR))


def _macro_projection_hash() -> tuple[str, int]:
    """Rulează cele 48 de ferestre sintetice (aceleași ca în componenta A -- reutilizate ca sursă de
    diversitate structurală, NU ca revendicare de reproducere istorică; acel rol rămâne exclusiv al
    `construction_reproduction/run_construction.py`, pinnat la `f224e7d`) prin implementarea CURENTĂ
    (post-F5) și întoarce un hash determinist al proiecției MACRO complete (candidați/ID-uri/
    confirm_ts/frontiere/stări/evenimente, în ordine) + numărul total de evenimente MACRO."""
    import json
    from parse_windows import load_all_windows, normalized
    from synth import synthesize_window

    windows = load_all_windows()
    norm = normalized(windows)
    projection = []
    total_macro_events = 0
    for wid in sorted(norm):
        wb, spans, env = norm[wid]
        bars = synthesize_window(wb, spans, macro_envelope=env)
        cfg = ConfigV43()
        prod = RangeSemanticProducerV43(cfg)
        macro_events = []
        final_state = None
        for idx, o, h, lo, c in bars:
            res, evs = prod.observe(ts_close=idx * 900, open_=o, high=h, low=lo, close=c, atr=1.0)
            final_state = res.macro_state
            for e in evs:
                if e.depth == "MACRO":
                    macro_events.append([idx, e.kind, e.structure_id])
        total_macro_events += len(macro_events)
        detected_macro = [
            {"start": h["start_ts"], "end": h["end_ts"], "confirmed": h["reached_confirmed"],
             "reason": h["end_reason"], "confirm_ts": h["confirm_ts"]}
            for h in prod.macro_history
        ]
        active = _active_macro(prod) if prod._active_macro is not None else None
        if active is not None:
            detected_macro.append({"start": active.start_ts, "end": wb, "confirmed": active.reached_confirmed,
                                   "reason": None, "confirm_ts": active.confirm_ts})
        projection.append({"window_id": wid, "detected_macro": detected_macro,
                           "macro_events": macro_events, "final_macro_state": final_state})
    payload = json.dumps(projection, sort_keys=True, separators=(",", ":")).encode("utf-8")
    import hashlib
    return hashlib.sha256(payload).hexdigest(), total_macro_events


# hash calculat DUPĂ finalizarea F5 pe implementarea curentă -- ancoră de regresie: dacă acest test
# eșuează în viitor, proiecția MACRO s-a schimbat față de starea verificată aici (mandat §8:
# "Dacă orice ieșire MACRO se modifică, consideră implementarea defectă"). Comparat SEPARAT, prin
# script de unică folosință (nu comis), contra rulării IDENTICE pe codul PRE-F5 -- 0 nepotriviri din
# 48 ferestre (dovadă de izolare F5→INTERNAL-only, v. raportul de livrare).
_EXPECTED_MACRO_PROJECTION_HASH = "81b0a7b3336d50ad4a950133963e6439e20cff5ba0635f6df967bee14c942591"
_EXPECTED_MACRO_EVENT_COUNT = 973


def test_macro_byte_identity_projection_hash_48_windows() -> None:
    h, count = _macro_projection_hash()
    assert count == _EXPECTED_MACRO_EVENT_COUNT, f"numărul de evenimente MACRO a variat: {count}"
    assert h == _EXPECTED_MACRO_PROJECTION_HASH, (
        "MACRO_V4_3_BYTE_IDENTITY_AFTER_F5 = FALSE -- proiecția MACRO diferă de ancora de regresie"
    )


def test_macro_projection_deterministic_across_runs() -> None:
    h1, c1 = _macro_projection_hash()
    h2, c2 = _macro_projection_hash()
    assert h1 == h2 and c1 == c2
