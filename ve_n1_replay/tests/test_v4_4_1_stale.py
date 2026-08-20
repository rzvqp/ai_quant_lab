"""V4.4.1 T-STALE construction tests (mandat VE-RANGE-V4_4_1-STALE-IMPLEMENTATION-001 §21): STALE-1 through
STALE-15, exactly as named in the mandate. Construction/regression only -- NO FB14, NO MB3-001..048, per
CEO Directive `NO_FB14_SCORING`/`NO_MB3_ACCESS`/`NO_FRESH_BLIND`. These tests do not validate semantic
correctness against real market data; they prove the frozen (`e2b65bf`) and calibrated (`9116c2b`) design was
implemented faithfully against the REAL code, mirroring the exact direct-construction-plus-real-orchestration-
call methodology already established and precedented throughout `test_v4_4_*.py` (confirmed_macro(),
_step_macro()/_evaluate_macro_formation() called directly on a precisely-controlled Structure -- not
re-derived expectations, not organically-grown bars chosen to coincidentally hit the target state)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_range_semantic_v4_3 import legs_bars   # noqa: E402

from ve_n1_replay.range_semantic_v4_3 import Depth   # noqa: E402
from ve_n1_replay.range_semantic_v4_4 import ConfigV44, RangeSemanticProducerV44   # noqa: E402
from ve_n1_replay.range_semantic_v4_4_1 import (   # noqa: E402
    ConfigV441, REASONS_V441, STALE_CANDIDATE_ABANDONED, RangeSemanticProducerV441, StructureV441,
)


def cfg441(**kw: Any) -> ConfigV441:
    return ConfigV441(**kw)


def never_confirmed_macro(prod: RangeSemanticProducerV441, *, structure_id: int = 1, upper: float = 110.0,
                          lower: float = 100.0, atr_ref: float = 1.0, start_ts: int = 0,
                          cfg: ConfigV441 | None = None) -> StructureV441:
    """Candidat MACRO cu frontiera stabilita dar NICIODATA confirmat -- construit direct, acelasi patern ca
    `confirmed_macro()` din test_v4_4_transitions.py, ridicat un nivel, dar FARA frozen=True/reached_confirmed
    (exact opusul acelui helper: T-STALE se aplica DOAR candidatilor neconfirmati, freeze e2b65bf §2)."""
    cfg = cfg or cfg441()
    st = StructureV441(structure_id=structure_id, depth=Depth.MACRO, parent_structure_id=None,
                       start_ts=start_ts, trailing_window=cfg.W)
    st.atr_ref = atr_ref
    st.up.offer(upper, 1e18)
    st.dn.offer(lower, 1e18)
    prod._active_macro = st
    return st


def feed_rejections(st: StructureV441, pairs: list[tuple[int, str]]) -> None:
    """pairs: [(bar_index, 'H'|'L'), ...] -- injecteaza direct in evidenta marginita, control precis asupra
    secventei (aceeasi motivatie ca `confirmed_macro()`: teste deterministe de tranzitie)."""
    for b, side in pairs:
        st.record_rejected_touch_v441(b, is_high=(side == "H"))


# ═══════════════════════════════════ STALE-1: reachability proof ═══════════════════════════════════

def test_stale1_reachable_via_step_macro_direct() -> None:
    """Reproduce fixture-ul P1 din calibrare (9116c2b), acum peste _step_macro() REAL, nu simularea
    standalone."""
    prod = RangeSemanticProducerV441(cfg441())
    st = never_confirmed_macro(prod, structure_id=7, start_ts=5)
    feed_rejections(st, [(30, 'L'), (34, 'H'), (38, 'L'), (42, 'H'), (46, 'L'), (50, 'H'), (54, 'L')])
    events: list[Any] = []
    result = prod._step_macro(54, high=109.0, low=101.0, close=105.0, events=events)
    assert result == STALE_CANDIDATE_ABANDONED
    assert STALE_CANDIDATE_ABANDONED in REASONS_V441
    assert any(e.kind == STALE_CANDIDATE_ABANDONED for e in events)
    assert prod._active_macro is None


def test_stale1_reachable_via_real_offer_swing_everywhere_rejection_path() -> None:
    """Proba separata: linia NOUA din _offer_swing_everywhere (inregistrarea respingerii) chiar se declanseaza
    printr-o respingere GENUINA (offer_swing intoarce SWING_OUTSIDE_CLUSTER real), nu doar prin scurtatura
    record_rejected_touch_v441() folosita in restul suitei pt. control precis al secventei."""
    prod = RangeSemanticProducerV441(cfg441())
    st = never_confirmed_macro(prod, structure_id=3, upper=110.0, lower=100.0, atr_ref=1.0, start_ts=0)
    assert len(st._rejected_touches) == 0
    events: list[Any] = []
    # 130 e la >>tol_cluster*atr_ref (plafon w_atr_sanity_ceiling=1.3952 => tol_cluster<=2.79) fata de
    # centrul de 110 -- respingere GARANTATA, indiferent de valoarea implicita a lui w_atr
    prod._offer_swing_everywhere(20, 130.0, True, events)
    assert len(st._rejected_touches) == 1
    assert st._rejected_touches[0] == (20, "H")
    prod._offer_swing_everywhere(25, 70.0, False, events)
    assert len(st._rejected_touches) == 2
    assert st._rejected_touches[1] == (25, "L")


# ═══════════════════════════════════ STALE-2: new genuine RANGE after stale candidate ═══════════════════════════════════

def test_stale2_new_genuine_range_can_form_after_abandonment() -> None:
    """Dupa abandon (slot golit), un candidat NOU, organic, format prin bare REALE (observe() public), trebuie
    sa poata forma independent -- fara nicio urma reziduala a candidatului abandonat."""
    prod = RangeSemanticProducerV441(cfg441())
    st = never_confirmed_macro(prod, structure_id=1, start_ts=5)
    feed_rejections(st, [(30, 'L'), (34, 'H'), (38, 'L'), (42, 'H'), (46, 'L'), (50, 'H'), (54, 'L')])
    events: list[Any] = []
    result = prod._step_macro(54, high=109.0, low=101.0, close=105.0, events=events)
    assert result == STALE_CANDIDATE_ABANDONED
    assert prod._active_macro is None

    prod._n = 55
    bars = legs_bars([(150, 0), (170, 6), (150, 6), (170, 6), (150, 6), (170, 6), (150, 6)], start=55)
    seen_reasons: set[str] = set()
    seen_events: set[str] = set()
    for b in bars:
        res, evs = prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
        seen_reasons.add(res.macro_reason)
        seen_events.update(e.kind for e in evs)
    # candidatul nou parcurge un ciclu de viata COMPLET, real (nu doar "non-null") -- formare -> confirmare,
    # cu bookkeeping-ul de identitate de episod dovedit ca a rulat (EPISODE_REPLACEMENT leaga succesorul de
    # candidatul abandonat), nu doar un slot gol reumplut accidental
    assert "EPISODE_REPLACEMENT" in seen_events, "noul candidat trebuie legat prin identitate de episod"
    assert "OK_RANGE_MACRO" in seen_reasons, "noul candidat trebuie sa poata CONFIRMA complet, independent"
    assert prod._active_macro is not None and prod._active_macro.reached_confirmed is True


# ═══════════════════════════════════ STALE-3: slow genuine RANGE survives ═══════════════════════════════════

def test_stale3_slow_genuine_range_never_abandoned() -> None:
    """N1-shape din calibrare: atingeri rare dar TOATE acceptate (niciodata respinse) -- niciodata trebuie sa
    declanseze T-STALE, oricat de batran devine candidatul."""
    cfg = cfg441()
    prod = RangeSemanticProducerV441(cfg)
    st = never_confirmed_macro(prod, structure_id=1, start_ts=5, cfg=cfg)
    # zero respingeri -- eligibilitate structurala exista (frontiera stabilita) dar evidenta lipseste complet
    for i in range(5, 300):
        assert prod._t_stale_should_fire(st, i) is False, f"declansare falsa la bara {i} fara evidenta"


# ═══════════════════════════════════ STALE-4: directional market anti-churn, 200-bar stress ═══════════════════════════════════

def test_stale4_directional_market_no_churn_200_bars() -> None:
    """N7/N8-shape din calibrare, extins la 200 bare (acelasi test de stres deja facut in calibrare, acum
    peste codul REAL): respingeri predominant intr-o singura parte, cu o rara alternanta izolata -- niciodata
    suficienta alternanta genuina pt. a declansa."""
    cfg = cfg441()
    prod = RangeSemanticProducerV441(cfg)
    st = never_confirmed_macro(prod, structure_id=1, start_ts=0, cfg=cfg)
    fired_at: list[int] = []
    for i in range(1, 201):
        # respingere la fiecare 4 bare, aproape intotdeauna 'H', cu o alternanta izolata la fiecare 50 bare
        if i % 4 == 0:
            side = 'L' if i % 50 == 0 else 'H'
            st.record_rejected_touch_v441(i, is_high=(side == 'H'))
        if prod._t_stale_should_fire(st, i):
            fired_at.append(i)
    assert fired_at == [], f"T-STALE a declansat fals intr-o piata directionala la barele {fired_at}"


# ═══════════════════════════════════ STALE-5: replacement still faces ER/RND/traversal ═══════════════════════════════════

def test_stale5_replacement_candidate_still_faces_full_confirmation_gates() -> None:
    """Dupa abandon, candidatul NOU nu ocoleste confirmarea -- refolosind fixture-ul INSUFFICIENT_EFFICIENCY
    deja verificat numeric in test_v4_4_reason_code_reachability.py, candidatul nou trebuie sa fie RESPINS la
    poarta T3, nu auto-confirmat doar pt. ca a inlocuit un candidat stale."""
    cfg = cfg441()
    prod = RangeSemanticProducerV441(cfg)
    st = never_confirmed_macro(prod, structure_id=1, start_ts=5, cfg=cfg)
    feed_rejections(st, [(30, 'L'), (34, 'H'), (38, 'L'), (42, 'H'), (46, 'L'), (50, 'H'), (54, 'L')])
    events: list[Any] = []
    assert prod._step_macro(54, 109.0, 101.0, 105.0, events) == STALE_CANDIDATE_ABANDONED
    assert prod._active_macro is None

    closes_a = [100.0 + i for i in range(29)]   # monoton -- ER scazuta, exact fixture-ul din reachability
    st_new = StructureV441(structure_id=90, depth=Depth.MACRO, parent_structure_id=None, start_ts=55,
                           trailing_window=cfg.W)
    st_new.atr_ref = 1.0
    st_new.up.offer(77.9, 1e18); st_new.up.offer(77.9, 1e18)
    st_new.dn.offer(50.0, 1e18); st_new.dn.offer(50.0, 1e18)
    for c in closes_a:
        st_new._trailing_closes.append(c)
    prod._active_macro = st_new
    ev_new: list[Any] = []
    reason = prod._evaluate_macro_formation(st_new, 100, ev_new)
    assert reason != "OK_RANGE_MACRO"
    assert st_new.reached_confirmed is False, "candidatul nou NU trebuie confirmat automat -- fara ocolire"


# ═══════════════════════════════════ STALE-6: next-bar-only replacement ═══════════════════════════════════

def test_stale6_no_same_bar_replacement_slot_stays_empty_until_next_bar() -> None:
    """La bara la care T-STALE declanseaza, slotul ramane GOL -- niciun candidat nou nu apare pana la bara
    URMATOARE (freeze e2b65bf: 'next-bar-only', nicio reutilizare same-bar a swing-ului declansator)."""
    cfg = cfg441()
    prod = RangeSemanticProducerV441(cfg)
    st = never_confirmed_macro(prod, structure_id=1, start_ts=5, cfg=cfg)
    feed_rejections(st, [(30, 'L'), (34, 'H'), (38, 'L'), (42, 'H'), (46, 'L'), (50, 'H'), (54, 'L')])
    events: list[Any] = []
    result = prod._step_macro(54, 109.0, 101.0, 105.0, events)
    assert result == STALE_CANDIDATE_ABANDONED
    # imediat dupa apelul care abandoneaza, IN ACEEASI bara -- slotul ramane None, nimic nu-l repopuleaza
    # sincron in interiorul _step_macro insusi (formarea unui candidat nou trece exclusiv prin
    # _offer_swing_everywhere, apelat abia la bara URMATOARE de catre observe())
    assert prod._active_macro is None
    assert prod._pending_up is None and prod._pending_dn is None


# ═══════════════════════════════════ STALE-7: snapshot/restart identical around abandonment ═══════════════════════════════════

def _seeded_stale_candidate(cfg: ConfigV441) -> tuple[RangeSemanticProducerV441, StructureV441]:
    """Candidat neconfirmat cu evidenta de respingere PRE-INCARCATA (4 elemente, 3 flip-uri, la barele 1-4) --
    varsta minima (12) e SINGURA poarta care mai lipseste, deci T-STALE declanseaza EXACT la bara 12,
    determinist (verificat empiric inainte de a scrie testul: bare 1-11 inerte/ESTABLISHING_FEW_SWINGS, bara
    12 declanseaza) -- necesar ca sa plasez granita snapshot/restart EXACT in jurul bare de declansare, nu
    undeva arbitrar unde T-STALE nici nu ar fi in joc."""
    prod = RangeSemanticProducerV441(cfg)
    st = StructureV441(structure_id=1, depth=Depth.MACRO, parent_structure_id=None, start_ts=0,
                       trailing_window=cfg.W)
    st.atr_ref = 1.0
    st.up.offer(110.0, 1e18); st.dn.offer(100.0, 1e18)
    prod._active_macro = st
    feed_rejections(st, [(1, 'L'), (2, 'H'), (3, 'L'), (4, 'H')])
    return prod, st


def test_stale7_snapshot_restart_across_stale_abandonment_bar_identical() -> None:
    """Sparge replay-ul EXACT inainte, respectiv EXACT dupa bara 12 (bara de declansare, verificata empiric)
    -- rezultatul trebuie sa fie identic cu rularea continua in ambele cazuri."""
    cfg = cfg441()

    def run_continuous(n_bars: int) -> list[tuple[str, tuple[str, ...]]]:
        prod, st = _seeded_stale_candidate(cfg)
        out = []
        for i in range(1, n_bars + 1):
            events: list[Any] = []
            result = prod._step_macro(i, 106.0, 104.0, 105.0, events)
            out.append((result, tuple(e.kind for e in events)))
        return out

    continuous = run_continuous(15)
    assert continuous[11] == (STALE_CANDIDATE_ABANDONED, (STALE_CANDIDATE_ABANDONED,))   # bara 12, index 11
    assert all(r == "ESTABLISHING_FEW_SWINGS" for r, _ in continuous[:11])   # inert pana atunci, nevacuu

    for split_bar in (11, 12, 13):   # chiar INAINTE de, EXACT LA, si chiar DUPA bara de declansare
        prod, st = _seeded_stale_candidate(cfg)
        chunked: list[tuple[str, tuple[str, ...]]] = []
        for i in range(1, split_bar + 1):
            events: list[Any] = []
            result = prod._step_macro(i, 106.0, 104.0, 105.0, events)
            chunked.append((result, tuple(e.kind for e in events)))
        snap = prod.snapshot_state()
        prod2 = RangeSemanticProducerV441(cfg)
        prod2.restore_state(snap)
        for i in range(split_bar + 1, 16):
            events = []
            result = prod2._step_macro(i, 106.0, 104.0, 105.0, events)
            chunked.append((result, tuple(e.kind for e in events)))
        assert chunked == continuous, f"diverge la granita split_bar={split_bar}"


# ═══════════════════════════════════ STALE-8: prefix/chunk invariance ═══════════════════════════════════

def test_stale8_prefix_invariance_with_rejected_evidence_accumulating() -> None:
    """Cresterea containerului nu rescrie niciodata rezultatele barelor anterioare, chiar cand un candidat
    stale acumuleaza evidenta de respingere in fundal."""
    cfg = cfg441()

    def run(bars_slice: list[Any]) -> list[dict[str, Any]]:
        p = RangeSemanticProducerV441(cfg)
        out = []
        for b in bars_slice:
            res, evs = p.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
            out.append({"macro_id": res.macro_id, "macro_reason": res.macro_reason,
                       "macro_state": res.macro_state, "events": tuple(e.kind for e in evs)})
        return out

    bars = legs_bars([(100, 0), (140, 3), (100, 3), (140, 3), (100, 3), (140, 3), (100, 3),
                      (140, 3), (100, 3), (140, 3), (100, 3)])
    reference = run(bars)
    for n in (10, 20, 30, 40):
        partial = run(bars[:n])
        assert partial == reference[:n], f"prefixul de {n} bare difera de referinta"


# ═══════════════════════════════════ STALE-9: V4.4 behavior unchanged absent T-STALE ═══════════════════════════════════

def test_stale9_v4_4_unchanged_when_no_stale_condition_occurs() -> None:
    """Pe un fixture care confirma rapid (nicio conditie T-STALE posibila), V4.4 si V4.4.1 trebuie sa produca
    secvente IDENTICE de macro_reason/macro_state/events, bara cu bara -- nicio schimbare de comportament in
    absenta conditiei noi."""
    bars = legs_bars([(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6),
                      (108, 5), (112, 5), (108, 5), (112, 5), (108, 5)])
    prod44 = RangeSemanticProducerV44(ConfigV44())
    prod441 = RangeSemanticProducerV441(cfg441())
    for b in bars:
        r44, e44 = prod44.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
        r441, e441 = prod441.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
        assert r44.macro_reason == r441.macro_reason
        assert r44.macro_state == r441.macro_state
        assert r44.macro_id == r441.macro_id
        assert tuple(e.kind for e in e44) == tuple(e.kind for e in e441)


# ═══════════════════════════════════ STALE-10: INTERNAL parity unchanged ═══════════════════════════════════

def test_stale10_internal_parity_unchanged_vs_v4_4() -> None:
    """Mirroring test_v4_4_internal_parity.py's own methodology (V4.3-vs-V4.4), ridicat un nivel: V4.4.1 e
    subclasa TRUE a lui V4.4 (campuri V4.3/V4.4 identice implicit), deci compararea directa nu are nevoie de
    maparea de campuri pe care V4.3-vs-V4.4 a necesitat-o."""
    fixtures = [
        legs_bars([(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6),
                  (108, 5), (112, 5), (108, 5), (112, 5), (108, 5), (112, 5)]),
        legs_bars([(100, 0), (200, 40)]),
    ]
    for bars in fixtures:
        prod44 = RangeSemanticProducerV44(ConfigV44())
        prod441 = RangeSemanticProducerV441(cfg441())
        for b in bars:
            r44, _ = prod44.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
            r441, _ = prod441.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
            assert r44.internal_id == r441.internal_id
            assert r44.internal_reason == r441.internal_reason
            assert r44.internal_state == r441.internal_state
            assert r44.internal_boundary_upper == r441.internal_boundary_upper
            assert r44.internal_boundary_lower == r441.internal_boundary_lower


# ═══════════════════════════════════ STALE-11/12: min_alternation fragility, disclosed CONSTRUCTION_ONLY ═══════════════════════════════════

def test_stale11_mutation_min_alternation_2_fires_on_the_fragile_negative_control() -> None:
    """CONSTRUCTION_ONLY_ZERO_VALIDATION_WEIGHT (mandat §7/§17): min_alternation=2 e DELIBERAT prea permisiv --
    declanseaza pe cazul N8 (canal ingust cu UN singur pullback izolat, 2 flip-uri) pe care registrul calibrat
    (min_alternation=3) il respinge corect. Documenteaza fragilitatea, NU o repara -- pastrata explicit
    (freeze §17, calibrare 9116c2b §5.3)."""
    cfg_mutated = cfg441(STALE_MIN_ALTERNATION=2, STALE_MIN_REJECTIONS=3)   # respecta podeaua validate()
    prod = RangeSemanticProducerV441(cfg_mutated)
    st = never_confirmed_macro(prod, structure_id=1, start_ts=3, cfg=cfg_mutated)
    # N8-shape: H H H L H H H (7 elemente, 2 flip-uri: H->L la poz 3, L->H la poz 4)
    feed_rejections(st, [(30, 'H'), (34, 'H'), (38, 'H'), (41, 'L'), (44, 'H'), (48, 'H'), (52, 'H')])
    assert prod._t_stale_should_fire(st, 52) is True, \
        "mutatia min_alternation=2 trebuie sa declanseze fals pe cazul fragil N8 -- daca NU declanseaza, " \
        "testul insusi si-a pierdut sensul (verifica podeaua/fixture-ul)"

    # ACELASI fixture sub registrul CALIBRAT (min_alternation=3) -- NU trebuie sa declanseze (negative control)
    cfg_frozen = cfg441()
    prod_frozen = RangeSemanticProducerV441(cfg_frozen)
    st_frozen = never_confirmed_macro(prod_frozen, structure_id=1, start_ts=3, cfg=cfg_frozen)
    feed_rejections(st_frozen, [(30, 'H'), (34, 'H'), (38, 'H'), (41, 'L'), (44, 'H'), (48, 'H'), (52, 'H')])
    assert prod_frozen._t_stale_should_fire(st_frozen, 52) is False


def test_stale12_mutation_min_alternation_4_misses_the_positive_control() -> None:
    """CONSTRUCTION_ONLY_ZERO_VALIDATION_WEIGHT: min_alternation=4 e DELIBERAT prea strict -- rateaza un caz
    pozitiv cu EXACT 3 flip-uri reale (L-H-L-H-H, 5 elemente) pe care registrul calibrat (min_alternation=3)
    il accepta corect. Fixture ales cu 5 elemente (nu 4) special ca sa izoleze poarta de ALTERNANTA de poarta
    de NUMAR: `STALE_MIN_REJECTIONS=5` (podeaua validate() pt. alternation=4) e deja SATISFACUTA de cele 5
    elemente -- deci refuzul de mai jos vine STRICT din alternanta insuficienta (3 < 4), nu dintr-un numar
    insuficient de respingeri conflat accidental cu ea."""
    cfg_mutated = cfg441(STALE_MIN_ALTERNATION=4, STALE_MIN_REJECTIONS=5)
    fixture = [(30, 'L'), (34, 'H'), (38, 'L'), (42, 'H'), (46, 'H')]   # L H L H H -- 3 flip-uri, 5 elemente

    st2 = StructureV441(structure_id=2, depth=Depth.MACRO, parent_structure_id=None, start_ts=5,
                        trailing_window=cfg_mutated.W)
    st2.atr_ref = 1.0; st2.up.offer(110.0, 1e18); st2.dn.offer(100.0, 1e18)
    feed_rejections(st2, fixture)
    in_window2 = st2.rejected_touches_in_window(46, cfg_mutated.STALE_WINDOW)
    flips2 = sum(1 for a, b in zip(in_window2, in_window2[1:]) if a != b)
    assert len(in_window2) == 5 and flips2 == 3   # poarta de numar SATISFACUTA, doar alternanta insuficienta
    prod2 = RangeSemanticProducerV441(cfg_mutated)
    prod2._active_macro = st2
    assert prod2._t_stale_should_fire(st2, 46) is False, \
        "mutatia min_alternation=4 trebuie sa rateze cazul cu exact 3 flip-uri reale (numarul fiind suficient)"

    # ACELASI fixture sub registrul CALIBRAT -- TREBUIE sa declanseze (pozitiv, nu ratat)
    cfg_frozen = cfg441()
    st3 = StructureV441(structure_id=3, depth=Depth.MACRO, parent_structure_id=None, start_ts=5,
                        trailing_window=cfg_frozen.W)
    st3.atr_ref = 1.0; st3.up.offer(110.0, 1e18); st3.dn.offer(100.0, 1e18)
    feed_rejections(st3, fixture)
    prod3 = RangeSemanticProducerV441(cfg_frozen)
    prod3._active_macro = st3
    assert prod3._t_stale_should_fire(st3, 46) is True


# ═══════════════════════════════════ STALE-13: window boundary 29 exact ═══════════════════════════════════

def test_stale13_window_expiry_boundary_29_bars_exact() -> None:
    """rejected_touches_in_window(as_of, window) foloseste `b > as_of - window` (strict) -- o respingere
    EXACT la `as_of - window` e EXCLUSA, la `as_of - window + 1` e INCLUSA (freeze §5: fereastra trailing
    marginita, recalculata la cerere)."""
    cfg = cfg441()
    st = StructureV441(structure_id=1, depth=Depth.MACRO, parent_structure_id=None, start_ts=0,
                       trailing_window=cfg.W)
    as_of = 100
    window = cfg.STALE_WINDOW
    assert window == 29
    st.record_rejected_touch_v441(as_of - window, is_high=True)       # bara 71 -- EXACT pe margine, EXCLUS
    in_window_edge = st.rejected_touches_in_window(as_of, window)
    assert len(in_window_edge) == 0, "o respingere EXACT la as_of-window trebuie exclusa (strict >)"

    st2 = StructureV441(structure_id=2, depth=Depth.MACRO, parent_structure_id=None, start_ts=0,
                        trailing_window=cfg.W)
    st2.record_rejected_touch_v441(as_of - window + 1, is_high=True)  # bara 72 -- prima bara INCLUSA
    in_window_included = st2.rejected_touches_in_window(as_of, window)
    assert len(in_window_included) == 1, "o respingere la as_of-window+1 trebuie inclusa"


# ═══════════════════════════════════ STALE-14: age boundary 11 vs 12 exact ═══════════════════════════════════

def test_stale14_min_age_boundary_11_vs_12_exact() -> None:
    cfg = cfg441()
    assert cfg.STALE_MIN_AGE == 12
    prod = RangeSemanticProducerV441(cfg)

    st_11 = never_confirmed_macro(prod, structure_id=1, start_ts=40, cfg=cfg)   # varsta la i=51 => 11
    feed_rejections(st_11, [(45, 'L'), (47, 'H'), (49, 'L'), (51, 'H')])
    assert prod._t_stale_should_fire(st_11, 51) is False, "varsta 11 < STALE_MIN_AGE=12 trebuie sa blocheze"

    prod2 = RangeSemanticProducerV441(cfg)
    st_12 = never_confirmed_macro(prod2, structure_id=2, start_ts=40, cfg=cfg)   # varsta la i=52 => 12
    feed_rejections(st_12, [(45, 'L'), (47, 'H'), (49, 'L'), (52, 'H')])
    assert prod2._t_stale_should_fire(st_12, 52) is True, "varsta EXACT 12 trebuie sa satisfaca poarta"


# ═══════════════════════════════════ STALE-15: rejected count boundary 3 vs 4 exact ═══════════════════════════════════

def test_stale15_min_rejections_boundary_3_vs_4_exact() -> None:
    """Cu min_alternation=3 (registrul calibrat), podeaua matematica (validate(): rejections >= alternation+1)
    inseamna ca 3 respingeri NU pot satisface NICIODATA alternanta minima de 3 (maxim 2 flip-uri posibile din
    3 elemente) -- ambele porti actioneaza impreuna la aceasta frontiera exacta, un fapt structural al
    registrului calibrat, nu un artefact al testului."""
    cfg = cfg441()
    assert cfg.STALE_MIN_REJECTIONS == 4 and cfg.STALE_MIN_ALTERNATION == 3
    prod = RangeSemanticProducerV441(cfg)

    st_3 = never_confirmed_macro(prod, structure_id=1, start_ts=0, cfg=cfg)
    feed_rejections(st_3, [(30, 'H'), (34, 'L'), (38, 'H')])   # 3 elemente, alternanta maxima posibila (2)
    assert prod._t_stale_should_fire(st_3, 38) is False

    prod2 = RangeSemanticProducerV441(cfg)
    st_4 = never_confirmed_macro(prod2, structure_id=2, start_ts=0, cfg=cfg)
    feed_rejections(st_4, [(30, 'H'), (34, 'L'), (38, 'H'), (42, 'L')])   # 4 elemente, 3 flip-uri -- satisface
    assert prod2._t_stale_should_fire(st_4, 42) is True


# ═══════════════════════════════════ protectii suplimentare (mandat §12/§17: dincolo de cele 15 denumite, dar
# cerute explicit de mandat -- expuse prin exercitiul de gandire pt. cele 8 mutatii numite, inainte de a le
# rula, nu descoperite dupa) ═══════════════════════════════════

def test_stale_confirmed_structure_immune_even_with_qualifying_rejection_evidence() -> None:
    """Mandat: T-STALE se aplica STRICT candidatilor neconfirmati -- niciodata CONFIRMED/WEAKENING/INTERNAL.
    Construieste o structura CONFIRMATA cu evidenta de respingere care AR satisface T-STALE daca ar fi
    neconfirmata (varsta/numar/alternanta toate satisfacute) -- poarta externa `if zones is None` din
    _step_macro trebuie sa excluda structural evaluarea T-STALE, indiferent de evidenta acumulata."""
    cfg = cfg441()
    prod = RangeSemanticProducerV441(cfg)
    st = StructureV441(structure_id=1, depth=Depth.MACRO, parent_structure_id=None, start_ts=0,
                       trailing_window=cfg.W)
    st.atr_ref = 1.0
    st.up.offer(110.0, 1e18); st.up.offer(110.0, 1e18); st.up.frozen = True
    st.dn.offer(100.0, 1e18); st.dn.offer(100.0, 1e18); st.dn.frozen = True
    st.reached_confirmed = True; st.confirm_ts = 0
    prod._active_macro = st
    feed_rejections(st, [(30, 'L'), (34, 'H'), (38, 'L'), (42, 'H'), (46, 'L'), (50, 'H'), (54, 'L')])
    # confirmare independenta ca evidenta ARFI suficienta pt. un candidat neconfirmat echivalent
    assert prod._t_stale_should_fire(st, 54) is True, \
        "fixture-ul trebuie sa satisfaca T-STALE pe cont propriu -- altfel testul nu dovedeste nimic"
    # dar prin orchestrarea REALA (_step_macro), structura CONFIRMATA nu poate fi niciodata omorata de T-STALE
    for k in range(29):
        st.push_close_v44(k, 102.0 if k % 2 == 0 else 108.0)   # in banda, ER/RND benigne -- fara T5 accidental
    events: list[Any] = []
    result = prod._step_macro(54, 106.0, 104.0, 105.0, events)
    assert result != STALE_CANDIDATE_ABANDONED
    assert not any(e.kind == STALE_CANDIDATE_ABANDONED for e in events)
    assert prod._active_macro is st, "structura CONFIRMATA nu trebuie omorata de T-STALE prin _step_macro"


def test_stale_restore_state_refuses_mismatched_identity_at_producer_level() -> None:
    """Mirroring test_restore_state_refuses_wrong_contract_version din test_v4_4_snapshot_robustness.py,
    ridicat la V4.4.1: contract_version/config_id/implementation_fingerprint gresite sunt refuzate fail-closed
    la nivel de PRODUCATOR (restore_state), fara nicio mutatie partiala de stare."""
    cfg = cfg441()
    prod = RangeSemanticProducerV441(cfg)
    bars = legs_bars([(100, 0), (120, 6), (100, 6), (120, 6), (100, 6)])
    for b in bars:
        prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
    snap = prod.snapshot_state()

    for bad_key, bad_value in (("contract_version", "range-hierarchical-v4.4"),
                               ("config_id", "0" * 64),
                               ("implementation_fingerprint", "TAMPERED")):
        tampered = dict(snap); tampered[bad_key] = bad_value
        prod2 = RangeSemanticProducerV441(cfg)
        pre_state = prod2.snapshot_state()
        raised = False
        try:
            prod2.restore_state(tampered)
        except Exception:
            raised = True
        assert raised, f"restore_state trebuie sa refuze {bad_key} nepotrivit"
        assert prod2.snapshot_state() == pre_state, f"nicio mutatie partiala dupa refuzul pe {bad_key}"
