"""Teste pentru cele trei detectoare de reacție (Void, BPR, Weekly). Sintetic; fără MT5.
Per detector: gradientul/geometria, non-lookahead (ferestre disjuncte), D7, fail-closed, propagarea PARTIAL.
"""

from __future__ import annotations

import os
import sys
from typing import Sequence

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from market_structure import Block  # noqa: E402
from imbalance_mechanics import FVGKind, FairValueGap  # noqa: E402
from institutional_levels import LevelKind, ReferenceLevel  # noqa: E402
from reaction_detectors import (  # noqa: E402
    BprReaction, EntrySide, VoidReaction, WeeklyLevelTouch, detect_bpr_reactions,
    detect_void_reactions, detect_weekly_level_touches,
)

_T0 = 1_600_000_000


def _arrs(rows: Sequence[tuple[float, float, float, float]]) -> tuple[
        list[float], list[float], list[float], list[float], list[int]]:
    o = [r[0] for r in rows]; h = [r[1] for r in rows]; l = [r[2] for r in rows]; c = [r[3] for r in rows]
    t = [_T0 + j * 900 for j in range(len(rows))]              # M15 consecutiv (fără gol temporal)
    return o, h, l, c, t


# ───────────────────────────── PARTEA 1 — void ─────────────────────────────
def _bull_void_rows() -> list[tuple[float, float, float, float]]:
    return [(100, 100.5, 99.5, 100), (100, 100.5, 99.5, 100), (100, 100.5, 99.5, 100),   # 0-2 (c=2)
            (110, 112, 108, 111),                                                          # 3: gap sus 10 → void BULL
            (111, 111.5, 104, 106),                                                        # 4: partial (low<=105)
            (106, 106.5, 99, 101),                                                         # 5: full   (low<=100)
            (101, 113.5, 109, 113),                                                        # 6: rejection (low<=110,close>110)
            (113, 113.5, 112.5, 113), (113, 113.5, 112.5, 113), (113, 113.5, 112.5, 113)]  # 7-9 filler


def test_void_bullish_three_step_gradient() -> None:
    o, h, l, c, t = _arrs(_bull_void_rows())
    r = detect_void_reactions(o, h, l, c, t, [Block(0, len(c))])
    assert len(r) == 1
    v = r[0]
    assert v.void_at_idx == 2 and v.polarity is FVGKind.BULLISH and v.available_idx == 3
    assert (v.zone_lower, v.zone_upper, v.mid) == (100.0, 110.0, 105.0)
    assert (v.partial_fill_idx, v.full_fill_idx, v.rejection_idx) == (4, 5, 6)   # gradient în 3 trepte


def test_void_bearish_symmetric() -> None:
    rows = [(100, 100.5, 99.5, 100), (100, 100.5, 99.5, 100), (100, 100.5, 99.5, 100),
            (90, 92, 88, 89),                                   # gap jos 10 → void BEAR (open<close)
            (89, 96, 88.5, 94),                                 # partial: high>=95? 96>=95 → partial
            (94, 101, 93, 99),                                  # full: high>=100 → 101
            (99, 91, 87, 87)]                                   # rejection: high>=90(91) & close<90(87)
    o, h, l, c, t = _arrs(rows)
    r = detect_void_reactions(o, h, l, c, t, [Block(0, len(c))])
    assert len(r) == 1 and r[0].polarity is FVGKind.BEARISH
    assert (r[0].zone_lower, r[0].zone_upper) == (90.0, 100.0)
    assert (r[0].partial_fill_idx, r[0].full_fill_idx, r[0].rejection_idx) == (4, 5, 6)


def test_void_no_reaction_leaves_none() -> None:
    rows = _bull_void_rows()[:4] + [(111, 111.5, 110.5, 111)] * 6   # nicio bară nu coboară în zonă
    o, h, l, c, t = _arrs(rows)
    r = detect_void_reactions(o, h, l, c, t, [Block(0, len(c))])
    assert len(r) == 1 and (r[0].partial_fill_idx, r[0].full_fill_idx, r[0].rejection_idx) == (None, None, None)


def test_void_measurement_disjoint_from_selection() -> None:
    # bara available_idx (c+1=3) NU intră în măsurare (scanarea începe la c+2) — nicio reacție pe bara 3
    o, h, l, c, t = _arrs(_bull_void_rows())
    r = detect_void_reactions(o, h, l, c, t, [Block(0, len(c))])
    for idx in (r[0].partial_fill_idx, r[0].full_fill_idx, r[0].rejection_idx):
        assert idx is None or idx >= r[0].available_idx + 1    # măsurare DISJUNCTĂ de selecție


# ───────────────────────────── PARTEA 2 — BPR (geometrie agnostică) ─────────────────────────────
def _bpr_fvgs() -> list[FairValueGap]:
    bull = FairValueGap(formed_idx=2, confirmed_idx=3, upper=102.0, lower=98.0, kind=FVGKind.BULLISH, block_index=0)
    bear = FairValueGap(formed_idx=3, confirmed_idx=4, upper=103.0, lower=99.0, kind=FVGKind.BEARISH, block_index=0)
    return [bull, bear]                                         # zonă = [max(98,99), min(102,103)] = [99,102]; avail=4


def test_bpr_entry_above_touch_and_traverse() -> None:
    # close[j-1] > 102 → entry ABOVE; bara atinge zona (conținere), apoi traversează sub (low<=99)
    h = [101.0] * 5 + [104, 104, 97, 97, 97]
    l = [101.0] * 5 + [100, 98, 96, 96, 96]                     # j=5 conținere(100<=102,104>=99); j=6 low98<=99 traverse
    c = [105.0] * 5 + [101, 97, 96, 96, 96]                     # close[4]=105>102 → ABOVE
    r = detect_bpr_reactions(h, l, c, _bpr_fvgs(), [Block(0, len(c))], tolerance=0.0)
    assert len(r) == 1
    b = r[0]
    assert (b.zone_lower, b.zone_upper, b.available_idx) == (99.0, 102.0, 4)
    assert b.touch_idx == 5 and b.entry_side is EntrySide.ABOVE and b.traverse_idx == 6


def test_bpr_entry_below_traverse_up() -> None:
    h = [95.0] * 5 + [100, 104, 104, 104, 104]                  # j=5 conținere; j=6 high104>=102 traverse
    l = [95.0] * 5 + [99, 100, 100, 100, 100]
    c = [95.0] * 5 + [100, 103, 103, 103, 103]                  # close[4]=95<99 → BELOW
    r = detect_bpr_reactions(h, l, c, _bpr_fvgs(), [Block(0, len(c))], tolerance=0.0)
    assert r[0].entry_side is EntrySide.BELOW and r[0].touch_idx == 5 and r[0].traverse_idx == 6


def test_bpr_reject_closes_back_on_entry_side() -> None:
    # entry ABOVE; bara intră în zonă (low<=102) și ÎNCHIDE înapoi deasupra (close>102) = D6
    h = [104.0] * 5 + [104, 104, 104, 104, 104]
    l = [104.0] * 5 + [101, 104, 104, 104, 104]                 # j=5 low101<=102 (conținere: high104>=99)
    c = [105.0] * 5 + [103, 105, 105, 105, 105]                 # close[4]=105>102 ABOVE; close5=103>102 → reject
    r = detect_bpr_reactions(h, l, c, _bpr_fvgs(), [Block(0, len(c))], tolerance=0.0)
    assert r[0].entry_side is EntrySide.ABOVE and r[0].reject_idx == 5


def test_bpr_entry_side_none_when_prev_inside_zone() -> None:
    h = [100.5] * 5 + [101, 101, 101, 101, 101]                 # close[4]=100.5 ÎN zonă [99,102] → entry ambiguu
    l = [100.5] * 5 + [100, 100, 100, 100, 100]
    c = [100.5] * 6 + [100, 100, 100, 100]
    r = detect_bpr_reactions(h, l, c, _bpr_fvgs(), [Block(0, len(c))], tolerance=0.0)
    assert r[0].touch_idx == 5 and r[0].entry_side is None      # conținere înregistrată, latura NEdeterminabilă
    assert r[0].traverse_idx is None and r[0].reject_idx is None


def test_bpr_pairing_conventions_window_and_tolerance() -> None:
    far = [FairValueGap(2, 3, 102.0, 98.0, FVGKind.BULLISH, 0),
           FairValueGap(10, 11, 103.0, 99.0, FVGKind.BEARISH, 0)]   # |2-10|>3 → nicio pereche
    h = [100.0] * 14; l = [100.0] * 14; c = [100.0] * 14
    assert detect_bpr_reactions(h, l, c, far, [Block(0, 14)], tolerance=0.0) == []
    disjoint = [FairValueGap(2, 3, 100.0, 98.0, FVGKind.BULLISH, 0),
                FairValueGap(3, 4, 105.0, 103.0, FVGKind.BEARISH, 0)]   # gap = 103-100=3 > 0 → fără BPR la tol 0
    assert detect_bpr_reactions([100.0] * 8, [100.0] * 8, [100.0] * 8, disjoint, [Block(0, 8)], tolerance=0.0) == []


def test_bpr_is_direction_agnostic_no_polarity_field() -> None:
    for field in ("polarity", "direction", "kind", "bias"):
        assert field not in BprReaction.__dataclass_fields__   # BPR nu are polaritate proprie — doar entry_side


# ───────────────────────────── PARTEA 3 — weekly (depășire, PARTIAL propagat) ─────────────────────────────
def _wk_level(price: float, kind: LevelKind, avail: int, completeness: str) -> ReferenceLevel:
    return ReferenceLevel(price=price, kind=kind, source_period_start=0, available_idx=avail, block_index=0,
                          days_contributing=5 if completeness == "COMPLETE" else 3, completeness=completeness)


def test_weekly_high_low_touch_by_exceedance() -> None:
    n = 8
    high = [100.0] * n; low = [100.0] * n
    high[3] = 111.0                                             # WEEKLY_HIGH=110 depășit (high>=110) la 3
    low[5] = 89.0                                               # WEEKLY_LOW=90 depășit (low<=90) la 5
    wk = [0] * n                                                # o singură săptămână
    levels = [_wk_level(110.0, LevelKind.WEEKLY_HIGH, 1, "COMPLETE"),
              _wk_level(90.0, LevelKind.WEEKLY_LOW, 1, "COMPLETE")]
    t = detect_weekly_level_touches(high, low, levels, wk, [Block(0, n)])
    by_kind = {x.level.kind: x.touch_idx for x in t}
    assert by_kind[LevelKind.WEEKLY_HIGH] == 3 and by_kind[LevelKind.WEEKLY_LOW] == 5   # DEPĂȘIRE, nu conținere


def test_weekly_window_bounded_by_current_week_and_d7() -> None:
    n = 8
    high = [100.0] * n; low = [100.0] * n
    high[2] = 111.0; high[6] = 111.0                            # atingere în săpt. 0 (bara 2) și săpt. 1 (bara 6)
    wk = [0, 0, 0, 0, 1, 1, 1, 1]                               # săptămâna se schimbă la bara 4
    lv = _wk_level(110.0, LevelKind.WEEKLY_HIGH, 1, "COMPLETE")
    t = detect_weekly_level_touches(high, low, [lv], wk, [Block(0, n)])
    assert len(t) == 1 and t[0].touch_idx == 2                  # DOAR în săptămâna nivelului; D7 prima atingere


def test_weekly_partial_flag_propagated_not_filtered() -> None:
    n = 6
    high = [100.0] * n; low = [100.0] * n; high[3] = 111.0
    wk = [0] * n
    lv = _wk_level(110.0, LevelKind.WEEKLY_HIGH, 1, "PARTIAL")  # săptămână carantinată
    t = detect_weekly_level_touches(high, low, [lv], wk, [Block(0, n)])
    assert len(t) == 1 and t[0].completeness == "PARTIAL"      # PROPAGAT, nu filtrat în primitivă
    # COMPLETE și PARTIAL se raportează SEPARAT (separarea = a consumatorului, prin `completeness`)
    complete = [x for x in t if x.completeness == "COMPLETE"]; partial = [x for x in t if x.completeness == "PARTIAL"]
    assert len(complete) == 0 and len(partial) == 1


def test_weekly_containment_not_used_for_extremes() -> None:
    # o bară care CONȚINE nivelul dar nu-l DEPĂȘEȘTE nu atinge un WEEKLY_HIGH (spre deosebire de Mid)
    n = 6
    high = [109.0] * n; low = [100.0] * n                       # range [100,109] conține 110? nu (110>109) → fără atingere
    wk = [0] * n
    lv = _wk_level(110.0, LevelKind.WEEKLY_HIGH, 1, "COMPLETE")
    assert detect_weekly_level_touches(high, low, [lv], wk, [Block(0, n)]) == []
