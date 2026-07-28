"""Institutional reference levels — MK-04. IMPLEMENTARE PARȚIALĂ (doar ce e ratificat).

Implementat: `compute_prior_day_levels` (PDH/PDL, D3_bis), `compute_prior_week_levels`
(Weekly H/L, D-WEEK: days_contributing + COMPLETE/PARTIAL).

Definiții pure. NU citește date, NU apelează `load()`. Primește array-uri + etichetele de
perioadă (`day_index`, `week_index`) și blocurile; NU derivă singur granițele.

**Granițele de perioadă se derivă CALLER-SIDE**, nu în acest modul, exact ca sub-barele HTF:
`day_index[i]` provine din ancora 17:00 New York DST-aware (`code/resample_ny.py`), iar
numărul de bare pe zi se NUMĂRĂ (coloana `sub`), niciodată nu se presupune 92 sau 96 — nicio
zi D1 nu are 96 bare, iar 92 e doar cea mai frecventă valoare (golul de mentenanță 21:00 UTC),
nu o constantă. Modulul e agnostic la câte bare are o zi: grupează pe `day_index`.

Depinde de `market_structure` pentru `Block`.

STARE DECIZII:
  D3_bis (RATIFICAT) — IMPLEMENTAT.  Memoria se resetează complet la fiecare graniță de bloc;
     prima zi / prima săptămână din fiecare bloc rămâne UNCLASSIFIED (nu emite nivel — nu are
     perioadă anterioară validă în bloc, iar împrumutul din afară ar încălca carantina).
  D-WEEK (RATIFICAT) — IMPLEMENTAT.  Fiecare Weekly H/L poartă `days_contributing` (nr. de zile
     de sesiune distincte care au contribuit) și `completeness` COMPLETE (5) / PARTIAL (<5).
  Q3-zi (granița de zi) — REZOLVAT de CEO: ancora 17:00 NY DST-aware. Aplicat CALLER-SIDE prin
     `day_index`; modulul nu-l codifică. Neblocant pentru modul.
  Q3-săptămână (granița de săptămână) — DESCHIS.  Când începe săptămâna (duminică 17:00 NY?).
     Modulul folosește `week_index` (caller), deci nu blochează modulul, dar blochează derivarea
     caller-side a lui `week_index`. Ce trebuie decis: definiția graniței de săptămână.
  Q4 (lag / disponibilitate, analog D1) — NEBLOCANT.  `available_idx` = prima bară a perioadei
     CURENTE (perioada anterioară e complet cunoscută la deschiderea celei curente) — mecanic
     forțat, lookahead-safe. Implementat. Ratificarea formală rămâne de confirmat, nu blochează.
  Q5 (consumare) — DESCHIS; blochează logica de consumare (neimplementată; nu se cere aici).
     Un nivel măturat o dată se consumă (D7-analog) sau rămâne activ? Modulul DOAR calculează
     nivelurile; sweeping/consumarea sunt în aval. Ce trebuie decis: consumare vs persistență.

  CLARIFICARE (neblocantă): „Weekly cu rolling pe zile de sesiune" — am implementat săptămâni
     DISCRETE (grupate pe `week_index`), nu o fereastră glisantă de 5 zile de sesiune. Dacă
     intenția e o fereastră glisantă, cere re-specificare.
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
    """Bara de la care nivelul e cunoscut fără lookahead = prima bară a perioadei curente (Q4)."""

    block_index: int

    days_contributing: int | None = None
    """Doar Weekly (D-WEEK): zile de sesiune distincte care au contribuit. None pentru PDH/PDL."""

    completeness: str | None = None
    """Doar Weekly (D-WEEK): "COMPLETE" (≥5 zile) sau "PARTIAL" (<5). None pentru PDH/PDL."""


def _runs(index: Sequence[int], start: int, end: int) -> list[tuple[int, int]]:
    """Segmentele contigue [first, last] de bare cu aceeași etichetă de perioadă în [start, end)."""
    runs: list[tuple[int, int]] = []
    cur_label: int | None = None
    for i in range(start, end):
        lab = index[i]
        if not runs or lab != cur_label:
            runs.append((i, i))
            cur_label = lab
        else:
            runs[-1] = (runs[-1][0], i)
    return runs


def compute_prior_day_levels(
    high: Sequence[float],
    low: Sequence[float],
    day_index: Sequence[int],
    blocks: Sequence[Block],
) -> list[ReferenceLevel]:
    """PDH/PDL din ziua ANTERIOARĂ, cu reset D3_bis la fiecare graniță de bloc.

    Prima zi din fiecare bloc → UNCLASSIFIED (nu emite nivel). `available_idx` = prima bară a
    zilei curente (Q4, fără lookahead). `day_index` provine din ancora 17:00 NY (caller-side).
    """
    out: list[ReferenceLevel] = []
    for b_i, block in enumerate(blocks):
        days = _runs(day_index, block.start, block.end)
        for k in range(1, len(days)):                 # prima zi (k=0) rămâne UNCLASSIFIED
            p0, p1 = days[k - 1]
            cur_first = days[k][0]
            pdh = max(high[j] for j in range(p0, p1 + 1))
            pdl = min(low[j] for j in range(p0, p1 + 1))
            out.append(ReferenceLevel(price=pdh, kind=LevelKind.PDH,
                                      source_period_start=p0, available_idx=cur_first, block_index=b_i))
            out.append(ReferenceLevel(price=pdl, kind=LevelKind.PDL,
                                      source_period_start=p0, available_idx=cur_first, block_index=b_i))
    return out


def compute_prior_week_levels(
    high: Sequence[float],
    low: Sequence[float],
    day_index: Sequence[int],
    week_index: Sequence[int],
    blocks: Sequence[Block],
) -> list[ReferenceLevel]:
    """Weekly High/Low din săptămâna ANTERIOARĂ, cu reset D3_bis + D-WEEK.

    Prima săptămână din fiecare bloc → UNCLASSIFIED. `days_contributing` = zile de sesiune
    distincte (`day_index`) în săptămâna sursă; `completeness` = COMPLETE (≥5) / PARTIAL (<5).
    `available_idx` = prima bară a săptămânii curente (Q4).
    """
    out: list[ReferenceLevel] = []
    for b_i, block in enumerate(blocks):
        weeks = _runs(week_index, block.start, block.end)
        for k in range(1, len(weeks)):                # prima săptămână (k=0) rămâne UNCLASSIFIED
            p0, p1 = weeks[k - 1]
            cur_first = weeks[k][0]
            wh = max(high[j] for j in range(p0, p1 + 1))
            wl = min(low[j] for j in range(p0, p1 + 1))
            n_days = len({day_index[j] for j in range(p0, p1 + 1)})
            completeness = "COMPLETE" if n_days >= 5 else "PARTIAL"
            out.append(ReferenceLevel(price=wh, kind=LevelKind.WEEKLY_HIGH,
                                      source_period_start=p0, available_idx=cur_first, block_index=b_i,
                                      days_contributing=n_days, completeness=completeness))
            out.append(ReferenceLevel(price=wl, kind=LevelKind.WEEKLY_LOW,
                                      source_period_start=p0, available_idx=cur_first, block_index=b_i,
                                      days_contributing=n_days, completeness=completeness))
    return out
