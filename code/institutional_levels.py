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

  D3_bis (RATIFICAT — STAT-LM001-GEOMETRY-MK03-MK04-v1.0)  Memoria zilnică (PDH/PDL) se
     RESETEAZĂ complet la fiecare graniță de bloc de descoperire; prima zi din segmentul
     nou e UNCLASSIFIED — nu există „zi precedentă" validă în bloc, iar a împrumuta una din
     afară ar încălca arhitectura de carantină. Analogul exact al D3, aceeași motivație.
  D-WEEK (RATIFICAT)  O săptămână trunchiată de o graniță PRODUCE un Weekly High/Low
     (calculat exclusiv pe barele active din bloc, fără împrumut extern), DAR poartă
     obligatoriu `days_contributing` (1-5) și `completeness` ("COMPLETE"=5 zile / "PARTIAL"=<5).
     Consumatorii din aval NU pot trata silent un nivel PARTIAL identic cu unul COMPLETE —
     fie îl exclud, fie îl tratează ca strat separat declarat explicit. Aceeași disciplină ca
     D3/D4: discontinuitățile de graniță trebuie vizibile, nu netezite.
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

    days_contributing: int | None = None
    """Doar Weekly (D-WEEK): zile active care au contribuit (1-5). None pentru PDH/PDL."""

    completeness: str | None = None
    """Doar Weekly (D-WEEK): "COMPLETE" (5 zile) sau "PARTIAL" (<5). None pentru PDH/PDL."""


def compute_prior_day_levels(
    high: Sequence[float],
    low: Sequence[float],
    day_index: Sequence[int],
    blocks: Sequence[Block],
) -> list[ReferenceLevel]:
    """PDH/PDL per zi, cu reset la graniță de bloc (D3_bis).

    `day_index[i]` = eticheta de zi calendaristică a barei i (Q3: 00:00 UTC?).

    NEIMPLEMENTAT — D3_bis RATIFICAT (reset complet la graniță, prima zi UNCLASSIFIED),
    dar Q3 (granița de zi/00:00 UTC?) și Q4 (lag de disponibilitate) rămân neratificate.
    """
    raise NotImplementedError("MK-04: D3_bis ratificat; Q3 (granița de zi) + Q4 (lag) neratificate")


def compute_prior_week_levels(
    high: Sequence[float],
    low: Sequence[float],
    week_index: Sequence[int],
    blocks: Sequence[Block],
) -> list[ReferenceLevel]:
    """Weekly High/Low per săptămână. Fiecare nivel poartă `days_contributing` (1-5) și
    `completeness` COMPLETE/PARTIAL (D-WEEK) — o săptămână trunchiată produce nivel, dar marcat.

    NEIMPLEMENTAT — D-WEEK RATIFICAT (nivel cu days_contributing + completeness), dar
    Q3 (granița de săptămână) și Q4 (lag) rămân neratificate.
    """
    raise NotImplementedError("MK-04: D-WEEK ratificat; Q3 (granița de săptămână) + Q4 (lag) neratificate")
