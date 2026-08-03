"""Remediere F2 (breakout menținut → o rupere per referință) + F3 (precondiție de ordonare, fail-closed)
în detect_breaks. Teste de regresie + edge cases, INDEPENDENTE (fixtures noi). Doar date sintetice.

F2: verificat empiric că filtrul upstream `consumed` (Mandat 5.2) satisface deja toate cele 7 criterii —
aceste teste sunt gardul de regresie explicit cerut. F3: nou, impus mecanic aici.
"""

from __future__ import annotations

import os
import sys

import pytest

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from market_structure import (  # noqa: E402
    Block, BreakKind, StructureBreak, StructureLabel, Swing, SwingKind, detect_breaks, detect_swings,
    label_structure,
)

K = 2
BASE_H, BASE_L, BASE_C = 100.0, 0.0, 50.0


def _base(n: int) -> tuple[list[float], list[float], list[float]]:
    return [BASE_H] * n, [BASE_L] * n, [BASE_C] * n


def _pipeline_breaks(high: list[float], low: list[float], close: list[float], blocks: list[Block]) -> list[StructureBreak]:
    return detect_breaks(close, label_structure(detect_swings(high, low, blocks, k=K)), blocks)


# ───────────────────────────── F2 criterii ─────────────────────────────
def test_c1_c7_sustained_breakout_single_bos_ref7() -> None:
    """Criteriile 1 & 7 (regresie explicită): breakout menținut pe barele 10-14 peste ref idx=7 → UN BOS_BULL."""
    n = 20
    high, low, close = _base(n)
    high[2] = 110.0                          # primul HIGH → UNCLASSIFIED (fără referință)
    high[7] = 120.0                          # al doilea HIGH → HH, confirmed_idx = 9
    for c in (10, 11, 12, 13, 14):
        close[c] = 130.0                     # breakout MENȚINUT
    br = _pipeline_breaks(high, low, close, [Block(0, n)])
    bos = [b for b in br if b.kind is BreakKind.BOS_BULL]
    assert len(bos) == 1
    assert bos[0].idx == 10 and bos[0].reference_swing.idx == 7
    assert [b.reference_swing.idx for b in br].count(7) == 1     # ref 7 consumat exact o dată


def test_c2_consumed_reference_not_reactivated() -> None:
    """Criteriul 2: după consumare, ref-ul NU se reactivează, chiar dacă prețul rămâne deasupra 20 de bare."""
    n = 40
    high, low, close = _base(n)
    high[2] = 110.0; high[7] = 120.0         # HH@7
    for c in range(10, 40):
        close[c] = 130.0                     # deasupra pe TOT restul blocului
    br = _pipeline_breaks(high, low, close, [Block(0, n)])
    assert sum(1 for b in br if b.reference_swing.idx == 7) == 1


def test_c3_new_later_swing_produces_own_break() -> None:
    """Criteriul 3: un swing NOU, confirmat ulterior, cu index distinct, produce PROPRIA rupere."""
    n = 30
    high, low, close = _base(n)
    high[2] = 110.0; high[7] = 120.0         # HH@7 conf9
    high[15] = 125.0; high[20] = 140.0       # HH@15 (125) conf17, HH@20 (140) conf22
    close[10] = 130.0                        # rupe ref7
    close[24] = 150.0                        # rupe ref20 (cel mai recent HH neconsumat)
    br = _pipeline_breaks(high, low, close, [Block(0, n)])
    refs = sorted((b.idx, b.reference_swing.idx) for b in br if b.kind is BreakKind.BOS_BULL)
    assert (10, 7) in refs and (24, 20) in refs
    assert all(b.reference_swing.idx != b2.reference_swing.idx or b is b2 for b in br for b2 in br)  # refs distincte


def test_c4_bull_bear_symmetric() -> None:
    """Criteriul 4: simetrie — breakout descendent menținut → UN BOS_BEAR."""
    n = 20
    high, low, close = _base(n)
    low[2] = -10.0                           # primul LOW → UNCLASSIFIED
    low[7] = -20.0                           # LL confirmed 9
    for c in (10, 11, 12, 13, 14):
        close[c] = -30.0
    br = _pipeline_breaks(high, low, close, [Block(0, n)])
    bos = [b for b in br if b.kind is BreakKind.BOS_BEAR]
    assert len(bos) == 1 and bos[0].idx == 10 and bos[0].reference_swing.idx == 7


def test_c5_block_boundary_reset_independent_breaks() -> None:
    """Criteriul 5: fiecare bloc procesat independent (consumed resetat per bloc) → o rupere per bloc."""
    n = 32
    blocks = [Block(0, 16), Block(16, 32)]
    high, low, close = _base(n)
    high[2] = 110.0; high[7] = 120.0         # bloc 0: HH@7
    high[18] = 110.0; high[23] = 120.0       # bloc 1: HH@23
    for c in (10, 11, 12):
        close[c] = 130.0
    for c in (26, 27, 28):
        close[c] = 130.0
    br = _pipeline_breaks(high, low, close, blocks)
    bos = [b for b in br if b.kind is BreakKind.BOS_BULL]
    assert len(bos) == 2
    assert {(b.block_index, b.reference_swing.idx) for b in bos} == {(0, 7), (1, 23)}


def test_c6_no_lookahead_future_mutation_preserves_earlier_breaks() -> None:
    """Criteriul 6: rescrierea barelor viitoare (>C) nu schimbă ruperile cu idx <= C."""
    n = 30
    high, low, close = _base(n)
    high[2] = 110.0; high[7] = 120.0
    close[10] = 130.0                        # BOS ref7 @10
    blocks = [Block(0, n)]
    ref = [(b.idx, b.kind.value, b.reference_swing.idx) for b in _pipeline_breaks(high, low, close, blocks)]
    C = 10
    hi2, lo2, cl2 = list(high), list(low), list(close)
    for j in range(C + 1, n):
        hi2[j] = 100.0 + (j % 5) * 9.0; lo2[j] = -(j % 4) * 7.0; cl2[j] = 20.0 + (j % 6) * 11.0
    mut = [(b.idx, b.kind.value, b.reference_swing.idx) for b in _pipeline_breaks(hi2, lo2, cl2, blocks)]
    assert [e for e in ref if e[0] <= C] == [e for e in mut if e[0] <= C]


# ───────────────────────────── F3 precondiție de ordonare, fail-closed ─────────────────────────────
def _swing(idx: int, confirmed_idx: int, price: float, label: StructureLabel) -> Swing:
    return Swing(idx=idx, confirmed_idx=confirmed_idx, price=price,
                 kind=SwingKind.HIGH, label=label, block_index=0)


def test_f3_valid_ordered_input_does_not_raise() -> None:
    n = 20
    _, _, close = _base(n)
    swings = [_swing(3, 5, 110.0, StructureLabel.UNCLASSIFIED), _swing(7, 9, 120.0, StructureLabel.HH)]
    detect_breaks(close, swings, [Block(0, n)])   # nu ridică


def test_f3_temporal_disorder_raises() -> None:
    close = _base(20)[2]
    swings = [_swing(7, 9, 120.0, StructureLabel.HH), _swing(3, 5, 110.0, StructureLabel.HH)]  # idx descrescător
    with pytest.raises(ValueError, match="F3"):
        detect_breaks(close, swings, [Block(0, 20)])


def test_f3_duplicate_idx_raises() -> None:
    close = _base(20)[2]
    swings = [_swing(7, 9, 120.0, StructureLabel.HH), _swing(7, 9, 121.0, StructureLabel.HH)]  # idx duplicat
    with pytest.raises(ValueError, match="F3"):
        detect_breaks(close, swings, [Block(0, 20)])


def test_f3_nonmonotonic_confirmed_idx_raises() -> None:
    close = _base(20)[2]
    swings = [_swing(3, 12, 110.0, StructureLabel.HH), _swing(7, 9, 120.0, StructureLabel.HH)]  # confirmed scade
    with pytest.raises(ValueError, match="F3"):
        detect_breaks(close, swings, [Block(0, 20)])


def test_f3_confirmed_before_extremum_raises() -> None:
    close = _base(20)[2]
    swings = [_swing(7, 5, 120.0, StructureLabel.HH)]         # confirmed_idx < idx
    with pytest.raises(ValueError, match="F3"):
        detect_breaks(close, swings, [Block(0, 20)])


# ── F3 extins la label_structure (Red Team) — ordonarea impusă și AICI ──
def test_f3_label_structure_valid_ordered_input_does_not_raise() -> None:
    label_structure([_swing(3, 5, 110.0, StructureLabel.UNCLASSIFIED),
                     _swing(7, 9, 120.0, StructureLabel.UNCLASSIFIED)])   # nu ridică


def test_f3_label_structure_temporal_disorder_raises() -> None:
    with pytest.raises(ValueError, match="F3"):
        label_structure([_swing(7, 9, 120.0, StructureLabel.UNCLASSIFIED),
                         _swing(3, 5, 110.0, StructureLabel.UNCLASSIFIED)])   # idx descrescător


def test_f3_label_structure_duplicate_idx_raises() -> None:
    with pytest.raises(ValueError, match="F3"):
        label_structure([_swing(7, 9, 120.0, StructureLabel.UNCLASSIFIED),
                         _swing(7, 9, 121.0, StructureLabel.UNCLASSIFIED)])   # idx duplicat
