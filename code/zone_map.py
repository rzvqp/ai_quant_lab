"""HARTA OPERAȚIONALĂ PE M15 — nivelul 3 (STAT-LEVEL2-CONDITION-AND-LEVEL3-ZONE-MAP-SPEC-v1.0, a595cc5,
manifest v2.7.52, Partea 3). Funcție PURĂ pe bare M15. Fără MT5, fără date reale.

NU E UN SCOR PONDERAT — E UN CONTOR NEPONDERAT. Ponderile NU se pot deriva la nivelul 3: a le deriva = a le
potrivi pe un REZULTAT = a ESTIMA = nivelul 6 (al doilea estimator + problemă de selecție, respins deja la
nivelul 2). Formatul CEO conținea răspunsul: „5/6" e un contor neponderat. Nivelul 3 emite SETUL DE TRĂSĂTURI +
CONTORUL + ordonarea; „confidence" vine de la nivelul 6, condiționat pe celula de confluență. Un singur estimator.

CELE PATRU TRĂSĂTURI RATIFICATE (proximitate 1×ATR), din primitive (redundanță dezvăluită, două tiere — L-R1):
  pdh_pdl    ← institutional_levels (PDH/PDL)            declanșatori: CAND-0001/0007/0019/0029/0034 ...
  fvg        ← imbalance_mechanics (FVG)                 declanșatori: CAND-0003/0007/0010/0030/0035
  liquidity  ← build_pools ← swings                      declanșatori: CAND-0020/0024/0025/0026/0032
  discount   ← session_levels (SESSION_MID, DEFINIT)     declanșatori: CAND-0028/0033
ZERO trăsături complet independente (ca la nivelul 2); ȘTIRILE rămân singura axă independentă.

PRAGUL, DERIVAT: k>=4 (confluență TOTALĂ). La 1×ATR harta e SATURATĂ (măsurat: 3/4 trăsături coincid pe 94,87%
din bare; k=4 42,82%). Doar cerința TOTALĂ lasă un complement material (57,18% bare fără zonă calificată >=50%,
falsificabil). **Derivarea e COMUNĂ pe (BANDĂ, k)** — banda saturează contorul înainte ca pragul să conteze; banda
intră în `schema_hash` alături de k. A PATRA oară aceeași saturație (primitiva B, bazinele nivel 2, confluența M15).

DISCOUNT/PREMIUM (§3.4): DEFINIT din `SESSION_MID` ratificat, FĂRĂ primitivă nouă (aritmetică preț-vs-Mid):
  DISCOUNT  close[i-1] < Mid(sesiunii anterioare, neexpirat)   PREMIUM  close[i-1] > Mid
  niciun Mid viu ⇒ trăsătura UNAVAILABLE, NU FALSE.
⚠ INTERPRETARE VE (semnalată Red Team): trăsătura CONTRIBUIE la contor când e DEFINITĂ (Mid viu — discount SAU
premium); direcția (discount/premium) e un atribut dezvăluit, nu schimbă prezența. `SESSION_MID` e primitiva pe
care declanșează CAND-0028/0033 ⇒ pentru ei, discount NU e context independent.

GRANIȚA (non-lookahead): trăsăturile la bara `i` citesc DOAR bare <= i-1 (referință = close[i-1]; structuri cu
`available_idx <= i-1`). Test prin perturbare. CONSTANTE: doar unități M15 (ZI 92 / SĂPTĂMÂNĂ 460 SUNT corecte pe
M15 — 460 a fost transplant pe H4, NU aici). NU emite „confidence".

FAIL-CLOSED: fereastră incompletă / ATR nefinit → UNAVAILABLE (NU k=0); Mid absent → discount UNAVAILABLE (NU
FALSE); nivel 1 sau 2 UNAVAILABLE → cascadă UNAVAILABLE; nicio zonă peste prag → MULȚIME VIDĂ (rezultat valid).
∀ bară cu ZoneMap UNAVAILABLE sau mulțime vidă ⇒ nivelul 6 == NO_TRADE.
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
from imbalance_mechanics import detect_fvgs
from liquidity_mechanics import PoolTier, build_pools
from session_levels import (SessionLevelKind, compute_prior_session_levels, derive_session_index,
                            session_labels)

BAND_ATR_MULT: float = 1.0       # banda de proximitate; JOINT cu k în schema_hash (banda saturează contorul)
THRESHOLD_K: int = 4             # confluență TOTALĂ (derivat: singurul care satisface falsificabilitatea)
FEATURE_NAMES: tuple[str, ...] = ("pdh_pdl", "fvg", "liquidity", "discount")
REDUNDANT_WITH: dict[str, tuple[str, ...]] = {   # dezvăluire cu două tiere (L-R1): candidați care declanșează pe fiecare
    "pdh_pdl": ("CAND-0001", "CAND-0007", "CAND-0019", "CAND-0029", "CAND-0034"),
    "fvg": ("CAND-0003", "CAND-0007", "CAND-0010", "CAND-0030", "CAND-0035"),
    "liquidity": ("CAND-0020", "CAND-0024", "CAND-0025", "CAND-0026", "CAND-0032"),
    "discount": ("CAND-0028", "CAND-0033"),
}


class Status(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class Zone:
    zone_id: str
    features: tuple[str, ...]              # trăsăturile PREZENTE (contorizate)
    k: int                                 # contorul de confluență (neponderat)
    feature_status: tuple[tuple[str, str], ...]   # (nume, AVAILABLE/UNAVAILABLE) pentru toate cele 4
    redundant_with: tuple[str, ...]        # candidați care declanșează pe trăsăturile prezente
    direction: str | None                  # discount/premium (atribut dezvăluit), None dacă discount absent/UNAVAILABLE


@dataclass(frozen=True)
class ZoneMap:
    zones: tuple[Zone, ...]                # peste prag, ordonate descrescător după k (mulțime vidă = rezultat valid)
    ranked_by_k: tuple[int, ...]
    counter_k: int | None                  # contorul la referință (înainte de prag)
    threshold_k: int
    band_atr: float
    reference_price: float | None
    as_of_index: int
    status: str
    reason: str
    schema_hash: str


_SCHEMA_HASH: str = hashlib.sha256(json.dumps({
    "features_ordered": list(FEATURE_NAMES),
    "primitives": {"pdh_pdl": "institutional_levels", "fvg": "imbalance_mechanics",
                   "liquidity": "build_pools<-swings", "discount": "session_levels.SESSION_MID"},
    "band_atr_mult": BAND_ATR_MULT, "threshold_k": THRESHOLD_K,   # JOINT (bandă, k)
    "units": "M15", "code_version": "level3-v1.0",
}, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def _fail(reason: str, as_of: int) -> ZoneMap:
    return ZoneMap(zones=(), ranked_by_k=(), counter_k=None, threshold_k=THRESHOLD_K, band_atr=BAND_ATR_MULT,
                   reference_price=None, as_of_index=as_of, status=Status.UNAVAILABLE.value, reason=reason,
                   schema_hash=_SCHEMA_HASH)


def _finite(x: float) -> bool:
    return x == x and x not in (float("inf"), float("-inf"))


def _day_index(time: Sequence[int]) -> np.ndarray:
    dt = pd.to_datetime(list(time), unit="s", utc=True)
    ny = dt.tz_convert("America/New_York").tz_localize(None)
    d = (ny - pd.Timedelta(hours=17)).floor("D").values.astype("datetime64[D]").astype("int64")
    return np.asarray(d, dtype=np.int64)


def _assemble(present: dict[str, bool], status: dict[str, str], direction: str | None,
              reference: float, as_of: int) -> ZoneMap:
    """Pur: din prezența/statusul celor 4 trăsături → ZoneMap. Contor NEPONDERAT; prag = confluență totală."""
    counter_k = sum(1 for nm in FEATURE_NAMES if present.get(nm, False))
    fstatus = tuple((nm, status.get(nm, Status.AVAILABLE.value)) for nm in FEATURE_NAMES)
    if counter_k >= THRESHOLD_K:
        feats = tuple(nm for nm in FEATURE_NAMES if present.get(nm, False))
        red: tuple[str, ...] = tuple(sorted({c for nm in feats for c in REDUNDANT_WITH.get(nm, ())}))
        zone = Zone(zone_id=f"zone@{as_of}", features=feats, k=counter_k, feature_status=fstatus,
                    redundant_with=red, direction=direction)
        return ZoneMap(zones=(zone,), ranked_by_k=(counter_k,), counter_k=counter_k, threshold_k=THRESHOLD_K,
                       band_atr=BAND_ATR_MULT, reference_price=reference, as_of_index=as_of,
                       status=Status.AVAILABLE.value, reason="mapped", schema_hash=_SCHEMA_HASH)
    return ZoneMap(zones=(), ranked_by_k=(), counter_k=counter_k, threshold_k=THRESHOLD_K, band_atr=BAND_ATR_MULT,
                   reference_price=reference, as_of_index=as_of, status=Status.AVAILABLE.value,
                   reason="empty_set_below_threshold", schema_hash=_SCHEMA_HASH)


def _near_level(prices: Sequence[float], avail: Sequence[int], ref: float, band: float, i_prev: int) -> bool:
    return any(av <= i_prev and abs(p - ref) <= band for p, av in zip(prices, avail))


def build_zone_map(
    high: Sequence[float], low: Sequence[float], close: Sequence[float], time: Sequence[int],
    *, atr: Sequence[float] | None = None, band_mult: float = BAND_ATR_MULT, threshold_k: int = THRESHOLD_K,
    regime_available: bool = True, bias_available: bool = True,
) -> ZoneMap:
    """Harta de confluență la bara CURENTĂ (ultima). Enumeră trăsăturile active, numără coincidențele (contor
    neponderat), emite lista ordonată peste pragul de confluență totală. PURĂ, cauzală (citește bare <= i-1)."""
    n = len(close)
    i = n - 1
    if n < 2:
        return _fail("incomplete_window", i)                    # nevoie de close[i-1]
    if not (regime_available and bias_available):
        return _fail("cascade_level1_or_level2_unavailable", i)  # nivel 1/2 UNAVAILABLE → cascadă
    ref = float(close[i - 1])
    a = float(atr[i - 1]) if atr is not None else atr14(high, low, close)[i - 1]
    if not _finite(a) or a <= 0.0:
        return _fail("atr_unavailable", i)
    band = band_mult * a
    ip = i - 1                                                  # ultima bară citibilă (non-lookahead)
    blk = [Block(0, n)]

    # ── trăsătura 1: PDH/PDL în bandă ──
    day = _day_index(time)
    levels = compute_prior_day_levels(high, low, day.tolist(), blk)
    present_pdh = _near_level([lv.price for lv in levels], [lv.available_idx for lv in levels], ref, band, ip)

    # ── trăsătura 2: FVG în bandă (confirmat <= i-1, zona atinge [ref-band, ref+band]) ──
    fvgs = detect_fvgs(high, low, blk)
    present_fvg = any(f.confirmed_idx <= ip and f.lower <= ref + band and f.upper >= ref - band for f in fvgs)

    # ── trăsătura 3: lichiditate (bazin) în bandă ──
    swings = label_structure(detect_swings(high, low, blk, k=2))
    pools = build_pools(swings, PoolTier.EXTERNAL)
    present_liq = _near_level([p.price for p in pools], [p.available_idx for p in pools], ref, band, ip)

    # ── trăsătura 4: discount/premium DEFINIT din SESSION_MID viu ──
    sidx = derive_session_index([int(t) for t in time]); slab = session_labels([int(t) for t in time])
    mids = [lv for lv in compute_prior_session_levels(high, low, sidx, slab, blk)
            if lv.kind is SessionLevelKind.SESSION_MID and lv.available_idx <= ip <= lv.expiry_idx]
    if not mids:
        present_disc, disc_status, direction = False, Status.UNAVAILABLE.value, None   # niciun Mid viu → UNAVAILABLE
    else:
        mid = max(mids, key=lambda lv: lv.available_idx)        # cel mai recent Mid viu (sesiunea anterioară)
        present_disc, disc_status = True, Status.AVAILABLE.value
        direction = "discount" if ref < mid.price else "premium"

    present = {"pdh_pdl": present_pdh, "fvg": present_fvg, "liquidity": present_liq, "discount": present_disc}
    status = {"pdh_pdl": Status.AVAILABLE.value, "fvg": Status.AVAILABLE.value,
              "liquidity": Status.AVAILABLE.value, "discount": disc_status}
    return _assemble(present, status, direction, ref, i)
