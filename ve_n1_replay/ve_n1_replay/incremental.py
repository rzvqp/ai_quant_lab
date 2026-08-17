"""Motor N1 replay INCREMENTAL — O(n)/bounded-amortized, byte-echivalent cu 0.1.0.

Cauza O(n²) din 0.1.0: `RawAxesBuilder.observe` re-rulează detect_swings/detect_breaks/expansion/compression peste
tot istoricul la fiecare bară. Aici:
- **expansion/compression** (mărginite, lookback ≤ HISTORY_HORIZON=460): apelate pe un BUFFER RULANT de 460 bare cu
  funcțiile RATIFICATE NEMODIFICATE ⇒ byte-identic (dovada de orizont: N1_INCREMENTAL_HORIZON.md).
- **structure/direction** (NELIMITATE — ultimul swing neconsumat poate fi arbitrar de vechi): STARE INCREMENTALĂ
  suficientă care reia EXACT logica ratificată detect_swings/label_structure/detect_breaks O(1) amortizat/bară
  (fractali k=2, tie-break strict, ordine bull-înainte-de-bear, re-armare din swing-uri neconsumate, ultimul break).
  NU trunchiere. Echivalența e demonstrată prin paritate exhaustivă (inclusiv swing >5000 bare vechime).

`N1IncrementalReplayEngine` moștenește `N1ReplayEngine` (guards, `_build_result`, identitate, snapshot/restore) și
înlocuiește DOAR `_axes_builder` ⇒ toate câmpurile de rezultat/fingerprint/identitate = 0.1.0 prin construcție.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Sequence
from typing import Any

import ve_brain  # type: ignore[import-untyped]  # extern, instalat separat

from ._bootstrap import vendored_module
from .version import (
    HISTORY_HORIZON, HISTORY_HORIZON_VERSION, LEDGER_SCHEMA_VERSION,
    INCREMENTAL_SNAPSHOT_SCHEMA_VERSION, VE_N1_REPLAY_VERSION,
)

_K: int = 2                                # fractal k (K_DEFAULT în market_structure)

_BREAK_KIND_TO_STRUCTURE_DIRECTION: dict[str, tuple[str, str]] = {
    "bos_bull": ("strong", "up"), "bos_bear": ("strong", "down"),
    "choch_bull": ("weak", "weak_up"), "choch_bear": ("weak", "weak_down"),
}


class _Swing:
    __slots__ = ("idx", "price", "kind", "label")

    def __init__(self, idx: int, price: float, kind: str, label: str) -> None:
        self.idx = idx; self.price = price; self.kind = kind; self.label = label


class IncrementalRawAxesBuilder:
    """Interfață identică cu `RawAxesBuilder` (`.observe(bar) -> ve_brain.RawAxes`, `.symbol`, `.bars_observed`,
    `.last_close`, `.atr14()`), dar O(1)/mărginit amortizat prin stare incrementală + buffer rulant."""

    def __init__(self, symbol: str, *, horizon: int = HISTORY_HORIZON) -> None:
        self._symbol = symbol
        self._horizon = horizon
        self._ve_brain: Any = ve_brain
        self._ms: Any = vendored_module("market_state")
        # buffer rulant pentru expansion/compression (ultimele `horizon` bare) — funcții ratificate NEMODIFICATE
        self._bo: deque[float] = deque(maxlen=horizon)
        self._bh: deque[float] = deque(maxlen=horizon)
        self._bl: deque[float] = deque(maxlen=horizon)
        self._bc: deque[float] = deque(maxlen=horizon)
        # fereastră mică pentru detecția fractalilor (2k+1 bare)
        self._wh: deque[float] = deque(maxlen=2 * _K + 1)
        self._wl: deque[float] = deque(maxlen=2 * _K + 1)
        self._n: int = 0
        # stare structură/direcție (NELIMITATĂ, NU trunchiată)
        self._last_high: _Swing | None = None
        self._last_low: _Swing | None = None
        self._stack: dict[str, list[_Swing]] = {"HH": [], "LL": [], "HL": [], "LH": []}
        self._consumed: set[int] = set()
        self._pending: _Swing | None = None        # swing detectat la bara precedentă (confirmed_idx = n-1)
        self._latest_break_kind: str | None = None

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def bars_observed(self) -> int:
        return self._n

    @property
    def last_close(self) -> float | None:
        return self._bc[-1] if self._bc else None

    @property
    def latest_break_kind(self) -> str | None:
        return self._latest_break_kind

    def live_labels(self) -> dict[str, int | None]:
        """live_hh/ll/hl/lh = idx-ul ultimului swing NECONSUMAT de fiecare etichetă (pentru paritate intermediară)."""
        return {lab: (s.idx if (s := self._top(lab)) is not None else None) for lab in ("HH", "LL", "HL", "LH")}

    def consumed_idx(self) -> set[int]:
        return set(self._consumed)

    def _pending_labeled(self) -> tuple[int, str, float] | None:
        """Swingul din `_pending` (confirmed_idx = bara curentă) cu eticheta pe care o va primi la stacking,
        calculată vs `_last_high/_last_low` curente (identic cu label_structure). None dacă UNCLASSIFIED."""
        s = self._pending
        if s is None:
            return None
        if s.kind == "high":
            if self._last_high is None:
                return None
            lab = "HH" if s.price > self._last_high.price else "LH"
        else:
            if self._last_low is None:
                return None
            lab = "HL" if s.price > self._last_low.price else "LL"
        return (s.idx, lab, s.price)

    def confirmed_unconsumed(self) -> dict[int, tuple[str, float]]:
        """Swing-uri confirmate (confirmed_idx <= bara curentă) NECONSUMATE, incl. pending-ul tocmai confirmat
        la bara curentă — vederea 'gata pentru decizia de la bara următoare' (paritate de stare intermediară)."""
        out: dict[int, tuple[str, float]] = {}
        for lab in ("HH", "LL", "HL", "LH"):
            for s in self._stack[lab]:
                if s.idx not in self._consumed:
                    out[s.idx] = (lab, s.price)
        p = self._pending_labeled()
        if p is not None:
            out[p[0]] = (p[1], p[2])          # pending are idx maxim ⇒ nu poate fi consumat la bara curentă
        return out

    def live_labels_next(self) -> dict[str, int | None]:
        """live_hh/ll/hl/lh pentru decizia de la bara URMĂTOARE (incl. pending-ul tocmai confirmat, care are
        idx maxim ⇒ devine live pentru eticheta lui)."""
        live: dict[str, int | None] = dict(self.live_labels())
        p = self._pending_labeled()
        if p is not None:
            live[p[1]] = p[0]
        return live

    def atr14(self) -> float | None:
        if not self._bc:
            return None
        v = self._ms.atr14(list(self._bh), list(self._bl), list(self._bc))
        last = v[-1]
        return last if last == last else None

    def _top(self, label: str) -> _Swing | None:
        st = self._stack[label]
        while st and st[-1].idx in self._consumed:
            st.pop()
        return st[-1] if st else None

    def _label_and_stack_pending(self) -> None:
        """Adaugă în stive swingul devenit CONFIRMAT (confirmed_idx < bara curentă). Etichetare în ordine de idx."""
        s = self._pending
        self._pending = None
        if s is None:
            return
        if s.kind == "high":
            prev = self._last_high
            s.label = "UNCLASSIFIED" if prev is None else ("HH" if s.price > prev.price else "LH")
            self._last_high = s
        else:
            prev = self._last_low
            s.label = "UNCLASSIFIED" if prev is None else ("HL" if s.price > prev.price else "LL")
            self._last_low = s
        if s.label in self._stack:                 # UNCLASSIFIED nu poate fi referință de break
            self._stack[s.label].append(s)

    def _detect_new_swing(self, i: int) -> None:
        """Detectează swingul (fractal k) la idx = i-K (fereastra [i-2K, i]). Strict pe ambele laturi (D2)."""
        if len(self._wh) < 2 * _K + 1:
            return
        c = _K                                     # centrul ferestrei în deque
        ch = self._wh[c]; cl = self._wl[c]
        is_high = all(ch > self._wh[j] for j in range(2 * _K + 1) if j != c)
        if is_high:
            self._pending = _Swing(idx=i - _K, price=ch, kind="high", label="UNCLASSIFIED")
            return
        is_low = all(cl < self._wl[j] for j in range(2 * _K + 1) if j != c)
        if is_low:
            self._pending = _Swing(idx=i - _K, price=cl, kind="low", label="UNCLASSIFIED")

    def observe(self, bar: Any) -> Any:
        if bar.symbol != self._symbol:
            raise ValueError(f"IncrementalRawAxesBuilder for {self._symbol!r} received a bar for {bar.symbol!r}")
        i = self._n                                # index 0-based al barei curente
        self._bo.append(bar.open); self._bh.append(bar.high); self._bl.append(bar.low); self._bc.append(bar.close)
        self._wh.append(bar.high); self._wl.append(bar.low)
        self._n += 1

        # (1) swingul detectat la bara i-1 (confirmed_idx = i-1 < i) devine utilizabil ⇒ etichetează + push
        self._label_and_stack_pending()

        # (2) rupturi la bara i (replică EXACT ordinea detect_breaks: bull hh elif lh; bear ll elif hl)
        px = bar.close
        hh = self._top("HH"); lh = self._top("LH"); ll = self._top("LL"); hl = self._top("HL")
        bull: str | None = None
        if hh is not None and px > hh.price:
            bull = "bos_bull"; self._consumed.add(hh.idx)
        elif lh is not None and px > lh.price:
            bull = "choch_bull"; self._consumed.add(lh.idx)
        bear: str | None = None
        if ll is not None and px < ll.price:
            bear = "bos_bear"; self._consumed.add(ll.idx)
        elif hl is not None and px < hl.price:
            bear = "choch_bear"; self._consumed.add(hl.idx)
        # _structure_and_direction = max(breaks, key=idx); la egalitate de idx (aceeași bară) câștigă bull (append primul)
        if bull is not None:
            self._latest_break_kind = bull
        elif bear is not None:
            self._latest_break_kind = bear

        # (3) detectează swingul la idx = i-K (confirmed_idx = i, utilizabil la bara următoare)
        self._detect_new_swing(i)

        # (4) axele mărginite din buffer-ul rulant (funcții RATIFICATE nemodificate)
        exp = self._ms.expansion(list(self._bo), list(self._bh), list(self._bl), list(self._bc))
        comp, valid = self._ms.compression(list(self._bh), list(self._bl))
        is_displacement = bool(exp[-1])
        is_compressed = bool(comp[-1]) if valid[-1] else None

        if self._latest_break_kind is None:
            structure, direction = None, None
        else:
            structure, direction = _BREAK_KIND_TO_STRUCTURE_DIRECTION.get(self._latest_break_kind, (None, None))

        return self._ve_brain.RawAxes(
            is_compressed=is_compressed, is_displacement=is_displacement, direction=direction, structure=structure)

    # ── stare pentru snapshot INCREMENTAL (mărginit: buffer + stive neconsumate + watermark) ──
    def snapshot_state(self) -> dict[str, Any]:
        return {
            "horizon": self._horizon, "n": self._n,
            "bo": list(self._bo), "bh": list(self._bh), "bl": list(self._bl), "bc": list(self._bc),
            "wh": list(self._wh), "wl": list(self._wl),
            "last_high": _swing_to(self._last_high), "last_low": _swing_to(self._last_low),
            "stack": {k: [_swing_to(s) for s in v] for k, v in self._stack.items()},
            "consumed": sorted(self._consumed), "pending": _swing_to(self._pending),
            "latest_break_kind": self._latest_break_kind,
        }

    def restore_state(self, st: dict[str, Any]) -> None:
        self._horizon = st["horizon"]; self._n = st["n"]
        self._bo = deque(st["bo"], maxlen=self._horizon); self._bh = deque(st["bh"], maxlen=self._horizon)
        self._bl = deque(st["bl"], maxlen=self._horizon); self._bc = deque(st["bc"], maxlen=self._horizon)
        self._wh = deque(st["wh"], maxlen=2 * _K + 1); self._wl = deque(st["wl"], maxlen=2 * _K + 1)
        self._last_high = _swing_from(st["last_high"]); self._last_low = _swing_from(st["last_low"])
        self._stack = {k: [x for s in v if (x := _swing_from(s)) is not None]
                       for k, v in st["stack"].items()}
        self._consumed = set(st["consumed"]); self._pending = _swing_from(st["pending"])
        self._latest_break_kind = st["latest_break_kind"]


def _swing_to(s: _Swing | None) -> list[Any] | None:
    return None if s is None else [s.idx, s.price, s.kind, s.label]


def _swing_from(v: list[Any] | None) -> _Swing | None:
    return None if v is None else _Swing(idx=v[0], price=v[1], kind=v[2], label=v[3])


# ═══════════════════════════════════════════════════════════════════════════════════════════════════
#  Motorul incremental + ledger canonic (precompute-once) — moștenește N1ReplayEngine, schimbă DOAR
#  builder-ul de axe și snapshot/restore (mărginit). Toate guard-urile / _build_result / identitatea
#  rămân vendate ⇒ per-bară rezultatul e byte-identic cu 0.1.0 (dovedit prin paritate exhaustivă).
# ═══════════════════════════════════════════════════════════════════════════════════════════════════

import dataclasses as _dc

_engine_mod: Any = vendored_module("ai_trader.n1_replay.engine")
_identity_mod: Any = vendored_module("ai_trader.n1_replay.identity")
N1ReplayEngine: Any = _engine_mod.N1ReplayEngine
_Bar: Any = vendored_module("ai_trader.live_signal_source.types").Bar


def _bar_parts(bar: Any) -> tuple[str, ...]:
    """Identitate de conținut per-bară (OHLCV + timp) — feed pentru bars_content_hash."""
    vals = (bar.ts_open, bar.ts_close, bar.open, bar.high, bar.low, bar.close, bar.volume)
    return tuple(repr(v) for v in vals)


@_dc.dataclass(frozen=True, slots=True, kw_only=True)
class N1IncrementalLedgerRecord:
    """Un rând canonic N1 per bară închisă — read-only pentru cele 355 de ipoteze. Primitive serializabile."""
    bar_index: int
    ts_open: int
    ts_close: int
    is_compressed: bool | None
    is_displacement: bool
    direction: str | None
    structure: str | None
    availability_status: str
    regime_axes_status: tuple[str, ...]
    applicable_regimes: tuple[str, ...]
    reason_codes: tuple[str, ...]
    input_data_identity: str
    n1_output_fingerprint: str
    router_output_fingerprint: str
    output_fingerprint: str
    latest_break_kind: str | None            # stare intermediară auditabilă (structure/direction origin)

    def as_dict(self) -> dict[str, Any]:
        return _dc.asdict(self)


@_dc.dataclass(frozen=True, slots=True, kw_only=True)
class N1IncrementalLedger:
    """Ledger-ul canonic N1 pentru un dataset — calculat O(1) DATĂ, apoi doar citit.

    `ledger_key` este cheia de invalidare fail-closed: orice schimbare de identitate a evaluării
    (dataset, wheel-uri, detector fingerprint, contract N1, Router, orizont/incremental, ultima bară)
    schimbă cheia ⇒ un cache purtând altă cheie NU poate fi refolosit (identitate ≠ ⇒ recompute)."""
    ledger_key: str
    evaluation_identity_fingerprint: str
    history_horizon: int
    history_horizon_version: str
    ledger_schema_version: str
    ve_n1_replay_version: str
    data_identity: str
    bar_count: int
    last_closed_bar_id: str
    records: tuple[N1IncrementalLedgerRecord, ...]

    def header(self) -> dict[str, Any]:
        return {
            "ledger_key": self.ledger_key,
            "evaluation_identity_fingerprint": self.evaluation_identity_fingerprint,
            "history_horizon": self.history_horizon,
            "history_horizon_version": self.history_horizon_version,
            "ledger_schema_version": self.ledger_schema_version,
            "ve_n1_replay_version": self.ve_n1_replay_version,
            "data_identity": self.data_identity,
            "bar_count": self.bar_count,
            "last_closed_bar_id": self.last_closed_bar_id,
        }


@_dc.dataclass(frozen=True, slots=True, kw_only=True)
class N1IncrementalSnapshot:
    """Snapshot MĂRGINIT: doar starea incrementală a builder-ului + ultima bară + cursor + ultimul
    rezultat — NU întregul istoric. Restore este O(HISTORY_HORIZON), nu O(n). Identitatea trebuie să se
    potrivească (fail-closed) exact ca la snapshot-ul de bază."""
    identity_fingerprint: str
    snapshot_schema_version: str
    history_horizon: int
    history_horizon_version: str
    bars_observed: int
    builder_state: dict[str, Any]
    last_bar_parts: tuple[Any, ...] | None
    last_result: Any


class N1IncrementalReplayEngine(N1ReplayEngine):  # type: ignore[misc]  # baza e vendată (Any) prin bootstrap
    """`N1ReplayEngine` cu builder incremental (O(1)/mărginit amortizat pe bară) + snapshot/restore
    mărginit + `replay_batch` (ledger canonic). Rezultatul per-bară = 0.1.0 prin construcție."""

    def __init__(self, *, symbol: str, timeframe: str, bar_interval_seconds: int,
                 implementation_commit: str, horizon: int = HISTORY_HORIZON, **kwargs: Any) -> None:
        super().__init__(symbol=symbol, timeframe=timeframe, bar_interval_seconds=bar_interval_seconds,
                         implementation_commit=implementation_commit, **kwargs)
        self._axes_builder = IncrementalRawAxesBuilder(symbol, horizon=horizon)
        self._horizon = horizon

    @property
    def bars_observed(self) -> int:                      # sursă de adevăr = builder-ul (robust după restore mărginit)
        return self._axes_builder.bars_observed

    @property
    def latest_break_kind(self) -> str | None:
        return self._axes_builder.latest_break_kind

    # ── snapshot/restore INCREMENTAL (mărginit) ──
    def snapshot(self) -> Any:
        last = self._observed_bars[-1] if self._observed_bars else None
        return N1IncrementalSnapshot(
            identity_fingerprint=self._identity.fingerprint(),
            snapshot_schema_version=INCREMENTAL_SNAPSHOT_SCHEMA_VERSION,
            history_horizon=self._horizon, history_horizon_version=HISTORY_HORIZON_VERSION,
            bars_observed=self._axes_builder.bars_observed,
            builder_state=self._axes_builder.snapshot_state(),
            last_bar_parts=None if last is None else _bar_parts(last),
            last_result=self._last_result,
        )

    def restore(self, snapshot: Any) -> None:
        errors = vendored_module("ai_trader.n1_replay.errors")
        if not isinstance(snapshot, N1IncrementalSnapshot):
            raise errors.IncompatibleSnapshotError("snapshot nu este N1IncrementalSnapshot")
        if snapshot.identity_fingerprint != self._identity.fingerprint():
            raise errors.IncompatibleSnapshotError(
                f"snapshot identity {snapshot.identity_fingerprint!r} != engine {self._identity.fingerprint()!r}")
        if (snapshot.history_horizon != self._horizon
                or snapshot.history_horizon_version != HISTORY_HORIZON_VERSION):
            raise errors.IncompatibleSnapshotError("orizont de istoric incompatibil")
        b = IncrementalRawAxesBuilder(self._symbol, horizon=self._horizon)
        b.restore_state(snapshot.builder_state)
        self._axes_builder = b
        # păstrăm DOAR ultima bară (guard-urile de ordine/duplicat au nevoie de ea); cursorul real = builder-ul
        if snapshot.last_bar_parts is None:
            self._observed_bars = []
        else:
            p = snapshot.last_bar_parts
            self._observed_bars = [_Bar(symbol=self._symbol, ts_open=int(p[0]), ts_close=int(p[1]),
                                        open=float(p[2]), high=float(p[3]), low=float(p[4]), close=float(p[5]),
                                        volume=None if p[6] in (None, "None") else float(p[6]))]
        self._last_result = snapshot.last_result

    def reset(self) -> None:
        self._axes_builder = IncrementalRawAxesBuilder(self._symbol, horizon=self._horizon)
        self._observed_bars = []
        self._last_result = None

    # ── precompute-once: ledger canonic dintr-o SINGURĂ trecere O(n) ──
    def replay_batch(self, bars: Sequence[Any], *, as_of: int | None = None) -> N1IncrementalLedger:
        """O trecere forward unică peste `bars` ⇒ ledger canonic read-only (355 ipoteze). Refuză
        (prin `observe_closed_bar`) bare neordonate / din viitor / duplicat-conflictuale."""
        records: list[N1IncrementalLedgerRecord] = []
        for bar in bars:
            base_i = self._axes_builder.bars_observed
            res = self.observe_closed_bar(bar, as_of=as_of)
            axes = res.raw_axes
            records.append(N1IncrementalLedgerRecord(
                bar_index=base_i, ts_open=bar.ts_open, ts_close=bar.ts_close,
                is_compressed=axes.is_compressed, is_displacement=axes.is_displacement,
                direction=axes.direction, structure=axes.structure,
                availability_status=res.availability_status,
                regime_axes_status=tuple(res.regime_axes_status),
                applicable_regimes=tuple(sorted(res.applicable_regimes)),
                reason_codes=tuple(res.reason_codes),
                input_data_identity=res.input_data_identity,
                n1_output_fingerprint=res.n1_output_fingerprint,
                router_output_fingerprint=res.router_output_fingerprint,
                output_fingerprint=res.output_fingerprint,
                latest_break_kind=self._axes_builder.latest_break_kind,
            ))
        data_identity = _identity_mod.bars_content_hash(tuple(bars), bar_to_parts=_bar_parts)
        last_id = records[-1].input_data_identity if records else ""
        ledger_key = _identity_mod._fp(
            self._identity.fingerprint(), HISTORY_HORIZON_VERSION, str(self._horizon),
            LEDGER_SCHEMA_VERSION, VE_N1_REPLAY_VERSION, data_identity, str(len(records)), last_id,
        )
        return N1IncrementalLedger(
            ledger_key=ledger_key, evaluation_identity_fingerprint=self._identity.fingerprint(),
            history_horizon=self._horizon, history_horizon_version=HISTORY_HORIZON_VERSION,
            ledger_schema_version=LEDGER_SCHEMA_VERSION, ve_n1_replay_version=VE_N1_REPLAY_VERSION,
            data_identity=data_identity, bar_count=len(records), last_closed_bar_id=last_id,
            records=tuple(records),
        )
