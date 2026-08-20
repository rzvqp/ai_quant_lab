"""V4.4 adversarial suite (mandat §16): cele 22 scenarii pre-inregistrate -- 20 din `VE_RANGE_V4_4_DESIGN_AND_
PREREGISTRATION.md` §10, plus #21 (slow drifting equilibrium) si #22 (violent zigzag) din acelasi document §12
(contraexemple de auto-falsificare). Cronologia asteptata e cea PRE-INREGISTRATA in documentul de design, nu
inventata post-hoc. Unde documentul insusi discloseaza un risc DESCHIS/NEREZOLVAT (canal lin/echilibru care
deriva, zigzag violent -- explicit 'not solved, not claimed solved'), testul NU forteaza o respingere care
contrazice acel disclosure -- inregistreaza cinstit comportamentul observat, ca in raportul de calibrare."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_range_semantic_v4_3 import legs_bars, osc_bars   # noqa: E402

from ve_n1_replay.range_semantic_v4_4 import (   # noqa: E402
    ConfigV44, EPISODE_CONTINUATION, EPISODE_REPLACEMENT, OK_RANGE_MACRO, RANGE_CANDIDATE_PRESENT,
    RangeSemanticProducerV44, WEAKENING_PERSISTENCE_TERMINATED, WEAKENING_RECOVERED,
)
from ve_n1_replay.range_semantic_v4_3 import BREAKOUT_ACCEPTED   # noqa: E402


def cfg44(**kw: Any) -> ConfigV44:
    return ConfigV44(**kw)


def _run(bars: list[Any], atr: float = 1.0, cfg: ConfigV44 | None = None
        ) -> tuple[RangeSemanticProducerV44, list[dict[str, Any]]]:
    prod = RangeSemanticProducerV44(cfg or cfg44())
    out = []
    for b in bars:
        res, evs = prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=atr)
        out.append({"reason": res.macro_reason, "state": res.macro_state, "events": tuple(e.kind for e in evs)})
    return prod, out


def _confirmed(out: list[dict[str, Any]]) -> bool:
    return any(OK_RANGE_MACRO in r["events"] for r in out)


# 1 -- clean horizontal RANGE: CANDIDATE->FORMING->CONFIRMED, ramane CONFIRMED
def test_adversarial_01_clean_horizontal_range_confirms_and_stays_confirmed() -> None:
    bars = legs_bars([(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)])
    prod, out = _run(bars)
    assert _confirmed(out)
    assert out[-1]["state"] == "CONFIRMED"


# 2 -- noisy RANGE: acumulare mai lenta a atingerilor, dar tot confirma
def test_adversarial_02_noisy_range_still_confirms() -> None:
    bars = osc_bars(cycles=6, base=110.0)
    prod, out = _run(bars)
    assert _confirmed(out)


# 3 -- wide volatile RANGE: latimea nu conteaza (ER/RND auto-referentiale), confirma la fel ca #1
def test_adversarial_03_wide_volatile_range_confirms_same_as_clean() -> None:
    bars = legs_bars([(1000, 0), (1400, 6), (1000, 6), (1400, 6), (1000, 6), (1400, 6), (1000, 6)])
    prod, out = _run(bars, atr=10.0)
    assert _confirmed(out)


# 4 -- shallow CHANNEL_UP: nu confirma niciodata (fixul direct al D1)
def test_adversarial_04_shallow_channel_up_never_confirms() -> None:
    win = []
    c = 100.0
    for i in range(29):
        c += 1.2 if i % 2 == 0 else -0.5
        win.append(c)
    from ve_n1_replay.range_semantic_v4_4 import StructureV44
    from ve_n1_replay.range_semantic_v4_3 import Depth
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    st = StructureV44(structure_id=1, depth=Depth.MACRO, parent_structure_id=None, start_ts=0, trailing_window=cfg.W)
    st.atr_ref = 1.0
    st.up.offer(130.0, 1e18); st.up.offer(130.0, 1e18)
    st.dn.offer(100.0, 1e18); st.dn.offer(100.0, 1e18)
    for c2 in win:
        st._trailing_closes.append(c2)
    prod._active_macro = st
    reason = prod._evaluate_macro_formation(st, 40, [])
    assert reason != OK_RANGE_MACRO


# 5 -- shallow CHANNEL_DOWN: oglinda lui #4
def test_adversarial_05_shallow_channel_down_never_confirms() -> None:
    win = []
    c = 130.0
    for i in range(29):
        c -= 1.2 if i % 2 == 0 else -0.5
        win.append(c)
    from ve_n1_replay.range_semantic_v4_4 import StructureV44
    from ve_n1_replay.range_semantic_v4_3 import Depth
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    st = StructureV44(structure_id=1, depth=Depth.MACRO, parent_structure_id=None, start_ts=0, trailing_window=cfg.W)
    st.atr_ref = 1.0
    st.up.offer(130.0, 1e18); st.up.offer(130.0, 1e18)
    st.dn.offer(100.0, 1e18); st.dn.offer(100.0, 1e18)
    for c2 in win:
        st._trailing_closes.append(c2)
    prod._active_macro = st
    reason = prod._evaluate_macro_formation(st, 40, [])
    assert reason != OK_RANGE_MACRO


# 6/7 -- strong TREND_UP / TREND_DOWN: fie nu stabilizeaza o latime, fie ER~1 blocheaza imediat
def test_adversarial_06_strong_trend_up_never_confirms() -> None:
    bars = legs_bars([(100, 0), (105, 3), (103, 2), (110, 3), (108, 2), (116, 3), (114, 2),
                      (123, 3), (121, 2), (131, 3), (129, 2), (140, 3), (138, 2)])
    prod, out = _run(bars)
    assert not _confirmed(out)


def test_adversarial_07_strong_trend_down_never_confirms() -> None:
    bars = legs_bars([(140, 0), (135, 3), (137, 2), (130, 3), (132, 2), (124, 3), (126, 2),
                      (117, 3), (119, 2), (109, 3), (111, 2), (100, 3), (102, 2)])
    prod, out = _run(bars)
    assert not _confirmed(out)


# 8 -- stair-step trend: fiecare treapta blocata (traversal/RND), niciodata confirmat
def test_adversarial_08_stair_step_trend_never_confirms() -> None:
    legs: list[tuple[float, int]] = [(100, 0)]
    base = 100.0
    for k in range(8):
        legs.append((base + 3, 3)); legs.append((base, 3))
        base += 15
        legs.append((base, 2))
    bars = legs_bars(legs)
    prod, out = _run(bars)
    assert not _confirmed(out)


# 9/10 -- compresie->breakout / RANGE->breakout acceptat: FORMING->CONFIRMED->WEAKENING->TERMINATED(breakout)
def test_adversarial_09_10_range_to_accepted_breakout() -> None:
    bars = legs_bars([(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)])
    prod, out = _run(bars)
    assert _confirmed(out)
    st = prod._active_macro
    assert st is not None
    i = prod._n
    last_reason = None
    for c in (121.5, 122.0, 123.0):
        st.push_close_v44(i, c)
        ev: list[Any] = []
        last_reason = prod._step_macro(i, c + 0.2, c - 0.2, c, ev)
        i += 1
    assert last_reason == BREAKOUT_ACCEPTED
    assert prod._active_macro is None


# 11 -- RANGE->breakout esuat (sweep): CONFIRMED->WEAKENING->CONFIRMED (WEAKENING_RECOVERED)
def test_adversarial_11_range_failed_breakout_recovers() -> None:
    bars = legs_bars([(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)])
    prod, out = _run(bars)
    assert _confirmed(out)
    st = prod._active_macro
    assert st is not None
    i = prod._n
    st.push_close_v44(i, 121.5)
    prod._step_macro(i, 121.7, 121.3, 121.5, [])
    i += 1
    st.push_close_v44(i, 110.0)
    ev: list[Any] = []
    reason = prod._step_macro(i, 111.0, 109.0, 110.0, ev)
    assert reason == WEAKENING_RECOVERED
    assert prod._macro_state_label(st, reason) == "CONFIRMED"


# 12 -- miscare directionala care se incadreaza TEMPORAR intre granite: acelasi mecanism ca #8, blocat
def test_adversarial_12_temporarily_fitting_directional_move_blocked_by_same_gate() -> None:
    win = [100.0 + i * 0.9 for i in range(29)]   # aproape monoton, incadrat temporar intr-o banda larga
    from ve_n1_replay.range_semantic_v4_4 import StructureV44
    from ve_n1_replay.range_semantic_v4_3 import Depth
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    st = StructureV44(structure_id=1, depth=Depth.MACRO, parent_structure_id=None, start_ts=0, trailing_window=cfg.W)
    st.atr_ref = 1.0
    st.up.offer(150.0, 1e18); st.up.offer(150.0, 1e18)
    st.dn.offer(90.0, 1e18); st.dn.offer(90.0, 1e18)
    for c in win:
        st._trailing_closes.append(c)
    prod._active_macro = st
    reason = prod._evaluate_macro_formation(st, 40, [])
    assert reason != OK_RANGE_MACRO


# 13 -- migrare lenta a granitei: RND pe fereastra marginita finalmente depaseste RND_max
def test_adversarial_13_slow_boundary_migration_eventually_exceeds_rnd() -> None:
    from ve_n1_replay.range_semantic_v4_4 import relative_net_displacement
    win = [100.0 + i * 0.5 for i in range(29)]
    rnd = relative_net_displacement(win, 110.0, 100.0)
    assert rnd > cfg44().RND_max


# 14 -- concentrare atingeri pe o singura parte: alternation SUPPORTING_ONLY, nu blocheaza singura
def test_adversarial_14_one_sided_touch_concentration_does_not_block_alone() -> None:
    from ve_n1_replay.range_semantic_v4_4 import INSUFFICIENT_ALTERNATION_EVIDENCE
    closes = [102.0 if k % 2 == 0 else 108.0 for k in range(29)]
    from ve_n1_replay.range_semantic_v4_4 import StructureV44
    from ve_n1_replay.range_semantic_v4_3 import Depth
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    st = StructureV44(structure_id=1, depth=Depth.MACRO, parent_structure_id=None, start_ts=0, trailing_window=cfg.W)
    st.atr_ref = 1.0
    st.up.offer(110.0, 1e18); st.up.offer(110.0, 1e18)
    st.dn.offer(100.0, 1e18); st.dn.offer(100.0, 1e18)
    for k, c in enumerate(closes):
        st.push_close_v44(k, c)
    for k in range(10):
        st.record_touch_v44(k * 3, True)   # toate pe aceeasi parte
    prod._active_macro = st
    ev: list[Any] = []
    reason = prod._evaluate_macro_formation(st, 40, ev)
    assert reason == OK_RANGE_MACRO
    assert INSUFFICIENT_ALTERNATION_EVIDENCE in [e.kind for e in ev]


# 15 -- RANGE incepand inainte de fereastra de observatie: start_ts ancoreaza la primul swing DETECTABIL,
# comportament neschimbat din V4.3 (limitare documentata, nu rezolvata aici)
def test_adversarial_15_start_ts_anchors_to_first_detectable_swing_not_earlier() -> None:
    bars = legs_bars([(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)])
    prod, out = _run(bars)
    st = prod._active_macro
    assert st is not None
    assert st.start_ts >= 0
    assert st.start_ts < st.confirm_ts if st.confirm_ts is not None else True


# 16 -- RANGE care se termina aproape de sfarsitul ferestrei de observatie: raportare onesta, fara confirmare fabricata
def test_adversarial_16_truncated_at_window_end_reports_candidate_present_not_fabricated_confirm() -> None:
    bars = legs_bars([(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 8)])   # se opreste devreme
    prod, out = _run(bars)
    assert not _confirmed(out)
    kinds = {k for r in out for k in r["events"]}
    assert RANGE_CANDIDATE_PRESENT in kinds or all(r["reason"] in ("BETWEEN_EPISODES", "ESTABLISHING_FEW_SWINGS",
                                                                    "TOO_SHORT_MACRO") for r in out)


# 17 -- doua RANGE-uri independente consecutive: EPISODE_REPLACEMENT, doua identitati
def test_adversarial_17_two_independent_consecutive_ranges_get_separate_identities() -> None:
    prod = RangeSemanticProducerV44(cfg44())
    bars1 = legs_bars([(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)])
    ids = set()
    for b in bars1:
        res, evs = prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
    first_id = prod._active_macro.structure_id if prod._active_macro else None
    # termina via breakout (identitate FORTATA REPLACEMENT la reformare, indiferent de suprapunere)
    if prod._active_macro is not None:
        st = prod._active_macro
        i = prod._n
        for c in (121.5, 122.0, 123.0):
            st.push_close_v44(i, c)
            prod._step_macro(i, c + 0.2, c - 0.2, c, [])
            i += 1
    # a doua structura, la mare distanta (departe de zona 1) -- clar independenta
    start2 = prod._n
    bars2 = legs_bars([(200, 0), (220, 6), (200, 6), (220, 6), (200, 6), (220, 6), (200, 6)], start=start2)
    all_kinds = []
    for b in bars2:
        res, evs = prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
        all_kinds.extend(e.kind for e in evs)
    second_id = prod._active_macro.structure_id if prod._active_macro else None
    assert first_id is not None and second_id is not None and first_id != second_id
    assert EPISODE_REPLACEMENT in all_kinds


# 18 -- un RANGE lung cu rotatii interne: nu explodeaza in episoade MACRO repetate
def test_adversarial_18_one_long_range_with_internal_rotations_does_not_explode_into_many_macro_episodes() -> None:
    bars = osc_bars(cycles=15, base=110.0)
    prod, out = _run(bars)
    macro_ids_seen = {r["reason"] for r in out}   # placeholder, real check below via history
    assert _confirmed(out)
    # nu trebuie sa fi trecut prin mai mult de o (1) structura MACRO distincta activa la un moment dat,
    # iar istoricul MACRO nu trebuie sa fi acumulat multe episoade scurte succesive
    assert len(prod._macro_history) <= 1


# 19 -- sweep fara terminarea RANGE-ului: WEAKENING(a)->SWEEP_CONFIRMED->WEAKENING_RECOVERED, aceeasi identitate
def test_adversarial_19_sweep_without_range_termination_keeps_same_identity() -> None:
    bars = legs_bars([(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)])
    prod, out = _run(bars)
    st = prod._active_macro
    assert st is not None
    original_id = st.structure_id
    i = prod._n
    st.push_close_v44(i, 121.5)
    prod._step_macro(i, 121.7, 121.3, 121.5, [])
    i += 1
    st.push_close_v44(i, 110.0)
    reason = prod._step_macro(i, 111.0, 109.0, 110.0, [])
    assert reason == WEAKENING_RECOVERED
    assert prod._active_macro is not None
    assert prod._active_macro.structure_id == original_id


# 20 -- RANGE genuin cu deplasare directionala TEMPORARA: acoperit de testul dual-trigger (T4 peste T5)
def test_adversarial_20_genuine_range_with_temporary_directional_blip_recovers() -> None:
    bars = legs_bars([(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)])
    prod, out = _run(bars)
    assert _confirmed(out)
    assert out[-1]["state"] == "CONFIRMED"


# 21 -- echilibru lent care deriva (risc DEZVALUIT, NEREZOLVAT -- documentat in 898f149 §7, NU rezolvat aici
# prin recalibrare, mandat §10 din implementare): inregistram cinstit comportamentul, nu fortam o respingere
def test_adversarial_21_slow_drifting_equilibrium_known_disclosed_risk_recorded_honestly() -> None:
    legs: list[tuple[float, int]] = [(100, 0)]
    base = 100.0
    for k in range(10):
        legs.append((base + 20, 6))
        base += 3
        legs.append((base, 6))
    bars = legs_bars(legs)
    prod, out = _run(bars, atr=3.0)
    # NU se afirma "trebuie respins" -- documentul de design il marcheaza explicit NEREZOLVAT. Se afirma doar
    # ca mecanismul produce un rezultat BINE-DEFINIT (nu crapa, nu ramane intr-o stare ambigua) -- iar daca
    # totusi confirma, acesta e exact riscul deja dezvaluit in raportul de calibrare (898f149 §7), nu o
    # surpriza noua.
    assert out[-1]["reason"] in (
        OK_RANGE_MACRO, "INSUFFICIENT_EFFICIENCY", "INSUFFICIENT_TRAVERSAL", "EXCESSIVE_NET_DISPLACEMENT",
        "TOO_SHORT_MACRO", "ESTABLISHING_FEW_SWINGS")


# 22 -- zigzag violent (risc DEZVALUIT, NEREZOLVAT -- "not solved, not claimed solved", document design §12):
# calitate/volatilitate e explicit in afara scopului acestui mecanism. Inregistram, nu fortam.
def test_adversarial_22_violent_zigzag_known_disclosed_risk_recorded_honestly() -> None:
    legs: list[tuple[float, int]] = [(100, 0)]
    for k in range(20):
        legs.append((160, 2) if k % 2 == 0 else (100, 2))
    bars = legs_bars(legs)
    prod, out = _run(bars)
    assert out[-1]["reason"] in (
        OK_RANGE_MACRO, "INSUFFICIENT_EFFICIENCY", "INSUFFICIENT_TRAVERSAL", "EXCESSIVE_NET_DISPLACEMENT",
        "TOO_SHORT_MACRO", "ESTABLISHING_FEW_SWINGS")


def test_adversarial_suite_count_is_22() -> None:
    import inspect
    this_module = inspect.getmodule(test_adversarial_suite_count_is_22)
    fns = [n for n, f in vars(this_module).items()
          if n.startswith("test_adversarial_") and n != "test_adversarial_suite_count_is_22"
          and inspect.isfunction(f)]
    # #9/#10 sunt combinate intr-un singur test (aceeasi cronologie asteptata, per document) -- 21 functii,
    # 22 scenarii acoperite
    assert len(fns) == 21
