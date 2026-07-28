"""Imbalance mechanics — MK-03. SCHELET NEIMPLEMENTAT.

MK-03 NU e ratificat. Deciziile echivalente lui D1-D7 (pentru structura/lichiditate)
NU există încă pentru imbalanțe. Acest fișier declară semnături, tipuri și definiții,
cu `NotImplementedError` în corp. Deciziile deschise sunt scrise ca ÎNTREBĂRI, nu
alese aici — le trimite CEO Statisticianului. A implementa acum ar însemna să aleg eu
acele decizii.

Depinde (când va fi implementat) de `market_structure` pentru `Block`.

CONCEPTE (definiții ICT/SMC, pure geometrie de preț):

  FVG   Fair Value Gap. Imbalanță pe 3 bare. Bullish: low[i+1] > high[i-1] (gol
        lăsat de bara i). Bearish: high[i+1] < low[i-1]. Nivelul gap-ului = [high[i-1],
        low[i+1]] (bullish) / [high[i+1], low[i-1]] (bearish).
  CE    Consequent Encroachment. Mijlocul 50% al FVG-ului — nivelul de referință
        pentru mitigare parțială.
  IFVG  Inverse FVG. Un FVG a cărui limită e violată și care își inversează polaritatea
        (suport devine rezistență).
  BPR   Balanced Price Range. Suprapunerea unui FVG bullish și a unuia bearish pe
        ACEEAȘI fereastră de preț — o zonă de dublă imbalanță.

ÎNTREBĂRI DESCHISE PENTRU STATISTICIAN (echivalentele lui D1-D7, neratificate):

  Q1 (lookahead, analog D1)  Un FVG la bara i cere bara i+1. Deci `confirmed_idx = i+1`.
     Se ratifică aceeași convenție ca D1 (consumatorii forward folosesc confirmed_idx)?
  Q2 (graniță de bloc, analog D3)  Supraviețuiește un FVG unei granițe de bloc de
     descoperire? Se resetează mașina de stare ca la D3, sau imbalanțele au altă regulă?
  D-BPR (RATIFICAT — STAT-LM001-GEOMETRY-MK03-MK04-v1.0)  BPR = suprapunere între un FVG
     bullish și unul bearish într-o fereastră de MAXIM 3 bare. Toleranța NU e fixă la 0,00:
     se NUMĂRĂ evenimentele la trei toleranțe — 0,00 / 0,10 / 0,25 dolari — pur descriptiv.
     REGULA DE ÎNGHEȚ (fixată ÎNAINTE de orice numărătoare, ca să nu fie aleasă după cifre):
     se îngheață CEA MAI MICĂ toleranță a cărei numărătoare atinge n≥25. Dacă 0,00 atinge
     → 0,00 (cea mai strictă/defensabilă); altfel 0,10; altfel 0,25. Dacă nici 0,25 nu
     atinge n≥25, BPR NU e testabilă la M15_v2 cu acest n — se raportează ca atare, NU se
     forțează un prag artificial. Monotonă și mecanică: favorizează precizia maximă fezabilă
     statistic, nu „mai multe evenimente". (Motiv: prețul aurului are 2 zecimale — coincidența
     exactă la 0,00 între două goluri independente e improbabilă; zero la 0,00 nu ar dovedi
     absența BPR, ci doar o precizie pe care prețul n-o are.)
  Q4 (inversare IFVG, analog D6)  Când se consideră un FVG „inversat" — close prin el,
     sau doar wick? Integral pe bara curentă (fără lookahead) sau pe fereastră?
  Q5 (consumare / re-armare, analog D7)  Un FVG mitigat (atins de CE 50% sau umplut
     integral) se consumă și nu mai produce semnale, sau rămâne activ (re-armare)?
  Q6 (mitigare CE)  Atingerea CE 50% = wick sau close? Umplerea integrală = wick sau close?
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
    """Bara de la care gap-ul e cunoscut. Q1: propus i+1, neratificat."""

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
    """Detectează Fair Value Gaps pe 3 bare, confinate în blocuri.

    NEIMPLEMENTAT — depinde de Q1 (confirmed_idx) și Q2 (granițe de bloc).
    """
    raise NotImplementedError("MK-03 neratificat: Q1 (lookahead), Q2 (graniță de bloc)")


def detect_inverse_fvgs(
    high: Sequence[float],
    low: Sequence[float],
    close: Sequence[float],
    fvgs: Sequence[FairValueGap],
    blocks: Sequence[Block],
) -> list[FairValueGap]:
    """Detectează FVG-uri inversate (IFVG).

    NEIMPLEMENTAT — depinde de Q4 (criteriul de inversare) și Q5 (consumare).
    """
    raise NotImplementedError("MK-03 neratificat: Q4 (inversare), Q5 (consumare)")


def count_bpr(
    fvgs: Sequence[FairValueGap],
    blocks: Sequence[Block],
    tolerances: tuple[float, ...] = (0.0, 0.10, 0.25),
    max_window_bars: int = 3,
) -> dict[float, int]:
    """Numără suprapunerile bullish×bearish FVG (fereastră ≤ max_window_bars) la fiecare
    toleranță — pur descriptiv. Regula de îngheț (cea mai mică toleranță cu n≥25) e a
    consumatorului, decisă ÎNAINTE de a vedea cifrele (D-BPR, vezi docstring-ul modulului).

    NEIMPLEMENTAT — restul deciziilor MK-03 (Q1/Q2/Q4/Q5/Q6) nu sunt ratificate.
    """
    raise NotImplementedError("MK-03: numărătoarea BPR e specificată (D-BPR) dar restul MK-03 neratificat (Q1/Q2/Q4/Q5/Q6)")
