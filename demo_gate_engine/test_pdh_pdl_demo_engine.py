"""Teste pentru motorul DEMO PDH-PDL — un test per gard care PICĂ fără el și TRECE cu el.

„Pică fără el" = arătat prin contrast: valoarea naivă (ne-gardată) diferă de rezultatul gardat al motorului.
Date sintetice; fără MT5, fără date reale. Motorul e pur. Acoperă și corecțiile RT-CODE-A-0005 (D1/D2/R1/R2).
"""

from __future__ import annotations

import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from pdh_pdl_demo_engine import (  # noqa: E402
    DemoSignal, ExitReason, min_executable_risk, simulate_demo_trade, simulate_demo_trades,
)

TICK = 0.1


def _bars(n: int, hi: float = 100.5, lo: float = 99.5) -> tuple[list[float], list[float], list[float], list[float]]:
    return [100.0] * n, [hi] * n, [lo] * n, [100.0] * n


def _sig(**kw: float) -> DemoSignal:
    base = dict(entry_idx=1, direction=1, strategy_stop_price=98.0, target_price=104.0,
                atr=1.0, effective_spread=0.1, cost=0.0, time_stop_idx=5)
    base.update(kw)
    return DemoSignal(entry_idx=int(base["entry_idx"]), direction=int(base["direction"]),
                      strategy_stop_price=base["strategy_stop_price"], target_price=base["target_price"],
                      atr=base["atr"], effective_spread=base["effective_spread"], cost=base["cost"],
                      time_stop_idx=int(base["time_stop_idx"]))


# ───────────────────────────── S1 — ierarhie STOP > TIME-STOP > TARGET ─────────────────────────────
def test_s1_stop_and_target_same_bar_resolves_STOP() -> None:
    """CERINȚA CENTRALĂ: o bară care atinge ȘI stopul ȘI ținta trebuie să rezolve STOP (pierdere), nu ținta."""
    o, h, l, c = _bars(7)
    l[2] = 97.0; h[2] = 105.0                 # bara ei+1 atinge AMBELE (stop 98, țintă 104)
    sig = _sig(time_stop_idx=5)               # bara 2 NU e graniță (izolează stop∧țintă)
    r = simulate_demo_trade(sig, o, h, l, c, TICK)
    assert r.exit_reason == ExitReason.STOP.value
    assert r.intrabar_ordering == "stop_over_target"
    assert r.exit_price == 98.0 and r.net_R is not None and r.net_R < 0     # pierdere
    hitS = l[2] <= r.executable_stop_price
    hitT = h[2] >= sig.target_price
    assert hitS and hitT                       # un motor target-first ar fi ales ținta → rezultat DIFERIT


def test_s1_target_and_timestop_on_boundary_resolves_TIME_STOP() -> None:
    o, h, l, c = _bars(5)
    h[3] = 105.0; l[3] = 99.0; c[3] = 101.0   # bara-graniță atinge ținta dar NU stopul
    sig = _sig(time_stop_idx=3)
    r = simulate_demo_trade(sig, o, h, l, c, TICK)
    assert r.exit_reason == ExitReason.TIME_STOP.value
    assert r.intrabar_ordering == "time_stop_over_target"
    assert r.exit_price == 101.0                                # close-ul, NU ținta 104
    assert h[3] >= sig.target_price


def test_s1_stop_and_timestop_on_boundary_resolves_STOP() -> None:
    o, h, l, c = _bars(5)
    l[3] = 97.0; c[3] = 100.0                 # bara-graniță atinge stopul
    sig = _sig(time_stop_idx=3)
    r = simulate_demo_trade(sig, o, h, l, c, TICK)
    assert r.exit_reason == ExitReason.STOP.value
    assert r.intrabar_ordering == "stop_over_time_stop"
    assert r.exit_price == 98.0


def test_s1_triple_collision_stop_target_timestop_resolves_STOP() -> None:
    """Coliziune TRIPLĂ pe bara-graniță: stop ȘI țintă ȘI time-stop → STOP (ordinea integrală)."""
    o, h, l, c = _bars(5)
    l[3] = 97.0; h[3] = 105.0; c[3] = 101.0   # bara 3 = graniță, atinge stop 98 ȘI țintă 104
    sig = _sig(time_stop_idx=3)
    r = simulate_demo_trade(sig, o, h, l, c, TICK)
    assert r.exit_reason == ExitReason.STOP.value
    assert r.intrabar_ordering == "stop_over_target_time_stop"
    assert r.exit_price == 98.0 and r.net_R is not None and r.net_R < 0


# ───────────────────────────── D1 (RT-CODE-A-0005) — S1 pe bara de INTRARE, la TOATE tranzacțiile ─────────────────────────────
def test_d1_entry_bar_stop_unfloored_is_STOP_not_target() -> None:
    """DEFECT D1 (fostul fixture care CODIFICA eroarea): long, stop 99 nepodit, low[ei]=98,9 trece prin stop,
    bara următoare high 105. Motorul TREBUIE să dea STOP (pierdere pe bara de intrare), NU TARGET (câștig)."""
    o, h, l, c = _bars(7, lo=98.9)
    l[2] = 99.6; h[2] = 105.0                  # bara ei+1 ar atinge ținta dacă intrarea ar supraviețui
    r = simulate_demo_trade(_sig(strategy_stop_price=99.0), o, h, l, c, TICK)  # dist 1,0 → nepodit; exec_stop 99,0
    assert r.floored is False
    assert r.exit_reason == ExitReason.STOP.value               # NU TARGET
    assert r.intrabar_ordering == "stop_at_entry_bar"
    assert r.exit_idx == 1 and r.exit_price == 99.0
    assert r.net_R is not None and r.net_R < 0                  # pierdere, NU câștig
    # contrast: un motor care sare bara de intrare (defectul) ar fi ajuns la ținta de la bara 2 → DIFERIT
    assert h[2] >= 104.0


def test_d1_entry_bar_stop_symmetric_short() -> None:
    o, h, l, c = _bars(7, hi=101.1)
    l[2] = 95.0; h[2] = 95.5                    # bara ei+1 ar atinge ținta jos dacă ar supraviețui
    sig = _sig(direction=-1, strategy_stop_price=101.0, target_price=96.0)   # short; exec_stop 101,0
    r = simulate_demo_trade(sig, o, h, l, c, TICK)
    assert r.floored is False and r.exit_reason == ExitReason.STOP.value
    assert r.intrabar_ordering == "stop_at_entry_bar" and r.exit_idx == 1 and r.exit_price == 101.0
    assert r.net_R is not None and r.net_R < 0


def test_d1_entry_bar_no_breach_proceeds_to_scan() -> None:
    """Fără breach pe bara de intrare → comportamentul normal de scanare (nefragmentat de D1)."""
    o, h, l, c = _bars(7)                       # low de bază 99,5 > exec_stop 98 → fără breach la intrare
    l[2] = 97.0                                 # stop pe bara ei+1
    r = simulate_demo_trade(_sig(), o, h, l, c, TICK)
    assert r.exit_reason == ExitReason.STOP.value and r.exit_idx == 2 and r.intrabar_ordering == "stop"


# ───────────────────────────── S2 — podea + sizing pe distanța corectată + spread observat ─────────────────────────────
def test_s2_floor_applied_sizing_on_floored_strategy_distance_retained() -> None:
    o, h, l, c = _bars(7, lo=99.7)            # low de bază 99.7 > exec_stop 99.5 (fără breach la intrare)
    h[2] = 105.0; l[2] = 99.6                 # bara 2 atinge ținta (fără stop)
    sig = _sig(strategy_stop_price=99.9, time_stop_idx=5)       # strategy dist = 0,1 (mic → podit)
    r = simulate_demo_trade(sig, o, h, l, c, TICK)
    assert r.floored is True
    assert abs(r.strategy_stop_distance - 0.1) < 1e-9          # PĂSTRAT, nu suprascris (~0,1)
    assert r.min_executable_risk == 0.5 and r.executable_stop_distance == 0.5
    assert r.exit_reason == ExitReason.TARGET.value and r.net_R is not None
    r_gated = r.net_R                                           # pe distanța PODITĂ (0,5) → 4/0,5 = 8
    r_naive = (1 * (104.0 - 100.0) - 0.0) / r.strategy_stop_distance   # fără podea: 4/0,1 ≈ 40
    assert abs(r_gated - 8.0) < 1e-9 and abs(r_naive - 40.0) < 1e-6
    assert abs(r_gated - r_naive) > 1.0


def test_s2_effective_spread_is_observed_not_modeled() -> None:
    o, h, l, c = _bars(7, lo=99.7); h[2] = 105.0; l[2] = 99.6
    r_low = simulate_demo_trade(_sig(effective_spread=0.1, strategy_stop_price=99.9), o, h, l, c, TICK)
    r_high = simulate_demo_trade(_sig(effective_spread=1.0, strategy_stop_price=99.9), o, h, l, c, TICK)
    assert r_low.min_executable_risk == max(2 * 0.1, 5 * TICK, 0.10 * 1.0) == 0.5
    assert r_high.min_executable_risk == max(2 * 1.0, 5 * TICK, 0.10 * 1.0) == 2.0
    assert r_low.min_executable_risk != r_high.min_executable_risk


# ───────────────────────────── S3 — țintă scanată strict de la entry_idx+1 ─────────────────────────────
def test_s3_entry_bar_target_touch_is_ignored() -> None:
    o, h, l, c = _bars(7)
    h[1] = 105.0                              # bara de INTRARE (ei=1) atinge ținta — trebuie IGNORATĂ
    l[2] = 97.0                               # bara ei+1 atinge stopul
    sig = _sig(time_stop_idx=5)
    r = simulate_demo_trade(sig, o, h, l, c, TICK)
    assert r.target_scan_start == 2                              # strict entry_idx+1
    assert r.exit_reason == ExitReason.STOP.value               # cu gardul: STOP (bara 1 ignorată)
    assert h[1] >= sig.target_price


def test_s3_prior_same_day_visit_before_entry_is_irrelevant() -> None:
    o, h, l, c = _bars(8)
    h[1] = 104.0                              # nivelul-țintă atins ÎNAINTE de intrare (bara 1 < entry)
    sig = _sig(entry_idx=3, time_stop_idx=6)  # intrare la bara 3; după intrare ținta NU se mai atinge
    r = simulate_demo_trade(sig, o, h, l, c, TICK)
    assert r.target_scan_start == 4                              # atingerea de la bara 1 e sub fereastră
    assert r.exit_reason == ExitReason.TIME_STOP.value          # ținta neatinsă după intrare → time-stop
    assert h[1] >= sig.target_price


# ───────────────────────────── D2 / R2 — time_stop_idx (înțeles unic) + precondiția F3 ─────────────────────────────
def test_audit_uses_time_stop_idx_single_meaning() -> None:
    o, h, l, c = _bars(7); h[2] = 105.0
    r = simulate_demo_trade(_sig(time_stop_idx=5), o, h, l, c, TICK)
    assert r.time_stop_idx == 5 and r.target_scan_end == 5      # UN singur câmp, un singur înțeles


def test_r2_f3_precondition_rejects_bad_bounds() -> None:
    o, h, l, c = _bars(5)
    with pytest.raises(ValueError, match="F3"):
        simulate_demo_trade(_sig(entry_idx=4, time_stop_idx=2), o, h, l, c, TICK)   # entry > time_stop
    with pytest.raises(ValueError, match="F3"):
        simulate_demo_trade(_sig(entry_idx=1, time_stop_idx=5), o, h, l, c, TICK)   # time_stop > n-1 (=4)


def test_entry_equals_time_stop_resolves_deterministically() -> None:
    """R1 clauza 3 (intrare/ieșire pe aceeași bară) e REZOLVABILĂ, nu INVALID: fără breach → TIME-STOP la close."""
    o, h, l, c = _bars(4); c[3] = 100.5
    r = simulate_demo_trade(_sig(entry_idx=3, time_stop_idx=3), o, h, l, c, TICK)
    assert r.exit_reason == ExitReason.TIME_STOP.value and r.exit_price == 100.5
    # cu breach pe aceeași bară → STOP (D1), tot rezolvabil (nu INVALID)
    o2, h2, l2, c2 = _bars(4); l2[3] = 97.0
    r2 = simulate_demo_trade(_sig(entry_idx=3, time_stop_idx=3), o2, h2, l2, c2, TICK)
    assert r2.exit_reason == ExitReason.STOP.value and r2.intrabar_ordering == "stop_at_entry_bar"


# ───────────────────────────── audit complet + INVALID îngust (3 condiții) + garda de intrare ─────────────────────────────
def test_all_audit_fields_emitted_per_trade() -> None:
    o, h, l, c = _bars(7); h[2] = 105.0
    r = simulate_demo_trade(_sig(), o, h, l, c, TICK)
    assert isinstance(r.intrabar_ordering, str) and r.intrabar_ordering            # S1
    for v in (r.strategy_stop_distance, r.min_executable_risk, r.executable_stop_distance):  # S2
        assert isinstance(v, float)
    assert isinstance(r.floored, bool)
    assert r.target_scan_start == r.entry_idx + 1 and r.target_scan_end == r.time_stop_idx    # S3
    assert r.exit_reason in {e.value for e in ExitReason}


def test_invalid_execution_condition1_floored_gap_at_entry() -> None:
    """Condiția (1): gap prin stopul PODIT la intrare, tranzacție PODITĂ → INVALID (îngust)."""
    o, h, l, c = _bars(7, lo=99.4)
    r = simulate_demo_trade(_sig(strategy_stop_price=99.95), o, h, l, c, TICK)   # dist 0,05 → podit; exec_stop 99,5
    assert r.floored is True and r.exit_reason == ExitReason.INVALID_EXECUTION.value
    assert r.intrabar_ordering == "gap_through_floored_stop_at_entry"


def test_same_entry_bar_breach_unfloored_is_STOP_not_invalid() -> None:
    """FIXTURE CORECTAT (RT-CODE-A-0005): aceeași atingere pe bara de intrare, dar NEPODIT → STOP cu REZULTAT
    verificat (pierdere), NU doar „nu e INVALID". Vechiul test verifica doar != INVALID și codifica eroarea D1."""
    o, h, l, c = _bars(7, lo=98.9); l[2] = 99.6; h[2] = 105.0
    r = simulate_demo_trade(_sig(strategy_stop_price=99.0), o, h, l, c, TICK)   # dist 1,0 → nepodit; exec_stop 99,0
    assert r.floored is False
    assert r.exit_reason == ExitReason.STOP.value               # REZULTAT, nu doar != INVALID
    assert r.exit_idx == 1 and r.exit_price == 99.0 and r.intrabar_ordering == "stop_at_entry_bar"
    assert r.net_R is not None and r.net_R < 0


def test_invalid_execution_condition2_zero_or_negative_risk() -> None:
    o, h, l, c = _bars(6)
    r = simulate_demo_trade(_sig(strategy_stop_price=100.0, atr=0.0, effective_spread=0.0), o, h, l, c, 0.0)
    assert r.executable_stop_distance == 0.0 and r.exit_reason == ExitReason.INVALID_EXECUTION.value
    assert r.intrabar_ordering == "zero_or_negative_risk"


def test_condition3_ambiguous_fill_subsumed_by_no_trade_guard() -> None:
    """Condiția (3) — intrare dincolo de stop (gap la deschidere): PRE-EMPTATĂ de garda structurală NO_TRADE
    (nepodit, exec = structural). Rezultat: exclusă (NO_TRADE), nu contorizată ca win/loss — echivalent cu INVALID."""
    o, h, l, c = _bars(6)
    r = simulate_demo_trade(_sig(strategy_stop_price=101.0), o, h, l, c, TICK)   # long, entry 100 <= stop 101
    assert r.traded is False and r.intrabar_ordering == "no_trade_entry_beyond_structural_stop"


def test_policy_entry_guards_no_trade() -> None:
    o, h, l, c = _bars(6)
    r_t = simulate_demo_trade(_sig(target_price=99.0), o, h, l, c, TICK)      # entry 100 >= țintă 99 (long)
    assert r_t.traded is False and r_t.intrabar_ordering == "no_trade_entry_beyond_target"
    r_s = simulate_demo_trade(_sig(strategy_stop_price=101.0), o, h, l, c, TICK)   # entry 100 <= stop 101 (long)
    assert r_s.traded is False and r_s.intrabar_ordering == "no_trade_entry_beyond_structural_stop"


def test_short_side_symmetry_stop_over_target() -> None:
    """S1 simetric pe short (PDH): bară care atinge stopul (sus) și ținta (jos) → STOP."""
    o, h, l, c = _bars(7)
    h[2] = 103.0; l[2] = 95.0                 # short: stop sus 102, țintă jos 96
    sig = _sig(direction=-1, strategy_stop_price=102.0, target_price=96.0, time_stop_idx=5)
    r = simulate_demo_trade(sig, o, h, l, c, TICK)
    assert r.exit_reason == ExitReason.STOP.value and r.intrabar_ordering == "stop_over_target"
    assert r.exit_price == 102.0 and r.net_R is not None and r.net_R < 0


def test_batch_runs_and_audits_all() -> None:
    o, h, l, c = _bars(7); h[2] = 105.0
    res = simulate_demo_trades([_sig(), _sig(direction=-1, strategy_stop_price=102.0, target_price=96.0)],
                               o, h, l, c, TICK)
    assert len(res) == 2 and all(r.intrabar_ordering for r in res)
