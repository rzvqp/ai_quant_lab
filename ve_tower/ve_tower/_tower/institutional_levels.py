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
  Q3-săptămână (granița de săptămână) — RESOLVED (v2.5.6): derivat din Q3-day (17:00 NY), NU ancoră
     nouă — `week_index` incrementează la prima bară după un gol de >1 zi calendaristică (weekendul).
     Helper `derive_week_index` (caller-side).
  Q4 (lag / disponibilitate, analog D1) — RATIFICAT.  `available_idx` = prima bară a perioadei
     curente — mecanic forțat, lookahead-safe. Implementat.
  Q5 (consumare) — RATIFICAT (analog D7): un PDH maturat NU rămâne activ la a doua atingere în
     aceeași zi — consumat la prima atingere în fereastra zilnică. `detect_level_touches`.
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


def derive_week_index(day_ordinal: Sequence[int]) -> list[int]:
    """Derivă `week_index` din golul de weekend (MK-04 Q3-week, RESOLVED): incrementează la prima
    bară a cărei zi urmează unui gol de >1 zi calendaristică față de ziua anterioară în bloc — NU
    o ancoră nouă, ci derivat din Q3-day (17:00 NY) deja rezolvat.

    `day_ordinal[i]` = ordinalul zilei calendaristice (17:00-NY) al barei i (monoton, cu goluri la
    weekend). Derivare CALLER-SIDE — modulele de niveluri primesc `week_index`; asta doar îl produce.
    """
    out: list[int] = []
    week = 0
    prev_day: int | None = None
    for d in day_ordinal:
        if prev_day is not None and d != prev_day and d - prev_day > 1:
            week += 1                                    # gol >1 zi = weekend → săptămână nouă
        out.append(week)
        prev_day = d
    return out


@dataclass(frozen=True)
class LevelTouch:
    """Prima atingere a unui nivel PDH/PDL în fereastra lui de disponibilitate (consumare D7)."""
    level: ReferenceLevel
    touch_idx: int
    block_index: int


def detect_level_touches(
    high: Sequence[float],
    low: Sequence[float],
    levels: Sequence[ReferenceLevel],
    day_index: Sequence[int],
    blocks: Sequence[Block],
) -> list[LevelTouch]:
    """Prima atingere a fiecărui nivel PDH/PDL, consumat O DATĂ (D7, MK-04 Q5): un PDH maturat NU
    rămâne activ la a doua atingere în ACEEAȘI zi.

    Atingere = fitilul ajunge la nivel: `high[j] >= price` (PDH/rezistență) / `low[j] <= price`
    (PDL/suport). Fereastra de disponibilitate = de la `available_idx` până la ultima bară a
    aceleiași zile (`day_index`), în același bloc (D4). Doar niveluri zilnice (PDH/PDL); nivelurile
    săptămânale au altă fereastră și se sar aici.
    """
    block_of = {b_i: block for b_i, block in enumerate(blocks)}
    out: list[LevelTouch] = []
    for lv in levels:
        if lv.kind not in (LevelKind.PDH, LevelKind.PDL):
            continue                                     # doar fereastra zilnică
        block = block_of.get(lv.block_index)
        if block is None:
            continue
        day = day_index[lv.available_idx]
        for j in range(lv.available_idx, block.end):
            if day_index[j] != day:                      # a ieșit din ziua curentă
                break
            touched = high[j] >= lv.price if lv.kind is LevelKind.PDH else low[j] <= lv.price
            if touched:
                out.append(LevelTouch(level=lv, touch_idx=j, block_index=lv.block_index))
                break                                    # consumat la prima atingere (D7), fără re-armare
    return out
