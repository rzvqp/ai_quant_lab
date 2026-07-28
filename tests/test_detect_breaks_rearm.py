"""Acceptance tests for the detect_breaks re-arming patch (Mandate 5.2).

Regula ratificată (Statistician): un swing depășit de corp intră într-o mulțime de
CONSUMATE, filtrată la nivel de bazin ÎNAINTE de atribuirea live_hh/live_ll/live_hl/
live_lh — niciodată anulare downstream. Un singur swing structural produce EXACT o rupere.

Aceste teste PIC pe codul actual (re-armare) și TREC după patch. Scrise înainte de patch,
nu retroactiv. Acoperă toate cele patru referințe + cazul consumat-urmat-de-același-tip.

Setup: `code/` nu e pachet; adăugăm în sys.path (ca pipeline-ul), nu reparăm importuri.
"""

import os
import sys

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from market_structure import (  # noqa: E402
    Block, BreakKind, detect_breaks, detect_swings, label_structure,
)


def _breaks(h, l, c):
    blocks = [Block(0, len(h))]
    swings = label_structure(detect_swings(h, l, blocks, k=2))
    return detect_breaks(c, swings, blocks)


def _of(breaks, kind):
    return [b for b in breaks if b.kind is kind]


# ── un singur swing structural de fiecare tip → EXACT o rupere ────────────────

def test_single_HH_produces_exactly_one_BOS_BULL():
    # un singur HH la idx7 (price 16), platou la 20 (fără swing, D2)
    h = [10, 11, 12, 11, 10, 14, 15, 16, 15, 14, 20, 20, 20, 20]
    l = [9, 8, 7, 8, 9, 13, 12, 11, 12, 13, 19, 19, 19, 19]
    c = [10, 11, 12, 11, 10, 14, 15, 16, 15, 14, 20, 20, 20, 20]
    bos = _of(_breaks(h, l, c), BreakKind.BOS_BULL)
    assert len(bos) == 1, f"un singur HH → o rupere; s-au produs {len(bos)}"
    assert bos[0].reference_swing.idx == 7


def test_single_LL_produces_exactly_one_BOS_BEAR():
    h = [21, 20, 19, 20, 21, 17, 16, 15, 16, 17, 11, 11, 11, 11]
    l = [20, 19, 18, 19, 20, 16, 15, 14, 15, 16, 10, 10, 10, 10]
    c = [20, 19, 18, 19, 20, 16, 15, 14, 15, 16, 10, 10, 10, 10]
    bear = _of(_breaks(h, l, c), BreakKind.BOS_BEAR)
    assert len(bear) == 1, f"un singur LL → o rupere; s-au produs {len(bear)}"
    assert bear[0].reference_swing.idx == 7


def test_single_LH_produces_exactly_one_CHOCH_BULL():
    # LH la idx7 (fără HH activ), close urcă peste el
    h = [10, 11, 16, 11, 10, 12, 13, 14, 13, 12, 20, 20, 20, 20]
    l = [9, 8, 7, 8, 9, 11, 12, 13, 12, 11, 19, 19, 19, 19]
    c = [10, 11, 16, 11, 10, 12, 13, 14, 13, 12, 20, 20, 20, 20]
    ch = _of(_breaks(h, l, c), BreakKind.CHOCH_BULL)
    assert len(ch) == 1, f"un singur LH → o rupere CHoCH; s-au produs {len(ch)}"
    assert ch[0].reference_swing.idx == 7


def test_single_HL_produces_exactly_one_CHOCH_BEAR():
    # highs plate (niciun swing high) → HL la idx7 (fără LL activ), close scade sub el
    h = [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30]
    l = [20, 19, 14, 19, 20, 18, 17, 16, 17, 18, 10, 10, 10, 10]
    c = [20, 19, 14, 19, 20, 18, 17, 16, 17, 18, 10, 10, 10, 10]
    ch = _of(_breaks(h, l, c), BreakKind.CHOCH_BEAR)
    assert len(ch) == 1, f"un singur HL → o rupere CHoCH; s-au produs {len(ch)}"
    assert ch[0].reference_swing.idx == 7


# ── consumat-urmat-de-același-tip: al doilea trebuie să devină activ normal ────

def test_consumed_swing_does_not_block_a_later_same_type():
    # HH_A la idx7 (16), rupt o dată; apoi HH_B la idx12 (24), rupt o dată.
    h = [10, 11, 12, 11, 10, 14, 15, 16, 15, 14, 20, 22, 24, 22, 20, 15, 15, 15, 15, 15]
    l = [9, 8, 7, 8, 9, 13, 12, 11, 12, 13, 19, 21, 23, 21, 19, 14, 14, 14, 14, 14]
    c = [10, 11, 12, 11, 10, 14, 15, 16, 17, 18, 19, 18, 17, 18, 17, 25, 25, 25, 25, 25]
    bos = _of(_breaks(h, l, c), BreakKind.BOS_BULL)
    assert len(bos) == 2, f"A consumat + B activ → 2 rupturi; s-au produs {len(bos)}"
    assert sorted(b.reference_swing.idx for b in bos) == [7, 12]  # A apoi B, fiecare o dată
