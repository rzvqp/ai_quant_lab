"""Teste sintetice pentru Modulul 5 (order_flow.py) — Order Block / Breaker / Mitigation / Rejection.

Array-uri în memorie, fără CSV, fără .load(). Acoperă: formarea OB = NotImplementedError; mașina de stare
Breaker (Low_OB, E010 verbatim); Mitigation (span E015 + cooldown); Rejection (D6 sweep-reject); și, cel
mai important, ABSENȚA LOOKAHEAD-ului = separarea anti-E010 (mutarea barelor de după un eveniment nu schimbă
niciun eveniment anterior).
"""

import os
import sys

import pytest

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from order_block_void import OrderBlock, OrderBlockKind  # noqa: E402
from order_flow import (  # noqa: E402
    Breaker, ReactionEvent, detect_mitigations, detect_order_blocks, detect_rejections, track_breaker,
)


def _bull_ob() -> OrderBlock:
    # corp bullish [100,102]; bara OB are Low_OB=99 (fitil sub corp)
    return OrderBlock(formation_idx=0, kind=OrderBlockKind.BULLISH, zone_lower=100.0, zone_upper=102.0)


def _bear_ob() -> OrderBlock:
    return OrderBlock(formation_idx=0, kind=OrderBlockKind.BEARISH, zone_lower=100.0, zone_upper=102.0)


def test_formation_is_open_not_invented():
    with pytest.raises(NotImplementedError):
        detect_order_blocks([1.0], [1.0], [1.0], [1.0], 1)


def test_breaker_bullish_flips_on_close_below_Low_OB():
    ob = _bull_ob()
    #        i:   0     1     2      3
    high = [102.0, 103, 101.5, 101.0]
    low = [99.0, 101.0, 100.5, 98.0]     # Low_OB = low[0] = 99.0
    close = [101.0, 102.0, 101.0, 98.5]   # bar 3 close 98.5 < 99.0 → flip
    br = track_breaker(ob, high, low, close, len(close))
    assert isinstance(br, Breaker)
    assert br.breaker_idx == 3
    assert br.kind is OrderBlockKind.BEARISH        # polaritate inversată
    assert (br.zone_lower, br.zone_upper) == (100.0, 102.0)  # zona re-înregistrată = corpul OB


def test_breaker_uses_bar_low_not_body_floor():
    # close scade sub podeaua CORPULUI (100) dar rămâne peste Low_OB (99) → NU e breaker
    ob = _bull_ob()
    high = [102.0, 101.0, 101.0]
    low = [99.0, 99.5, 99.2]
    close = [101.0, 99.6, 99.3]      # sub 100 (corp) dar peste 99 (Low_OB) → fără flip
    assert track_breaker(ob, high, low, close, len(close)) is None


def test_breaker_bearish_symmetric():
    ob = _bear_ob()
    high = [103.0, 102.0, 104.0]     # High_OB = high[0] = 103.0; bar 2 high irelevant, close contează
    low = [100.0, 101.0, 102.0]
    close = [101.0, 101.5, 103.5]    # bar 2 close 103.5 > 103.0 → flip la bullish
    br = track_breaker(ob, high, low, close, len(close))
    assert br is not None and br.breaker_idx == 2 and br.kind is OrderBlockKind.BULLISH


def test_mitigation_span_overlap_and_cooldown():
    ob = _bull_ob()
    # bare care ating zona [100,102] la i=2 și i=3 (consecutive, ≤4 → o singură vizită), apoi i=10 (vizită nouă)
    n = 12
    high = [102.0] + [99.5] * (n - 1)
    low = [99.0] + [99.5] * (n - 1)
    close = [101.0] + [99.5] * (n - 1)
    for i in (2, 3):                 # touch: low<=102 & high>=100
        high[i], low[i] = 101.0, 100.5
    high[10], low[10] = 101.0, 100.5
    ev = detect_mitigations(ob, high, low, close, n)
    assert [e.visit_number for e in ev] == [1, 2]
    assert [e.event_idx for e in ev] == [2, 10]          # i=3 unit în vizita 1 prin cooldown


def test_mitigation_stops_at_breaker():
    ob = _bull_ob()
    n = 8
    high = [102.0] + [101.0] * (n - 1)
    low = [99.0] + [100.5] * (n - 1)     # atinge zona la fiecare bară
    close = [101.0, 101.0, 98.0, 101.0, 101.0, 101.0, 101.0, 101.0]  # breaker la i=2 (close 98<99)
    ev = detect_mitigations(ob, high, low, close, n)
    assert all(e.event_idx < 2 for e in ev)              # nicio vizită la/după breaker


def test_rejection_d6_sweep_reject_bullish():
    ob = _bull_ob()
    # fitil sub podeaua corpului (100) + închidere înapoi deasupra → rejecție
    n = 6
    high = [102.0, 101.0, 101.0, 101.0, 101.0, 101.0]
    low = [99.0, 100.5, 99.5, 100.5, 100.5, 100.5]        # i=2: low 99.5 < 100 (zone_lower)
    close = [101.0, 100.8, 100.7, 100.8, 100.8, 100.8]    # i=2: close 100.7 > 100 → reject
    ev = detect_rejections(ob, high, low, close, n)
    assert [e.event_idx for e in ev] == [2]
    assert ev[0].event_type == "rejection"


def test_window_separation_disjoint_contract():
    ob = _bull_ob()
    n = 30
    high = [102.0] + [99.5] * (n - 1)
    low = [99.0] + [99.5] * (n - 1)
    close = [101.0] + [99.5] * (n - 1)
    high[5], low[5] = 101.0, 100.5       # o mitigare la i=5
    ev = detect_mitigations(ob, high, low, close, n)
    assert len(ev) == 1
    e = ev[0]
    assert e.selection_end == e.event_idx == 5
    assert e.measurement_start == 5 and e.measurement_end == min(5 + 20, n)


def test_no_lookahead_mitigation():
    """Mutarea barelor de DUPĂ un eveniment NU schimbă niciun eveniment cu event_idx anterior."""
    ob = _bull_ob()
    n = 30
    high = [102.0] + [99.5] * (n - 1)
    low = [99.0] + [99.5] * (n - 1)
    close = [101.0] + [99.5] * (n - 1)
    for i in (5, 15):
        high[i], low[i] = 101.0, 100.5
    base = detect_mitigations(ob, high, low, close, n)
    base_before = [(e.event_idx, e.visit_number) for e in base if e.event_idx < 10]
    # mutăm agresiv barele de după i=10 (inclusiv creăm un breaker fals)
    for i in range(11, n):
        high[i], low[i], close[i] = 200.0, 50.0, 40.0
    mutated = detect_mitigations(ob, high, low, close, n)
    mutated_before = [(e.event_idx, e.visit_number) for e in mutated if e.event_idx < 10]
    assert base_before == mutated_before        # evenimentele anterioare lui i=10 neschimbate


def test_no_lookahead_rejection():
    ob = _bear_ob()
    n = 30
    high = [103.0] + [100.5] * (n - 1)
    low = [100.0] + [100.5] * (n - 1)
    close = [101.0] + [100.5] * (n - 1)
    high[4], close[4] = 103.5, 101.5     # rejecție bearish la i=4: high>102 (zone_upper) & close<102
    base = detect_rejections(ob, high, low, close, n)
    base_before = [(e.event_idx, e.visit_number) for e in base if e.event_idx < 10]
    for i in range(11, n):
        high[i], low[i], close[i] = 500.0, 400.0, 450.0
    mutated = detect_rejections(ob, high, low, close, n)
    mutated_before = [(e.event_idx, e.visit_number) for e in mutated if e.event_idx < 10]
    assert base_before == mutated_before
