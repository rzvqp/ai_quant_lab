"""Ratificare etapa 2/4 — CUANTIFICAREA costurilor acceptate D2 și D3 (MK-01). Date SINTETICE, fără date reale.

D2 (inegalitate strictă pe ambele laturi) respinge egalitățile: câte swing-uri se pierd față de alternativa
menționată în docstring — „strict la stânga, non-strict la dreapta" (care alege bara din STÂNGA a unui platou).
D3 (reset la graniță de bloc) lasă UNCLASSIFIED primul swing de fiecare tip per bloc: câte se pierd astfel.

Ambele sunt costuri ACCEPTATE (ratificate), dar nemăsurate până acum. NU se ratifică, NU se modifică modulele.
Serii sintetice deterministe (numpy seeded); niciun CSV, nicio atingere a datelor de descoperire.
"""

from __future__ import annotations

import os
import sys
from typing import Any

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from market_structure import Block, StructureLabel, SwingKind, detect_swings, label_structure

K = 2
SEED = 20260730


def _synthetic(n: int, seed: int, grid: float) -> tuple[list[float], list[float]]:
    """Random walk H/L determinist, rotunjit pe o grilă (grid mare → mai multe egalități/platouri)."""
    rng = np.random.default_rng(seed)
    steps = rng.normal(0.0, 1.0, size=n).cumsum()
    mid = 1000.0 + steps
    halfrange = np.abs(rng.normal(0.0, 1.0, size=n)) + 0.5
    high = np.round((mid + halfrange) / grid) * grid
    low = np.round((mid - halfrange) / grid) * grid
    return [float(x) for x in high], [float(x) for x in low]


def _count_predicates(high: list[float], low: list[float], block: Block, k: int) -> tuple[int, int, int, int]:
    """(strict_high, strict_low, semi_high, semi_low) în ACELAȘI loop/confinare ca detect_swings.
    strict = > pe ambele laturi (regula D2 curentă). semi = > la stânga ȘI >= la dreapta (alternativa)."""
    sh = sl = mh = ml = 0
    for i in range(block.start + k, block.end - k):
        if not block.contains_window(i, k):
            continue
        left = range(i - k, i); right = range(i + 1, i + k + 1)
        # regula STRICT (oglindește detect_swings EXACT: is_high; elif is_low)
        if all(high[i] > high[j] for j in left) and all(high[i] > high[j] for j in right):
            sh += 1
        elif all(low[i] < low[j] for j in left) and all(low[i] < low[j] for j in right):
            sl += 1
        # regula SEMI (independentă: strict-stânga, non-strict-dreapta; aceeași prioritate HIGH)
        if all(high[i] > high[j] for j in left) and all(high[i] >= high[j] for j in right):
            mh += 1
        elif all(low[i] < low[j] for j in left) and all(low[i] <= low[j] for j in right):
            ml += 1
    return sh, sl, mh, ml


def quantify_d2() -> dict[str, Any]:
    print("\n########## D2 — pierdere prin respingerea egalităților (strict vs strict-stânga/non-strict-dreapta) ##########")
    out: dict[str, Any] = {}
    for grid in (0.5, 1.0, 2.0):
        n = 30_000
        high, low = _synthetic(n, SEED, grid)
        block = Block(0, n)
        sh, sl, mh, ml = _count_predicates(high, low, block, K)
        strict = sh + sl; semi = mh + ml; lost = semi - strict
        # verificare de coincidență: strict == detect_swings (regula D2 curentă)
        ds = len(detect_swings(high, low, [block], k=K))
        ok = ds == strict
        pct = 100.0 * lost / semi if semi else 0.0
        out[f"grid_{grid}"] = dict(n=n, strict=strict, semi_alt=semi, lost=lost, lost_pct=round(pct, 2),
                                   detect_swings_matches_strict=ok)
        print(f"  grilă={grid:>4}: strict(D2)={strict:5d}  alt(strict-stânga)={semi:5d}  "
              f"PIERDUTE={lost:5d} ({pct:5.2f}% din alt)  [detect_swings==strict: {ok}]")
    return out


def _multiblock_synthetic(block_len: int, n_blocks: int, seed: int, grid: float) -> tuple[list[float], list[float], list[Block]]:
    highs: list[float] = []; lows: list[float] = []; blocks: list[Block] = []
    for b in range(n_blocks):
        h, l = _synthetic(block_len, seed + b, grid)
        start = len(highs)
        highs.extend(h); lows.extend(l)
        blocks.append(Block(start, start + block_len))
    return highs, lows, blocks


def quantify_d3() -> dict[str, Any]:
    print("\n########## D3 — pierdere prin UNCLASSIFIED (primul swing de fiecare tip per bloc) ##########")
    out: dict[str, Any] = {}
    for n_blocks in (4, 8, 16):
        block_len = 4_000
        highs, lows, blocks = _multiblock_synthetic(block_len, n_blocks, SEED, grid=0.25)
        swings = label_structure(detect_swings(highs, lows, blocks, k=K))
        total = len(swings)
        unclassified = sum(1 for s in swings if s.label is StructureLabel.UNCLASSIFIED)
        # verificare: unclassified == Σ blocuri (are ≥1 HIGH) + Σ blocuri (are ≥1 LOW)
        exp = 0
        for b_i in range(n_blocks):
            bs = [s for s in swings if s.block_index == b_i]
            exp += (1 if any(s.kind is SwingKind.HIGH for s in bs) else 0)
            exp += (1 if any(s.kind is SwingKind.LOW for s in bs) else 0)
        pct = 100.0 * unclassified / total if total else 0.0
        out[f"blocks_{n_blocks}"] = dict(n_blocks=n_blocks, total_swings=total, unclassified_lost=unclassified,
                                         expected_2_per_block=exp, matches=unclassified == exp,
                                         lost_pct=round(pct, 3))
        print(f"  {n_blocks:2d} blocuri × {block_len}: swing-uri={total:5d}  UNCLASSIFIED(pierdute)={unclassified:3d} "
              f"(≈{unclassified/n_blocks:.2f}/bloc, aștept {exp})  {pct:.3f}% din total")
    print("  (D3 = cost FIX ≈ 2 swing-uri/bloc — 1 primul HIGH + 1 primul LOW — deci % scade cu densitatea de swing-uri)")
    return out


def main() -> int:
    print(f"MK-01 costuri D2/D3 pe date SINTETICE (seed={SEED}, k={K}) — fără date reale")
    d2 = quantify_d2()
    d3 = quantify_d3()
    print("\n=== REZUMAT ===")
    print(f"  D2: pierdere = {[v['lost'] for v in d2.values()]} swing-uri (grile 0.5/1.0/2.0); crește cu frecvența egalităților.")
    print(f"  D3: pierdere = {[v['unclassified_lost'] for v in d3.values()]} swing-uri (4/8/16 blocuri) = ~2/bloc, cost fix.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
