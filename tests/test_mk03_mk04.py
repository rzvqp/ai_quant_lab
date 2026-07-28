"""Teste sintetice pentru primitivele MK-03/MK-04 implementate (Mandat 5.3).

Doar ce e ratificat: FVG, CE 50%, count_bpr (D-BPR); PDH/PDL + D3_bis; Weekly + D-WEEK.
Neimplementate (NotImplementedError): IFVG. Array-uri în memorie, fără CSV, fără .load().
"""

import os
import sys

import pytest

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from market_structure import Block  # noqa: E402
from imbalance_mechanics import (  # noqa: E402
    FairValueGap, FVGKind, count_bpr, detect_fvgs, detect_inverse_fvgs,
)
from institutional_levels import (  # noqa: E402
    LevelKind, compute_prior_day_levels, compute_prior_week_levels,
)


# ─────────────────────────── MK-03: FVG ──────────────────────────────────────
def test_fvg_bullish_detected_with_correct_level_and_confirmed_idx():
    h = [10, 20, 10]
    l = [9, 19, 15]
    fvgs = detect_fvgs(h, l, [Block(0, 3)])
    assert len(fvgs) == 1
    f = fvgs[0]
    assert f.kind is FVGKind.BULLISH and f.formed_idx == 1 and f.confirmed_idx == 2
    assert f.lower == 10 and f.upper == 15          # [high[0], low[2]]
    assert f.ce_50 == 12.5


def test_fvg_bearish_detected():
    h = [10, 5, 8]          # high[2]=8 < low[0]=? need high[i+1] < low[i-1]
    l = [9, 4, 6]
    fvgs = detect_fvgs(h, l, [Block(0, 3)])
    assert len(fvgs) == 1 and fvgs[0].kind is FVGKind.BEARISH
    assert fvgs[0].lower == 8 and fvgs[0].upper == 9   # [high[2], low[0]]


def test_no_gap_no_fvg():
    h = [10, 11, 12]
    l = [9, 10, 11]         # low[2]=11 not > high[0]=10? 11>10 -> would be bullish; make it not
    l = [9, 10, 9]
    assert detect_fvgs(h, l, [Block(0, 3)]) == []


def test_fvg_window_confined_to_block():
    # un gol care ar traversa granița dintre blocul [0,3) și [3,6) NU e detectat peste ea
    h = [10, 10, 10, 10, 20, 10]
    l = [9, 9, 9, 9, 19, 30]      # low[5]=30 > high[3]=10 dar i=4 e la granița blocului 2
    fvgs = detect_fvgs(h, l, [Block(0, 3), Block(3, 6)])
    # i valabil în blocul 2: range(4,5) -> i=4; fereastra 3,4,5 în [3,6) -> permis
    # niciun FVG cu fereastra care traversează granița 3
    for f in fvgs:
        assert (f.block_index == 0 and 1 <= f.formed_idx <= 1) or (f.block_index == 1 and 4 <= f.formed_idx <= 4)


def test_detect_inverse_fvgs_is_open_question():
    with pytest.raises(NotImplementedError):
        detect_inverse_fvgs([1.0], [1.0], [1.0], [], [Block(0, 1)])


# ─────────────────────────── MK-03: count_bpr (D-BPR) ────────────────────────
def _fvg(kind, lo, hi, idx, blk=0):
    return FairValueGap(formed_idx=idx, confirmed_idx=idx + 1, lower=lo, upper=hi, kind=kind, block_index=blk)


def test_count_bpr_monotone_across_tolerances():
    fvgs = [
        _fvg(FVGKind.BULLISH, 10, 15, 1), _fvg(FVGKind.BEARISH, 11, 14, 2),   # overlap (gap<=0) → toate
        _fvg(FVGKind.BULLISH, 20, 25, 5), _fvg(FVGKind.BEARISH, 25.2, 30, 6),  # gap=0.2 → doar t=0.25
    ]
    c = count_bpr(fvgs, [Block(0, 10)], tolerances=(0.0, 0.10, 0.25), max_window_bars=3)
    assert c[0.0] == 1 and c[0.10] == 1 and c[0.25] == 2         # monoton
    assert c[0.0] <= c[0.10] <= c[0.25]


def test_count_bpr_respects_window_and_block():
    fvgs = [
        _fvg(FVGKind.BULLISH, 10, 15, 1), _fvg(FVGKind.BEARISH, 11, 14, 9),      # |1-9|=8 > 3 → nu
        _fvg(FVGKind.BULLISH, 10, 15, 1, blk=0), _fvg(FVGKind.BEARISH, 11, 14, 2, blk=1),  # blocuri ≠ → nu
    ]
    assert count_bpr(fvgs, [Block(0, 10), Block(10, 20)]) == {0.0: 0, 0.10: 0, 0.25: 0}


# ─────────────────────────── MK-04: PDH/PDL + D3_bis ─────────────────────────
def test_pdh_pdl_from_prior_day_and_lag():
    h = [10, 12, 11, 20, 22, 21, 15, 14, 16]
    l = [8, 9, 7, 18, 19, 17, 13, 12, 11]
    day = [0, 0, 0, 1, 1, 1, 2, 2, 2]
    lv = compute_prior_day_levels(h, l, day, [Block(0, 9)])
    pdh = {x.available_idx: x.price for x in lv if x.kind is LevelKind.PDH}
    pdl = {x.available_idx: x.price for x in lv if x.kind is LevelKind.PDL}
    assert pdh == {3: 12, 6: 22}          # ziua 0 → PDH 12 la ziua 1 (avail 3); ziua 1 → 22 la ziua 2
    assert pdl == {3: 7, 6: 17}
    # prima zi (ziua 0) NU produce nivel (D3_bis)
    assert all(x.available_idx != 0 for x in lv)


def test_d3bis_first_day_of_each_block_unclassified():
    h = [10, 11, 12, 13, 14, 15]
    l = [1, 2, 3, 4, 5, 6]
    day = [0, 0, 0, 1, 1, 1]           # bloc1 are DOAR ziua 1 → prima (și singura) zi → 0 niveluri
    lv = compute_prior_day_levels(h, l, day, [Block(0, 3), Block(3, 6)])
    assert [x.block_index for x in lv] == []   # niciun bloc nu are ≥2 zile → 0 niveluri


# ─────────────────────────── MK-04: Weekly + D-WEEK ──────────────────────────
def test_weekly_complete_and_partial_with_days_contributing():
    #        w0: 5 zile (COMPLETE) | w1: 2 zile (PARTIAL) | w2: 1 zi
    day = [0, 1, 2, 3, 4, 5, 6, 7]
    week = [0, 0, 0, 0, 0, 1, 1, 2]
    h = [10, 11, 12, 13, 14, 20, 21, 30]
    l = [5, 6, 7, 8, 9, 18, 19, 28]
    lv = compute_prior_week_levels(h, l, day, week, [Block(0, 8)])
    wh = [x for x in lv if x.kind is LevelKind.WEEKLY_HIGH]
    # ref w0 (la w1): COMPLETE, 5 zile, WH=14; ref w1 (la w2): PARTIAL, 2 zile, WH=21
    by_avail = {x.available_idx: x for x in wh}
    assert by_avail[5].price == 14 and by_avail[5].days_contributing == 5 and by_avail[5].completeness == "COMPLETE"
    assert by_avail[7].price == 21 and by_avail[7].days_contributing == 2 and by_avail[7].completeness == "PARTIAL"


def test_d3bis_first_week_unclassified():
    day = [0, 1, 2]
    week = [0, 0, 0]                   # o singură săptămână → prima → 0 niveluri
    lv = compute_prior_week_levels([1.0, 2, 3], [1.0, 2, 3], day, week, [Block(0, 3)])
    assert lv == []
