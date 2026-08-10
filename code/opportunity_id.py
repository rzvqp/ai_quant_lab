"""IDENTITATEA OPORTUNITĂȚII (STAT-OPPORTUNITY-IDENTITY-SPEC-v1.0, a36b2d7, v2.7.60). Prima sarcină a fazei —
„Se face PRIMA, sau nu se face niciuna" (contract Partea 8). `zone@{bară}` numește o BARĂ, nu o oportunitate:
aceeași zonă economică emitea ~5,23 id-uri. Cheia se pune pe GEOMETRIE + CICLU DE VIAȚĂ, nu pe indexul barei.

CHEIA (înghețată la creare, bara i0):
    anchor a = close[i0-1]              ÎNGHEȚAT       band b = BAND_ATR_MULT × atr[i0-1]   ÎNGHEȚAT
    apartenență la j>i0:  |close[j-1] − a| <= b        cauzal (citește j-1)
`opportunity_id` = cheie surogat (contor monoton), NICIODATĂ funcție de indexul barei.

Banda se ÎNGHEAȚĂ (nu se recalculează): o bandă vie urmărește prețul (ATR crește → banda se lărgește → prețul
rămâne în ea → durată NEMĂRGINITĂ = fail-mort). Înghețarea mărginește durata prin construcție; e și conservatoare.

DOUĂ CEASURI (confundarea lor face regula CEO inexecutabilă):
    ceas ECONOMIC     se închide la band_exit           (mediană măsurată 4 bare M15)
    ceas de IDENTITATE se închide la i0+W+1             (ÎNTOTDEAUNA, indiferent de primul)
Numai ~4,77% dintre oportunități mai sunt în viață la i0+W+1 — identitatea trebuie să SUPRAVIEȚUIASCĂ închiderii
economice, altfel N4 n-are la ce atașa dovada.

D7 pe OPORTUNITATE: `DECIDED` se atinge exact o dată, la i0. O emisie ulterioară în aceeași bandă REÎMPROSPĂTEAZĂ,
nu redecide — asta face „o oportunitate = un slot de familie" adevărat MECANIC. Re-armarea în <=W (11,42% măsurat)
e absorbită de ceasul de identitate FĂRĂ constantă nouă (niciun cooldown); re-armările de dincolo de W sunt
oportunități genuin noi, RAPORTATE ca fracție.

⚠ INTERPRETARE VE (Red Team): banda de IDENTITATE = 1×ATR (per acest spec, pentru grupare) e DISTINCTĂ de banda
de confluență N3 = 0,25×ATR (SPEC 1). Prima definește identitatea; a doua numără trăsături. Marcată aici.

Punctul 6 al regulii (N4 NU modifică retroactiv decizia) e impus prin TIP: `DecisionRecord` și `EvidenceRecord`
sunt DOUĂ înregistrări imuabile, legate DOAR prin `opportunity_id`. N4 nu are câmp de scris în decizie.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal

from level_output import LevelOutput

BAND_ATR_MULT: float = 1.0       # banda de IDENTITATE (1×ATR ratificat), pentru grupare — NU banda de confluență N3


class OppState(Enum):
    OPEN = "open"                # i0 → band_exit (refresh permis)
    DECIDED = "decided"          # i0, o singură dată (D7); înregistrare ÎNGHEȚATĂ
    EVIDENCE_PENDING = "evidence_pending"   # i0+1 → i0+W+1 (N4 atașează o dată)
    CLOSED = "closed"            # max(band_exit, i0+W+1), doar citire


@dataclass
class Opportunity:
    opportunity_id: str
    anchor: float                # ÎNGHEȚAT close[i0-1]
    band: float                  # ÎNGHEȚAT
    created_at: int              # i0 == zone_hit == decided_at
    evidence_deadline: int       # i0 + w + 1 (ceasul de IDENTITATE)
    last_seen: int
    refresh_count: int = 0
    band_exit_at: int | None = None      # ceasul ECONOMIC
    closed_at: int | None = None
    close_reason: str | None = None      # band_exit / expired_identity / series_end
    state: OppState = OppState.OPEN

    def contains(self, close_prev: float) -> bool:
        return abs(close_prev - self.anchor) <= self.band


@dataclass(frozen=True)
class DecisionRecord:
    """Scris O DATĂ, la i0. Fără setter, fără câmp de evidence — N4 nu are unde scrie (punctul 6, prin TIP)."""
    opportunity_id: str
    decided_at: int              # == i0 == zone_hit
    outcome: Literal["TRADE", "NO_TRADE"]
    inputs_hash: str             # peste N1, N2, N3 AȘA CUM ERAU la i0
    schema_hash: str


@dataclass(frozen=True)
class EvidenceRecord:
    """Scris O DATĂ, la i0+W+1. Referă DecisionRecord DOAR prin id — nu-l poate atinge."""
    opportunity_id: str
    attached_at: int             # i0 + w + 1
    descriptor: LevelOutput[object]   # LevelOutput[ZoneConfirmationResult] la cablare


@dataclass
class OpportunityTracker:
    """Grupează emisiile N3 (o emisie = o zonă calificată la bara j) în oportunități economice persistente.
    Deterministic; cauzal (citește close[j-1], atr[j-1]). `re_arm_beyond_w` numără oportunitățile genuin noi."""
    w: int
    band_atr_mult: float = BAND_ATR_MULT
    _counter: int = 0
    open_opps: list[Opportunity] = field(default_factory=list)
    closed_opps: list[Opportunity] = field(default_factory=list)
    re_arm_beyond_w: int = 0

    def _new_id(self) -> str:
        self._counter += 1
        return f"opp-{self._counter:08d}"

    def _close(self, opp: Opportunity, j: int, reason: str) -> None:
        opp.closed_at = j
        opp.close_reason = reason
        opp.state = OppState.CLOSED
        self.open_opps.remove(opp)
        self.closed_opps.append(opp)

    def step(self, j: int, close_prev: float, atr_prev: float, emitted: bool) -> Opportunity | None:
        """O bară. Închide ce a expirat, apoi (dacă N3 a emis) reîmprospătează un membru sau creează un id nou.
        Întoarce oportunitatea creată la această bară (DECIDED), sau None."""
        # 1) închideri: ceasul economic (band_exit) și cel de identitate (deadline)
        for opp in list(self.open_opps):
            if j >= opp.evidence_deadline:                       # ceasul de IDENTITATE (întotdeauna)
                self._close(opp, j, "expired_identity")
            elif opp.band_exit_at is None and not opp.contains(close_prev):
                opp.band_exit_at = j                             # ceasul ECONOMIC — marcat, dar id-ul supraviețuiește
        if not emitted:
            return None
        # 2) emisie: reîmprospătare dacă cade în banda unei oportunități încă vii (identitate deschisă)
        for opp in self.open_opps:
            if opp.contains(close_prev):
                opp.last_seen = j
                opp.refresh_count += 1
                return None                                      # NU un id nou (D7: nu redecide)
        # 3) altfel oportunitate NOUĂ (DECIDED la i0=j). Re-armare de dincolo de W dacă recentă la aceeași ancoră
        if not (atr_prev == atr_prev) or atr_prev <= 0.0:        # NaN/nefinit → fără bandă validă
            return None
        for cl in self.closed_opps[-64:]:                        # re-armare genuin nouă (>W): raportare, nu suprimare
            if abs(close_prev - cl.anchor) <= self.band_atr_mult * atr_prev and j - (cl.closed_at or j) <= 20:
                self.re_arm_beyond_w += 1
                break
        opp = Opportunity(opportunity_id=self._new_id(), anchor=close_prev, band=self.band_atr_mult * atr_prev,
                          created_at=j, evidence_deadline=j + self.w + 1, last_seen=j, state=OppState.DECIDED)
        self.open_opps.append(opp)
        return opp
