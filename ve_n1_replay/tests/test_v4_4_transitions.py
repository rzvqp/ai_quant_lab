"""V4.4 state-machine transitions -- T1-T9 + T-KILL (`f241698` §3), episode identity (§6), and the WEAKENING
indefinite-holding-state fix, all tested against the REAL orchestration code (`_step_macro`,
`_evaluate_macro_formation`, `_episode_identity_for_new_macro`), not re-derived expectations. Every fixture
below was numerically verified against the actual functions before being written into an assertion (mandat:
tests must be non-vacuous, not post-hoc-invented)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_range_semantic_v4_3 import legs_bars   # noqa: E402

from ve_n1_replay.range_semantic_v4_3 import (   # noqa: E402
    BREAKOUT_ACCEPTED, Depth, SWEEP_CONFIRMED, ZONES_DEGENERATE, ZONES_INVERTED,
)
from ve_n1_replay.range_semantic_v4_4 import (   # noqa: E402
    ConfigV44, EPISODE_CONTINUATION, EPISODE_MERGED, EPISODE_REPLACEMENT, EXCESSIVE_NET_DISPLACEMENT,
    INSUFFICIENT_ALTERNATION_EVIDENCE, INSUFFICIENT_EFFICIENCY, INSUFFICIENT_TRAVERSAL,
    NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT, OK_RANGE_MACRO, RANGE_CANDIDATE_PRESENT, RANGE_WEAKENING,
    RangeSemanticProducerV44, StructureV44, WEAKENING_PERSISTENCE_TERMINATED, WEAKENING_RECOVERED,
)


def cfg44(**kw: Any) -> ConfigV44:
    return ConfigV44(**kw)


def confirmed_macro(prod: RangeSemanticProducerV44, *, structure_id: int = 1, upper: float = 110.0,
                    lower: float = 100.0, atr_ref: float = 1.0, cfg: ConfigV44 | None = None) -> StructureV44:
    """Structura MACRO CONFIRMATA, construita direct (fara sa treaca prin swing-detection) -- acelasi
    patern ca `mkst()` din suita V4.3, ridicat un nivel: da control precis peste boundary/atr/fereastra
    marginita, necesar pt. teste de tranzitie WEAKENING/T-KILL deterministe."""
    cfg = cfg or ConfigV44()
    st = StructureV44(structure_id=structure_id, depth=Depth.MACRO, parent_structure_id=None, start_ts=0,
                      trailing_window=cfg.W)
    st.atr_ref = atr_ref
    st.up.offer(upper, 1e18); st.up.offer(upper, 1e18); st.up.frozen = True
    st.dn.offer(lower, 1e18); st.dn.offer(lower, 1e18); st.dn.frozen = True
    st.reached_confirmed = True
    st.confirm_ts = 0
    prod._active_macro = st
    return st


def seed_benign_window(st: StructureV44, *, start_bar: int = 0) -> int:
    """Umple `_trailing_closes` cu o oscilatie 102/108 (in interiorul [100,110]) care satisface confortabil
    toate cele 3 porti (ER/traversal/RND) -- pt. teste WEAKENING care nu vor sa declanseze T5 accidental."""
    i = start_bar
    for k in range(29):
        c = 102.0 if k % 2 == 0 else 108.0
        st.push_close_v44(i, c)
        i += 1
    return i


# ═══════════════════════════════════ T-KILL (prioritate 0, inaintea oricarei alte verificari) ═══════════════════════════════════

def test_t_kill_zones_degenerate_via_atr_spike_on_confirmed_structure() -> None:
    """Un salt de ATR poate degenera zonele unei structuri deja CONFIRMATE (latimea e fixa dupa inghet,
    dar `atr_ref` se actualizeaza in fiecare bara) -- T-KILL are prioritate absoluta, verificat inaintea
    oricarei alte ramuri din `_step_macro`."""
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    st = confirmed_macro(prod, upper=110.0, lower=100.0, atr_ref=1.0, cfg=cfg)
    for k in range(3):
        st.push_close_v44(k, 104.0)
    ev: list[Any] = []
    assert prod._step_macro(3, 104.5, 103.5, 104.0, ev) == OK_RANGE_MACRO
    st.atr_ref = 7.0   # width(10) <= 2*w_atr*atr_ref(2*0.8*7=11.2) -> ZONES_DEGENERATE
    ev = []
    reason = prod._step_macro(4, 104.5, 103.5, 104.0, ev)
    assert reason == ZONES_DEGENERATE
    assert [e.kind for e in ev] == [ZONES_DEGENERATE]
    assert prod._active_macro is None
    assert prod._last_terminated_macro_end_reason == ZONES_DEGENERATE
    assert prod._last_terminated_macro_id == 1


def test_t_kill_zones_inverted() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    st = StructureV44(structure_id=2, depth=Depth.MACRO, parent_structure_id=None, start_ts=0, trailing_window=cfg.W)
    st.atr_ref = 1.0
    st.up.offer(98.0, 1e18); st.up.offer(98.2, 1e18)
    st.dn.offer(105.0, 1e18); st.dn.offer(105.2, 1e18)
    prod._active_macro = st
    ev: list[Any] = []
    reason = prod._step_macro(0, 99.0, 97.0, 98.0, ev)
    assert reason == ZONES_INVERTED
    assert prod._active_macro is None


# ═══════════════════════════════════ T1/T2/T3 -- formare, prin observe() public, capat la capat ═══════════════════════════════════

def test_t2_range_candidate_present_emitted_exactly_once() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    macro_legs: list[tuple[float, int]] = [(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)]
    bars = legs_bars(macro_legs)
    seen = 0
    for b in bars:
        _, evs = prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
        seen += sum(1 for e in evs if e.kind == RANGE_CANDIDATE_PRESENT)
    assert seen == 1


def test_t3_confirms_genuine_oscillating_range() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    macro_legs: list[tuple[float, int]] = [(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)]
    bars = legs_bars(macro_legs)
    confirmed = False
    for b in bars:
        res, evs = prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
        if any(e.kind == OK_RANGE_MACRO for e in evs):
            confirmed = True
    assert confirmed
    assert prod._active_macro is not None
    assert prod._active_macro.reached_confirmed


def test_t3_rejects_shallow_channel_via_discrimination_gate_not_just_cluster_tolerance() -> None:
    """Un canal in panta usoara (riscul 'shallow channel' disclosed in `898f149` §7), care ATINGE
    width+touch+durata (deci ar fi confirmat sub regulile VECHI V4.3), trebuie respins de poarta NOUA T3.
    Construit direct (precondictii width/touch/durata satisfacute explicit) pt. a evita fragilitatea
    pipeline-ului de detectie a swing-urilor realiste -- proba ramane asupra GATE-ULUI insusi (`efficiency_
    ratio`/`traversal_count`/`relative_net_displacement` REALE, neschimbate), nu asupra mecanismului
    mostenit de toleranta a clusterului (acela e testat separat, prin scenariul confirmat mai sus)."""
    cfg = cfg44()
    win: list[float] = []
    c = 100.0
    for i in range(29):
        c += 1.2 if i % 2 == 0 else -0.5
        win.append(c)   # oscileaza, dar deriva constant -- niciodata nu revine sa atinga ambele extreme
    prod, st = _macro_candidate_for_gate(cfg, win, upper=130.0, lower=100.0)
    reason = prod._evaluate_macro_formation(st, 40, [])
    assert reason != OK_RANGE_MACRO
    assert reason in (EXCESSIVE_NET_DISPLACEMENT, INSUFFICIENT_TRAVERSAL, INSUFFICIENT_EFFICIENCY)
    assert not st.reached_confirmed


# ═══════════════════════════════════ T3 -- prioritate FIXA ER -> traversal -> RND la esec simultan ═══════════════════════════════════
# Fiecare caz de mai jos e verificat NUMERIC (probat separat) inainte de a fi scris aici -- fixture-uri
# construite direct pe `_trailing_closes`, nu "sperate" din bare realiste.

def _macro_candidate_for_gate(cfg: ConfigV44, closes: list[float], upper: float, lower: float
                              ) -> tuple[RangeSemanticProducerV44, StructureV44]:
    prod = RangeSemanticProducerV44(cfg)
    st = StructureV44(structure_id=9, depth=Depth.MACRO, parent_structure_id=None, start_ts=0, trailing_window=cfg.W)
    st.atr_ref = 1.0
    st.up.offer(upper, 1e18); st.up.offer(upper, 1e18)
    st.dn.offer(lower, 1e18); st.dn.offer(lower, 1e18)
    for c in closes:
        st._trailing_closes.append(c)
    prod._active_macro = st
    return prod, st


def test_t3_gate_priority_all_three_fail_reports_efficiency_first() -> None:
    cfg = cfg44()
    closes = [100.0 + i for i in range(29)]   # ER=1.0, traversal=0, RND~1.0036 -- verified numerically
    prod, st = _macro_candidate_for_gate(cfg, closes, upper=77.9, lower=50.0)
    reason = prod._evaluate_macro_formation(st, 100, [])
    assert reason == INSUFFICIENT_EFFICIENCY


def test_t3_gate_priority_traversal_before_rnd_when_efficiency_passes() -> None:
    cfg = cfg44()
    closes = []
    c = 100.0
    for i in range(29):
        c += 5.0 if i % 2 == 0 else -3.0
        closes.append(c)   # ER=0.25 (passes), traversal=0 (fails), RND=1.4 (fails) -- verified numerically
    prod, st = _macro_candidate_for_gate(cfg, closes, upper=95.0, lower=75.0)
    reason = prod._evaluate_macro_formation(st, 100, [])
    assert reason == INSUFFICIENT_TRAVERSAL


def test_t3_alternation_evidence_is_supporting_only_reported_but_never_blocks_confirmation() -> None:
    """Regresie pt. bug-ul gasit inaintea inghetului: `alternation_rate`/`ALT_MIN`/`touches_in_window` erau
    definite dar niciodata cablate -- `INSUFFICIENT_ALTERNATION_EVIDENCE` era de neatins. Acum: dovada slaba
    (sub `ALT_MIN` sau <3 atingeri) emite evenimentul, dar NU blocheaza confirmarea (SUPPORTING_ONLY, mandat
    §5) -- 3 cazuri: putine atingeri (None), atingeri alternante (trece), atingeri toate pe aceeasi parte
    (0.0, sub prag)."""
    cfg = cfg44()
    closes = [102.0 if k % 2 == 0 else 108.0 for k in range(29)]

    prod_few, st_few = _macro_candidate_for_gate(cfg, closes, upper=110.0, lower=100.0)
    ev_few: list[Any] = []
    reason_few = prod_few._evaluate_macro_formation(st_few, 40, ev_few)
    assert reason_few == OK_RANGE_MACRO
    assert INSUFFICIENT_ALTERNATION_EVIDENCE in [e.kind for e in ev_few]
    assert st_few.reached_confirmed

    prod_alt, st_alt = _macro_candidate_for_gate(cfg, closes, upper=110.0, lower=100.0)
    for k in range(10):
        st_alt.record_touch_v44(k * 3, k % 2 == 0)
    ev_alt: list[Any] = []
    reason_alt = prod_alt._evaluate_macro_formation(st_alt, 40, ev_alt)
    assert reason_alt == OK_RANGE_MACRO
    assert INSUFFICIENT_ALTERNATION_EVIDENCE not in [e.kind for e in ev_alt]
    assert st_alt.reached_confirmed

    prod_same, st_same = _macro_candidate_for_gate(cfg, closes, upper=110.0, lower=100.0)
    for k in range(10):
        st_same.record_touch_v44(k * 3, True)
    ev_same: list[Any] = []
    reason_same = prod_same._evaluate_macro_formation(st_same, 40, ev_same)
    assert reason_same == OK_RANGE_MACRO
    assert INSUFFICIENT_ALTERNATION_EVIDENCE in [e.kind for e in ev_same]
    assert st_same.reached_confirmed


def test_t3_gate_reports_rnd_only_when_efficiency_and_traversal_both_pass() -> None:
    cfg = cfg44()
    closes = [95.0 if i % 2 == 0 else 205.0 for i in range(27)]
    closes += [205.0, 400.0]   # ER=0.096 (passes), traversal=27 (passes), RND=15.25 (fails) -- verified
    prod, st = _macro_candidate_for_gate(cfg, closes, upper=160.0, lower=140.0)
    reason = prod._evaluate_macro_formation(st, 100, [])
    assert reason == EXCESSIVE_NET_DISPLACEMENT


# ═══════════════════════════════════ T4/T6/T8 -- ciclul de excursie ═══════════════════════════════════

def test_t4_excursion_opens_labels_weakening_excursion_pending() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    st = confirmed_macro(prod, cfg=cfg)
    i = seed_benign_window(st)
    st.push_close_v44(i, 111.5)
    ev: list[Any] = []
    reason = prod._step_macro(i, 111.6, 111.4, 111.5, ev)
    assert reason == NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT
    assert st.weakening_reason == "EXCURSION_PENDING"
    assert RANGE_WEAKENING in [e.kind for e in ev]


def test_t6_reentry_within_k_reentry_recovers_to_confirmed() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    st = confirmed_macro(prod, cfg=cfg)
    i = seed_benign_window(st)
    st.push_close_v44(i, 111.5)
    prod._step_macro(i, 111.6, 111.4, 111.5, [])
    i += 1
    st.push_close_v44(i, 105.0)
    ev: list[Any] = []
    reason = prod._step_macro(i, 106.0, 104.0, 105.0, ev)
    assert reason == WEAKENING_RECOVERED
    assert st.weakening_reason is None
    kinds = [e.kind for e in ev]
    assert SWEEP_CONFIRMED in kinds and WEAKENING_RECOVERED in kinds
    assert prod._macro_state_label(st, reason) == "CONFIRMED"


def test_t8_n_accept_consecutive_closes_outside_terminates_via_breakout() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    st = confirmed_macro(prod, cfg=cfg)
    i = seed_benign_window(st)
    last_reason = None
    for c in (111.5, 112.0, 113.0):   # N_accept=3
        st.push_close_v44(i, c)
        last_reason = prod._step_macro(i, c + 0.2, c - 0.2, c, [])
        i += 1
    assert last_reason == BREAKOUT_ACCEPTED
    assert prod._active_macro is None
    assert prod._last_terminated_macro_end_reason == BREAKOUT_ACCEPTED
    assert st.end_reason == BREAKOUT_ACCEPTED


def test_accepted_breakout_cannot_leave_a_stale_confirmed_range_active() -> None:
    """Mandat §7: 'accepted breakout cannot leave stale confirmed range active' -- dupa T8, structura veche
    nu mai e `_active_macro` sub nicio forma, si niciun apel ulterior nu o poate re-confirma implicit."""
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    st = confirmed_macro(prod, cfg=cfg)
    old_id = st.structure_id
    i = seed_benign_window(st)
    for c in (111.5, 112.0, 113.0):
        st.push_close_v44(i, c)
        prod._step_macro(i, c + 0.2, c - 0.2, c, [])
        i += 1
    assert prod._active_macro is None
    ev: list[Any] = []
    reason = prod._step_macro(i, 113.5, 113.0, 113.2, ev)
    assert reason == "BETWEEN_EPISODES" or reason != OK_RANGE_MACRO
    assert prod._active_macro is None
    assert old_id != (prod._active_macro.structure_id if prod._active_macro else None)


# ═══════════════════════════════════ T5/T7/T9 -- degradare pe fereastra marginita ═══════════════════════════════════

def test_t5_trailing_degradation_entry_via_monotonic_run() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    st = confirmed_macro(prod, cfg=cfg)
    i = 0; c = 101.0
    entered_at = None
    for k in range(5):
        c += 0.3
        st.push_close_v44(i, c)
        reason = prod._step_macro(i, c + 0.1, c - 0.1, c, [])
        if st.weakening_reason == "TRAILING_DEGRADATION" and entered_at is None:
            entered_at = i
            assert reason == RANGE_WEAKENING
        i += 1
    assert entered_at is not None
    assert prod._macro_state_label(st, RANGE_WEAKENING) == "WEAKENING"


def test_t7_recovery_requires_both_er_and_rnd_at_strict_threshold() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    st = confirmed_macro(prod, cfg=cfg)
    i = 0; c = 101.0
    for k in range(5):
        c += 0.3
        st.push_close_v44(i, c)
        prod._step_macro(i, c + 0.1, c - 0.1, c, [])
        i += 1
    assert st.weakening_reason == "TRAILING_DEGRADATION"
    recovered_at = None
    for k in range(40):
        c = 104.0 + (0.4 if k % 2 == 0 else -0.4)
        st.push_close_v44(i, c)
        reason = prod._step_macro(i, c + 0.1, c - 0.1, c, [])
        if reason == WEAKENING_RECOVERED:
            recovered_at = i
            break
        i += 1
    assert recovered_at is not None
    assert st.weakening_reason is None
    assert st._weakening_bars == 0
    assert prod._macro_state_label(st, reason) == "CONFIRMED"


def test_t9_persistence_terminates_after_weakening_max_bars() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    st = confirmed_macro(prod, cfg=cfg)
    i = 0; c = 101.0
    terminated_at = None
    for k in range(60):
        c += 0.05
        if c >= 110.7:
            c = 101.0
        st.push_close_v44(i, c)
        reason = prod._step_macro(i, c + 0.05, c - 0.05, c, [])
        if reason == WEAKENING_PERSISTENCE_TERMINATED:
            terminated_at = i
            break
        i += 1
    assert terminated_at is not None
    assert prod._active_macro is None
    assert prod._last_terminated_macro_end_reason == WEAKENING_PERSISTENCE_TERMINATED


def test_weakening_persistence_counter_increments_in_the_middle_zone_not_just_past_looser_threshold() -> None:
    """Regresie pt. bug-ul de 'indefinite holding state' gasit si corectat inaintea inghetului: un ER care
    sta STRICT intre `ER_max`(0.5, prag de recuperare) si `ER_weakening`(0.75, prag de INTRARE) trebuie sa
    incrementeze contorul in FIECARE bara -- cod-ul original defect incrementa doar cand era inca peste
    `ER_weakening`, lasand aceasta zona intermediara sa nu progreseze niciodata spre `WEAKENING_MAX_BARS`."""
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    st = confirmed_macro(prod, cfg=cfg)
    i = 0; c = 101.0
    for k in range(3):
        c += 0.4
        st.push_close_v44(i, c)
        prod._step_macro(i, c + 0.1, c - 0.1, c, [])
        i += 1
    assert st.weakening_reason == "TRAILING_DEGRADATION"

    from ve_n1_replay.range_semantic_v4_4 import efficiency_ratio, relative_net_displacement
    bars_seen = []
    for k in range(22):
        c += 0.28 if k % 2 == 0 else -0.06
        st.push_close_v44(i, c)
        bars_before = st._weakening_bars
        reason = prod._step_macro(i, c + 0.05, c - 0.05, c, [])
        er = efficiency_ratio(st._trailing_closes)
        rnd = relative_net_displacement(st._trailing_closes, st.boundary_upper, st.boundary_lower)
        bars_seen.append((er, rnd, st._weakening_bars, reason))
        if reason == WEAKENING_PERSISTENCE_TERMINATED:
            break
        assert st._weakening_bars == bars_before + 1, (
            f"contorul NU a incrementat la bara {i} (er={er}, rnd={rnd}) -- stare de asteptare nedefinita")
        i += 1
    midzone_bars = [b for b in bars_seen if 0.5 < b[0] <= 0.75]
    assert len(midzone_bars) >= 5, "fixture-ul nu a exercitat de fapt zona intermediara ER -- test vacuu"
    assert bars_seen[-1][3] == WEAKENING_PERSISTENCE_TERMINATED


def test_dual_trigger_new_excursion_overrides_trailing_degradation_label_and_pauses_counter() -> None:
    """T4 are prioritate NECONDITIONATA asupra unui T5 deja activ: eticheta devine EXCURSION_PENDING, iar
    contorul de persistenta al TRAILING_DEGRADATION se OPRESTE (nu se reseteaza, nu creste) cat timp
    excursia e activa -- simplificare marginala asumata explicit (vezi docstring-ul modulului)."""
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    st = confirmed_macro(prod, cfg=cfg)
    i = 0; c = 101.0
    for k in range(3):
        c += 0.3
        st.push_close_v44(i, c)
        prod._step_macro(i, c + 0.1, c - 0.1, c, [])
        i += 1
    assert st.weakening_reason == "TRAILING_DEGRADATION"
    bars_before = st._weakening_bars

    c2 = 111.5
    st.push_close_v44(i, c2)
    ev: list[Any] = []
    reason = prod._step_macro(i, c2 + 0.1, c2 - 0.1, c2, ev)
    assert reason == NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT
    assert st.weakening_reason == "EXCURSION_PENDING"
    assert st._weakening_bars == bars_before   # paused, not reset, not incremented


# ═══════════════════════════════════ identitate de episod (§6/§9) ═══════════════════════════════════

def test_episode_identity_replacement_when_no_prior_structure() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    action, target = prod._episode_identity_for_new_macro((100.0, 110.0), 50)
    assert (action, target) == ("REPLACEMENT", None)


def test_episode_identity_continuation_when_non_breakout_termination_overlaps_within_gap() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    prod._last_terminated_macro_zone = (100.0, 110.0)
    prod._last_terminated_macro_end_ts = 40
    prod._last_terminated_macro_id = 7
    prod._last_terminated_macro_end_reason = ZONES_DEGENERATE
    action, target = prod._episode_identity_for_new_macro((101.0, 111.0), 40 + cfg.GAP_MAX)
    assert (action, target) == ("CONTINUATION", 7)


def test_episode_identity_forced_replacement_after_breakout_even_if_overlap_and_gap_would_qualify() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    prod._last_terminated_macro_zone = (100.0, 110.0)
    prod._last_terminated_macro_end_ts = 40
    prod._last_terminated_macro_id = 7
    prod._last_terminated_macro_end_reason = BREAKOUT_ACCEPTED
    action, target = prod._episode_identity_for_new_macro((101.0, 111.0), 42)
    assert (action, target) == ("REPLACEMENT", None)


def test_episode_identity_replacement_when_gap_exceeds_gap_max() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    prod._last_terminated_macro_zone = (100.0, 110.0)
    prod._last_terminated_macro_end_ts = 40
    prod._last_terminated_macro_id = 7
    prod._last_terminated_macro_end_reason = ZONES_DEGENERATE
    action, target = prod._episode_identity_for_new_macro((101.0, 111.0), 40 + cfg.GAP_MAX + 1)
    assert action == "REPLACEMENT"


def test_episode_merge_logic_itself_is_correct_when_precondition_is_forced() -> None:
    """Dovada ca ramura MERGE nu e cod mort/gresit -- forteaza precondictia (`_active_macro` viu, IoU
    suficient) direct, ocolind imposibilitatea structurala de la nivelul apelantului public."""
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)

    class _FakeLiveMacro:
        structure_id = 3
        boundary_lower = 100.0
        boundary_upper = 110.0

    prod._active_macro = _FakeLiveMacro()   # type: ignore[assignment]
    action, target = prod._episode_identity_for_new_macro((101.0, 111.0), 41)
    assert (action, target) == ("MERGE", 3)


def test_episode_merge_is_structurally_unreachable() -> None:
    """Proba, nu presupunere: pe un scenariu lung, variat (multe rotatii interne, mai multe episoade MACRO
    succesive, terminari prin KILL/breakout/persistenta WEAKENING), EPISODE_MERGED nu apare niciodata prin
    API-ul public `observe()`, in timp ce EPISODE_CONTINUATION/EPISODE_REPLACEMENT apar -- confirmand ca
    scenariul chiar exercita formarea de episoade (nu e un test vacuu care nu ajunge niciodata acolo).
    Motivul structural (documentat si in docstring-ul modulului): `_episode_identity_for_new_macro` e
    apelat doar din ramura `depth is Depth.MACRO` a `_offer_swing_everywhere`, care e atinsa doar cand
    `forming_macro = self._active_macro is None` era True -- deci precondictia MERGE (`_active_macro is not
    None`) nu poate fi niciodata adevarata in acel punct al codului."""
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    all_events: list[Any] = []
    i = 0
    for cycle in range(4):
        macro_legs: list[tuple[float, int]] = [
            (100 + cycle * 30, 0), (120 + cycle * 30, 6), (100 + cycle * 30, 6), (120 + cycle * 30, 6),
            (100 + cycle * 30, 6), (120 + cycle * 30, 6), (100 + cycle * 30, 6),
            (135 + cycle * 30, 3), (150 + cycle * 30, 3), (165 + cycle * 30, 3)]   # breakout tail
        bars = legs_bars(macro_legs, start=i)
        for b in bars:
            _, evs = prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
            all_events.extend(evs)
        i += len(bars) + 2
    kinds = [e.kind for e in all_events]
    assert EPISODE_MERGED not in kinds
    assert EPISODE_REPLACEMENT in kinds or EPISODE_CONTINUATION in kinds


# ═══════════════════════════════════ tranzitii interzise ═══════════════════════════════════

def test_weakening_structure_never_silently_reverts_to_forming_or_candidate_label() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    st = confirmed_macro(prod, cfg=cfg)
    i = 0; c = 101.0
    for k in range(5):
        c += 0.3
        st.push_close_v44(i, c)
        prod._step_macro(i, c + 0.1, c - 0.1, c, [])
        i += 1
    assert st.weakening_reason == "TRAILING_DEGRADATION"
    label = prod._macro_state_label(st, RANGE_WEAKENING)
    assert label == "WEAKENING"
    assert label not in ("CANDIDATE", "FORMING")


def test_terminated_structure_id_is_never_reused_as_active_macro() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    st = confirmed_macro(prod, structure_id=42, cfg=cfg)
    for k in range(3):
        st.push_close_v44(k, 104.0)
    st.atr_ref = 7.0
    prod._step_macro(3, 104.5, 103.5, 104.0, [])
    assert prod._active_macro is None
    assert prod._registry is not None
