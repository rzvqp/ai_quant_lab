"""TREI DETECTOARE DE REACȚIE — Void, BPR, Weekly (STAT-THREE-REACTION-DETECTORS-SPEC-v1.0, e68e0cd,
manifest v2.7.40). Deblochează CAND-0004 (void), CAND-0005 (BPR), producția Alpha (weekly, populație=275).

Precedent urmat: `session_levels.py` — oglindire bară cu bară, ZERO convenții paralele. Reutilizează
`detect_liquidity_voids`, `count_bpr`-convenția, `compute_prior_week_levels`, semnătura D6 wick-sweep, `_runs`,
D3_bis/D4, D7, ancora 17:00 NY (prin `day_index`/`week_index` caller-side). Fără lookahead. FEREASTRA DE MĂSURARE
DISJUNCTĂ de cea de SELECȚIE (anti-E010): selecția se încheie la `available_idx`; măsurarea scanează de la
`available_idx+1` (exact ca `detect_fvg_reactions`: `confirmed_idx+1`). NU ratific — Red Team atacă.

PARTEA 1 — void: oglindește gradientul FVG (Q6) în 3 trepte; un void e ACELAȘI tip de obiect (interval de preț
           sărit). Respingerea reutilizează D6 wick-sweep VERBATIM. Fără a patra definiție.
PARTEA 2 — BPR: geometrie AGNOSTICĂ la direcție, INCLUSIV `entry_side`; politica adaugă direcția din bias și
           declară regula (ca `Mid` la nivelul 3). BPR nu are polaritate proprie.
PARTEA 3 — weekly: DEPĂȘIRE (nu conținere) — extreme genuine de perioadă, ca PDH/PDL. `completeness` (COMPLETE/
           PARTIAL) se PROPAGĂ, NU se filtrează în primitivă; COMPLETE și PARTIAL se raportează SEPARAT
           (o săptămână PARTIAL are extreme pe mai puține zile ⇒ mai aproape de preț ⇒ atinsă mai des; poolarea
           ar umfla rata). Măsurat: 538 COMPLETE, 34 PARTIAL. Populație weekly utilizabilă = 275 (colapsul e la
           BIAS, nu la geometrie — detectorul NU e degenerat).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from market_structure import Block
from order_block_void import detect_liquidity_voids
from imbalance_mechanics import FVGKind, FairValueGap
from institutional_levels import LevelKind, ReferenceLevel

_BPR_MAX_WINDOW = 3               # convenția count_bpr: |formed_idx_a − formed_idx_b| ≤ 3, același bloc


class EntrySide(Enum):
    ABOVE = "above"
    BELOW = "below"


def _block_of_bar(idx: int, blocks: Sequence[Block]) -> tuple[int, Block] | None:
    for b_i, block in enumerate(blocks):
        if block.start <= idx < block.end:
            return b_i, block
    return None


# ══════════════════════════ PARTEA 1 — detect_void_reactions ══════════════════════════
@dataclass(frozen=True)
class VoidReaction:
    void_at_idx: int                 # c (tranziția c→c+1)
    zone_lower: float                # min(close[c], open[c+1])
    zone_upper: float                # max(close[c], open[c+1])
    mid: float
    polarity: FVGKind                # BULLISH dacă open[c+1] > close[c] (gap sus → suport dedesubt); altfel BEARISH
    available_idx: int               # c+1 (ambii termeni cunoscuți la c+1)
    partial_fill_idx: int | None     # prima bară care atinge MID   (consumarea D7 = declanșatorul)
    full_fill_idx: int | None        # prima bară care traversează zona
    rejection_idx: int | None        # prima bară care INTRĂ și ÎNCHIDE înapoi în afară (D6 verbatim)
    block_index: int


def detect_void_reactions(
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    time: Sequence[int], blocks: Sequence[Block],
) -> list[VoidReaction]:
    """Gradientul în 3 trepte per void (oglindă `detect_fvg_reactions`). Ferestre disjuncte, D7, confinat în bloc."""
    out: list[VoidReaction] = []
    for v in detect_liquidity_voids(open_, close, time):
        c = v.at_idx
        found = _block_of_bar(c, blocks)
        if found is None:
            continue
        b_i, block = found
        cp1 = c + 1
        if cp1 >= block.end:                                 # c+1 trebuie să fie în ACELAȘI bloc (D4)
            continue
        zl = min(float(close[c]), float(open_[cp1]))
        zu = max(float(close[c]), float(open_[cp1]))
        if zu <= zl:
            continue                                         # gap nul → fără zonă
        mid = (zl + zu) / 2.0
        if open_[cp1] > close[c]:
            polarity = FVGKind.BULLISH
        elif open_[cp1] < close[c]:
            polarity = FVGKind.BEARISH
        else:
            continue                                         # egalitate → fără polaritate
        partial: int | None = None
        full: int | None = None
        rej: int | None = None
        for j in range(cp1 + 1, block.end):                  # măsurare DISJUNCTĂ (de la available_idx+1)
            if polarity is FVGKind.BULLISH:
                if partial is None and low[j] <= mid:
                    partial = j
                if full is None and low[j] <= zl:
                    full = j
                if rej is None and low[j] <= zu and close[j] > zu:
                    rej = j
            else:
                if partial is None and high[j] >= mid:
                    partial = j
                if full is None and high[j] >= zu:
                    full = j
                if rej is None and high[j] >= zl and close[j] < zl:
                    rej = j
            if partial is not None and full is not None and rej is not None:
                break
        out.append(VoidReaction(void_at_idx=c, zone_lower=zl, zone_upper=zu, mid=mid, polarity=polarity,
                                available_idx=cp1, partial_fill_idx=partial, full_fill_idx=full,
                                rejection_idx=rej, block_index=b_i))
    return out


# ══════════════════════════ PARTEA 2 — detect_bpr_reactions ══════════════════════════
@dataclass(frozen=True)
class BprReaction:
    formation_idx: int               # max(formed_idx_a, formed_idx_b)
    zone_lower: float                # max(lower_a, lower_b)
    zone_upper: float                # min(upper_a, upper_b)
    available_idx: int               # max(confirmed_idx_a, confirmed_idx_b) — AMBELE confirmate
    touch_idx: int | None            # prima bară al cărei range SUPRAPUNE zona (CONȚINERE, ca Mid)
    entry_side: EntrySide | None     # latura de intrare (close[j-1] vs zonă) — geometrie, direcția e a politicii
    traverse_idx: int | None         # prima bară care traversează COMPLET dinspre entry_side spre latura opusă
    reject_idx: int | None           # prima bară care intră și ÎNCHIDE înapoi pe latura de INTRARE (D6 verbatim)
    block_index: int
    tolerance: float


def detect_bpr_reactions(
    high: Sequence[float], low: Sequence[float], close: Sequence[float],
    fvgs: Sequence[FairValueGap], blocks: Sequence[Block], tolerance: float = 0.0,
) -> list[BprReaction]:
    """Reacție la BPR (pereche FVG bull×bear, convenția `count_bpr`). Geometrie DIRECȚIONAL-AGNOSTICĂ + `entry_side`;
    politica adaugă direcția din bias și declară regula. Toleranță 0,0 (strictă) prim candidat (escaladarea e a
    consumatorului). Ferestre disjuncte, D7, confinat în bloc."""
    block_of = {b_i: block for b_i, block in enumerate(blocks)}
    bulls = [f for f in fvgs if f.kind is FVGKind.BULLISH]
    bears = [f for f in fvgs if f.kind is FVGKind.BEARISH]
    out: list[BprReaction] = []
    for a in bulls:
        for b in bears:
            if a.block_index != b.block_index:
                continue
            if abs(a.formed_idx - b.formed_idx) > _BPR_MAX_WINDOW:
                continue
            if max(a.lower, b.lower) - min(a.upper, b.upper) > tolerance:   # convenția count_bpr
                continue
            block = block_of.get(a.block_index)
            if block is None:
                continue
            zl = max(a.lower, b.lower)
            zu = min(a.upper, b.upper)
            available = max(a.confirmed_idx, b.confirmed_idx)
            touch: int | None = None
            side: EntrySide | None = None
            trav: int | None = None
            rej: int | None = None
            for j in range(available + 1, block.end):        # măsurare DISJUNCTĂ
                if touch is None and low[j] <= zu and high[j] >= zl:       # CONȚINERE (ca Mid)
                    touch = j
                    if j - 1 >= 0:
                        prev = close[j - 1]                  # cauzal, bara anterioară
                        side = EntrySide.ABOVE if prev > zu else EntrySide.BELOW if prev < zl else None
                if touch is not None and side is not None:
                    if trav is None:
                        if side is EntrySide.ABOVE and low[j] <= zl:
                            trav = j
                        elif side is EntrySide.BELOW and high[j] >= zu:
                            trav = j
                    if rej is None:                          # închide înapoi pe latura de INTRARE (D6)
                        if side is EntrySide.ABOVE and low[j] <= zu and close[j] > zu:
                            rej = j
                        elif side is EntrySide.BELOW and high[j] >= zl and close[j] < zl:
                            rej = j
                if touch is not None and (side is None or (trav is not None and rej is not None)):
                    break
            out.append(BprReaction(formation_idx=max(a.formed_idx, b.formed_idx), zone_lower=zl, zone_upper=zu,
                                   available_idx=available, touch_idx=touch, entry_side=side, traverse_idx=trav,
                                   reject_idx=rej, block_index=a.block_index, tolerance=tolerance))
    return out


# ══════════════════════════ PARTEA 3 — detect_weekly_level_touches ══════════════════════════
@dataclass(frozen=True)
class WeeklyLevelTouch:
    level: ReferenceLevel
    touch_idx: int
    block_index: int
    completeness: str                # PROPAGAT (COMPLETE/PARTIAL) — se raportează SEPARAT, nu se filtrează aici


def detect_weekly_level_touches(
    high: Sequence[float], low: Sequence[float], levels: Sequence[ReferenceLevel],
    week_index: Sequence[int], blocks: Sequence[Block],
) -> list[WeeklyLevelTouch]:
    """Oglindește `detect_level_touches` VERBATIM, cu fereastra SĂPTĂMÂNII curente (nu ziua). DEPĂȘIRE (nu
    conținere): WEEKLY_HIGH `high>=price` / WEEKLY_LOW `low<=price` — extreme reale de perioadă, ca PDH/PDL.
    D7: consumat la PRIMA atingere. `completeness` propagat (COMPLETE și PARTIAL emise AMBELE; separarea = politică)."""
    block_of = {b_i: block for b_i, block in enumerate(blocks)}
    out: list[WeeklyLevelTouch] = []
    for lv in levels:
        if lv.kind not in (LevelKind.WEEKLY_HIGH, LevelKind.WEEKLY_LOW):
            continue                                         # doar fereastra săptămânală
        block = block_of.get(lv.block_index)
        if block is None:
            continue
        wk = week_index[lv.available_idx]
        for j in range(lv.available_idx, block.end):
            if week_index[j] != wk:                          # a ieșit din săptămâna curentă
                break
            touched = high[j] >= lv.price if lv.kind is LevelKind.WEEKLY_HIGH else low[j] <= lv.price
            if touched:
                out.append(WeeklyLevelTouch(level=lv, touch_idx=j, block_index=lv.block_index,
                                            completeness=lv.completeness or ""))
                break                                        # consumat la prima atingere (D7), fără re-armare
    return out
