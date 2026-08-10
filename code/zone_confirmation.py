"""CONFIRMAREA ZONEI PE M5 — nivelul 4 (STAT-LEVEL4-M5-CONFIRMATION-SPEC-v1.0, d977446, manifest v2.7.54).

**STARE: APPROVED_WITH_LIMITATIONS (decizie CEO, pasul 4/4, peste `ca683ff`). FREEZE v1.1.** Două limitări
consemnate, ambele la granița de integrare (NEreparate aici — se tratează la cablare):
  Z4-L1  UNDETERMINED se tratează prin MEMBRUL ENUM (`ZoneConfirmation.UNDETERMINED`) sau prin `status`,
         NICIODATĂ prin valoarea ordinală 0. (Statisticianul specifică regula la cablarea nivelului 6; VE o
         implementează atunci. Enum-ul păstrează valoarea 0 pentru ORDINEA cu semn, dar consumatorul NU o
         testează ca `== 0`.)
  Z4-L2  nivelul 4 validează o INTRARE PE MOMENTUM POST-FEREASTRĂ (la hit+W+1), nu un filtru de zonă —
         confirmarea înlocuiește tranzacția de la nivelul 3, nu o filtrează. Consemnat, NU reparat.

Funcție PURĂ pe bare M5. Fără MT5, fără date reale. **CEO: se construiește și se testează MECANIC acum; validarea
împreună cu nivelul 3 se AMÂNĂ** — ferestrele de descoperire M5 și M15_v2 se suprapun ~40 zile, un singur regim;
orice altceva rupe sigiliul. Desigilarea NU se face. Construcția/testele mecanice NU sunt blocate.

CE MĂSOARĂ (cele patru măsurători sunt de fapt DOUĂ axe):
  · PENETRAREA nu e o măsurătoare — e CRITERIUL DE SELECȚIE. Fără penetrare, interacțiunea nu intră în populație.
  · PERSISTENȚA și REVENIREA sunt aceeași variabilă cu semn opus (median 0,517 vs 0,483, sumă ~1). Folosim persistența.
  · PROGRESUL — singura axă independentă.
  · EFORTUL (nr. de încercări) e SATURAT (median 38/60 penetrează) ⇒ NU e prag; intră doar prin raportul cu progresul.

IEȘIREA: o SINGURĂ variabilă ORDINALĂ (nu două steaguri) — două booleene ar PERMITE starea contradictorie
(absorbție ȘI acceptare) pe care definiția o interzice; ordinala o face INEXPRIMABILĂ prin TIP. Scală cu semn −2..+2:
  −2 ACCEPTANCE_BEARISH        penetrare în JOS ACCEPTATĂ (rămâne sub suport)      → bearish tare
  −1 ABSORPTION_PROXY_BULLISH  penetrare în SUS ABSORBITĂ (bull respins)           → bearish slab
   0 UNDETERMINED
  +1 ABSORPTION_PROXY_BEARISH  penetrare în JOS ABSORBITĂ (bear respins)           → bullish slab
  +2 ACCEPTANCE_BULLISH        penetrare în SUS ACCEPTATĂ (rămâne peste rezistență) → bullish tare
(„PROXY_<X>" = direcția penetrării ABSORBITE; semnalul e reversul.) Nivelul 4 NU emite probabilitate — nivelul 6 o face.

GRANIȚA DE TIMP (cea mai ușor de greșit): fereastra se ÎNCHIDE la `hit+W`; intrarea e permisă cel mai devreme la
`hit+W+1`. Descriptorul citește DOAR bare ≤ hit+W. Altfel s-ar condiționa intrarea pe barele care determină și
rezultatul = lookahead față de decizie. Consecință: tranzacția NU mai e cea de la nivelul 3 — confirmarea o
ÎNLOCUIEȘTE (intrare cu W bare mai târziu, alt preț, alt risc), nu o filtrează.

W=60: NU e transplant. E orizontul de dependență de 5 ORE (care a justificat H=20 pe M15) convertit în unități M5
(zi M5 = 274,72 bare). Un orizont în TIMP CALENDARISTIC se transferă între timeframe-uri; unul în BARE nu.

`tick_volume` EXCLUS — proveniență neconfirmată; nu intră NICIODATĂ în clasificarea primară (structural: funcția ia
doar OHLC). Praguri = ALEGERI cu ancoră de ocupanță egală (terțile), NU derivate (derivarea binomială a EȘUAT:
sub nul ar trece 5%, trec 44,7% — barele nu sunt independente). Fiecare clasă ≤ ~1/3; UNDETERMINED majoritar.

FAIL-CLOSED → UNDETERMINED: fereastră incompletă (hit+W depășește seria), ATR absent/nefinit, zonă absentă/nefinită,
nicio penetrare (nu intră în populație). UNDETERMINED ⇒ sentinel la nivelul 6 ⇒ NO-TRADE prin TIP.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from market_state import atr14

# Praguri = ALEGERI (terțile, ocupanță egală), pre-înregistrate. NU derivate din structura fenomenului.
W_DEFAULT = 60                   # orizont de 5h în unități M5 (timp calendaristic, NU bare transplantate)
P33_PROGRESS = 2.53              # progres dincolo / ATR — terțila inferioară
P67_PROGRESS = 5.99              # terțila superioară
P33_PERSISTENCE = 0.22           # fracția închiderilor dincolo — terțila inferioară
P67_PERSISTENCE = 0.80           # terțila superioară
TICK_VOLUME_EXCLUDED = True      # proveniență neconfirmată; niciodată în clasificarea primară


class ZoneConfirmation(Enum):
    """O SINGURĂ variabilă ordinală (−2..+2). Contradicția absorbție∧acceptare e INEXPRIMABILĂ prin tip."""
    ACCEPTANCE_BEARISH = -2
    ABSORPTION_PROXY_BULLISH = -1
    UNDETERMINED = 0
    ABSORPTION_PROXY_BEARISH = 1
    ACCEPTANCE_BULLISH = 2


class Status(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class ZoneConfirmationResult:
    """UN SINGUR câmp de clasificare (`confirmation`) — fără steaguri absorbție/acceptare separate."""
    confirmation: ZoneConfirmation
    persistence: float | None            # fracția închiderilor dincolo (revenirea = 1 − aceasta)
    progress_atr: float | None           # progres maxim dincolo / ATR
    encounters: int | None               # bare care penetrează (INFORMATIV, saturat — NU un prag)
    hit_idx: int | None
    window_end_idx: int | None           # hit + W (fereastra se închide)
    descriptor_available_idx: int | None  # hit + W + 1 (intrarea permisă cel mai devreme)
    status: str
    reason: str
    schema_hash: str


_SCHEMA_HASH: str = hashlib.sha256(json.dumps({
    "descriptors_ordered": ["persistence", "progress_atr"],   # penetrare = selecție; efort = saturat (exclus ca prag)
    "W": W_DEFAULT, "progress_tertiles": [P33_PROGRESS, P67_PROGRESS],
    "persistence_tertiles": [P33_PERSISTENCE, P67_PERSISTENCE],
    "tick_volume_excluded": TICK_VOLUME_EXCLUDED, "code_version": "level4-v1.0",
}, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def _fail(reason: str) -> ZoneConfirmationResult:
    return ZoneConfirmationResult(
        confirmation=ZoneConfirmation.UNDETERMINED, persistence=None, progress_atr=None, encounters=None,
        hit_idx=None, window_end_idx=None, descriptor_available_idx=None,
        status=Status.UNAVAILABLE.value, reason=reason, schema_hash=_SCHEMA_HASH)


def _outcome_label(side: int, acceptance: bool, absorption: bool) -> ZoneConfirmation:
    """(latura penetrării, rezultat) → ordinala cu semn. `side`=+1 penetrare în sus, −1 în jos."""
    if acceptance:
        return ZoneConfirmation.ACCEPTANCE_BULLISH if side > 0 else ZoneConfirmation.ACCEPTANCE_BEARISH
    if absorption:                                    # penetrarea a fost absorbită ⇒ reversul direcției ei
        return ZoneConfirmation.ABSORPTION_PROXY_BULLISH if side > 0 else ZoneConfirmation.ABSORPTION_PROXY_BEARISH
    return ZoneConfirmation.UNDETERMINED


def classify_zone_confirmation(
    high: Sequence[float], low: Sequence[float], close: Sequence[float], level: float, side: int,
    *, w: int = W_DEFAULT, atr: Sequence[float] | None = None, search_start: int = 0,
) -> ZoneConfirmationResult:
    """Confirmarea unei zone (nivel M15) pe bare M5. `side`=+1 penetrare în SUS (dincolo=deasupra), −1 în JOS.
    Găsește prima penetrare (selecție), măsoară fereastra [hit+1, hit+W], emite ordinala. PURĂ, cauzală."""
    n = len(close)
    if not (side == 1 or side == -1):
        return _fail("invalid_side")
    if not _finite(level):
        return _fail("zone_unavailable")                        # zonă de la nivelul 3 absentă/UNAVAILABLE → cascadă

    # ── PENETRARE = criteriul de SELECȚIE: prima bară care depășește nivelul în direcția `side` ──
    hit = -1
    for j in range(max(0, search_start), n):
        if (high[j] >= level) if side > 0 else (low[j] <= level):
            hit = j
            break
    if hit < 0:
        return _fail("no_penetration")                          # nu intră în populație

    win_end = hit + w
    if win_end > n - 1:                                         # fereastră incompletă → fail-closed
        return _fail("incomplete_window")

    a = atr[hit] if atr is not None else atr14(high, low, close)[hit]   # ATR cauzal la hit
    if not _finite(a) or a <= 0.0:
        return _fail("atr_unavailable")

    # ── fereastra [hit+1, hit+W] (se închide la hit+W; intrarea la hit+W+1) — DOAR bare ≤ hit+W ──
    beyond = 0                                                  # închideri dincolo (persistență)
    encounters = 0                                             # bare care penetrează (informativ, saturat)
    prog = 0.0                                                 # progres maxim dincolo
    for j in range(hit + 1, win_end + 1):
        if side > 0:
            if high[j] >= level:
                encounters += 1
            if close[j] > level:
                beyond += 1
            prog = max(prog, high[j] - level)
        else:
            if low[j] <= level:
                encounters += 1
            if close[j] < level:
                beyond += 1
            prog = max(prog, level - low[j])
    wlen = win_end - hit                                       # = W bare
    persistence = beyond / wlen
    progress_atr = prog / a

    # ── clasificare: AMBELE condiții în ACELAȘI sens; altfel NEDETERMINAT (majoritar prin construcție) ──
    acceptance = persistence >= P67_PERSISTENCE and progress_atr >= P67_PROGRESS
    absorption = persistence <= P33_PERSISTENCE and progress_atr <= P33_PROGRESS
    label = _outcome_label(side, acceptance, absorption)
    return ZoneConfirmationResult(
        confirmation=label, persistence=round(persistence, 6), progress_atr=round(progress_atr, 6),
        encounters=encounters, hit_idx=hit, window_end_idx=win_end, descriptor_available_idx=win_end + 1,
        status=Status.AVAILABLE.value, reason="classified", schema_hash=_SCHEMA_HASH)


def _finite(x: float) -> bool:
    return x == x and x not in (float("inf"), float("-inf"))
