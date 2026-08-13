"""Teste de construcție pentru evaluatorul canonic (v2.7.66). ATENȚIE: verdictul îl dau cele 18 teste canonice ale
Red Team, NU acestea. Nu declar terminat fiindcă trec astea.
"""

from __future__ import annotations

import os
import sys

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from level_output import Ok, Unavailable  # noqa: E402
from canonical_evaluator import (  # noqa: E402
    BASE_PROVISIONAL, STRESS_PROVISIONAL, ExecutedTrade, InvalidExecution, NoEntry, Rejection, Signal, SpreadFull,
    half_of, evaluate_signal, evaluate_strategy, minimum_stop_distance,
)

Bars = tuple[list[float], list[float], list[float], list[float]]


def _sig(**kw: object) -> Signal:
    d: dict[str, object] = dict(strategy_id="S", signal_id="sig1", signal_bar=0, direction=1,
                                requested_stop_price=90.0, target_kind="none", target_param=None,
                                max_holding_bars=5, spread_price=SpreadFull(0.05), atr=1.0, timestamp=1000)
    d.update(kw)
    return Signal(**d)  # type: ignore[arg-type]


def _flat(n: int, v: float = 100.0) -> Bars:
    return [v] * n, [v + 0.2] * n, [v - 0.2] * n, [v] * n


# ── R1/§1 unități: spread FULL, podeaua ia jumătatea; 2×half = full ──
def test_r1_units_spread_half_cancels_conversion() -> None:
    ms = minimum_stop_distance(half_of(SpreadFull(0.05)), 0.1)   # 2×(0.05/2)=0.05 ; 0.10×0.1=0.01 ; tick 0.05
    assert abs(ms.minimum_stop_distance - 0.05) < 1e-9
    big = minimum_stop_distance(half_of(SpreadFull(1.0)), 1.0)   # 2×0.5=1.0 domină
    assert big.dominant_component == "spread" and abs(big.minimum_stop_distance - 1.0) < 1e-9


# ── R2 ──
def test_r2_entry_next_open() -> None:
    o, h, l, c = _flat(6); o[1] = 101.0
    out = evaluate_signal(_sig(signal_bar=0, requested_stop_price=80.0), o, h, l, c)
    assert isinstance(out, ExecutedTrade) and out.entry_bar == 1 and out.entry_price == 101.0


def test_r2_no_next_open_is_no_entry() -> None:
    o, h, l, c = _flat(4)
    assert isinstance(evaluate_signal(_sig(signal_bar=3), o, h, l, c), NoEntry)


# ── R3 REJECT-NOT-WIDEN ──
def test_r3_reject_below_minimum_no_widening() -> None:
    o, h, l, c = _flat(6)
    out = evaluate_signal(_sig(requested_stop_price=99.9, spread_price=SpreadFull(0.001), atr=5.0), o, h, l, c)
    assert isinstance(out, Rejection) and out.reason_code == "STOP_BELOW_MINIMUM"
    assert out.dominant_component == "atr" and abs(out.minimum_stop_distance - 0.5) < 1e-9
    assert abs(out.requested_stop_distance - 0.1) < 1e-9


# ── §5(a) MEAS-9: risc ≤ 0 (gap PRIN stop) → INVALID_EXECUTION (numărat, niciodată câștig) ──
def test_meas9_gap_through_stop_is_invalid_execution() -> None:
    o, h, l, c = _flat(6); o[1] = 100.0
    out = evaluate_signal(_sig(signal_bar=0, requested_stop_price=101.0), o, h, l, c)   # stop 101 PESTE intrarea 100
    assert isinstance(out, InvalidExecution) and out.reason_code == "INVALID_EXECUTION"
    assert out.directional_risk <= 0.0 and not hasattr(out, "results")   # niciun R, niciun câștig fictiv


# ── A2 GEOMETRIE STRICTĂ: recompensă ≤ 0 (gap/open pe țintă) → INVALID_EXECUTION (nu ieșire-la-intrare) ──
def test_a2_gap_through_target_is_invalid() -> None:
    o, h, l, c = _flat(6); o[1] = 100.0
    out = evaluate_signal(_sig(signal_bar=0, requested_stop_price=90.0, target_kind="price", target_param=99.5),
                          o, h, l, c)   # target 99,5 SUB intrarea 100 (long) → recompensă < 0
    assert isinstance(out, InvalidExecution) and out.violation == "reward_nonpositive"
    assert out.directional_reward is not None and out.directional_reward <= 0.0 and not hasattr(out, "results")


def test_a2_open_exactly_on_stop_is_invalid() -> None:
    o, h, l, c = _flat(6); o[1] = 100.0
    out = evaluate_signal(_sig(signal_bar=0, requested_stop_price=100.0), o, h, l, c)   # open EXACT pe stop
    assert isinstance(out, InvalidExecution) and out.violation == "risk_nonpositive"


# ── R4 ──
def test_r4_cost_spread_once() -> None:
    assert abs(BASE_PROVISIONAL.total_cost_price - 0.05) < 1e-9
    assert abs(STRESS_PROVISIONAL.total_cost_price - 0.24) < 1e-9


# ── R5 SL primează pe bara de intrare ──
def test_r5_sl_primes_same_bar() -> None:
    o = [100.0, 100.0, 100.0, 100.0]; h = [100.2, 103.0, 100.2, 100.2]
    l = [99.8, 98.0, 99.8, 99.8]; c = [100.0]*4
    out = evaluate_signal(_sig(signal_bar=0, requested_stop_price=99.0, target_kind="price", target_param=102.0),
                          o, h, l, c)
    assert isinstance(out, ExecutedTrade) and out.exit_reason == "stop" and all(r.net_R < 0 for r in out.results)


# ── R6 inclusiv ──
def test_r6_holding_inclusive() -> None:
    o, h, l, c = _flat(20); o[1] = 100.0
    out = evaluate_signal(_sig(requested_stop_price=80.0, max_holding_bars=10), o, h, l, c)
    assert isinstance(out, ExecutedTrade) and out.exit_reason == "time" and out.exit_bar == 1 + 10 - 1


# ── R7 still-open ──
def test_r7_boundary_still_open() -> None:
    o, h, l, c = _flat(20); o[1] = 100.0
    out = evaluate_signal(_sig(requested_stop_price=80.0, max_holding_bars=10), o, h, l, c, block_end=5)
    assert isinstance(out, ExecutedTrade) and out.still_open_at_end and out.exit_reason == "still_open_at_end"


# ── R11 run_hash + compare RIDICĂ ──
def test_r11_run_hash_and_compare_raises() -> None:
    from canonical_evaluator import RunContext, compare, NonComparableError
    import pytest
    o, h, l, c = _flat(6); o[1] = 100.0
    xau = evaluate_signal(_sig(requested_stop_price=80.0), o, h, l, c, run=RunContext("XAUUSD", "M15", "v2"))
    es = evaluate_signal(_sig(requested_stop_price=80.0), o, h, l, c, run=RunContext("ES", "M15", "v2"))
    assert isinstance(xau, ExecutedTrade) and isinstance(es, ExecutedTrade)
    assert xau.run_hash != es.run_hash                        # instrumente diferite ⇒ id-uri diferite
    compare(xau.run_hash, xau.run_hash)                       # identic → OK
    with pytest.raises(NonComparableError):
        compare(xau.run_hash, es.run_hash)                    # diferit → RIDICĂ


# ── §7 MEAS-10: câmpurile de concentrare pe raportul CANONIC + numărarea INVALID ──
def test_meas10_report_carries_concentration_and_invalid_count() -> None:
    o, h, l, c = _flat(30)
    sigs = [_sig(signal_id=f"ok{i}", signal_bar=i, requested_stop_price=80.0, max_holding_bars=3) for i in range(0, 10)]
    sigs.append(_sig(signal_id="inv", signal_bar=15, requested_stop_price=101.0))   # gap prin stop → INVALID
    rep, _ = evaluate_strategy("S", sigs, o, h, l, c)
    assert rep.invalid_executions == 1                        # numărat, exclus din randamente
    assert rep.base_concentration is not None and rep.stress_concentration is not None
    bc = rep.base_concentration
    assert isinstance(bc.best_trade_share, (Ok, Unavailable))  # LevelOutput (Unavailable dacă sum_R ≤ 0)
    assert bc.n_trimmed >= 1 and 0.0 <= bc.trimmed_fraction <= 1.0
