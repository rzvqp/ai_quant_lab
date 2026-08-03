"""Semantica de CASCADĂ pentru detect_breaks (Statistician v2.7.38). Teste INDEPENDENTE, date sintetice.

Acoperă: cascadă susținută (multiple swing-uri depășite de un close → toate rup la c), ruptura suprimată-și-
pierdută sub vechea semantică (livrată acum), BOS și CHoCH pe aceeași bară contra referințelor distincte,
ordinea descrescătoare după reference_swing.idx. D2/D7/F3 neschimbate.
"""

from __future__ import annotations

import os
import sys

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from market_structure import (  # noqa: E402
    Block, BreakKind, StructureBreak, StructureLabel, Swing, detect_breaks, detect_swings, label_structure,
)

K = 2


def _base(n: int) -> tuple[list[float], list[float], list[float]]:
    return [100.0] * n, [0.0] * n, [50.0] * n


def _labelled(high: list[float], low: list[float], n: int) -> list[Swing]:
    return label_structure(detect_swings(high, low, [Block(0, n)], k=K))


def _old_detect_breaks(close: list[float], swings: list[Swing], n: int) -> list[StructureBreak]:
    """Semantica VECHE (slot unic live_* + if/elif intra-direcție) — referință pt. a arăta ce s-a schimbat."""
    from market_structure import _mk_break
    out: list[StructureBreak] = []
    consumed: set[int] = set()
    for c in range(n):
        lhh = lll = lhl = llh = None
        for s in swings:
            if s.confirmed_idx >= c or s.idx in consumed:
                continue
            if s.label is StructureLabel.HH:
                lhh = s
            elif s.label is StructureLabel.LL:
                lll = s
            elif s.label is StructureLabel.HL:
                lhl = s
            elif s.label is StructureLabel.LH:
                llh = s
        px = close[c]
        if lhh is not None and px > lhh.price:
            out.append(_mk_break(c, BreakKind.BOS_BULL, lhh, px, 0)); consumed.add(lhh.idx)
        elif llh is not None and px > llh.price:
            out.append(_mk_break(c, BreakKind.CHOCH_BULL, llh, px, 0)); consumed.add(llh.idx)
        if lll is not None and px < lll.price:
            out.append(_mk_break(c, BreakKind.BOS_BEAR, lll, px, 0)); consumed.add(lll.idx)
        elif lhl is not None and px < lhl.price:
            out.append(_mk_break(c, BreakKind.CHOCH_BEAR, lhl, px, 0)); consumed.add(lhl.idx)
    return out


def test_sustained_cascade_all_same_label_break_at_one_bar_descending() -> None:
    """Trei HH active, un singur close le depășește pe toate → TREI BOS_BULL la aceeași bară, ordine descrescătoare."""
    n = 30
    high, low, close = _base(n)
    high[3] = 110.0; high[8] = 120.0; high[13] = 130.0; high[18] = 140.0   # HH@8/13/18 (3=UNCLASSIFIED)
    close[25] = 150.0                                                       # depășește 120, 130, 140 (nu 110)
    br = detect_breaks(close, _labelled(high, low, n), [Block(0, n)])
    at25 = [b for b in br if b.idx == 25]
    assert len(at25) == 3 and all(b.kind is BreakKind.BOS_BULL for b in at25)
    assert [b.reference_swing.idx for b in at25] == [18, 13, 8]             # DESCRESCĂTOR
    # vechea semantică: doar 1 rupere la bara 25 (slot unic → doar cel mai recent HH), restul eșalonate
    old = _old_detect_breaks(close, _labelled(high, low, n), n)
    assert len([b for b in old if b.idx == 25]) == 1


def test_suppressed_choch_lost_under_old_now_delivered() -> None:
    """HH(120) și LH(115) ambele depășite la c=20 (close 125), apoi close cade → sub vechea semantică CHoCH e
    SUPRIMAT și PIERDUT definitiv; sub cascadă apare la 20."""
    n = 26
    high, low, close = _base(n)
    high[3] = 110.0; high[8] = 120.0; high[13] = 115.0        # HH@8 (120), LH@13 (115)
    close[20] = 125.0                                          # depășește ȘI HH ȘI LH
    for c in range(21, n):
        close[c] = 50.0                                        # close cade înapoi — LH nu mai e atins vreodată
    sw = _labelled(high, low, n)
    assert any(s.idx == 13 and s.label is StructureLabel.LH for s in sw)
    new = detect_breaks(close, sw, [Block(0, n)])
    old = _old_detect_breaks(close, sw, n)
    # NEW: LH@13 produce un CHOCH_BULL (la bara 20); OLD: niciodată (suprimat de elif + close cade)
    assert sum(1 for b in new if b.reference_swing.idx == 13) == 1
    assert sum(1 for b in old if b.reference_swing.idx == 13) == 0


def test_bos_and_choch_same_bar_distinct_refs() -> None:
    n = 26
    high, low, close = _base(n)
    high[3] = 110.0; high[8] = 120.0; high[13] = 115.0        # HH@8, LH@13
    close[20] = 125.0
    br = [b for b in detect_breaks(close, _labelled(high, low, n), [Block(0, n)]) if b.idx == 20]
    kinds = {b.kind for b in br}
    assert BreakKind.BOS_BULL in kinds and BreakKind.CHOCH_BULL in kinds       # ambele pe aceeași bară
    assert {b.reference_swing.idx for b in br} == {8, 13}                      # referințe DISTINCTE
    assert br[0].reference_swing.idx == 13                                     # descrescător: LH@13 (mai recent) primul


def test_descending_order_across_kinds() -> None:
    n = 30
    high, low, close = _base(n)
    high[3] = 110.0; high[8] = 120.0; high[13] = 115.0; high[18] = 118.0   # HH@8, LH@13, LH@18 (118<120)
    close[25] = 130.0                                                       # depășește HH(120), LH(115), LH(118)
    at25 = [b for b in detect_breaks(close, _labelled(high, low, n), [Block(0, n)]) if b.idx == 25]
    idxs = [b.reference_swing.idx for b in at25]
    assert idxs == sorted(idxs, reverse=True) and idxs == [18, 13, 8]
