"""F1-only remediation (mandat "RANGE V4 F1-ONLY REMEDIATION AFTER RT-RANGE-0012").

Red Team's implementation audit (RT-RANGE-0012, `892355f`/E87) found the F5 units fix shipped in
`69af414` was NOT MACRO-isolated in effect on real bars (real ATR != 1.0): it changed the frozen MACRO
baseline 62/88 -> 58/88. The finding also named VE's own `test_macro_byte_identity_projection_hash_
48_windows` (deleted with this mandate, formerly in `test_f5_tol_cluster_units.py`) as VACUOUS -- it
ran the synthetic construction corpus exclusively at `atr=1.0`, the one value at which `tol_cluster *
atr_ref` is an exact no-op, so it could never have caught an ATR-dependent leak.

CEO chose remediation option (b): F1 only, F5 DEFERRED_RESEARCH_ONLY_NON_BLOCKING. The boundary-retest
guard in `range_semantic_v4_3.py` is reverted to its exact pre-F5 (`82f27c0`) form. This file replaces
the deleted F5 suite with two independent, non-vacuous proofs that the revert is real and complete:

1. STRUCTURAL (full coverage, not sampled): the exact 4-line pre-F5 guard body, extracted once via
   `git show 82f27c0:...`, is verified byte-identical in the running source; a full `git diff 82f27c0`
   of the whole file (recorded in the delivery report) shows the only remaining differences are the
   implementation-fingerprint constant/`__all__` entry and two additive snapshot/restore lines -- none
   of which execute during `observe()`. This is a stronger claim than any sampled test can make: it
   covers every code path, not a chosen set of inputs.

2. BEHAVIORAL, non-vacuous: the retest guard is exercised directly at FIVE distinct, mostly non-unit
   ATR values (0.65/1.0/1.85/3.2/10.0 -- spanning below/around/well-above the real XAUUSD M15 ATR14
   median ~1.87), proving the accept/reject outcome no longer depends on ATR at all (F5 present would
   have made this test fail -- a wide-band ATR would filter a swing a narrow-band ATR lets through, the
   exact effect this suite's now-deleted predecessor demonstrated deliberately as PASSING evidence for
   F5). The 48-window construction-corpus MACRO projection hash is likewise swept across the same five
   ATR values (not just 1.0), each anchored to a value computed on the CURRENT reverted code.

Real-bar/real-ATR confirmation (the actual gate Red Team used) remains Red Team's domain -- VE has no
escrow access for this mandate either (see delivery report); `verify_f1_only_macro_identity.py` in
`construction_reproduction/` is provided so Red Team can run the identical comparison directly against
the real 48 sealed windows.

Does not import/modify `tests/test_range_semantic_v4_3.py` (still forbidden) -- reuses its helpers via
import; that file stays byte-untouched (verified separately, empty `git diff`).
"""
from __future__ import annotations

import hashlib
import inspect
import json
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
    RangeSemanticProducerV43,
    SNAPSHOT_CONTRACT_MISMATCH,
    Structure,
)


def _active_macro(prod: RangeSemanticProducerV43) -> Structure:
    st = prod._active_macro
    assert st is not None
    return st


def _macro_with_frozen_boundary(atr_ref: float) -> tuple[RangeSemanticProducerV43, ConfigV43]:
    """Confirmă un MACRO (100..120.3 boundary) și setează `atr_ref`-ul lui la valoarea cerută, pentru
    control fin al distanței testate față de `tol_cluster` BRUT (fără scalare, post-revert)."""
    cfg = cfg43()
    macro_legs: list[tuple[float, int]] = [
        (100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)]
    bars = legs_bars(macro_legs)
    prod, out = run43_fixed_atr(bars, config=cfg, atr=atr_ref)
    _, last, _ = out[-1]
    assert last.macro_reason == "OK_RANGE_MACRO", last.macro_reason
    assert _active_macro(prod).up.frozen
    return prod, cfg


_ATR_SWEEP = (0.65, 1.0, 1.85, 3.2, 10.0)


# ═══════════════════════ 1. dovadă STRUCTURALĂ -- gardul revenit byte-identic la 82f27c0 ═══════════════════════

# Extras o singură dată, verbatim, din `git show 82f27c0:ve_n1_replay/ve_n1_replay/range_semantic_v4_3.py`
# (liniile 743-746 ale acelui blob) -- NU retranscris din memorie.
_PRE_F5_GUARD_BODY = (
    "        if forming_internal and self._active_macro is not None:\n"
    "            boundary = self._active_macro.up.center if is_high else self._active_macro.dn.center\n"
    "            if boundary is not None and abs(price - boundary) <= self._cfg.tol_cluster:\n"
    "                return\n"
)


def test_boundary_retest_guard_is_byte_identical_to_pre_f5_82f27c0_source() -> None:
    """Acoperire COMPLETĂ, nu eșantionată -- dacă gardul ar reintroduce orice scalare ATR, acest test
    ar eșua indiferent de ce valori de ATR ar rula testele comportamentale de mai jos."""
    src_path = Path(sys.modules["ve_n1_replay.range_semantic_v4_3"].__file__)  # type: ignore[arg-type]
    text = src_path.read_text(encoding="utf-8")
    assert _PRE_F5_GUARD_BODY in text, "gardul de re-testare a frontierei nu mai e byte-identic cu 82f27c0"


def test_guard_source_contains_no_atr_ref_reference() -> None:
    """Gardă independentă, complementară -- caută explicit absența `atr_ref` pe linia gardului
    (verificare pe funcție întreagă, nu doar substring-matching pe fișier)."""
    src = inspect.getsource(RangeSemanticProducerV43._offer_swing_everywhere)
    guard_lines = [ln for ln in src.splitlines() if "tol_cluster" in ln]
    assert guard_lines, "linia gardului (cu tol_cluster) nu a fost găsită în _offer_swing_everywhere"
    for ln in guard_lines:
        assert "atr_ref" not in ln, f"gardul reintroduce scalarea ATR: {ln!r}"


def test_implementation_fingerprint_correctly_labels_f1_only_not_f224e7d_not_f1_f5() -> None:
    assert RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT
    fp = RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT.lower()
    assert "f1-only" in fp
    assert fp != "f1-f5-conformance-2026-08-20", "nu trebuie să rămână cu amprenta pachetului RESPINS"


# ═══════════════════════ 2. dovadă COMPORTAMENTALĂ, ne-vacuă -- gardul e ATR-independent ═══════════════════════

def test_retest_guard_outcome_identical_across_five_distinct_atr_values() -> None:
    """F5 (amânat) ar fi făcut acest test să EȘUEZE: la ATR mare, banda scalată ar fi filtrat un swing
    pe care, la ATR mic, l-ar fi lăsat să treacă -- exact comportamentul pe care suita ștearsă îl
    demonstra intenționat ca dovadă PENTRU F5. Post-remediere, aceeași distanță absolută (2,5, peste
    `tol_cluster` brut = 1,60) trebuie tratată IDENTIC -- candidat nou legitim -- la orice ATR."""
    distance = 2.5
    outcomes = {}
    for atr in _ATR_SWEEP:
        prod, _ = _macro_with_frozen_boundary(atr_ref=atr)
        boundary = _active_macro(prod).up.center
        assert boundary is not None
        events: list[Any] = []
        prod._offer_swing_everywhere(200, boundary + distance, True, events)
        outcomes[atr] = prod._pending_up is not None
    assert all(outcomes.values()), f"distanța 2,5 ar trebui să treacă gardul la ORICE ATR: {outcomes}"


def test_retest_guard_filters_within_raw_tol_cluster_across_five_distinct_atr_values() -> None:
    """Complementar -- o distanță STRICT sub `tol_cluster` brut (1,60, fără scalare) trebuie filtrată
    (tratată ca re-testare) la orice ATR, INCLUSIV la ATR mare unde F5 ar fi lărgit banda suplimentar
    (comportament NEDORIT, tocmai motivul remedierii -- banda rămâne fixă, ne-scalată)."""
    distance = 1.0
    outcomes = {}
    for atr in _ATR_SWEEP:
        prod, _ = _macro_with_frozen_boundary(atr_ref=atr)
        boundary = _active_macro(prod).up.center
        assert boundary is not None
        events: list[Any] = []
        prod._offer_swing_everywhere(200, boundary + distance, True, events)
        outcomes[atr] = prod._pending_up is None
    assert all(outcomes.values()), f"distanța 1,0 ar trebui filtrată la ORICE ATR: {outcomes}"


def test_atr_ref_none_has_zero_effect_guard_never_reads_it() -> None:
    """Corectat față de asumpția erei-F5 (unde `atr_ref is None` dezactiva explicit filtrul): gardul
    revenit NU mai citește deloc `atr_ref`, deci setarea lui pe `None` nu are NICIUN efect -- rezultatul
    trebuie să fie IDENTIC cu cel obținut la un `atr_ref` numeric oarecare, la aceeași distanță (0,5,
    sub `tol_cluster` brut = 1,60 -> filtrat în ambele cazuri). Testul inițial (moștenit din suita F5
    ștearsă) presupunea greșit că `atr_ref=None` dezactivează filtrul -- a eșuat imediat la rulare,
    confirmând că revert-ul e complet (nici măcar ramura fail-closed specifică F5 nu a supraviețuit)."""
    prod_with_atr, _ = _macro_with_frozen_boundary(atr_ref=1.0)
    boundary_with = _active_macro(prod_with_atr).up.center
    assert boundary_with is not None
    events_with: list[Any] = []
    prod_with_atr._offer_swing_everywhere(200, boundary_with + 0.5, True, events_with)

    prod_none, _ = _macro_with_frozen_boundary(atr_ref=1.0)
    _active_macro(prod_none).atr_ref = None
    boundary_none = _active_macro(prod_none).up.center
    assert boundary_none is not None
    events_none: list[Any] = []
    prod_none._offer_swing_everywhere(200, boundary_none + 0.5, True, events_none)

    assert (prod_with_atr._pending_up is None) == (prod_none._pending_up is None), (
        "atr_ref=None a schimbat rezultatul gardului -- gardul citește din nou atr_ref undeva"
    )
    assert prod_none._pending_up is None, "distanța 0,5 < tol_cluster brut (1,60) trebuie filtrată"


def test_macro_formation_and_confirmation_unaffected() -> None:
    prod, _ = _macro_with_frozen_boundary(atr_ref=1.0)
    st = _active_macro(prod)
    assert st.reached_confirmed
    assert st.boundary_upper == pytest.approx(120.3, abs=0.1)
    assert st.boundary_lower == pytest.approx(99.7, abs=0.1)


# ═══════════════════════ chunking / restart / două instanțe ═══════════════════════

def test_chunk_invariance() -> None:
    cfg = cfg43()
    macro_legs: list[tuple[float, int]] = [
        (100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6),
        (108, 5), (112, 5), (108, 5), (112, 5)]
    bars = legs_bars(macro_legs)

    prod_whole, _ = run43_fixed_atr(bars, config=cfg, atr=1.0)

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


def test_two_instances_no_shared_state() -> None:
    prod1, _ = _macro_with_frozen_boundary(atr_ref=1.0)
    prod2, _ = _macro_with_frozen_boundary(atr_ref=1.85)
    boundary1 = _active_macro(prod1).up.center
    assert boundary1 is not None
    events1: list[Any] = []
    prod1._offer_swing_everywhere(200, boundary1 + 1.0, True, events1)   # filtrat pe prod1
    assert prod2._pending_up is None   # prod2 neatins de apelul de mai sus


def test_restart_between_breach_and_resolution_identical() -> None:
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


# ═══════════════════════ identitate / snapshot gating (mandat §C, §F) ═══════════════════════

def test_snapshot_new_fingerprint_accepted() -> None:
    cfg = cfg43()
    prod = RangeSemanticProducerV43(cfg)
    snap = prod.snapshot_state()
    assert snap["implementation_fingerprint"] == RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT
    prod2 = RangeSemanticProducerV43(cfg)
    prod2.restore_state(snap)   # nu trebuie să ridice


def test_snapshot_missing_fingerprint_refused_simulates_bare_f224e7d() -> None:
    """Un snapshot din `f224e7d`/`82f27c0` (dinainte de orice fingerprint de implementare) nu ar avea
    deloc cheia -- simulat prin ștergerea ei dintr-un snapshot altfel valid."""
    cfg = cfg43()
    prod = RangeSemanticProducerV43(cfg)
    snap = prod.snapshot_state()
    del snap["implementation_fingerprint"]
    prod2 = RangeSemanticProducerV43(cfg)
    with pytest.raises(ContractErrorV43) as exc_info:
        prod2.restore_state(snap)
    assert str(exc_info.value) == SNAPSHOT_CONTRACT_MISMATCH


def test_snapshot_rejected_f1_f5_fingerprint_refused() -> None:
    """Un snapshot din pachetul RESPINS `69af414` (F1+F5) NU trebuie să restaureze silențios aici,
    chiar dacă `contract_version`/`config_id` se potrivesc (nu s-au schimbat niciodată)."""
    cfg = cfg43()
    prod = RangeSemanticProducerV43(cfg)
    snap = prod.snapshot_state()
    snap["implementation_fingerprint"] = "f1-f5-conformance-2026-08-20"
    prod2 = RangeSemanticProducerV43(cfg)
    with pytest.raises(ContractErrorV43) as exc_info:
        prod2.restore_state(snap)
    assert str(exc_info.value) == SNAPSHOT_CONTRACT_MISMATCH


def test_snapshot_stale_or_corrupt_fingerprint_value_refused() -> None:
    cfg = cfg43()
    prod = RangeSemanticProducerV43(cfg)
    snap = prod.snapshot_state()
    snap["implementation_fingerprint"] = "some-unrelated-tag"
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


def test_restore_is_atomic_on_refusal() -> None:
    """Un restore refuzat nu trebuie să lase instanța țintă parțial mutată."""
    cfg = cfg43()
    prod_a, _ = _macro_with_frozen_boundary(atr_ref=1.0)
    snap_good = prod_a.snapshot_state()

    prod_target = RangeSemanticProducerV43(cfg)
    before = prod_target.snapshot_state()

    snap_bad = dict(snap_good)
    snap_bad["implementation_fingerprint"] = "f1-f5-conformance-2026-08-20"
    with pytest.raises(ContractErrorV43):
        prod_target.restore_state(snap_bad)

    after = prod_target.snapshot_state()
    assert before == after, "restore refuzat nu trebuie să modifice starea instanței țintă"


# ═════════════ MACRO byte-identity peste 48 ferestre, la CINCI valori ATR distincte (mandat §D) ═════════════

_CR_DIR = Path(__file__).resolve().parent.parent / "construction_reproduction"
sys.path.insert(0, str(_CR_DIR))


def _macro_projection_hash(atr_value: float) -> tuple[str, int]:
    """Rulează cele 48 de ferestre sintetice ale corpusului de construcție (reutilizate STRICT ca
    sursă de diversitate structurală pentru regresie -- NU ca revendicare de reproducere istorică,
    acel rol rămâne al `construction_reproduction/run_construction.py`, pinnat la `f224e7d`) prin
    implementarea CURENTĂ (F1-only, F5 revenit) la un ATR FIX dat, și întoarce hash-ul determinist al
    proiecției MACRO complete + numărul total de evenimente MACRO."""
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
            res, evs = prod.observe(ts_close=idx * 900, open_=o, high=h, low=lo, close=c, atr=atr_value)
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
    return hashlib.sha256(payload).hexdigest(), total_macro_events


# Ancore calculate O SINGURĂ DATĂ pe implementarea F1-only CURENTĂ (post-revert), la fiecare din cele
# cinci valori ATR ale sweep-ului -- NU doar la atr=1,0 (exact vacuitatea găsită de Red Team). Notă:
# ancora la atr=1,0 (81b0a7b3...c942591, 973 evenimente) coincide EXACT cu ancora calculată anterior pe
# codul cu F5 PREZENT (mandatul F1+F5) -- confirmare directă că atr=1,0 nu poate distinge "F5 prezent"
# de "F5 absent", motivul exact pentru care testul anterior era vacuu. Celelalte patru valori NU
# coincid cu nimic calculat anterior (F5 nu a fost niciodată testat la ele) și sunt dovada nouă,
# ne-vacuă, cerută de mandat.
_EXPECTED_PROJECTIONS: dict[float, tuple[str, int]] = {
    0.65: ("4ec40a81b2f1b8e4b8f552f6b1664eaad9cc6b7f34c8a70813f344234d069e91", 801),
    1.0:  ("81b0a7b3336d50ad4a950133963e6439e20cff5ba0635f6df967bee14c942591", 973),
    1.85: ("9d80775db970b6c8e0c9ea28d2039fd53678e5b831f458ccfe3a9972a7c8baa0", 940),
    3.2:  ("ef443e311ff1388a60c9bf777385fba9db65c0a87e30c4aab460c3b712ca00a7", 973),
    10.0: ("439da0c1131602984be463a09f1d47f4d60e4b145555ca3480518aafa04e327f", 1231),
}


@pytest.mark.parametrize("atr_value", sorted(_EXPECTED_PROJECTIONS))
def test_macro_projection_hash_at_non_unit_atr(atr_value: float) -> None:
    """Non-vacuu prin construcție: patru din cele cinci ATR NU sunt 1,0, deci orice reintroducere a
    unei scalări `atr_ref` în gardul de re-testare ar produce hash-uri diferite de ancorele de mai jos
    (deoarece o astfel de scalare ar filtra un NUMĂR diferit de candidați INTERNAL la fiecare ATR,
    care s-ar propaga -- exact mecanismul F5-MACRO-LEAK documentat de RT-RANGE-0012 -- în populația
    MACRO/proiecția finală)."""
    expected_hash, expected_events = _EXPECTED_PROJECTIONS[atr_value]
    actual_hash, actual_events = _macro_projection_hash(atr_value)
    assert actual_events == expected_events, f"atr={atr_value}: numărul de evenimente MACRO a variat"
    assert actual_hash == expected_hash, (
        f"atr={atr_value}: proiecția MACRO diferă de ancora de regresie -- posibilă reintroducere a "
        f"unei scalări ATR-dependente în calea forming-internal"
    )


def test_macro_projection_deterministic_across_repeated_runs() -> None:
    for atr_value in (1.0, 1.85):
        h1, c1 = _macro_projection_hash(atr_value)
        h2, c2 = _macro_projection_hash(atr_value)
        assert h1 == h2 and c1 == c2
