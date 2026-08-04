"""Market structure primitives — MK-01.

RATIFICAT (manifest v2.7.39, commit `2d795bc`). Cod verificat: fidelitate (Statistician),
executabilitate + garduri F2/F3 + semantica de cascadă v2.7.38 (VE), atac adversarial (Red Team).
NU mai e draft. (Corecție de header cerută de Alpha — text, zero schimbare de cod.)

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

    F3 (extins de Red Team la `label_structure`, nu doar `detect_breaks`): clasificarea compară cu ULTIMUL
    swing de același tip din ordinea listei — o ordine greșită produce etichete GREȘITE în TĂCERE. Precondiția
    de ordonare fail-closed se impune și AICI, la intrare, înainte de orice etichetare.
    """
    _assert_ordering_precondition(swings)                       # F3 — fail-closed (idem detect_breaks)

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


def _assert_ordering_precondition(swings: Sequence[Swing]) -> None:
    """F3 — precondiție de ORDONARE, fail-closed, impusă MECANIC (Mandat remediere F2/F3).

    Bucla de activare din `detect_breaks` selectează referința live ca ULTIMUL swing de o etichetă
    dată în ordinea listei — deci ordinea de intrare NU e igienă, ci CORECTITUDINE. Presupunerea
    (semnalată la ratificarea etapei 2 ca risc latent) e acum DECLARATĂ și IMPUSĂ. Violarea ridică
    `ValueError` — NU produce tăcut rezultate greșite. Verifică toate patru:
      • ordine temporală   — `idx` strict crescător în ordinea listei
      • identificatori unici — `idx` unic (implicat de strict crescător; mesaj explicit)
      • confirmed_idx monoton — non-descrescător
      • nicio confirmare înainte de extrem — `confirmed_idx >= idx` (partea de runtime — activarea DOAR
        când `confirmed_idx < c` — rămâne impusă în buclă, D1).
    `detect_swings` produce mereu această ordine (per-bloc, blocuri în ordine de index), deci pipeline-ul
    real nu declanșează niciodată excepția; doar intrări construite manual, incoerente, o fac.
    """
    prev: Swing | None = None
    for s in swings:
        if s.confirmed_idx < s.idx:
            raise ValueError(
                f"F3: confirmed_idx ({s.confirmed_idx}) < idx ({s.idx}) — confirmare înainte de extrem.")
        if prev is not None:
            if s.idx == prev.idx:
                raise ValueError(f"F3: idx duplicat ({s.idx}) — identificatori neunici.")
            if s.idx < prev.idx:
                raise ValueError(
                    f"F3: idx neordonat ({s.idx} după {prev.idx}) — ordine temporală încălcată.")
            if s.confirmed_idx < prev.confirmed_idx:
                raise ValueError(
                    f"F3: confirmed_idx nemonoton ({s.confirmed_idx} după {prev.confirmed_idx}).")
        prev = s


_BREAK_KIND: dict[StructureLabel, BreakKind] = {
    StructureLabel.HH: BreakKind.BOS_BULL, StructureLabel.LL: BreakKind.BOS_BEAR,
    StructureLabel.HL: BreakKind.CHOCH_BEAR, StructureLabel.LH: BreakKind.CHOCH_BULL,
}


def detect_breaks(
    close: Sequence[float],
    swings: Sequence[Swing],
    blocks: Sequence[Block],
) -> list[StructureBreak]:
    """Body-BOS și CHoCH — SEMANTICĂ DE CASCADĂ (Statistician v2.7.38). Doar corpul declanșează; fitilele nu.

    BOS bullish   close[c] > price(HH)      CHoCH bullish close[c] > price(LH)
    BOS bearish   close[c] < price(LL)      CHoCH bearish close[c] < price(HL)

    CASCADĂ (v2.7.38): la bara c, TOATE swing-urile ACTIVE depășite de close[c] produc câte o rupere LA c —
    nu eșalonat. Se corectează DOI vectori de întârziere: (a) pointerii live_* cu slot unic evaluau doar cel
    mai recent swing de fiecare tip; (b) if/elif-ul intra-direcție SUPRIMA un LH depășit când un HH rupea pe
    aceeași bară — iar dacă close-ul cădea la bara următoare, ruperea suprimată se pierdea DEFINITIV. Corecția
    livrează ce D7 specifica deja (fiecare swing distinct → exact o rupere); D2/D7 NESCHIMBATE — se schimbă
    DOAR bara pe care e înregistrată. Consecință: BOS și CHoCH pot apărea pe ACEEAȘI bară, contra referințelor
    DISTINCTE (nu dublă numărare).

    D1: doar swing-uri cu confirmed_idx < c (fără lookahead). D7/re-armare: filtru UPSTREAM `consumed`
    (Mandat 5.2), fiecare idx consumat o dată. F3: precondiția de ordonare, fail-closed, la intrare.

    ORDINE (v2.7.38): rupturile emise la bara c = DESCRESCĂTOR după `reference_swing.idx` (cel mai recent swing
    depășit primul). idx unic per swing → ordine totală. Motiv: păstrează referința pe care codul vechi deja o
    alegea în prima poziție (consumatorul `_first_break_after` cu `b.idx < best.idx` nu poate separa idx egale)
    → schimbarea rămâne strict de TIMING, nu de referință.
    """
    _assert_ordering_precondition(swings)                       # F3 — fail-closed, înainte de orice procesare

    out: list[StructureBreak] = []

    for b_i, block in enumerate(blocks):
        block_swings = [s for s in swings if s.block_index == b_i]
        consumed: set[int] = set()                              # nivel de bazin, per bloc (D3 reset)

        for c in range(block.start, block.end):
            px = close[c]
            # TOATE swing-urile active (confirmate < c, neconsumate) depășite de close[c] — ambele direcții
            hits: list[Swing] = []
            for s in block_swings:
                if s.confirmed_idx >= c or s.idx in consumed:
                    continue
                if (s.label is StructureLabel.HH or s.label is StructureLabel.LH) and px > s.price:
                    hits.append(s)
                elif (s.label is StructureLabel.LL or s.label is StructureLabel.HL) and px < s.price:
                    hits.append(s)
            hits.sort(key=lambda s: s.idx, reverse=True)        # DESCRESCĂTOR după idx (cel mai recent primul)
            for s in hits:
                out.append(_mk_break(c, _BREAK_KIND[s.label], s, px, b_i))
                consumed.add(s.idx)                             # consumat în ACELAȘI pas, înainte de a avansa

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
