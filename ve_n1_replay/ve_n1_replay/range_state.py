"""RANGE_STATE + evenimente longitudinale de range/breakout — producător ADITIV versionat (0.2.0).

Implementează STAT-RANGE-RECONCILED-SPEC-v1.0 (@aca7801, manifest v2.7.75 @5063448), pe baza raportului de
reachability RT-RANGE-0001 (@5e56396). RANGE_STATE e un STRAT NOU, SEPARAT:

- NU reutilizează și NU reinterpretează `StructBand.RANGE` (care înseamnă INSTABILITATE/flip proaspăt, dovadă RT);
- NU trece prin `applicable_regimes` (care nu poate produce RANGE — `structure=="range"` e static imposibil);
- NU atinge ve_brain / N3 / N4 / EV / N6 / motorul N1 (rezultatele N1 rămân BYTE-IDENTICE cu 0.1.1);
- consumă DOAR informație ≤ momentul evaluării: swing-uri CONFIRMATE (fractali simetrici 2k+1), ATR cauzal,
  seria close/high/low a barelor ÎNCHISE. Zero lookahead.

Reutilizare (nu invenție): detecția de fractali (strict D2, identică cu `detect_swings`), `atr14`, semnătura
wick-sweep D6 (`liquidity_mechanics`, ratificat v2.7.39). ER = |Δclose_net| / Σ|Δclose| — aritmetică pură.
"""
from __future__ import annotations

import dataclasses as _dc
import hashlib
from collections import deque
from enum import Enum
from typing import Any

from .version import (
    RANGE_STATE_SCHEMA_VERSION, RANGE_PRODUCER_VERSION, RANGE_EVENT_CONTRACT_VERSION,
    RANGE_STATE_CONTRACT_VERSION, BARS_PER_DAY_M15,
)

_K: int = 2  # fractal k (K_DEFAULT în market_structure — swing la i confirmat la i+k)


# ═══════════════════════════════════ enums / vocabular ═══════════════════════════════════
class BoundaryValidity(Enum):
    PROVISIONAL = "PROVISIONAL"   # < n_touch atingeri
    CONFIRMED = "CONFIRMED"       # >= n_touch pe AMBELE limite
    EXTENDED = "EXTENDED"         # un swing nou depășește limita fără acceptare ⇒ limita se MUTĂ
    VIOLATED = "VIOLATED"         # acceptare confirmată dincolo ⇒ invalidare


class DataReadiness(Enum):
    WARMUP = "WARMUP"
    READY = "READY"
    DEGRADED = "DEGRADED"


class ConsolidationState(Enum):
    NONE = "NONE"
    FORMING = "FORMING"           # boundary_validity = PROVISIONAL
    ESTABLISHED = "ESTABLISHED"   # CONFIRMED și ER <= ER_max și bars_in_state >= d_min
    DECAYING = "DECAYING"         # ER crește peste ER_max fără violare — semnal, NU invalidare


class RangeEventKind(Enum):
    RANGE_LOW_REJECTION = "RANGE_LOW_REJECTION"
    RANGE_HIGH_REJECTION = "RANGE_HIGH_REJECTION"
    RANGE_MID = "RANGE_MID"
    BREAKOUT_CANDIDATE = "BREAKOUT_CANDIDATE"
    BREAKOUT_ACCEPTED = "BREAKOUT_ACCEPTED"
    BREAKOUT_RETEST = "BREAKOUT_RETEST"
    FAILED_BREAKOUT = "FAILED_BREAKOUT"
    LIQUIDITY_SWEEP_REVERSAL = "LIQUIDITY_SWEEP_REVERSAL"


class MachineState(Enum):
    IDLE = "IDLE"                 # niciun range activ
    FORMING = "FORMING"           # box provizoriu, neconfirmat
    ESTABLISHED = "ESTABLISHED"   # range confirmat, acționabil
    CANDIDATE = "CANDIDATE"       # breakout candidate în curs
    ACCEPTED = "ACCEPTED"         # breakout acceptat; range VIOLAT; se urmărește retest


# reason codes (Partea B)
OK_RANGE = "OK_RANGE"
FEW_TOUCHES = "FEW_TOUCHES"
ER_TOO_HIGH = "ER_TOO_HIGH"
TOO_SHORT = "TOO_SHORT"
WIDTH_OUT_OF_GRID = "WIDTH_OUT_OF_GRID"
WARMUP = "WARMUP"
INPUT_UNAVAILABLE = "INPUT_UNAVAILABLE"
BOUNDARY_EXTENDED = "BOUNDARY_EXTENDED"
ACCEPTED_BREAK = "ACCEPTED_BREAK"
MAX_DURATION = "MAX_DURATION"
NO_STRUCTURE = "NO_STRUCTURE"     # lipsă structură (fără pereche de limite) — Unavailable, niciodată „range presupus"

# ── F7 SAFETY_GUARD (STAT-M-INFERENCE-FINAL @d0d08c1, manifest v2.7.77): RANGE_MID_NO_ENTRY ──
# NU e strategie și NU e ipoteză (nu produce p-value / MDE / prag). E o INTERDICȚIE executabilă: în RANGE_MID
# intrarea e REFUZATĂ PRIN CONSTRUCȚIE. Rămâne STARE EXPLICITĂ, contorizată separat (`n_guards`), auditabilă —
# NICIODATĂ dedusă din absența tranzacțiilor.
SAFETY_GUARD_RANGE_MID_NO_ENTRY = "RANGE_MID_NO_ENTRY"
SAFETY_GUARDS_REGISTER: tuple[str, ...] = (SAFETY_GUARD_RANGE_MID_NO_ENTRY,)


@_dc.dataclass(frozen=True, slots=True)
class EntryDecision:
    """Refuz executabil. `permitted=False` cu `guard` setat ⇒ intrare INTERZISĂ prin construcție (F7)."""
    permitted: bool
    guard: str | None
    reason: str


def entry_decision(event: "RangeEvent | None") -> EntryDecision:
    """SAFETY_GUARD F7, executabil: orice strategie care cere o intrare în RANGE_MID primește REFUZ. Zero entry,
    zero candidate, zero p-value, zero broker — prin construcție. Orice alt eveniment ⇒ neguvernat de acest guard."""
    if event is not None and event.kind == RangeEventKind.RANGE_MID.value:
        return EntryDecision(permitted=False, guard=SAFETY_GUARD_RANGE_MID_NO_ENTRY, reason="RANGE_MID_NO_ENTRY")
    return EntryDecision(permitted=True, guard=None, reason="")


def _sha(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


# ═══════════════════════════════════ configurație + identitate ═══════════════════════════════════
@_dc.dataclass(frozen=True, slots=True)
class RangeConfig:
    """Definiția RANGE, pre-înregistrată. Primara (Partea F): n_touch=2, tol=0.25×ATR, ER_max=0.40,
    d_min=1 zi (96 bare M15), N_acceptance=2, precedence=RANGE_STATE_OVER_TREND_PAUSE, width_filter=off.
    Variantele grilei sunt SENSITIVITY-ONLY (nu produc p-value, nu consumă slot)."""
    n_touch: int = 2
    tol_atr: float = 0.25
    er_max: float = 0.40
    d_min_bars: int = BARS_PER_DAY_M15               # o ZI a timeframe-ului (M15: 96, ratificat split_manifest)
    width_filter: tuple[float, float] | None = None  # (min,max) în unități ATR; None ⇒ width doar RAPORTAT
    n_acceptance: int = 2
    precedence_rule: str = "RANGE_STATE_OVER_TREND_PAUSE"
    timeframe: str = "15m"
    swing_k: int = _K
    atr_window: int = 14
    # parametri OPERAȚIONALI (în afara range_spec_id; intră în config_hash ⇒ run_hash)
    range_window: int = 512          # fereastra mărginită pt. detecție/memorie (>= max episode)
    max_duration_bars: int | None = None  # None ⇒ fără invalidare MAX_DURATION; setabil pt. teste/grilă
    retest_window_bars: int = 12     # fereastra pt. BREAKOUT_RETEST după ACCEPTED
    candidate_expiry_bars: int | None = None  # None ⇒ n_acceptance+1 (regula spec)

    def range_spec_id(self) -> str:
        """sha256 peste dicționarul ORDONAT al DEFINIȚIEI (Partea B/F). Un rezultat FĂRĂ range_spec_id e
        NON-COMPARABIL PRIN TIP cu orice alt rezultat de range."""
        wf = "off" if self.width_filter is None else f"{self.width_filter[0]}:{self.width_filter[1]}"
        return _sha(
            f"n_touch={self.n_touch}", f"tol_atr={self.tol_atr}", f"er_max={self.er_max}",
            f"d_min_bars={self.d_min_bars}", f"width_filter={wf}", f"N_acceptance={self.n_acceptance}",
            f"precedence_rule={self.precedence_rule}", f"timeframe={self.timeframe}",
            f"swing_k={self.swing_k}", f"atr_window={self.atr_window}",
            f"range_state_schema_version={RANGE_STATE_SCHEMA_VERSION}",
            f"producer_version={RANGE_PRODUCER_VERSION}",
        )

    def config_hash(self) -> str:
        """sha256 peste TOATE câmpurile (incl. operaționale) — acoperă parametrii din afara range_spec_id."""
        return _sha(
            self.range_spec_id(), f"range_window={self.range_window}",
            f"max_duration_bars={self.max_duration_bars}", f"retest_window_bars={self.retest_window_bars}",
            f"candidate_expiry_bars={self.candidate_expiry_bars}",
        )

    def run_hash(self, data_identity: str) -> str:
        """sha256(config_hash ‖ sha256(data_identity) ‖ range_spec_id) — identitatea completă de rulare."""
        return _sha(self.config_hash(), _sha(data_identity), self.range_spec_id())

    def _cand_expiry(self) -> int:
        return self.candidate_expiry_bars if self.candidate_expiry_bars is not None else self.n_acceptance + 1


# ═══════════════════════════════════ rezultat + eveniment (contract Ok/Unavailable) ═══════════════════════════════════
@_dc.dataclass(frozen=True, slots=True)
class RangeStateResult:
    """Contract Ok/Unavailable. `available=False` ⇒ doar `reason` (WARMUP/INPUT_UNAVAILABLE/NO_STRUCTURE)."""
    available: bool
    reason: str
    range_spec_id: str
    bar_index: int
    ts_close: int
    # câmpuri Ok (None când available=False)
    upper: float | None = None
    lower: float | None = None
    range_mid: float | None = None
    boundary_validity: str | None = None
    data_readiness: str | None = None
    consolidation_state: str | None = None
    structural_start_ts: int | None = None
    actionable_start_ts: int | None = None       # = confirm_ts (>= structural_start_ts + k bare)
    touches_upper: int | None = None
    touches_lower: int | None = None
    bars_in_state: int | None = None
    path_sum: float | None = None
    net_disp: float | None = None
    efficiency_ratio: float | None = None
    width_atr: float | None = None
    trend_context: str | None = None             # atributul de precedență (TREND_PAUSE păstrat, nu pierdut)
    invalidation: str | None = None              # None cât e activ; ACCEPTED_BREAK/MAX_DURATION/INPUT_UNAVAILABLE
    reason_codes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return _dc.asdict(self)


@_dc.dataclass(frozen=True, slots=True)
class RangeEvent:
    """Eveniment longitudinal. `confirm_ts` folosește EXCLUSIV bare <= confirm_ts (zero lookahead).
    `not_yet_available` declară explicit informația care NU e disponibilă la confirmare."""
    kind: str
    confirm_ts: int
    bar_index: int
    boundary: str | None                         # 'upper' / 'lower' / None
    reason_codes: tuple[str, ...]
    not_yet_available: tuple[str, ...]
    event_contract_version: str
    range_spec_id: str
    safety_guard: str | None = None              # F7: RANGE_MID_NO_ENTRY marcat EXPLICIT (auditabil, nu dedus)

    def as_dict(self) -> dict[str, Any]:
        return _dc.asdict(self)


class RangeContractError(Exception):
    """Tranziție interzisă de mașina de stări — fail-closed."""


# ═══════════════════════════════════ swing confirmat (stare internă) ═══════════════════════════════════
class _CSwing:
    __slots__ = ("idx", "confirm_idx", "price", "is_high", "ts")

    def __init__(self, idx: int, confirm_idx: int, price: float, is_high: bool, ts: int) -> None:
        self.idx = idx; self.confirm_idx = confirm_idx; self.price = price; self.is_high = is_high; self.ts = ts


# ═══════════════════════════════════ producătorul incremental ═══════════════════════════════════
class RangeStateProducer:
    """Producător INCREMENTAL (stare, NU recalcul pe fereastră) al RANGE_STATE + evenimente. `observe` primește
    o bară închisă + ATR cauzal și întoarce `(RangeStateResult, list[RangeEvent])`. Serializabil integral."""

    def __init__(self, config: RangeConfig) -> None:
        self._cfg = config
        self._spec_id = config.range_spec_id()
        self._n = 0
        self._last_atr: float = 0.0
        # fereastra de fractali (2k+1) pentru stream-ul de swing-uri CONFIRMATE (strict D2, identic detect_swings)
        self._wh: deque[float] = deque(maxlen=2 * config.swing_k + 1)
        self._wl: deque[float] = deque(maxlen=2 * config.swing_k + 1)
        self._wts: deque[int] = deque(maxlen=2 * config.swing_k + 1)
        # swing-uri confirmate active (mărginite la range_window bare)
        self._highs: deque[_CSwing] = deque()
        self._lows: deque[_CSwing] = deque()
        # starea episodului de range (incrementală)
        self._machine = MachineState.IDLE
        self._upper: float | None = None
        self._lower: float | None = None
        self._structural_start_idx: int | None = None
        self._structural_start_ts: int | None = None
        self._confirm_ts: int | None = None            # actionable_start_ts
        self._first_close: float | None = None
        self._path_sum: float = 0.0
        self._prev_close: float | None = None
        self._boundary_validity: BoundaryValidity | None = None
        self._was_confirmed: bool = False
        self._invalidation: str | None = None
        # stare breakout
        self._cand_boundary: str | None = None
        self._cand_dir: int = 0
        self._cand_consec: int = 0
        self._cand_bar: int | None = None
        self._accepted_boundary_price: float | None = None
        self._accepted_dir: int = 0
        self._accepted_bar: int | None = None

    # ── detecția incrementală a swing-urilor confirmate (strict D2, byte-echivalent detect_swings) ──
    def _detect_confirmed_swing(self, i: int) -> _CSwing | None:
        k = self._cfg.swing_k
        if len(self._wh) < 2 * k + 1:
            return None
        c = k
        ch = self._wh[c]; cl = self._wl[c]
        cts_idx = i - k
        cts = self._wts[c]                         # ts_close al barei formării extremului (retrospectiv)
        if all(ch > self._wh[j] for j in range(2 * k + 1) if j != c):
            return _CSwing(idx=cts_idx, confirm_idx=i, price=ch, is_high=True, ts=cts)
        if all(cl < self._wl[j] for j in range(2 * k + 1) if j != c):
            return _CSwing(idx=cts_idx, confirm_idx=i, price=cl, is_high=False, ts=cts)
        return None

    def _prune(self, i: int) -> None:
        lo = i - self._cfg.range_window + 1
        while self._highs and self._highs[0].idx < lo:
            self._highs.popleft()
        while self._lows and self._lows[0].idx < lo:
            self._lows.popleft()

    def _reset_episode(self) -> None:
        self._machine = MachineState.IDLE
        self._upper = self._lower = None
        self._structural_start_idx = self._structural_start_ts = self._confirm_ts = None
        self._first_close = None
        self._path_sum = 0.0
        self._boundary_validity = None
        self._was_confirmed = False
        self._cand_boundary = None; self._cand_dir = 0; self._cand_consec = 0; self._cand_bar = None

    def _touch_counts(self) -> tuple[int, int]:
        cfg = self._cfg
        assert self._upper is not None and self._lower is not None
        # toleranța e în unități ATR; folosim ultimul ATR primit (stocat pe bară)
        tol = cfg.tol_atr * self._last_atr
        tu = sum(1 for s in self._highs if s.price >= self._upper - tol)
        tl = sum(1 for s in self._lows if s.price <= self._lower + tol)
        return tu, tl

    def observe(self, *, bar_index: int, ts_close: int, open_: float, high: float, low: float,
                close: float, atr: float | None, trend_context: str | None) -> tuple[RangeStateResult, list[RangeEvent]]:
        cfg = self._cfg
        i = self._n
        self._n += 1
        self._wh.append(high); self._wl.append(low); self._wts.append(ts_close)
        self._last_atr = atr if atr is not None else 0.0

        def unavailable(reason: str, readiness: DataReadiness) -> tuple[RangeStateResult, list[RangeEvent]]:
            return (RangeStateResult(available=False, reason=reason, range_spec_id=self._spec_id,
                                     bar_index=i, ts_close=ts_close, data_readiness=readiness.value,
                                     reason_codes=(reason,)), [])

        # WARMUP / INPUT indisponibil — NICIODATĂ interpretate drept RANGE_STATE (fail-closed)
        if atr is None:
            if i < cfg.atr_window or i < 2 * cfg.swing_k + 1:
                return unavailable(WARMUP, DataReadiness.WARMUP)
            # ATR ar fi trebuit disponibil ⇒ intrare lipsă ⇒ invalidează un episod activ, propagă motivul
            if self._machine in (MachineState.FORMING, MachineState.ESTABLISHED, MachineState.CANDIDATE):
                self._invalidation = INPUT_UNAVAILABLE
                self._reset_episode()
            return unavailable(INPUT_UNAVAILABLE, DataReadiness.DEGRADED)

        # actualizează seria de close (path_sum) DOAR cât un episod e activ
        # (1) înregistrează swing-ul confirmat la bara i (confirmed_idx = i)
        sw = self._detect_confirmed_swing(i)
        if sw is not None:
            (self._highs if sw.is_high else self._lows).append(sw)
        self._prune(i)

        events: list[RangeEvent] = []

        # (2) actualizează/începe episodul din swing-urile active
        if self._machine == MachineState.IDLE:
            if self._highs and self._lows:
                self._start_episode(i, close)
        if self._machine != MachineState.IDLE:
            self._extend_boundaries(i, events)
            # ER / path_sum incremental
            if self._prev_close is not None and self._first_close is not None:
                self._path_sum += abs(close - self._prev_close)
            # MAX_DURATION
            if (cfg.max_duration_bars is not None and self._structural_start_idx is not None
                    and (i - self._structural_start_idx + 1) > cfg.max_duration_bars):
                self._invalidation = MAX_DURATION
                self._reset_episode()

        self._prev_close = close

        if self._machine == MachineState.IDLE:
            # fără pereche de limite / episod tocmai încheiat ⇒ Unavailable (surfacează invalidarea o dată)
            return self._build_result(i, ts_close, close, atr, trend_context), events

        # (3) clasificare + mașina de evenimente
        self._run_machine(i, ts_close, high, low, close, atr, events)

        # (4) asamblează rezultatul
        result = self._build_result(i, ts_close, close, atr, trend_context)
        return result, events

    def _start_episode(self, i: int, close: float) -> None:
        assert self._highs and self._lows
        self._upper = max(s.price for s in self._highs)
        self._lower = min(s.price for s in self._lows)
        # structural_start = cel mai vechi swing activ; ts-ul lui e ts_close al barei formării (retrospectiv)
        oldest = min([*self._highs, *self._lows], key=lambda s: s.idx)
        self._structural_start_idx = oldest.idx
        self._structural_start_ts = oldest.ts
        self._machine = MachineState.FORMING
        self._boundary_validity = BoundaryValidity.PROVISIONAL
        self._first_close = close
        self._prev_close = close       # baseline al episodului ⇒ path_sum acumulează DOAR în interiorul episodului
        self._path_sum = 0.0
        self._was_confirmed = False
        self._invalidation = None

    def _extend_boundaries(self, i: int, events: list[RangeEvent]) -> None:
        assert self._upper is not None and self._lower is not None
        moved = False
        if self._highs:
            hi = max(s.price for s in self._highs)
            if hi > self._upper:
                self._upper = hi; moved = True
        if self._lows:
            lo = min(s.price for s in self._lows)
            if lo < self._lower:
                self._lower = lo; moved = True
        tu, tl = self._touch_counts()
        confirmed = tu >= self._cfg.n_touch and tl >= self._cfg.n_touch
        if moved and self._machine in (MachineState.ESTABLISHED, MachineState.CANDIDATE):
            self._boundary_validity = BoundaryValidity.EXTENDED
        elif confirmed:
            self._boundary_validity = BoundaryValidity.CONFIRMED
        else:
            self._boundary_validity = BoundaryValidity.PROVISIONAL
        # tranziția FORMING → ESTABLISHED la prima confirmare (înregistrează confirm_ts = actionable_start)
        if confirmed and not self._was_confirmed:
            self._was_confirmed = True
            self._confirm_ts = self._wts[-1]
            if self._machine == MachineState.FORMING:
                self._machine = MachineState.ESTABLISHED

    def _consol_state(self, er: float, bars_in_state: int) -> ConsolidationState:
        cfg = self._cfg
        if self._boundary_validity == BoundaryValidity.PROVISIONAL:
            return ConsolidationState.FORMING
        if self._was_confirmed and er <= cfg.er_max and bars_in_state >= cfg.d_min_bars:
            return ConsolidationState.ESTABLISHED
        if self._was_confirmed and er > cfg.er_max:
            return ConsolidationState.DECAYING
        return ConsolidationState.FORMING

    def _mk_event(self, kind: RangeEventKind, ts: int, i: int, boundary: str | None,
                  reasons: tuple[str, ...], nya: tuple[str, ...]) -> RangeEvent:
        guard = SAFETY_GUARD_RANGE_MID_NO_ENTRY if kind is RangeEventKind.RANGE_MID else None
        return RangeEvent(kind=kind.value, confirm_ts=ts, bar_index=i, boundary=boundary,
                          reason_codes=reasons, not_yet_available=nya,
                          event_contract_version=RANGE_EVENT_CONTRACT_VERSION, range_spec_id=self._spec_id,
                          safety_guard=guard)

    def _run_machine(self, i: int, ts: int, high: float, low: float, close: float, atr: float,
                     events: list[RangeEvent]) -> None:
        cfg = self._cfg
        assert self._upper is not None and self._lower is not None
        tol = cfg.tol_atr * atr
        upper, lower = self._upper, self._lower

        if self._machine == MachineState.CANDIDATE:
            self._machine_candidate(i, ts, close, events)
            return
        if self._machine == MachineState.ACCEPTED:
            self._machine_accepted(i, ts, high, low, close, tol, events)
            return
        if self._machine != MachineState.ESTABLISHED:
            return  # FORMING: fără evenimente până la ESTABLISHED

        # ESTABLISHED — evenimente în ordine de prioritate, mutually exclusive prin poziția lui close
        if close > upper:                      # close dincolo de limita CONFIRMED ⇒ CANDIDATE (sus)
            self._open_candidate('upper', +1, i, ts, close, events)
            return
        if close < lower:                      # (jos)
            self._open_candidate('lower', -1, i, ts, close, events)
            return
        # sweep-reversal D6 (wick dincolo + close înăuntru, ACEEAȘI bară)
        if high > upper and close < upper:
            events.append(self._mk_event(RangeEventKind.LIQUIDITY_SWEEP_REVERSAL, ts, i, 'upper',
                                         (OK_RANGE,), ()))
            return
        if low < lower and close > lower:
            events.append(self._mk_event(RangeEventKind.LIQUIDITY_SWEEP_REVERSAL, ts, i, 'lower',
                                         (OK_RANGE,), ()))
            return
        # respingeri (close în banda tol lângă o limită, dar înăuntru)
        if lower <= close <= lower + tol:
            events.append(self._mk_event(RangeEventKind.RANGE_LOW_REJECTION, ts, i, 'lower', (OK_RANGE,), ()))
            return
        if upper - tol <= close <= upper:
            events.append(self._mk_event(RangeEventKind.RANGE_HIGH_REJECTION, ts, i, 'upper', (OK_RANGE,), ()))
            return
        # mijloc (fără entry) — STARE emisă, nu absență
        if lower + tol < close < upper - tol:
            events.append(self._mk_event(RangeEventKind.RANGE_MID, ts, i, None, (OK_RANGE,), ()))

    def _open_candidate(self, boundary: str, direction: int, i: int, ts: int, close: float,
                        events: list[RangeEvent]) -> None:
        self._machine = MachineState.CANDIDATE
        self._cand_boundary = boundary; self._cand_dir = direction
        self._cand_consec = 1; self._cand_bar = i
        # la CANDIDATE nu se știe încă dacă va fi ACCEPTED sau FAILED — se declară explicit
        events.append(self._mk_event(RangeEventKind.BREAKOUT_CANDIDATE, ts, i, boundary, (OK_RANGE,),
                                     ("will_be_accepted_or_failed",)))

    def _beyond(self, close: float) -> bool:
        assert self._upper is not None and self._lower is not None
        if self._cand_dir > 0:
            return close > self._upper
        return close < self._lower

    def _machine_candidate(self, i: int, ts: int, close: float, events: list[RangeEvent]) -> None:
        cfg = self._cfg
        if self._beyond(close):
            self._cand_consec += 1
            if self._cand_consec >= cfg.n_acceptance:
                # BREAKOUT_ACCEPTED — mutual exclusiv cu FAILED prin construcția mașinii
                self._machine = MachineState.ACCEPTED
                self._boundary_validity = BoundaryValidity.VIOLATED
                self._invalidation = ACCEPTED_BREAK
                self._accepted_boundary_price = self._upper if self._cand_dir > 0 else self._lower
                self._accepted_dir = self._cand_dir
                self._accepted_bar = i
                events.append(self._mk_event(RangeEventKind.BREAKOUT_ACCEPTED, ts, i, self._cand_boundary,
                                             (ACCEPTED_BREAK,), ("will_retest_or_not",)))
            return
        # close înapoi ÎNĂUNTRU înainte de N ⇒ FAILED_BREAKOUT (range-ul SUPRAVIEȚUIEȘTE)
        b = self._cand_boundary
        self._machine = MachineState.ESTABLISHED
        self._cand_boundary = None; self._cand_dir = 0; self._cand_consec = 0; self._cand_bar = None
        events.append(self._mk_event(RangeEventKind.FAILED_BREAKOUT, ts, i, b, (OK_RANGE,), ()))

    def _machine_accepted(self, i: int, ts: int, high: float, low: float, close: float, tol: float,
                          events: list[RangeEvent]) -> None:
        cfg = self._cfg
        assert self._accepted_boundary_price is not None
        b = self._accepted_boundary_price
        boundary = 'upper' if self._accepted_dir > 0 else 'lower'
        # retest: revenire în banda tol a limitei străpunse, FĂRĂ re-închidere înăuntru
        if self._accepted_dir > 0:
            hit = low <= b + tol and close >= b        # coboară la limită din exterior, nu închide sub ea
        else:
            hit = high >= b - tol and close <= b
        if hit:
            events.append(self._mk_event(RangeEventKind.BREAKOUT_RETEST, ts, i, boundary, (OK_RANGE,), ()))
            self._end_after_accept()
            return
        # expiră retest-ul
        if self._accepted_bar is not None and (i - self._accepted_bar) >= cfg.retest_window_bars:
            self._end_after_accept()

    def _end_after_accept(self) -> None:
        self._accepted_boundary_price = None; self._accepted_dir = 0; self._accepted_bar = None
        self._reset_episode()   # episodul e mort; un range nou se poate forma ulterior
        self._invalidation = None   # ACCEPTED_BREAK a fost deja surfacat în starea ACCEPTED

    def _build_result(self, i: int, ts: int, close: float, atr: float,
                      trend_context: str | None) -> RangeStateResult:
        cfg = self._cfg
        # range VIOLAT (breakout acceptat) — invalidat, dar mașina urmărește încă retest-ul; raportăm invalidarea
        if self._machine == MachineState.ACCEPTED:
            return RangeStateResult(available=False, reason=ACCEPTED_BREAK, range_spec_id=self._spec_id,
                                    bar_index=i, ts_close=ts, data_readiness=DataReadiness.READY.value,
                                    boundary_validity=BoundaryValidity.VIOLATED.value,
                                    invalidation=ACCEPTED_BREAK, reason_codes=(ACCEPTED_BREAK,))
        # episod încheiat (MAX_DURATION / INPUT_UNAVAILABLE / după retest) — surfacează invalidarea O SINGURĂ dată
        if self._machine == MachineState.IDLE:
            inv = self._invalidation
            self._invalidation = None
            return RangeStateResult(available=False, reason=(inv or NO_STRUCTURE), range_spec_id=self._spec_id,
                                    bar_index=i, ts_close=ts, data_readiness=DataReadiness.READY.value,
                                    invalidation=inv, reason_codes=((inv,) if inv else (NO_STRUCTURE,)))
        assert self._upper is not None and self._lower is not None
        net_disp = close - (self._first_close if self._first_close is not None else close)
        er = abs(net_disp) / self._path_sum if self._path_sum > 0 else 0.0
        bars_in_state = (i - self._structural_start_idx + 1) if self._structural_start_idx is not None else 1
        width_atr = (self._upper - self._lower) / atr if atr > 0 else 0.0
        tu, tl = self._touch_counts()
        consol = self._consol_state(er, bars_in_state)

        reasons: list[str] = []
        if self._boundary_validity == BoundaryValidity.EXTENDED:
            reasons.append(BOUNDARY_EXTENDED)
        if tu < cfg.n_touch or tl < cfg.n_touch:
            reasons.append(FEW_TOUCHES)
        if er > cfg.er_max:
            reasons.append(ER_TOO_HIGH)
        if bars_in_state < cfg.d_min_bars:
            reasons.append(TOO_SHORT)
        width_out = cfg.width_filter is not None and not (cfg.width_filter[0] <= width_atr <= cfg.width_filter[1])
        if width_out:
            reasons.append(WIDTH_OUT_OF_GRID)
        if not reasons and consol == ConsolidationState.ESTABLISHED:
            reasons.append(OK_RANGE)

        # actionable numai de la confirm_ts; înainte de confirmare actionable_start_ts = None
        actionable = self._confirm_ts
        return RangeStateResult(
            available=True, reason=OK_RANGE if consol == ConsolidationState.ESTABLISHED else "forming",
            range_spec_id=self._spec_id, bar_index=i, ts_close=ts,
            upper=self._upper, lower=self._lower, range_mid=(self._upper + self._lower) / 2.0,
            boundary_validity=(self._boundary_validity.value if self._boundary_validity else None),
            data_readiness=DataReadiness.READY.value, consolidation_state=consol.value,
            structural_start_ts=self._structural_start_ts, actionable_start_ts=actionable,
            touches_upper=tu, touches_lower=tl, bars_in_state=bars_in_state,
            path_sum=self._path_sum, net_disp=net_disp, efficiency_ratio=er, width_atr=width_atr,
            trend_context=trend_context, invalidation=None, reason_codes=tuple(reasons),
        )

    # ── snapshot / restore integral (bit-identic) ──
    def snapshot_state(self) -> dict[str, Any]:
        return {
            "n": self._n, "wh": list(self._wh), "wl": list(self._wl), "wts": list(self._wts),
            "highs": [[s.idx, s.confirm_idx, s.price, s.is_high, s.ts] for s in self._highs],
            "lows": [[s.idx, s.confirm_idx, s.price, s.is_high, s.ts] for s in self._lows],
            "machine": self._machine.value, "upper": self._upper, "lower": self._lower,
            "structural_start_idx": self._structural_start_idx, "structural_start_ts": self._structural_start_ts,
            "confirm_ts": self._confirm_ts, "first_close": self._first_close, "path_sum": self._path_sum,
            "prev_close": self._prev_close,
            "boundary_validity": (self._boundary_validity.value if self._boundary_validity else None),
            "was_confirmed": self._was_confirmed, "invalidation": self._invalidation,
            "cand_boundary": self._cand_boundary, "cand_dir": self._cand_dir,
            "cand_consec": self._cand_consec, "cand_bar": self._cand_bar,
            "accepted_boundary_price": self._accepted_boundary_price, "accepted_dir": self._accepted_dir,
            "accepted_bar": self._accepted_bar,
            "last_atr": getattr(self, "_last_atr", 0.0),
        }

    def restore_state(self, st: dict[str, Any]) -> None:
        k = self._cfg.swing_k
        self._n = st["n"]
        self._wh = deque(st["wh"], maxlen=2 * k + 1); self._wl = deque(st["wl"], maxlen=2 * k + 1)
        self._wts = deque(st["wts"], maxlen=2 * k + 1)
        self._highs = deque(_CSwing(a, b, c, d, e) for a, b, c, d, e in st["highs"])
        self._lows = deque(_CSwing(a, b, c, d, e) for a, b, c, d, e in st["lows"])
        self._machine = MachineState(st["machine"]); self._upper = st["upper"]; self._lower = st["lower"]
        self._structural_start_idx = st["structural_start_idx"]; self._structural_start_ts = st["structural_start_ts"]
        self._confirm_ts = st["confirm_ts"]; self._first_close = st["first_close"]; self._path_sum = st["path_sum"]
        self._prev_close = st["prev_close"]
        self._boundary_validity = BoundaryValidity(st["boundary_validity"]) if st["boundary_validity"] else None
        self._was_confirmed = st["was_confirmed"]; self._invalidation = st["invalidation"]
        self._cand_boundary = st["cand_boundary"]; self._cand_dir = st["cand_dir"]
        self._cand_consec = st["cand_consec"]; self._cand_bar = st["cand_bar"]
        self._accepted_boundary_price = st["accepted_boundary_price"]; self._accepted_dir = st["accepted_dir"]
        self._accepted_bar = st["accepted_bar"]
        self._last_atr = st["last_atr"]
