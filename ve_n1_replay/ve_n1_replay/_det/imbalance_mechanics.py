"""Imbalance mechanics — MK-03. ÎNCHIS (toate întrebările rezolvate, manifest v2.5.6, 00dfa6f).

Implementat: `detect_fvgs`, `FairValueGap.ce_50`, `count_bpr` (D-BPR), `detect_inverse_fvgs`
(Q4), `detect_fvg_reactions` (Q5+Q6 gradient + consumare D7).

Definiții pure. NU citește date, NU apelează `load()`, NU cunoaște manifestul. Rămâne inert
până când o ipoteză pre-înregistrată îl folosește (`no_unregistered_research_lines_rule`).
Depinde de `market_structure` pentru `Block`.

CONCEPTE:
  FVG   Bullish: low[i+1]>high[i-1], nivel [high[i-1],low[i+1]]. Bearish simetric.
  CE    Consequent Encroachment, mijloc 50% (`ce_50`).
  IFVG  Inverse FVG. Prima close ulterioară dincolo de marginea îndepărtată → polaritate inversată.
  BPR   Suprapunere bullish×bearish FVG în fereastră ≤3 bare (D-BPR).

DECIZII (rezolvate — reutilizări de decizii existente, NU convenții noi):
  Q1 (lookahead) — RATIFICAT: `confirmed_idx = i+1`, mecanic forțat (analog D1).
  Q2 (graniță de bloc) — RATIFICAT: FVG-urile NU supraviețuiesc unei granițe de bloc (analog D4);
     la sfârșit de bloc ies din scop. Toate funcțiile confinează în bloc.
  D-BPR — `count_bpr`, numărătoare la 0,00/0,10/0,25, fără îngheț (regula e a consumatorului).
  Q4 (inversare IFVG) — RESOLVED: prima bară ulterioară cu `close<lower` (bull)/`close>upper`
     (bear) — CLOSE decisiv, nu fitil; verbatim din e010/e012. `detect_inverse_fvgs`.
  Q5 (consumare) — RATIFICAT (analog D7): consumat o dată la prima atingere CE-50, fără re-armare,
     în blocul curent (fără dimensiune sesiune/zi). `detect_fvg_reactions.ce50_touch_idx`.
  Q6 (gradient CE) — RATIFICAT (asimetrie fitil/close): treapta 1 CE-50 (FITIL, low<=ce_50),
     treapta 2 umplere (FITIL, low<=lower), treapta 3 inversare (CLOSE, close<lower). Simetric bear.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from market_structure import Block


class FVGKind(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"


@dataclass(frozen=True)
class FairValueGap:
    formed_idx: int
    """Bara de mijloc (i) a tiparului de 3 bare."""

    confirmed_idx: int
    """Bara de la care gap-ul e cunoscut. = i+1 (mecanic forțat, Q1)."""

    upper: float
    lower: float
    kind: FVGKind
    block_index: int

    @property
    def ce_50(self) -> float:
        """Consequent Encroachment — mijlocul 50%."""
        return (self.upper + self.lower) / 2.0


@dataclass(frozen=True)
class BalancedPriceRange:
    upper: float
    lower: float
    bullish_fvg_idx: int
    bearish_fvg_idx: int
    block_index: int


def detect_fvgs(
    high: Sequence[float],
    low: Sequence[float],
    blocks: Sequence[Block],
) -> list[FairValueGap]:
    """FVG pe 3 lumânări, cu fereastra [i-1, i, i+1] confinată integral într-un bloc.

    Bullish: `low[i+1] > high[i-1]` → nivel [high[i-1], low[i+1]].
    Bearish: `high[i+1] < low[i-1]` → nivel [high[i+1], low[i-1]].
    `formed_idx = i`, `confirmed_idx = i+1` (mecanic forțat, Q1). Confinarea ferestrei în
    bloc e invariantul de carantină D3/D4, nu Q2 (supraviețuirea rămâne deschisă).
    """
    out: list[FairValueGap] = []
    for b_i, block in enumerate(blocks):
        for i in range(block.start + 1, block.end - 1):   # fereastra 3 bare în bloc
            if low[i + 1] > high[i - 1]:
                out.append(FairValueGap(
                    formed_idx=i, confirmed_idx=i + 1,
                    lower=high[i - 1], upper=low[i + 1],
                    kind=FVGKind.BULLISH, block_index=b_i))
            elif high[i + 1] < low[i - 1]:
                out.append(FairValueGap(
                    formed_idx=i, confirmed_idx=i + 1,
                    lower=high[i + 1], upper=low[i - 1],
                    kind=FVGKind.BEARISH, block_index=b_i))
    return out


def detect_inverse_fvgs(
    high: Sequence[float],
    low: Sequence[float],
    close: Sequence[float],
    fvgs: Sequence[FairValueGap],
    blocks: Sequence[Block],
) -> list[FairValueGap]:
    """IFVG (MK-03 Q4, RESOLVED, manifest v2.5.6): un FVG bullish se inversează PRIMA DATĂ când o
    bară ULTERIOARĂ are `close < lower` (marginea îndepărtată/joasă) — violare decisivă prin CLOSE,
    nu fitil intrabar; bearish simetric: `close > upper`. Definiție reutilizată VERBATIM din
    e010_breaker_block_snatch.py și e012_inverted_fvg.py (identică în ambele). NU engulf pe o bară;
    prima închidere ulterioară dincolo de margine, oricâte bare durează. IFVG = entitate NOUĂ cu
    polaritate inversată, aceeași zonă, „formată" la bara de inversare. Confinat în bloc (D4).
    """
    block_of = {b_i: block for b_i, block in enumerate(blocks)}
    out: list[FairValueGap] = []
    for f in fvgs:
        block = block_of.get(f.block_index)
        if block is None:
            continue
        for j in range(f.confirmed_idx + 1, block.end):        # bară ulterioară, același bloc (D4)
            if f.kind is FVGKind.BULLISH and close[j] < f.lower:
                out.append(FairValueGap(formed_idx=j, confirmed_idx=j, lower=f.lower, upper=f.upper,
                                        kind=FVGKind.BEARISH, block_index=f.block_index))
                break
            if f.kind is FVGKind.BEARISH and close[j] > f.upper:
                out.append(FairValueGap(formed_idx=j, confirmed_idx=j, lower=f.lower, upper=f.upper,
                                        kind=FVGKind.BULLISH, block_index=f.block_index))
                break
    return out


@dataclass(frozen=True)
class FvgReaction:
    """Reacția unui FVG: gradientul în 3 trepte (Q6) + consumarea D7 (Q5). Indici None dacă treapta
    nu s-a produs în bloc (D4)."""
    formed_idx: int
    kind: FVGKind
    ce50_touch_idx: int | None      # treapta 1 (consumare D7, FITIL): low<=ce_50 / high>=ce_50
    full_fill_idx: int | None       # treapta 2 (umplere, FITIL): low<=lower / high>=upper
    inversion_idx: int | None       # treapta 3 (inversare, CLOSE): close<lower / close>upper (Q4)
    block_index: int


def detect_fvg_reactions(
    high: Sequence[float],
    low: Sequence[float],
    close: Sequence[float],
    fvgs: Sequence[FairValueGap],
    blocks: Sequence[Block],
) -> list[FvgReaction]:
    """Gradientul în 3 trepte per FVG (Q6) + consumarea (Q5, D7), confinat în bloc (D4).

    Treapta 1 — CE-50, la nivel de FITIL = CONSUMAREA (D7): `low<=ce_50` (bull) / `high>=ce_50`
    (bear), prima atingere. Treapta 2 — umplere completă, FITIL: `low<=lower` / `high>=upper`.
    Treapta 3 — inversare, CLOSE (Q4): `close<lower` / `close>upper`. Consumarea (D7) e la prima
    atingere CE-50; umplerea și inversarea sunt proprietăți suplimentare înregistrate, NU re-armări.
    Lifetime = blocul curent (fără dimensiune sesiune/zi — respins explicit în rezoluție).
    """
    block_of = {b_i: block for b_i, block in enumerate(blocks)}
    out: list[FvgReaction] = []
    for f in fvgs:
        block = block_of.get(f.block_index)
        if block is None:
            continue
        ce = f.ce_50
        ce50: int | None = None
        full: int | None = None
        inv: int | None = None
        for j in range(f.confirmed_idx + 1, block.end):
            if f.kind is FVGKind.BULLISH:
                if ce50 is None and low[j] <= ce:
                    ce50 = j
                if full is None and low[j] <= f.lower:
                    full = j
                if inv is None and close[j] < f.lower:
                    inv = j
            else:
                if ce50 is None and high[j] >= ce:
                    ce50 = j
                if full is None and high[j] >= f.upper:
                    full = j
                if inv is None and close[j] > f.upper:
                    inv = j
            if ce50 is not None and full is not None and inv is not None:
                break
        out.append(FvgReaction(formed_idx=f.formed_idx, kind=f.kind, ce50_touch_idx=ce50,
                               full_fill_idx=full, inversion_idx=inv, block_index=f.block_index))
    return out


def count_bpr(
    fvgs: Sequence[FairValueGap],
    blocks: Sequence[Block],
    tolerances: tuple[float, ...] = (0.0, 0.10, 0.25),
    max_window_bars: int = 3,
) -> dict[float, int]:
    """D-BPR: numără suprapunerile bullish×bearish FVG (același bloc, `formed_idx` în ≤
    `max_window_bars`) la fiecare toleranță — pur descriptiv, FĂRĂ îngheț.

    Suprapunere la toleranța `t`: `max(lower_a, lower_b) - min(upper_a, upper_b) <= t`.
    La `t=0` cere intersecție/atingere strictă; monotonă în `t` (0→0,10→0,25). Regula de
    îngheț (cea mai mică toleranță cu n≥25) e a consumatorului, decisă în avans — NU aici.
    """
    bulls = [f for f in fvgs if f.kind is FVGKind.BULLISH]
    bears = [f for f in fvgs if f.kind is FVGKind.BEARISH]
    counts: dict[float, int] = {t: 0 for t in tolerances}
    for a in bulls:
        for b in bears:
            if a.block_index != b.block_index:
                continue
            if abs(a.formed_idx - b.formed_idx) > max_window_bars:
                continue
            gap = max(a.lower, b.lower) - min(a.upper, b.upper)   # ≤0 = suprapunere; >0 = distanță
            for t in tolerances:
                if gap <= t:
                    counts[t] += 1
    return counts
