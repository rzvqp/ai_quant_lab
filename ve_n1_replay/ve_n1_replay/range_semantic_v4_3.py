"""RANGE HIERARCHICAL V4.3 — PROTOTIP (mandat CEO "IMPLEMENTARE PROTOTIP RANGE HIERARCHICAL V4.3").

Autorizat de Red Team `RANGE_V4_IMPLEMENTATION_PACKAGE_STATIC_PASS` (RT-RANGE-0006, commit `2c113ef`, E81) pe
pachetul Statistician `d6e599e` (manifest v2.7.94 `@14d4c22`, fingerprint `a5d69e2d0150d7ca2cf750df49f65cfc
55b91fa89d13568fa42f81a48f4ee565` — verificat independent, nu doar citat) — verdict
`VE_CAN_IMPLEMENT_WITHOUT_INVENTION = TRUE`. **Autorizează EXCLUSIV construirea și evaluarea prototipului —
NU wheel, NU integrare, NU tranzacționare.**

Oracol contractual (sursă normativă a fiecărei reguli, NU inventat aici): `statistician/harness/
range_v42_contract_harness.py` @`d6e599e` (SHA-256 `c917604bd42a0943d77d385523ececba149a3e78f76a4875ce94cf
82a368c72d`, 409 linii, verificat independent) + `test_range_v42_adversarial.py` (SHA-256 `ecb4140e7f47d7b8
6cb29ef7d50e193a1375dddc2c5505aef7a65add2d277f40`, 329 linii) — rulate independent aici: **79 PASS / 0 FAIL,
mypy --strict clean**, confirmate identic cu raportul Red Team. Numele fișierului harness conține "v42" din
motive istorice (v4.3 = v4.2 + 17 corecții, NEIZOLATE într-un fișier nou de Statistician) — `contract_version`
propriu-zis, NORMATIV, e `range-hierarchical-v4.3` (singular, fără ambiguitate — RT §2). **VE nu implementează
v4.2**: acest fișier și toate simbolurile sale poartă EXCLUSIV `v4_3`/`V43`.

Domeniul structural: EXACT două adâncimi, `MACRO` (0) și `INTERNAL` (1). Al treilea nivel e STRUCTURAL
IMPOSIBIL (`DEPTH_LIMIT_EXCEEDED`, impus mecanic în `assign_level`, nu doar documentat — corecția C14).

Ce NU e acest modul: nu e wheel, nu produce semnale, nu calculează PnL, nu atinge SEALED/OOS, nu implementează
Strategy Catalog/Alpha/AI Trader/LIVE_SHADOW/broker. Config-ul, harness-ul și cele 29 reason codes sunt
NORMATIVE (Statistician + CEO) — orchestrarea per-bară (când se formează un candidat, cui i se oferă un
swing nou, ce se întâmplă cu un candidat refuzat) e responsabilitatea VE, explicit autorizată de verdict
("orchestrarea per-bară, nu inventarea unei reguli") și documentată exhaustiv mai jos, la fiecare decizie.
"""
from __future__ import annotations

import dataclasses as _dc
import hashlib
import heapq
import json
from collections import deque
from enum import Enum
from typing import Any

from .range_semantic_v3 import _RunningMedian, _Swing

RANGE_HIERARCHICAL_V4_3_CONTRACT_VERSION = "range-hierarchical-v4.3"
RANGE_HIERARCHICAL_V4_3_NORMATIVE_CONFIG_ID = (
    "24f72a60fcde42746d44f098558a745fac0f20b0141865bdbe0359f9cc3826da")

# **F5 (RT-RANGE-0011, `8d71fce`)**: corecția de la linia ~745 schimbă COMPORTAMENTUL detectorului pe
# calea forming-internal (bandă de re-testare a frontierei MACRO scalată corect prin ATR) fără să schimbe
# nicio valoare de configurație -- `config_id` rămâne byte-identic (§7 mandat). Asta înseamnă că gardul de
# fail-closed existent la restore (`contract_version` + `config_id`) NU ar refuza un snapshot PRE-F5 --
# un pericol real de restore cross-versiune, semnalat explicit de Red Team ("VE must ensure the new code
# fingerprint participates in snapshot/version gating"). Identitate de IMPLEMENTARE separată de identitate
# de CONTRACT/CONFIG -- bumped manual la fiecare schimbare de comportament care nu mișcă `config_id`,
# verificată suplimentar (nu în locul) la `contract_version`/`config_id` în `restore_state`.
RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT = "f1-f5-conformance-2026-08-20"

__all__ = [
    "ContractErrorV43", "ConfigNotRatifiedErrorV43",
    "Depth", "MacroState", "InternalState", "REASONS_V43", "ROLES_V43",
    "ConfigV43", "Cluster", "Structure", "Excursion", "Registry",
    "RangeSemanticProducerV43", "RangeSemanticResultV43", "RangeEventV43",
    "degeneracy_check", "evaluate_candidate", "evaluate_candidate_with_n_touch", "offer_swing",
    "assign_level", "promotion_check", "guard_timestamp", "sweep_reversal_confirmed",
    "RANGE_HIERARCHICAL_V4_3_CONTRACT_VERSION", "RANGE_HIERARCHICAL_V4_3_NORMATIVE_CONFIG_ID",
    "RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT",
]


class ContractErrorV43(Exception):
    """Echivalentul `ContractError` din harness — refuz fail-closed la nivel de contract."""


class ConfigNotRatifiedErrorV43(Exception):
    """Construcția unui producător/motor V4.3 fără `acknowledge_construction_only=True` explicit."""


# ═══════════════════════════════════ vocabular (identic cu harness-ul) ═══════════════════════════════════

class Depth(Enum):
    MACRO = 0
    INTERNAL = 1


class MacroState(Enum):
    TRANSITION_MACRO = "TRANSITION_MACRO"
    RANGE_FORMING = "RANGE_FORMING"
    RANGE_CONFIRMED = "RANGE_CONFIRMED"
    BOUNDARY_EXCURSION = "BOUNDARY_EXCURSION"
    SWEEP_CONFIRMED = "SWEEP_CONFIRMED"
    BREAKOUT_PENDING = "BREAKOUT_PENDING"
    BREAKOUT_ACCEPTED = "BREAKOUT_ACCEPTED"
    EPISODE_CLOSED = "EPISODE_CLOSED"
    TREND_UP = "TREND_UP"
    TREND_DOWN = "TREND_DOWN"
    UNAVAILABLE = "UNAVAILABLE"


class InternalState(Enum):
    INT_SUBRANGE = "INT_SUBRANGE"
    INT_CHANNEL_UP = "INT_CHANNEL_UP"
    INT_CHANNEL_DOWN = "INT_CHANNEL_DOWN"
    INT_BALANCE = "INT_BALANCE"


# setul ÎNCHIS de 29 reason codes — identic, ordine identică cu `REASONS` din harness (§10 mandat: 29 exact)
OK_RANGE_MACRO = "OK_RANGE_MACRO"
OK_RANGE_INTERNAL = "OK_RANGE_INTERNAL"
ESTABLISHING_FEW_SWINGS = "ESTABLISHING_FEW_SWINGS"
TOO_SHORT_MACRO = "TOO_SHORT_MACRO"
TOO_SHORT_INTERNAL = "TOO_SHORT_INTERNAL"
ZONES_DEGENERATE = "ZONES_DEGENERATE"
ZONES_INVERTED = "ZONES_INVERTED"
ATR_UNAVAILABLE = "ATR_UNAVAILABLE"
BETWEEN_EPISODES = "BETWEEN_EPISODES"
SWING_OUTSIDE_CLUSTER = "SWING_OUTSIDE_CLUSTER"
NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT = "NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT"
SWEEP_CONFIRMED = "SWEEP_CONFIRMED"
BREAKOUT_ACCEPTED = "BREAKOUT_ACCEPTED"
LIQUIDITY_SWEEP_REVERSAL = "LIQUIDITY_SWEEP_REVERSAL"
IS_TREND_MACRO = "IS_TREND_MACRO"
PROMOTION_REFUSED_PRECONDITION_P1 = "PROMOTION_REFUSED_PRECONDITION_P1"
PROMOTION_REFUSED_PRECONDITION_P2 = "PROMOTION_REFUSED_PRECONDITION_P2"
PROMOTION_REFUSED_PRECONDITION_P3 = "PROMOTION_REFUSED_PRECONDITION_P3"
PROMOTION_REFUSED_PRECONDITION_P4 = "PROMOTION_REFUSED_PRECONDITION_P4"
LEVEL_ASSIGNMENT_UNRESOLVED = "LEVEL_ASSIGNMENT_UNRESOLVED"
PARTIAL_OVERLAP_NO_CONTAINMENT = "PARTIAL_OVERLAP_NO_CONTAINMENT"
DEPTH_LIMIT_EXCEEDED = "DEPTH_LIMIT_EXCEEDED"
ROLE_ASSERTED_BEFORE_CONFIRMATION = "ROLE_ASSERTED_BEFORE_CONFIRMATION"
ROLE_KNOWN_BEFORE_CONFIRM = "ROLE_KNOWN_BEFORE_CONFIRM"
SNAPSHOT_CONTRACT_MISMATCH = "SNAPSHOT_CONTRACT_MISMATCH"
FUTURE_TIMESTAMP_REFUSED = "FUTURE_TIMESTAMP_REFUSED"
DEAD_ID_REUSE_REFUSED = "DEAD_ID_REUSE_REFUSED"
REVERSAL_REFERENCE_UNAVAILABLE = "REVERSAL_REFERENCE_UNAVAILABLE"
REVERSAL_WINDOW_EXPIRED = "REVERSAL_WINDOW_EXPIRED"

REASONS_V43: tuple[str, ...] = (
    OK_RANGE_MACRO, OK_RANGE_INTERNAL, ESTABLISHING_FEW_SWINGS,
    TOO_SHORT_MACRO, TOO_SHORT_INTERNAL,
    ZONES_DEGENERATE, ZONES_INVERTED, ATR_UNAVAILABLE, BETWEEN_EPISODES,
    SWING_OUTSIDE_CLUSTER, NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT, SWEEP_CONFIRMED,
    BREAKOUT_ACCEPTED, LIQUIDITY_SWEEP_REVERSAL, IS_TREND_MACRO,
    PROMOTION_REFUSED_PRECONDITION_P1, PROMOTION_REFUSED_PRECONDITION_P2,
    PROMOTION_REFUSED_PRECONDITION_P3, PROMOTION_REFUSED_PRECONDITION_P4,
    LEVEL_ASSIGNMENT_UNRESOLVED, PARTIAL_OVERLAP_NO_CONTAINMENT, DEPTH_LIMIT_EXCEEDED,
    ROLE_ASSERTED_BEFORE_CONFIRMATION, ROLE_KNOWN_BEFORE_CONFIRM,
    SNAPSHOT_CONTRACT_MISMATCH, FUTURE_TIMESTAMP_REFUSED, DEAD_ID_REUSE_REFUSED,
    REVERSAL_REFERENCE_UNAVAILABLE, REVERSAL_WINDOW_EXPIRED,
)
assert len(REASONS_V43) == 29, f"setul de reason codes trebuie sa fie inchis la 29, are {len(REASONS_V43)}"

ROLES_V43: tuple[str, ...] = ("ACCUMULATION_CONFIRMED", "DISTRIBUTION_CONFIRMED",
                              "TREND_EXHAUSTION_CONFIRMED", "TREND_CONTINUATION_CONFIRMED")


# ═══════════════════════════════════ configurație — port fidel al `ConfigV43` din harness ═══════════════════════════════════

@_dc.dataclass(frozen=True, slots=True)
class ConfigV43:
    """Câmpuri IDENTICE cu `ConfigV43` din harness — inclusiv setul EXACT, ca `config_id()` (aceeași
    formulă: dict peste `__dataclass_fields__` + cele trei proprietăți derivate, JSON `sort_keys`,
    sha256) să reproducă BIT-IDENTIC valoarea normativă `24f72a60…` pt. valorile implicite CEO-fixate —
    verificat direct (`test_config_id_matches_normative_value`). Gate-ul `acknowledge_construction_only`
    NU e câmp aici (ar strica config_id) — e parametru SEPARAT la construcția producătorului/motorului."""
    d_macro: int = 29
    d_internal: int = 12
    n_touch: int = 2
    K_reentry: int = 22
    N_accept: int = 3
    K_struct: int = 2
    n_external_swings: int = 2
    atr_window: int = 14
    w_atr: float = 0.80
    atr_source: str = "ai_trader.structural_observer.vendor_bridge.atr14"
    atr_provenance_wheel_sha256: str = (
        "39673910666e13708b1d4cb7266d1730bb1c9ceea4e0b021a1bf3cfa1f8281f4")
    contract_version: str = RANGE_HIERARCHICAL_V4_3_CONTRACT_VERSION

    def __post_init__(self) -> None:
        # întărire (hardening) fata de harness: harness cere `CFG.validate()` apelat EXPLICIT de utilizator
        # (potrivit pt. un oracol de testare adversarială); pt. suprafața de producție a prototipului,
        # validarea automată la construcție e mai sigură — nu lasă niciodată un obiect construit-dar-invalid
        # să circule. Nu atinge niciun câmp, deci nu afectează config_id().
        self.validate()

    @property
    def tol_cluster(self) -> float:
        """Banda ÎNTREAGĂ de apartenență la cluster — proprietate CALCULATĂ, niciodată stocată (C2)."""
        return 2.0 * self.w_atr

    @property
    def s_max(self) -> float:
        """Plafonul de DERIVĂ pe durata obiectului — coincide numeric cu `tol_cluster`, măsoară altceva."""
        return 2.0 * self.w_atr

    @property
    def w_atr_sanity_ceiling(self) -> float:
        return 1.3952

    def validate(self) -> None:
        if not (0 < self.w_atr < self.w_atr_sanity_ceiling):
            raise ContractErrorV43(
                f"W_ATR_OUT_OF_SANITY_RANGE: {self.w_atr} not in (0,{self.w_atr_sanity_ceiling})")
        if self.d_internal >= self.d_macro:
            raise ContractErrorV43("D_INTERNAL_NOT_BELOW_D_MACRO")
        if self.n_touch < 2:
            raise ContractErrorV43("N_TOUCH_BELOW_STRUCTURAL_FLOOR")
        if self.K_struct < 1 or self.n_external_swings < 1 or self.N_accept < 1 or self.K_reentry < 1:
            raise ContractErrorV43("NON_POSITIVE_STRUCTURAL_PARAMETER")

    def config_id(self) -> str:
        payload: dict[str, Any] = {**{k: getattr(self, k) for k in self.__dataclass_fields__},
                                   "_derived_tol_cluster": self.tol_cluster,
                                   "_derived_s_max": self.s_max,
                                   "_derived_w_atr_sanity_ceiling": self.w_atr_sanity_ceiling}
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


# ═══════════════════════════════════ obiecte structurale ═══════════════════════════════════

class Cluster:
    """Port al `Cluster` din harness — CU o schimbare de performanță: `center` (mediana) folosește
    `_RunningMedian` (0.4.0, două heap-uri, O(log m) inserare / O(1) citire) în loc de `sorted(members)`
    la fiecare citire. `Cluster.members` din harness ESTE nemărginit pe durata vieții unei structuri
    (exact ca `_Segment.highs`/`.lows` din 0.4.0/V3, ÎNAINTE de fix-ul `_RunningMedian`) — dacă aș fi copiat
    `sorted(self.members)` literal, ar fi fost EXACT defectul O(n log n)/citire, O(n² log n)/durata vieții
    unei structuri lungi pe care 0.4.0 l-a auto-prins și corectat înainte de livrare (vezi
    `ve-brain-tower-artifacts.md`), și exact clasa de defect O(n²) pe care mandatul §14 o interzice explicit
    pt. acest prototip. `members` rămâne lista completă (audit/snapshot), dar NU mai e sursa de citire a
    medianei pe calea fierbinte."""
    __slots__ = ("members", "frozen", "_median")

    def __init__(self) -> None:
        self.members: list[float] = []
        self.frozen = False
        self._median = _RunningMedian()

    @property
    def center(self) -> float | None:
        if not self.members:
            return None
        return self._median.median()

    def offer(self, price: float, tol_abs: float) -> bool:
        """Adaugă un swing dacă e în toleranță față de centrul CURENT (înainte de adăugare). Refuză altfel."""
        if self.frozen:
            return False
        c = self.center
        if c is None or abs(price - c) <= tol_abs:
            self.members.append(price)
            self._median.add(price)
            return True
        return False

    def snapshot(self) -> list[float]:
        return list(self.members)

    @classmethod
    def restore(cls, members: list[float], frozen: bool) -> "Cluster":
        c = cls()
        for m in members:
            c.members.append(m)
            c._median.add(m)
        c.frozen = frozen
        return c


class _UnboundedSlope:
    """Panta OLS pe ÎNTREAGA durată a unei structuri (nemărginită — spre deosebire de fereastra trailing
    `d_min_bars` din 0.4.1) — statistici suficiente O(1)/bară, NICIODATĂ o re-parcurgere completă. Aceeași
    tehnică validată în 0.4.1 (§12 RT-RANGE-0004), aici FĂRĂ fază de evicție (nu există fereastră, doar
    creștere): `Sx(n)=n(n-1)/2`, `Sxx(n)=n(n-1)(2n-1)/6` formă închisă din `n` singur; `Sy`/`Sxy` acumulate
    prin adăugare pură. Nu stochează NICIUN preț — doar trei scalari, memorie O(1) pe durata vieții
    structurii, oricât de lungă (exact tipul de cost pe care mandatul §14 îl interzice dacă ar fi O(n)/bară
    re-calculat din lista completă de închideri, cum face `normalized_drift` din harness dacă e apelat naiv
    pe o listă `closes` care crește nemărginit)."""
    __slots__ = ("_sum_y", "_sum_xy", "_n")

    def __init__(self) -> None:
        self._sum_y = 0.0
        self._sum_xy = 0.0
        self._n = 0

    def push(self, y: float) -> None:
        self._sum_xy += self._n * y
        self._sum_y += y
        self._n += 1

    def slope(self) -> float:
        n = self._n
        if n < 2:
            return 0.0
        sx = n * (n - 1) / 2.0
        sxx = n * (n - 1) * (2 * n - 1) / 6.0
        denom = n * sxx - sx * sx
        if denom == 0.0:
            return 0.0
        return (n * self._sum_xy - sx * self._sum_y) / denom

    def snapshot(self) -> dict[str, Any]:
        return {"sum_y": self._sum_y, "sum_xy": self._sum_xy, "n": self._n}

    @classmethod
    def restore(cls, st: dict[str, Any]) -> "_UnboundedSlope":
        obj = cls()
        obj._sum_y = st["sum_y"]; obj._sum_xy = st["sum_xy"]; obj._n = st["n"]
        return obj


class Structure:
    """Port al `Structure` din harness, cu urmărirea O(1)/bară a derivei (`_UnboundedSlope` în loc de o
    listă `closes` re-parcursă la fiecare bară) și `n_bars` (numărul de bare de la `start_ts`, folosit ca
    `duration` în `normalized_drift` — echivalentul lui `bar - start_ts + 1` din harness)."""

    def __init__(self, *, structure_id: int, depth: Depth, parent_structure_id: int | None,
                start_ts: int) -> None:
        self.structure_id = structure_id
        self.depth = depth
        self.parent_structure_id = parent_structure_id
        self.start_ts = start_ts
        self.confirm_ts: int | None = None
        self.end_ts: int | None = None
        self.end_reason: str | None = None
        self.state: MacroState | InternalState = MacroState.RANGE_FORMING
        self.up = Cluster()
        self.dn = Cluster()
        self.atr_ref: float | None = None
        self.predecessor_id: int | None = None
        self.role: str | None = None
        self.role_known_ts: int | None = None
        self.breakout_side: str | None = None   # 'upper'/'lower' -- pt. decizia de rol retrospectiv (VE, §9)
        self._drift = _UnboundedSlope()
        self.n_bars = 0
        self.reached_confirmed = False
        # excursie curentă (breach în curs) -- vezi Excursion, atașată separat de producator

    @property
    def boundary_upper(self) -> float | None:
        return self.up.center

    @property
    def boundary_lower(self) -> float | None:
        return self.dn.center

    def zones(self, w_atr: float) -> tuple[tuple[float, float], tuple[float, float]] | None:
        if self.boundary_upper is None or self.boundary_lower is None or self.atr_ref is None:
            return None
        h = w_atr * self.atr_ref
        return ((self.boundary_upper - h, self.boundary_upper + h),
                (self.boundary_lower - h, self.boundary_lower + h))

    def push_close(self, close: float) -> None:
        self._drift.push(close)
        self.n_bars += 1

    def normalized_drift(self, atr: float) -> float:
        if atr <= 0:
            return 0.0
        return abs(self._drift.slope()) * self.n_bars / atr

    def assign_role(self, role: str, known_ts: int) -> None:
        if self.end_ts is None:
            raise ContractErrorV43(ROLE_ASSERTED_BEFORE_CONFIRMATION)
        if self.confirm_ts is None or known_ts < self.confirm_ts:
            raise ContractErrorV43(ROLE_KNOWN_BEFORE_CONFIRM)
        if role not in ROLES_V43:
            raise ContractErrorV43(f"UNKNOWN_ROLE:{role}")
        self.role = role
        self.role_known_ts = known_ts

    def snapshot(self) -> dict[str, Any]:
        return {
            "structure_id": self.structure_id, "depth": self.depth.value,
            "parent_structure_id": self.parent_structure_id, "start_ts": self.start_ts,
            "confirm_ts": self.confirm_ts, "end_ts": self.end_ts, "end_reason": self.end_reason,
            "state": self.state.value, "up_members": self.up.snapshot(), "up_frozen": self.up.frozen,
            "dn_members": self.dn.snapshot(), "dn_frozen": self.dn.frozen, "atr_ref": self.atr_ref,
            "predecessor_id": self.predecessor_id, "role": self.role, "role_known_ts": self.role_known_ts,
            "breakout_side": self.breakout_side,
            "drift_state": self._drift.snapshot(), "n_bars": self.n_bars,
            "reached_confirmed": self.reached_confirmed,
        }

    @classmethod
    def restore(cls, st: dict[str, Any]) -> "Structure":
        s = cls(structure_id=st["structure_id"], depth=Depth(st["depth"]),
                parent_structure_id=st["parent_structure_id"], start_ts=st["start_ts"])
        s.confirm_ts = st["confirm_ts"]; s.end_ts = st["end_ts"]; s.end_reason = st["end_reason"]
        state_val = st["state"]
        s.state = MacroState(state_val) if state_val in {e.value for e in MacroState} else InternalState(state_val)
        s.up = Cluster.restore(st["up_members"], st["up_frozen"])
        s.dn = Cluster.restore(st["dn_members"], st["dn_frozen"])
        s.atr_ref = st["atr_ref"]
        s.predecessor_id = st["predecessor_id"]; s.role = st["role"]; s.role_known_ts = st["role_known_ts"]
        s.breakout_side = st["breakout_side"]
        s._drift = _UnboundedSlope.restore(st["drift_state"]); s.n_bars = st["n_bars"]
        s.reached_confirmed = st["reached_confirmed"]
        return s


# ═══════════════════════════════════ primitive pure — port fidel din harness ═══════════════════════════════════

def degeneracy_check(st: Structure, cfg: ConfigV43) -> str | None:
    """KILL (ZONES_INVERTED/ZONES_DEGENERATE), nu DELAY — identic cu harness-ul. ATR_UNAVAILABLE și
    ESTABLISHING_FEW_SWINGS NU sunt KILL (candidatul poate încă primi ATR/swing-uri) — asimetria e impusă
    de orchestrare (`RangeSemanticProducerV43`), nu de această funcție pură (identică semantic cu harness-ul,
    care e la fel de pură — nu marchează nimic `end_ts` aici)."""
    bu, bl = st.boundary_upper, st.boundary_lower
    if bu is None or bl is None or st.atr_ref is None:
        return ATR_UNAVAILABLE if st.atr_ref is None else ESTABLISHING_FEW_SWINGS
    if bu < bl:
        return ZONES_INVERTED
    if (bu - bl) <= 2.0 * cfg.w_atr * st.atr_ref:
        return ZONES_DEGENERATE
    return None


def evaluate_candidate_with_n_touch(st: Structure | None, bar: int, cfg: ConfigV43) -> str:
    """**Găsit, documentat**: `n_touch` (§4 mandat: "n_touch=2 pentru fiecare frontieră"; §6 mandat: "minimum
    două swing-uri pe fiecare frontieră"; tabelul §4 din pachetul Statistician, itemul 7) NU e verificat
    NICĂIERI în codul REAL al `degeneracy_check`/`evaluate_candidate` din harness — funcția verifică doar
    `boundary_upper is None`/`boundary_lower is None` (adică `Cluster` GOL, 0 membri), nu `< n_touch`
    (confirmat: `n_touch` apare EXCLUSIV în `ConfigV43.validate()`, ca prag de validare a configurației, NU
    în calea de decizie — verificat prin grep exhaustiv pe cele 409 linii). Testul harness-ului (9a/9b)
    exercită doar cazul complet-gol (0 membri), deci nu discriminează între cele două interpretări posibile.

    Text CEO explicit (§6, nu doar proza spec-ului Statistician) cere "minimum două swing-uri pe fiecare
    frontieră" — deci acest wrapper adaugă gărzii de mai jos, ÎNAINTE de a delega la `evaluate_candidate`
    (portul FIDEL, neschimbat, al funcției din harness, comparabil direct cu oracolul pt. cazul complet-gol
    și pt. toate celelalte gărzi). `degeneracy_check`/`evaluate_candidate` NU au fost modificate — rămân
    ports 1:1, testabile separat contra harness-ului; acest wrapper e stratul de orchestrare adițional."""
    if st is not None and st.end_ts is None:
        if len(st.up.members) < cfg.n_touch or len(st.dn.members) < cfg.n_touch:
            return ESTABLISHING_FEW_SWINGS
    return evaluate_candidate(st, bar, cfg)


def evaluate_candidate(st: Structure | None, bar: int, cfg: ConfigV43) -> str:
    """CORECȚIA C15, portată identic — conjuncția de confirmare, un singur callable, ordine de prioritate
    NORMATIVĂ: intâi input lipsă/KILL (fail-closed), abia apoi poarta de durată."""
    if st is None or st.end_ts is not None:
        return BETWEEN_EPISODES
    kill = degeneracy_check(st, cfg)
    if kill is not None:
        return kill
    d_min = cfg.d_macro if st.depth is Depth.MACRO else cfg.d_internal
    if bar - st.start_ts < d_min:
        return TOO_SHORT_MACRO if st.depth is Depth.MACRO else TOO_SHORT_INTERNAL
    return OK_RANGE_MACRO if st.depth is Depth.MACRO else OK_RANGE_INTERNAL


def offer_swing(st: Structure, price: float, side: str, cfg: ConfigV43) -> tuple[bool, str]:
    """§3.3 apelabil — port fidel. Swingul refuzat NU se pierde (semnalat, nu adăugat) — poate începe un
    episod ulterior, exact cum cere contractul."""
    if st.atr_ref is None:
        return False, ATR_UNAVAILABLE
    cl = st.up if side == "high" else st.dn
    if cl.offer(price, cfg.tol_cluster * st.atr_ref):
        return True, OK_RANGE_MACRO if st.depth is Depth.MACRO else OK_RANGE_INTERNAL
    return False, SWING_OUTSIDE_CLUSTER


def assign_level(cand_start: int, cand_end: int, cand_lo: float, cand_hi: float,
                 parent: Structure | None, cfg: ConfigV43) -> tuple[Depth | None, str | None, int | None]:
    """R1/R2/R3 din contract §2 — port identic (inclusiv corecția C14: părinte INTERNAL => DEPTH_LIMIT_EXCEEDED,
    impus mecanic, nu doar scris)."""
    if parent is None or parent.end_ts is not None:
        return Depth.MACRO, None, None
    contained_time = cand_start >= parent.start_ts and cand_end <= (parent.end_ts or cand_end)
    pb_lo, pb_hi = parent.boundary_lower, parent.boundary_upper
    contained_price = pb_lo is not None and pb_hi is not None and cand_lo >= pb_lo and cand_hi <= pb_hi
    if contained_time and contained_price:
        if parent.depth is Depth.INTERNAL:
            return None, DEPTH_LIMIT_EXCEEDED, None
        return Depth.INTERNAL, None, parent.structure_id
    if cand_start < parent.start_ts <= cand_end or (pb_lo is not None and not contained_price and contained_time):
        return None, PARTIAL_OVERLAP_NO_CONTAINMENT, None
    return None, LEVEL_ASSIGNMENT_UNRESOLVED, None


def promotion_check(p1_left_frozen_boundary: bool, p2_breakout_accepted: bool,
                    external_swings_confirmed: int, p4_previous_closed_and_kept: bool,
                    cfg: ConfigV43) -> tuple[bool, str]:
    """§5 apelabil — port identic (denumire completă normativă `PROMOTION_REFUSED_PRECONDITION_Pk`, C16)."""
    if not p1_left_frozen_boundary:
        return False, PROMOTION_REFUSED_PRECONDITION_P1
    if not p2_breakout_accepted:
        return False, PROMOTION_REFUSED_PRECONDITION_P2
    if external_swings_confirmed < cfg.n_external_swings:
        return False, PROMOTION_REFUSED_PRECONDITION_P3
    if not p4_previous_closed_and_kept:
        return False, PROMOTION_REFUSED_PRECONDITION_P4
    return True, IS_TREND_MACRO


def guard_timestamp(ts: int, as_of: int) -> None:
    if ts > as_of:
        raise ContractErrorV43(FUTURE_TIMESTAMP_REFUSED)


# ═══════════════════════════════════ mașina de excursie (sweep/breakout) — port fidel ═══════════════════════════════════

class Excursion:
    __slots__ = ("open_bar", "direction", "closes_outside", "reentry_bar")

    def __init__(self, open_bar: int, direction: int) -> None:
        self.open_bar = open_bar
        self.direction = direction
        self.closes_outside = 0
        self.reentry_bar: int | None = None

    def observe(self, bar: int, outside: bool, cfg: ConfigV43) -> tuple[str, tuple[str, ...]]:
        if outside:
            self.closes_outside += 1
            if self.closes_outside >= cfg.N_accept:
                return BREAKOUT_ACCEPTED, ()
            return "BOUNDARY_EXCURSION", (NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT,)
        self.closes_outside = 0                      # reintrarea RESETEAZĂ contorul
        if bar - self.open_bar <= cfg.K_reentry:
            self.reentry_bar = bar
            return SWEEP_CONFIRMED, ()
        return "BREAKOUT_PENDING", (NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT,)

    def snapshot(self) -> dict[str, Any]:
        return {"open_bar": self.open_bar, "direction": self.direction,
                "closes_outside": self.closes_outside, "reentry_bar": self.reentry_bar}

    @classmethod
    def restore(cls, st: dict[str, Any]) -> "Excursion":
        ex = cls(st["open_bar"], st["direction"])
        ex.closes_outside = st["closes_outside"]; ex.reentry_bar = st["reentry_bar"]
        return ex


def sweep_reversal_confirmed(ex: Excursion, bar: int, close_price: float,
                             ref_swing: float | None, ref_confirm_ts: int | None,
                             episode_end_ts: int | None) -> tuple[bool, str]:
    """CORECȚIA C13, port identic — fereastra reversalului e VIAȚA EPISODULUI, fără parametru nou."""
    if ex.reentry_bar is None:
        return False, NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT
    if ref_swing is None or ref_confirm_ts is None:
        return False, REVERSAL_REFERENCE_UNAVAILABLE
    if ref_confirm_ts > ex.open_bar:
        raise ContractErrorV43(FUTURE_TIMESTAMP_REFUSED)
    if bar <= ex.reentry_bar:
        return False, NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT
    if episode_end_ts is not None and bar > episode_end_ts:
        return False, REVERSAL_WINDOW_EXPIRED
    broken = close_price > ref_swing if ex.direction == -1 else close_price < ref_swing
    return (True, LIQUIDITY_SWEEP_REVERSAL) if broken else (False, NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT)


# ═══════════════════════════════════ registru cu identitate — port fidel ═══════════════════════════════════

class Registry:
    """Emite ID-uri monoton crescătoare, REFUZĂ reutilizarea unui ID mort (C7)."""

    def __init__(self) -> None:
        self._next = 1
        self._dead: set[int] = set()

    def new_id(self) -> int:
        i = self._next
        self._next += 1
        return i

    def kill(self, i: int) -> None:
        self._dead.add(i)

    def assert_alive(self, i: int) -> None:
        if i in self._dead:
            raise ContractErrorV43(DEAD_ID_REUSE_REFUSED)

    def snapshot(self) -> dict[str, Any]:
        return {"next": self._next, "dead": sorted(self._dead)}

    @classmethod
    def restore(cls, st: dict[str, Any]) -> "Registry":
        r = cls()
        r._next = st["next"]; r._dead = set(st["dead"])
        return r


# ═══════════════════════════════════ rezultat / eveniment per bară ═══════════════════════════════════

@_dc.dataclass(frozen=True, slots=True)
class RangeEventV43:
    kind: str
    bar_index: int
    structure_id: int | None
    depth: str | None
    reason_codes: tuple[str, ...]
    not_yet_available: tuple[str, ...]
    boundary: str | None = None


@_dc.dataclass(frozen=True, slots=True)
class RangeSemanticResultV43:
    available: bool
    bar_index: int
    ts_close: int
    macro_id: int | None
    macro_reason: str
    macro_state: str | None
    macro_boundary_upper: float | None
    macro_boundary_lower: float | None
    macro_confirm_ts: int | None
    macro_role: str | None
    regime: str | None              # 'TREND_UP'/'TREND_DOWN' cât timp niciun MACRO nu e activ, altfel None
    internal_id: int | None
    internal_reason: str | None
    internal_state: str | None
    internal_boundary_upper: float | None
    internal_boundary_lower: float | None
    internal_role: str | None
    config_id: str
    contract_version: str


# ═══════════════════════════════════ producătorul — orchestrarea per-bară (VE, §"ce a mai rămas") ═══════════════════════════════════

class RangeSemanticProducerV43:
    """Compune primitivele PURE de mai sus (identice cu harness-ul — oracolul contractual) într-un detector
    INCREMENTAL, O(1)/bară. Deciziile de ORCHESTRARE de mai jos (când se formează un candidat nou, cui i se
    oferă un swing, ce se întâmplă cu un candidat refuzat, când se verifică promovarea/rolul) NU sunt scrise
    în harness — harness-ul verifică doar funcțiile pure, apelate cu stări deja construite manual în teste.
    Verdictul Red Team autorizează explicit exact acest pas ("orchestrarea per-bară, nu inventarea unei
    reguli") — fiecare decizie de orchestrare de mai jos e documentată, NU ascunsă.

    **Decizii de orchestrare (documentate, nu-inventie-de-reguli — reguli deja normative, doar SECVENȚIATE)**:
    1. Fereastra de fractal (K_struct) e GLOBALĂ (un singur detector de swing-uri), nu per-structură — swing-urile
       sunt o proprietate a PREȚULUI, nu a structurii care le observă (identic cu N1/V3).
    2. Un candidat NOU (la orice adâncime) începe să se formeze din PRIMUL swing pe o parte; `assign_level`
       se apelă prima dată quando are ȘI un swing sus ȘI un swing jos (geometrie minimă pt. cand_lo/cand_hi;
       `cand_start`=primul dintre cele două, `cand_end`=bara curentă). Testat împotriva părintelui cel mai
       ADÂNC deschis (`_active_internal` dacă e deschis, altfel `_active_macro`, altfel None) — asta face
       `DEPTH_LIMIT_EXCEEDED` reachable natural (candidat conținut într-un INTERNAL deja activ).
    3. Un candidat REFUZAT (`PARTIAL_OVERLAP_NO_CONTAINMENT`/`LEVEL_ASSIGNMENT_UNRESOLVED`/`DEPTH_LIMIT_EXCEEDED`)
       nu rămâne "pe pauză" să fie reîncercat — swing-urile sale rămân disponibile (nepierdute, ca la
       `offer_swing`) pt. UN candidat viitor, format din zero, zero-lookahead honest (nicio reclasificare
       retroactivă a unei bare deja raportate).
    4. `ZONES_INVERTED`/`ZONES_DEGENERATE` = KILL imediat (ID mort, discardat din urmărire) — `ATR_UNAVAILABLE`/
       `ESTABLISHING_FEW_SWINGS` NU sunt KILL (candidatul așteaptă mai multe swing-uri/ATR). Asimetria nu e
       scrisă în `degeneracy_check` (funcție pură) — mandatul §6 o cere explicit doar pt. gardă/degenerare.
    5. `atr_ref` al unei structuri active se RE-CITEȘTE din ATR-ul curent la fiecare bară (nu e înghețat la
       formare) — identic cu V3 (`w = cfg.w_atr * self._last_atr`, recalculat mereu), ca zonele să rămână
       adaptive la volatilitate pe durata unei structuri lungi.
    6. Promovarea: breakout acceptat -> MACRO se închide imediat (`TERMINATED_BY_BREAKOUT`, identic cu V3) ->
       se numără swing-uri CONFIRMATE dincolo de frontiera SPARTĂ, în direcția ruperii -> la al doilea,
       `promotion_check` (P1/P4 mecanic adevărate — originalul e deja închis+păstrat) -> `IS_TREND_MACRO` ->
       regim `TREND_UP`/`TREND_DOWN` raportat cât timp niciun MACRO nou nu s-a confirmat încă.
    7. Rol retrospectiv: un episod ÎNCHIS (MACRO sau INTERNAL, prin breakout, nu prin KILL) primește rol
       când succesorul lui DIRECT (`predecessor_id`) atinge la rândul lui `OK_RANGE_*`/promovare — direcția
       succesorului (aceeași parte cu ruperea originalului) decide ACCUMULATION vs DISTRIBUTION (identic
       pt. TREND: CONTINUATION dacă succesorul continuă direcția, EXHAUSTION altfel). `role_known_ts` = bara
       la care succesorul a confirmat.
    """

    def __init__(self, config: ConfigV43) -> None:
        self._cfg = config
        self._n = 0
        self._last_atr: float | None = None
        k = config.K_struct
        self._wh: deque[float] = deque(maxlen=2 * k + 1)
        self._wl: deque[float] = deque(maxlen=2 * k + 1)
        self._registry = Registry()
        self._active_macro: Structure | None = None
        self._active_internal: Structure | None = None
        self._macro_excursion: Excursion | None = None
        self._internal_excursion: Excursion | None = None
        self._macro_reversal_watch: dict[str, Any] | None = None
        self._internal_reversal_watch: dict[str, Any] | None = None
        self._pending_up: tuple[int, float] | None = None
        self._pending_dn: tuple[int, float] | None = None
        self._promo_direction: int | None = None
        self._promo_broken_boundary: float | None = None
        self._promo_external_count = 0
        self._promo_original_id: int | None = None
        self._promo_fired = False   # **Găsit, remediat**: gardă SEPARATĂ de `_regime`, care se poate reseta
                                    # (raportare) când un candidat nou se FORMEAZĂ -- fără ea, promovarea putea
                                    # emite IS_TREND_MACRO de mai multe ori pt. ACEEAȘI fereastră de breakout
                                    # (descoperit prin exercitarea unei fixture HBL-20, nu prin citirea codului)
        self._regime: str | None = None
        self._macro_history: deque[Structure] = deque(maxlen=64)
        self._internal_history: deque[Structure] = deque(maxlen=64)
        self._awaiting_role: dict[int, Structure] = {}
        self._last_ended_macro_id: int | None = None
        self._last_ended_internal_id: int | None = None

    @property
    def macro_history(self) -> tuple[dict[str, Any], ...]:
        return tuple(s.snapshot() for s in self._macro_history)

    @property
    def internal_history(self) -> tuple[dict[str, Any], ...]:
        return tuple(s.snapshot() for s in self._internal_history)

    # ── detecție fractal, K_struct fix, identică (independentă high/low) cu `confirmed_swings` din harness ──
    def _detect_confirmed_swings(self, i: int) -> list[tuple[int, float, bool]]:
        k = self._cfg.K_struct
        out: list[tuple[int, float, bool]] = []
        if len(self._wh) == 2 * k + 1:
            c = k
            ch = self._wh[c]
            if ch == max(self._wh) and list(self._wh).count(ch) == 1:
                out.append((i - k, ch, True))
            cl = self._wl[c]
            if cl == min(self._wl) and list(self._wl).count(cl) == 1:
                out.append((i - k, cl, False))
        return out

    def _deepest_open(self) -> Structure | None:
        if self._active_internal is not None:
            return self._active_internal
        return self._active_macro

    def _clear_pending(self) -> None:
        self._pending_up = None; self._pending_dn = None

    def _offer_swing_everywhere(self, i: int, price: float, is_high: bool, events: list[RangeEventV43]) -> None:
        side = "high" if is_high else "low"
        accepted_by_macro = False
        for st in (self._active_macro, self._active_internal):
            if st is not None:
                ok, _ = offer_swing(st, price, side, self._cfg)
                if st is self._active_macro:
                    accepted_by_macro = ok
        # numărătoarea de swing-uri externe pt. promovare (dincolo de frontiera SPARTĂ, în direcția ruperii)
        if self._promo_direction is not None and self._promo_broken_boundary is not None:
            beyond = (price > self._promo_broken_boundary if self._promo_direction == 1
                     else price < self._promo_broken_boundary)
            if beyond:
                self._promo_external_count += 1
                self._maybe_promote(i, events)
        # formarea unui candidat NOU (dacă locul e liber la adâncimea relevantă)
        forming_internal = self._active_macro is not None and self._active_internal is None
        forming_macro = self._active_macro is None
        if not (forming_internal or forming_macro):
            return
        # **Găsit, remediat**: un swing deja ACCEPTAT de clusterul MACRO-ului (îi extinde propria frontieră)
        # nu poate ALIMENTA SIMULTAN un candidat INTERNAL nou -- altfel primele swing-uri care formează chiar
        # MACRO-ul deveneau, din greșeală, "candidatul intern" (aceleași puncte de preț la ambele adâncimi).
        # Un INTERNAL legitim se formează DOAR din swing-uri pe care MACRO-ul însuși le-a refuzat
        # (SWING_OUTSIDE_CLUSTER) -- adică un nivel de preț STRICT mai local.
        if forming_internal and accepted_by_macro:
            return
        # **Găsit, remediat**: odată ce MACRO-ul e confirmat, clusterele lui îngheață (`frozen=True`, §6) --
        # un swing care doar RE-TESTEAZĂ nivelul MACRO-ului (aceeași frontieră, respinsă STRICT din cauza
        # înghețării, nu din cauza distanței) e totuși respins de `offer_swing` cu ACELAȘI motiv generic
        # (`SWING_OUTSIDE_CLUSTER`) ca un swing genuin nou -- deci `accepted_by_macro=False` nu mai distinge
        # cele două cazuri. Fără acest filtru suplimentar, o simplă reatingere a frontierei MACRO înghețate
        # (prețul revine exact la vechiul extrem al MACRO-ului) devenea, din greșeală, ancora unui candidat
        # INTERNAL nou -- descoperit prin exercitarea unei fixture reale (limita inferioară a unui internal
        # ieșise identică cu vechiul extrem al MACRO-ului, la 12+ puncte de restul geometriei internalului,
        # blocând definitiv al doilea touch pe acea parte). Filtru: dacă prețul e încă în `tol_cluster` față
        # de frontiera proprie a MACRO-ului pe partea respectivă, tratează-l ca re-testare de frontieră (fără
        # informație nouă), nu ca material pt. candidat nou -- ACEEAȘI toleranță normativă folosită de
        # `Cluster.offer`, nicio valoare inventată.
        # **F5 (RT-RANGE-0011, conformance fix, nu schimbare semantică)**: `tol_cluster` e un multiplicator
        # ATR FĂRĂ unitate (`2 × w_atr = 1.60`), exact ca la linia lui `offer_swing` de mai sus
        # (`cfg.tol_cluster * st.atr_ref`) -- comparat aici DIRECT cu o distanță de preț în USD, fără scalare
        # prin ATR, trata greșit 1.60 ca 1.60 USD în loc de 1.60×ATR USD (bandă normativă mediană ~2,997 USD
        # vs 1,600 USD implementat greșit -- bandă normativă mai LARGĂ pe ~87% din bare). Comentariul de mai
        # sus afirma "ACEEAȘI toleranță ca `Cluster.offer`", dar codul nu implementa acea identitate -- găsit
        # de Statistician (pachet `870d3f8`), confirmat independent de Red Team (`RT-RANGE-0011`/`8d71fce`).
        # Corectat prin scalare cu `atr_ref`, mirror exact al liniei 442. ATR indisponibil (`atr_ref is None`)
        # -> filtrul NU se poate aplica (nicio toleranță absolută calculabilă) -- swing-ul trece la calea
        # normală de candidat nou, fail-closed spre "nu presupune re-testare", nu spre "presupune re-testare".
        # Direcția e cunoscută dinainte: bandă mai largă -> filtrul se declanșează MAI des -> MAI puțini
        # candidați INTERNAL -- decis pe conformitate, nu pe recall (interzis explicit de mandat).
        if forming_internal and self._active_macro is not None:
            boundary = self._active_macro.up.center if is_high else self._active_macro.dn.center
            atr_ref = self._active_macro.atr_ref
            if boundary is not None and atr_ref is not None and abs(price - boundary) <= self._cfg.tol_cluster * atr_ref:
                return
        # **Găsit, remediat**: `_pending_up`/`_pending_dn` PĂSTREAZĂ DOAR cel mai RECENT swing respins pe
        # fiecare parte (nu acumulează o listă nemărginită) -- o listă care creștea la nesfârșit putea lega
        # un swing VECHI, respins cu mult timp în urmă (posibil aparținând altei faze de preț cu totul), de
        # un swing NOU, complet nerelaționat, doar fiindcă erau primele disponibile pe fiecare parte la
        # momentul formării candidatului -- descoperit prin exercitarea unei fixture reale (limita inferioară
        # a unui internal ieșise identică cu un swing de-al MACRO-ului, mult mai vechi și nerelaționat).
        # Reținând doar CEL MAI RECENT swing pe fiecare parte, candidatul nou se formează din geometrie
        # temporal apropiată, coerentă.
        if is_high:
            self._pending_up = (i, price)
        else:
            self._pending_dn = (i, price)
        if self._pending_up is None or self._pending_dn is None:
            return
        cand_start = min(self._pending_up[0], self._pending_dn[0])
        cand_end = i
        cand_hi = self._pending_up[1]
        cand_lo = self._pending_dn[1]
        parent = self._deepest_open() if forming_internal else None
        depth, refuse_reason, parent_id = assign_level(cand_start, cand_end, cand_lo, cand_hi, parent, self._cfg)
        if depth is None:
            events.append(RangeEventV43(kind=refuse_reason or LEVEL_ASSIGNMENT_UNRESOLVED, bar_index=i,
                                        structure_id=None, depth=None, reason_codes=(refuse_reason or "",),
                                        not_yet_available=()))
            self._clear_pending()
            return
        new_id = self._registry.new_id()
        st = Structure(structure_id=new_id, depth=depth, parent_structure_id=parent_id, start_ts=cand_start)
        st.atr_ref = self._last_atr
        offer_swing(st, self._pending_up[1], "high", self._cfg)
        offer_swing(st, self._pending_dn[1], "low", self._cfg)
        self._clear_pending()
        if depth is Depth.MACRO:
            st.predecessor_id = self._last_ended_macro_id; self._last_ended_macro_id = None
            self._active_macro = st
            self._regime = None   # doar eticheta de RAPORTARE -- urmărirea promovării continuă separat mai
                                  # jos, până la CONFIRMAREA acestui candidat (nu doar formarea lui, §8)
        else:
            st.predecessor_id = self._last_ended_internal_id; self._last_ended_internal_id = None
            self._active_internal = st

    # ── închiderea unei structuri: KILL (degenerare/inversare) sau breakout acceptat ──
    def _kill_structure(self, depth: Depth, st: Structure, i: int, reason: str,
                        events: list[RangeEventV43]) -> None:
        st.end_ts = i; st.end_reason = reason
        self._registry.kill(st.structure_id)
        hist = self._macro_history if depth is Depth.MACRO else self._internal_history
        hist.append(st)
        events.append(RangeEventV43(kind=reason, bar_index=i, structure_id=st.structure_id,
                                    depth=depth.name, reason_codes=(reason,), not_yet_available=()))
        if depth is Depth.MACRO:
            self._last_ended_macro_id = st.structure_id
            self._active_macro = None; self._macro_excursion = None
        else:
            self._last_ended_internal_id = st.structure_id
            self._active_internal = None; self._internal_excursion = None

    def _close_via_breakout(self, depth: Depth, st: Structure, i: int, side: str,
                            events: list[RangeEventV43]) -> None:
        st.end_ts = i; st.end_reason = BREAKOUT_ACCEPTED; st.breakout_side = side
        hist = self._macro_history if depth is Depth.MACRO else self._internal_history
        hist.append(st)
        kind = BREAKOUT_ACCEPTED
        events.append(RangeEventV43(kind=kind, bar_index=i, structure_id=st.structure_id, depth=depth.name,
                                    reason_codes=(BREAKOUT_ACCEPTED,), not_yet_available=(), boundary=side))
        if depth is Depth.MACRO:
            self._last_ended_macro_id = st.structure_id
            self._active_macro = None; self._macro_excursion = None
            self._promo_direction = 1 if side == "upper" else -1
            self._promo_broken_boundary = st.boundary_upper if side == "upper" else st.boundary_lower
            self._promo_fired = False
            self._promo_external_count = 0
            self._promo_original_id = st.structure_id
        else:
            self._last_ended_internal_id = st.structure_id
            self._active_internal = None; self._internal_excursion = None
        self._awaiting_role[st.structure_id] = st

    # ── un singur pas (excursie/breach/gate) pt. o adâncime — reutilizat pt. MACRO și INTERNAL ──
    def _step_depth(self, depth: Depth, i: int, high: float, low: float, close: float,
                    events: list[RangeEventV43]) -> str:
        st = self._active_macro if depth is Depth.MACRO else self._active_internal
        if st is None:
            return BETWEEN_EPISODES
        kill = degeneracy_check(st, self._cfg)
        if kill in (ZONES_INVERTED, ZONES_DEGENERATE):
            self._kill_structure(depth, st, i, kill, events)
            return kill
        # **Găsit, remediat**: mandatul §6 spune explicit "zonele se îngheață la confirm_ts; atingerile sunt
        # evenimente POST-confirmare" -- excursia/breach-ul nu are voie să se declanșeze pe un candidat ÎNCĂ
        # ÎN FORMARE (înainte de prima confirmare OK_RANGE_*). Descoperit prin exercitarea unei fixture de
        # promovare: fără această gardă, candidați proaspăt formați (0 bare de viață) intrau IMEDIAT în
        # excursie/breakout doar fiindcă geometria lor inițială era strânsă față de prețul curent, aflat deja
        # în plină tendință -- o cascadă falsă de "breakout" pe structuri niciodată confirmate.
        zones = st.zones(self._cfg.w_atr) if st.reached_confirmed else None
        excursion = self._macro_excursion if depth is Depth.MACRO else self._internal_excursion
        if excursion is not None and zones is not None:
            (up_lo, up_hi), (lo_lo, lo_hi) = zones
            side = "upper" if excursion.direction == 1 else "lower"
            outside = close > up_hi if side == "upper" else close < lo_lo
            kind, nya = excursion.observe(i, outside, self._cfg)
            if kind == BREAKOUT_ACCEPTED:
                self._close_via_breakout(depth, st, i, side, events)
                return BREAKOUT_ACCEPTED
            if kind == SWEEP_CONFIRMED:
                events.append(RangeEventV43(kind=SWEEP_CONFIRMED, bar_index=i, structure_id=st.structure_id,
                                            depth=depth.name, reason_codes=(SWEEP_CONFIRMED,),
                                            not_yet_available=(), boundary=side))
                # **Găsit, remediat**: `sweep_reversal_confirmed` (C13) era portat fidel și testat DIRECT,
                # dar nu era apelat NICĂIERI din bucla per-bară -- adică `LIQUIDITY_SWEEP_REVERSAL` nu putea
                # fi emis NICIODATĂ prin observare reală bară-cu-bară, doar prin apel manual al funcției pure
                # (descoperit abia acum, verificând EXPLICIT dacă orchestrarea chiar cheamă funcția, nu doar
                # dacă string-ul constantei apare undeva în sursă). Fereastra reversalului e "viața episodului"
                # (C13) -- deci excursia rezolvată prin reintrare rămâne "sub observație" (watch separat de
                # slot-ul de excursie activă, care trebuie golit ca o excursie NOUĂ să poată deschide) până
                # când fie prețul confirmă reversal-ul (close dincolo de swing-ul de referință de pe partea
                # OPUSĂ direcției excursiei), fie episodul se închide (REVERSAL_WINDOW_EXPIRED, verificat
                # dinamic la fiecare bară, nu memorat static la momentul creării watch-ului).
                ref_side = "upper" if excursion.direction == -1 else "lower"
                watch = {"excursion": excursion.snapshot(), "structure_id": st.structure_id,
                         "ref_side": ref_side,
                         "ref_swing": (st.up.center if ref_side == "upper" else st.dn.center),
                         "ref_confirm_ts": st.confirm_ts}
                if depth is Depth.MACRO:
                    self._macro_excursion = None
                    self._macro_reversal_watch = watch
                else:
                    self._internal_excursion = None
                    self._internal_reversal_watch = watch
                return SWEEP_CONFIRMED
            events.append(RangeEventV43(kind=kind, bar_index=i, structure_id=st.structure_id,
                                        depth=depth.name, reason_codes=(), not_yet_available=nya,
                                        boundary=side))
            return NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT
        if zones is not None:
            (up_lo, up_hi), (lo_lo, lo_hi) = zones
            if close > up_hi or close < lo_lo:
                side = "upper" if close > up_hi else "lower"
                ex = Excursion(open_bar=i - 1, direction=1 if side == "upper" else -1)
                if depth is Depth.MACRO:
                    self._macro_excursion = ex
                else:
                    self._internal_excursion = ex
                kind, nya = ex.observe(i, True, self._cfg)
                if kind == BREAKOUT_ACCEPTED:   # posibil doar dacă N_accept==1 (nepermis, dar defensiv corect)
                    self._close_via_breakout(depth, st, i, side, events)
                    return BREAKOUT_ACCEPTED
                events.append(RangeEventV43(kind=kind, bar_index=i, structure_id=st.structure_id,
                                            depth=depth.name, reason_codes=(), not_yet_available=nya,
                                            boundary=side))
                return NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT
        reason = evaluate_candidate_with_n_touch(st, i, self._cfg)
        if reason in (OK_RANGE_MACRO, OK_RANGE_INTERNAL) and not st.reached_confirmed:
            st.reached_confirmed = True
            if st.confirm_ts is None:
                st.confirm_ts = i
            # §6 mandat: "zonele se îngheață la confirm_ts" + "extremele noi nu mută frontierele" -- odată
            # confirmată, frontiera nu mai poate fi deplasată de swing-uri ulterioare (Cluster.frozen, portat
            # din harness dar niciodată folosit până acum -- găsit prin exercitarea directă a unei fixture).
            st.up.frozen = True
            st.dn.frozen = True
            if depth is Depth.MACRO and self._promo_direction is not None:
                # §8 mandat: promovarea concurează cu formarea unui candidat NOU după breakout -- oricare se
                # rezolvă PRIMUL câștigă. Dacă un nou MACRO CONFIRMĂ (nu doar se formează) înainte ca cele
                # n_external_swings cerute să apară, fereastra de promovare se închide -- piața s-a
                # consolidat din nou, nu a confirmat un trend.
                self._promo_direction = None; self._promo_broken_boundary = None; self._promo_external_count = 0
            events.append(RangeEventV43(kind=reason, bar_index=i, structure_id=st.structure_id,
                                        depth=depth.name, reason_codes=(reason,), not_yet_available=()))
            self._resolve_role_if_watched(st, i)
        return reason

    def _end_ts_for(self, depth: Depth, structure_id: int) -> int | None:
        """`episode_end_ts` pt. C13 -- verificat DINAMIC la fiecare bară (nu memorat static la creare):
        None cât timp structura e încă activă (episodul e viu), end_ts real dacă s-a închis între timp
        (istoric mărginit, maxlen=64) — dacă id-ul nu se mai găsește nicăieri (evacuat din istoricul
        mărginit înainte ca reversal-ul să se rezolve, extrem de improbabil), tratează fail-closed drept
        EXPIRAT (nu drept "încă deschis la nesfârșit")."""
        active = self._active_macro if depth is Depth.MACRO else self._active_internal
        if active is not None and active.structure_id == structure_id:
            return None
        history = self._macro_history if depth is Depth.MACRO else self._internal_history
        for s in history:
            if s.structure_id == structure_id:
                return s.end_ts
        return -1   # evacuat din istoric -- fail-closed: tratat ca deja expirat, nu ca etern deschis

    def _check_reversal_watch(self, depth: Depth, i: int, close: float, events: list[RangeEventV43]) -> None:
        watch = self._macro_reversal_watch if depth is Depth.MACRO else self._internal_reversal_watch
        if watch is None:
            return
        ex = Excursion.restore(watch["excursion"])
        episode_end_ts = self._end_ts_for(depth, watch["structure_id"])
        ok, reason = sweep_reversal_confirmed(
            ex, i, close, watch["ref_swing"], watch["ref_confirm_ts"], episode_end_ts)
        if ok:
            events.append(RangeEventV43(kind=LIQUIDITY_SWEEP_REVERSAL, bar_index=i,
                                        structure_id=watch["structure_id"], depth=depth.name,
                                        reason_codes=(LIQUIDITY_SWEEP_REVERSAL,), not_yet_available=()))
            if depth is Depth.MACRO:
                self._macro_reversal_watch = None
            else:
                self._internal_reversal_watch = None
        elif reason == REVERSAL_WINDOW_EXPIRED:
            if depth is Depth.MACRO:
                self._macro_reversal_watch = None
            else:
                self._internal_reversal_watch = None

    # ── rol retrospectiv: succesorul DIRECT confirmă -> rezolvă rolul predecesorului închis prin breakout ──
    def _resolve_role_if_watched(self, successor: Structure, i: int) -> None:
        pred_id = successor.predecessor_id
        if pred_id is None or pred_id not in self._awaiting_role:
            return
        pred = self._awaiting_role.pop(pred_id)
        # `_promo_fired` (nu `_regime is not None`) -- `_regime` e o etichetă de RAPORTARE, resetată de
        # formarea oricărui candidat nou; `_promo_fired` marchează dacă FEREASTRA de promovare a acestui
        # predecesor anume s-a rezolvat cu succes (limitare cunoscută, documentată: o singură fereastră de
        # promovare urmărită global -- adecvat unui PROTOTIP, nu unui detector de producție cu breakout-uri
        # multiple suprapuse).
        if pred.structure_id == self._promo_original_id and self._promo_fired:
            promo_dir_upper = self._promo_direction == 1
            role = "TREND_CONTINUATION_CONFIRMED" if (successor.breakout_side == "upper") == promo_dir_upper \
                else "TREND_EXHAUSTION_CONFIRMED"
        else:
            role = "ACCUMULATION_CONFIRMED" if pred.breakout_side == "upper" else "DISTRIBUTION_CONFIRMED"
        pred.assign_role(role, i)

    # ── promovare: se verifică după fiecare swing extern nou (vezi `_offer_swing_everywhere`) ──
    def _maybe_promote(self, i: int, events: list[RangeEventV43]) -> None:
        # **Găsit, remediat**: gardă pe `_promo_fired`, NU pe `self._regime is not None` -- `_regime` (doar
        # etichetă de raportare) se resetează la formarea oricărui candidat nou (chiar dacă promovarea NU s-a
        # anulat), ceea ce putea lăsa poarta deschisă și emite `IS_TREND_MACRO` de mai multe ori pt. ACEEAȘI
        # fereastră (descoperit prin exercitarea unei fixture HBL-20 reale, nu prin citirea codului).
        if self._promo_direction is None or self._promo_fired:
            return
        if self._promo_external_count < self._cfg.n_external_swings:
            return
        ok, reason = promotion_check(
            p1_left_frozen_boundary=True, p2_breakout_accepted=True,
            external_swings_confirmed=self._promo_external_count, p4_previous_closed_and_kept=True,
            cfg=self._cfg)
        if ok:
            self._promo_fired = True
            self._regime = "TREND_UP" if self._promo_direction == 1 else "TREND_DOWN"
            events.append(RangeEventV43(kind=IS_TREND_MACRO, bar_index=i, structure_id=self._promo_original_id,
                                        depth=Depth.MACRO.name, reason_codes=(IS_TREND_MACRO,),
                                        not_yet_available=()))

    @staticmethod
    def _state_label(reason: str) -> str | None:
        if reason == BETWEEN_EPISODES:
            return None
        if reason in (ESTABLISHING_FEW_SWINGS, ATR_UNAVAILABLE, TOO_SHORT_MACRO, TOO_SHORT_INTERNAL):
            return MacroState.RANGE_FORMING.value
        if reason in (OK_RANGE_MACRO, OK_RANGE_INTERNAL):
            return MacroState.RANGE_CONFIRMED.value
        if reason == NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT:
            return MacroState.BOUNDARY_EXCURSION.value
        if reason == SWEEP_CONFIRMED:
            return MacroState.SWEEP_CONFIRMED.value
        if reason == BREAKOUT_ACCEPTED:
            return MacroState.EPISODE_CLOSED.value
        if reason in (ZONES_DEGENERATE, ZONES_INVERTED):
            return MacroState.EPISODE_CLOSED.value
        return None

    def _channel_or_state_label(self, st: Structure | None, reason: str) -> str | None:
        """**Găsit, remediat**: `normalized_drift`/`s_max` (item 4/13 din matricea §4 -- 'canal vs sub-range')
        nu era conectat NICĂIERI în bucla per-bară a producătorului (doar în `_UnboundedSlope`/`Structure.
        normalized_drift`, funcție PURĂ, neapelată din `_step_depth`). Descoperit prin exercitarea directă a
        unei fixture MACRO+INTERNAL, nu prin citirea codului. Clasificarea CANAL e STRICT la nivel INTERNAL
        (mandatul §5: un obiect INTERNAL NU poate închide MACRO doar fiindcă e CHANNEL_UP/DOWN/SUBRANGE/
        BALANCE -- deci clasificarea NU e o poartă care blochează confirmarea, e o ETICHETĂ DESCRIPTIVĂ a
        stării INTERNAL, coexistând cu reason code-ul obișnuit; niciun cod nou de reason -- `IS_CHANNEL` NU
        există în setul închis de 29). Aplicată doar cât timp structura e VIE și NEÎNTR-O excursie (altfel
        eticheta de excursie/închidere are prioritate -- canalul e o descriere a stării de RANGE, nu a unei
        rupturi în curs)."""
        if st is None or st.depth is not Depth.INTERNAL or st.end_ts is not None:
            return self._state_label(reason)
        if reason in (NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT, SWEEP_CONFIRMED, BREAKOUT_ACCEPTED):
            return self._state_label(reason)
        if st.atr_ref is None or st.atr_ref <= 0 or st.n_bars < 2:
            return self._state_label(reason)
        drift = st.normalized_drift(st.atr_ref)
        if drift > self._cfg.s_max:
            slope_sign = st._drift.slope()
            return InternalState.INT_CHANNEL_UP.value if slope_sign > 0 else InternalState.INT_CHANNEL_DOWN.value
        base = self._state_label(reason)
        if base == MacroState.RANGE_CONFIRMED.value:
            return InternalState.INT_SUBRANGE.value
        if base == MacroState.RANGE_FORMING.value:
            return InternalState.INT_BALANCE.value
        return base

    def observe(self, *, ts_close: int, open_: float, high: float, low: float, close: float,
               atr: float | None, trend_context: str | None = None
              ) -> tuple[RangeSemanticResultV43, list[RangeEventV43]]:
        i = self._n
        self._n += 1
        self._wh.append(high); self._wl.append(low)
        self._last_atr = atr
        events: list[RangeEventV43] = []

        if atr is not None:
            if self._active_macro is not None:
                self._active_macro.atr_ref = atr
            if self._active_internal is not None:
                self._active_internal.atr_ref = atr

        for sw_bar, price, is_high in self._detect_confirmed_swings(i):
            self._offer_swing_everywhere(sw_bar, price, is_high, events)

        if self._active_macro is not None:
            self._active_macro.push_close(close)
        if self._active_internal is not None:
            self._active_internal.push_close(close)

        macro_reason = self._step_depth(Depth.MACRO, i, high, low, close, events)
        internal_reason = self._step_depth(Depth.INTERNAL, i, high, low, close, events)
        self._check_reversal_watch(Depth.MACRO, i, close, events)
        self._check_reversal_watch(Depth.INTERNAL, i, close, events)

        m = self._active_macro
        n = self._active_internal
        macro_state = self._regime if (m is None and self._regime is not None) else self._state_label(macro_reason)
        internal_state = self._channel_or_state_label(n, internal_reason)
        result = RangeSemanticResultV43(
            available=atr is not None, bar_index=i, ts_close=ts_close,
            macro_id=m.structure_id if m else None, macro_reason=macro_reason, macro_state=macro_state,
            macro_boundary_upper=m.boundary_upper if m else None,
            macro_boundary_lower=m.boundary_lower if m else None,
            macro_confirm_ts=m.confirm_ts if m else None,
            macro_role=m.role if m else None,
            regime=self._regime if m is None else None,
            internal_id=n.structure_id if n else None, internal_reason=internal_reason,
            internal_state=internal_state,
            internal_boundary_upper=n.boundary_upper if n else None,
            internal_boundary_lower=n.boundary_lower if n else None,
            internal_role=n.role if n else None,
            config_id=self._cfg.config_id(), contract_version=self._cfg.contract_version)
        return result, events

    # ── snapshot / restore integral (fail-closed pe contract_version + config_id, C9; +
    #    implementation_fingerprint din F5 -- config_id NU se schimbă la corecția F5 (nicio valoare
    #    de configurație nu s-a modificat), deci gardul contract_version+config_id singur NU ar
    #    refuza un snapshot PRE-F5 -- pericol real de restore cross-versiune, semnalat de Red Team) ──
    def snapshot_state(self) -> dict[str, Any]:
        return {
            "contract_version": self._cfg.contract_version, "config_id": self._cfg.config_id(),
            "implementation_fingerprint": RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT,
            "n": self._n, "wh": list(self._wh), "wl": list(self._wl), "last_atr": self._last_atr,
            "registry": self._registry.snapshot(),
            "active_macro": self._active_macro.snapshot() if self._active_macro else None,
            "active_internal": self._active_internal.snapshot() if self._active_internal else None,
            "macro_excursion": self._macro_excursion.snapshot() if self._macro_excursion else None,
            "internal_excursion": self._internal_excursion.snapshot() if self._internal_excursion else None,
            "macro_reversal_watch": dict(self._macro_reversal_watch) if self._macro_reversal_watch else None,
            "internal_reversal_watch": (dict(self._internal_reversal_watch)
                                        if self._internal_reversal_watch else None),
            "pending_up": list(self._pending_up) if self._pending_up is not None else None,
            "pending_dn": list(self._pending_dn) if self._pending_dn is not None else None,
            "promo_direction": self._promo_direction, "promo_broken_boundary": self._promo_broken_boundary,
            "promo_external_count": self._promo_external_count, "promo_original_id": self._promo_original_id,
            "promo_fired": self._promo_fired,
            "regime": self._regime,
            "macro_history": [s.snapshot() for s in self._macro_history],
            "internal_history": [s.snapshot() for s in self._internal_history],
            "awaiting_role": {k: v.snapshot() for k, v in self._awaiting_role.items()},
            "last_ended_macro_id": self._last_ended_macro_id,
            "last_ended_internal_id": self._last_ended_internal_id,
        }

    def restore_state(self, st: dict[str, Any]) -> None:
        if (st.get("contract_version") != self._cfg.contract_version
                or st.get("config_id") != self._cfg.config_id()
                or st.get("implementation_fingerprint") != RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT):
            raise ContractErrorV43(SNAPSHOT_CONTRACT_MISMATCH)
        k = self._cfg.K_struct
        self._n = st["n"]
        self._wh = deque(st["wh"], maxlen=2 * k + 1); self._wl = deque(st["wl"], maxlen=2 * k + 1)
        self._last_atr = st["last_atr"]
        self._registry = Registry.restore(st["registry"])
        self._active_macro = Structure.restore(st["active_macro"]) if st["active_macro"] else None
        self._active_internal = Structure.restore(st["active_internal"]) if st["active_internal"] else None
        self._macro_excursion = Excursion.restore(st["macro_excursion"]) if st["macro_excursion"] else None
        self._internal_excursion = (Excursion.restore(st["internal_excursion"])
                                    if st["internal_excursion"] else None)
        mrw, irw = st.get("macro_reversal_watch"), st.get("internal_reversal_watch")
        self._macro_reversal_watch = dict(mrw) if mrw else None
        self._internal_reversal_watch = dict(irw) if irw else None
        pu, pd = st["pending_up"], st["pending_dn"]
        self._pending_up = (pu[0], pu[1]) if pu is not None else None
        self._pending_dn = (pd[0], pd[1]) if pd is not None else None
        self._promo_direction = st["promo_direction"]; self._promo_broken_boundary = st["promo_broken_boundary"]
        self._promo_external_count = st["promo_external_count"]; self._promo_original_id = st["promo_original_id"]
        self._promo_fired = st["promo_fired"]
        self._regime = st["regime"]
        self._macro_history = deque((Structure.restore(s) for s in st["macro_history"]), maxlen=64)
        self._internal_history = deque((Structure.restore(s) for s in st["internal_history"]), maxlen=64)
        self._awaiting_role = {int(k2): Structure.restore(v) for k2, v in st["awaiting_role"].items()}
        self._last_ended_macro_id = st["last_ended_macro_id"]
        self._last_ended_internal_id = st["last_ended_internal_id"]
