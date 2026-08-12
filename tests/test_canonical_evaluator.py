"""Teste pentru evaluatorul canonic unic — unul per regulă R1..R7, R11. ATENȚIE: acestea sunt testele MELE de
construcție; verdictul îl dau cele 17 teste canonice ale Red Team, NU acestea. Nu declar implementarea terminată
fiindcă trec astea.
"""

from __future__ import annotations

import os
import sys

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from canonical_evaluator import (  # noqa: E402
    BASE_PROVISIONAL, STRESS_PROVISIONAL, TICK_SIZE, ExecutedTrade, NoEntry, Rejection, Signal,
    evaluate_signal, evaluate_strategy, minimum_stop_distance,
)

Bars = tuple[list[float], list[float], list[float], list[float]]


def _sig(**kw: object) -> Signal:
    d: dict[str, object] = dict(strategy_id="S", signal_id="sig1", signal_bar=0, direction=1,
                                requested_stop_price=90.0, target_kind="none", target_param=None,
                                max_holding_bars=5, spread_price=0.05, atr=1.0, timestamp=1000)
    d.update(kw)
    return Signal(**d)  # type: ignore[arg-type]


def _flat(n: int, open_val: float = 100.0) -> Bars:
    o = [open_val] * n; h = [open_val + 0.2] * n; l = [open_val - 0.2] * n; c = [open_val] * n
    return o, h, l, c


# ── R1: tick_size sursă unică, increment de preț ──
def test_r1_tick_size_single_source() -> None:
    assert TICK_SIZE == 0.01                                    # increment de PREȚ (USD), nu costul unui tick


# ── R2: intrare la open[i+1] ──
def test_r2_entry_is_next_open() -> None:
    o, h, l, c = _flat(6)
    o[1] = 101.0                                                # open-ul barei de intrare (i+1)
    out = evaluate_signal(_sig(signal_bar=0, requested_stop_price=80.0), o, h, l, c)
    assert isinstance(out, ExecutedTrade) and out.entry_bar == 1 and out.entry_price == 101.0


def test_r2_no_next_open_is_no_entry() -> None:
    o, h, l, c = _flat(4)
    out = evaluate_signal(_sig(signal_bar=3), o, h, l, c)       # ultima bară → fără open[i+1]
    assert isinstance(out, NoEntry)


# ── R3: RESPINGERE (nu extindere), cu componenta dominantă ──
def test_r3_reject_when_below_minimum_no_widening() -> None:
    o, h, l, c = _flat(6)
    # stop cerut la 99,9 (distanță 0,1) sub podeaua dominată de 0,10×ATR=0,50 (ATR=5)
    out = evaluate_signal(_sig(requested_stop_price=99.9, spread_price=0.001, atr=5.0), o, h, l, c)
    assert isinstance(out, Rejection) and out.reason_code == "STOP_BELOW_MINIMUM"
    assert out.dominant_component == "0.10x_atr" and abs(out.minimum_stop_distance - 0.5) < 1e-9
    assert abs(out.requested_stop_distance - 0.1) < 1e-9        # distanța CERUTĂ, neextinsă


def test_r3_dominant_components() -> None:
    assert minimum_stop_distance(1.0, 1.0).dominant_component == "2x_spread"      # 2,0
    assert minimum_stop_distance(0.001, 0.1).dominant_component == "floor_0.05usd"  # 0,05
    assert minimum_stop_distance(0.001, 5.0).dominant_component == "0.10x_atr"    # 0,50


def test_r3_rejection_has_no_pnl_stays_in_signals() -> None:
    o, h, l, c = _flat(6)
    out = evaluate_signal(_sig(requested_stop_price=99.99, spread_price=0.001, atr=5.0), o, h, l, c)
    assert isinstance(out, Rejection)
    assert not hasattr(out, "results") and not hasattr(out, "net_R")   # fără P&L fictiv


# ── R4: cost = spread + entry_slip + exit_slip, în AMBELE scenarii ──
def test_r4_cost_formula_not_doubled() -> None:
    assert abs(BASE_PROVISIONAL.total_cost_price - 0.05) < 1e-9
    assert abs(STRESS_PROVISIONAL.total_cost_price - 0.24) < 1e-9   # 0,08+0,08+0,08, NU 2×spread
    assert BASE_PROVISIONAL.calibrated is False and STRESS_PROVISIONAL.calibrated is False   # PROVISIONAL


def test_r4_both_scenarios_reported() -> None:
    o, h, l, c = _flat(6); o[1] = 100.0
    out = evaluate_signal(_sig(requested_stop_price=90.0, max_holding_bars=3), o, h, l, c)
    assert isinstance(out, ExecutedTrade)
    names = {r.scenario for r in out.results}
    assert names == {"BASE_PROVISIONAL", "STRESS_PROVISIONAL"}
    base = next(r for r in out.results if r.scenario == "BASE_PROVISIONAL")
    stress = next(r for r in out.results if r.scenario == "STRESS_PROVISIONAL")
    assert stress.net_R < base.net_R                           # cost STRESS mai mare ⇒ R mai mic


# ── R5: SL PRIMEAZĂ, inclusiv pe bara de intrare; costurile indiferent de motiv ──
def test_r5_sl_primes_on_same_bar_collision() -> None:
    # long entry 100, stop 99, target 102; bara de intrare atinge AMBELE (low 98, high 103) → SL câștigă = pierdere
    o = [100.0, 100.0, 100.0, 100.0]; h = [100.2, 103.0, 100.2, 100.2]
    l = [99.8, 98.0, 99.8, 99.8]; c = [100.0, 100.0, 100.0, 100.0]
    out = evaluate_signal(_sig(signal_bar=0, requested_stop_price=99.0, target_kind="price", target_param=102.0),
                          o, h, l, c)
    assert isinstance(out, ExecutedTrade)
    assert out.exit_reason == "stop" and out.exit_bar == 1 and out.exit_price == 99.0   # SL, nu TP
    assert all(r.net_R < 0 for r in out.results)              # pierdere (defectul D1: era raportat câștig)


def test_r5_cost_applied_on_time_exit_too() -> None:
    o, h, l, c = _flat(6); o[1] = 100.0                        # fără atingere → time-exit, dar costul se aplică
    out = evaluate_signal(_sig(requested_stop_price=90.0, max_holding_bars=3), o, h, l, c)
    assert isinstance(out, ExecutedTrade) and out.exit_reason == "time"
    base = next(r for r in out.results if r.scenario == "BASE_PROVISIONAL")
    assert base.total_cost_price == 0.05 and base.net_R < 0    # gross~0, minus cost ⇒ negativ


# ── R6: max_holding inclusiv, bara de intrare = bara 1 ──
def test_r6_holding_inclusive_entry_is_bar_1() -> None:
    o, h, l, c = _flat(20); o[1] = 100.0
    out = evaluate_signal(_sig(requested_stop_price=80.0, max_holding_bars=10), o, h, l, c)   # bare 1..10
    assert isinstance(out, ExecutedTrade)
    assert out.exit_reason == "time" and out.exit_bar == 1 + 10 - 1                # time-exit la close-ul barei 10
    out1 = evaluate_signal(_sig(requested_stop_price=80.0, max_holding_bars=1), o, h, l, c)   # DOAR bara de intrare
    assert isinstance(out1, ExecutedTrade) and out1.exit_bar == 1                  # ei = bara 1


# ── R7: still-open la granița blocului, raportat SEPARAT, NU time-exit ──
def test_r7_boundary_is_still_open_not_time_exit() -> None:
    o, h, l, c = _flat(20); o[1] = 100.0
    # holding 10 dar blocul se termină la bara 5 → rămasă deschisă, NU time-exit la graniță
    out = evaluate_signal(_sig(requested_stop_price=80.0, max_holding_bars=10), o, h, l, c, block_end=5)
    assert isinstance(out, ExecutedTrade)
    assert out.still_open_at_end is True and out.exit_reason == "still_open_at_end" and out.exit_bar == 5


# ── R11: config_id imuabil; scenarii diferite ⇒ config diferit ──
def test_r11_config_id_and_comparability() -> None:
    o, h, l, c = _flat(6); o[1] = 100.0
    a = evaluate_signal(_sig(requested_stop_price=80.0), o, h, l, c)
    b = evaluate_signal(_sig(requested_stop_price=80.0), o, h, l, c)
    assert isinstance(a, ExecutedTrade) and isinstance(b, ExecutedTrade)
    assert a.config_id == b.config_id and len(a.config_id) == 16   # deterministic, comparabile
    diff = evaluate_signal(_sig(requested_stop_price=80.0), o, h, l, c, scenarios=(BASE_PROVISIONAL,))
    assert isinstance(diff, ExecutedTrade) and diff.config_id != a.config_id   # altă config ⇒ NON-COMPARABLE


# ── raportarea per strategie: câmpuri obligatorii ──
def test_strategy_report_mandatory_fields() -> None:
    o, h, l, c = _flat(30)
    for i in range(1, 30):
        o[i] = 100.0
    sigs = [
        _sig(signal_id="ok1", signal_bar=0, requested_stop_price=80.0, max_holding_bars=3),      # executabil
        _sig(signal_id="ok2", signal_bar=5, requested_stop_price=80.0, max_holding_bars=3),      # executabil
        _sig(signal_id="rej", signal_bar=10, requested_stop_price=99.99, spread_price=0.001, atr=5.0),  # respins
        _sig(signal_id="open", signal_bar=20, requested_stop_price=80.0, max_holding_bars=10),   # still-open (block_end)
    ]
    rep, outs = evaluate_strategy("S", sigs, o, h, l, c, block_end=22)
    assert rep.total_signals == 4 and rep.rejected == 1 and rep.no_entry == 0
    assert rep.still_open_at_end == 1 and rep.eligible_trades == 2
    assert abs(rep.rejected_pct - 25.0) < 1e-9
    assert dict(rep.rejection_reasons) == {"STOP_BELOW_MINIMUM": 1}
    assert rep.base_mean_R is not None and rep.stress_mean_R is not None
    assert rep.base_minus_stress is not None and rep.base_minus_stress > 0   # BASE > STRESS
