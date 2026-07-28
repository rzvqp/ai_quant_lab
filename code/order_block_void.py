"""Order Block + Liquidity Void — definiții ÎNGHEȚATE (MK Modul 5, manifest v2.5.9, 444e0e8).

Definiții pure. NU citește date, NU apelează `load()`, NU rulează backtest. Inert până când o
ipoteză pre-înregistrată le folosește.

LIQUIDITY VOID (definition_3, RATIFICAT — prag DERIVAT, criteriu HIBRID):
  O tranziție de bară c→c+1 e Void DACĂ ORICARE:
    (temporal) time[c+1]−time[c] > 900s, EXCLUZÂND fereastra de mentenanță zilnică (mins≤75 ȘI
               ora(time[c]) ∈ {20,21} UTC — reutilizat VERBATIM din code/gapfind.py). Weekend-urile
               INCLUSE (redeschiderile de weekend SUNT void-uri temporale — vezi why_hybrid).
    (mărime)   |Open[c+1] − Close[c]| > $1,20  (= 3× cost_round_trip $0,40, derivat, nu ales).
  Hibrid pentru că niciun criteriu singur nu acoperă conceptul: gap-uri de mărime fără pauză
  (slippage CPI) invizibile la timp; pauze fără salt (redeschideri) invizibile la mărime.

ORDER BLOCK (definition_2, RATIFICAT cu 2 corecții):
  ZONA = CORPUL, [Close, Open] (bearish: Close_Bdown..Open_Bdown, Open>Close). NU [Open, Low]
  (corp+fitil) — fitilul are rol EXCLUSIV de atingere (D6), includerea lui ar face „atingerea OB"
  ambiguă. SEPARAREA FERESTRELOR (pre-împotriva circularității E010, structurală, NU verificare adăugată):
    (1) fereastra de VALABILITATE: OB activ de la formare până la ORICARE: (a) atingere de FITIL în zonă
        (consumare analog D7, o dată, fără re-armare) SAU (b) CLOSE decisiv dincolo de zonă (devine
        „breaker" — verbatim din criteriul de inversare E010/E012). (a) și (b) sunt evenimente DIFERITE;
        (a) NU implică (b).
    (2) fereastra de MĂSURARE: începe DOAR la bara evenimentului calificator (a) sau (b), NICIODATĂ la
        formare — orizontul grupei A (20 bare) rulează înainte de ACOLO. Prin construcție, cele două
        ferestre nu pot colapsa în aceeași (spre deosebire de E010, unde erau identice).

ÎNTREBARE DESCHISĂ (enumerată, nerezolvată): criteriul de FORMARE al OB (care lumânare DEVINE un OB) NU
e specificat în definiție — doar ZONA și separarea ferestrelor sunt. Aici OB-urile se primesc ca intrare
(formation_idx, kind, zone). BLOCHEAZĂ detectarea autonomă a OB; NU blochează zona/ferestrele. Ce trebuie
decis: criteriul de formare (ex. ultima lumânare opusă înainte de un BOS).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

COST_ROUND_TRIP = 0.40
VOID_SIZE_THRESHOLD = 3.0 * COST_ROUND_TRIP     # $1.20, derivat (3x cost)
BAR_SECONDS = 900
GROUP_A_HORIZON = 20


class VoidKind(Enum):
    TEMPORAL = "temporal"
    SIZE = "size"
    BOTH = "both"


@dataclass(frozen=True)
class LiquidityVoid:
    at_idx: int          # tranziția c→c+1: `at_idx` = c
    kind: VoidKind
    gap_seconds: int
    price_jump: float     # |Open[c+1] − Close[c]|


def _is_maintenance(epoch_c: int, gap_seconds: int) -> bool:
    """Fereastra de mentenanță zilnică, verbatim din gapfind.py: gap ≤75min ȘI ora(c) ∈ {20,21} UTC."""
    import datetime as _dt
    hour = _dt.datetime.fromtimestamp(epoch_c, tz=_dt.timezone.utc).hour
    return gap_seconds <= 75 * 60 and hour in (20, 21)


def detect_liquidity_voids(
    open_: Sequence[float], close: Sequence[float], time: Sequence[int],
    size_threshold: float = VOID_SIZE_THRESHOLD,
) -> list[LiquidityVoid]:
    """Void-uri hibride (temporal SAU mărime) pe tranzițiile c→c+1. Vezi docstring-ul modulului."""
    out: list[LiquidityVoid] = []
    for c in range(len(close) - 1):
        gap = int(time[c + 1]) - int(time[c])
        temporal = gap > BAR_SECONDS and not _is_maintenance(int(time[c]), gap)
        jump = abs(float(open_[c + 1]) - float(close[c]))
        size = jump > size_threshold
        if temporal and size:
            out.append(LiquidityVoid(c, VoidKind.BOTH, gap, jump))
        elif temporal:
            out.append(LiquidityVoid(c, VoidKind.TEMPORAL, gap, jump))
        elif size:
            out.append(LiquidityVoid(c, VoidKind.SIZE, gap, jump))
    return out


class OrderBlockKind(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"


@dataclass(frozen=True)
class OrderBlock:
    formation_idx: int
    kind: OrderBlockKind
    zone_lower: float     # = min(Close, Open) — CORPUL, fără fitil
    zone_upper: float     # = max(Close, Open)


@dataclass(frozen=True)
class ObValidityEvent:
    """Evenimentul care ÎNCHEIE fereastra de valabilitate și DESCHIDE fereastra de măsurare."""
    ob_formation_idx: int
    event_idx: int
    event_type: str       # "wick_touch" (a) sau "breaker_close" (b) — evenimente DIFERITE
    measurement_start: int
    measurement_end: int   # event_idx + GROUP_A_HORIZON (măsurarea rulează de la eveniment, nu de la formare)


def order_block_zone(open_bar: float, close_bar: float) -> tuple[float, float]:
    """Zona OB = CORPUL [min(Close,Open), max(Close,Open)]. Fitilul e EXCLUS (rol de atingere, D6)."""
    return (min(close_bar, open_bar), max(close_bar, open_bar))


def resolve_validity_and_measurement(
    ob: OrderBlock, high: Sequence[float], low: Sequence[float], close: Sequence[float],
    block_end: int, horizon: int = GROUP_A_HORIZON,
) -> ObValidityEvent | None:
    """Separarea ferestrelor (anti-E010): caută primul eveniment calificator după formare —
    (a) atingere de FITIL în zonă SAU (b) CLOSE decisiv dincolo de zonă — și pornește măsurarea DE ACOLO.

    NEIMPLEMENTAT parțial: (a)/(b) sunt specificate, dar declanșarea depinde de criteriul de FORMARE al
    OB (întrebare deschisă) și de direcția „dincolo de zonă" per tip. Structura ferestrelor e înghețată;
    detectarea evenimentului rămâne de completat odată ce formarea e ratificată.
    """
    raise NotImplementedError(
        "OB: zona + separarea ferestrelor sunt înghețate; declanșarea (a)/(b) depinde de criteriul de "
        "FORMARE al OB, întrebare deschisă (vezi docstring-ul modulului).")
