"""Teste pentru extensia de EXIT DINAMIC (prima expansiune opusă). Contrast fără/cu gard, date sintetice.

Include corecțiile RT-CODE-A-0005: D1 (S1 pe bara de intrare), podeaua S2, INVALID, precondiția F3 (R2).
"""

from __future__ import annotations

import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from pdh_pdl_demo_engine import DemoSignal, ExitReason  # noqa: E402
from dynamic_exit_engine import simulate_demo_trade_dynamic  # noqa: E402

TICK = 0.1


def _bars(n: int, lo: float = 99.5) -> tuple[list[float], list[float], list[float], list[float]]:
    return [100.0] * n, [100.5] * n, [lo] * n, [100.0] * n


def _sig(**kw: float) -> DemoSignal:
    b = dict(entry_idx=1, direction=1, strategy_stop_price=98.0, target_price=float("nan"),
             atr=1.0, effective_spread=0.1, cost=0.0, time_stop_idx=6)
    b.update(kw)
    return DemoSignal(entry_idx=int(b["entry_idx"]), direction=int(b["direction"]),
                      strategy_stop_price=b["strategy_stop_price"], target_price=b["target_price"],
                      atr=b["atr"], effective_spread=b["effective_spread"], cost=b["cost"],
                      time_stop_idx=int(b["time_stop_idx"]))


def test_opposing_expansion_exit_at_next_open() -> None:
    o, h, l, c = _bars(8)
    ed = [0] * 8; ed[3] = -1                    # expansiune OPUSĂ (bearish) la bara 3, pt. un long
    o[4] = 101.0                                # open-ul barei următoare = prețul de ieșire
    r = simulate_demo_trade_dynamic(_sig(time_stop_idx=6), o, h, l, c, ed, TICK)
    assert r.exit_reason == ExitReason.TARGET.value and r.intrabar_ordering == "opposing_expansion"
    assert r.exit_idx == 4 and r.exit_price == 101.0
    assert ed[3] == -1                          # fără regula de exit, poziția ar fi ținut la termen → DIFERIT


def test_stop_wins_over_opposing_same_bar() -> None:
    o, h, l, c = _bars(8)
    l[3] = 97.0                                 # bara 3 atinge stopul (98)
    ed = [0] * 8; ed[3] = -1                    # ȘI e expansiune opusă
    r = simulate_demo_trade_dynamic(_sig(time_stop_idx=6), o, h, l, c, ed, TICK)
    assert r.exit_reason == ExitReason.STOP.value and r.intrabar_ordering == "stop_over_opposing"
    assert r.exit_price == 98.0                 # STOP primează peste exitul de expansiune opusă


def test_block_boundary_time_stop_when_no_opposing() -> None:
    o, h, l, c = _bars(6); c[5] = 100.5
    ed = [0] * 6                                # nicio expansiune opusă
    r = simulate_demo_trade_dynamic(_sig(time_stop_idx=5), o, h, l, c, ed, TICK)
    assert r.exit_reason == ExitReason.TIME_STOP.value and r.exit_price == 100.5   # close-ul termenului-limită


# ───────────────────────────── RT-CODE-A-0005 — D1 / podea / INVALID / F3 ─────────────────────────────
def test_d1_entry_bar_stop_unfloored_dynamic() -> None:
    """D1: stop nepodit atins pe bara de INTRARE → STOP (nu sărit spre exitul dinamic ulterior)."""
    o, h, l, c = _bars(8, lo=98.9)
    ed = [0] * 8; ed[3] = -1                    # ar exista un exit de expansiune mai târziu — irelevant, stopul e ACUM
    r = simulate_demo_trade_dynamic(_sig(strategy_stop_price=99.0), o, h, l, c, ed, TICK)  # exec_stop 99,0
    assert r.floored is False and r.exit_reason == ExitReason.STOP.value
    assert r.intrabar_ordering == "stop_at_entry_bar" and r.exit_idx == 1 and r.exit_price == 99.0
    assert r.net_R is not None and r.net_R < 0


def test_dynamic_floor_and_invalid_gap_at_entry() -> None:
    """Podea S2 + condiția (1): gap prin stopul PODIT la intrare → INVALID (podit)."""
    o, h, l, c = _bars(8, lo=99.4)
    ed = [0] * 8
    r = simulate_demo_trade_dynamic(_sig(strategy_stop_price=99.95), o, h, l, c, ed, TICK)  # dist 0,05 → podit
    assert r.floored is True and r.exit_reason == ExitReason.INVALID_EXECUTION.value
    assert r.intrabar_ordering == "gap_through_floored_stop_at_entry"


def test_dynamic_zero_risk_invalid() -> None:
    o, h, l, c = _bars(6)
    ed = [0] * 6
    r = simulate_demo_trade_dynamic(_sig(strategy_stop_price=100.0, atr=0.0, effective_spread=0.0, time_stop_idx=5),
                                    o, h, l, c, ed, 0.0)
    assert r.executable_stop_distance == 0.0 and r.exit_reason == ExitReason.INVALID_EXECUTION.value
    assert r.intrabar_ordering == "zero_or_negative_risk"


def test_dynamic_r2_f3_precondition() -> None:
    o, h, l, c = _bars(6); ed = [0] * 6
    with pytest.raises(ValueError, match="F3"):
        simulate_demo_trade_dynamic(_sig(entry_idx=1, time_stop_idx=6), o, h, l, c, ed, TICK)  # time_stop > n-1
