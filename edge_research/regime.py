"""CAUSAL REGIME CLASSIFIER (research-only, Flow B) — for the regime×family loop.

The regime PREDICATE is the causal, lookahead-safe part of a strategy's identity. RANGE is BLOCKED
(TRUE_RANGE_NOT_IDENTIFIABLE), so we classify only the regimes that ARE causally identifiable from
ratified primitives:

  TREND_UP / TREND_DOWN  — from the MK-01 swing structure (label_structure): the most recent CONFIRMED
                           HIGH swing is HH and the most recent CONFIRMED LOW swing is HL  -> TREND_UP;
                           LH + LL -> TREND_DOWN; anything mixed/insufficient -> NONE (not eligible).
                           Uses only swings with confirmed_idx <= bar  => NO LOOKAHEAD. This is exactly
                           the bootstrapping detect_breaks uses (HH+HL='up', LH+LL='down').
  COMPRESSION            — market_state: atr14 < 0.8 * rolling50(atr14) (causal, measurable).
  BREAKOUT_TRANSITION    — a body break of structure (detect_breaks BOS) marks the transition bar.

This module does NOT modify N1-N6 or the Router; it is a research-only predicate computed from the
ratified detectors so Flow-A hypotheses can be regime-scoped and pre-registered. When the lab's N1 is
consumable, the eligibility predicate is swapped to N1 at the source (identity/run_hash change = a NEW
hypothesis).
"""
from __future__ import annotations
import os, sys
import numpy as np, pandas as pd
for _c in [os.environ.get("RATIFIED_CODE_DIR"),
           r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\44ba92ba-04ad-40f2-a48e-0ee6a8aca893\scratchpad\ratified_code\code"]:
    if _c and os.path.isdir(_c):
        if _c not in sys.path:
            sys.path.insert(0, _c)
        break
from market_structure import detect_swings, label_structure, SwingKind, StructureLabel

UP = "TREND_UP"; DOWN = "TREND_DOWN"; NONE = "NONE"


def trend_regime(high, low, blocks, k: int = 2):
    """Per-bar causal trend regime array (len n) of {TREND_UP, TREND_DOWN, NONE}. No lookahead:
    at bar j only swings with confirmed_idx <= j are used."""
    n = len(high)
    swings = label_structure(detect_swings(high, low, blocks, k))
    # events at the bar they become known (confirmed_idx), split by kind
    ev = sorted(((s.confirmed_idx, s.kind, s.label) for s in swings), key=lambda x: x[0])
    reg = [NONE] * n
    last_high = None; last_low = None; ptr = 0
    for j in range(n):
        while ptr < len(ev) and ev[ptr][0] <= j:
            _, kind, label = ev[ptr]
            if kind is SwingKind.HIGH:
                last_high = label
            else:
                last_low = label
            ptr += 1
        if last_high is StructureLabel.HH and last_low is StructureLabel.HL:
            reg[j] = UP
        elif last_high is StructureLabel.LH and last_low is StructureLabel.LL:
            reg[j] = DOWN
    return reg


def episodes(regime_arr, target):
    """Contiguous runs of `target` regime -> list of (start, end) half-open. An 'episode' = one
    continuous stretch of the eligible regime (the unit for the >=5-episode falsification gate)."""
    out = []
    i = 0; n = len(regime_arr)
    while i < n:
        if regime_arr[i] == target:
            j = i
            while j < n and regime_arr[j] == target:
                j += 1
            out.append((i, j)); i = j
        else:
            i += 1
    return out


def last_swing_levels(high, low, blocks, k: int = 2):
    """Per-bar (last_confirmed_swing_high_price, last_confirmed_swing_low_price). Lookahead-safe:
    a swing is known only at confirmed_idx. Used for WIDE structural stops (a swing extreme, not the
    immediate bar low) — the CAND-0037 lesson that a large stop is cost/fat-tail robust."""
    n = len(high)
    swings = detect_swings(high, low, blocks, k)
    ev = sorted(((s.confirmed_idx, s.kind, s.price) for s in swings), key=lambda x: x[0])
    hi_lvl = [float("nan")] * n; lo_lvl = [float("nan")] * n
    lh = float("nan"); ll = float("nan"); ptr = 0
    for j in range(n):
        while ptr < len(ev) and ev[ptr][0] <= j:
            _, kind, price = ev[ptr]
            if kind is SwingKind.HIGH:
                lh = price
            else:
                ll = price
            ptr += 1
        hi_lvl[j] = lh; lo_lvl[j] = ll
    return hi_lvl, lo_lvl


def compression_flags(atr14):
    """Causal COMPRESSION predicate: atr14 < 0.8 * rolling50(atr14)."""
    atr = np.asarray(atr14, float)
    ma = pd.Series(atr).rolling(50).mean().to_numpy()
    return (atr < 0.8 * ma)
