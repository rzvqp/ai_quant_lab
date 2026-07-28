"""Modulul 5 — order_flow.py: Order Block / Breaker / Mitigation / Rejection (MK, Mandat 5.8).

Primitive PURE. NU citește prețuri, NU apelează `load()`, NU rulează backtest, NU are logică de trade /
ordine / management de poziție. Inerte până când o ipoteză pre-înregistrată le folosește. mypy --strict.

Parametri RATIFICAȚI (Statistician, manifest v2.6.1 `2fb948f`, doc `3c64848`):
  - Order Block = primitivă PUR GEOMETRICĂ, zona = CORPUL `[min(Close,Open), max(Close,Open)]`. ZERO
    referință la volum (filtrul de volum ELIMINAT — coloana `volume` are proveniență neconfirmată; un
    filtru într-o primitivă persistentă s-ar moșteni tăcut de orice familie viitoare). Importat din
    `order_block_void.py` (NEATINS — tocmai a trecut auditul independent `dcc9067`).
  - Criteriul de FORMARE al OB (care lumânare DEVINE un OB) rămâne DESCHIS — `NotImplementedError`.
    Statisticianul l-a lăsat explicit neancorat (nicio familie formalizată nu-l cere).
  - Breaker / Mitigation / Rejection = definite prin REUTILIZARE a mecanicilor deja ratificate, nu invenții:
      Breaker   = criteriul de inversare E010/E012, verbatim `e010_breaker_block_snatch.py`: OB bullish
                  se inversează prima dată când CLOSE-ul unei bare cade sub PODEAUA OB = `Low_OB` (LOW-ul
                  barei OB, fitil inclus — nu podeaua corpului), simetric bearish pe close peste `High_OB`.
                  DISTINCȚIE deliberată: ZONA (pt. atingere/mitigare) = CORPUL; PODEAUA de inversare =
                  `Low_OB` (bara întreagă), exact ca E010. OB → MUTED, coordonatele re-înregistrate ca
                  Breaker cu polaritate inversată.
      Mitigation = evenimentul (a) din fereastra de valabilitate OB (atingere de FITIL = consumare D7),
                  convenția E015 `visits_for_ob`: span contiguu care SUPRAPUNE zona
                  (`low<=zone_high & high>=zone_low`), atingeri consecutive la ≤4 bare distanță unite într-o
                  SINGURĂ vizită (cooldown), numerotate secvențial, tracking-ul STOPează la primul
                  breaker-close (clasificare FORWARD-ONLY, fără lookahead).
      Rejection = mecanica D6 wick-sweep-reject, verbatim `liquidity_mechanics.detect_sweeps`: bullish OB
                  `low[i] < zone_lower AND close[i] > zone_lower` (penetrare de fitil sub podeaua corpului
                  + închidere înapoi deasupra), simetric bearish.

CONSTRÂNGERE ANTI-E010 (adăugată de CEO peste ordin, verificată la OB de Research Lab): Mitigation și
Rejection ating ACELEAȘI zone de preț ca OB. E010 a picat fiindcă fereastra de SELECȚIE și cea de MĂSURARE
erau IDENTICE (`min(j+1+480,n)` la ambele). Aici contractul e DISJUNCT PRIN CONSTRUCȚIE, nu verificat după:
  - fereastra de SELECȚIE (existența evenimentului + numărul vizitei + oprirea la breaker) = funcție PURĂ
    de barele `<= event_idx`; NICIODATĂ nu citește bare viitoare;
  - fereastra de MĂSURARE (rezultatul/reacția) = `[event_idx, event_idx + H]`, H = orizontul grupei A (20),
    strict înainte; barele `> event_idx` NU intră niciodată în selecție.
`test_order_flow.py::test_no_lookahead_*` demonstrează mecanic: mutarea barelor de după un eveniment nu
schimbă niciun eveniment cu `event_idx` anterior.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from order_block_void import GROUP_A_HORIZON, OrderBlock, OrderBlockKind

VISIT_COOLDOWN = 4  # E015: atingeri la ≤4 bare distanță = aceeași vizită


class ObLifecycle(Enum):
    ACTIVE = "active"    # OB valid, neînchis prin
    MUTED = "muted"      # OB închis prin (close dincolo de podea/plafon) → inversat în Breaker


@dataclass(frozen=True)
class Breaker:
    """OB inversat: aceeași zonă (corp), polaritate opusă, marcat la bara de flip."""
    source_ob_formation_idx: int
    source_kind: OrderBlockKind
    breaker_idx: int                 # bara la care CLOSE a depășit podeaua/plafonul (flip)
    kind: OrderBlockKind             # polaritate INVERSATĂ
    zone_lower: float                # zona re-înregistrată = corpul OB
    zone_upper: float


@dataclass(frozen=True)
class ReactionEvent:
    """Un eveniment de mitigare sau rejecție cu SEPARARE anti-E010 a ferestrelor (disjunctă prin construcție)."""
    ob_formation_idx: int
    event_idx: int
    event_type: str                  # "mitigation" | "rejection"
    visit_number: int                # secvențial, forward-only (E015), 1-based
    selection_end: int               # = event_idx; clasificarea folosește DOAR bare <= selection_end
    measurement_start: int           # = event_idx; reacția se măsoară pe [measurement_start, measurement_end)
    measurement_end: int             # = min(event_idx + H, block_end); STRICT înainte, nu alimentează selecția


def detect_order_blocks(
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    block_end: int,
) -> list[OrderBlock]:
    """Criteriul de FORMARE al OB — DESCHIS prin decizia Statisticianului (nicio familie formalizată nu-l
    cere). NU îl inventez. Zona (corp) și separarea ferestrelor sunt înghețate în `order_block_void.py`."""
    raise NotImplementedError(
        "Criteriul de FORMARE al OB (care lumânare devine candidat OB) rămâne neancorat, cf. Statistician "
        "v2.6.1. Breaker/Mitigation/Rejection primesc OB-ul ca INTRARE; formarea nu e inventată aici.")


def track_breaker(
    ob: OrderBlock, high: Sequence[float], low: Sequence[float], close: Sequence[float], block_end: int,
) -> Breaker | None:
    """Mașina de stare Breaker (E010 verbatim). OB bullish → bearish breaker prima dată când `close[i]`
    cade sub PODEAUA `Low_OB = low[formation_idx]` (bara întreagă, fitil inclus); simetric bearish pe
    `close[i] > High_OB = high[formation_idx]`. Podeaua de inversare NU e podeaua corpului — e LOW-ul barei
    OB, exact ca `e010_breaker_block_snatch.py`. Forward-only: prima depășire, fără re-armare."""
    floor = low[ob.formation_idx]      # Low_OB (fitil inclus) — E010 verbatim, NU zone_lower
    ceiling = high[ob.formation_idx]   # High_OB
    for i in range(ob.formation_idx + 1, block_end):
        if ob.kind is OrderBlockKind.BULLISH and close[i] < floor:
            return Breaker(ob.formation_idx, ob.kind, i, OrderBlockKind.BEARISH, ob.zone_lower, ob.zone_upper)
        if ob.kind is OrderBlockKind.BEARISH and close[i] > ceiling:
            return Breaker(ob.formation_idx, ob.kind, i, OrderBlockKind.BULLISH, ob.zone_lower, ob.zone_upper)
    return None


def _breaker_stop(ob: OrderBlock, high: Sequence[float], low: Sequence[float], close: Sequence[float],
                  block_end: int) -> int:
    """Bara la care tracking-ul de vizite STOPează = primul breaker-close (E015); altfel `block_end`.
    Forward-only: pentru o vizită la bara i, `i < stop` ⇔ niciun breaker în [formare, i] (info PAST-ONLY)."""
    br = track_breaker(ob, high, low, close, block_end)
    return br.breaker_idx if br is not None else block_end


def _scan_reactions(
    ob: OrderBlock, high: Sequence[float], low: Sequence[float], close: Sequence[float], block_end: int,
    event_type: str, horizon: int, cooldown: int,
) -> list[ReactionEvent]:
    """Nucleul comun Mitigation/Rejection: scanare forward-only cu cooldown E015 + separare anti-E010."""
    zl, zh = ob.zone_lower, ob.zone_upper        # ZONA = CORPUL (ratificat)
    bull = ob.kind is OrderBlockKind.BULLISH
    stop = _breaker_stop(ob, high, low, close, block_end)
    out: list[ReactionEvent] = []
    visit = 0
    last_hit: int | None = None
    for i in range(ob.formation_idx + 1, stop):
        if event_type == "mitigation":
            hit = (low[i] <= zh) and (high[i] >= zl)                 # E015: span suprapune zona
        else:  # rejection — D6 wick-sweep-reject (detect_sweeps verbatim)
            hit = (low[i] < zl and close[i] > zl) if bull else (high[i] > zh and close[i] < zh)
        if not hit:
            continue
        if last_hit is not None and (i - last_hit) <= cooldown:      # cooldown → aceeași vizită
            last_hit = i
            continue
        visit += 1
        out.append(ReactionEvent(
            ob_formation_idx=ob.formation_idx, event_idx=i, event_type=event_type, visit_number=visit,
            selection_end=i, measurement_start=i, measurement_end=min(i + horizon, block_end)))
        last_hit = i
    return out


def detect_mitigations(
    ob: OrderBlock, high: Sequence[float], low: Sequence[float], close: Sequence[float], block_end: int,
    horizon: int = GROUP_A_HORIZON, cooldown: int = VISIT_COOLDOWN,
) -> list[ReactionEvent]:
    """Mitigări (E015): atingeri de FITIL care suprapun zona-corp, cu cooldown, oprite la primul breaker.
    Fiecare eveniment poartă separarea anti-E010 (selecție `<= event_idx`, măsurare `[event_idx, +H)`)."""
    return _scan_reactions(ob, high, low, close, block_end, "mitigation", horizon, cooldown)


def detect_rejections(
    ob: OrderBlock, high: Sequence[float], low: Sequence[float], close: Sequence[float], block_end: int,
    horizon: int = GROUP_A_HORIZON, cooldown: int = VISIT_COOLDOWN,
) -> list[ReactionEvent]:
    """Rejecții (D6 sweep-reject): fitil penetrează podeaua/plafonul corpului ȘI închide înapoi înăuntru.
    Aceeași separare anti-E010 ca la mitigare — contract disjunct prin construcție, nu verificat după."""
    return _scan_reactions(ob, high, low, close, block_end, "rejection", horizon, cooldown)
