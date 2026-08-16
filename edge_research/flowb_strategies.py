"""FLOW B — STRATEGY LIBRARY (research-only). Cards (pre-registered) + signal builders keyed by id.

Each builder: build(ctx) -> (list[Trade], eligibility_arr). `eligibility_arr` is the per-bar causal
regime the candidate REQUIRES (contiguous runs = 'episodes' for the >=5 gate). Signal fires ONLY where
eligible (regime is part of identity). Logic is SEPARATE from the evaluator. RANGE families are absent
(BLOCKED). Widening a stop = a NEW id (never a 'repair' of an old result; OOS never used to pick it).
"""
from __future__ import annotations
import os, sys
import numpy as np
for _c in [os.environ.get("RATIFIED_CODE_DIR"),
           r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\44ba92ba-04ad-40f2-a48e-0ee6a8aca893\scratchpad\ratified_code\code"]:
    if _c and os.path.isdir(_c):
        if _c not in sys.path:
            sys.path.insert(0, _c)
        break
from edge_research._screen import Trade
from edge_research.regime import trend_regime, last_swing_levels, compression_flags, UP, DOWN
from market_structure import detect_swings, label_structure, detect_breaks, BreakKind
from market_state import expansion

HOLD = 20; HOLD_L = 40


_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "loop_state")


class Ctx:
    def __init__(self, d, blocks):
        self.d = d; self.blocks = blocks
        self.o = d["open"].to_numpy(); self.h = d["high"].to_numpy()
        self.l = d["low"].to_numpy(); self.c = d["close"].to_numpy()
        self.atr = d["atr14"].to_numpy(); self.n = len(d)
        # cache the heavy regime/swing computation keyed by (n, first/last time) so restarts are fast
        os.makedirs(_CACHE_DIR, exist_ok=True)
        key = f"{self.n}_{int(d['time'].iloc[0])}_{int(d['time'].iloc[-1])}"
        cache = os.path.join(_CACHE_DIR, f"ctx_{key}.npz")
        if os.path.exists(cache):
            z = np.load(cache, allow_pickle=True)
            self.reg = list(z["reg"]); self.sh = list(z["sh"]); self.sl = list(z["sl"]); self.exp = list(z["exp"])
        else:
            self.reg = trend_regime(self.h, self.l, blocks)
            self.sh, self.sl = last_swing_levels(self.h, self.l, blocks)
            self.exp = expansion(self.o, self.h, self.l, self.c)
            np.savez(cache, reg=np.array(self.reg, dtype=object), sh=np.array(self.sh),
                     sl=np.array(self.sl), exp=np.array(self.exp))
        self._breaks = None

    def breaks(self):
        if self._breaks is None:
            sw = label_structure(detect_swings(self.h, self.l, self.blocks))
            self._breaks = detect_breaks(self.c, sw, self.blocks)
        return self._breaks


def _elig_trend(ctx, target):
    return np.array([r == target for r in ctx.reg])


# ── TREND_UP × pullback continuation LONG, WIDE swing-low stop (new hypotheses vs T03) ──
def build_T05(ctx):
    o, h, l, c, reg, sl = ctx.o, ctx.h, ctx.l, ctx.c, ctx.reg, ctx.sl
    tr = []
    for i in range(3, ctx.n - 1):
        if reg[i] != UP or not np.isfinite(sl[i]):
            continue
        if h[i-1] < h[i-2] and l[i-1] < l[i-2] and h[i-2] < h[i-3] and l[i-2] < l[i-3] and c[i] > h[i-1]:
            if sl[i] < o[min(i+1, ctx.n-1)]:      # stop below entry (structural swing low)
                tr.append(Trade(i, "long", float(sl[i]), HOLD_L))
    return tr, _elig_trend(ctx, UP)


# ── TREND_UP × momentum continuation LONG, WIDE swing-low stop ──
def build_T06(ctx):
    o, h, l, c, reg, sl, exp = ctx.o, ctx.h, ctx.l, ctx.c, ctx.reg, ctx.sl, ctx.exp
    up_bar = c > o
    tr = []
    for i in range(1, ctx.n - 1):
        if reg[i] == UP and exp[i] and up_bar[i] and np.isfinite(sl[i]) and sl[i] < o[min(i+1, ctx.n-1)]:
            tr.append(Trade(i, "long", float(sl[i]), HOLD_L))
    return tr, _elig_trend(ctx, UP)


# ── BREAKOUT_TRANSITION × breakout confirmation (body-BOS = the transition) ──
def build_BT01(ctx):
    tr = []
    elig = np.zeros(ctx.n, dtype=bool)
    o = ctx.o; sh, sl = ctx.sh, ctx.sl
    for b in ctx.breaks():
        i = b.idx
        if not (0 < i < ctx.n - 1):
            continue
        elig[i] = True
        if b.kind is BreakKind.BOS_BULL and np.isfinite(sl[i]) and sl[i] < o[i+1]:
            tr.append(Trade(i, "long", float(sl[i]), HOLD_L))
        elif b.kind is BreakKind.BOS_BEAR and np.isfinite(sh[i]) and sh[i] > o[i+1]:
            tr.append(Trade(i, "short", float(sh[i]), HOLD_L))
    return tr, elig


# ── BREAKOUT_TRANSITION × retest continuation (BOS then a retest of the broken level) ──
def build_BT02(ctx):
    tr = []; elig = np.zeros(ctx.n, dtype=bool)
    o, h, l, c = ctx.o, ctx.h, ctx.l, ctx.c
    def be(idx):
        for bl in ctx.blocks:
            if bl.start <= idx < bl.end:
                return bl.end
        return ctx.n
    for b in ctx.breaks():
        i = b.idx; lvl = b.reference_swing.price
        if not (0 < i < ctx.n - 1):
            continue
        elig[i] = True
        up = b.kind is BreakKind.BOS_BULL; dn = b.kind is BreakKind.BOS_BEAR
        if not (up or dn):
            continue
        end = min(i + 1 + HOLD, be(i))
        for j in range(i + 1, end):                      # first retest touch of the broken level
            if (up and l[j] <= lvl <= h[j]) or (dn and l[j] <= lvl <= h[j]):
                if up and lvl < o[min(j+1, ctx.n-1)]:
                    tr.append(Trade(j, "long", float(l[j]), HOLD_L))
                elif dn and lvl > o[min(j+1, ctx.n-1)]:
                    tr.append(Trade(j, "short", float(h[j]), HOLD_L))
                break
    return tr, elig


# ── COMPRESSION × breakout preparation (accumulated-range stop; regime = compression) ──
def build_C01(ctx):
    o, h, l, c = ctx.o, ctx.h, ctx.l, ctx.c
    comp = compression_flags(ctx.atr); exp = ctx.exp
    tr = []; elig = np.zeros(ctx.n, dtype=bool)
    for i in np.flatnonzero(exp):
        if not (0 < i < ctx.n - 1):
            continue
        j = i - 1; hh = -np.inf; ll = np.inf; steps = 0
        while j >= 0 and comp[j] and steps < 200:
            hh = max(hh, h[j]); ll = min(ll, l[j]); j -= 1; steps += 1
        if steps < 2 or hh <= ll:
            continue
        elig[i] = True                          # eligible = expansion bar exiting a >=2-bar compression
        if c[i] > o[i] and c[i] > hh and ll < o[i+1]:
            tr.append(Trade(i, "long", float(ll), HOLD_L))
        elif c[i] < o[i] and c[i] < ll and hh > o[i+1]:
            tr.append(Trade(i, "short", float(hh), HOLD_L))
    return tr, elig


# ── TREND_DOWN × selective structure SHORT (pullback short, wide swing-high stop) ──
def build_TD01(ctx):
    o, h, l, c, reg, sh = ctx.o, ctx.h, ctx.l, ctx.c, ctx.reg, ctx.sh
    tr = []
    for i in range(3, ctx.n - 1):
        if reg[i] != DOWN or not np.isfinite(sh[i]):
            continue
        if h[i-1] > h[i-2] and l[i-1] > l[i-2] and h[i-2] > h[i-3] and l[i-2] > l[i-3] and c[i] < l[i-1]:
            if sh[i] > o[min(i+1, ctx.n-1)]:
                tr.append(Trade(i, "short", float(sh[i]), HOLD_L))
    return tr, _elig_trend(ctx, DOWN)


# ── registry of candidate cards + builders (the initial queue's hypotheses) ──
LIBRARY = {
    "CAND-T05": dict(family="trend_pullback_continuation", cell="TREND_UP × pullback LONG",
                     regime="TREND_UP", direction="long", stop="last confirmed swing low (WIDE)",
                     hold=HOLD_L, note="new hypothesis: wide structural stop (vs T03 tight); NOT a repair",
                     build=build_T05),
    "CAND-T06": dict(family="trend_momentum_continuation", cell="TREND_UP × momentum LONG",
                     regime="TREND_UP", direction="long", stop="last confirmed swing low (WIDE)",
                     hold=HOLD_L, note="new hypothesis: wide structural stop (vs T01 tight)",
                     build=build_T06),
    "CAND-BT01": dict(family="breakout_transition_confirmation", cell="BREAKOUT_TRANSITION × confirmation",
                      regime="BREAKOUT_TRANSITION (body-BOS)", direction="break side",
                      stop="opposite last swing (WIDE)", hold=HOLD_L, build=build_BT01),
    "CAND-BT02": dict(family="breakout_transition_retest", cell="BREAKOUT_TRANSITION × retest continuation",
                      regime="BREAKOUT_TRANSITION (BOS+retest)", direction="break side",
                      stop="retest bar extreme", hold=HOLD_L, build=build_BT02),
    "CAND-C01": dict(family="compression_breakout", cell="COMPRESSION × breakout preparation",
                     regime="COMPRESSION (atr<0.8*ma)", direction="expansion side",
                     stop="accumulated compression range far edge (WIDE)", hold=HOLD_L, build=build_C01),
    "CAND-TD01": dict(family="trend_down_selective_short", cell="TREND_DOWN × selective structure SHORT",
                      regime="TREND_DOWN", direction="short", stop="last confirmed swing high (WIDE)",
                      hold=HOLD_L, build=build_TD01),
}
