"""RangeStateReplayEngine (0.2.0) — compune motorul N1 BYTE-IDENTIC (0.1.1) cu producătorul ADITIV RANGE_STATE.

- N1 rămâne NEATINS: `N1IncrementalReplayEngine` produce exact aceleași rezultate ca 0.1.1 (output_fingerprint
  byte-identic). RANGE_STATE e un STRAT separat care consumă doar bare închise + ATR cauzal + swing-uri confirmate.
- Precedență (Partea D): `RANGE_STATE_OVER_TREND_PAUSE`. Direcția N1 (up/down) devine `trend_context` — un ATRIBUT
  păstrat, nu o etichetă concurentă. TREND_PAUSE ⊆ RANGE_STATE ⇒ taxonomia NU e o partiție.
- `replay_batch` ⇒ ledger canonic RANGE read-only, cheiat pe `run_hash` (config_hash ‖ data_identity ‖ range_spec_id).
- Snapshot/restore COMBINAT, mărginit: snapshot-ul N1 incremental + starea RANGE, restaurabile bit-identic; fail-closed
  la nepotrivire de identitate.
"""
from __future__ import annotations

import dataclasses as _dc
from collections import Counter
from typing import Any

from .incremental import N1IncrementalReplayEngine, _bar_parts, _identity_mod
from .range_state import (
    RangeConfig, RangeStateProducer, RangeStateResult, RangeEvent, RangeEventKind,
    SAFETY_GUARD_RANGE_MID_NO_ENTRY, SAFETY_GUARDS_REGISTER, entry_decision, EntryDecision,
)
from .version import (
    RANGE_LEDGER_SCHEMA_VERSION, RANGE_SNAPSHOT_SCHEMA_VERSION, RANGE_STATE_CONTRACT_VERSION,
    RANGE_EVENT_CONTRACT_VERSION, PKG_N1_CONTRACT_VERSION, PKG_RAW_AXIS_SCHEMA_VERSION, PKG_ROUTER_VERSION,
    VE_N1_REPLAY_VERSION,
)


def _trend_context(direction: str | None) -> str | None:
    """Direcția N1 (byte-identică) devine contextul de trend păstrat sub precedența RANGE_STATE_OVER_TREND_PAUSE."""
    return direction  # up / weak_up / down / weak_down / None(UNCERTAIN)


@_dc.dataclass(frozen=True, slots=True)
class RangeReplayRecord:
    """Un rând de ledger RANGE per bară — include amprenta N1 (dovada byte-identității) + starea RANGE + evenimente."""
    bar_index: int
    ts_close: int
    n1_output_fingerprint: str            # din rezultatul N1 byte-identic (probează neatingerea N1)
    n1_direction: str | None
    n1_structure: str | None
    range_available: bool
    range_reason: str
    consolidation_state: str | None
    boundary_validity: str | None
    upper: float | None
    lower: float | None
    actionable_start_ts: int | None
    structural_start_ts: int | None
    trend_context: str | None
    invalidation: str | None
    range_reason_codes: tuple[str, ...]
    events: tuple[dict[str, Any], ...]
    safety_guard: str | None              # F7 RANGE_MID_NO_ENTRY marcat explicit dacă a apărut pe bară

    def as_dict(self) -> dict[str, Any]:
        return _dc.asdict(self)


@_dc.dataclass(frozen=True, slots=True)
class RangeLedger:
    run_hash: str
    range_spec_id: str
    config_hash: str
    data_identity: str
    n1_evaluation_identity_fingerprint: str
    range_state_contract_version: str
    range_event_contract_version: str
    pkg_n1_contract_version: str
    pkg_raw_axis_schema_version: str
    pkg_router_version: str
    range_ledger_schema_version: str
    ve_n1_replay_version: str
    bar_count: int
    n_guards: int                                   # contor SEPARAT F7 (SAFETY_GUARDS) — nu atinge niciun prag
    occupancy: dict[str, int]                       # matrice de ocupanță: consolidation_state + fiecare eveniment
    records: tuple[RangeReplayRecord, ...]

    def header(self) -> dict[str, Any]:
        d = {k: getattr(self, k) for k in (
            "run_hash", "range_spec_id", "config_hash", "data_identity",
            "n1_evaluation_identity_fingerprint", "range_state_contract_version", "range_event_contract_version",
            "pkg_n1_contract_version", "pkg_raw_axis_schema_version", "pkg_router_version",
            "range_ledger_schema_version", "ve_n1_replay_version", "bar_count", "n_guards")}
        d["occupancy"] = dict(self.occupancy)
        d["safety_guards_register"] = list(SAFETY_GUARDS_REGISTER)
        return d


@_dc.dataclass(frozen=True, slots=True)
class RangeSnapshot:
    """Snapshot COMBINAT mărginit: N1 incremental (bounded) + starea producătorului RANGE + identitate."""
    range_snapshot_schema_version: str
    n1_identity_fingerprint: str
    range_spec_id: str
    config_hash: str
    n1_snapshot: Any
    range_state: dict[str, Any]


class RangeSnapshotError(Exception):
    """Nepotrivire de identitate / versiune / range_spec_id la restore — fail-closed."""


class RangeStateReplayEngine:
    def __init__(self, *, symbol: str, timeframe: str, bar_interval_seconds: int,
                 implementation_commit: str, range_config: RangeConfig | None = None, **kwargs: Any) -> None:
        self._n1 = N1IncrementalReplayEngine(
            symbol=symbol, timeframe=timeframe, bar_interval_seconds=bar_interval_seconds,
            implementation_commit=implementation_commit, **kwargs)
        self._cfg = range_config if range_config is not None else RangeConfig(timeframe=timeframe)
        self._range = RangeStateProducer(self._cfg)
        self._symbol = symbol

    @property
    def n1(self) -> N1IncrementalReplayEngine:
        return self._n1

    @property
    def range_config(self) -> RangeConfig:
        return self._cfg

    @property
    def bars_observed(self) -> int:
        return self._n1.bars_observed

    def observe_closed_bar(self, bar: Any, *, as_of: int | None = None
                           ) -> tuple[Any, RangeStateResult, list[RangeEvent]]:
        """Un pas: N1 byte-identic + RANGE_STATE + evenimente. Ordinea guard-urilor N1 (refuzuri) e neatinsă."""
        n1_result = self._n1.observe_closed_bar(bar, as_of=as_of)
        atr = self._n1._axes_builder.atr14()          # ATR14 cauzal (același folosit de exp/comp), None în warmup
        tctx = _trend_context(n1_result.raw_axes.direction)
        range_result, events = self._range.observe(
            bar_index=self._n1.bars_observed - 1, ts_close=bar.ts_close,
            open_=bar.open, high=bar.high, low=bar.low, close=bar.close, atr=atr, trend_context=tctx)
        return n1_result, range_result, events

    def entry_decision_for(self, event: RangeEvent | None) -> EntryDecision:
        """Refuz executabil F7 — expus la nivel de motor pentru orice consumator de strategie."""
        return entry_decision(event)

    def replay_batch(self, bars: Any, *, as_of: int | None = None) -> RangeLedger:
        records: list[RangeReplayRecord] = []
        occ: Counter[str] = Counter()
        n_guards = 0
        for bar in bars:
            n1_result, range_result, events = self.observe_closed_bar(bar, as_of=as_of)
            ev_dicts = tuple(e.as_dict() for e in events)
            guard = None
            for e in events:
                occ[e.kind] += 1
                if e.safety_guard is not None:
                    guard = e.safety_guard
                    n_guards += 1
            if range_result.available and range_result.consolidation_state is not None:
                occ[f"CONSOL_{range_result.consolidation_state}"] += 1
            elif not range_result.available:
                occ[f"UNAVAILABLE_{range_result.reason}"] += 1
            records.append(RangeReplayRecord(
                bar_index=range_result.bar_index, ts_close=range_result.ts_close,
                n1_output_fingerprint=n1_result.output_fingerprint,
                n1_direction=n1_result.raw_axes.direction, n1_structure=n1_result.raw_axes.structure,
                range_available=range_result.available, range_reason=range_result.reason,
                consolidation_state=range_result.consolidation_state,
                boundary_validity=range_result.boundary_validity,
                upper=range_result.upper, lower=range_result.lower,
                actionable_start_ts=range_result.actionable_start_ts,
                structural_start_ts=range_result.structural_start_ts,
                trend_context=range_result.trend_context, invalidation=range_result.invalidation,
                range_reason_codes=range_result.reason_codes, events=ev_dicts, safety_guard=guard))
        bars_tuple = tuple(bars)
        data_identity = _identity_mod.bars_content_hash(bars_tuple, bar_to_parts=_bar_parts)
        return RangeLedger(
            run_hash=self._cfg.run_hash(data_identity), range_spec_id=self._cfg.range_spec_id(),
            config_hash=self._cfg.config_hash(), data_identity=data_identity,
            n1_evaluation_identity_fingerprint=self._n1.identity.fingerprint(),
            range_state_contract_version=RANGE_STATE_CONTRACT_VERSION,
            range_event_contract_version=RANGE_EVENT_CONTRACT_VERSION,
            pkg_n1_contract_version=PKG_N1_CONTRACT_VERSION,
            pkg_raw_axis_schema_version=PKG_RAW_AXIS_SCHEMA_VERSION, pkg_router_version=PKG_ROUTER_VERSION,
            range_ledger_schema_version=RANGE_LEDGER_SCHEMA_VERSION, ve_n1_replay_version=VE_N1_REPLAY_VERSION,
            bar_count=len(records), n_guards=n_guards, occupancy=dict(occ), records=tuple(records))

    # ── snapshot / restore COMBINAT (mărginit, fail-closed) ──
    def snapshot(self) -> RangeSnapshot:
        return RangeSnapshot(
            range_snapshot_schema_version=RANGE_SNAPSHOT_SCHEMA_VERSION,
            n1_identity_fingerprint=self._n1.identity.fingerprint(),
            range_spec_id=self._cfg.range_spec_id(), config_hash=self._cfg.config_hash(),
            n1_snapshot=self._n1.snapshot(), range_state=self._range.snapshot_state())

    def restore(self, snapshot: RangeSnapshot) -> None:
        if not isinstance(snapshot, RangeSnapshot):
            raise RangeSnapshotError("snapshot nu este RangeSnapshot")
        if snapshot.range_snapshot_schema_version != RANGE_SNAPSHOT_SCHEMA_VERSION:
            raise RangeSnapshotError("versiune de schemă snapshot RANGE incompatibilă")
        if snapshot.n1_identity_fingerprint != self._n1.identity.fingerprint():
            raise RangeSnapshotError("identitate N1 incompatibilă")
        if snapshot.range_spec_id != self._cfg.range_spec_id() or snapshot.config_hash != self._cfg.config_hash():
            raise RangeSnapshotError("range_spec_id / config_hash incompatibil")
        self._n1.restore(snapshot.n1_snapshot)
        self._range = RangeStateProducer(self._cfg)
        self._range.restore_state(snapshot.range_state)

    def reset(self) -> None:
        self._n1.reset()
        self._range = RangeStateProducer(self._cfg)
