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
  Q3 (BPR „aceeași fereastră de preț")  Ce înseamnă exact suprapunere pentru BPR —
     intersecție de intervale nevidă? un prag minim de suprapunere (%)? egalitate de
     limite? CEO a numit explicit această întrebare ca nedecisă.
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


def detect_bpr(
    fvgs: Sequence[FairValueGap],
    blocks: Sequence[Block],
) -> list[BalancedPriceRange]:
    """Detectează Balanced Price Ranges (suprapunere bullish×bearish FVG).

    NEIMPLEMENTAT — depinde de Q3 (definiția „aceleiași ferestre de preț").
    """
    raise NotImplementedError("MK-03 neratificat: Q3 (definiția suprapunerii BPR)")
