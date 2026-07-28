"""Imbalance mechanics — MK-03. IMPLEMENTARE PARȚIALĂ (doar ce e ratificat).

Implementat: `detect_fvgs` (FVG pe 3 lumânări), `FairValueGap.ce_50`, `count_bpr` (D-BPR).
Neimplementat, cu `NotImplementedError` + întrebare deschisă: `detect_inverse_fvgs` (IFVG).

Definiții pure. NU citește date, NU apelează `load()`, NU cunoaște manifestul. Primește
array-uri + blocuri; returnează structuri. Rămâne inert până când o ipoteză pre-înregistrată
îl folosește (`no_unregistered_research_lines_rule`).

Depinde de `market_structure` pentru `Block`.

CONCEPTE:
  FVG   Fair Value Gap. Imbalanță pe 3 bare. Bullish: low[i+1] > high[i-1]; nivelul
        = [high[i-1], low[i+1]]. Bearish: high[i+1] < low[i-1]; nivelul = [high[i+1], low[i-1]].
  CE    Consequent Encroachment. Mijlocul 50% al FVG-ului (proprietate `ce_50`).
  IFVG  Inverse FVG. Un FVG „închis complet de corpul opus" care își inversează polaritatea.
  BPR   Balanced Price Range. Suprapunere bullish×bearish FVG în fereastră ≤3 bare (D-BPR).

STARE DECIZII (echivalentele lui D1-D7):

  Q1 (lookahead, analog D1) — NEBLOCANT.  `confirmed_idx = i+1` e MECANIC FORȚAT (un FVG pe
     3 bare nu poate fi cunoscut înainte de bara i+1; nu există alternativă lookahead-safe,
     exact ca D1). Implementat cu i+1. Ratificarea FORMALĂ a convenției rămâne de confirmat,
     dar nu blochează — nu e o alegere liberă.
  Q2 (graniță de bloc, analog D3) — DESCHIS; blochează DOAR durata de viață.  Formarea FVG
     confinează fereastra de 3 bare într-un singur bloc (invariantul de carantină D3/D4 deja
     stabilit — o fereastră care traversează o graniță e fără sens; NU e o decizie nouă).
     DESCHIS rămâne: SUPRAVIEȚUIEȘTE un FVG deja format unei granițe de bloc ulterioare
     (durata de viață / mitigare cross-bloc)? Blochează logica de supraviețuire/mitigare
     cross-bloc, NU detectarea FVG. Ce trebuie decis: FVG-ul se invalidează la graniță (ca D4)
     sau persistă?
  D-BPR (RATIFICAT) — IMPLEMENTAT în `count_bpr`.  Numărătoare la 0,00/0,10/0,25, fără îngheț
     (regula de îngheț — cea mai mică toleranță cu n≥25 — e a consumatorului, în avans).
  Q4 (inversare IFVG, analog D6) — DESCHIS; blochează `detect_inverse_fvgs`.  „Închis complet
     de corpul opus" e AMBIGUU: (a) o singură bară de sens opus al cărei CORP (open-close)
     acoperă integral golul, SAU (b) o închidere (close) dincolo de marginea îndepărtată a
     golului? Și: wick sau doar corp? Ce trebuie decis: definiția exactă a inversării.
  Q5 (consumare / re-armare, analog D7) — DESCHIS; blochează logica de consumare (neimplementată).
     Un FVG mitigat (atins de CE 50% sau umplut integral) se consumă (o singură dată) sau rămâne
     activ (re-armare)? Ce trebuie decis: consumare vs re-armare.
  Q6 (mitigare CE) — DESCHIS; blochează DETECTAREA mitigării, NU nivelul.  NIVELUL CE (`ce_50`)
     e neambiguu (mijloc 50%) — implementat. DESCHIS: atingerea CE = wick sau close? Umplerea
     integrală = wick sau close? Ce trebuie decis: criteriul de atingere.
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
    """IFVG. NEIMPLEMENTAT — Q4: „închis complet de corpul opus" e ambiguu (corp-engulf vs
    close dincolo de marginea îndepărtată; wick vs corp). Necesită definiția exactă a inversării.
    """
    raise NotImplementedError("MK-03 Q4: definitia IFVG 'inchis complet de corp opus' e ambigua")


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
