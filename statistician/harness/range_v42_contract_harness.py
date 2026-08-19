"""HARNESS CONTRACTUAL `range-hierarchical-v4.3` — verifica CONTRACTUL, nu e detector VE si nu e wheel.

Scop unic: sa demonstreze ca fiecare camp obligatoriu din contract e CALCULABIL din datele
disponibile la momentul deciziei, si ca fiecare poarta poate SI sa treaca SI sa esueze.
NU produce semnale, NU calculeaza PnL, NU se livreaza ca artefact de productie.

Configuratie FIXATA de CEO (nemodificabila aici):
    d_macro=29 · d_internal=12 · n_touch=2 · K_reentry=22 · N_accept=3
    K_struct=2 · n_external_swings=2 · atr_window=14 · w_atr=0.80
Derivate (CALCULATE, niciodata stocate):
    tol_cluster = 2*w_atr = 1.60      s_max = 2*w_atr = 1.60
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ─────────────────────────── configuratie ───────────────────────────

@dataclass(frozen=True)
class ConfigV43:
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
    contract_version: str = "range-hierarchical-v4.3"

    # ---- DERIVATE: proprietati, NU campuri. Nu se pot stoca si nu pot diverge. ----
    @property
    def tol_cluster(self) -> float:
        """Banda INTREAGA de apartenenta la cluster. Aceeasi populatie/statistica ca w_atr,
        operand dublu => identitate exacta, demonstrata la v2.7.93 (raport 2.0000000000)."""
        return 2.0 * self.w_atr

    @property
    def s_max(self) -> float:
        """Plafonul de DERIVA pe durata obiectului. Cuplare ratificata la V2, pastrata.
        ★ Coincide NUMERIC cu tol_cluster, dar masoara altceva: deriva vs latimea zonei.
        Sunt doua marimi distincte care se intampla sa aiba aceeasi formula."""
        return 2.0 * self.w_atr

    @property
    def w_atr_sanity_ceiling(self) -> float:
        """Plafon de non-degenerare RE-DERIVAT sub ancora NOUA (v2.7.93): separarea minima
        masurata a frontierelor etichetate = 2.790 ATR => w_atr < 2.790/2. Inlocuieste 0.495,
        care fusese derivat sub ancora VECHE (mediana pe 512 bare) si e un transplant expirat."""
        return 1.3952

    def validate(self) -> None:
        if not (0 < self.w_atr < self.w_atr_sanity_ceiling):
            raise ContractError(f"W_ATR_OUT_OF_SANITY_RANGE: {self.w_atr} not in (0,{self.w_atr_sanity_ceiling})")
        if self.d_internal >= self.d_macro:
            raise ContractError("D_INTERNAL_NOT_BELOW_D_MACRO")
        if self.n_touch < 2:
            raise ContractError("N_TOUCH_BELOW_STRUCTURAL_FLOOR")
        if self.K_struct < 1 or self.n_external_swings < 1 or self.N_accept < 1 or self.K_reentry < 1:
            raise ContractError("NON_POSITIVE_STRUCTURAL_PARAMETER")

    def config_id(self) -> str:
        import hashlib, json
        payload = {**{k: getattr(self, k) for k in self.__dataclass_fields__},
                   "_derived_tol_cluster": self.tol_cluster,
                   "_derived_s_max": self.s_max,
                   "_derived_w_atr_sanity_ceiling": self.w_atr_sanity_ceiling}
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class ContractError(Exception):
    pass


# ─────────────────────────── vocabular ───────────────────────────

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


REASONS = (
    # C17 — codul de esec era despartit pe adancime, cel de succes nu; simetrizat.
    "OK_RANGE_MACRO", "OK_RANGE_INTERNAL", "ESTABLISHING_FEW_SWINGS",
    "TOO_SHORT_MACRO", "TOO_SHORT_INTERNAL",
    "ZONES_DEGENERATE", "ZONES_INVERTED", "ATR_UNAVAILABLE", "BETWEEN_EPISODES",
    "SWING_OUTSIDE_CLUSTER", "NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT", "SWEEP_CONFIRMED",
    "BREAKOUT_ACCEPTED", "LIQUIDITY_SWEEP_REVERSAL", "IS_TREND_MACRO",
    "PROMOTION_REFUSED_PRECONDITION_P1", "PROMOTION_REFUSED_PRECONDITION_P2",
    "PROMOTION_REFUSED_PRECONDITION_P3", "PROMOTION_REFUSED_PRECONDITION_P4",
    "LEVEL_ASSIGNMENT_UNRESOLVED", "PARTIAL_OVERLAP_NO_CONTAINMENT", "DEPTH_LIMIT_EXCEEDED",
    "ROLE_ASSERTED_BEFORE_CONFIRMATION", "ROLE_KNOWN_BEFORE_CONFIRM",
    "SNAPSHOT_CONTRACT_MISMATCH", "FUTURE_TIMESTAMP_REFUSED", "DEAD_ID_REUSE_REFUSED",
    "REVERSAL_REFERENCE_UNAVAILABLE", "REVERSAL_WINDOW_EXPIRED",   # C13
)

ROLES = ("ACCUMULATION_CONFIRMED", "DISTRIBUTION_CONFIRMED",
         "TREND_EXHAUSTION_CONFIRMED", "TREND_CONTINUATION_CONFIRMED")


# ─────────────────────────── obiecte structurale ───────────────────────────

@dataclass
class Cluster:
    members: list[float] = field(default_factory=list)
    frozen: bool = False

    @property
    def center(self) -> float | None:
        if not self.members:
            return None
        s = sorted(self.members)
        n = len(s)
        return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0   # mediana, par -> medie

    def offer(self, price: float, tol_abs: float) -> bool:
        """Adauga un swing daca e in toleranta fata de centrul CURENT. Refuza altfel."""
        if self.frozen:
            return False
        c = self.center
        if c is None or abs(price - c) <= tol_abs:
            self.members.append(price)
            return True
        return False


@dataclass
class Structure:
    structure_id: int
    depth: Depth
    parent_structure_id: int | None
    start_ts: int
    confirm_ts: int | None = None
    end_ts: int | None = None
    state: Any = MacroState.RANGE_FORMING
    up: Cluster = field(default_factory=Cluster)
    dn: Cluster = field(default_factory=Cluster)
    atr_ref: float | None = None
    reason_codes: tuple[str, ...] = ()
    not_yet_available: tuple[str, ...] = ()
    predecessor_id: int | None = None
    role: str | None = None
    role_known_ts: int | None = None

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

    def assign_role(self, role: str, known_ts: int) -> None:
        if self.end_ts is None:
            raise ContractError("ROLE_ASSERTED_BEFORE_CONFIRMATION")
        if self.confirm_ts is None or known_ts < self.confirm_ts:
            raise ContractError("ROLE_KNOWN_BEFORE_CONFIRM")
        if role not in ROLES:
            raise ContractError(f"UNKNOWN_ROLE:{role}")
        self.role = role
        self.role_known_ts = known_ts


# ─────────────────────────── primitive ───────────────────────────

def confirmed_swings(high: list[float], low: list[float], k: int
                     ) -> tuple[list[tuple[int, int, float]], list[tuple[int, int, float]]]:
    """(index_extrem, index_confirmare = extrem+k, pret). Zero lookahead: confirmarea e la j+k."""
    sh, sl = [], []
    n = len(high)
    for j in range(k, n - k):
        w = high[j - k:j + k + 1]
        if high[j] == max(w) and w.count(high[j]) == 1:
            sh.append((j, j + k, high[j]))
        w = low[j - k:j + k + 1]
        if low[j] == min(w) and w.count(low[j]) == 1:
            sl.append((j, j + k, low[j]))
    return sh, sl


def degeneracy_check(st: Structure, cfg: ConfigV43) -> str | None:
    """KILL, nu DELAY: se verifica INAINTE de confirmare si omoara candidatul."""
    bu, bl = st.boundary_upper, st.boundary_lower
    if bu is None or bl is None or st.atr_ref is None:
        return "ATR_UNAVAILABLE" if st.atr_ref is None else "ESTABLISHING_FEW_SWINGS"
    if bu < bl:
        return "ZONES_INVERTED"
    if (bu - bl) <= 2.0 * cfg.w_atr * st.atr_ref:
        return "ZONES_DEGENERATE"
    return None


def normalized_drift(closes: list[float], atr: float, duration: int) -> float:
    """|panta OLS| * durata / ATR — adimensional. Separa INT_CHANNEL_* de INT_SUBRANGE."""
    n = len(closes)
    if n < 2 or atr <= 0:
        return 0.0
    xm = (n - 1) / 2.0
    ym = sum(closes) / n
    den = sum((i - xm) ** 2 for i in range(n))
    if den == 0:
        return 0.0
    b = sum((i - xm) * (closes[i] - ym) for i in range(n)) / den
    return abs(b) * duration / atr


# ─────────────────────────── masina de excursie ───────────────────────────

@dataclass
class Excursion:
    open_bar: int
    direction: int                 # +1 sus, -1 jos
    closes_outside: int = 0
    reentry_bar: int | None = None

    def observe(self, bar: int, outside: bool, cfg: ConfigV43) -> tuple[str, tuple[str, ...]]:
        if outside:
            self.closes_outside += 1
            if self.closes_outside >= cfg.N_accept:
                return "BREAKOUT_ACCEPTED", ()
            return "BOUNDARY_EXCURSION", ("NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT",)
        self.closes_outside = 0                      # ★ reintrarea RESETEAZA contorul
        if bar - self.open_bar <= cfg.K_reentry:
            self.reentry_bar = bar
            return "SWEEP_CONFIRMED", ()
        return "BREAKOUT_PENDING", ("NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT",)


def sweep_reversal_confirmed(ex: Excursion, bar: int, close_price: float,
                            ref_swing: float | None, ref_confirm_ts: int | None,
                            episode_end_ts: int | None) -> tuple[bool, str]:
    """CORECTIA C13 — §4.1 era INCOMPLETA: `LIQUIDITY_SWEEP_REVERSAL` era declarat ca
    reason code, dar fereastra in care trebuie sa apara ruptura opusa NU era definita
    nicaieri, iar `K_struct` e interzis explicit de contract ca numar de swing-uri.

    Inchidere FARA PARAMETRU NOU: dupa `SWEEP_CONFIRMED`, reversalul se confirma cand
    pretul INCHIDE dincolo de ultimul swing confirmat OPUS, format inainte de
    deschiderea excursiei. Fereastra este VIATA EPISODULUI, nu o constanta libera.
    """
    if ex.reentry_bar is None:
        return False, "NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT"
    if ref_swing is None or ref_confirm_ts is None:
        return False, "REVERSAL_REFERENCE_UNAVAILABLE"
    if ref_confirm_ts > ex.open_bar:                 # zero-lookahead, fail-closed
        raise ContractError("FUTURE_TIMESTAMP_REFUSED")
    if bar <= ex.reentry_bar:
        return False, "NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT"
    if episode_end_ts is not None and bar > episode_end_ts:
        return False, "REVERSAL_WINDOW_EXPIRED"
    broken = close_price > ref_swing if ex.direction == -1 else close_price < ref_swing
    return (True, "LIQUIDITY_SWEEP_REVERSAL") if broken else (False, "NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT")


# ─────────────────────────── registru cu identitate ───────────────────────────

class Registry:
    """Emite id-uri monoton crescatoare si REFUZA reutilizarea unui id mort."""

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
            raise ContractError("DEAD_ID_REUSE_REFUSED")


def offer_swing(st: "Structure", price: float, side: str, cfg: ConfigV43) -> tuple[bool, str]:
    """§3.3 facut apelabil. Swingul refuzat NU se pierde: e semnalat ca posibil
    inceput al unui episod ULTERIOR, exact cum cere contractul."""
    if st.atr_ref is None:
        return False, "ATR_UNAVAILABLE"
    cl = st.up if side == "high" else st.dn
    if cl.offer(price, cfg.tol_cluster * st.atr_ref):
        return True, "OK_RANGE_MACRO" if st.depth is Depth.MACRO else "OK_RANGE_INTERNAL"
    return False, "SWING_OUTSIDE_CLUSTER"


def evaluate_candidate(st: "Structure | None", bar: int, cfg: ConfigV43) -> str:
    """CORECTIA C15 — conjunctia de confirmare exista in contract ca PROZA, dar nicaieri
    ca functie unica. VE ar fi trebuit sa o compuna singur, adica exact inventia pe care
    mandatul o interzice. Aici e scrisa o singura data, cu ordine de prioritate FIXA, si
    intoarce EXACT un reason code.

    Ordinea: intai starile de input lipsa (fail-closed), apoi starile KILL, abia apoi
    poarta de durata. Motiv: `TOO_SHORT_*` inseamna „inca nu", iar a raporta „inca nu"
    despre un candidat deja MORT ar fi fals.
    """
    if st is None or st.end_ts is not None:
        return "BETWEEN_EPISODES"
    kill = degeneracy_check(st, cfg)
    if kill is not None:
        return kill                      # ATR_UNAVAILABLE / FEW_SWINGS / INVERTED / DEGENERATE
    d_min = cfg.d_macro if st.depth is Depth.MACRO else cfg.d_internal
    if bar - st.start_ts < d_min:
        return "TOO_SHORT_MACRO" if st.depth is Depth.MACRO else "TOO_SHORT_INTERNAL"
    return "OK_RANGE_MACRO" if st.depth is Depth.MACRO else "OK_RANGE_INTERNAL"


def promotion_check(p1_left_frozen_boundary: bool, p2_breakout_accepted: bool,
                    external_swings_confirmed: int, p4_previous_closed_and_kept: bool,
                    cfg: ConfigV43) -> tuple[bool, str]:
    """§5 facut apelabil. Preconditiile se evalueaza in ORDINEA din contract, iar refuzul
    numeste PRIMA precondit,ie neindeplinita. Denumirea completa
    `PROMOTION_REFUSED_PRECONDITION_Pk` e normativa (C16): tabelul §T12 al contractului
    scria forma scurta `PROMOTION_REFUSED_P1`, care NU exista in setul inchis de coduri.
    """
    if not p1_left_frozen_boundary:
        return False, "PROMOTION_REFUSED_PRECONDITION_P1"
    if not p2_breakout_accepted:
        return False, "PROMOTION_REFUSED_PRECONDITION_P2"
    if external_swings_confirmed < cfg.n_external_swings:
        return False, "PROMOTION_REFUSED_PRECONDITION_P3"
    if not p4_previous_closed_and_kept:
        return False, "PROMOTION_REFUSED_PRECONDITION_P4"
    return True, "IS_TREND_MACRO"


# ─────────────────────────── nivel ───────────────────────────

def assign_level(cand_start: int, cand_end: int, cand_lo: float, cand_hi: float,
                 parent: Structure | None, cfg: ConfigV43) -> tuple[Depth | None, str | None, int | None]:
    """R1 / R2 / R3 din contract §2, aplicate mecanic."""
    if parent is None or parent.end_ts is not None:
        return Depth.MACRO, None, None
    contained_time = cand_start >= parent.start_ts and cand_end <= (parent.end_ts or cand_end)
    pb_lo, pb_hi = parent.boundary_lower, parent.boundary_upper
    contained_price = pb_lo is not None and pb_hi is not None and cand_lo >= pb_lo and cand_hi <= pb_hi
    if contained_time and contained_price:
        # CORECTIA C14 — `DEPTH_LIMIT_EXCEEDED` era DECLARAT dar niciodata EMIS: un candidat
        # continut intr-un parinte INTERNAL primea din nou INTERNAL, adica un al treilea nivel,
        # exact cel eliminat prin decizia CEO. Adancimea maxima e acum IMPUSA, nu doar scrisa.
        if parent.depth is Depth.INTERNAL:
            return None, "DEPTH_LIMIT_EXCEEDED", None
        return Depth.INTERNAL, None, parent.structure_id
    if cand_start < parent.start_ts <= cand_end or (pb_lo is not None and not contained_price and contained_time):
        return None, "PARTIAL_OVERLAP_NO_CONTAINMENT", None
    return None, "LEVEL_ASSIGNMENT_UNRESOLVED", None


def snapshot(st: Structure, cfg: ConfigV43) -> dict[str, Any]:
    return {"contract_version": cfg.contract_version, "config_id": cfg.config_id(),
            "structure_id": st.structure_id, "depth": st.depth.value,
            "parent": st.parent_structure_id, "start_ts": st.start_ts,
            "confirm_ts": st.confirm_ts, "end_ts": st.end_ts,
            "up": list(st.up.members), "dn": list(st.dn.members),
            "frozen": st.up.frozen and st.dn.frozen, "atr_ref": st.atr_ref,
            "role": st.role, "role_known_ts": st.role_known_ts}


def restore(snap: dict[str, Any], cfg: ConfigV43) -> Structure:
    if snap.get("contract_version") != cfg.contract_version or snap.get("config_id") != cfg.config_id():
        raise ContractError("SNAPSHOT_CONTRACT_MISMATCH")
    st = Structure(structure_id=snap["structure_id"], depth=Depth(snap["depth"]),
                   parent_structure_id=snap["parent"], start_ts=snap["start_ts"],
                   confirm_ts=snap["confirm_ts"], end_ts=snap["end_ts"], atr_ref=snap["atr_ref"],
                   role=snap["role"], role_known_ts=snap["role_known_ts"])
    st.up.members = list(snap["up"]); st.dn.members = list(snap["dn"])
    st.up.frozen = st.dn.frozen = snap["frozen"]
    return st


def guard_timestamp(ts: int, as_of: int) -> None:
    if ts > as_of:
        raise ContractError("FUTURE_TIMESTAMP_REFUSED")
