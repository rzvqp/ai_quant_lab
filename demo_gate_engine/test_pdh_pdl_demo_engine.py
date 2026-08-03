"""Teste pentru motorul DEMO PDH-PDL — un test per gard care PICĂ fără el și TRECE cu el.

„Pică fără el" = arătat prin contrast: valoarea naivă (ne-gardată) diferă de rezultatul gardat al motorului.
Date sintetice; fără MT5, fără date reale. Motorul e pur.
"""

from __future__ import annotations

import os
import sys

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
                atr=1.0, effective_spread=0.1, cost=0.0, day_end_idx=5)
    base.update(kw)
    return DemoSignal(entry_idx=int(base["entry_idx"]), direction=int(base["direction"]),
                      strategy_stop_price=base["strategy_stop_price"], target_price=base["target_price"],
                      atr=base["atr"], effective_spread=base["effective_spread"], cost=base["cost"],
                      day_end_idx=int(base["day_end_idx"]))


# ───────────────────────────── S1 — ierarhie STOP > TIME-STOP > TARGET ─────────────────────────────
def test_s1_stop_and_target_same_bar_resolves_STOP() -> None:
    """CERINȚA CENTRALĂ: o bară care atinge ȘI stopul ȘI ținta trebuie să rezolve STOP (pierdere), nu ținta."""
    o, h, l, c = _bars(7)
    l[2] = 97.0; h[2] = 105.0                 # bara ei+1 atinge AMBELE (stop 98, țintă 104)
    sig = _sig(day_end_idx=5)                 # bara 2 NU e graniță (izolează stop∧țintă)
    r = simulate_demo_trade(sig, o, h, l, c, TICK)
    # cu gardul: STOP
    assert r.exit_reason == ExitReason.STOP.value
    assert r.intrabar_ordering == "stop_over_target"
    assert r.exit_price == 98.0 and r.net_R is not None and r.net_R < 0     # pierdere
    # fără gardul (naiv target-first): aceeași bară ar fi dat ȚINTĂ (câștig) — ambele condiții sunt adevărate
    hitS = l[2] <= r.executable_stop_price
    hitT = h[2] >= sig.target_price
    assert hitS and hitT                       # deci un motor target-first ar fi ales ținta → rezultat DIFERIT


def test_s1_target_and_timestop_on_boundary_resolves_TIME_STOP() -> None:
    o, h, l, c = _bars(5)
    h[3] = 105.0; l[3] = 99.0; c[3] = 101.0   # bara-graniță atinge ținta dar NU stopul
    sig = _sig(day_end_idx=3)
    r = simulate_demo_trade(sig, o, h, l, c, TICK)
    assert r.exit_reason == ExitReason.TIME_STOP.value          # cu gardul: TIME-STOP la close
    assert r.intrabar_ordering == "time_stop_over_target"
    assert r.exit_price == 101.0                                # close-ul zilei, NU ținta 104
    assert h[3] >= sig.target_price                             # naiv target-first ar fi dat ținta → DIFERIT


def test_s1_stop_and_timestop_on_boundary_resolves_STOP() -> None:
    o, h, l, c = _bars(5)
    l[3] = 97.0; c[3] = 100.0                 # bara-graniță atinge stopul
    sig = _sig(day_end_idx=3)
    r = simulate_demo_trade(sig, o, h, l, c, TICK)
    assert r.exit_reason == ExitReason.STOP.value               # STOP primează peste TIME-STOP
    assert r.intrabar_ordering == "stop_over_time_stop"
    assert r.exit_price == 98.0                                 # naiv time-stop-first ar fi ieșit la close → DIFERIT


# ───────────────────────────── S2 — podea + sizing pe distanța corectată + spread observat ─────────────────────────────
def test_s2_floor_applied_sizing_on_floored_strategy_distance_retained() -> None:
    o, h, l, c = _bars(7, lo=99.7)            # low de bază 99.7 > exec_stop 99.5 (fără breach la intrare)
    h[2] = 105.0; l[2] = 99.6                 # bara 2 atinge ținta (fără stop)
    sig = _sig(strategy_stop_price=99.9, day_end_idx=5)         # strategy dist = 0,1 (mic → podit)
    r = simulate_demo_trade(sig, o, h, l, c, TICK)
    assert r.floored is True
    assert abs(r.strategy_stop_distance - 0.1) < 1e-9          # PĂSTRAT, nu suprascris (~0,1)
    assert r.min_executable_risk == 0.5 and r.executable_stop_distance == 0.5
    assert r.exit_reason == ExitReason.TARGET.value and r.net_R is not None
    r_gated = r.net_R                                           # pe distanța PODITĂ (0,5) → 4/0,5 = 8
    r_naive = (1 * (104.0 - 100.0) - 0.0) / r.strategy_stop_distance   # fără podea: 4/0,1 ≈ 40 (poziție nemărginită)
    assert abs(r_gated - 8.0) < 1e-9 and abs(r_naive - 40.0) < 1e-6
    assert abs(r_gated - r_naive) > 1.0                        # sizing-ul nepodit dă un R total mult diferit


def test_s2_effective_spread_is_observed_not_modeled() -> None:
    o, h, l, c = _bars(7, lo=99.7); h[2] = 105.0; l[2] = 99.6
    r_low = simulate_demo_trade(_sig(effective_spread=0.1, strategy_stop_price=99.9), o, h, l, c, TICK)
    r_high = simulate_demo_trade(_sig(effective_spread=1.0, strategy_stop_price=99.9), o, h, l, c, TICK)
    assert r_low.min_executable_risk == max(2 * 0.1, 5 * TICK, 0.10 * 1.0) == 0.5
    assert r_high.min_executable_risk == max(2 * 1.0, 5 * TICK, 0.10 * 1.0) == 2.0
    assert r_low.min_executable_risk != r_high.min_executable_risk          # depinde de spreadul OBSERVAT, nu constant


# ───────────────────────────── S3 — țintă scanată strict de la entry_idx+1 ─────────────────────────────
def test_s3_entry_bar_target_touch_is_ignored() -> None:
    o, h, l, c = _bars(7)
    h[1] = 105.0                              # bara de INTRARE (ei=1) atinge ținta — trebuie IGNORATĂ
    l[2] = 97.0                               # bara ei+1 atinge stopul
    sig = _sig(day_end_idx=5)
    r = simulate_demo_trade(sig, o, h, l, c, TICK)
    assert r.target_scan_start == 2                              # strict entry_idx+1
    assert r.exit_reason == ExitReason.STOP.value               # cu gardul: STOP (bara 1 ignorată)
    assert h[1] >= sig.target_price                             # naiv-de-la-ei ar fi dat ținta la bara 1 → DIFERIT


def test_s3_prior_same_day_visit_before_entry_is_irrelevant() -> None:
    o, h, l, c = _bars(8)
    h[1] = 104.0                              # nivelul-țintă atins ÎNAINTE de intrare (bara 1 < entry)
    sig = _sig(entry_idx=3, day_end_idx=6)    # intrare la bara 3; după intrare ținta NU se mai atinge
    r = simulate_demo_trade(sig, o, h, l, c, TICK)
    assert r.target_scan_start == 4                              # atingerea de la bara 1 e sub fereastră
    assert r.exit_reason == ExitReason.TIME_STOP.value          # ținta neatinsă după intrare → time-stop
    assert h[1] >= sig.target_price                             # o citire pe toată ziua ar fi zis „țintă atinsă" → DIFERIT


# ───────────────────────────── audit complet + INVALID îngust + garda de intrare ─────────────────────────────
def test_all_audit_fields_emitted_per_trade() -> None:
    o, h, l, c = _bars(7); h[2] = 105.0
    r = simulate_demo_trade(_sig(), o, h, l, c, TICK)
    assert isinstance(r.intrabar_ordering, str) and r.intrabar_ordering            # S1
    for v in (r.strategy_stop_distance, r.min_executable_risk, r.executable_stop_distance):  # S2
        assert isinstance(v, float)
    assert isinstance(r.floored, bool)
    assert r.target_scan_start == r.entry_idx + 1 and r.target_scan_end == r.day_end_idx      # S3
    assert r.exit_reason in {e.value for e in ExitReason}


def test_invalid_execution_is_narrow_floored_only() -> None:
    # (a) gap prin stopul PODIT la intrare, tranzacție PODITĂ → INVALID
    o, h, l, c = _bars(7, lo=99.4)
    r_floored = simulate_demo_trade(_sig(strategy_stop_price=99.95), o, h, l, c, TICK)   # dist 0,05 → podit; exec_stop 99,5; low 99,4 breach
    assert r_floored.floored is True and r_floored.exit_reason == ExitReason.INVALID_EXECUTION.value
    assert r_floored.intrabar_ordering == "gap_through_floored_stop_at_entry"
    # (b) aceeași atingere pe bara de intrare, dar NEPODIT → NU e INVALID (scop îngust)
    o2, h2, l2, c2 = _bars(7, lo=98.9); l2[2] = 99.6; h2[2] = 105.0
    r_unfloored = simulate_demo_trade(_sig(strategy_stop_price=99.0), o2, h2, l2, c2, TICK)  # dist 1,0 → nepodit; exec_stop 99,0; low intrare 98,9 breach
    assert r_unfloored.floored is False and r_unfloored.exit_reason != ExitReason.INVALID_EXECUTION.value


def test_invalid_execution_zero_or_negative_risk() -> None:
    o, h, l, c = _bars(5)
    r = simulate_demo_trade(_sig(strategy_stop_price=100.0, atr=0.0, effective_spread=0.0), o, h, l, c, 0.0)
    assert r.executable_stop_distance == 0.0 and r.exit_reason == ExitReason.INVALID_EXECUTION.value
    assert r.intrabar_ordering == "zero_or_negative_risk"


def test_policy_entry_guards_no_trade() -> None:
    o, h, l, c = _bars(5)
    r_t = simulate_demo_trade(_sig(target_price=99.0), o, h, l, c, TICK)      # entry 100 >= țintă 99 (long)
    assert r_t.traded is False and r_t.intrabar_ordering == "no_trade_entry_beyond_target"
    r_s = simulate_demo_trade(_sig(strategy_stop_price=101.0), o, h, l, c, TICK)   # entry 100 <= stop 101 (long)
    assert r_s.traded is False and r_s.intrabar_ordering == "no_trade_entry_beyond_structural_stop"


def test_short_side_symmetry_stop_over_target() -> None:
    """S1 simetric pe short (PDH): bară care atinge stopul (sus) și ținta (jos) → STOP."""
    o, h, l, c = _bars(7)
    h[2] = 103.0; l[2] = 95.0                 # short: stop sus 102, țintă jos 96
    sig = _sig(direction=-1, strategy_stop_price=102.0, target_price=96.0, day_end_idx=5)
    r = simulate_demo_trade(sig, o, h, l, c, TICK)
    assert r.exit_reason == ExitReason.STOP.value and r.intrabar_ordering == "stop_over_target"
    assert r.exit_price == 102.0 and r.net_R is not None and r.net_R < 0


def test_batch_runs_and_audits_all() -> None:
    o, h, l, c = _bars(7); h[2] = 105.0
    res = simulate_demo_trades([_sig(), _sig(direction=-1, strategy_stop_price=102.0, target_price=96.0)],
                               o, h, l, c, TICK)
    assert len(res) == 2 and all(r.intrabar_ordering for r in res)
