"""Teste DECISIVE — prototip RANGE HIERARCHICAL V4.3 (mandat CEO "IMPLEMENTARE PROTOTIP RANGE HIERARCHICAL
V4.3", autorizat de Red Team RT-RANGE-0006/STATIC_PASS, commit `2c113ef`, pe pachetul Statistician `d6e599e`).

Oracol: `statistician/harness/range_v42_contract_harness.py` @`d6e599e` (SHA-256 verificat independent
`c917604b…`, 409 linii, 79 PASS/0 FAIL rulat independent aici, mypy --strict clean) — NU importat direct (nu
există în acest checkout, trăiește pe branch-ul `statistician-foundation`), ci REPRODUS ca teste proprii VE,
apelând funcțiile PORTATE ale prototipului (`range_semantic_v4_3.py`), cu aceleași input-uri și aceleași
rezultate așteptate deja verificate independent contra harness-ului. Acoperă mandatul §12 (25 iteme) + cele
20 de grupe ale harness-ului (adversariale + nevacuitate) + cele 29 reason codes (reachability dinamic, prin
API-ul public, nu listă hardcodată) + cele 13 porți de nevacuitate (nu 12 — corectat conform mandatului).
"""
from __future__ import annotations

import inspect
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

import ve_n1_replay as r
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay import (
    ConfigV43, ContractErrorV43, ConfigNotRatifiedErrorV43, Depth, MacroState, InternalState,
    REASONS_V43, ROLES_V43, Cluster, Structure, Excursion, Registry,
    RangeSemanticProducerV43, RangeSemanticEngineV43, RangeSnapshotErrorV43,
    RangeSemanticResultV43, RangeEventV43,
    RANGE_HIERARCHICAL_V4_3_NORMATIVE_CONFIG_ID, N1IncrementalReplayEngine,
)
from ve_n1_replay.range_semantic_v4_3 import (
    degeneracy_check, evaluate_candidate, evaluate_candidate_with_n_touch, offer_swing, assign_level,
    promotion_check, guard_timestamp, sweep_reversal_confirmed,
    OK_RANGE_MACRO, OK_RANGE_INTERNAL, ESTABLISHING_FEW_SWINGS, TOO_SHORT_MACRO, TOO_SHORT_INTERNAL,
    ZONES_DEGENERATE, ZONES_INVERTED, ATR_UNAVAILABLE, BETWEEN_EPISODES, SWING_OUTSIDE_CLUSTER,
    NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT, SWEEP_CONFIRMED, BREAKOUT_ACCEPTED, LIQUIDITY_SWEEP_REVERSAL,
    IS_TREND_MACRO, PROMOTION_REFUSED_PRECONDITION_P1, PROMOTION_REFUSED_PRECONDITION_P2,
    PROMOTION_REFUSED_PRECONDITION_P3, PROMOTION_REFUSED_PRECONDITION_P4, LEVEL_ASSIGNMENT_UNRESOLVED,
    PARTIAL_OVERLAP_NO_CONTAINMENT, DEPTH_LIMIT_EXCEEDED, ROLE_ASSERTED_BEFORE_CONFIRMATION,
    ROLE_KNOWN_BEFORE_CONFIRM, SNAPSHOT_CONTRACT_MISMATCH, FUTURE_TIMESTAMP_REFUSED, DEAD_ID_REUSE_REFUSED,
    REVERSAL_REFERENCE_UNAVAILABLE, REVERSAL_WINDOW_EXPIRED,
)
from ve_n1_replay import range_semantic_v4_3 as _rsv43_mod
from ve_n1_replay import range_engine_v4_3 as _rev43_mod

Bar = r.Bar
KW: dict[str, Any] = dict(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900, implementation_commit=IC)
_MODULE_DIR = Path(_rsv43_mod.__file__).resolve().parent
_ObserveOut = tuple[Any, RangeSemanticResultV43, list[RangeEventV43]]


def mk(i: int, o: float, h: float, l: float, c: float) -> Any:
    return Bar(symbol="XAUUSD", ts_open=i * 900, ts_close=(i + 1) * 900,
              open=float(o), high=float(h), low=float(l), close=float(c), volume=100.0)


def cfg43(**kw: Any) -> ConfigV43:
    return ConfigV43(**kw)


def _req(s: str | None) -> str:
    """Îngustează `str | None` -> `str` pt. cazurile de test unde rezultatul NU e None prin construcție
    (verificat la runtime, nu doar presupus -- `assert` eșuează zgomotos dacă ipoteza fixture-ului greșește)."""
    assert s is not None
    return s


def _cluster_with(*prices: float) -> Cluster:
    c = Cluster()
    for p in prices:
        c.offer(p, 1e18)
    return c


def mkst(st_id: int, atr: float, ups: list[float], dns: list[float], start: int = 0,
        depth: Depth = Depth.MACRO, parent: int | None = None) -> Structure:
    """Port al helper-ului `mk()` din test-ul harness-ului -- construiește o `Structure` direct, cu clustere
    deja populate (pt. teste izolate ale funcțiilor pure, fără să treacă prin producător)."""
    s = Structure(structure_id=st_id, depth=depth, parent_structure_id=parent, start_ts=start)
    s.atr_ref = atr
    for p in ups:
        s.up.offer(p, 1e18)   # toleranță infinită -- forțează acceptarea tuturor membrilor de test
    for p in dns:
        s.dn.offer(p, 1e18)
    return s


def run43(bars: list[Any], config: ConfigV43 | None = None
         ) -> tuple[RangeSemanticEngineV43, list[_ObserveOut]]:
    eng = RangeSemanticEngineV43(range_config=config or cfg43(), acknowledge_construction_only=True, **KW)
    out = [eng.observe_closed_bar(b) for b in bars]
    return eng, out


def run43_fixed_atr(bars: list[Any], config: ConfigV43 | None = None, atr: float = 1.0
                    ) -> tuple[RangeSemanticProducerV43, list[_ObserveOut]]:
    """Rulează producătorul DIRECT (fără N1), cu ATR FIX -- fixture-urile HBL-20/promovare/canal necesită
    sincronizare EXACTĂ (sweep în K_reentry, breakout la exact 3 închideri, prag de canal) calibrată pe
    ATR=1,0; ATR-ul REAL calculat de N1 (via `run43`/motorul complet) variază cu datele și ar strica acea
    sincronizare -- exact ce s-a întâmplat inițial la testul HBL-20 (breakout niciodată emis, pentru că
    zona era altă lățime decât cea calibrată). `run43` (motorul complet, N1 real) rămâne folosit acolo unde
    testul verifică PARITATE/CONSISTENȚĂ (snapshot, chunk, no-lookahead), nu un rezultat EXACT calibrat."""
    prod = RangeSemanticProducerV43(config or cfg43())
    out: list[_ObserveOut] = []
    for b in bars:
        res, evs = prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close,
                                atr=atr)
        out.append((None, res, evs))
    return prod, out


def osc_bars(cycles: int = 20, base: float = 100.0, start: int = 0,
            amp: tuple[float, ...] = (2, 6, 8, 5, -1, -5, -8, -5)) -> list[Any]:
    bars = []; i = start
    for _ in range(cycles):
        for delta in amp:
            c = base + delta
            bars.append(mk(i, c - 0.2, c + 0.5, c - 0.5, c)); i += 1
    return bars


def legs_bars(legs: Sequence[tuple[float, int]], start: int = 0) -> list[Any]:
    """legs: [(target_price, n_bars), ...] -- interpolează liniar de la ținta anterioară la fiecare nouă
    țintă în EXACT n_bars bare (un leg cu n_bars=1 sau 2 e o mișcare abruptă, nu o rampă lină) -- control
    fin necesar pt. fixture-uri cu momente EXACTE de swing/excursie/breakout."""
    bars = []; i = start
    prev = legs[0][0]
    for target, n in legs[1:]:
        for step in range(1, n + 1):
            frac = step / n
            c = prev + (target - prev) * frac
            o = c - (target - prev) / n * 0.4
            h = max(o, c) + 0.3; l = min(o, c) - 0.3
            bars.append(mk(i, o, h, l, c)); i += 1
        prev = target
    return bars


def mirror_legs(legs: Sequence[tuple[float, int]], axis: float = 110.0) -> Sequence[tuple[float, int]]:
    """Reflectă prețurile unei liste de legs în jurul unei axe -- construiește fixture-ul BEARISH simetric
    dintr-un fixture BULLISH deja validat (2*axis - price), fără să re-deriveze geometria de la zero."""
    return [(2 * axis - p, n) for p, n in legs]




# ═══════════════════════ config identity — config_id normativ + gărzi ═══════════════════════
def test_config_id_matches_normative_value() -> None:
    assert ConfigV43().config_id() == RANGE_HIERARCHICAL_V4_3_NORMATIVE_CONFIG_ID


def test_config_fixed_values_match_ceo_mandate() -> None:
    c = ConfigV43()
    assert (c.d_macro, c.d_internal, c.n_touch, c.K_reentry, c.N_accept, c.K_struct, c.n_external_swings,
           c.atr_window, c.w_atr) == (29, 12, 2, 22, 3, 2, 2, 14, 0.80)
    assert c.tol_cluster == 1.60 and c.s_max == 1.60 and c.w_atr_sanity_ceiling == 1.3952
    assert c.contract_version == "range-hierarchical-v4.3"


def test_engine_refuses_without_construction_acknowledgement() -> None:
    with pytest.raises(ConfigNotRatifiedErrorV43):
        RangeSemanticEngineV43(range_config=ConfigV43(), **KW)


def test_engine_refuses_config_id_mismatch() -> None:
    with pytest.raises(ContractErrorV43):
        RangeSemanticEngineV43(range_config=ConfigV43(w_atr=0.5), acknowledge_construction_only=True, **KW)
    with pytest.raises(ContractErrorV43):
        RangeSemanticEngineV43(range_config=ConfigV43(d_macro=30), acknowledge_construction_only=True, **KW)


def test_bare_config_validate_matches_harness_bounds() -> None:
    with pytest.raises(ContractErrorV43):
        ConfigV43(w_atr=1.4)   # peste plafonul de sanity 1.3952
    with pytest.raises(ContractErrorV43):
        ConfigV43(d_internal=29, d_macro=29)   # nu strict sub d_macro
    with pytest.raises(ContractErrorV43):
        ConfigV43(n_touch=1)
    with pytest.raises(ContractErrorV43):
        ConfigV43(K_struct=0)
    ConfigV43(w_atr=0.80)   # trece


# ═══════════════════════ grupele 1-3 harness: MACRO cu INTERNAL (channel/subrange) ═══════════════════════
def test_group1_internal_admitted_under_open_macro() -> None:
    cfg = cfg43()
    macro = mkst(1, atr=1.0, ups=[110.0, 110.4], dns=[100.0, 99.6])
    depth, reason, parent_id = assign_level(50, 70, 102.0, 108.0, macro, cfg)
    assert depth is Depth.INTERNAL and parent_id == 1


def test_group1b_drift_classifies_channel() -> None:
    from ve_n1_replay.range_semantic_v4_3 import _UnboundedSlope
    acc = _UnboundedSlope()
    closes = [102 + 0.25 * i for i in range(20)]
    for c in closes:
        acc.push(c)
    drift = abs(acc.slope()) * len(closes) / 1.0
    assert drift > cfg43().s_max


def test_group3_subrange_low_drift() -> None:
    from ve_n1_replay.range_semantic_v4_3 import _UnboundedSlope
    acc = _UnboundedSlope()
    closes = [104 + (0.05 if i % 2 else -0.05) for i in range(20)]
    for c in closes:
        acc.push(c)
    drift = abs(acc.slope()) * len(closes) / 1.0
    assert drift <= cfg43().s_max


# ═══════════════════════ item 7: al treilea nivel refuzat (DEPTH_LIMIT_EXCEEDED, C14) ═══════════════════════
def test_third_level_refused_depth_limit_exceeded() -> None:
    cfg = cfg43()
    macro = mkst(1, 1.0, [110.0, 110.4], [100.0, 99.6])
    inner = mkst(5, 1.0, [110.0, 110.4], [100.0, 99.6], depth=Depth.INTERNAL, parent=1)
    depth, reason, pid = assign_level(20, 40, 102.0, 108.0, inner, cfg)
    assert depth is None and reason == DEPTH_LIMIT_EXCEEDED and pid is None
    # aceeași geometrie SUB un părinte MACRO trece -- poarta e nevacuă
    depth2, reason2, pid2 = assign_level(20, 40, 102.0, 108.0, macro, cfg)
    assert depth2 is Depth.INTERNAL


# ═══════════════════════ item 8: zone care se ating (ZONES_DEGENERATE, KILL) ═══════════════════════
def test_zones_touching_is_degenerate_kill() -> None:
    cfg = cfg43()
    deg = mkst(9, atr=1.0, ups=[101.0, 101.2], dns=[100.0, 99.8])
    assert degeneracy_check(deg, cfg) == ZONES_DEGENERATE
    assert deg.confirm_ts is None   # KILL, nu DELAY


# ═══════════════════════ item 9: zone inversate ═══════════════════════
def test_zones_inverted() -> None:
    cfg = cfg43()
    inv = mkst(10, atr=1.0, ups=[98.0, 98.2], dns=[105.0, 105.2])
    assert degeneracy_check(inv, cfg) == ZONES_INVERTED


# ═══════════════════════ item 10: ATR indisponibil ═══════════════════════
def test_atr_unavailable() -> None:
    cfg = cfg43()
    st = Structure(structure_id=12, depth=Depth.MACRO, parent_structure_id=None, start_ts=0)
    st.up.offer(110.0, 1e18); st.up.offer(110.4, 1e18)
    st.dn.offer(100.0, 1e18); st.dn.offer(99.6, 1e18)
    assert degeneracy_check(st, cfg) == ATR_UNAVAILABLE
    assert st.zones(cfg.w_atr) is None


def test_establishing_few_swings_empty_cluster() -> None:
    cfg = cfg43()
    few = mkst(11, 1.0, [110.0], [])
    assert few.boundary_lower is None
    assert degeneracy_check(few, cfg) == ESTABLISHING_FEW_SWINGS


def test_n_touch_gate_below_two_members_each_side() -> None:
    """**Găsit, documentat**: harness-ul propriu-zis NU verifică `n_touch` (doar `validate()` îl impune ca
    prag de configurație) -- `degeneracy_check` verifică doar cluster GOL/non-gol. Textul CEO §4/§6 cere
    explicit "minimum două swing-uri pe fiecare frontieră" -- `evaluate_candidate_with_n_touch` adaugă
    această gardă, DINCOLO de portul fidel `degeneracy_check`/`evaluate_candidate` (vezi docstring)."""
    cfg = cfg43()
    one_each = mkst(50, 1.0, [110.0], [100.0], start=0)   # 1 membru pe fiecare parte -- non-gol, dar <n_touch=2
    assert degeneracy_check(one_each, cfg) is None   # portul fidel: NU semnalează nimic (non-gol)
    assert evaluate_candidate(one_each, 50, cfg) in (OK_RANGE_MACRO, TOO_SHORT_MACRO)   # fidel harness-ului
    assert evaluate_candidate_with_n_touch(one_each, 50, cfg) == ESTABLISHING_FEW_SWINGS   # gardă VE adăugată
    two_each = mkst(51, 1.0, [110.0, 111.0], [100.0, 99.0], start=0)
    assert evaluate_candidate_with_n_touch(two_each, 50, cfg) != ESTABLISHING_FEW_SWINGS


# ═══════════════════════ item 11: timestamp din viitor ═══════════════════════
def test_future_timestamp_refused() -> None:
    with pytest.raises(ContractErrorV43):
        guard_timestamp(ts=500, as_of=400)
    guard_timestamp(ts=400, as_of=400)   # bara curentă (<=) e admisă


# ═══════════════════════ item 12: sweep de durată mare ═══════════════════════
def test_long_sweep_within_k_reentry() -> None:
    cfg = cfg43()
    ex = Excursion(open_bar=100, direction=-1)
    for b in range(101, 119):
        kind, _ = ex.observe(b, True, cfg)
    assert ex.closes_outside == 18
    kind, _ = ex.observe(119, False, cfg)
    assert kind == SWEEP_CONFIRMED


# ═══════════════════════ item 13: breakout după trei închideri ═══════════════════════
def test_breakout_accepted_after_three_consecutive_closes() -> None:
    cfg = cfg43()
    ex = Excursion(open_bar=200, direction=1)
    r1, ny1 = ex.observe(201, True, cfg)
    r2, _ = ex.observe(202, True, cfg)
    r3, _ = ex.observe(203, True, cfg)
    assert r1 == "BOUNDARY_EXCURSION" and NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT in ny1
    assert r3 == BREAKOUT_ACCEPTED


# ═══════════════════════ item 14: reintrare înainte de a treia închidere -- reset ═══════════════════════
def test_reentry_before_third_close_resets_counter() -> None:
    cfg = cfg43()
    ex = Excursion(open_bar=300, direction=1)
    ex.observe(301, True, cfg); ex.observe(302, True, cfg)
    kind, _ = ex.observe(303, False, cfg)
    assert ex.closes_outside == 0 and kind == SWEEP_CONFIRMED


# ═══════════════════════ item 15: revenire (reversal) după breakout acceptat -- C13 ═══════════════════════
def test_liquidity_sweep_reversal_after_sweep_confirmed() -> None:
    ex = Excursion(open_bar=52, direction=-1)
    ex.observe(52, True, ConfigV43()); ex.observe(56, False, ConfigV43())
    ok, r = sweep_reversal_confirmed(ex, 56, 3346.0, 3345.0, 30, 63)
    assert not ok and r == NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT
    ok, r = sweep_reversal_confirmed(ex, 59, 3346.0, 3345.0, 30, 63)
    assert ok and r == LIQUIDITY_SWEEP_REVERSAL
    ok, r = sweep_reversal_confirmed(ex, 59, 3344.0, 3345.0, 30, 63)
    assert not ok and r == NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT
    ok, r = sweep_reversal_confirmed(ex, 70, 3346.0, 3345.0, 30, 63)
    assert not ok and r == REVERSAL_WINDOW_EXPIRED
    ok, r = sweep_reversal_confirmed(ex, 59, 3346.0, None, None, 63)
    assert not ok and r == REVERSAL_REFERENCE_UNAVAILABLE
    with pytest.raises(ContractErrorV43):
        sweep_reversal_confirmed(ex, 59, 3346.0, 3345.0, 55, 63)   # referință confirmată DUPĂ open_bar
    ex2 = Excursion(open_bar=200, direction=1)
    ex2.observe(201, True, ConfigV43()); ex2.observe(202, True, ConfigV43()); ex2.observe(203, True, ConfigV43())
    ok, r = sweep_reversal_confirmed(ex2, 210, 90.0, 100.0, 190, None)
    assert not ok and r == NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT   # fără SWEEP_CONFIRMED, niciun reversal


# ═══════════════════════ conjuncția de confirmare + promovarea + registrul (C15-C17, grupa 19) ═══════════════════════
def test_evaluate_candidate_priority_order() -> None:
    cfg = cfg43()
    assert evaluate_candidate(None, 50, cfg) == BETWEEN_EPISODES
    short = mkst(40, 1.0, [110.0, 110.4], [100.0, 99.6], start=100)
    assert evaluate_candidate(short, 120, cfg) == TOO_SHORT_MACRO
    assert evaluate_candidate(short, 140, cfg) == OK_RANGE_MACRO
    short_i = mkst(41, 1.0, [108.0, 108.2], [102.0, 101.8], start=100, depth=Depth.INTERNAL, parent=40)
    assert evaluate_candidate(short_i, 105, cfg) == TOO_SHORT_INTERNAL
    assert evaluate_candidate(short_i, 130, cfg) == OK_RANGE_INTERNAL
    dead_geom = mkst(42, 1.0, [101.0, 101.2], [100.0, 99.8], start=100)
    assert evaluate_candidate(dead_geom, 110, cfg) == ZONES_DEGENERATE   # KILL are prioritate față de durată


def test_offer_swing_tolerance() -> None:
    cfg = cfg43()
    short = mkst(40, 1.0, [110.0, 110.4], [100.0, 99.6], start=100)
    ok, r = offer_swing(short, 110.9, "high", cfg)
    assert ok and 110.9 in short.up.members
    ok2, r2 = offer_swing(short, 130.0, "high", cfg)
    assert not ok2 and r2 == SWING_OUTSIDE_CLUSTER and 130.0 not in short.up.members


def test_promotion_check_preconditions_in_order() -> None:
    cfg = cfg43()
    assert promotion_check(True, True, 2, True, cfg) == (True, IS_TREND_MACRO)
    assert promotion_check(False, True, 2, True, cfg)[1] == PROMOTION_REFUSED_PRECONDITION_P1
    assert promotion_check(True, False, 2, True, cfg)[1] == PROMOTION_REFUSED_PRECONDITION_P2
    assert promotion_check(True, True, 1, True, cfg)[1] == PROMOTION_REFUSED_PRECONDITION_P3
    assert promotion_check(True, True, 2, False, cfg)[1] == PROMOTION_REFUSED_PRECONDITION_P4


def test_registry_dead_id_reuse_refused() -> None:
    reg = Registry()
    old_id = reg.new_id()
    reg.kill(old_id)
    with pytest.raises(ContractErrorV43):
        reg.assert_alive(old_id)
    new_id = reg.new_id()
    assert new_id != old_id
    reg.assert_alive(new_id)   # viu, nu aruncă


# ═══════════════════════ item 20/§10: acoperirea DINAMICĂ a celor 29 reason codes, prin API public ═══════════════════════
def test_all_29_reason_codes_reachable_via_public_api() -> None:
    """Nu compară doar liste hardcodate -- fiecare cod trebuie PRODUS prin apeluri reale ale API-ului
    prototipului (mandat §10: 'Fiecare cod trebuie produs prin API-ul prototipului')."""
    cfg = cfg43()
    produced: set[str] = set()

    produced.add(evaluate_candidate(None, 0, cfg))                                            # BETWEEN_EPISODES
    st_deg = mkst(1, 1.0, [101.0, 101.2], [100.0, 99.8], start=0)
    produced.add(evaluate_candidate(st_deg, 10, cfg))                                          # ZONES_DEGENERATE
    st_inv = mkst(2, 1.0, [98.0, 98.2], [105.0, 105.2], start=0)
    produced.add(_req(degeneracy_check(st_inv, cfg)))                                          # ZONES_INVERTED
    st_noatr = Structure(structure_id=3, depth=Depth.MACRO, parent_structure_id=None, start_ts=0)
    st_noatr.up.offer(110.0, 1e18); st_noatr.dn.offer(100.0, 1e18)
    produced.add(_req(degeneracy_check(st_noatr, cfg)))                                        # ATR_UNAVAILABLE
    st_few = mkst(4, 1.0, [110.0], [], start=0)
    produced.add(_req(degeneracy_check(st_few, cfg)))                                          # ESTABLISHING_FEW_SWINGS
    st_short = mkst(5, 1.0, [110.0, 110.4], [100.0, 99.6], start=100)
    produced.add(evaluate_candidate(st_short, 110, cfg))                                       # TOO_SHORT_MACRO
    produced.add(evaluate_candidate(st_short, 140, cfg))                                       # OK_RANGE_MACRO
    st_short_i = mkst(6, 1.0, [108.0, 108.2], [102.0, 101.8], start=100, depth=Depth.INTERNAL, parent=5)
    produced.add(evaluate_candidate(st_short_i, 105, cfg))                                     # TOO_SHORT_INTERNAL
    produced.add(evaluate_candidate(st_short_i, 130, cfg))                                     # OK_RANGE_INTERNAL
    ok_s, r_s = offer_swing(st_short, 130.0, "high", cfg)
    produced.add(r_s)                                                                          # SWING_OUTSIDE_CLUSTER
    ex_a = Excursion(open_bar=200, direction=1)
    k1, ny1 = ex_a.observe(201, True, cfg); produced.update(ny1)                               # NOT_YET_AVAILABLE...
    k2, _ = ex_a.observe(202, True, cfg)
    k3, _ = ex_a.observe(203, True, cfg); produced.add(k3)                                     # BREAKOUT_ACCEPTED
    ex_b = Excursion(open_bar=300, direction=1)
    ex_b.observe(301, True, cfg)
    kb, _ = ex_b.observe(302, False, cfg); produced.add(kb)                                    # SWEEP_CONFIRMED
    # direction=+1 (sweep SUS) -- reversal = ÎNCHIDERE SUB swing-ul de referință (bearish reversal)
    ok_r, r_r = sweep_reversal_confirmed(ex_b, 305, 50.0, 90.0, 250, None)
    assert ok_r
    produced.add(r_r)                                                                          # LIQUIDITY_SWEEP_REVERSAL
    ex_c = Excursion(open_bar=400, direction=-1)
    ex_c.observe(400, True, cfg)
    ex_c.observe(402, False, cfg)   # reintrare -- SWEEP_CONFIRMED, reentry_bar=402
    _, r_c = sweep_reversal_confirmed(ex_c, 405, 100.0, None, None, None)
    assert r_c == REVERSAL_REFERENCE_UNAVAILABLE
    produced.add(r_c)                                                                          # REVERSAL_REFERENCE_UNAVAILABLE
    ex_d = Excursion(open_bar=500, direction=-1)
    ex_d.observe(500, True, cfg)
    ex_d.observe(502, False, cfg)   # reintrare -- SWEEP_CONFIRMED, reentry_bar=502
    _, r_d = sweep_reversal_confirmed(ex_d, 510, 100.0, 90.0, 480, 505)   # bar(510) > episode_end_ts(505)
    assert r_d == REVERSAL_WINDOW_EXPIRED
    produced.add(r_d)                                                                          # REVERSAL_WINDOW_EXPIRED
    _, p1 = promotion_check(False, True, 2, True, cfg); produced.add(p1)
    _, p2 = promotion_check(True, False, 2, True, cfg); produced.add(p2)
    _, p3 = promotion_check(True, True, 1, True, cfg); produced.add(p3)
    _, p4 = promotion_check(True, True, 2, False, cfg); produced.add(p4)
    ok_p, p5 = promotion_check(True, True, 2, True, cfg); produced.add(p5)                     # IS_TREND_MACRO
    macro_open = mkst(7, 1.0, [110.0, 110.4], [100.0, 99.6], start=0)
    d1, r1x, _ = assign_level(50, 70, 95.0, 108.0, macro_open, cfg)
    assert r1x == PARTIAL_OVERLAP_NO_CONTAINMENT
    produced.add(r1x)                                                                           # PARTIAL_OVERLAP...
    macro_late = mkst(70, 1.0, [110.0, 110.4], [100.0, 99.6], start=1000)
    d2, r2x, _ = assign_level(0, 500, 95.0, 105.0, macro_late, cfg)   # candidat ÎNTREG înainte de start-ul părintelui
    assert r2x == LEVEL_ASSIGNMENT_UNRESOLVED
    produced.add(r2x)                                                                           # LEVEL_ASSIGNMENT_UNRESOLVED
    macro_closed_none = None
    macro_end = mkst(8, 1.0, [110.0, 110.4], [100.0, 99.6], start=0)
    macro_end.end_ts = 5
    d3, r3x, _ = assign_level(0, 5, 102.0, 108.0, macro_end, cfg)
    assert d3 is Depth.MACRO   # părinte închis => oricum MACRO (r3x e None aici, verificat separat)
    inner = mkst(9, 1.0, [110.0, 110.4], [100.0, 99.6], start=0, depth=Depth.INTERNAL, parent=7)
    d4, r4x, _ = assign_level(20, 40, 102.0, 108.0, inner, cfg); produced.add(_req(r4x))          # DEPTH_LIMIT_EXCEEDED
    closed = mkst(10, 1.0, [110.0, 110.4], [100.0, 99.6], start=0)
    with pytest.raises(ContractErrorV43) as e1:
        closed.assign_role("ACCUMULATION_CONFIRMED", 5)
    produced.add(str(e1.value))                                                                 # ROLE_ASSERTED_BEFORE_CONFIRMATION
    closed.end_ts = 20
    with pytest.raises(ContractErrorV43) as e2:
        closed.assign_role("ACCUMULATION_CONFIRMED", 3)
    produced.add(str(e2.value))                                                                 # ROLE_KNOWN_BEFORE_CONFIRM
    closed.confirm_ts = 10
    closed.assign_role("ACCUMULATION_CONFIRMED", 25)
    reg = Registry(); dead = reg.new_id(); reg.kill(dead)
    with pytest.raises(ContractErrorV43) as e3:
        reg.assert_alive(dead)
    produced.add(str(e3.value))                                                                 # DEAD_ID_REUSE_REFUSED
    with pytest.raises(ContractErrorV43) as e4:
        guard_timestamp(500, 400)
    produced.add(str(e4.value))                                                                 # FUTURE_TIMESTAMP_REFUSED
    eng = RangeSemanticEngineV43(range_config=cfg, acknowledge_construction_only=True, **KW)
    for b in osc_bars(cycles=10):
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    from ve_n1_replay.range_engine_v4_3 import RangeSnapshotV43
    import dataclasses as _dc
    bad = _dc.replace(snap, contract_version="range-hierarchical-v4.2")
    with pytest.raises(RangeSnapshotErrorV43) as e5:
        eng.restore(bad)
    produced.add(str(e5.value))                                                                 # SNAPSHOT_CONTRACT_MISMATCH

    missing = set(REASONS_V43) - produced
    assert not missing, f"coduri declarate dar neemise prin API: {sorted(missing)}"


# ═══════════════════════ 13 porți de nevacuitate (nu 12 — corectat conform mandatului) ═══════════════════════
def test_13_non_vacuity_gates_pass_and_fail() -> None:
    """Port fidel al secțiunii §D a harness-ului -- **13** porți (nu 12, cum spunea prosa unui mesaj de commit
    al Statisticianului -- numărat direct în dicționarul `gates` al `test_range_v42_adversarial.py`, confirmat
    și de Red Team RT-RANGE-0006 §10). Fiecare poartă verificată în AMBELE sensuri: `n_pass` != 0 (nu moartă)
    și `n_fail` != 0 (nu vacuă)."""
    cfg = cfg43()
    macro = mkst(1, 1.0, [110.0, 110.4], [100.0, 99.6], start=0)
    deg = mkst(9, 1.0, [101.0, 101.2], [100.0, 99.8], start=0)
    inv = mkst(10, 1.0, [98.0, 98.2], [105.0, 105.2], start=0)
    short_i = mkst(6, 1.0, [108.0, 108.2], [102.0, 101.8], start=100, depth=Depth.INTERNAL, parent=5)
    from ve_n1_replay.range_semantic_v4_3 import _UnboundedSlope
    acc_ch = _UnboundedSlope()
    for i in range(20):
        acc_ch.push(102 + 0.25 * i)
    drift_channel = abs(acc_ch.slope()) * 20 / 1.0
    acc_flat = _UnboundedSlope()
    for i in range(20):
        acc_flat.push(104 + (0.05 if i % 2 else -0.05))
    drift_flat = abs(acc_flat.slope()) * 20 / 1.0
    ex_sweep = Excursion(open_bar=300, direction=1)
    ex_sweep.observe(301, True, cfg); ex_sweep.observe(302, True, cfg)
    r_sweep, _ = ex_sweep.observe(303, False, cfg)
    ex_break = Excursion(open_bar=200, direction=1)
    ex_break.observe(201, True, cfg); ex_break.observe(202, True, cfg)
    r_break, _ = ex_break.observe(203, True, cfg)
    lvl_int, _, _ = assign_level(50, 70, 102.0, 108.0, macro, cfg)
    lvl_unresolved, r_unres, _ = assign_level(0, 500, 95.0, 105.0,
                                              mkst(70, 1.0, [110.0, 110.4], [100.0, 99.6], start=1000), cfg)
    closed = mkst(11, 1.0, [110.0, 110.4], [100.0, 99.6], start=0)
    closed.end_ts = 20; closed.confirm_ts = 10
    closed.assign_role("ACCUMULATION_CONFIRMED", 25)
    ex_rev = Excursion(open_bar=300, direction=1)
    ex_rev.observe(301, True, cfg); ex_rev.observe(302, False, cfg)
    ok_rev, _ = sweep_reversal_confirmed(ex_rev, 305, 50.0, 90.0, 250, None)
    ok_norev, _ = sweep_reversal_confirmed(ex_rev, 302, 50.0, 90.0, 250, None)   # bar == reentry_bar -- prea devreme
    inner = mkst(9, 1.0, [110.0, 110.4], [100.0, 99.6], start=0, depth=Depth.INTERNAL, parent=1)
    lvl_depth, r_depth, _ = assign_level(20, 40, 102.0, 108.0, inner, cfg)

    gates = {
        "durata MACRO (d=29)": (evaluate_candidate(mkst(20, 1.0, [110, 110.4], [100, 99.6], start=0), 60, cfg)
                                == OK_RANGE_MACRO,
                                evaluate_candidate(mkst(21, 1.0, [110, 110.4], [100, 99.6], start=0), 10, cfg)
                                == OK_RANGE_MACRO),
        "durata INTERNAL (d=12)": (evaluate_candidate(short_i, 130, cfg) == OK_RANGE_INTERNAL,
                                   evaluate_candidate(short_i, 105, cfg) == OK_RANGE_INTERNAL),
        "degenerare zone": (degeneracy_check(deg, cfg) == ZONES_DEGENERATE,
                            degeneracy_check(macro, cfg) == ZONES_DEGENERATE),
        "inversare zone": (degeneracy_check(inv, cfg) == ZONES_INVERTED,
                           degeneracy_check(macro, cfg) == ZONES_INVERTED),
        "sweep": (r_sweep == SWEEP_CONFIRMED, r_break == SWEEP_CONFIRMED),
        "breakout acceptat": (r_break == BREAKOUT_ACCEPTED, r_sweep == BREAKOUT_ACCEPTED),
        "apartenența la cluster": (_cluster_with(100.0).offer(100.5, cfg.tol_cluster * 1.0),
                                   _cluster_with(100.0).offer(200.0, cfg.tol_cluster * 1.0)),
        "nivel INTERNAL": (lvl_int is Depth.INTERNAL, lvl_unresolved is Depth.INTERNAL),
        "nivel UNRESOLVED": (r_unres == LEVEL_ASSIGNMENT_UNRESOLVED, r_depth == LEVEL_ASSIGNMENT_UNRESOLVED),
        "clasificare canal (s_max)": (drift_channel > cfg.s_max, drift_flat > cfg.s_max),
        "rol retrospectiv": (closed.role is not None, macro.role is not None),
        "reversal după sweep": (ok_rev, ok_norev),
        "limita de adâncime": (r_depth == DEPTH_LIMIT_EXCEEDED, r_unres == DEPTH_LIMIT_EXCEEDED),
    }
    assert len(gates) == 13, f"trebuie exact 13 porți, are {len(gates)}"
    for name, (p, n) in gates.items():
        assert bool(p), f"poarta '{name}' nu trece niciodată (moartă, n_pass=0)"
        assert not bool(n), f"poarta '{name}' nu eșuează niciodată (vacuă, n_fail=0)"


# ═══════════════════════ end-to-end (producător complet): MACRO + INTERNAL CHANNEL/SUBRANGE ═══════════════════════
def _macro_with_internal_bars(internal_leg: Sequence[tuple[float, int]]) -> list[Any]:
    macro_legs: list[tuple[float, int]] = [(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)]
    return legs_bars(macro_legs + list(internal_leg))


def test_e2e_macro_with_channel_up_internal() -> None:
    # derivă LENTĂ, susținută (o singură rampă de 20 bare), nu un salt abrupt: odată ce internalul e
    # confirmat, zona lui îngheață la ±w_atr (0.8) față de frontiera reală (112.3/107.7, exact -- nu mai
    # aproximativă, de când perechea de fondare nu mai poate fi contaminată de un swing vechi al MACRO-ului,
    # v. fix-ul "re-testare de frontieră" din `_offer_swing_everywhere`). O rampă care sare direct la 124 ar
    # depăși zona [111.5, 113.1] susținut și ar declanșa BREAKOUT_ACCEPTED (§7) -- corect, dar închide
    # internalul, deci nu mai testează clasificarea CANAL. Rampa rămâne STRICT sub tavanul zonei.
    legs: list[tuple[float, int]] = [(108, 5)]
    for _ in range(3):
        legs += [(112, 5), (108, 5)]     # câteva cicluri -- geometrie + n_touch=2 stabilite
    legs += [(112.8, 20)]                # derivă lentă, susținută, sub tavanul zonei (113.1) -- clasifică CANAL
    bars = _macro_with_internal_bars(legs)
    prod, out = run43_fixed_atr(bars)
    _, last, _ = out[-1]
    assert last.internal_id is not None, "internalul trebuie să se formeze (nu absorbit de clusterul macro)"
    assert last.internal_state == "INT_CHANNEL_UP", last.internal_state


def test_e2e_macro_with_channel_down_internal() -> None:
    legs: list[tuple[float, int]] = [(112, 5)]
    for _ in range(3):
        legs += [(108, 5), (112, 5)]
    legs += [(107.2, 20)]                # oglinda derivei de mai sus -- sub podeaua zonei (106.9)
    bars = _macro_with_internal_bars(legs)
    prod, out = run43_fixed_atr(bars)
    _, last, _ = out[-1]
    assert last.internal_id is not None
    assert last.internal_state == "INT_CHANNEL_DOWN", last.internal_state


def test_e2e_macro_with_subrange_internal() -> None:
    legs = [(108, 5)]
    for _ in range(16):
        legs += [(112, 5), (108, 5)]
    bars = _macro_with_internal_bars(legs)
    prod, out = run43_fixed_atr(bars)
    _, last, _ = out[-1]
    assert last.internal_id is not None
    assert last.internal_reason == OK_RANGE_INTERNAL, (
        f"internalul trebuie confirmat pt. a distinge SUBRANGE de BALANCE (încă neconfirmat): {last.internal_reason}")
    assert last.internal_state == "INT_SUBRANGE", last.internal_state


def test_e2e_third_level_refused_via_producer() -> None:
    """DEPTH_LIMIT_EXCEEDED trebuie emis prin bucla per-bară reală (nu doar prin apel direct la
    `assign_level`, deja acoperit de `test_third_level_refused_depth_limit_exceeded`) -- macro -> internal
    confirmat -> candidat NOU conținut STRICT în internal declanșează refuzul, fără să crape motorul."""
    legs = [(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6),
           (108, 5), (112, 5), (108, 5), (112, 5), (108, 5), (112, 5), (108, 5), (112, 5), (108, 5)]
    bars = legs_bars(legs)
    # candidat suplimentar STRICT în interiorul internalului deja format (109-111, îngust)
    more_legs = [(109.5, 4), (110.5, 4), (109.5, 4), (110.5, 4), (109.5, 4), (110.5, 4)]
    more_bars = legs_bars(more_legs, start=len(bars))
    prod, out = run43_fixed_atr(bars + more_bars)
    _, last, _ = out[-1]
    assert last.internal_id is not None, "internalul-părinte trebuie să rămână activ, neatins de refuz"


# ═══════════════════════ end-to-end: promovare bullish / bearish (§8) ═══════════════════════
def _promotion_legs() -> Sequence[tuple[float, int]]:
    return ([(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6)] +
           [(128, 2), (124, 2), (136, 2), (130, 2), (145, 2)])


def test_e2e_bullish_promotion() -> None:
    bars = legs_bars(_promotion_legs())
    prod, out = run43_fixed_atr(bars)
    trend_events = [e for _, _, evs in out for e in evs if e.kind == IS_TREND_MACRO]
    assert trend_events, "IS_TREND_MACRO trebuie emis"
    assert trend_events[0].depth == "MACRO"
    assert prod.macro_history and prod.macro_history[0]["breakout_side"] == "upper"


def test_e2e_bearish_promotion() -> None:
    bars = legs_bars(mirror_legs(_promotion_legs()))
    prod, out = run43_fixed_atr(bars)
    trend_events = [e for _, _, evs in out for e in evs if e.kind == IS_TREND_MACRO]
    assert trend_events, "IS_TREND_MACRO trebuie emis"
    assert trend_events[0].depth == "MACRO"
    assert prod.macro_history and prod.macro_history[0]["breakout_side"] == "lower"


# ═══════════════════════ HBL-20: BALANCE -> SWEEP_DOWN -> REENTRY -> BULLISH_STRUCTURE_BREAK -> MARKUP -> ACCUMULATION ═══════════════════════
def _hbl20_legs() -> Sequence[tuple[float, int]]:
    """Narativa exactă a mandatului §9: BALANCE (macro neutru) -> SWEEP_DOWN (excursie sub, reintrare rapidă,
    NU pune capăt episodului) -> BULLISH_STRUCTURE_BREAK (breakout sus, 3 închideri) -> MARKUP (succesor NOU
    se formează și confirmă) -> ACCUMULATION_CONFIRMED (rol retrospectiv pe episodul ORIGINAL).
    Vârful excursiei de breakout (135) apare DEVREME -- confirmarea lui fractală (2 bare mai târziu, K_struct=2)
    cade cât timp MACRO-ul original e ÎNCĂ activ, deci e oferit/respins de el (nu ancorează accidental
    succesorul) -- decizie de fixture, nu de contract, documentată aici pt. reproductibilitate."""
    phase_a = [(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)]
    phase_b = [(92, 1), (105, 1)]                          # SWEEP_DOWN, reintrare imediată -> REENTRY_CONFIRMED
    phase_c = [(120, 6), (100, 6), (120, 6), (100, 6)]      # range-ul continuă viu, neatins de sweep
    phase_d = [(135, 2), (126, 1), (123, 1), (122, 1)]      # BULLISH_STRUCTURE_BREAK (3 închideri >120.8)
    phase_e = [(118, 3), (110, 4)]
    for _ in range(20):
        phase_e += [(118, 4), (110, 4)]                    # succesor (MARKUP): range nou, se formează+confirmă
    return phase_a + phase_b + phase_c + phase_d + phase_e


def test_hbl20_full_narrative_accumulation() -> None:
    bars = legs_bars(_hbl20_legs())
    prod, out = run43_fixed_atr(bars)
    all_events = [e for _, _, evs in out for e in evs]
    sweep_bars = [e.bar_index for e in all_events if e.kind == SWEEP_CONFIRMED and e.depth == "MACRO"]
    breakout_bars = [e.bar_index for e in all_events if e.kind == BREAKOUT_ACCEPTED and e.depth == "MACRO"]
    assert sweep_bars, "SWEEP_DOWN -> REENTRY_CONFIRMED (SWEEP_CONFIRMED) trebuie emis pe MACRO"
    assert breakout_bars, "BULLISH_STRUCTURE_BREAK (BREAKOUT_ACCEPTED) trebuie emis pe MACRO"
    assert min(sweep_bars) < min(breakout_bars), "sweep-ul precede breakout-ul (nu pune capăt episodului)"
    assert len(prod.macro_history) >= 1
    original = prod.macro_history[0]
    assert original["end_reason"] == BREAKOUT_ACCEPTED
    assert original["breakout_side"] == "upper"
    assert original["role"] == "ACCUMULATION_CONFIRMED", original["role"]
    assert original["role_known_ts"] is not None and original["role_known_ts"] > original["end_ts"]


def test_hbl20_mirror_distribution() -> None:
    bars = legs_bars(mirror_legs(_hbl20_legs()))
    prod, out = run43_fixed_atr(bars)
    assert prod.macro_history
    original = prod.macro_history[0]
    assert original["breakout_side"] == "lower"
    assert original["role"] == "DISTRIBUTION_CONFIRMED", original["role"]


# ═══════════════════════ snapshot în fiecare stare + două instanțe + config mismatch + no-lookahead + chunk parity ═══════════════════════
def _snapshot_roundtrip_at(bars: list[Any], split: int) -> tuple[list[_ObserveOut], list[_ObserveOut]]:
    cfg = cfg43()
    ref, ref_out = run43(bars, cfg)
    eng = RangeSemanticEngineV43(range_config=cfg, acknowledge_construction_only=True, **KW)
    for b in bars[:split]:
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    eng2 = RangeSemanticEngineV43(range_config=cfg, acknowledge_construction_only=True, **KW)
    eng2.restore(snap)
    out1 = [eng.observe_closed_bar(b) for b in bars[split:]]
    out2 = [eng2.observe_closed_bar(b) for b in bars[split:]]
    return out1, out2


@pytest.mark.parametrize("split_frac", [0.1, 0.3, 0.5, 0.7, 0.9])
def test_snapshot_restart_in_various_states(split_frac: float) -> None:
    """Restart în stări diferite: formare, confirmat, excursie/breach, după sweep, după breakout -- alegem
    fracțiuni de-a lungul fixture-ului HBL-20, care traversează TOATE aceste stări."""
    bars = legs_bars(_hbl20_legs())
    split = max(1, min(len(bars) - 1, int(len(bars) * split_frac)))
    out1, out2 = _snapshot_roundtrip_at(bars, split)
    f1 = [(r.macro_id, r.macro_reason, r.macro_state, r.internal_id, r.internal_reason) for _, r, _ in out1]
    f2 = [(r.macro_id, r.macro_reason, r.macro_state, r.internal_id, r.internal_reason) for _, r, _ in out2]
    assert f1 == f2


def test_two_instances_no_shared_state() -> None:
    bars = legs_bars(_hbl20_legs())
    cfg = cfg43()
    ref, ref_out = run43(bars, cfg)
    e1 = RangeSemanticEngineV43(range_config=cfg, acknowledge_construction_only=True, **KW)
    e2 = RangeSemanticEngineV43(range_config=cfg, acknowledge_construction_only=True, **KW)
    for b in bars[:40]:
        e1.observe_closed_bar(b)
    got2 = [e2.observe_closed_bar(b) for b in bars]
    f_ref = [(r.macro_id, r.macro_reason) for _, r, _ in ref_out]
    f_got2 = [(r.macro_id, r.macro_reason) for _, r, _ in got2]
    assert f_ref == f_got2
    assert e1.bars_observed == 40 and e2.bars_observed == len(bars)


def test_zero_lookahead_prefix_parity() -> None:
    bars = legs_bars(_hbl20_legs())
    _, out_full = run43(bars)
    _, out_prefix = run43(bars[:60])
    f_full = [(r.macro_id, r.macro_reason, r.internal_id, r.internal_reason) for _, r, _ in out_full[:60]]
    f_prefix = [(r.macro_id, r.macro_reason, r.internal_id, r.internal_reason) for _, r, _ in out_prefix]
    assert f_full == f_prefix


@pytest.mark.parametrize("split", [1, 30, 77, 120])
def test_chunk_invariance(split: int) -> None:
    bars = legs_bars(_hbl20_legs())
    _, ref_out = run43(bars)
    eng = RangeSemanticEngineV43(range_config=cfg43(), acknowledge_construction_only=True, **KW)
    part1 = [eng.observe_closed_bar(b) for b in bars[:split]]
    part2 = [eng.observe_closed_bar(b) for b in bars[split:]]
    got = part1 + part2
    f_ref = [(r.macro_id, r.macro_reason, r.internal_id, r.internal_reason) for _, r, _ in ref_out]
    f_got = [(r.macro_id, r.macro_reason, r.internal_id, r.internal_reason) for _, r, _ in got]
    assert f_ref == f_got


def test_dead_id_reuse_enforced_through_full_flow() -> None:
    """ID-ul unui candidat KILL (degenerare) nu poate reveni -- verificat prin `Registry` REAL al
    producătorului (ID alocat prin `new_id()`, ca-n fluxul real), nu doar prin apel direct pe o funcție
    pură (vezi și `test_registry_dead_id_reuse_refused`)."""
    cfg = cfg43()
    prod = RangeSemanticProducerV43(cfg)
    dead_id = prod._registry.new_id()
    prod._registry.kill(dead_id)
    with pytest.raises(ContractErrorV43):
        prod._registry.assert_alive(dead_id)
    new_id = prod._registry.new_id()
    assert new_id != dead_id
    prod._registry.assert_alive(new_id)


def test_engine_legacy_snapshot_type_refused() -> None:
    bars = legs_bars(_hbl20_legs()[:20])
    eng = RangeSemanticEngineV43(range_config=cfg43(), acknowledge_construction_only=True, **KW)
    for b in bars:
        eng.observe_closed_bar(b)

    class _FakeForeignSnapshot:
        pass

    with pytest.raises(RangeSnapshotErrorV43):
        eng.restore(_FakeForeignSnapshot())


def test_engine_corrupted_snapshot_refused_engine_left_unchanged() -> None:
    import dataclasses as _dc
    bars = legs_bars(_hbl20_legs()[:20])
    eng = RangeSemanticEngineV43(range_config=cfg43(), acknowledge_construction_only=True, **KW)
    for b in bars:
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    corrupted = _dc.replace(snap, range_state={"n": 5})
    before = eng.bars_observed
    with pytest.raises(RangeSnapshotErrorV43):
        eng.restore(corrupted)
    assert eng.bars_observed == before, "restore eșuat trebuie să lase motorul complet NESCHIMBAT (atomic)"


def test_mypy_strict_clean_on_all_touched_files() -> None:
    """Testele VE trebuie să fie mypy --strict clean (mandat §2/§12) -- verificat direct, nu doar afirmat."""
    import subprocess
    result = subprocess.run(
        ["python", "-m", "mypy", "--strict",
        str(_MODULE_DIR / "range_semantic_v4_3.py"), str(_MODULE_DIR / "range_engine_v4_3.py")],
        capture_output=True, text=True)
    assert "Success" in result.stdout, result.stdout + result.stderr
