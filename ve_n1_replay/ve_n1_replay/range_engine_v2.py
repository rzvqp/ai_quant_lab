"""RangeStateReplayEngineV2 (0.3.0) — compune motorul N1 BYTE-IDENTIC (0.1.1, neatins) cu producătorul SPEC V2.

Arhitectură identică cu `range_engine.py` (0.2.0, NEMODIFICAT): schimbă DOAR producătorul de range. N1 rămâne
`N1IncrementalReplayEngine` neatins ⇒ `output_fingerprint` per-bară byte-identic cu 0.1.1/0.2.0.

Snapshot/restore V2 refuză fail-closed orice mismatch: versiune de schemă, identitate N1, `range_spec_id`/
`config_hash`, ȘI explicit un snapshot dintr-o ALTĂ versiune de producător (0.2.0 `RangeSnapshot` restaurat
într-un motor V2, sau invers) — niciun rebuild parțial/incomplet nu e acceptat.
"""
from __future__ import annotations

import dataclasses as _dc
from collections import Counter
from typing import Any

from .incremental import N1IncrementalReplayEngine, _bar_parts, _identity_mod
from .range_engine import RangeSnapshot as RangeSnapshotV1   # DOAR pentru izolarea explicită de tip la restore
from .range_state_v2 import (
    RangeConfigV2, RangeStateProducerV2, RangeStateResultV2, RangeEventV2, RangeEventKindV2,
    SAFETY_GUARDS_REGISTER, entry_decision_v2, EntryDecisionV2,
)
from .version import (
    RANGE_LEDGER_SCHEMA_VERSION_V2, RANGE_SNAPSHOT_SCHEMA_VERSION_V2, RANGE_STATE_CONTRACT_VERSION_V2,
    RANGE_EVENT_CONTRACT_VERSION_V2, RANGE_STATE_MACHINE_VERSION_V2, PKG_N1_CONTRACT_VERSION_V2,
    PKG_RAW_AXIS_SCHEMA_VERSION_V2, PKG_ROUTER_VERSION_V2, VE_N1_REPLAY_VERSION,
    RANGE_V2_STATISTICIAN_SOURCE_COMMIT, RANGE_V2_STATISTICIAN_MANIFEST_COMMIT,
    PREDECESSOR_0_2_0_VERSION, PREDECESSOR_0_2_0_WHEEL_SHA256, N1_BASELINE_VERSION,
)


def _trend_context(direction: str | None) -> str | None:
    return direction


@_dc.dataclass(frozen=True, slots=True)
class RangeReplayRecordV2:
    bar_index: int
    ts_close: int
    n1_output_fingerprint: str
    n1_direction: str | None
    n1_structure: str | None
    range_available: bool
    range_reason: str
    consolidation_state: str | None
    structure_class: str | None
    boundary_validity: str | None
    anchor_upper: float | None
    anchor_lower: float | None
    actionable_start_ts: int | None
    structural_start_ts: int | None
    structure_events_inside: int | None
    trend_context: str | None
    invalidation: str | None
    range_reason_codes: tuple[str, ...]
    events: tuple[dict[str, Any], ...]
    safety_guard: str | None

    def as_dict(self) -> dict[str, Any]:
        return _dc.asdict(self)


@_dc.dataclass(frozen=True, slots=True)
class RangeLedgerV2:
    run_hash: str
    range_spec_id: str
    config_hash: str
    data_identity: str
    n1_evaluation_identity_fingerprint: str
    n1_baseline_version: str
    predecessor_version: str
    predecessor_wheel_sha256: str
    statistician_source_commit: str
    statistician_manifest_commit: str
    range_state_contract_version: str
    range_event_contract_version: str
    range_state_machine_version: str
    pkg_n1_contract_version: str
    pkg_raw_axis_schema_version: str
    pkg_router_version: str
    range_ledger_schema_version: str
    ve_n1_replay_version: str
    bar_count: int
    n_guards: int
    occupancy: dict[str, int]
    records: tuple[RangeReplayRecordV2, ...]

    def header(self) -> dict[str, Any]:
        d = {k: getattr(self, k) for k in (
            "run_hash", "range_spec_id", "config_hash", "data_identity", "n1_evaluation_identity_fingerprint",
            "n1_baseline_version", "predecessor_version", "predecessor_wheel_sha256",
            "statistician_source_commit", "statistician_manifest_commit",
            "range_state_contract_version", "range_event_contract_version", "range_state_machine_version",
            "pkg_n1_contract_version", "pkg_raw_axis_schema_version", "pkg_router_version",
            "range_ledger_schema_version", "ve_n1_replay_version", "bar_count", "n_guards")}
        d["occupancy"] = dict(self.occupancy)
        d["safety_guards_register"] = list(SAFETY_GUARDS_REGISTER)
        return d


@_dc.dataclass(frozen=True, slots=True)
class RangeSnapshotV2:
    range_snapshot_schema_version: str
    n1_identity_fingerprint: str
    range_spec_id: str
    config_hash: str
    n1_snapshot: Any
    range_state: dict[str, Any]


class RangeSnapshotErrorV2(Exception):
    pass


class RangeStateReplayEngineV2:
    def __init__(self, *, symbol: str, timeframe: str, bar_interval_seconds: int,
                 implementation_commit: str, range_config: RangeConfigV2 | None = None, **kwargs: Any) -> None:
        self._n1 = N1IncrementalReplayEngine(
            symbol=symbol, timeframe=timeframe, bar_interval_seconds=bar_interval_seconds,
            implementation_commit=implementation_commit, **kwargs)
        self._cfg = range_config if range_config is not None else RangeConfigV2.multiday(timeframe=timeframe)
        self._range = RangeStateProducerV2(self._cfg)
        self._symbol = symbol

    @property
    def n1(self) -> N1IncrementalReplayEngine:
        return self._n1

    @property
    def range_config(self) -> RangeConfigV2:
        return self._cfg

    @property
    def bars_observed(self) -> int:
        return self._n1.bars_observed

    def observe_closed_bar(self, bar: Any, *, as_of: int | None = None
                           ) -> tuple[Any, RangeStateResultV2, list[RangeEventV2]]:
        n1_result = self._n1.observe_closed_bar(bar, as_of=as_of)
        atr = self._n1._axes_builder.atr14()
        tctx = _trend_context(n1_result.raw_axes.direction)
        range_result, events = self._range.observe(
            bar_index=self._n1.bars_observed - 1, ts_close=bar.ts_close,
            open_=bar.open, high=bar.high, low=bar.low, close=bar.close, atr=atr, trend_context=tctx)
        return n1_result, range_result, events

    def entry_decision_for(self, event: RangeEventV2 | None) -> EntryDecisionV2:
        return entry_decision_v2(event)

    def replay_batch(self, bars: Any, *, as_of: int | None = None) -> RangeLedgerV2:
        records: list[RangeReplayRecordV2] = []
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
                if range_result.structure_class:
                    occ[f"CLASS_{range_result.structure_class}"] += 1
            elif not range_result.available:
                occ[f"UNAVAILABLE_{range_result.reason}"] += 1
            records.append(RangeReplayRecordV2(
                bar_index=range_result.bar_index, ts_close=range_result.ts_close,
                n1_output_fingerprint=n1_result.output_fingerprint,
                n1_direction=n1_result.raw_axes.direction, n1_structure=n1_result.raw_axes.structure,
                range_available=range_result.available, range_reason=range_result.reason,
                consolidation_state=range_result.consolidation_state, structure_class=range_result.structure_class,
                boundary_validity=range_result.boundary_validity,
                anchor_upper=range_result.anchor_upper, anchor_lower=range_result.anchor_lower,
                actionable_start_ts=range_result.actionable_start_ts,
                structural_start_ts=range_result.structural_start_ts,
                structure_events_inside=range_result.structure_events_inside,
                trend_context=range_result.trend_context, invalidation=range_result.invalidation,
                range_reason_codes=range_result.reason_codes, events=ev_dicts, safety_guard=guard))
        bars_tuple = tuple(bars)
        data_identity = _identity_mod.bars_content_hash(bars_tuple, bar_to_parts=_bar_parts)
        return RangeLedgerV2(
            run_hash=self._cfg.run_hash(data_identity), range_spec_id=self._cfg.range_spec_id(),
            config_hash=self._cfg.config_hash(), data_identity=data_identity,
            n1_evaluation_identity_fingerprint=self._n1.identity.fingerprint(),
            n1_baseline_version=N1_BASELINE_VERSION, predecessor_version=PREDECESSOR_0_2_0_VERSION,
            predecessor_wheel_sha256=PREDECESSOR_0_2_0_WHEEL_SHA256,
            statistician_source_commit=RANGE_V2_STATISTICIAN_SOURCE_COMMIT,
            statistician_manifest_commit=RANGE_V2_STATISTICIAN_MANIFEST_COMMIT,
            range_state_contract_version=RANGE_STATE_CONTRACT_VERSION_V2,
            range_event_contract_version=RANGE_EVENT_CONTRACT_VERSION_V2,
            range_state_machine_version=RANGE_STATE_MACHINE_VERSION_V2,
            pkg_n1_contract_version=PKG_N1_CONTRACT_VERSION_V2,
            pkg_raw_axis_schema_version=PKG_RAW_AXIS_SCHEMA_VERSION_V2, pkg_router_version=PKG_ROUTER_VERSION_V2,
            range_ledger_schema_version=RANGE_LEDGER_SCHEMA_VERSION_V2, ve_n1_replay_version=VE_N1_REPLAY_VERSION,
            bar_count=len(records), n_guards=n_guards, occupancy=dict(occ), records=tuple(records))

    # ── snapshot / restore V2 (mărginit, fail-closed, refuză migrare implicită de la 0.2.0) ──
    def snapshot(self) -> RangeSnapshotV2:
        return RangeSnapshotV2(
            range_snapshot_schema_version=RANGE_SNAPSHOT_SCHEMA_VERSION_V2,
            n1_identity_fingerprint=self._n1.identity.fingerprint(),
            range_spec_id=self._cfg.range_spec_id(), config_hash=self._cfg.config_hash(),
            n1_snapshot=self._n1.snapshot(), range_state=self._range.snapshot_state())

    def restore(self, snapshot: Any) -> None:
        if isinstance(snapshot, RangeSnapshotV1):
            raise RangeSnapshotErrorV2(
                "refuz: snapshot 0.2.0 (range-state-snapshot-v1) NU poate fi restaurat într-un motor V2 — "
                "migrare explicită necesară, niciun rebuild parțial acceptat")
        if not isinstance(snapshot, RangeSnapshotV2):
            raise RangeSnapshotErrorV2(f"snapshot de tip necunoscut: {type(snapshot).__name__!r}")
        if snapshot.range_snapshot_schema_version != RANGE_SNAPSHOT_SCHEMA_VERSION_V2:
            raise RangeSnapshotErrorV2(
                f"versiune de schemă snapshot RANGE incompatibilă: {snapshot.range_snapshot_schema_version!r} != "
                f"{RANGE_SNAPSHOT_SCHEMA_VERSION_V2!r}")
        if snapshot.n1_identity_fingerprint != self._n1.identity.fingerprint():
            raise RangeSnapshotErrorV2("identitate N1 incompatibilă")
        if snapshot.range_spec_id != self._cfg.range_spec_id() or snapshot.config_hash != self._cfg.config_hash():
            raise RangeSnapshotErrorV2("range_spec_id / config_hash incompatibil")
        self._n1.restore(snapshot.n1_snapshot)
        self._range = RangeStateProducerV2(self._cfg)
        self._range.restore_state(snapshot.range_state)

    def reset(self) -> None:
        self._n1.reset()
        self._range = RangeStateProducerV2(self._cfg)
