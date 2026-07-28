"""Market structure primitives — MK-01.

DRAFT DE REFERINȚĂ. Nu e cod verificat. Necesită implementare, testare și
ratificare de o divizie, conform separării producător/verificator din
CROSS-VERIFY-SPEC.

Definiții pure. Acest modul NU citește date, NU apelează `load()`, NU cunoaște
manifestul. Primește array-uri și granițe de bloc; returnează structuri.

Conformitate `no_unregistered_research_lines_rule`: modulul rămâne inert până
când o ipoteză pre-înregistrată formal îl folosește.

TREI DECIZII DE PROIECTARE care necesită ratificarea Statisticianului:

  D1  Lookahead. Un fractal k=2 la bara i nu poate fi cunoscut înainte de bara
      i+k. Fiecare swing returnează AMBII indici: `idx` (unde e extremul) și
      `confirmed_idx = idx + k` (de unde e cunoscut). Orice consumator forward
      trebuie să folosească `confirmed_idx`.

  D2  Departajare. Specificația scrie `High[i] == max(High[i-k..i+k])`, care
      acceptă egalități — două bare cu același maxim s-ar califica amândouă.
      Implementarea de aici cere inegalitate STRICTĂ pe ambele laturi, deci
      egalitățile nu produc swing. Alternativa — strict la stânga, non-strict
      la dreapta — e menționată dar neimplementată.

  D3  Granițe de bloc. Datele de descoperire au goluri reale între blocuri,
      separate de benzi de carantină. Mașina de stare se RESETEAZĂ la fiecare
      început de bloc, iar niciun swing nu poate avea fereastra traversând o
      graniță. Fără asta, structura de dinaintea unei regiuni sigilate ar fi
      moștenită după ea, anulând carantina.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final, Sequence

K_DEFAULT: Final[int] = 2


class SwingKind(Enum):
    HIGH = "high"
    LOW = "low"


class StructureLabel(Enum):
    HH = "HH"
    HL = "HL"
    LH = "LH"
    LL = "LL"
    UNCLASSIFIED = "unclassified"


class BreakKind(Enum):
    BOS_BULL = "bos_bull"
    BOS_BEAR = "bos_bear"
    CHOCH_BULL = "choch_bull"
    CHOCH_BEAR = "choch_bear"


@dataclass(frozen=True)
class Block:
    """Interval contiguu de indici, [start, end). Fără goluri în interior."""

    start: int
    end: int

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError(f"bloc gol sau inversat: [{self.start}, {self.end})")

    def contains_window(self, center: int, k: int) -> bool:
        """Fereastra [center-k, center+k] încape integral în bloc."""
        return (center - k) >= self.start and (center + k) < self.end


@dataclass(frozen=True)
class Swing:
    idx: int
    """Bara unde se află extremul."""

    confirmed_idx: int
    """Bara de la care extremul e cunoscut. Egal cu idx + k. D1."""

    price: float
    kind: SwingKind
    label: StructureLabel
    block_index: int


@dataclass(frozen=True)
class StructureBreak:
    idx: int
    """Bara pe care corpul închide dincolo de referință."""

    kind: BreakKind
    reference_swing: Swing
    close: float
    block_index: int


def detect_swings(
    high: Sequence[float],
    low: Sequence[float],
    blocks: Sequence[Block],
    k: int = K_DEFAULT,
) -> list[Swing]:
    """Fractali simetrici cu fereastră 2k+1, confinate în blocuri.

    Un swing high la i cere high[i] strict mai mare decât toate celelalte
    2k bare din fereastră. Idem, invers, pentru swing low.

    D2: inegalitate strictă pe ambele laturi. O egalitate nu produce swing.
    D3: fereastra trebuie să încapă integral într-un singur bloc.
    """
    if k < 1:
        raise ValueError("k trebuie să fie cel puțin 1")
    if len(high) != len(low):
        raise ValueError("high și low au lungimi diferite")

    out: list[Swing] = []

    for b_i, block in enumerate(blocks):
        for i in range(block.start + k, block.end - k):
            if not block.contains_window(i, k):
                continue

            window = range(i - k, i + k + 1)

            is_high = all(high[i] > high[j] for j in window if j != i)
            if is_high:
                out.append(
                    Swing(
                        idx=i,
                        confirmed_idx=i + k,
                        price=high[i],
                        kind=SwingKind.HIGH,
                        label=StructureLabel.UNCLASSIFIED,
                        block_index=b_i,
                    )
                )
                continue

            is_low = all(low[i] < low[j] for j in window if j != i)
            if is_low:
                out.append(
                    Swing(
                        idx=i,
                        confirmed_idx=i + k,
                        price=low[i],
                        kind=SwingKind.LOW,
                        label=StructureLabel.UNCLASSIFIED,
                        block_index=b_i,
                    )
                )

    return out


def label_structure(swings: Sequence[Swing]) -> list[Swing]:
    """Clasifică fiecare swing ca HH, HL, LH sau LL.

    Comparația se face cu ultimul swing de ACELAȘI tip din ACELAȘI bloc.
    Primul swing de fiecare tip într-un bloc rămâne UNCLASSIFIED — nu are
    referință, iar împrumutarea uneia din blocul anterior ar traversa
    carantina. D3.
    """
    out: list[Swing] = []
    last_high: dict[int, Swing] = {}
    last_low: dict[int, Swing] = {}

    for s in swings:
        b = s.block_index

        if s.kind is SwingKind.HIGH:
            prev = last_high.get(b)
            if prev is None:
                label = StructureLabel.UNCLASSIFIED
            elif s.price > prev.price:
                label = StructureLabel.HH
            else:
                label = StructureLabel.LH
            labelled = _relabel(s, label)
            last_high[b] = labelled
        else:
            prev = last_low.get(b)
            if prev is None:
                label = StructureLabel.UNCLASSIFIED
            elif s.price > prev.price:
                label = StructureLabel.HL
            else:
                label = StructureLabel.LL
            labelled = _relabel(s, label)
            last_low[b] = labelled

        out.append(labelled)

    return out


def _relabel(s: Swing, label: StructureLabel) -> Swing:
    return Swing(
        idx=s.idx,
        confirmed_idx=s.confirmed_idx,
        price=s.price,
        kind=s.kind,
        label=label,
        block_index=s.block_index,
    )


def detect_breaks(
    close: Sequence[float],
    swings: Sequence[Swing],
    blocks: Sequence[Block],
) -> list[StructureBreak]:
    """Body-BOS și CHoCH. Doar corpul declanșează; fitilele nu.

    BOS bullish   close[c] > price(ultimul HH confirmat)
    BOS bearish   close[c] < price(ultimul LL confirmat)
    CHoCH bearish close[c] < price(ultimul HL confirmat)
    CHoCH bullish close[c] > price(ultimul LH confirmat)

    D1: se folosește doar un swing cu confirmed_idx < c. Un swing al cărui
    extrem e la idx dar care se confirmă la idx+k NU poate declanșa o rupere
    înainte de idx+k.

    Un swing e consumat de prima rupere care îl depășește; nu se refolosește.
    """
    out: list[StructureBreak] = []

    for b_i, block in enumerate(blocks):
        block_swings = [s for s in swings if s.block_index == b_i]

        # PATCH re-armare (Mandat 5.2, regulă ratificată de Statistician): un swing depășit
        # de corp intră într-o mulțime de CONSUMATE (nivel de bazin). Bucla de activare îl
        # SARE UPSTREAM, înainte de atribuirea live_*. NICIODATĂ anulare downstream — vechiul
        # `live_* = None` de după rupere nu ținea, pentru că activarea îl reactiva din același
        # swing la bara următoare.
        consumed: set[int] = set()

        live_hh: Swing | None = None
        live_ll: Swing | None = None
        live_hl: Swing | None = None
        live_lh: Swing | None = None

        for c in range(block.start, block.end):
            # Referințele active se recompun în fiecare bară din swing-urile NECONSUMATE,
            # confirmate STRICT înainte de bara curentă (filtru upstream, înainte de atribuire).
            live_hh = live_ll = live_hl = live_lh = None
            for s in block_swings:
                if s.confirmed_idx >= c or s.idx in consumed:
                    continue
                if s.label is StructureLabel.HH:
                    live_hh = s
                elif s.label is StructureLabel.LL:
                    live_ll = s
                elif s.label is StructureLabel.HL:
                    live_hl = s
                elif s.label is StructureLabel.LH:
                    live_lh = s

            px = close[c]

            if live_hh is not None and px > live_hh.price:
                out.append(_mk_break(c, BreakKind.BOS_BULL, live_hh, px, b_i))
                consumed.add(live_hh.idx)
            elif live_lh is not None and px > live_lh.price:
                out.append(_mk_break(c, BreakKind.CHOCH_BULL, live_lh, px, b_i))
                consumed.add(live_lh.idx)

            if live_ll is not None and px < live_ll.price:
                out.append(_mk_break(c, BreakKind.BOS_BEAR, live_ll, px, b_i))
                consumed.add(live_ll.idx)
            elif live_hl is not None and px < live_hl.price:
                out.append(_mk_break(c, BreakKind.CHOCH_BEAR, live_hl, px, b_i))
                consumed.add(live_hl.idx)

    return out


def _mk_break(
    idx: int, kind: BreakKind, ref: Swing, close: float, block_index: int
) -> StructureBreak:
    return StructureBreak(
        idx=idx,
        kind=kind,
        reference_swing=ref,
        close=close,
        block_index=block_index,
    )
