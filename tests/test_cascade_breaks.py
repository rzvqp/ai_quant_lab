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
    Block, BreakKind, StructureBreak, StructureLabel, Swing, SwingKind, detect_breaks, detect_swings,
    label_structure,
)

K = 2
_HIGH_LABELS = (StructureLabel.HH, StructureLabel.LH)
_LOW_LABELS = (StructureLabel.LL, StructureLabel.HL)


def _sw(idx: int, confirmed: int, price: float, label: StructureLabel) -> Swing:
    kind = SwingKind.HIGH if label in _HIGH_LABELS else SwingKind.LOW
    return Swing(idx=idx, confirmed_idx=confirmed, price=price, kind=kind, label=label, block_index=0)


def _ever_exceeded(s: Swing, close: list[float], n: int) -> bool:
    for j in range(s.confirmed_idx + 1, n):
        if s.label in _HIGH_LABELS and close[j] > s.price:
            return True
        if s.label in _LOW_LABELS and close[j] < s.price:
            return True
    return False


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


# ── SARCINA 2 (v2.7.39): cele patru teste lipsă semnalate de Red Team ──
def test_reference_selection_invariant_descending_is_load_bearing() -> None:
    """Ordinea descrescătoare e PORTANTĂ, nu cosmetică: consumatorul (prima din listă la idx egal) primește
    referința cu idx MAXIM = exact ce alegea slot-unic vechi (cel mai recent). Ascendent ar referi ALT nivel."""
    n = 30
    high, low, close = _base(n)
    high[3] = 110.0; high[8] = 120.0; high[13] = 130.0; high[18] = 140.0
    close[25] = 150.0
    at25 = [b for b in detect_breaks(close, _labelled(high, low, n), [Block(0, n)]) if b.idx == 25]
    idxs = [b.reference_swing.idx for b in at25]
    assert idxs == [18, 13, 8]                                   # DESCRESCĂTOR — invariant impus
    assert at25[0].reference_swing.idx == max(idxs)             # primul = cel mai recent (ca slot-unic vechi)
    assert at25[0].reference_swing.idx != min(idxs)             # ascendent ar da altă referință → ordinea CONTEAZĂ


def test_aggregate_conservation_each_exceeded_swing_breaks_exactly_once() -> None:
    """Conservare agregată (invariantul pe care vechiul bug îl încălca): fiecare swing depășit produce EXACT o
    rupere, toate referințele unice, mulțimea rupturilor = mulțimea swing-urilor depășite. Vechea semantică o încalcă."""
    n = 26
    high, low, close = _base(n)
    high[3] = 110.0; high[8] = 120.0; high[13] = 115.0          # HH@8, LH@13
    close[20] = 125.0                                            # depășește ambele
    for c in range(21, n):
        close[c] = 50.0                                          # close cade → LH pierdut sub vechea semantică
    sw = _labelled(high, low, n)
    new_refs = [b.reference_swing.idx for b in detect_breaks(close, sw, [Block(0, n)])]
    exceeded = {s.idx for s in sw if s.label is not StructureLabel.UNCLASSIFIED and _ever_exceeded(s, close, n)}
    assert len(new_refs) == len(set(new_refs))                  # niciun swing rupt de două ori
    assert set(new_refs) == exceeded                            # conservare: TOATE cele depășite, doar ele
    old_refs = {b.reference_swing.idx for b in _old_detect_breaks(close, sw, n)}
    assert len(old_refs) < len(exceeded)                        # vechea semantică ÎNCĂLCA conservarea (a pierdut)


def test_f4_opposite_simultaneous_breaks_distinct_refs() -> None:
    """F4: pe o structură inversată (high-swing sub low-swing), un close intermediar rupe SIMULTAN bullish ȘI
    bearish, contra referințelor distincte. Ordine descrescătoare după idx."""
    n = 20
    close = [50.0] * n
    # confirmed_idx=11 pt. AMBELE → active abia de la bara 12 (nicio bară anterioară nu le poate rupe separat;
    # orice close ∈(90,100) rupe simultan ambele, iar <=90 / >=100 ar rupe doar una — deci prima bară activă)
    swings = [_sw(3, 11, 90.0, StructureLabel.HH), _sw(8, 11, 100.0, StructureLabel.HL)]   # HH 90 < HL 100
    close[12] = 95.0                                             # 95>90 (BOS_BULL) ȘI 95<100 (CHOCH_BEAR)
    br = [b for b in detect_breaks(close, swings, [Block(0, n)]) if b.idx == 12]
    assert {b.kind for b in br} == {BreakKind.BOS_BULL, BreakKind.CHOCH_BEAR}   # opuse simultane
    assert {b.reference_swing.idx for b in br} == {3, 8}                        # referințe distincte
    assert br[0].reference_swing.idx == 8                                       # descrescător: HL@8 primul


def test_high_multiplicity_ten_breaks_one_bar_descending_unique() -> None:
    """Multiplicitate mare: 10 swing-uri active depășite de un singur close → 10 rupturi pe aceeași bară
    (măsurătoarea a găsit până la 24; testele foloseau maxim 3)."""
    n = 40
    close = [50.0] * n
    swings = [_sw(2 * i, 2 * i + 1, 100.0 + i, StructureLabel.HH) for i in range(1, 11)]   # idx 2..20
    close[30] = 1000.0
    at30 = [b for b in detect_breaks(close, swings, [Block(0, n)]) if b.idx == 30]
    idxs = [b.reference_swing.idx for b in at30]
    assert len(at30) == 10 and all(b.kind is BreakKind.BOS_BULL for b in at30)
    assert idxs == sorted(idxs, reverse=True) == [20, 18, 16, 14, 12, 10, 8, 6, 4, 2]
    assert len(set(idxs)) == 10
