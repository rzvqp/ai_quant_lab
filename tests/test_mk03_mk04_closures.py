"""Teste sintetice pentru primitivele MK-03/MK-04 închise în Mandat 5.5 (v2.5.6).

IFVG (Q4), gradientul FVG + consumare (Q5/Q6), derive_week_index (Q3-week), PDH touch (Q5).
Array-uri în memorie, fără CSV, fără .load().
"""

import os
import sys

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from market_structure import Block  # noqa: E402
from imbalance_mechanics import (  # noqa: E402
    FVGKind, detect_fvg_reactions, detect_fvgs, detect_inverse_fvgs,
)
from institutional_levels import (  # noqa: E402
    LevelKind, ReferenceLevel, derive_week_index, detect_level_touches,
)


# ─────────────────────── MK-03 Q4: IFVG (close beyond far edge) ───────────────
def test_ifvg_bullish_inverts_on_first_close_below_lower():
    # serie curată: un SINGUR FVG bullish [10,12] (bare suprapuse, fără goluri bearish)
    h = [10, 15, 16, 14, 12, 11]
    l = [8, 13, 12, 11, 9.5, 9]
    c = [10, 15, 13, 13, 9.5, 9]     # close[4]=9.5 < lower(10) → inversare la j=4
    blocks = [Block(0, 6)]
    fvgs = detect_fvgs(h, l, blocks)
    assert len(fvgs) == 1 and fvgs[0].kind is FVGKind.BULLISH   # [10,12]
    ifvgs = detect_inverse_fvgs(h, l, c, fvgs, blocks)
    assert len(ifvgs) == 1
    inv = ifvgs[0]
    assert inv.kind is FVGKind.BEARISH and inv.formed_idx == 4   # polaritate inversată, la close-through
    assert inv.lower == 10 and inv.upper == 12                   # aceeași zonă


def test_ifvg_no_inversion_without_close_through():
    h = [10, 15, 16, 14, 12]
    l = [8, 13, 12, 11, 11]
    c = [10, 15, 13, 13, 11]         # close nu coboară sub 10 → fără inversare (fitilul nu contează)
    fvgs = detect_fvgs(h, l, [Block(0, 5)])
    assert len(fvgs) == 1
    assert detect_inverse_fvgs(h, l, c, fvgs, [Block(0, 5)]) == []


# ─────────────────── MK-03 Q5/Q6: gradientul în 3 trepte + D7 ─────────────────
def test_fvg_reaction_gradient_wick_then_close():
    h = [10, 15, 16, 14, 12, 11]
    l = [8, 13, 12, 11, 9.5, 9]      # low[3]=11<=ce50(11) FITIL; low[4]=9.5<=lower(10) FITIL
    c = [10, 15, 13, 13, 9.5, 9]     # close[4]=9.5<lower(10) CLOSE → inversare
    fvgs = detect_fvgs(h, l, [Block(0, 6)])           # bullish [10,12], ce50=11
    assert len(fvgs) == 1
    r = detect_fvg_reactions(h, l, c, fvgs, [Block(0, 6)])[0]
    assert r.ce50_touch_idx == 3      # treapta 1 (consumare D7), fitil
    assert r.full_fill_idx == 4       # treapta 2, fitil
    assert r.inversion_idx == 4       # treapta 3, close


def test_ce50_touch_is_wick_not_close():
    # low atinge ce50 dar close rămâne deasupra → tot se consideră atingere CE-50 (fitil)
    h = [10, 15, 16, 14]
    l = [8, 13, 12, 11]             # low[3]=11 <= ce50=11
    c = [10, 15, 13, 14]           # close[3]=14 > ce50 (nu close)
    fvgs = detect_fvgs(h, l, [Block(0, 4)])
    assert len(fvgs) == 1
    r = detect_fvg_reactions(h, l, c, fvgs, [Block(0, 4)])[0]
    assert r.ce50_touch_idx == 3 and r.inversion_idx is None


# ─────────────────── MK-04 Q3-week: derivare din golul de weekend ─────────────
def test_derive_week_index_increments_on_weekend_gap():
    # zile 100,101 consecutive; salt la 104 (gol de 3 zile = weekend) → săptămână nouă
    assert derive_week_index([100, 100, 101, 101, 104, 104]) == [0, 0, 0, 0, 1, 1]


def test_derive_week_index_no_gap_single_week():
    assert derive_week_index([100, 101, 102]) == [0, 0, 0]


# ─────────────────── MK-04 Q5: PDH consumat la prima atingere/zi ──────────────
def test_pdh_consumed_at_first_touch_within_day():
    h = [10, 10, 10, 15, 21, 22, 15]
    l = [9, 9, 9, 14, 20, 21, 14]
    day = [0, 0, 0, 1, 1, 1, 1]      # PDH disponibil de la bara 3 (ziua 1)
    lv = ReferenceLevel(price=20.0, kind=LevelKind.PDH, source_period_start=0,
                        available_idx=3, block_index=0)
    touches = detect_level_touches(h, l, [lv], day, [Block(0, 7)])
    assert len(touches) == 1                    # o singură atingere, deși high[5]=22 e a doua
    assert touches[0].touch_idx == 4            # prima bară cu high>=20 (D7, fără re-armare)


def test_pdl_touch_and_weekly_skipped():
    l = [9, 9, 8, 5, 9]
    h = [10, 10, 10, 10, 10]
    day = [0, 0, 1, 1, 1]
    pdl = ReferenceLevel(price=6.0, kind=LevelKind.PDL, source_period_start=0, available_idx=2, block_index=0)
    wk = ReferenceLevel(price=6.0, kind=LevelKind.WEEKLY_LOW, source_period_start=0, available_idx=2,
                        block_index=0, days_contributing=2, completeness="PARTIAL")
    touches = detect_level_touches(h, l, [pdl, wk], day, [Block(0, 5)])
    assert len(touches) == 1 and touches[0].touch_idx == 3   # low[3]=5<=6; weekly sărit (fereastră diferită)
