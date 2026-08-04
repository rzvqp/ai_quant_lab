"""Liquidity mechanics — MK-02.

RATIFICAT (manifest v2.7.39, commit `2d795bc`). Cod verificat: fidelitate (Statistician),
executabilitate + leakage (VE), atac adversarial (Red Team). NU mai e draft.
(Corecție de header cerută de Alpha — text, zero schimbare de cod.)

Definiții pure. NU citește date, NU apelează `load()`, NU cunoaște manifestul.

Depinde de `market_structure` pentru `Block`, `Swing`, `StructureLabel`.

PATRU DECIZII DE PROIECTARE care necesită ratificarea Statisticianului:

  D4  Bazine externe și goluri. Bazinele externe se derivă din HH/LL pe
      contextul HTF. Fișierele HTF derivate au GOLURI reale între blocurile
      de descoperire. Un bazin format înaintea unui gol NU supraviețuiește
      după el — se invalidează la granița de bloc. Fără această regulă, un
      nivel format înainte de o regiune sigilată ar fi măturat după ea.

  D5  Alinierea M5. Specificația cere bazine interne din fractali M5 mapați
      pe structura M15. Contextul HTF aliniat pe M5 NU EXISTĂ — fișierele
      derivate sunt block-local pe blocurile M15_v2, iar ferestrele de
      descoperire M5 nu sunt acoperite. Corecția 2026 are zero bare H4.

      Modulul acceptă orice serie de bare cu blocurile ei, deci e agnostic
      la timeframe. Dar maparea cross-timeframe M5 → M15 NU e implementată
      aici; cere un artefact de aliniere care nu există în manifest.

  D6  Sweep fără lookahead. Semnătura wick-sweep se evaluează integral pe
      bara curentă: low[c] < pool ȘI close[c] > pool. Nu cere bare viitoare.
      Aceasta e singura primitivă din MK-01/MK-02 fără lookahead.

  D7  Consumarea bazinului. Un bazin măturat se marchează consumat și nu mai
      produce semnale. Alternativa — bazine care rămân active după măturare —
      e menționată dar neimplementată; ar cere o regulă de re-armare.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from market_structure import Block, StructureLabel, Swing, SwingKind


class PoolTier(Enum):
    EXTERNAL = "external"
    """Derivat din HH/LL pe context HTF."""

    INTERNAL = "internal"
    """Derivat din fractali minori pe timeframe de execuție. Inducement."""


class PoolSide(Enum):
    ABOVE = "above"
    """Lichiditate deasupra pieței — stopuri de short, buy-stops."""

    BELOW = "below"
    """Lichiditate sub piață — stopuri de long, sell-stops."""


@dataclass(frozen=True)
class LiquidityPool:
    price: float
    formed_idx: int
    """Bara pe care s-a format extremul."""

    available_idx: int
    """Bara de la care bazinul e cunoscut. Egal cu confirmed_idx al swing-ului."""

    side: PoolSide
    tier: PoolTier
    block_index: int
    source_label: StructureLabel


@dataclass(frozen=True)
class SweepEvent:
    idx: int
    """Bara pe care s-a produs măturarea."""

    pool: LiquidityPool
    penetration: float
    """Cât de adânc a trecut extremul dincolo de bazin, în unități de preț."""

    close_back_inside: bool
    """True dacă închiderea a revenit în range. Semnătura wick-sweep."""

    block_index: int


def build_pools(
    swings: Sequence[Swing],
    tier: PoolTier,
) -> list[LiquidityPool]:
    """Construiește bazine din swing-uri etichetate.

    HH și LH produc bazine ABOVE. HL și LL produc bazine BELOW.
    Swing-urile UNCLASSIFIED se ignoră — nu au referință structurală.

    D4: `block_index` se propagă. Consumatorii trebuie să respecte granițele.
    """
    out: list[LiquidityPool] = []

    for s in swings:
        if s.label is StructureLabel.UNCLASSIFIED:
            continue

        side = PoolSide.ABOVE if s.kind is SwingKind.HIGH else PoolSide.BELOW

        out.append(
            LiquidityPool(
                price=s.price,
                formed_idx=s.idx,
                available_idx=s.confirmed_idx,
                side=side,
                tier=tier,
                block_index=s.block_index,
                source_label=s.label,
            )
        )

    return out


def detect_sweeps(
    high: Sequence[float],
    low: Sequence[float],
    close: Sequence[float],
    pools: Sequence[LiquidityPool],
    blocks: Sequence[Block],
    require_close_back_inside: bool = True,
) -> list[SweepEvent]:
    """Detectează măturări de lichiditate.

    Semnătura wick-sweep, pentru un bazin BELOW la preț p:

        low[c] < p        extremul a trecut dincolo
        close[c] > p      închiderea a revenit în range

    Simetric pentru ABOVE: high[c] > p și close[c] < p.

    D6: ambele condiții se evaluează pe bara c. Fără lookahead.

    D4: un bazin e activ doar în blocul lui, de la available_idx până la
    sfârșitul blocului sau până la consumare. Nu supraviețuiește unei granițe.

    D7: după măturare, bazinul e consumat și nu mai produce semnale.

    Dacă `require_close_back_inside` e False, se raportează orice penetrare,
    inclusiv rupturi cu închidere dincolo. Util pentru a distinge măturarea
    de ruperea structurală, dar nu e semnătura wick-sweep.
    """
    out: list[SweepEvent] = []

    for b_i, block in enumerate(blocks):
        active = [
            p
            for p in pools
            if p.block_index == b_i and block.start <= p.available_idx < block.end
        ]
        consumed: set[int] = set()

        for c in range(block.start, block.end):
            for k, pool in enumerate(active):
                if k in consumed:
                    continue
                if pool.available_idx >= c:
                    continue

                if pool.side is PoolSide.BELOW:
                    penetrated = low[c] < pool.price
                    back_inside = close[c] > pool.price
                    depth = pool.price - low[c]
                else:
                    penetrated = high[c] > pool.price
                    back_inside = close[c] < pool.price
                    depth = high[c] - pool.price

                if not penetrated:
                    continue
                if require_close_back_inside and not back_inside:
                    continue

                out.append(
                    SweepEvent(
                        idx=c,
                        pool=pool,
                        penetration=depth,
                        close_back_inside=back_inside,
                        block_index=b_i,
                    )
                )
                consumed.add(k)

    return out


def sweep_against_reference(
    high: Sequence[float],
    low: Sequence[float],
    close: Sequence[float],
    reference_price: Sequence[float],
    blocks: Sequence[Block],
    side: PoolSide,
) -> list[int]:
    """Variantă pentru referințe de nivel — PDH, PDL, deschidere de sesiune.

    `reference_price[i]` e nivelul valabil la bara i. Se presupune deja
    aliniat și lag-uit corect de apelant; acest modul nu îl derivă.

    Returnează indicii barelor cu semnătură wick-sweep.

    Notă: dacă `reference_price` e derivat din bare ale zilei curente fără lag,
    conține lookahead. Responsabilitatea alinierii e a apelantului.
    """
    out: list[int] = []

    for block in blocks:
        for c in range(block.start, block.end):
            ref = reference_price[c]

            if side is PoolSide.BELOW:
                if low[c] < ref and close[c] > ref:
                    out.append(c)
            else:
                if high[c] > ref and close[c] < ref:
                    out.append(c)

    return out
