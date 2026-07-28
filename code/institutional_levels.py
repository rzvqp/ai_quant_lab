"""Institutional reference levels — MK-04. SCHELET NEIMPLEMENTAT.

MK-04 NU e ratificat. Deciziile echivalente lui D1-D7 NU există pentru nivelurile
instituționale. Semnături, tipuri, definiții; `NotImplementedError` în corp. Deciziile
deschise = ÎNTREBĂRI pentru Statistician, nu alese aici.

Depinde (când va fi implementat) de `market_structure` pentru `Block`.

CONCEPTE:

  PDH / PDL   Previous Day High / Low. Extremele zilei calendaristice anterioare,
              disponibile fără lookahead abia de la deschiderea zilei curente.
  WH / WL     Weekly High / Low. Extremele săptămânii anterioare.

Aceste niveluri sunt „liquidity pools" externe pe care le consumă MK-02
(`sweep_against_reference`), dar derivarea lor (aliniere, lag, reset la graniță)
aparține acestui modul.

ÎNTREBĂRI DESCHISE PENTRU STATISTICIAN (neratificate):

  Q1 (reset D3_bis)  Cum se resetează PDH/PDL la o graniță de bloc de descoperire?
     O „zi anterioară" a cărei bară traversează banda de carantină NU are un
     precedent valid — se marchează nivelul UNAVAILABLE la începutul fiecărui bloc,
     ca analogul D3? CEO a numit explicit această întrebare.
  Q2 (săptămână tăiată de graniță)  Ce se întâmplă cu o săptămână tăiată de o graniță
     de bloc? Weekly High/Low se calculează pe săptămâna parțială din interiorul
     blocului, sau se marchează UNAVAILABLE până la prima săptămână completă din bloc?
     CEO a numit explicit această întrebare.
  Q3 (definiția zilei/săptămânii)  Granița de zi = 00:00 UTC (ca Path A la DC-0004)?
     Granița de săptămână = luni 00:00 UTC? Fus fix, fără DST? Trebuie declarat, nu deduc.
  Q4 (disponibilitate/lag, analog D1)  PDH e cunoscut abia de la deschiderea zilei
     curente (`available_idx` = prima bară a zilei curente). Se ratifică `entry@next-open`
     lookahead-safe deja stabilit? Fără asta, PDH derivat din bare ale zilei curente = lookahead.
  Q5 (consumare)  Un nivel PDH măturat o dată se consumă (D7-analog) sau rămâne activ
     tot restul zilei?
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from market_structure import Block


class LevelKind(Enum):
    PDH = "pdh"
    PDL = "pdl"
    WEEKLY_HIGH = "weekly_high"
    WEEKLY_LOW = "weekly_low"


@dataclass(frozen=True)
class ReferenceLevel:
    price: float
    kind: LevelKind

    source_period_start: int
    """Prima bară a perioadei-sursă (ziua/săptămâna anterioară)."""

    available_idx: int
    """Bara de la care nivelul e cunoscut fără lookahead. Q4: propus prima bară a
    perioadei curente, neratificat."""

    block_index: int


def compute_prior_day_levels(
    high: Sequence[float],
    low: Sequence[float],
    day_index: Sequence[int],
    blocks: Sequence[Block],
) -> list[ReferenceLevel]:
    """PDH/PDL per zi, cu reset la graniță de bloc (D3_bis).

    `day_index[i]` = eticheta de zi calendaristică a barei i (Q3: 00:00 UTC?).

    NEIMPLEMENTAT — depinde de Q1 (reset D3_bis), Q3 (granița de zi), Q4 (lag).
    """
    raise NotImplementedError("MK-04 neratificat: Q1 (reset D3_bis), Q3 (zi), Q4 (lag)")


def compute_prior_week_levels(
    high: Sequence[float],
    low: Sequence[float],
    week_index: Sequence[int],
    blocks: Sequence[Block],
) -> list[ReferenceLevel]:
    """Weekly High/Low per săptămână, cu tratamentul săptămânii tăiate de graniță.

    NEIMPLEMENTAT — depinde de Q2 (săptămână tăiată), Q3 (granița de săptămână), Q4 (lag).
    """
    raise NotImplementedError("MK-04 neratificat: Q2 (săptămână tăiată), Q3, Q4")
