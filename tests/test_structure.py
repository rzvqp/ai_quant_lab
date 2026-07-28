"""Teste mecanice pentru MK-01/MK-02 (market_structure / liquidity_mechanics).

Scrise de Validation Engine pentru a verifica CONFORMITATEA implementării cu cele
șapte decizii ratificate D1-D7 (STAT-MKTSTRUCT-RATIF-PREREG-v1.0). Array-uri
sintetice generate în memorie, fără CSV, fără atingerea datelor reale.

Nota de setup: `code/` NU e pachet (fără __init__.py) și modulele lui importă
absolut (mstrat.py: `from alpha_lab import CFG`). Adăugăm `code/` în sys.path ca să
reproducem modelul de execuție al pipeline-ului — NU reparăm importul absolut din
liquidity_mechanics.py (raportat separat ca observație, nu corectat).
"""

import os
import sys

import pytest

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from market_structure import (  # noqa: E402
    Block,
    StructureLabel,
    SwingKind,
    detect_breaks,
    detect_swings,
    label_structure,
)
from liquidity_mechanics import (  # noqa: E402
    LiquidityPool,
    PoolSide,
    PoolTier,
    detect_sweeps,
)


# ─────────────────────────── D1 — lookahead ────────────────────────────────
def test_D1_swing_cannot_trigger_break_before_idx_plus_k():
    """Nicio rupere nu poate referi un swing la o bară c <= idx+k (confirmed_idx)."""
    k = 2
    # două vârfuri (al doilea = HH), apoi preț care le depășește imediat
    high = [10, 11, 20, 11, 10, 11, 30, 11, 10, 10, 10, 10, 10, 10, 10, 10]
    low = [9, 8, 9, 8, 7, 8, 9, 8, 7, 7, 7, 7, 7, 7, 7, 7]
    close = [10, 10, 15, 12, 11, 12, 25, 31, 32, 33, 34, 35, 36, 37, 38, 39]
    blocks = [Block(0, len(high))]
    swings = label_structure(detect_swings(high, low, blocks, k=k))
    breaks = detect_breaks(close, swings, blocks)
    # invariantul D1: fiecare rupere apare STRICT după confirmarea swing-ului referit
    for br in breaks:
        assert br.idx > br.reference_swing.confirmed_idx, (
            f"rupere la {br.idx} referă swing confirmat la {br.reference_swing.confirmed_idx}")
    # și confirmed_idx == idx + k pentru orice swing
    for s in swings:
        assert s.confirmed_idx == s.idx + k


# ─────────────────────────── D2 — departajare strictă ──────────────────────
def test_D2_tied_maximum_produces_zero_swing():
    """Două bare cu același maxim în fereastră → ZERO swing (inegalitate strictă)."""
    # platou la vârf: high[3]==high[4]==20
    high = [10, 12, 15, 20, 20, 15, 12, 10]
    low = [9, 8, 7, 6, 6, 7, 8, 9]
    blocks = [Block(0, len(high))]
    swings = detect_swings(high, low, blocks, k=2)
    highs = [s for s in swings if s.kind is SwingKind.HIGH]
    assert highs == [], f"un platou nu trebuie să producă swing high, dar a produs {highs}"


def test_D2_unique_peak_produces_one_swing():
    high = [10, 12, 15, 21, 15, 12, 10]
    low = [9, 8, 7, 6, 7, 8, 9]
    blocks = [Block(0, len(high))]
    highs = [s for s in detect_swings(high, low, blocks, k=2) if s.kind is SwingKind.HIGH]
    assert len(highs) == 1 and highs[0].idx == 3


# ─────────────────────────── D3 — reset la graniță ─────────────────────────
def _two_block_series():
    # fiecare bloc: 2 vârfuri (al 2-lea mai înalt) + 2 văi (a 2-a mai joasă)
    seg = [10, 11, 20, 11, 5, 6, 25, 6, 4, 3, 2, 3]  # peaks idx2(20),6(25); troughs idx? build low sep
    high = seg + seg
    low = [5, 4, 5, 4, 1, 2, 3, 2, 0, 1, 2, 1] * 2
    blocks = [Block(0, 12), Block(12, 24)]
    return high, low, blocks


def test_D3_first_swing_of_each_type_per_block_is_unclassified():
    high, low, blocks = _two_block_series()
    swings = label_structure(detect_swings(high, low, blocks, k=2))
    for b_i in (0, 1):
        blk = [s for s in swings if s.block_index == b_i]
        first_high = next((s for s in blk if s.kind is SwingKind.HIGH), None)
        first_low = next((s for s in blk if s.kind is SwingKind.LOW), None)
        if first_high is not None:
            assert first_high.label is StructureLabel.UNCLASSIFIED, f"bloc {b_i} primul high"
        if first_low is not None:
            assert first_low.label is StructureLabel.UNCLASSIFIED, f"bloc {b_i} primul low"
    # bloc 1 nu împrumută referință din bloc 0: primul lui high e tot UNCLASSIFIED
    b1_highs = [s for s in swings if s.block_index == 1 and s.kind is SwingKind.HIGH]
    assert b1_highs and b1_highs[0].label is StructureLabel.UNCLASSIFIED


def test_D3_no_swing_window_crosses_a_block_boundary():
    high, low, blocks = _two_block_series()
    swings = detect_swings(high, low, blocks, k=2)
    for s in swings:
        blk = blocks[s.block_index]
        assert blk.start + 2 <= s.idx < blk.end - 2  # fereastra 2k+1 în bloc


# ─────────────────────────── D4 — bazin nu supraviețuiește graniței ────────
def test_D4_pool_does_not_survive_block_boundary():
    # bazin BELOW format în blocul 0; măturare geometrică apare în blocul 1
    blocks = [Block(0, 10), Block(10, 20)]
    pool = LiquidityPool(price=100.0, formed_idx=3, available_idx=5,
                         side=PoolSide.BELOW, tier=PoolTier.EXTERNAL,
                         block_index=0, source_label=StructureLabel.HL)
    n = 20
    high = [110.0] * n
    low = [105.0] * n
    close = [107.0] * n
    # în blocul 1 (bara 12): low sub 100 și close peste 100 = semnătură wick-sweep
    low[12] = 95.0
    close[12] = 101.0
    sweeps = detect_sweeps(high, low, close, [pool], blocks)
    assert sweeps == [], "un bazin din blocul 0 NU trebuie măturat în blocul 1"


def test_D4_same_pool_swept_inside_its_own_block():
    blocks = [Block(0, 20)]  # un singur bloc — controlul pozitiv
    pool = LiquidityPool(price=100.0, formed_idx=3, available_idx=5,
                         side=PoolSide.BELOW, tier=PoolTier.EXTERNAL,
                         block_index=0, source_label=StructureLabel.HL)
    n = 20
    high, low, close = [110.0] * n, [105.0] * n, [107.0] * n
    low[12] = 95.0
    close[12] = 101.0
    sweeps = detect_sweeps(high, low, close, [pool], blocks)
    assert len(sweeps) == 1 and sweeps[0].idx == 12


# ─────────────────────────── D6 — wick-sweep pe bara curentă ───────────────
def test_D6_sweep_uses_only_current_bar():
    blocks = [Block(0, 10)]
    pool = LiquidityPool(price=100.0, formed_idx=1, available_idx=2,
                         side=PoolSide.BELOW, tier=PoolTier.INTERNAL,
                         block_index=0, source_label=StructureLabel.HL)
    n = 10
    high, low, close = [110.0] * n, [105.0] * n, [107.0] * n
    # bara 5: penetrare + close-back în range → sweep
    low[5] = 90.0
    close[5] = 101.0
    sweeps = detect_sweeps(high, low, close, [pool], blocks)
    assert len(sweeps) == 1 and sweeps[0].idx == 5 and sweeps[0].close_back_inside


def test_D6_penetration_without_close_back_is_not_wick_sweep():
    blocks = [Block(0, 10)]
    pool = LiquidityPool(price=100.0, formed_idx=1, available_idx=2,
                         side=PoolSide.BELOW, tier=PoolTier.INTERNAL,
                         block_index=0, source_label=StructureLabel.HL)
    n = 10
    high, low, close = [110.0] * n, [105.0] * n, [107.0] * n
    low[5] = 90.0
    close[5] = 95.0  # închidere DINCOLO de bazin — rupere, nu wick-sweep
    sweeps = detect_sweeps(high, low, close, [pool], blocks, require_close_back_inside=True)
    assert sweeps == []


# ─────────────────────────── D7 — bazin consumat, fără re-armare ───────────
def test_D7_matured_pool_does_not_rearm():
    blocks = [Block(0, 20)]
    pool = LiquidityPool(price=100.0, formed_idx=1, available_idx=2,
                         side=PoolSide.BELOW, tier=PoolTier.INTERNAL,
                         block_index=0, source_label=StructureLabel.HL)
    n = 20
    high, low, close = [110.0] * n, [105.0] * n, [107.0] * n
    # DOUĂ bare care ambele ar califica ca wick-sweep pe același bazin
    for c in (5, 12):
        low[c] = 90.0
        close[c] = 101.0
    sweeps = [s for s in detect_sweeps(high, low, close, [pool], blocks) if s.pool is pool]
    assert len(sweeps) == 1, f"bazinul maturat nu se re-armează; s-au produs {len(sweeps)} măturări"
    assert sweeps[0].idx == 5  # prima maturare consumă bazinul
