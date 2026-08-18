"""RANGE_STATE SEMANTIC SPEC V2 — remediu `SEMANTIC_SPEC_DEFECT` (0.3.0). NU un patch peste 0.2.0.

Sursă normativă: Statistician STAT-RANGE-SEMANTIC-DIAGNOSIS-V2-v1.0 @`3aac2cc` (manifest v2.7.78 @`18aa2a1`).
`ve_n1_replay/range_state.py` (0.2.0) rămâne NEMODIFICAT, păstrat pentru audit — acest fișier e un producător NOU.

**Cauza defectului 0.2.0 (dovedită structural, nu doar măsurată):**
    limita 0.2.0 = extremul unei mulțimi CRESCĂTOARE de swing-uri confirmate ⇒ nedescrescătoare în lungimea
    ferestrei. A atinge durata minimă cerea fereastra să crească; creșterea ridica limita; ridicarea limitei
    invalida RETROACTIV atingerile numărate contra limitei VECHI. Cu cât fereastra era mai lungă, cu atât
    detectorul își distrugea singur dovezile — o definiție NESATISFIABILĂ, nu o eroare de implementare.

**Schimbarea centrală V2 (repară exact cei doi factori măsurați, fără criterii noi):**
    anchor = MEDIANA extremelor swing-urilor confirmate de pe acea latură, în fereastra activă (mărginită) —
             mediana NU e monotonă în lungimea ferestrei ⇒ nu se auto-invalidează; un singur spike nu o mută.
    boundary_zone = [anchor − w, anchor + w] — o ZONĂ, nu o linie.
    touch = orice bară al cărei interval [low, high] intersectează `boundary_zone` la momentul acelei bare —
            evaluat CAUZAL contra zonei-așa-cum-era-ATUNCI și ACUMULAT ca un contor monoton. Nu se re-scanează
            NICIODATĂ istoricul contra unei zone noi ⇒ o atingere confirmată cauzal nu dispare retroactiv.

BOS/CHoCH intern NU invalidează episodul (se numără ca descriptor, `structure_events_inside`, prin reutilizarea
directă a `IncrementalRawAxesBuilder` ratificat — fără reimplementare a detectorilor de break). Separarea
range/canal foloseşte panta regresiei (OLS incrementală O(1)/bară) — controalele negative (canal ascendent/
descendent) primesc `structure_class = CHANNEL_UP/CHANNEL_DOWN`, NICIODATĂ `RANGE_STATE`.

`w` (lățime de zonă) și `s_max` (prag de pantă) sunt declarate „PRE-ÎNREGISTRATĂ" în document, dar FĂRĂ valoare
numerică literală (verificat: absentă din text și din manifest). Nu le optimizez pe rezultate — expuse ca
parametri de `RangeConfigV2`, cu valori implicite PROPUSE DE VE PE TEMEI STRUCTURAL, NERATIFICATE de Statistician
(vezi RANGE_STATE_V2_CONTRACT.md). Zero acces la date reale de piață în acest fișier sau în testele lui.
"""
from __future__ import annotations

import dataclasses as _dc
import hashlib
from collections import deque
from enum import Enum
from typing import Any

from .range_state import DataReadiness   # neschimbat față de V1 — reutilizare, nu invenție
from .incremental import IncrementalRawAxesBuilder   # reutilizat DOAR pt. contorul descriptiv structure_events_inside
from .version import (
    RANGE_STATE_SCHEMA_VERSION_V2, RANGE_PRODUCER_VERSION_V2, RANGE_EVENT_CONTRACT_VERSION_V2,
    RANGE_STATE_MACHINE_VERSION_V2, BARS_PER_DAY_M15, BARS_PER_INTRADAY_SESSION_M15,
)

_K: int = 2  # fractal k (identic cu V1/N1 — K_DEFAULT din market_structure)


# ═══════════════════════════════════ enums / vocabular V2 ═══════════════════════════════════
class BoundaryValidityV2(Enum):
    PROVISIONAL = "PROVISIONAL"   # < n_touch pe cel puțin o latură
    CONFIRMED = "CONFIRMED"       # >= n_touch pe AMBELE, acumulat cauzal (NICIODATĂ retrogradat de o mediană nouă)
    VIOLATED = "VIOLATED"         # acceptare confirmată dincolo de zonă


class ConsolidationStateV2(Enum):
    NONE = "NONE"
    FORMING = "FORMING"           # boundary PROVISIONAL sau structure_class încă UNCLASSIFIED
    ESTABLISHED = "ESTABLISHED"   # CONFIRMED + bars_in_state >= d_min + structure_class == RANGE_STATE
    DECAYING = "DECAYING"         # panta se apropie de prag fără a-l depăși încă — semnal, nu invalidare


class StructureClass(Enum):
    """Separarea range / canal (Partea 6.4) — NU un output al `applicable_regimes`; strict local acestui producător."""
    UNCLASSIFIED = "UNCLASSIFIED"
    RANGE_STATE = "RANGE_STATE"
    CHANNEL_UP = "CHANNEL_UP"
    CHANNEL_DOWN = "CHANNEL_DOWN"


class RangeEventKindV2(Enum):
    RANGE_FORMING = "RANGE_FORMING"
    RANGE_ESTABLISHED = "RANGE_ESTABLISHED"
    RANGE_HIGH = "RANGE_HIGH"
    RANGE_LOW = "RANGE_LOW"
    RANGE_MID = "RANGE_MID"
    BREAKOUT_CANDIDATE = "BREAKOUT_CANDIDATE"
    BREAKOUT_ACCEPTED_LONG = "BREAKOUT_ACCEPTED_LONG"
    BREAKOUT_ACCEPTED_SHORT = "BREAKOUT_ACCEPTED_SHORT"
    BREAKOUT_RETEST = "BREAKOUT_RETEST"
    BREAKOUT_FAILED = "BREAKOUT_FAILED"
    LIQUIDITY_SWEEP = "LIQUIDITY_SWEEP"


class MachineStateV2(Enum):
    IDLE = "IDLE"
    FORMING = "FORMING"
    ESTABLISHED = "ESTABLISHED"
    CANDIDATE = "CANDIDATE"
    ACCEPTED = "ACCEPTED"

# reason codes (extensie V2 — reutilizează vocabularul V1 unde sensul nu s-a schimbat)
OK_RANGE = "OK_RANGE"
FEW_TOUCHES = "FEW_TOUCHES"
TOO_SHORT = "TOO_SHORT"
IS_CHANNEL = "IS_CHANNEL"                 # NOU V2 — separarea range/canal a eșuat testul de pantă
WARMUP = "WARMUP"
INPUT_UNAVAILABLE = "INPUT_UNAVAILABLE"
ACCEPTED_BREAK = "ACCEPTED_BREAK"
MAX_DURATION = "MAX_DURATION"
NO_STRUCTURE = "NO_STRUCTURE"

# F7 SAFETY_GUARD — neschimbat semantic față de 0.2.0 (STAT-M-INFERENCE-FINAL @d0d08c1, confirmat nemodificat
# de manifestul v2.7.78: „F7 = SAFETY_GUARD" în invarianții neatinși)
SAFETY_GUARD_RANGE_MID_NO_ENTRY = "RANGE_MID_NO_ENTRY"
SAFETY_GUARDS_REGISTER: tuple[str, ...] = (SAFETY_GUARD_RANGE_MID_NO_ENTRY,)


@_dc.dataclass(frozen=True, slots=True)
class EntryDecisionV2:
    permitted: bool
    guard: str | None
    reason: str


def entry_decision_v2(event: "RangeEventV2 | None") -> EntryDecisionV2:
    """SAFETY_GUARD F7 — refuz executabil identic ca semnificație cu 0.2.0: RANGE_MID ⇒ zero entry, prin construcție."""
    if event is not None and event.kind == RangeEventKindV2.RANGE_MID.value:
        return EntryDecisionV2(permitted=False, guard=SAFETY_GUARD_RANGE_MID_NO_ENTRY, reason="RANGE_MID_NO_ENTRY")
    return EntryDecisionV2(permitted=True, guard=None, reason="")


def _sha(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


# ═══════════════════════════════════ configurație + identitate ═══════════════════════════════════
@_dc.dataclass(frozen=True, slots=True)
class RangeConfigV2:
    """`w_atr` (lățime de zonă) și `s_max` (prag de pantă) sunt declarate „PRE-ÎNREGISTRATĂ" în spec dar FĂRĂ o
    valoare numerică literală în document sau manifest — verificat, absentă din ambele. Nu le-am optimizat pe
    rezultate (interzis explicit de mandat). Valorile implicite de mai jos sunt PROPUSE DE VE, PE TEMEI
    STRUCTURAL, NERATIFICATE de Statistician:
      - `w_atr = 0.25`: reutilizează punctul median al GRILEI deja pre-înregistrate în v1 ({0.10,0.25,0.50}×ATR,
        Partea F @aca7801) — NU redus dintr-o rulare pe date reale ale acestui producător (interval necunoscut
        pt. construcția mediană+interval; grila veche era calibrată pt. o construcție diferită — max+close).
      - `s_max = 0.15` (ATR per bară × d_min, adică deriva cumulată maximă admisă pe durata stării, ca fracție
        din ATR): parametru NOU introdus de V2, fără precedent în corpus; ales să fie mic (majoritatea drift-ului
        unui range adevărat trebuie să fie sub o fracție mică din ATR pe toată durata), NU derivat din rulare.
    Ambele trebuie confirmate de Statistician/CEO înainte de orice verdict empiric P1-P3 (RANGE_STATE_V2_CONTRACT.md).
    """
    n_touch: int = 2
    w_atr: float = 0.25                       # NERATIFICAT — vezi docstring
    s_max: float = 0.15                        # NERATIFICAT — vezi docstring
    d_min_bars: int = BARS_PER_DAY_M15          # implicit MULTIDAY_RANGE; vezi .intraday()/.multiday()
    duration_class: str = "MULTIDAY_RANGE"
    n_acceptance: int = 2
    precedence_rule: str = "RANGE_STATE_OVER_TREND_PAUSE"
    timeframe: str = "15m"
    swing_k: int = _K
    atr_window: int = 14
    range_window: int = 512
    max_duration_bars: int | None = None
    retest_window_bars: int = 12
    candidate_expiry_bars: int | None = None

    @classmethod
    def intraday(cls, **kw: Any) -> "RangeConfigV2":
        kw.setdefault("d_min_bars", BARS_PER_INTRADAY_SESSION_M15)
        kw.setdefault("duration_class", "INTRADAY_RANGE")
        return cls(**kw)

    @classmethod
    def multiday(cls, **kw: Any) -> "RangeConfigV2":
        kw.setdefault("d_min_bars", BARS_PER_DAY_M15)
        kw.setdefault("duration_class", "MULTIDAY_RANGE")
        return cls(**kw)

    def range_spec_id(self) -> str:
        return _sha(
            f"n_touch={self.n_touch}", f"w_atr={self.w_atr}", f"s_max={self.s_max}",
            f"d_min_bars={self.d_min_bars}", f"duration_class={self.duration_class}",
            f"N_acceptance={self.n_acceptance}", f"precedence_rule={self.precedence_rule}",
            f"timeframe={self.timeframe}", f"swing_k={self.swing_k}", f"atr_window={self.atr_window}",
            f"range_state_schema_version={RANGE_STATE_SCHEMA_VERSION_V2}",
            f"producer_version={RANGE_PRODUCER_VERSION_V2}",
        )

    def config_hash(self) -> str:
        return _sha(
            self.range_spec_id(), f"range_window={self.range_window}",
            f"max_duration_bars={self.max_duration_bars}", f"retest_window_bars={self.retest_window_bars}",
            f"candidate_expiry_bars={self.candidate_expiry_bars}",
        )

    def run_hash(self, data_identity: str) -> str:
        return _sha(self.config_hash(), _sha(data_identity), self.range_spec_id())

    def _cand_expiry(self) -> int:
        return self.candidate_expiry_bars if self.candidate_expiry_bars is not None else self.n_acceptance + 1


# ═══════════════════════════════════ rezultat + eveniment ═══════════════════════════════════
@_dc.dataclass(frozen=True, slots=True)
class RangeStateResultV2:
    available: bool
    reason: str
    range_spec_id: str
    bar_index: int
    ts_close: int
    anchor_upper: float | None = None
    anchor_lower: float | None = None
    w: float | None = None                    # lățime de zonă în preț (= w_atr × atr curent)
    boundary_zone_upper: tuple[float, float] | None = None
    boundary_zone_lower: tuple[float, float] | None = None
    range_mid: float | None = None
    boundary_validity: str | None = None
    data_readiness: str | None = None
    consolidation_state: str | None = None
    structure_class: str | None = None
    slope: float | None = None
    structural_start_ts: int | None = None
    actionable_start_ts: int | None = None
    touches_upper: int | None = None
    touches_lower: int | None = None
    bars_in_state: int | None = None
    structure_events_inside: int | None = None
    trend_context: str | None = None
    invalidation: str | None = None
    reason_codes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return _dc.asdict(self)


@_dc.dataclass(frozen=True, slots=True)
class RangeEventV2:
    kind: str
    confirm_ts: int
    bar_index: int
    boundary: str | None
    reason_codes: tuple[str, ...]
    not_yet_available: tuple[str, ...]
    event_contract_version: str
    range_spec_id: str
    safety_guard: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return _dc.asdict(self)


class RangeContractErrorV2(Exception):
    pass


class _CSwing:
    __slots__ = ("idx", "price", "is_high", "ts")

    def __init__(self, idx: int, price: float, is_high: bool, ts: int) -> None:
        self.idx = idx; self.price = price; self.is_high = is_high; self.ts = ts


def _median(values: list[float]) -> float:
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0


# ═══════════════════════════════════ producătorul incremental V2 ═══════════════════════════════════
class RangeStateProducerV2:
    """Producător INCREMENTAL SPEC V2. `observe(...)` primește o bară închisă + ATR cauzal, întoarce
    `(RangeStateResultV2, list[RangeEventV2])`. Stare serializabilă integral, restaurabilă bit-identic."""

    def __init__(self, config: RangeConfigV2) -> None:
        self._cfg = config
        self._spec_id = config.range_spec_id()
        self._n = 0
        self._last_atr: float = 0.0
        # fereastra de fractali (2k+1) — stream de swing-uri CONFIRMATE, strict D2, identic cu N1
        self._wh: deque[float] = deque(maxlen=2 * config.swing_k + 1)
        self._wl: deque[float] = deque(maxlen=2 * config.swing_k + 1)
        self._wts: deque[int] = deque(maxlen=2 * config.swing_k + 1)
        self._highs: deque[_CSwing] = deque()     # swing-uri HIGH confirmate, active (mărginite la range_window)
        self._lows: deque[_CSwing] = deque()
        # episod curent
        self._machine = MachineStateV2.IDLE
        self._anchor_upper: float | None = None
        self._anchor_lower: float | None = None
        self._structural_start_idx: int | None = None
        self._structural_start_ts: int | None = None
        self._confirm_ts: int | None = None
        self._touches_upper: int = 0
        self._touches_lower: int = 0
        self._was_confirmed: bool = False
        self._boundary_validity: BoundaryValidityV2 | None = None
        self._invalidation: str | None = None
        self._structure_class: StructureClass = StructureClass.UNCLASSIFIED
        # regresie OLS pe FEREASTRA MĂRGINITĂ trailing de `d_min_bars` close-uri (NU episodul întreg — o fereastră
        # care CREȘTE nemărginit ar face panta din ce în ce mai zgomotoasă/instabilă în timp, sensibilă la
        # capetele vechi ale unei ferestre parțiale de ciclu; fereastra fixă = același `d_min` folosit și în
        # formula de derivă ⇒ coerent, O(d_min_bars)/bară, mărginit — nu O(n))
        self._closes: deque[float] = deque(maxlen=config.d_min_bars)
        # contor descriptiv de evenimente structurale INTERNE (BOS/CHoCH) — NU invalidează episodul
        self._internal: IncrementalRawAxesBuilder = IncrementalRawAxesBuilder("V2_INTERNAL", horizon=config.range_window)
        self._internal_last_break: str | None = None
        self._structure_events_inside: int = 0
        # breakout
        self._cand_boundary: str | None = None
        self._cand_dir: int = 0
        self._cand_consec: int = 0
        self._cand_bar: int | None = None
        self._accepted_zone_edge: float | None = None
        self._accepted_dir: int = 0
        self._accepted_bar: int | None = None

    # ── fractal HIGH/LOW brut (identic ca detecție cu N1/V1 — NU labeling, doar extremul) ──
    def _detect_confirmed_swing(self, i: int) -> _CSwing | None:
        k = self._cfg.swing_k
        if len(self._wh) < 2 * k + 1:
            return None
        c = k
        ch = self._wh[c]; cl = self._wl[c]
        idx = i - k
        cts = self._wts[c]                          # ts_close al barei formării extremului (retrospectiv)
        if all(ch > self._wh[j] for j in range(2 * k + 1) if j != c):
            return _CSwing(idx=idx, price=ch, is_high=True, ts=cts)
        if all(cl < self._wl[j] for j in range(2 * k + 1) if j != c):
            return _CSwing(idx=idx, price=cl, is_high=False, ts=cts)
        return None

    def _prune(self, i: int) -> None:
        lo = i - self._cfg.range_window + 1
        while self._highs and self._highs[0].idx < lo:
            self._highs.popleft()
        while self._lows and self._lows[0].idx < lo:
            self._lows.popleft()

    def _reset_episode(self) -> None:
        self._machine = MachineStateV2.IDLE
        self._anchor_upper = self._anchor_lower = None
        self._structural_start_idx = self._structural_start_ts = self._confirm_ts = None
        self._touches_upper = self._touches_lower = 0
        self._was_confirmed = False
        self._boundary_validity = None
        self._structure_class = StructureClass.UNCLASSIFIED
        self._closes.clear()
        self._structure_events_inside = 0
        self._cand_boundary = None; self._cand_dir = 0; self._cand_consec = 0; self._cand_bar = None

    def _update_anchors(self) -> None:
        if self._highs:
            self._anchor_upper = _median([s.price for s in self._highs])
        if self._lows:
            self._anchor_lower = _median([s.price for s in self._lows])

    def _update_regression(self, close: float) -> None:
        self._closes.append(close)                # deque mărginit la d_min_bars — O(1) amortizat/bară

    def _slope(self) -> float:
        """OLS pe fereastra TRAILING de până la `d_min_bars` close-uri — O(d_min_bars)/bară, mărginit."""
        n = len(self._closes)
        if n < 2:
            return 0.0
        sx = sy = sxy = sxx = 0.0
        for x, y in enumerate(self._closes):
            fx = float(x)
            sx += fx; sy += y; sxy += fx * y; sxx += fx * fx
        denom = n * sxx - sx * sx
        if denom == 0.0:
            return 0.0
        return (n * sxy - sx * sy) / denom

    def observe(self, *, bar_index: int, ts_close: int, open_: float, high: float, low: float,
                close: float, atr: float | None, trend_context: str | None
               ) -> tuple[RangeStateResultV2, list[RangeEventV2]]:
        cfg = self._cfg
        i = self._n
        self._n += 1
        self._wh.append(high); self._wl.append(low); self._wts.append(ts_close)
        self._last_atr = atr if atr is not None else 0.0

        def unavailable(reason: str, readiness: DataReadiness) -> tuple[RangeStateResultV2, list[RangeEventV2]]:
            return (RangeStateResultV2(available=False, reason=reason, range_spec_id=self._spec_id,
                                       bar_index=i, ts_close=ts_close, data_readiness=readiness.value,
                                       reason_codes=(reason,)), [])

        if atr is None:
            if i < cfg.atr_window or i < 2 * cfg.swing_k + 1:
                return unavailable(WARMUP, DataReadiness.WARMUP)
            if self._machine != MachineStateV2.IDLE:
                self._invalidation = INPUT_UNAVAILABLE
                self._reset_episode()
            return unavailable(INPUT_UNAVAILABLE, DataReadiness.DEGRADED)

        # descriptor intern (BOS/CHoCH) — NICIODATĂ nu invalidează, doar se numără dacă un episod e activ
        self._internal.observe(_InternalBar(bar_index, ts_close, open_, high, low, close))
        if self._machine != MachineStateV2.IDLE:
            lb = self._internal.latest_break_kind
            if lb is not None and lb != self._internal_last_break:
                self._structure_events_inside += 1
        self._internal_last_break = self._internal.latest_break_kind

        sw = self._detect_confirmed_swing(i)
        if sw is not None:
            (self._highs if sw.is_high else self._lows).append(sw)
        self._prune(i)

        events: list[RangeEventV2] = []

        if self._machine == MachineStateV2.IDLE:
            if self._highs and self._lows:
                self._start_episode(i)
                events.append(self._mk_event(RangeEventKindV2.RANGE_FORMING, ts_close, i, None, (OK_RANGE,), ()))

        if self._machine != MachineStateV2.IDLE:
            self._update_anchors()
            self._update_regression(close)
            if (cfg.max_duration_bars is not None and self._structural_start_idx is not None
                    and (i - self._structural_start_idx + 1) > cfg.max_duration_bars):
                self._invalidation = MAX_DURATION
                self._reset_episode()

        if self._machine == MachineStateV2.IDLE:
            return self._build_result(i, ts_close, close, atr, trend_context), events

        self._run_machine(i, ts_close, high, low, close, atr, events)
        result = self._build_result(i, ts_close, close, atr, trend_context)
        return result, events

    def _start_episode(self, i: int) -> None:
        oldest = min([*self._highs, *self._lows], key=lambda s: s.idx)
        self._structural_start_idx = oldest.idx
        self._structural_start_ts = oldest.ts
        self._machine = MachineStateV2.FORMING
        self._boundary_validity = BoundaryValidityV2.PROVISIONAL
        self._touches_upper = 0; self._touches_lower = 0
        self._was_confirmed = False
        self._invalidation = None
        self._structure_class = StructureClass.UNCLASSIFIED
        self._closes.clear()
        self._structure_events_inside = 0
        self._internal_last_break = self._internal.latest_break_kind

    def _touch_zone(self, lo_bar: float, hi_bar: float, anchor: float) -> bool:
        w = self._cfg.w_atr * self._last_atr
        return hi_bar >= anchor - w and lo_bar <= anchor + w

    def _run_machine(self, i: int, ts: int, high: float, low: float, close: float, atr: float,
                     events: list[RangeEventV2]) -> None:
        cfg = self._cfg
        if self._machine == MachineStateV2.CANDIDATE:
            self._machine_candidate(i, ts, close, events)
            return
        if self._machine == MachineStateV2.ACCEPTED:
            self._machine_accepted(i, ts, high, low, close, events)
            return

        assert self._anchor_upper is not None and self._anchor_lower is not None
        w = cfg.w_atr * atr
        upper_edge = self._anchor_upper + w
        lower_edge = self._anchor_lower - w

        # touch acumulat CAUZAL contra zonei curente — NICIODATĂ re-scanat retroactiv contra unei zone viitoare
        touched_upper_now = self._touch_zone(low, high, self._anchor_upper)
        touched_lower_now = self._touch_zone(low, high, self._anchor_lower)

        if self._machine == MachineStateV2.FORMING or self._machine == MachineStateV2.ESTABLISHED:
            if close > upper_edge:
                self._touches_upper += 1 if touched_upper_now else 0
                self._open_candidate('upper', +1, i, ts, events)
                return
            if close < lower_edge:
                self._touches_lower += 1 if touched_lower_now else 0
                self._open_candidate('lower', -1, i, ts, events)
                return
            if high > upper_edge and close <= upper_edge:
                events.append(self._mk_event(RangeEventKindV2.LIQUIDITY_SWEEP, ts, i, 'upper', (OK_RANGE,), ()))
                if touched_upper_now:
                    self._touches_upper += 1
                self._maybe_confirm(ts, i, events)
                return
            if low < lower_edge and close >= lower_edge:
                events.append(self._mk_event(RangeEventKindV2.LIQUIDITY_SWEEP, ts, i, 'lower', (OK_RANGE,), ()))
                if touched_lower_now:
                    self._touches_lower += 1
                self._maybe_confirm(ts, i, events)
                return
            if touched_upper_now:
                self._touches_upper += 1
                events.append(self._mk_event(RangeEventKindV2.RANGE_HIGH, ts, i, 'upper', (OK_RANGE,), ()))
                self._maybe_confirm(ts, i, events)
                return
            if touched_lower_now:
                self._touches_lower += 1
                events.append(self._mk_event(RangeEventKindV2.RANGE_LOW, ts, i, 'lower', (OK_RANGE,), ()))
                self._maybe_confirm(ts, i, events)
                return
            events.append(self._mk_event(RangeEventKindV2.RANGE_MID, ts, i, None, (OK_RANGE,), ()))
            self._maybe_confirm(ts, i, events)

    def _maybe_confirm(self, ts: int, i: int, events: list[RangeEventV2]) -> None:
        cfg = self._cfg
        confirmed = self._touches_upper >= cfg.n_touch and self._touches_lower >= cfg.n_touch
        if confirmed:
            self._boundary_validity = BoundaryValidityV2.CONFIRMED
            if not self._was_confirmed:
                self._was_confirmed = True
                self._confirm_ts = ts
        else:
            self._boundary_validity = BoundaryValidityV2.PROVISIONAL
        self._classify_and_maybe_establish(ts, i, events)

    def _classify_and_maybe_establish(self, ts: int, i: int, events: list[RangeEventV2]) -> None:
        cfg = self._cfg
        bars_in_state = self._bars_in_state()
        was_established = self._machine == MachineStateV2.ESTABLISHED
        if self._boundary_validity != BoundaryValidityV2.CONFIRMED or bars_in_state < cfg.d_min_bars:
            self._structure_class = StructureClass.UNCLASSIFIED
            if self._machine == MachineStateV2.FORMING:
                return
        slope = self._slope()
        drift = abs(slope) * cfg.d_min_bars      # spec: |slope| × d_min (constantă FIXĂ), NU × bars_in_state
        threshold = cfg.s_max * self._last_atr   # (altfel deriva crește nemărginit cu durata episodului, fals-pozitiv)
        if self._boundary_validity == BoundaryValidityV2.CONFIRMED and bars_in_state >= cfg.d_min_bars:
            if drift <= threshold:
                self._structure_class = StructureClass.RANGE_STATE
                if self._machine == MachineStateV2.FORMING and not was_established:
                    self._machine = MachineStateV2.ESTABLISHED
                    events.append(self._mk_event(RangeEventKindV2.RANGE_ESTABLISHED, ts, i, None, (OK_RANGE,), ()))
            else:
                self._structure_class = StructureClass.CHANNEL_UP if slope > 0 else StructureClass.CHANNEL_DOWN

    def _bars_in_state(self) -> int:
        if self._structural_start_idx is None:
            return 0
        return self._n - self._structural_start_idx

    def _mk_event(self, kind: RangeEventKindV2, ts: int, i: int, boundary: str | None,
                  reasons: tuple[str, ...], nya: tuple[str, ...]) -> RangeEventV2:
        guard = SAFETY_GUARD_RANGE_MID_NO_ENTRY if kind is RangeEventKindV2.RANGE_MID else None
        return RangeEventV2(kind=kind.value, confirm_ts=ts, bar_index=i, boundary=boundary,
                            reason_codes=reasons, not_yet_available=nya,
                            event_contract_version=RANGE_EVENT_CONTRACT_VERSION_V2, range_spec_id=self._spec_id,
                            safety_guard=guard)

    def _open_candidate(self, boundary: str, direction: int, i: int, ts: int, events: list[RangeEventV2]) -> None:
        self._machine = MachineStateV2.CANDIDATE
        self._cand_boundary = boundary; self._cand_dir = direction
        self._cand_consec = 1; self._cand_bar = i
        events.append(self._mk_event(RangeEventKindV2.BREAKOUT_CANDIDATE, ts, i, boundary, (OK_RANGE,),
                                     ("will_be_accepted_or_failed",)))

    def _beyond(self, close: float) -> bool:
        assert self._anchor_upper is not None and self._anchor_lower is not None
        w = self._cfg.w_atr * self._last_atr
        if self._cand_dir > 0:
            return close > self._anchor_upper + w
        return close < self._anchor_lower - w

    def _machine_candidate(self, i: int, ts: int, close: float, events: list[RangeEventV2]) -> None:
        cfg = self._cfg
        if self._beyond(close):
            self._cand_consec += 1
            if self._cand_consec >= cfg.n_acceptance:
                assert self._anchor_upper is not None and self._anchor_lower is not None
                self._machine = MachineStateV2.ACCEPTED
                self._boundary_validity = BoundaryValidityV2.VIOLATED
                self._invalidation = ACCEPTED_BREAK
                w = cfg.w_atr * self._last_atr
                self._accepted_zone_edge = ((self._anchor_upper + w) if self._cand_dir > 0
                                            else (self._anchor_lower - w))
                self._accepted_dir = self._cand_dir
                self._accepted_bar = i
                kind = (RangeEventKindV2.BREAKOUT_ACCEPTED_LONG if self._cand_dir > 0
                       else RangeEventKindV2.BREAKOUT_ACCEPTED_SHORT)
                events.append(self._mk_event(kind, ts, i, self._cand_boundary, (ACCEPTED_BREAK,),
                                             ("will_retest_or_not",)))
            return
        b = self._cand_boundary
        self._machine = MachineStateV2.ESTABLISHED
        self._cand_boundary = None; self._cand_dir = 0; self._cand_consec = 0; self._cand_bar = None
        events.append(self._mk_event(RangeEventKindV2.BREAKOUT_FAILED, ts, i, b, (OK_RANGE,), ()))

    def _machine_accepted(self, i: int, ts: int, high: float, low: float, close: float,
                          events: list[RangeEventV2]) -> None:
        cfg = self._cfg
        assert self._accepted_zone_edge is not None
        edge = self._accepted_zone_edge
        boundary = 'upper' if self._accepted_dir > 0 else 'lower'
        if self._accepted_dir > 0:
            hit = low <= edge and close >= edge
        else:
            hit = high >= edge and close <= edge
        if hit:
            events.append(self._mk_event(RangeEventKindV2.BREAKOUT_RETEST, ts, i, boundary, (OK_RANGE,), ()))
            self._end_after_accept()
            return
        if self._accepted_bar is not None and (i - self._accepted_bar) >= cfg.retest_window_bars:
            self._end_after_accept()

    def _end_after_accept(self) -> None:
        self._accepted_zone_edge = None; self._accepted_dir = 0; self._accepted_bar = None
        self._reset_episode()
        self._invalidation = None

    def _build_result(self, i: int, ts: int, close: float, atr: float,
                      trend_context: str | None) -> RangeStateResultV2:
        cfg = self._cfg
        if self._machine == MachineStateV2.ACCEPTED:
            return RangeStateResultV2(available=False, reason=ACCEPTED_BREAK, range_spec_id=self._spec_id,
                                      bar_index=i, ts_close=ts, data_readiness=DataReadiness.READY.value,
                                      boundary_validity=BoundaryValidityV2.VIOLATED.value,
                                      invalidation=ACCEPTED_BREAK, reason_codes=(ACCEPTED_BREAK,))
        if self._machine == MachineStateV2.IDLE:
            inv = self._invalidation
            self._invalidation = None
            return RangeStateResultV2(available=False, reason=(inv or NO_STRUCTURE), range_spec_id=self._spec_id,
                                      bar_index=i, ts_close=ts, data_readiness=DataReadiness.READY.value,
                                      invalidation=inv, reason_codes=((inv,) if inv else (NO_STRUCTURE,)))
        assert self._anchor_upper is not None and self._anchor_lower is not None
        w = cfg.w_atr * atr
        bars_in_state = self._bars_in_state()
        slope = self._slope()

        reasons: list[str] = []
        if self._touches_upper < cfg.n_touch or self._touches_lower < cfg.n_touch:
            reasons.append(FEW_TOUCHES)
        if bars_in_state < cfg.d_min_bars:
            reasons.append(TOO_SHORT)
        if self._structure_class in (StructureClass.CHANNEL_UP, StructureClass.CHANNEL_DOWN):
            reasons.append(IS_CHANNEL)
        consol = ConsolidationStateV2.NONE
        if self._boundary_validity == BoundaryValidityV2.PROVISIONAL:
            consol = ConsolidationStateV2.FORMING
        elif self._structure_class == StructureClass.RANGE_STATE:
            consol = ConsolidationStateV2.ESTABLISHED
        elif self._structure_class in (StructureClass.CHANNEL_UP, StructureClass.CHANNEL_DOWN):
            consol = ConsolidationStateV2.DECAYING
        else:
            consol = ConsolidationStateV2.FORMING
        if not reasons and consol == ConsolidationStateV2.ESTABLISHED:
            reasons.append(OK_RANGE)

        return RangeStateResultV2(
            available=True, reason=(OK_RANGE if consol == ConsolidationStateV2.ESTABLISHED else "forming"),
            range_spec_id=self._spec_id, bar_index=i, ts_close=ts,
            anchor_upper=self._anchor_upper, anchor_lower=self._anchor_lower, w=w,
            boundary_zone_upper=(self._anchor_upper - w, self._anchor_upper + w),
            boundary_zone_lower=(self._anchor_lower - w, self._anchor_lower + w),
            range_mid=(self._anchor_upper + self._anchor_lower) / 2.0,
            boundary_validity=(self._boundary_validity.value if self._boundary_validity else None),
            data_readiness=DataReadiness.READY.value, consolidation_state=consol.value,
            structure_class=self._structure_class.value, slope=slope,
            structural_start_ts=self._structural_start_ts, actionable_start_ts=self._confirm_ts,
            touches_upper=self._touches_upper, touches_lower=self._touches_lower, bars_in_state=bars_in_state,
            structure_events_inside=self._structure_events_inside,
            trend_context=trend_context, invalidation=None, reason_codes=tuple(reasons),
        )

    # ── snapshot / restore bit-identic ──
    def snapshot_state(self) -> dict[str, Any]:
        return {
            "n": self._n, "wh": list(self._wh), "wl": list(self._wl), "wts": list(self._wts),
            "highs": [[s.idx, s.price, s.is_high, s.ts] for s in self._highs],
            "lows": [[s.idx, s.price, s.is_high, s.ts] for s in self._lows],
            "machine": self._machine.value,
            "anchor_upper": self._anchor_upper, "anchor_lower": self._anchor_lower,
            "structural_start_idx": self._structural_start_idx, "structural_start_ts": self._structural_start_ts,
            "confirm_ts": self._confirm_ts,
            "touches_upper": self._touches_upper, "touches_lower": self._touches_lower,
            "was_confirmed": self._was_confirmed,
            "boundary_validity": (self._boundary_validity.value if self._boundary_validity else None),
            "invalidation": self._invalidation, "structure_class": self._structure_class.value,
            "closes": list(self._closes),
            "internal_state": self._internal.snapshot_state(), "internal_last_break": self._internal_last_break,
            "structure_events_inside": self._structure_events_inside,
            "cand_boundary": self._cand_boundary, "cand_dir": self._cand_dir,
            "cand_consec": self._cand_consec, "cand_bar": self._cand_bar,
            "accepted_zone_edge": self._accepted_zone_edge, "accepted_dir": self._accepted_dir,
            "accepted_bar": self._accepted_bar, "last_atr": self._last_atr,
        }

    def restore_state(self, st: dict[str, Any]) -> None:
        k = self._cfg.swing_k
        self._n = st["n"]
        self._wh = deque(st["wh"], maxlen=2 * k + 1); self._wl = deque(st["wl"], maxlen=2 * k + 1)
        self._wts = deque(st["wts"], maxlen=2 * k + 1)
        self._highs = deque(_CSwing(a, b, c, d) for a, b, c, d in st["highs"])
        self._lows = deque(_CSwing(a, b, c, d) for a, b, c, d in st["lows"])
        self._machine = MachineStateV2(st["machine"])
        self._anchor_upper = st["anchor_upper"]; self._anchor_lower = st["anchor_lower"]
        self._structural_start_idx = st["structural_start_idx"]; self._structural_start_ts = st["structural_start_ts"]
        self._confirm_ts = st["confirm_ts"]
        self._touches_upper = st["touches_upper"]; self._touches_lower = st["touches_lower"]
        self._was_confirmed = st["was_confirmed"]
        self._boundary_validity = BoundaryValidityV2(st["boundary_validity"]) if st["boundary_validity"] else None
        self._invalidation = st["invalidation"]; self._structure_class = StructureClass(st["structure_class"])
        self._closes = deque(st["closes"], maxlen=self._cfg.d_min_bars)
        self._internal = IncrementalRawAxesBuilder("V2_INTERNAL", horizon=self._cfg.range_window)
        self._internal.restore_state(st["internal_state"])
        self._internal_last_break = st["internal_last_break"]
        self._structure_events_inside = st["structure_events_inside"]
        self._cand_boundary = st["cand_boundary"]; self._cand_dir = st["cand_dir"]
        self._cand_consec = st["cand_consec"]; self._cand_bar = st["cand_bar"]
        self._accepted_zone_edge = st["accepted_zone_edge"]; self._accepted_dir = st["accepted_dir"]
        self._accepted_bar = st["accepted_bar"]; self._last_atr = st["last_atr"]


class _InternalBar:
    """Adaptor minimal pt. `IncrementalRawAxesBuilder.observe` (contorul descriptiv intern) — simbol distinct
    de `symbol`-ul real, pentru a nu coincide accidental cu vreun engine N1 real (izolare completă)."""
    __slots__ = ("symbol", "ts_open", "ts_close", "open", "high", "low", "close", "volume")

    def __init__(self, i: int, ts_close: int, open_: float, high: float, low: float, close: float) -> None:
        self.symbol = "V2_INTERNAL"
        self.ts_open = ts_close - 900; self.ts_close = ts_close
        self.open = open_; self.high = high; self.low = low; self.close = close; self.volume = 0.0
