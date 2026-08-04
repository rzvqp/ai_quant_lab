"""Session reference levels — MK-04 (sesiuni). RATIFICABIL — oglindește PDH/PDL bar cu bar (Statistician v2.7.39).

Trei niveluri per sesiune ÎNCHEIATĂ: High, Low, Mid + detectoare de atingere. Definiții pure (NU citesc date,
NU apelează `load()`). Fără lookahead: nivelul se calculează din sesiunea ÎNCHEIATĂ, disponibil de la bara
următoare (`available_idx`). D3_bis la granițe de bloc, D7 pentru consumare, ancora 17:00 NY (via `day_index`
caller-side); ceasul de sesiune (ore UTC, `market_state.session_of`) e derivat caller-side, exact ca `day_index`.
REUTILIZEAZĂ `institutional_levels._runs` — fără convenții paralele.

Mid E UN OBIECT DIFERIT de High/Low (spec):
  - stopurile stau DINCOLO de extreme; nimeni nu pune nimic la mijloc → Mid cere test propriu de atingere,
    bazat pe CONȚINERE (`low[j] <= Mid <= high[j]`), NU pe depășire;
  - Mid NU are direcție intrinsecă — direcția o declară POLITICA, nu se deduce din nivel;
  - cele trei NU se raportează niciodată împreună → atingerile H/L (`detect_session_level_touches`) sunt
    SEPARATE de Mid (`detect_session_mid_touches`).

DOUĂ PRIMITIVE DISTINCTE:
  A `compute_prior_session_levels`  — EXPIRĂ după sesiunea următoare (activ o singură sesiune) → 2-3 niveluri
     active oricând, curat, exact ca PDH/PDL.
  B `compute_persistent_session_levels` — PERSISTĂ până la prima atingere (consumat D7), se ACUMULEAZĂ.
     ⚠ PRECONDIȚIE DURĂ: numărul de niveluri active se MĂSOARĂ înainte de a construi ceva pe B
     (`count_active_persistent_levels`) — volumul mare fără filtru e tiparul care pierde cel mai mult
     (DZ×FVG 18.275/−2.432$, CAND-0020 34.006/−15.409R, CAND-0024 18.852/−2.605R).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from market_structure import Block
from market_state import session_of
from institutional_levels import _runs


class SessionLevelKind(Enum):
    SESSION_HIGH = "session_high"    # rezistență — atingere prin DEPĂȘIRE (high>=price)
    SESSION_LOW = "session_low"      # suport — atingere prin DEPĂȘIRE (low<=price)
    SESSION_MID = "session_mid"      # OBIECT DIFERIT — atingere prin CONȚINERE, fără direcție


@dataclass(frozen=True)
class SessionLevel:
    price: float
    kind: SessionLevelKind
    source_session_start: int        # prima bară a sesiunii-sursă (închisă)
    available_idx: int               # prima bară de la care e cunoscut (fără lookahead)
    expiry_idx: int                  # ultima bară a ferestrei de valabilitate (A: sfârșit sesiune curentă; B: sfârșit bloc)
    block_index: int
    session_label: str               # eticheta sesiunii-sursă (asia/london/ny/late)


@dataclass(frozen=True)
class SessionLevelTouch:
    level: SessionLevel
    touch_idx: int
    block_index: int


def derive_session_index(time: Sequence[int]) -> list[int]:
    """Ordinal MONOTON de sesiune (analog `day_index`): incrementează la fiecare schimbare de sesiune
    (`session_of` pe ora UTC). Caller-side, ca `day_index`; `_runs` îl segmentează în sesiuni."""
    out: list[int] = []
    idx = 0
    prev: str | None = None
    for t in time:
        s = session_of(int(t))
        if prev is not None and s != prev:
            idx += 1
        out.append(idx)
        prev = s
    return out


def session_labels(time: Sequence[int]) -> list[str]:
    return [session_of(int(t)) for t in time]


def _emit(high: Sequence[float], low: Sequence[float], p0: int, p1: int, avail: int, expiry: int,
          b_i: int, label: str) -> list[SessionLevel]:
    sh = max(high[j] for j in range(p0, p1 + 1))
    sl = min(low[j] for j in range(p0, p1 + 1))
    sm = (sh + sl) / 2.0
    return [
        SessionLevel(sh, SessionLevelKind.SESSION_HIGH, p0, avail, expiry, b_i, label),
        SessionLevel(sl, SessionLevelKind.SESSION_LOW, p0, avail, expiry, b_i, label),
        SessionLevel(sm, SessionLevelKind.SESSION_MID, p0, avail, expiry, b_i, label),
    ]


def compute_prior_session_levels(
    high: Sequence[float], low: Sequence[float], session_index: Sequence[int], session_label: Sequence[str],
    blocks: Sequence[Block],
) -> list[SessionLevel]:
    """PRIMITIVA A (expiră): High/Low/Mid ale sesiunii ANTERIOARE, active DOAR pe sesiunea curentă. Reset D3_bis
    (prima sesiune a blocului nu emite). `available_idx` = prima bară a sesiunii curente (Q4, fără lookahead)."""
    out: list[SessionLevel] = []
    for b_i, block in enumerate(blocks):
        sessions = _runs(session_index, block.start, block.end)
        for k in range(1, len(sessions)):                     # prima sesiune (k=0) rămâne UNCLASSIFIED
            p0, p1 = sessions[k - 1]
            cur_first, cur_last = sessions[k]
            out.extend(_emit(high, low, p0, p1, cur_first, cur_last, b_i, session_label[p0]))
    return out


def compute_persistent_session_levels(
    high: Sequence[float], low: Sequence[float], session_index: Sequence[int], session_label: Sequence[str],
    blocks: Sequence[Block],
) -> list[SessionLevel]:
    """PRIMITIVA B (persistă): High/Low/Mid ale FIECĂREI sesiuni închise, disponibile de la sesiunea următoare,
    active până la prima atingere (D7) sau sfârșitul blocului. Se ACUMULEAZĂ — vezi precondiția de mai jos."""
    out: list[SessionLevel] = []
    for b_i, block in enumerate(blocks):
        sessions = _runs(session_index, block.start, block.end)
        for k in range(0, len(sessions) - 1):                 # fiecare sesiune închisă, disponibilă de la următoarea
            p0, p1 = sessions[k]
            avail = sessions[k + 1][0]
            out.extend(_emit(high, low, p0, p1, avail, block.end - 1, b_i, session_label[p0]))
    return out


def detect_session_level_touches(
    high: Sequence[float], low: Sequence[float], levels: Sequence[SessionLevel],
) -> list[SessionLevelTouch]:
    """Atingeri High/Low prin DEPĂȘIRE (D7 consumat o dată): SESSION_HIGH → `high[j]>=price` (rezistență);
    SESSION_LOW → `low[j]<=price` (suport). Mid EXCLUS (are detector propriu). Fereastra = [available_idx, expiry_idx]."""
    out: list[SessionLevelTouch] = []
    for lv in levels:
        if lv.kind is SessionLevelKind.SESSION_MID:
            continue
        for j in range(lv.available_idx, lv.expiry_idx + 1):
            touched = high[j] >= lv.price if lv.kind is SessionLevelKind.SESSION_HIGH else low[j] <= lv.price
            if touched:
                out.append(SessionLevelTouch(lv, j, lv.block_index))
                break                                          # D7: consumat la prima atingere
    return out


def detect_session_mid_touches(
    high: Sequence[float], low: Sequence[float], levels: Sequence[SessionLevel],
) -> list[SessionLevelTouch]:
    """Atingeri Mid prin CONȚINERE (obiect diferit, fără direcție): `low[j] <= Mid <= high[j]`, consumat o dată
    (D7). SEPARAT de High/Low — cele trei nu se raportează niciodată împreună."""
    out: list[SessionLevelTouch] = []
    for lv in levels:
        if lv.kind is not SessionLevelKind.SESSION_MID:
            continue
        for j in range(lv.available_idx, lv.expiry_idx + 1):
            if low[j] <= lv.price <= high[j]:                  # CONȚINERE, nu depășire; nicio direcție
                out.append(SessionLevelTouch(lv, j, lv.block_index))
                break                                          # D7
    return out


def count_active_persistent_levels(
    levels: Sequence[SessionLevel], touches: Sequence[SessionLevelTouch], n: int,
) -> list[int]:
    """PRECONDIȚIA DURĂ pentru primitiva B: câte niveluri sunt ACTIVE la fiecare bară (disponibile și
    NEatinse încă). Un nivel e activ pe [available_idx, min(prima atingere, expiry_idx)]. Se MĂSOARĂ înainte de
    a construi ceva pe B — volumul mare fără filtru e tiparul care pierde."""
    touch_of: dict[int, int] = {}
    for t in touches:
        key = id(t.level)
        if key not in touch_of or t.touch_idx < touch_of[key]:
            touch_of[key] = t.touch_idx
    active = [0] * n
    for lv in levels:
        end = touch_of.get(id(lv), lv.expiry_idx)
        for j in range(lv.available_idx, min(end, lv.expiry_idx) + 1):
            if 0 <= j < n:
                active[j] += 1
    return active
