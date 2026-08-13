"""HARTA OPERAȚIONALĂ PE M15 — nivelul 3, RE-ANCORATĂ (STAT-SPEC1-N3-ZONE-MAP-CORRECTION-v1.0, 404b6c8, v2.7.61).
Înlocuiește ancorarea pe preț (`ref=close[i-1]`) a versiunii @11ae360. Funcție PURĂ pe bare M15. Fără MT5.

CAUZA RĂDĂCINĂ reparată: ancora pe PREȚ întreba „câte trăsături sunt lângă PREȚ" (răspuns mereu „toate") și
producea O SINGURĂ zonă/bară (nimic de ordonat). AMBELE defecte = unul. **Ancora se mută pe GRUPUL DE TRĂSĂTURI:
prețul ajunge la zonă; zona NU urmărește prețul.**

BANDĂ 0,25×ATR — aleasă pe TRACTABILITATE ȘI VARIABILITATE (19 zone/bară; `k` variază între zone în 91,8%), NU pe
informativitate: contorul NU discriminează față de nul la NICIO bandă (+0,15…+1,02p), a treia oară. `k` = DESCRIPTOR
etichetat „ne-discriminant vs nul", NU un scor, NU o poartă.

PATRU FAMILII NECOLINIARE (coliniaritatea dovedită în cod, `redundancy_by_static_inspection` reutilizat din bias_h1):
    level  PDH/PDL                    compute_prior_day_levels
    fvg    FVG ∪ IFVG                 detect_fvgs, detect_inverse_fvgs        (IFVG = același FVG inversat)
    pool   lichiditate                build_pools                              (bazine externe)
    ob     OB ∪ DemandZone ∪ Breaker  detect_order_blocks, detect_demand_zones, track_breaker
                                        (DemandZone ITEREAZĂ peste OB; Breaker = corp OB inversat → aceeași familie)
ATRIBUTE (NU numără în k): discount/premium (din SESSION_MID), tip, vechime, distanță. `discount` IESE din contor
(nu e locație). Familia `ob` INTRĂ (era absentă). Mulțimea nu crește, dar se SCHIMBĂ. PWH/PWL exclus (CEO). BPR
exclus (n-are localizator → ar fi primitivă nouă). ORDONARE `(distance_atr ASC, age_bars DESC, k DESC)` — arhitecturală
(proximitate=acționabilitate, vechime=persistență netestată, contor=cel mai slab), pre-înregistrată în schema_hash,
NEACORDABILĂ pe rezultate. Cheia zonei = STAT-OPPORTUNITY-IDENTITY (ancoră+bandă înghețate). CONTRACT: LevelOutput.

Non-lookahead: instanțe cu `available_idx <= i-1`, `close[i-1]` referință de distanță. Fail-closed → Unavailable.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Sequence

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

from market_state import atr14
from market_structure import Block, detect_swings, label_structure
from institutional_levels import compute_prior_day_levels
from imbalance_mechanics import detect_fvgs, detect_inverse_fvgs
from liquidity_mechanics import PoolTier, build_pools
from order_flow import detect_demand_zones, detect_order_blocks, track_breaker
from session_levels import (SessionLevelKind, compute_prior_session_levels, derive_session_index,
                            session_labels)
from level_output import LevelOutput, Ok, Unavailable

BAND_ATR_MULT: float = 0.25       # banda de confluență (TRACTABILITATE+VARIABILITATE, NU informativitate)
SORT_KEY: str = "(distance_atr ASC, age_bars DESC, k DESC)"   # ordonare ARHITECTURALĂ, în schema_hash


class Family(Enum):
    LEVEL = "level"
    FVG = "fvg"
    POOL = "pool"
    OB = "ob"


REDUNDANT_WITH: dict[str, tuple[str, ...]] = {   # dezvăluire cu două tiere: candidați care declanșează pe familie
    "level": ("CAND-0001", "CAND-0007", "CAND-0019", "CAND-0029", "CAND-0034"),
    "fvg": ("CAND-0003", "CAND-0007", "CAND-0010", "CAND-0030", "CAND-0035"),
    "pool": ("CAND-0020", "CAND-0024", "CAND-0026", "CAND-0032"),
    "ob": ("CAND-0011", "CAND-0012", "CAND-0014", "CAND-0031", "CAND-0036"),
}


@dataclass(frozen=True)
class _Instance:
    family: Family
    price: float
    available_idx: int


@dataclass(frozen=True)
class Zone:
    zone_id: str                          # cheie surogat (opportunity-identity), NU „zone@bară"
    price_anchor: float                   # media prețurilor instanțelor din grup (ancora, NU prețul curent)
    band: float                           # banda × ATR la creare, ÎNGHEȚATĂ
    composition: tuple[tuple[str, int], ...]   # tipurile prezente + număr de instanțe per tip
    k: int                                # DESCRIPTOR, etichetat „ne-discriminant vs nul"
    distance_atr: float                   # |price_anchor − close[j-1]| / ATR  — axă de ordonare
    age_bars: int                         # j − max(available_idx din grup)     — axă de ordonare
    attribute: str                        # discount / premium / unavailable (din SESSION_MID)
    relative_rank: int                    # poziția în ordonarea la bara j (1 = primul)
    evidence_available: bool              # dacă N4 a atașat descriptor (SPEC 2) — False aici (pre-N4)


@dataclass(frozen=True)
class ZoneMap:
    zones: tuple[Zone, ...]               # TOATE grupurile, ORDONATE (mulțime vidă = Ok cu zones=())
    band_atr: float
    reference_price: float
    as_of_index: int
    k_label: str                          # „descriptor, ne-discriminant vs nul"
    sort_key: str


_SCHEMA_HASH: str = hashlib.sha256(json.dumps({
    "families_ordered": [f.value for f in Family],
    "primitives": {"level": "institutional_levels", "fvg": "detect_fvgs+detect_inverse_fvgs",
                   "pool": "build_pools", "ob": "detect_order_blocks+detect_demand_zones+track_breaker"},
    "band_atr_mult": BAND_ATR_MULT, "sort_key": SORT_KEY, "k_role": "descriptor_non_discriminant",
    "discount": "attribute_not_counter", "units": "M15", "code_version": "level3-v2.0-reanchored",
}, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def _finite(x: float) -> bool:
    return x == x and x not in (float("inf"), float("-inf"))


def _day_index(time: Sequence[int]) -> np.ndarray:
    dt = pd.to_datetime(list(time), unit="s", utc=True)
    ny = dt.tz_convert("America/New_York").tz_localize(None)
    d = (ny - pd.Timedelta(hours=17)).floor("D").values.astype("datetime64[D]").astype("int64")
    return np.asarray(d, dtype=np.int64)


def _instances(high: Sequence[float], low: Sequence[float], close: Sequence[float], open_: Sequence[float],
               time: Sequence[int], n: int, ip: int, blk: list[Block]) -> list[_Instance]:
    """Instanțe active (available_idx <= i-1) per FAMILIE, cu prețul lor. Reutilizează primitivele ratificate."""
    out: list[_Instance] = []
    # level ─ PDH/PDL
    day = _day_index(time)
    for lv in compute_prior_day_levels(high, low, day.tolist(), blk):
        if lv.available_idx <= ip:
            out.append(_Instance(Family.LEVEL, float(lv.price), lv.available_idx))
    # fvg ─ FVG ∪ IFVG (o familie: IFVG e același FVG inversat)
    fvgs = detect_fvgs(high, low, blk)
    for f in list(fvgs) + list(detect_inverse_fvgs(high, low, close, fvgs, blk)):
        if f.confirmed_idx <= ip:
            out.append(_Instance(Family.FVG, float(f.ce_50), f.confirmed_idx))
    # pool ─ lichiditate externă
    swings = label_structure(detect_swings(high, low, blk, k=2))
    for p in build_pools(swings, PoolTier.EXTERNAL):
        if p.available_idx <= ip:
            out.append(_Instance(Family.POOL, float(p.price), p.available_idx))
    # ob ─ OB ∪ DemandZone ∪ Breaker (o familie: DemandZone iterează OB; Breaker = corp OB inversat)
    obs = detect_order_blocks(open_, high, low, close, n)
    for ob in obs:
        if ob.formation_idx <= ip:
            out.append(_Instance(Family.OB, 0.5 * (ob.zone_lower + ob.zone_upper), ob.formation_idx))
        br = track_breaker(ob, high, low, close, n)
        if br is not None and br.breaker_idx <= ip:            # bara de flip = disponibilitate breaker
            out.append(_Instance(Family.OB, 0.5 * (br.zone_lower + br.zone_upper), br.breaker_idx))
    for dz in detect_demand_zones(open_, high, low, close, n):
        if dz.formation_idx <= ip:
            out.append(_Instance(Family.OB, 0.5 * (dz.zone_lower + dz.zone_upper), dz.formation_idx))
    return out


def _cluster(instances: list[_Instance], band: float) -> list[list[_Instance]]:
    """Grupare geometrică single-linkage: instanțe la <= band una de alta intră în același grup. Ancora = grupul."""
    if not instances:
        return []
    ordered = sorted(instances, key=lambda x: x.price)
    groups: list[list[_Instance]] = [[ordered[0]]]
    for inst in ordered[1:]:
        if inst.price - groups[-1][-1].price <= band:          # prag de legătură = banda de confluență
            groups[-1].append(inst)
        else:
            groups.append([inst])
    return groups


def _attribute(price_anchor: float, high: Sequence[float], low: Sequence[float], time: Sequence[int],
               ip: int, n: int, blk: list[Block]) -> str:
    """discount/premium al zonei față de SESSION_MID viu; UNAVAILABLE dacă niciun Mid viu (NU FALSE)."""
    sidx = derive_session_index([int(t) for t in time]); slab = session_labels([int(t) for t in time])
    mids = [lv for lv in compute_prior_session_levels(high, low, sidx, slab, blk)
            if lv.kind is SessionLevelKind.SESSION_MID and lv.available_idx <= ip <= lv.expiry_idx]
    if not mids:
        return "unavailable"
    mid = max(mids, key=lambda lv: lv.available_idx)
    return "discount" if price_anchor < mid.price else "premium"


def build_zone_map(
    high: Sequence[float], low: Sequence[float], close: Sequence[float], open_: Sequence[float],
    time: Sequence[int], *, atr: Sequence[float] | None = None, band_mult: float = BAND_ATR_MULT,
    regime_available: bool = True, bias_available: bool = True,
) -> LevelOutput[ZoneMap]:
    """Harta RE-ANCORATĂ la bara curentă: enumeră instanțe → grupează geometric → ordonează. CONTRACT LevelOutput.
    `Ok(ZoneMap(zones=()))` (nicio zonă) e un REZULTAT; `Unavailable` = n-am putut calcula (fail-closed)."""
    n = len(close)
    i = n - 1
    if n < 2:
        return Unavailable(reason="incomplete_window", as_of=i)
    if not (regime_available and bias_available):
        return Unavailable(reason="cascade_level1_or_level2_unavailable", as_of=i)   # nivel 1/2 în mulțimea necesară
    ref = float(close[i - 1])
    a = float(atr[i - 1]) if atr is not None else atr14(high, low, close)[i - 1]
    if not _finite(a) or a <= 0.0:
        return Unavailable(reason="atr_unavailable", as_of=i)
    band = band_mult * a
    ip = i - 1
    blk = [Block(0, n)]

    groups = _cluster(_instances(high, low, close, open_, time, n, ip, blk), band)
    zones_unranked: list[Zone] = []
    for gi, g in enumerate(groups):
        prices = [inst.price for inst in g]
        anchor = float(sum(prices) / len(prices))
        fams: dict[Family, int] = {}
        for inst in g:
            fams[inst.family] = fams.get(inst.family, 0) + 1
        comp = tuple((f.value, fams[f]) for f in Family if f in fams)
        k = len(fams)                                          # familii DISTINCTE (descriptor)
        age = i - max(inst.available_idx for inst in g)
        zones_unranked.append(Zone(
            zone_id=f"grp{gi}@anchor{anchor:.5f}", price_anchor=anchor, band=band, composition=comp, k=k,
            distance_atr=abs(anchor - ref) / a, age_bars=age,
            attribute=_attribute(anchor, high, low, time, ip, n, blk), relative_rank=0, evidence_available=False))

    ranked = sorted(zones_unranked, key=lambda z: (z.distance_atr, -z.age_bars, -z.k))   # (dist ASC, age DESC, k DESC)
    zones = tuple(
        Zone(zone_id=z.zone_id, price_anchor=z.price_anchor, band=z.band, composition=z.composition, k=z.k,
             distance_atr=round(z.distance_atr, 6), age_bars=z.age_bars, attribute=z.attribute,
             relative_rank=r + 1, evidence_available=z.evidence_available)
        for r, z in enumerate(ranked))
    zmap = ZoneMap(zones=zones, band_atr=band_mult, reference_price=ref, as_of_index=i,
                   k_label="descriptor_non_discriminant_vs_null", sort_key=SORT_KEY)
    return Ok(value=zmap, as_of=i, valid_until=i + 1, schema_hash=_SCHEMA_HASH)
