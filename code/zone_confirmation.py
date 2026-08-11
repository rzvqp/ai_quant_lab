"""CONFIRMAREA ZONEI PE M5 — nivelul 4, v2.0 CEAS W=3 (STAT-SPEC2-N4-CONFIRMATION-CLOCK-v1.0, doc 404b6c8, manifest
v2.7.61). Corecție funcțională peste v1.1 (`ca683ff`/`d977446`): **N4 NU mai e post-decizie — e parte OBLIGATORIE a
deciziei, ÎNAINTE de N6.** Confirmare cauzală pre-decizie, cel mai scurt ceas valid, plus atriția pierdută explicită.

PRECONDIȚIE BLOCANTĂ (SPEC2 §1): re-ancorarea N3 (SPEC1, `5888978`). „Prețul intră în zonă" NU e definibil cât timp
zona e ancorată pe preț (prețul e mereu în zonă). Constatare, nu dependență introdusă.

CEASUL — W=3 bare M5 = 15 min = exact O bară M15 (SPEC2 §4):
  · NU un compromis: W=1 domină W=60 pe AMBELE axe (pierdute 57,88%→86,47%, calitate 65,81%→57,07%). O fereastră
    mai lungă DILUEAZĂ dovada (persistența și progresul se acordă mai rar în același sens), nu o acumulează.
  · De ce W=3 și nu W=1: la W≤2 axa de persistență colapsează la un bit ({0,1} la W=1; {0,½,1} la W=2), iar
    clasificatorul cu DOUĂ condiții independente — cel RATIFICAT — degenerează într-o condiție-plus-un-bit. W=3 dă
    persistence ∈ {0, ⅓, ⅔, 1} (4 valori) → terțile bine definite. W=3 = cel mai scurt ceas la care clasificatorul
    ratificat RĂMÂNE cel ratificat (regula de scop interzice re-ratificarea cerută de W=1). Alinierea cu cadența M15
    a lui N3 e o CONSECINȚĂ, nu un criteriu.
  · MISSED_BEFORE_CONFIRMATION = atriție PRE-DECLARATĂ (~64% din interacțiuni la W=3): politica vede ~36%. Se
    jurnalizează la fiecare rulare, NU se compensează, NU se salvează retroactiv (ar fi selecția interzisă la v2.7.59).

TERȚILE RE-DERIVATE LA W=3 (SPEC2 §6 MATERIAL — măsurate la implementare, NU transportate de la W=60: pragurile de
la W=60 ar fi transplant de unitate). Măsurătoare pe M5 real (OANDA_XAUUSD_M5), evenimente = penetrări ale zonelor
RE-ANCORATE N3 (patru familii), D7 prima atingere, N=3.508 evenimente:
    progres măsurat contra benzii M15 (SPEC2 §3 autocorecție: NU ATR M5 — banda ratificată a zonei e 1×ATR M15).
    distribuție rezultantă: ACCEPTANCE 29,30%  ABSORPTION 28,73%  UNDETERMINED 41,96% (deplasată față de 32,8/29,8
    pe familia `level`-only, exact cum a prezis SPEC2 §6 pentru cele patru familii — „nivelurile se vor deplasa").

CONTRACT LevelOutput (v2.7.59, `995539a`): ieșirea e `LevelOutput[ZoneConfirmationResult]`.
  · UNDETERMINED (ordinala 0) = REZULTAT MĂSURAT (Ok): am măsurat persistența și progresul, niciun capăt nu a
    declanșat — 0 e neutru MĂSURAT, deci INFORMAȚIE.
  · fail-closed (n-am-putut-măsura) = Unavailable: fereastră incompletă, ATR absent/nefinit, zonă absentă (cascadă
    de la N3), latură invalidă, nicio penetrare (nu intră în populație). N6 le vede prin TIP → NO-TRADE.
Ambele duc la NO-TRADE la N6, dar prin constructori diferiți: una e „neutru", cealaltă e „lipsă". Două surse de
adevăr = niciuna → `status: str` s-a ȘTERS; statusul e CONSTRUCTORUL (Ok/Unavailable), nu un câmp.

CE MĂSOARĂ (patru măsurători = DOUĂ axe): PENETRAREA = criteriul de SELECȚIE (fără ea, nu intri în populație);
PERSISTENȚA și REVENIREA = aceeași variabilă cu semn opus (folosim persistența); PROGRESUL = singura axă
independentă; EFORTUL (încercări) e SATURAT ⇒ informativ, NU prag.

IEȘIREA (ZoneConfirmationResult.confirmation): o SINGURĂ ordinală cu semn −2..+2 — două booleene ar permite starea
contradictorie (absorbție ȘI acceptare), inexprimabilă aici prin TIP:
  −2 ACCEPTANCE_BEARISH  · −1 ABSORPTION_PROXY_BULLISH · 0 UNDETERMINED · +1 ABSORPTION_PROXY_BEARISH · +2 ACCEPTANCE_BULLISH
(„PROXY_<X>" = direcția penetrării ABSORBITE; semnalul e reversul.) N4 NU emite probabilitate — N6 o face.

GRANIȚA DE TIMP: fereastra se ÎNCHIDE la `hit+W`; intrarea permisă cel mai devreme la `hit+W+1`. Descriptorul citește
DOAR bare ≤ hit+W (altfel s-ar condiționa intrarea pe barele care determină rezultatul = lookahead). Consecință
(Z4-L2, consemnat): confirmarea ÎNLOCUIEȘTE tranzacția de la N3 (intrare cu W bare mai târziu), nu o filtrează.

`tick_volume` EXCLUS structural (funcția ia doar OHLC). Praguri = ALEGERI cu ancoră de ocupanță egală (terțile) —
derivarea binomială a EȘUAT (barele nu sunt independente: sub nul ar trece 5%, treceau 44,7%).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from level_output import LevelOutput, Ok, Unavailable
from market_state import atr14

# Ceasul — W=3 bare M5 (15 min = o bară M15). Cel mai scurt ceas la care clasificatorul ratificat rămâne ratificat.
W_DEFAULT = 3
# Terțile RE-DERIVATE la W=3 (măsurate pe M5 real, 3.508 evenimente, progres contra benzii M15). ALEGERI, nu derivate.
P33_PROGRESS = 0.2240            # progres dincolo / ATR-M15 — terțila inferioară @ W=3
P67_PROGRESS = 0.8378            # terțila superioară @ W=3
P33_PERSISTENCE = 0.0000        # fracția închiderilor dincolo — terțila inferioară @ W=3 (⇒ exact 0/3)
P67_PERSISTENCE = 0.6667        # terțila superioară @ W=3 (⇒ ≥ 2/3)
TICK_VOLUME_EXCLUDED = True      # proveniență neconfirmată; niciodată în clasificarea primară


class ZoneConfirmation(Enum):
    """O SINGURĂ variabilă ordinală (−2..+2). Contradicția absorbție∧acceptare e INEXPRIMABILĂ prin tip."""
    ACCEPTANCE_BEARISH = -2
    ABSORPTION_PROXY_BULLISH = -1
    UNDETERMINED = 0
    ABSORPTION_PROXY_BEARISH = 1
    ACCEPTANCE_BULLISH = 2


@dataclass(frozen=True)
class ZoneConfirmationResult:
    """Payload-ul din `Ok` — UN SINGUR câmp de clasificare (`confirmation`), fără steaguri separate. FĂRĂ `status`
    (constructorul Ok/Unavailable e sursa de adevăr), FĂRĂ `reason`/`schema_hash` (trăiesc pe wrapper-ul LevelOutput).
    Prezent DOAR când s-a măsurat: câmpurile nu sunt Optional — Ok garantează măsurarea."""
    confirmation: ZoneConfirmation
    persistence: float                    # fracția închiderilor dincolo (revenirea = 1 − aceasta)
    progress_atr: float                   # progres maxim dincolo / ATR-M15
    encounters: int                       # bare care penetrează (INFORMATIV, saturat — NU un prag)
    hit_idx: int
    window_end_idx: int                   # hit + W (fereastra se închide)
    descriptor_available_idx: int         # hit + W + 1 (intrarea permisă cel mai devreme)


_SCHEMA_HASH: str = hashlib.sha256(json.dumps({
    "descriptors_ordered": ["persistence", "progress_atr"],   # penetrare = selecție; efort = saturat (exclus ca prag)
    "W": W_DEFAULT, "progress_tertiles": [P33_PROGRESS, P67_PROGRESS],
    "persistence_tertiles": [P33_PERSISTENCE, P67_PERSISTENCE],
    "progress_reference": "M15_band_1xATR",                   # autocorecția SPEC2 §3
    "tick_volume_excluded": TICK_VOLUME_EXCLUDED, "code_version": "level4-v2.0-w3",
}, sort_keys=True).encode("utf-8")).hexdigest()[:16]


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
) -> LevelOutput[ZoneConfirmationResult]:
    """Confirmarea unei zone (nivel M15) pe bare M5. `side`=+1 penetrare în SUS (dincolo=deasupra), −1 în JOS.
    Găsește prima penetrare (selecție), măsoară fereastra [hit+1, hit+W], emite ordinala. PURĂ, cauzală.
    Ok(ZoneConfirmationResult) incl. UNDETERMINED măsurat; Unavailable = n-am-putut-măsura (fail-closed)."""
    n = len(close)
    last = n - 1
    if not (side == 1 or side == -1):
        return Unavailable(reason="invalid_side", as_of=last)
    if not _finite(level):
        return Unavailable(reason="zone_unavailable", as_of=last)   # zonă de la N3 absentă/UNAVAILABLE → cascadă

    # ── PENETRARE = criteriul de SELECȚIE: prima bară care depășește nivelul în direcția `side` ──
    hit = -1
    for j in range(max(0, search_start), n):
        if (high[j] >= level) if side > 0 else (low[j] <= level):
            hit = j
            break
    if hit < 0:
        return Unavailable(reason="no_penetration", as_of=last)     # nu intră în populație

    win_end = hit + w
    if win_end > n - 1:                                            # fereastră incompletă → fail-closed
        return Unavailable(reason="incomplete_window", as_of=last)

    a = atr[hit] if atr is not None else atr14(high, low, close)[hit]   # ATR cauzal la hit (banda M15)
    if not _finite(a) or a <= 0.0:
        return Unavailable(reason="atr_unavailable", as_of=hit)

    # ── fereastra [hit+1, hit+W] (se închide la hit+W; intrarea la hit+W+1) — DOAR bare ≤ hit+W ──
    beyond = 0                                                     # închideri dincolo (persistență)
    encounters = 0                                                # bare care penetrează (informativ, saturat)
    prog = 0.0                                                    # progres maxim dincolo
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
    wlen = win_end - hit                                          # = W bare
    persistence = beyond / wlen
    progress_atr = prog / a

    # ── clasificare: AMBELE condiții în ACELAȘI sens; altfel NEDETERMINAT (0 măsurat = informație) ──
    acceptance = persistence >= P67_PERSISTENCE and progress_atr >= P67_PROGRESS
    absorption = persistence <= P33_PERSISTENCE and progress_atr <= P33_PROGRESS
    label = _outcome_label(side, acceptance, absorption)
    result = ZoneConfirmationResult(
        confirmation=label, persistence=round(persistence, 6), progress_atr=round(progress_atr, 6),
        encounters=encounters, hit_idx=hit, window_end_idx=win_end, descriptor_available_idx=win_end + 1)
    # descriptorul e disponibil la hit+W+1 (as_of); dincolo de hit+W+2 nu se mai folosește (carry-forward = eroare)
    return Ok(value=result, as_of=win_end + 1, valid_until=win_end + 2, schema_hash=_SCHEMA_HASH)


def _finite(x: float) -> bool:
    return x == x and x not in (float("inf"), float("-inf"))
