"""Teste sintetice pentru PIESA 3 (partial_exit.py) — mecanica 75/25 cu breakeven. Array-uri în memorie."""

import os
import sys

import pytest

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from partial_exit import simulate_partial_exit  # noqa: E402

# Long: entry=100, sl=99 (R=1$), tp1=102 (+2R), tp2=103 (+3R). Bare mari pt. control precis.
ENTRY, SL, TP1, TP2, DIR = 100.0, 99.0, 102.0, 103.0, +1
COST = 0.20


def _series(n=30):
    return ([100.0] * n, [100.5] * n, [99.5] * n, [100.0] * n)   # o,h,l,c neutre (nu ating nimic)


def test_stopped_full_before_tp1():
    o, h, l, c = _series()
    l[3] = 98.5                                  # stop 99 atins @3, înainte de TP1
    r = simulate_partial_exit(0, DIR, ENTRY, SL, TP1, TP2, h, l, c, 20, 29, COST)
    assert r.exit_reason == "stopped_full"
    assert r.R_leg1 == -1.0 and r.R_leg2 == -1.0
    assert abs(r.net_R - (-1.0 - COST / 1.0)) < 1e-9          # −1 − cost/R


def test_tp1_then_tp2():
    o, h, l, c = _series()
    for j in range(4, 9):                        # după TP1, prețul stă DEASUPRA breakeven (100) → runnerul ține
        o[j] = h[j] = l[j] = c[j] = 101.5
    h[4], l[4] = 102.5, 101.0                    # TP1 (102) @4, low>breakeven
    for j in range(5, 8):
        h[j] = 102.0                             # sub TP2 (103)
    h[8], l[8] = 103.5, 101.0                    # TP2 (103) @8
    r = simulate_partial_exit(0, DIR, ENTRY, SL, TP1, TP2, h, l, c, 20, 29, COST)
    assert r.exit_reason == "tp1_then_tp2"
    assert r.R_leg1 == 2.0 and r.R_leg2 == 3.0
    assert abs(r.net_R - (0.75 * 2.0 + 0.25 * 3.0 - COST)) < 1e-9   # cost/R=0.20 (R=1)


def test_tp1_then_breakeven():
    o, h, l, c = _series()
    h[4] = 102.5                                 # TP1 @4 → stop la breakeven (100)
    l[9] = 99.8                                  # revine la 100 (breakeven) @9, TP2 neatins
    r = simulate_partial_exit(0, DIR, ENTRY, SL, TP1, TP2, h, l, c, 20, 29, COST)
    assert r.exit_reason == "tp1_then_breakeven"
    assert r.R_leg1 == 2.0 and r.R_leg2 == 0.0   # leg2 la intrare EXACT = 0R
    assert abs(r.net_R - (0.75 * 2.0 + 0.25 * 0.0 - COST)) < 1e-9


def test_timeout_no_tp1_uses_min_horizon_or_eod():
    o, h, l, c = _series()
    c[10] = 101.0                                # închidere pe timp
    # day_end=10 vine ÎNAINTEA horizon=20 → exit la min(0+20,10)=10 (orizont VARIABIL)
    r = simulate_partial_exit(0, DIR, ENTRY, SL, TP1, TP2, h, l, c, 20, 10, COST)
    assert r.exit_reason == "timeout_no_tp1"
    assert r.leg1_exit_idx == 10 and r.leg2_exit_idx == 10
    assert abs(r.R_leg1 - 1.0) < 1e-9 and abs(r.net_R - (1.0 - COST)) < 1e-9


def test_ambiguous_bar_stop_wins_by_default_QA():
    o, h, l, c = _series()
    h[3], l[3] = 102.5, 98.5                     # TP1 ȘI stop pe aceeași bară @3
    r_def = simulate_partial_exit(0, DIR, ENTRY, SL, TP1, TP2, h, l, c, 20, 29, COST)
    assert r_def.exit_reason == "stopped_full"   # default stop_before_target=True → stopul câștigă
    r_alt = simulate_partial_exit(0, DIR, ENTRY, SL, TP1, TP2, h, l, c, 20, 29, COST, stop_before_target=False)
    assert r_alt.exit_reason in ("tp1_then_tp2", "tp1_then_breakeven", "tp1_then_timeout")


def test_tp1_tp2_same_bar_toggle_QB():
    o, h, l, c = _series()
    h[4] = 103.5                                 # TP1 ȘI TP2 pe aceeași bară @4
    r_both = simulate_partial_exit(0, DIR, ENTRY, SL, TP1, TP2, h, l, c, 20, 29, COST)
    assert r_both.exit_reason == "tp1_then_tp2" and r_both.leg2_exit_idx == 4   # default: ambele @4
    r_seq = simulate_partial_exit(0, DIR, ENTRY, SL, TP1, TP2, h, l, c, 20, 29, COST, tp1_tp2_same_bar=False)
    assert r_seq.R_leg1 == 2.0                    # TP1 @4, TP2 abia dintr-o bară ulterioară (aici → timeout)


def test_short_direction_symmetric():
    # Short: entry=100, sl=101 (R=1), tp1=98 (+2R), tp2=97 (+3R); breakeven=100
    o = [100.0] * 30; h = [100.5] * 30; l = [99.5] * 30; c = [100.0] * 30
    for j in range(4, 9):                          # după TP1, prețul stă SUB breakeven (high<100) → runnerul ține
        o[j] = h[j] = l[j] = c[j] = 98.5
    l[4], h[4] = 97.5, 99.0                        # TP1 (98) @4
    for j in range(5, 8):
        l[j] = 97.6                                # peste TP2 (97)
    l[8], h[8] = 96.5, 99.0                        # TP2 (97) @8
    r = simulate_partial_exit(0, -1, 100.0, 101.0, 98.0, 97.0, h, l, c, 20, 29, COST)
    assert r.exit_reason == "tp1_then_tp2" and r.R_leg1 == 2.0 and r.R_leg2 == 3.0


def test_zero_risk_raises():
    o, h, l, c = _series()
    with pytest.raises(ValueError):
        simulate_partial_exit(0, DIR, 100.0, 100.0, 102.0, 103.0, h, l, c, 20, 29, COST)
