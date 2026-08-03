"""Ratificare etapa 2/4 — EXECUTABILITATE + leakage pentru market_structure (MK-01) și liquidity_mechanics
(MK-02). Teste INDEPENDENTE (fixtures noi, valori așteptate derivate manual de la zero — NU reutilizează
tests/test_structure.py sau alte teste existente, care împart presupunerile implementării). Doar date
sintetice în memorie; fără CSV, fără date reale. NU se ratifică (decizia e a CEO după Red Team); NU se
modifică modulele. Acoperă D1-D7 + anti-lookahead + D3-la-fiecare-graniță + D7-nu-blochează-ulterioarele.

Contract forward-safe verificat: detect_swings expune confirmed_idx=idx+k; consumatorii (detect_breaks,
build_pools, detect_sweeps) folosesc confirmed_idx/available_idx STRICT înainte de bara curentă.
"""

from __future__ import annotations

import os
import sys

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from market_structure import (  # noqa: E402
    Block, BreakKind, StructureLabel, SwingKind, detect_breaks, detect_swings, label_structure,
)
from liquidity_mechanics import (  # noqa: E402
    LiquidityPool, PoolSide, PoolTier, build_pools, detect_sweeps,
)

K = 2
BASE_H, BASE_L, BASE_C = 100.0, 0.0, 50.0


def _base(n: int) -> tuple[list[float], list[float], list[float]]:
    return [BASE_H] * n, [BASE_L] * n, [BASE_C] * n


def _hi_spike(high: list[float], i: int, v: float) -> None:
    high[i] = v                      # v > BASE_H → swing HIGH unic la i (vecinii = BASE_H)


def _lo_spike(low: list[float], i: int, v: float) -> None:
    low[i] = v                       # v < BASE_L → swing LOW unic la i


# ───────────────────────────── D1 — lookahead / confirmed_idx ─────────────────────────────
def test_d1_confirmed_idx_equals_idx_plus_k() -> None:
    high, low, _ = _base(7)
    _hi_spike(high, 3, 110.0)
    sw = detect_swings(high, low, [Block(0, 7)], k=K)
    assert len(sw) == 1
    s = sw[0]
    assert s.idx == 3 and s.confirmed_idx == 3 + K and s.kind is SwingKind.HIGH and s.price == 110.0


def test_d1_break_cannot_fire_before_reference_confirmed() -> None:
    """HH confirmat la idx 10; un close deasupra la c=10 (==confirmed) NU rupe; la c=12 (>confirmed) rupe."""
    n = 16
    high, low, close = _base(n)
    _hi_spike(high, 3, 110.0)                 # primul HIGH → UNCLASSIFIED
    _hi_spike(high, 8, 120.0)                 # al doilea HIGH, mai sus → HH, confirmed_idx = 10
    close[10] = 130.0                         # c == confirmed_idx(10): referința NU e încă live
    close[12] = 130.0                         # c  > confirmed_idx: live → rupere
    swings = label_structure(detect_swings(high, low, [Block(0, n)], k=K))
    hh = [s for s in swings if s.label is StructureLabel.HH]
    assert len(hh) == 1 and hh[0].idx == 8 and hh[0].confirmed_idx == 10
    breaks = detect_breaks(close, swings, [Block(0, n)])
    assert len(breaks) == 1
    assert breaks[0].idx == 12 and breaks[0].kind is BreakKind.BOS_BULL and breaks[0].reference_swing.idx == 8


# ───────────────────────────── D2 — inegalitate strictă respinge egalitățile ─────────────────────────────
def test_d2_unique_top_yields_swing_but_flat_top_does_not() -> None:
    high_u, low_u, _ = _base(7)
    _hi_spike(high_u, 3, 110.0)               # vârf UNIC → 1 swing
    assert len([s for s in detect_swings(high_u, low_u, [Block(0, 7)], k=K) if s.kind is SwingKind.HIGH]) == 1

    high_f, low_f, _ = _base(8)
    _hi_spike(high_f, 3, 110.0)
    _hi_spike(high_f, 4, 110.0)               # platou (egalitate) → strict pe ambele laturi respinge AMBELE
    assert len([s for s in detect_swings(high_f, low_f, [Block(0, 8)], k=K) if s.kind is SwingKind.HIGH]) == 0


# ───────────────────────────── D3 — reset la FIECARE graniță de bloc ─────────────────────────────
def test_d3_first_swing_of_each_type_unclassified_every_block() -> None:
    n = 48
    blocks = [Block(0, 16), Block(16, 32), Block(32, 48)]
    high, low, _ = _base(n)
    for b in (0, 16, 32):                     # per bloc: primul HIGH (mai jos) + al doilea HIGH (mai sus)
        _hi_spike(high, b + 3, 110.0)
        _hi_spike(high, b + 8, 120.0)
    swings = label_structure(detect_swings(high, low, blocks, k=K))
    firsts = [s for s in swings if s.idx in (3, 19, 35)]
    seconds = [s for s in swings if s.idx in (8, 24, 40)]
    assert len(firsts) == 3 and all(s.label is StructureLabel.UNCLASSIFIED for s in firsts)  # NEmoștenit între blocuri
    assert len(seconds) == 3 and all(s.label is StructureLabel.HH for s in seconds)


def test_d3_window_may_not_cross_block_boundary() -> None:
    n = 16
    high, low, _ = _base(n)
    _hi_spike(high, 14, 110.0)                # i+k = 16 = block.end → fereastra iese din bloc → exclus
    _hi_spike(high, 15, 111.0)
    assert detect_swings(high, low, [Block(0, n)], k=K) == []


# ───────────────────────────── D4 — bazinul NU supraviețuiește unei granițe de bloc ─────────────────────────────
def _below_pool(price: float, available_idx: int, block_index: int) -> LiquidityPool:
    return LiquidityPool(price=price, formed_idx=available_idx - K, available_idx=available_idx,
                         side=PoolSide.BELOW, tier=PoolTier.EXTERNAL, block_index=block_index,
                         source_label=StructureLabel.LL)


def test_d4_pool_not_swept_outside_its_block() -> None:
    blocks = [Block(0, 16), Block(16, 32)]
    n = 32
    high, low, close = _base(n)
    pool = _below_pool(price=-20.0, available_idx=8, block_index=0)   # bazin în blocul 0
    low[20] = -30.0; close[20] = 50.0                                # semnătură perfectă, dar în blocul 1
    assert detect_sweeps(high, low, close, [pool], blocks) == []      # inactiv în afara blocului 0
    # control: aceeași semnătură în blocul 0 (c=12 > available_idx) → se declanșează
    low2 = list(low); close2 = list(close)
    low2[12] = -30.0; close2[12] = 50.0
    ev = detect_sweeps(high, low2, close2, [pool], blocks)
    assert len(ev) == 1 and ev[0].idx == 12


# ───────────────────────────── D6 — sweep evaluat integral pe bara curentă (fără lookahead) ─────────────────────────────
def test_d6_sweep_requires_both_conditions_on_the_same_bar() -> None:
    n = 12
    high, low, close = _base(n)
    pool = _below_pool(price=-20.0, available_idx=3, block_index=0)
    low[5] = -30.0; close[5] = 50.0          # penetrare ȘI close înapoi, pe ACEEAȘI bară → sweep
    low[7] = -30.0; close[7] = -25.0         # penetrare dar close DEDESUBT (fără back-inside) → fără sweep
    ev = detect_sweeps(high, low, close, [pool], [Block(0, n)])
    assert len(ev) == 1
    assert ev[0].idx == 5 and ev[0].close_back_inside is True and ev[0].penetration == -20.0 - (-30.0)


def test_d6_split_conditions_across_two_bars_do_not_sweep() -> None:
    n = 12
    high, low, close = _base(n)
    pool = _below_pool(price=-20.0, available_idx=3, block_index=0)
    low[5] = -30.0; close[5] = -25.0         # doar penetrare (close sub) — fără back-inside
    low[6] = -10.0; close[6] = 50.0          # doar close deasupra — fără penetrare
    assert detect_sweeps(high, low, close, [pool], [Block(0, n)]) == []


# ───────────────────────────── D7 — consumare o dată, dar NU blochează bazinele ulterioare ─────────────────────────────
def test_d7_pool_consumed_once() -> None:
    n = 20
    high, low, close = _base(n)
    pool = _below_pool(price=-20.0, available_idx=3, block_index=0)
    for c in (5, 10):                        # două bare care ambele mătură același bazin
        low[c] = -30.0; close[c] = 50.0
    ev = detect_sweeps(high, low, close, [pool], [Block(0, n)])
    assert len(ev) == 1 and ev[0].idx == 5   # consumat la prima; a doua nu re-declanșează


def test_d7_consumption_does_not_block_later_distinct_pools() -> None:
    n = 20
    high, low, close = _base(n)
    p1 = _below_pool(price=-20.0, available_idx=3, block_index=0)
    p2 = _below_pool(price=-40.0, available_idx=3, block_index=0)
    low[5] = -30.0; close[5] = 50.0          # mătură p1 (nu p2: low -30 nu penetrează -40)
    low[10] = -50.0; close[10] = 50.0        # mătură p2 (și ar re-mătura p1, dar p1 e consumat)
    ev = sorted(detect_sweeps(high, low, close, [p1, p2], [Block(0, n)]), key=lambda e: e.idx)
    assert len(ev) == 2
    assert ev[0].idx == 5 and ev[0].pool.price == -20.0
    assert ev[1].idx == 10 and ev[1].pool.price == -40.0


# ───────────────────────────── D5 — agnostic la timeframe; fără mapare M5→M15 ─────────────────────────────
def test_d5_timeframe_agnostic_and_no_cross_tf_mapping() -> None:
    import liquidity_mechanics as lm
    # (a) fără artefact de aliniere cross-timeframe expus
    for banned in ("align_m5_to_m15", "map_m5_to_m15", "align", "resample"):
        assert not hasattr(lm, banned)
    # (b) pur index-based: aceleași array-uri + blocuri → același rezultat, indiferent de „sensul" barelor
    n = 12
    high, low, close = _base(n)
    pool = _below_pool(price=-20.0, available_idx=3, block_index=0)
    low[5] = -30.0; close[5] = 50.0
    a = detect_sweeps(high, low, close, [pool], [Block(0, n)])
    b = detect_sweeps(list(high), list(low), list(close), [pool], [Block(0, n)])
    assert [e.idx for e in a] == [e.idx for e in b] == [5]


# ───────────────────────────── Anti-lookahead: mutarea barelor VIITOARE nu schimbă evenimentele ANTERIOARE ─────────────────────────────
_LBL = {StructureLabel.UNCLASSIFIED: 0, StructureLabel.HH: 1, StructureLabel.HL: 2,
        StructureLabel.LH: 3, StructureLabel.LL: 4}
_BRK = {BreakKind.BOS_BULL: 1, BreakKind.BOS_BEAR: 2, BreakKind.CHOCH_BULL: 3, BreakKind.CHOCH_BEAR: 4}


def _pipeline(high: list[float], low: list[float], close: list[float], block: Block) -> dict[str, list[tuple[int, ...]]]:
    """Toate câmpurile codificate ca int (tuple omogen), ca invariantul anti-lookahead să se compare exact."""
    swings = label_structure(detect_swings(high, low, [block], k=K))
    breaks = detect_breaks(close, swings, [block])
    pools = build_pools(swings, PoolTier.EXTERNAL)
    sweeps = detect_sweeps(high, low, close, pools, [block])
    return {
        "swings": [(s.idx, s.confirmed_idx, int(s.price), 1 if s.kind is SwingKind.HIGH else 0, _LBL[s.label])
                   for s in swings],
        "breaks": [(b.idx, _BRK[b.kind]) for b in breaks],
        "pools": [(p.formed_idx, p.available_idx, int(p.price), 1 if p.side is PoolSide.ABOVE else 0) for p in pools],
        "sweeps": [(e.idx, int(e.pool.price)) for e in sweeps],
    }


def test_anti_lookahead_future_mutation_preserves_past_events() -> None:
    n = 30
    high, low, close = _base(n)
    _hi_spike(high, 3, 110.0)
    _hi_spike(high, 9, 120.0)                 # HH confirmed 11
    _lo_spike(low, 6, -10.0)
    _lo_spike(low, 12, -20.0)                 # LL confirmed 14 → bazin BELOW
    close[16] = 130.0                         # BOS_BULL peste HH (c=16 > 11)
    low[18] = -30.0; close[18] = 50.0         # sweep al bazinului LL (c=18 > available 14)
    block = Block(0, n)
    ref = _pipeline(high, low, close, block)

    C = 14                                    # tot ce e cunoscut la <= 14: swing3(conf5), swing9(conf11), low6(conf8), low12(conf14)

    def known_at(kind: str, ev: tuple[int, ...]) -> int:
        return ev[1] if kind in ("swings", "pools") else ev[0]   # confirmed/available pt swings/pools; idx altfel

    def filt(d: dict[str, list[tuple[int, ...]]]) -> dict[str, list[tuple[int, ...]]]:
        return {k: sorted(e for e in v if known_at(k, e) <= C) for k, v in d.items()}

    hi2, lo2, cl2 = list(high), list(low), list(close)
    for j in range(C + 1, n):                 # rescrie ARBITRAR toate barele viitoare
        hi2[j] = 100.0 + (j % 7) * 13.0; lo2[j] = -(j % 5) * 11.0; cl2[j] = 20.0 + (j % 9) * 7.0
    mut = _pipeline(hi2, lo2, cl2, block)

    assert filt(ref) == filt(mut)             # evenimentele cunoscute la <= C sunt IDENTICE
