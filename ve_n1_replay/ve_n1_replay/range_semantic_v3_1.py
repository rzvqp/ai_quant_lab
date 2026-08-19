"""RANGE SEMANTIC V3.1 (0.4.1) — PERFORMANCE DELTA FIX, NU un patch semantic.

Remediază EXCLUSIV defectul §12 identificat de Red Team `RT-RANGE-0004` @`87cad2c` (ledger E79), verdict
`RANGE_V3_SEMANTIC_FAIL` pe `ve_n1_replay 0.4.0` (build `dead38d`, delivery `034b919`): `RangeConfigV3`
accepta `d_min_bars` NEMĂRGINIT (ex. 200000), iar `_Segment.slope()` (0.4.0) re-parcurgea ÎNTREAGA coadă
`closes` la FIECARE bară — O(`d_min_bars`)/bară, măsurat 20,1× cost pt. 20× `d_min_bars`, extrapolat ~8,9h
la `d_min_bars=200000` (peste garanția de 4h la 355.696 bare). Restul semanticii V3 (14 stări, segmentare
longitudinală, ancoră locală, `ZONES_DEGENERATE`, K/N, HBL-20, F7) a trecut INDEPENDENT verificat de Red
Team — NEATINS aici (domeniu STRICT performanță).

**Fix ales — Varianta A (preferată de mandat)**: pantă OLS pe fereastra trailing calculată printr-o
reformulare cu STATISTICI SUFICIENTE, actualizate incremental O(1)/bară, NU o resortare/reparcurgere
completă. NICIUN plafon arbitrar pt. `d_min_bars` — spec `bf9f780` e tăcută asupra unui asemenea maxim, iar
mandatul interzice explicit alegerea unui număr doar ca benchmarkul să treacă (Varianta B rămâne
NEUTILIZATĂ din lipsă de sursă normativă). Aceeași definiție matematică OLS, aceeași fereastră semantică
(`d_min_bars`), memorie explicit mărginită (`deque(maxlen=d_min_bars)` neschimbată + trei scalari), verificat
identic cu un oracol recalculat de la zero la FIECARE prefix (`tests/test_range_semantic_v3_1.py`), inclusiv
la scara adversarială `d_min_bars=200000` din raportul Red Team.

**`ve_n1_replay/range_semantic_v3.py` (0.4.0) rămâne BYTE-NEATINS** (verificat: `git diff` gol) — păstrat
pentru audit/rollback, la fel ca fiecare versiune anterioară. Acest fișier e NOU, spațiu de nume propriu
pt. identitate (`RANGE_PRODUCER_VERSION_V3_1`), dar REUTILIZEAZĂ direct (import, NU reimplementare) tot ce
NU s-a schimbat semantic: enumurile celor 14 stări/evenimente, toate reason codes, `RangeConfigV3` (K/N/
w_atr/d_min_bars — NICIO schimbare de câmp/validare), `_Swing`, `_RunningMedian` (ancora, neatinsă),
`EntryDecisionV3`/`entry_decision_v3` (F7), dataclass-urile de rezultat/eveniment/istoric.
"""
from __future__ import annotations

import dataclasses as _dc
from collections import deque
from typing import Any

from .range_semantic_v3 import (
    ConfigNotRatifiedError, RangeSemanticContractErrorV3,
    SegmentEventKindV3, SegmentLifecycleV3,
    OK_RANGE, RANGE_FORMING, ESTABLISHING_FEW_SWINGS, ATR_UNAVAILABLE, FEW_TOUCHES, TOO_SHORT, IS_CHANNEL,
    ZONES_DEGENERATE, BETWEEN_SEGMENTS, TERMINATED_BY_BREAKOUT, RANGE_FAILED_PRECONDITION, SWEEP_WINDOW_EXPIRED,
    NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT, REASON_CODES_V3,
    SAFETY_GUARD_RANGE_MID_NO_ENTRY, SAFETY_GUARDS_REGISTER,
    EntryDecisionV3, entry_decision_v3,
    RangeConfigV3, RangeSemanticResultV3, RangeEventV3, ConfirmedSegmentRecordV3,
    _Swing, _RunningMedian, _sha,
)
from .version import (
    RANGE_SEMANTIC_CONTRACT_VERSION_V3, RANGE_CONFIG_SCHEMA_VERSION_V3, RANGE_EVENT_CONTRACT_VERSION_V3,
    RANGE_PRODUCER_VERSION_V3_1,
)

__all__ = [
    "ConfigNotRatifiedError", "RangeSemanticContractErrorV3",
    "SegmentEventKindV3", "SegmentLifecycleV3", "REASON_CODES_V3",
    "SAFETY_GUARD_RANGE_MID_NO_ENTRY", "SAFETY_GUARDS_REGISTER",
    "EntryDecisionV3", "entry_decision_v3",
    "RangeConfigV31", "RangeSemanticResultV3", "RangeEventV3", "ConfirmedSegmentRecordV3",
    "RangeSemanticProducerV31",
]


# ═══════════════════════════════════ configurație — CÂMPURI moștenite neschimbate, identitate nouă + hardening ═══════════════════════════════════
class RangeConfigV31(RangeConfigV3):
    """Reutilizează `RangeConfigV3` (0.4.0) NESCHIMBAT ca CÂMPURI — K/N/w_atr/d_min_bars/n_touch/... și
    `__post_init__` al PĂRINTELUI (inclusiv invariantul `K<=N`) rulează EXACT ca-n 0.4.0, nicio duplicare
    (`super().__post_init__()`). Identitatea (`range_spec_id`) diferă, ca fingerprint-ul configurației să
    reflecte implementarea 0.4.1 (panta incrementală), nu 0.4.0 — mandatul §5.

    **Amendament CEO (hardening input-validation, NU schimbare semantică RANGE)**: `RangeConfigV3` (0.4.0)
    nu validează NICIODATĂ `d_min_bars` — un gol PREEXISTENT (K/N/w_atr au verificări explicite, d_min_bars
    nu). La `d_min_bars=0`, 0.4.0 rămâne silențios (`slope()` întoarce mereu 0.0 -- coada `deque(maxlen=0)`
    rămâne perpetuu goală), dar `_SegmentV31.push_close()` (0.4.1) verifică `len(closes)==maxlen` ÎNAINTE de
    append și indexează `closes[0]` pe o coadă goală -> `IndexError` necontractual, descoperit și raportat
    (`RANGE_V3_1_PARITY_REPORT.md` §5b) ÎNAINTE de livrare. Remediat aici, la GRANIȚA de construcție a
    configurației -- `d_min_bars` invalid nu poate produce NICIODATĂ o instanță `RangeConfigV31`, deci nu
    poate ajunge NICIODATĂ la `_SegmentV31`/`RangeSemanticProducerV31`/`RangeSemanticEngineV31` (calea de
    crash devine STRUCTURAL INACCESIBILĂ, nu doar "prinsă" mai târziu)."""
    __slots__ = ()

    def range_spec_id(self) -> str:
        return _sha(
            f"K={self.K}", f"N={self.N}", f"w_atr={self.w_atr}", f"n_touch={self.n_touch}",
            f"d_min_bars={self.d_min_bars}", f"duration_class={self.duration_class}",
            f"timeframe={self.timeframe}", f"swing_k={self.swing_k}", f"atr_window={self.atr_window}",
            f"range_semantic_contract_version={RANGE_SEMANTIC_CONTRACT_VERSION_V3}",
            f"range_config_schema_version={RANGE_CONFIG_SCHEMA_VERSION_V3}",
            f"producer_version={RANGE_PRODUCER_VERSION_V3_1}",   # <- SINGURA diferență față de RangeConfigV3
        )
    # config_hash()/run_hash() (moștenite neschimbate) apelează self.range_spec_id() -- dispatch normal,
    # preiau automat noul fingerprint fără nicio suprascriere suplimentară.

    def __post_init__(self) -> None:
        super().__post_init__()   # K/N/w_atr/acknowledge_construction_only/K<=N -- EXACT ca-n 0.4.0, neschimbate
        if isinstance(self.d_min_bars, bool) or not isinstance(self.d_min_bars, int):
            raise RangeSemanticContractErrorV3(
                f"d_min_bars trebuie să fie int, primit {type(self.d_min_bars).__name__}={self.d_min_bars!r} "
                "-- fereastra trailing a pantei (statistici suficiente incrementale) e definită doar pt. un "
                "număr întreg de bare; bool e explicit refuzat deși e subtip de int (ambiguitate de tip)")
        if self.d_min_bars < 1:
            raise RangeSemanticContractErrorV3(
                f"d_min_bars trebuie să fie >=1, primit {self.d_min_bars!r} -- o fereastră de sub 1 bară nu "
                "are pantă/geometrie definită (0 ar produce o coadă `deque(maxlen=0)` perpetuu goală)")


# ═══════════════════════════════════ panta OLS incrementală — fix-ul §12 ═══════════════════════════════════
class _IncrementalSlope:
    """Panta OLS pe fereastra trailing MĂRGINITĂ, prin statistici suficiente — NU o reparcurgere completă la
    fiecare bară (asta era exact defectul RT-RANGE-0004 §12: O(d_min_bars)/bară).

    x = poziția LOCALĂ 0..n-1 în fereastră (spațiere egală, cunoscută) ⇒ `Sx(n)=n(n-1)/2`, `Sxx(n)=
    n(n-1)(2n-1)/6` sunt FORME ÎNCHISE — funcție DOAR de mărimea curentă a ferestrei, niciodată urmărite
    incremental (deci fără risc de acumulare/cancelare pe termen lung din partea lor). `Sy`/`Sxy` (care
    DEPIND de valorile y și de poziția lor relativă) sunt actualizate incremental, O(1)/bară:
      - în creștere (fereastra încă nu s-a umplut): adăugare pură la poziția `n` curentă, fără deplasare;
      - plină (o valoare iese, una intră): valoarea la poziția 0 e evicted, restul se deplasează cu -1
        (derivare: `Sxy_nou = Sxy_vechi - Sy_vechi + y_evicted + (n-1)*y_nou`), noua valoare intră la n-1.
    Aceeași definiție matematică OLS ca varianta 0.4.0 (batch); verificat empiric identic cu un oracol
    recalculat de la zero la FIECARE prefix, pe secvențe adversariale + la scara `d_min_bars=200000` din
    raportul Red Team (diferență absolută 0,0 la finalul umplerii, teste dedicate)."""
    __slots__ = ("_maxlen", "_sum_y", "_sum_xy", "_n")

    def __init__(self, maxlen: int) -> None:
        self._maxlen = maxlen
        self._sum_y: float = 0.0
        self._sum_xy: float = 0.0
        self._n: int = 0

    def push(self, y_new: float, y_evicted: float | None) -> None:
        """`y_evicted` = valoarea care tocmai a ieșit din coada `closes` (None cât timp fereastra se umple)."""
        if y_evicted is None:
            n = self._n
            self._sum_xy += n * y_new
            self._sum_y += y_new
            self._n += 1
        else:
            n = self._maxlen
            self._sum_xy = self._sum_xy - self._sum_y + y_evicted + (n - 1) * y_new
            self._sum_y = self._sum_y - y_evicted + y_new
            # self._n rămâne = maxlen (fereastra era deja plină, evict+append o păstrează plină)

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
    def restore(cls, st: dict[str, Any], maxlen: int) -> "_IncrementalSlope":
        obj = cls(maxlen)
        obj._sum_y = st["sum_y"]; obj._sum_xy = st["sum_xy"]; obj._n = st["n"]
        return obj


class _SegmentV31:
    """Copie CHIRURGICALĂ a `_Segment` (0.4.0, `range_semantic_v3.py`, NEATINSĂ) — identică peste tot ÎN
    AFARA urmăririi pantei: `closes` rămâne coada mărginită (audit + sursă pt. valoarea evicted), dar
    `slope()` citește acum `_IncrementalSlope` (O(1)) în loc să re-parcurgă `closes` (O(d_min_bars))."""

    def __init__(self, *, segment_id: int, predecessor_id: int | None, transition_reason: str | None,
                config: RangeConfigV31) -> None:
        self.segment_id = segment_id
        self.predecessor_id = predecessor_id
        self.transition_reason = transition_reason
        self._cfg = config
        self.lifecycle = SegmentLifecycleV3.ESTABLISHING
        self.structural_start_idx: int | None = None
        self.structural_start_ts: int | None = None
        self.confirm_ts: int | None = None
        self.was_confirmed = False
        self.establishing_emitted = False
        self.highs: list[_Swing] = []
        self.lows: list[_Swing] = []
        self._high_median = _RunningMedian()
        self._low_median = _RunningMedian()
        self.anchor_upper: float | None = None
        self.anchor_lower: float | None = None
        self.touches_upper = 0
        self.touches_lower = 0
        self.closes: deque[float] = deque(maxlen=config.d_min_bars)
        self._slope = _IncrementalSlope(maxlen=config.d_min_bars)   # NOU în 0.4.1 -- fix-ul §12
        self.n: int = 0
        self.pending_side: str | None = None
        self.pending_breach_idx: int | None = None
        self.pending_consec_outside: int = 0
        self.pending_zone_edge: float | None = None
        self.ended = False
        self.end_reason: str | None = None
        self.reached_established = False

    def add_swing(self, sw: _Swing) -> None:
        (self.highs if sw.is_high else self.lows).append(sw)
        (self._high_median if sw.is_high else self._low_median).add(sw.price)
        if self.structural_start_idx is None or sw.idx < self.structural_start_idx:
            self.structural_start_idx = sw.idx
            self.structural_start_ts = sw.ts

    def update_anchors(self) -> None:
        if len(self._high_median):
            self.anchor_upper = self._high_median.median()
        if len(self._low_median):
            self.anchor_lower = self._low_median.median()

    def geometry_valid(self, w: float) -> bool:
        if self.anchor_upper is None or self.anchor_lower is None:
            return False
        import math
        if not (math.isfinite(self.anchor_upper) and math.isfinite(self.anchor_lower)):
            return False
        if self.anchor_upper <= self.anchor_lower:
            return False
        return (self.anchor_upper - self.anchor_lower) > 2.0 * w

    def bars_in_segment(self, current_idx: int) -> int:
        if self.structural_start_idx is None:
            return 0
        return current_idx - self.structural_start_idx + 1

    def push_close(self, value: float) -> None:
        """Înlocuiește `self.closes.append(close)` direct (0.4.0) -- capturează valoarea evicted ÎNAINTE de
        append (deque-ul o elimină silențios), actualizează statisticile suficiente O(1), APOI adaugă."""
        evicted = self.closes[0] if len(self.closes) == self.closes.maxlen else None
        self._slope.push(value, evicted)
        self.closes.append(value)

    def slope(self) -> float:
        """O(1) -- vezi `_IncrementalSlope`. Fix-ul §12: 0.4.0 re-parcurgea `closes` complet aici."""
        return self._slope.slope()

    # ── snapshot / restore ──
    def snapshot(self) -> dict[str, Any]:
        return {
            "segment_id": self.segment_id, "predecessor_id": self.predecessor_id,
            "transition_reason": self.transition_reason, "lifecycle": self.lifecycle.value,
            "structural_start_idx": self.structural_start_idx, "structural_start_ts": self.structural_start_ts,
            "confirm_ts": self.confirm_ts, "was_confirmed": self.was_confirmed,
            "establishing_emitted": self.establishing_emitted,
            "highs": [[s.idx, s.price, s.is_high, s.ts] for s in self.highs],
            "lows": [[s.idx, s.price, s.is_high, s.ts] for s in self.lows],
            "anchor_upper": self.anchor_upper, "anchor_lower": self.anchor_lower,
            "touches_upper": self.touches_upper, "touches_lower": self.touches_lower,
            "closes": list(self.closes), "n": self.n,
            "slope_state": self._slope.snapshot(),   # NOU în 0.4.1
            "pending_side": self.pending_side, "pending_breach_idx": self.pending_breach_idx,
            "pending_consec_outside": self.pending_consec_outside, "pending_zone_edge": self.pending_zone_edge,
            "ended": self.ended, "end_reason": self.end_reason, "reached_established": self.reached_established,
        }

    @classmethod
    def restore(cls, st: dict[str, Any], config: RangeConfigV31) -> "_SegmentV31":
        seg = cls(segment_id=st["segment_id"], predecessor_id=st["predecessor_id"],
                  transition_reason=st["transition_reason"], config=config)
        seg.lifecycle = SegmentLifecycleV3(st["lifecycle"])
        seg.structural_start_idx = st["structural_start_idx"]; seg.structural_start_ts = st["structural_start_ts"]
        seg.confirm_ts = st["confirm_ts"]; seg.was_confirmed = st["was_confirmed"]
        seg.establishing_emitted = st["establishing_emitted"]
        seg.highs = [_Swing(a, b, c, d) for a, b, c, d in st["highs"]]
        seg.lows = [_Swing(a, b, c, d) for a, b, c, d in st["lows"]]
        for s in seg.highs:
            seg._high_median.add(s.price)
        for s in seg.lows:
            seg._low_median.add(s.price)
        seg.anchor_upper = st["anchor_upper"]; seg.anchor_lower = st["anchor_lower"]
        seg.touches_upper = st["touches_upper"]; seg.touches_lower = st["touches_lower"]
        seg.closes = deque(st["closes"], maxlen=config.d_min_bars); seg.n = st["n"]
        seg._slope = _IncrementalSlope.restore(st["slope_state"], config.d_min_bars)
        seg.pending_side = st["pending_side"]; seg.pending_breach_idx = st["pending_breach_idx"]
        seg.pending_consec_outside = st["pending_consec_outside"]; seg.pending_zone_edge = st["pending_zone_edge"]
        seg.ended = st["ended"]; seg.end_reason = st["end_reason"]; seg.reached_established = st["reached_established"]
        return seg


# ═══════════════════════════════════ producătorul incremental V3.1 ═══════════════════════════════════
class RangeSemanticProducerV31:
    """Copie CHIRURGICALĂ a `RangeSemanticProducerV3` (0.4.0, NEATINSĂ) — identică peste tot ÎN AFARA
    folosirii `_SegmentV31` (panta O(1)) și a apelului `seg.push_close(close)` (fostul `seg.closes.append`
    direct). Nicio schimbare de semantică de stare/eveniment/tranziție/reason-code."""

    def __init__(self, config: RangeConfigV31) -> None:
        self._cfg = config
        self._spec_id = config.range_spec_id()
        self._n = 0
        self._last_atr: float = 0.0
        self._last_close: float | None = None
        self._wh: deque[float] = deque(maxlen=2 * config.swing_k + 1)
        self._wl: deque[float] = deque(maxlen=2 * config.swing_k + 1)
        self._wts: deque[int] = deque(maxlen=2 * config.swing_k + 1)
        self._next_segment_id = 1
        self._active: _SegmentV31 | None = None
        self._last_ended_id: int | None = None
        self._last_ended_reason: str | None = None
        self._history: deque[ConfirmedSegmentRecordV3] = deque(maxlen=config.segment_history_limit)

    @property
    def history(self) -> tuple[ConfirmedSegmentRecordV3, ...]:
        return tuple(self._history)

    def _detect_confirmed_swing(self, i: int) -> _Swing | None:
        k = self._cfg.swing_k
        if len(self._wh) < 2 * k + 1:
            return None
        c = k
        ch = self._wh[c]; cl = self._wl[c]; idx = i - k; cts = self._wts[c]
        if all(ch > self._wh[j] for j in range(2 * k + 1) if j != c):
            return _Swing(idx=idx, price=ch, is_high=True, ts=cts)
        if all(cl < self._wl[j] for j in range(2 * k + 1) if j != c):
            return _Swing(idx=idx, price=cl, is_high=False, ts=cts)
        return None

    def _new_segment(self, predecessor_id: int | None, transition_reason: str | None) -> _SegmentV31:
        seg = _SegmentV31(segment_id=self._next_segment_id, predecessor_id=predecessor_id,
                          transition_reason=transition_reason, config=self._cfg)
        self._next_segment_id += 1
        return seg

    def _end_segment(self, seg: _SegmentV31, i: int, end_ts: int, end_reason: str) -> None:
        seg.ended = True; seg.end_reason = end_reason
        self._history.append(ConfirmedSegmentRecordV3(
            segment_id=seg.segment_id, predecessor_id=seg.predecessor_id, end_reason=end_reason,
            structural_start_ts=seg.structural_start_ts or end_ts, confirm_ts=seg.confirm_ts, end_ts=end_ts,
            bars_in_segment=seg.bars_in_segment(i), anchor_lower=seg.anchor_lower,
            anchor_upper=seg.anchor_upper, reached_established=seg.reached_established))
        self._last_ended_id = seg.segment_id
        self._last_ended_reason = end_reason
        self._active = None
        self._wh.clear(); self._wl.clear(); self._wts.clear()

    def observe(self, *, ts_close: int, open_: float, high: float, low: float,
                close: float, atr: float | None, trend_context: str | None
               ) -> tuple[RangeSemanticResultV3, list[RangeEventV3]]:
        cfg = self._cfg
        i = self._n
        self._n += 1
        self._wh.append(high); self._wl.append(low); self._wts.append(ts_close)
        self._last_atr = atr if atr is not None else 0.0
        self._last_close = close

        def unavailable(reason: str, *, segment_id: int | None = None, predecessor_id: int | None = None,
                        transition_reason: str | None = None, extra: list[RangeEventV3] | None = None
                       ) -> tuple[RangeSemanticResultV3, list[RangeEventV3]]:
            ev = self._mk_event(SegmentEventKindV3.UNAVAILABLE, ts_close, i, segment_id, None, (reason,), ())
            events_out = (extra or []) + [ev]
            return (RangeSemanticResultV3(available=False, reason=reason, range_spec_id=self._spec_id,
                                          bar_index=i, ts_close=ts_close, segment_id=segment_id,
                                          predecessor_id=predecessor_id, transition_reason=transition_reason,
                                          reason_codes=(reason,)), events_out)

        if atr is None:
            if i < cfg.atr_window or i < 2 * cfg.swing_k + 1:
                return unavailable(ATR_UNAVAILABLE)
            if self._active is not None:
                ended_id = self._active.segment_id
                ended_pred = self._active.predecessor_id
                ended_transition = self._active.transition_reason
                self._end_segment(self._active, i, ts_close, RANGE_FAILED_PRECONDITION)
                failed_ev = self._mk_event(SegmentEventKindV3.RANGE_FAILED, ts_close, i, ended_id, None,
                                           (RANGE_FAILED_PRECONDITION,), ())
                return unavailable(ATR_UNAVAILABLE, segment_id=ended_id, predecessor_id=ended_pred,
                                   transition_reason=ended_transition, extra=[failed_ev])
            return unavailable(ATR_UNAVAILABLE)

        sw = self._detect_confirmed_swing(i)

        if self._active is None:
            self._active = self._new_segment(self._last_ended_id, self._last_ended_reason)
            self._last_ended_id = None; self._last_ended_reason = None
        seg = self._active
        if sw is not None:
            seg.add_swing(sw)
        seg.n += 1
        if cfg.max_duration_bars is not None and seg.structural_start_idx is not None:
            if (i - seg.structural_start_idx + 1) > cfg.max_duration_bars:
                ended_id = seg.segment_id
                self._end_segment(seg, i, ts_close, RANGE_FAILED_PRECONDITION)
                res = RangeSemanticResultV3(available=True, reason=RANGE_FAILED_PRECONDITION,
                                            range_spec_id=self._spec_id,
                                            bar_index=i, ts_close=ts_close, segment_id=ended_id,
                                            predecessor_id=seg.predecessor_id,
                                            transition_reason=seg.transition_reason, trend_context=trend_context,
                                            confirmed_event=SegmentEventKindV3.RANGE_FAILED.value,
                                            reason_codes=(RANGE_FAILED_PRECONDITION,))
                return res, [self._mk_event(SegmentEventKindV3.RANGE_FAILED, ts_close, i, ended_id, None,
                                            (RANGE_FAILED_PRECONDITION,), ())]

        if not seg.highs or not seg.lows:
            res = RangeSemanticResultV3(
                available=True, reason=SegmentEventKindV3.TRANSITION.value, range_spec_id=self._spec_id,
                bar_index=i, ts_close=ts_close,
                segment_id=seg.segment_id, predecessor_id=seg.predecessor_id,
                transition_reason=seg.transition_reason, lifecycle=seg.lifecycle.value,
                structural_start_ts=seg.structural_start_ts, bars_in_segment=seg.bars_in_segment(i),
                trend_context=trend_context, confirmed_event=SegmentEventKindV3.TRANSITION.value,
                reason_codes=(ESTABLISHING_FEW_SWINGS,))
            return res, [self._mk_event(SegmentEventKindV3.TRANSITION, ts_close, i, seg.segment_id, None,
                                        (ESTABLISHING_FEW_SWINGS,), ())]

        seg.update_anchors()
        seg.push_close(close)   # <- singura schimbare de linie vs 0.4.0 (`seg.closes.append(close)`)
        events: list[RangeEventV3] = []
        assert seg.anchor_upper is not None and seg.anchor_lower is not None
        w = cfg.w_atr * self._last_atr

        if not seg.establishing_emitted:
            seg.establishing_emitted = True
            events.append(self._mk_event(SegmentEventKindV3.RANGE_ESTABLISHING, ts_close, i, seg.segment_id,
                                         None, (ESTABLISHING_FEW_SWINGS,), ()))

        if seg.lifecycle == SegmentLifecycleV3.BREACH_PENDING:
            self._resolve_pending(seg, i, ts_close, high, low, close, events)
        else:
            self._evaluate_active(seg, i, ts_close, high, low, close, w, events)

        confirmed = events[-1].kind if events else None
        pending = (f"BOUNDARY_BREACH_PENDING_{seg.pending_side.upper()}" if seg.pending_side else None)
        slope = seg.slope()
        reasons = self._reasons_for(seg, i, w)
        primary_reason = OK_RANGE if seg.lifecycle == SegmentLifecycleV3.ESTABLISHED else reasons[0]
        result = RangeSemanticResultV3(
            available=True, reason=primary_reason,
            range_spec_id=self._spec_id, bar_index=i, ts_close=ts_close,
            segment_id=seg.segment_id, predecessor_id=seg.predecessor_id, transition_reason=seg.transition_reason,
            lifecycle=seg.lifecycle.value, structural_start_ts=seg.structural_start_ts, confirm_ts=seg.confirm_ts,
            bars_in_segment=seg.bars_in_segment(i), anchor_lower=seg.anchor_lower, anchor_upper=seg.anchor_upper,
            range_mid=(seg.anchor_upper + seg.anchor_lower) / 2.0, w=w,
            touches_upper=seg.touches_upper, touches_lower=seg.touches_lower,
            pending_event=pending, confirmed_event=confirmed, slope=slope, trend_context=trend_context,
            reason_codes=reasons)
        return result, events

    def _reasons_for(self, seg: _SegmentV31, i: int, w: float) -> tuple[str, ...]:
        cfg = self._cfg
        reasons: list[str] = []
        if not seg.geometry_valid(w):
            reasons.append(ZONES_DEGENERATE)
        if seg.touches_upper < cfg.n_touch or seg.touches_lower < cfg.n_touch:
            reasons.append(FEW_TOUCHES)
        if seg.structural_start_idx is not None and seg.bars_in_segment(i) < cfg.d_min_bars:
            reasons.append(TOO_SHORT)
        drift = abs(seg.slope()) * cfg.d_min_bars
        if drift > cfg.s_max * self._last_atr:
            reasons.append(IS_CHANNEL)
        if seg.lifecycle == SegmentLifecycleV3.ESTABLISHED:
            reasons.append(OK_RANGE)
        elif not reasons:
            reasons.append(RANGE_FORMING)
        return tuple(reasons)

    def _touch_zone(self, lo_bar: float, hi_bar: float, anchor: float, w: float) -> bool:
        return hi_bar >= anchor - w and lo_bar <= anchor + w

    def _evaluate_active(self, seg: _SegmentV31, i: int, ts: int, high: float, low: float, close: float,
                         w: float, events: list[RangeEventV3]) -> None:
        cfg = self._cfg
        assert seg.anchor_upper is not None and seg.anchor_lower is not None
        anchor_upper: float = seg.anchor_upper
        anchor_lower: float = seg.anchor_lower

        if seg.lifecycle != SegmentLifecycleV3.ESTABLISHED and seg.bars_in_segment(i) >= cfg.d_min_bars:
            slope = seg.slope()
            drift = abs(slope) * cfg.d_min_bars
            if drift > cfg.s_max * self._last_atr:
                kind = SegmentEventKindV3.CHANNEL_UP if slope > 0 else SegmentEventKindV3.CHANNEL_DOWN
                events.append(self._mk_event(kind, ts, i, seg.segment_id, None, (IS_CHANNEL,), ()))
                self._end_segment(seg, i, ts, IS_CHANNEL)
                return

        upper_edge = anchor_upper + w
        lower_edge = anchor_lower - w
        touched_upper = self._touch_zone(low, high, anchor_upper, w)
        touched_lower = self._touch_zone(low, high, anchor_lower, w)
        if touched_upper:
            seg.touches_upper += 1
        if touched_lower:
            seg.touches_lower += 1

        if high > upper_edge or low < lower_edge:
            side = 'upper' if high > upper_edge else 'lower'
            edge = upper_edge if side == 'upper' else lower_edge
            seg.lifecycle = SegmentLifecycleV3.BREACH_PENDING
            seg.pending_side = side; seg.pending_breach_idx = i; seg.pending_zone_edge = edge
            seg.pending_consec_outside = 0
            self._resolve_pending(seg, i, ts, high, low, close, events)
            return

        if touched_upper:
            events.append(self._mk_event(SegmentEventKindV3.BOUNDARY_TEST_UPPER, ts, i, seg.segment_id,
                                         'upper', (OK_RANGE,), ()))
        elif touched_lower:
            events.append(self._mk_event(SegmentEventKindV3.BOUNDARY_TEST_LOWER, ts, i, seg.segment_id,
                                         'lower', (OK_RANGE,), ()))
        else:
            events.append(self._mk_event(SegmentEventKindV3.RANGE_MID, ts, i, seg.segment_id, None, (OK_RANGE,), ()))

        self._confirm_establish(seg, i, ts, w, events)

    def _confirm_establish(self, seg: _SegmentV31, i: int, ts: int, w: float, events: list[RangeEventV3]) -> None:
        cfg = self._cfg
        if not seg.geometry_valid(w):
            return
        confirmed_now = seg.touches_upper >= cfg.n_touch and seg.touches_lower >= cfg.n_touch
        if confirmed_now and not seg.was_confirmed:
            seg.was_confirmed = True
            seg.confirm_ts = ts
        if not seg.was_confirmed:
            return
        bars = seg.bars_in_segment(i)
        if bars < cfg.d_min_bars:
            return
        drift = abs(seg.slope()) * cfg.d_min_bars
        if drift > cfg.s_max * self._last_atr:
            return
        if seg.lifecycle != SegmentLifecycleV3.ESTABLISHED:
            seg.lifecycle = SegmentLifecycleV3.ESTABLISHED
            seg.reached_established = True
            events.append(self._mk_event(SegmentEventKindV3.RANGE_ESTABLISHED, ts, i, seg.segment_id, None,
                                         (OK_RANGE,), ()))

    def _resolve_pending(self, seg: _SegmentV31, i: int, ts: int, high: float, low: float, close: float,
                         events: list[RangeEventV3]) -> None:
        cfg = self._cfg
        assert seg.pending_zone_edge is not None and seg.pending_side is not None
        edge = seg.pending_zone_edge
        side = seg.pending_side
        back_inside = (close <= edge) if side == 'upper' else (close >= edge)
        seg.pending_consec_outside += 1
        bars_pending = seg.pending_consec_outside

        if back_inside:
            if bars_pending <= cfg.K:
                kind = (SegmentEventKindV3.LIQUIDITY_SWEEP_UP if side == 'upper'
                       else SegmentEventKindV3.LIQUIDITY_SWEEP_DOWN)
                events.append(self._mk_event(kind, ts, i, seg.segment_id, side, (OK_RANGE,), ()))
            else:
                events.append(self._mk_event(SegmentEventKindV3.TRANSITION, ts, i, seg.segment_id, side,
                                             (SWEEP_WINDOW_EXPIRED,), ()))
            seg.lifecycle = SegmentLifecycleV3.ESTABLISHED if seg.reached_established else SegmentLifecycleV3.ESTABLISHING
            seg.pending_side = None; seg.pending_breach_idx = None
            seg.pending_consec_outside = 0; seg.pending_zone_edge = None
            return

        if bars_pending >= cfg.N:
            kind = (SegmentEventKindV3.BREAKOUT_ACCEPTANCE_UP if side == 'upper'
                   else SegmentEventKindV3.BREAKOUT_ACCEPTANCE_DOWN)
            events.append(self._mk_event(kind, ts, i, seg.segment_id, side, (TERMINATED_BY_BREAKOUT,), ()))
            self._end_segment(seg, i, ts, TERMINATED_BY_BREAKOUT)
            return
        events.append(self._mk_event(SegmentEventKindV3.TRANSITION, ts, i, seg.segment_id, side,
                                     (BETWEEN_SEGMENTS,), (NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT,)))

    def _mk_event(self, kind: SegmentEventKindV3, ts: int, i: int, segment_id: int | None, boundary: str | None,
                 reasons: tuple[str, ...], nya: tuple[str, ...]) -> RangeEventV3:
        guard = SAFETY_GUARD_RANGE_MID_NO_ENTRY if kind is SegmentEventKindV3.RANGE_MID else None
        return RangeEventV3(kind=kind.value, confirm_ts=ts, bar_index=i, segment_id=segment_id, boundary=boundary,
                            reason_codes=reasons, not_yet_available=nya,
                            event_contract_version=RANGE_EVENT_CONTRACT_VERSION_V3, range_spec_id=self._spec_id,
                            safety_guard=guard)

    # ── snapshot / restore integral ──
    def snapshot_state(self) -> dict[str, Any]:
        return {
            "n": self._n, "wh": list(self._wh), "wl": list(self._wl), "wts": list(self._wts),
            "last_atr": self._last_atr, "last_close": self._last_close,
            "next_segment_id": self._next_segment_id,
            "active": (self._active.snapshot() if self._active is not None else None),
            "last_ended_id": self._last_ended_id, "last_ended_reason": self._last_ended_reason,
            "history": [
                {"segment_id": r.segment_id, "predecessor_id": r.predecessor_id, "end_reason": r.end_reason,
                 "structural_start_ts": r.structural_start_ts, "confirm_ts": r.confirm_ts, "end_ts": r.end_ts,
                 "bars_in_segment": r.bars_in_segment, "anchor_lower": r.anchor_lower,
                 "anchor_upper": r.anchor_upper, "reached_established": r.reached_established}
                for r in self._history],
        }

    def restore_state(self, st: dict[str, Any]) -> None:
        k = self._cfg.swing_k
        self._n = st["n"]
        self._wh = deque(st["wh"], maxlen=2 * k + 1); self._wl = deque(st["wl"], maxlen=2 * k + 1)
        self._wts = deque(st["wts"], maxlen=2 * k + 1)
        self._last_atr = st["last_atr"]; self._last_close = st["last_close"]
        self._next_segment_id = st["next_segment_id"]
        self._active = _SegmentV31.restore(st["active"], self._cfg) if st["active"] is not None else None
        self._last_ended_id = st["last_ended_id"]; self._last_ended_reason = st["last_ended_reason"]
        self._history = deque(
            (ConfirmedSegmentRecordV3(**r) for r in st["history"]), maxlen=self._cfg.segment_history_limit)
