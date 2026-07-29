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
    Breaker, DemandZone, ReactionEvent, detect_demand_zones, detect_mitigations, detect_order_blocks,
    detect_rejections, track_breaker,
)


def test_demand_zone_is_full_range_superset_of_ob():
    o, h, l, c, n = _engulfing_series()
    obs = detect_order_blocks(o, h, l, c, n)
    dzs = detect_demand_zones(o, h, l, c, n)
    assert len(dzs) == len(obs) == 1
    dz, ob = dzs[0], obs[0]
    assert isinstance(dz, DemandZone) and dz.formation_idx == ob.formation_idx and dz.kind is ob.kind
    # DemandZone = [Low, High] al barei-ancoră (15): superset STRICT al corpului OB [99,100]
    assert (dz.zone_lower, dz.zone_upper) == (l[15], h[15]) == (98.8, 100.3)
    assert dz.zone_lower <= ob.zone_lower and dz.zone_upper >= ob.zone_upper


def _engulfing_series(n: int = 18):
    """Bare mici (ATR warmup), bară bearish 15, impuls bullish 16 care înghite corpul lui 15."""
    o = [100.0] * n; h = [100.6] * n; l = [99.4] * n; c = [100.0] * n
    for i in range(1, 15):
        c[i] = 100.0 + (0.2 if i % 2 else -0.2)
    o[15], c[15], h[15], l[15] = 100.0, 99.0, 100.3, 98.8     # bearish, body [99,100]
    o[16], c[16], h[16], l[16] = 98.9, 101.5, 101.7, 98.7     # impuls bullish, înghite [99,100]
    return o, h, l, c, n


def _ob_then_touch_series(touch_idx: int = 22, n: int = 30):
    """Impuls bullish @16 (OB formation_idx=15, zonă corp [99,100], podea low[15]=98.8), preț SUS după impuls,
    apoi o atingere LEGITIMĂ (fitil în zonă, close peste podea) la `touch_idx`."""
    o, h, l, c, _ = _engulfing_series(n=n)
    for j in range(17, n):
        o[j] = h[j] = l[j] = c[j] = 101.5                     # sus, nu atinge zona, fără breaker
    o[touch_idx], h[touch_idx], l[touch_idx], c[touch_idx] = 101.0, 101.2, 98.9, 100.2  # fitil în [99,100], close>98.8
    return o, h, l, c, n


def test_fix_impulse_bar_produces_no_reaction():
    """Bara de impuls (16) NU mai produce o vizită; atingerea legitimă (22) apare în continuare — Mit ȘI Rej."""
    o, h, l, c, n = _ob_then_touch_series(touch_idx=22)
    ob = detect_order_blocks(o, h, l, c, n)[0]
    assert ob.formation_idx == 15
    mits = detect_mitigations(ob, h, l, c, n)
    rejs = detect_rejections(ob, h, l, c, n)
    assert all(e.event_idx != 16 for e in mits)               # impulsul nu mai e o vizită
    assert all(e.event_idx != 16 for e in rejs)
    assert [e.event_idx for e in mits] == [22]                # doar atingerea legitimă
    assert [e.event_idx for e in rejs] == [22]                # low 98.9<99=zl, close 100.2>99 → rejecție D6


def test_ob_formation_bullish_engulfing_impulse():
    o, h, l, c, n = _engulfing_series()
    obs = detect_order_blocks(o, h, l, c, n)
    assert len(obs) == 1
    ob = obs[0]
    assert ob.kind is OrderBlockKind.BULLISH
    assert ob.formation_idx == 15                              # bara-ancoră ÎNGHIȚITĂ (i-1)
    assert (ob.zone_lower, ob.zone_upper) == (99.0, 100.0)     # CORPUL barei înghițite
    # podeaua breaker-ului frozen = low[formation_idx] = low al barei OB
    assert l[ob.formation_idx] == 98.8


def test_ob_formation_requires_opposite_and_engulfment():
    # impuls bullish dar bara precedentă tot bullish (nu opusă) → fără OB
    o, h, l, c, n = _engulfing_series()
    o[15], c[15] = 99.0, 100.0                                 # bara 15 acum BULLISH (aceeași direcție)
    assert detect_order_blocks(o, h, l, c, n) == []
    # impuls prea slab (range mic) → fără OB
    o2, h2, l2, c2, n2 = _engulfing_series()
    h2[16], l2[16], o2[16], c2[16] = 100.4, 99.6, 99.7, 100.3  # range 0.8 < 1.5×ATR
    assert detect_order_blocks(o2, h2, l2, c2, n2) == []


def test_ob_formation_no_lookahead():
    """Mutarea barelor de DUPĂ impuls nu schimbă niciun OB anterior (formarea folosește doar bare ≤ i)."""
    o, h, l, c, n = _engulfing_series(n=30)
    o[16], c[16], h[16], l[16] = 98.9, 101.5, 101.7, 98.7      # impuls @16
    base = [(x.formation_idx, x.kind.value, x.zone_lower, x.zone_upper) for x in detect_order_blocks(o, h, l, c, n)]
    for i in range(18, n):                                     # mutăm agresiv barele > impuls
        o[i], h[i], l[i], c[i] = 500.0, 600.0, 50.0, 55.0
    after = [(x.formation_idx, x.kind.value, x.zone_lower, x.zone_upper) for x in detect_order_blocks(o, h, l, c, n)]
    assert [x for x in base if x[0] < 17] == [x for x in after if x[0] < 17]


def _bull_ob() -> OrderBlock:
    # corp bullish [100,102]; bara OB are Low_OB=99 (fitil sub corp)
    return OrderBlock(formation_idx=0, kind=OrderBlockKind.BULLISH, zone_lower=100.0, zone_upper=102.0)


def _bear_ob() -> OrderBlock:
    return OrderBlock(formation_idx=0, kind=OrderBlockKind.BEARISH, zone_lower=100.0, zone_upper=102.0)


def test_ob_formation_empty_on_trivial_input():
    assert detect_order_blocks([1.0], [1.0], [1.0], [1.0], 1) == []   # fără ATR/impuls → fără OB


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
