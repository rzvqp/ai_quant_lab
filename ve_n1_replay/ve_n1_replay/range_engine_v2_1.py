"""RangeStateReplayEngineV2Pinned (0.3.1) — compune N1 (0.1.1, neatins) + `RangeStateProducerV2` (0.3.0, NEATINS,
IMPORTAT direct) cu configurația PIN-uită `RangeConfigV2Pinned`. Nicio linie din motorul N1 sau din producătorul
V2 nu e reimplementată aici — doar traducerea configurației și identitatea/snapshot-ul proprii lui 0.3.1.

Refuz fail-closed la restore: snapshot dintr-o versiune STRĂINĂ (0.2.0 `RangeSnapshot`, 0.3.0 `RangeSnapshotV2`,
sau orice tip necunoscut) — nicio migrare implicită, niciun rebuild parțial.
"""
from __future__ import annotations

import dataclasses as _dc
from collections import Counter
from typing import Any

from .incremental import N1IncrementalReplayEngine, _bar_parts, _identity_mod
from .range_engine import RangeSnapshot as RangeSnapshotV1        # 0.2.0 — doar pt. izolare explicită de tip
from .range_engine_v2 import RangeSnapshotV2 as RangeSnapshotV2_030  # 0.3.0 — idem
from .range_state_v2 import (          # 0.3.0, NEATINS — producătorul REAL, reutilizat neschimbat
    RangeStateProducerV2, RangeStateResultV2, RangeEventV2, RangeEventKindV2,
    SAFETY_GUARDS_REGISTER, entry_decision_v2, EntryDecisionV2,
)
from .range_state_v2_1 import RangeConfigV2Pinned, LegacyConfigRejectedError
from .version import (
    RANGE_LEDGER_SCHEMA_VERSION_V2_1, RANGE_SNAPSHOT_SCHEMA_VERSION_V2_1, RANGE_CONFIG_SCHEMA_VERSION_V2_1,
    RANGE_STATE_CONTRACT_VERSION_V2, RANGE_EVENT_CONTRACT_VERSION_V2, RANGE_STATE_MACHINE_VERSION_V2,
    PKG_N1_CONTRACT_VERSION_V2, PKG_RAW_AXIS_SCHEMA_VERSION_V2, PKG_ROUTER_VERSION_V2, VE_N1_REPLAY_VERSION,
    RANGE_V2_1_STATISTICIAN_PREREG_COMMIT, RANGE_V2_1_STATISTICIAN_RESULT_COMMIT,
    RANGE_V2_1_MANIFEST_COMMIT, RANGE_V2_1_MANIFEST_FINGERPRINT, RANGE_V2_1_CONSTRUCTION_CONTROL_EPISODE_ID,
    PREDECESSOR_0_3_0_VERSION, PREDECESSOR_0_3_0_WHEEL_SHA256, PREDECESSOR_0_3_0_BUILD_COMMIT,
    PREDECESSOR_0_3_0_DELIVERY_COMMIT, N1_BASELINE_VERSION,
)


def _trend_context(direction: str | None) -> str | None:
    return direction


@_dc.dataclass(frozen=True, slots=True)
class RangeReplayRecordV2Pinned:
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
class RangeLedgerV2Pinned:
    run_hash: str
    range_spec_id: str
    config_hash: str
    data_identity: str
    n1_evaluation_identity_fingerprint: str
    n1_baseline_version: str
    predecessor_version: str
    predecessor_wheel_sha256: str
    predecessor_build_commit: str
    predecessor_delivery_commit: str
    statistician_prereg_commit: str
    statistician_result_commit: str
    statistician_manifest_commit: str
    statistician_manifest_fingerprint: str
    construction_control_episode_id: str
    w_atr: float
    derived_s_max: float
    s_max_derivation_formula: str
    range_state_contract_version: str
    range_event_contract_version: str
    range_state_machine_version: str
    range_config_schema_version: str
    pkg_n1_contract_version: str
    pkg_raw_axis_schema_version: str
    pkg_router_version: str
    range_ledger_schema_version: str
    ve_n1_replay_version: str
    bar_count: int
    n_guards: int
    occupancy: dict[str, int]
    records: tuple[RangeReplayRecordV2Pinned, ...]

    def header(self) -> dict[str, Any]:
        d = {k: getattr(self, k) for k in (
            "run_hash", "range_spec_id", "config_hash", "data_identity", "n1_evaluation_identity_fingerprint",
            "n1_baseline_version", "predecessor_version", "predecessor_wheel_sha256", "predecessor_build_commit",
            "predecessor_delivery_commit", "statistician_prereg_commit", "statistician_result_commit",
            "statistician_manifest_commit", "statistician_manifest_fingerprint", "construction_control_episode_id",
            "w_atr", "derived_s_max", "s_max_derivation_formula",
            "range_state_contract_version", "range_event_contract_version", "range_state_machine_version",
            "range_config_schema_version", "pkg_n1_contract_version", "pkg_raw_axis_schema_version",
            "pkg_router_version", "range_ledger_schema_version", "ve_n1_replay_version", "bar_count", "n_guards")}
        d["occupancy"] = dict(self.occupancy)
        d["safety_guards_register"] = list(SAFETY_GUARDS_REGISTER)
        return d


@_dc.dataclass(frozen=True, slots=True)
class RangeSnapshotV2Pinned:
    range_snapshot_schema_version: str
    range_config_schema_version: str
    n1_identity_fingerprint: str
    range_spec_id: str
    config_hash: str
    n1_snapshot: Any
    range_state: dict[str, Any]


class RangeSnapshotErrorV2Pinned(Exception):
    pass


class RangeStateReplayEngineV2Pinned:
    """Motorul 0.3.1: N1 (0.1.1) + `RangeStateProducerV2` (0.3.0) — AMBELE neatinse, importate — parametrizate
    prin `RangeConfigV2Pinned`. Singura diferență de comportament față de 0.3.0 e VALOAREA `w_atr`/`s_max`."""

    def __init__(self, *, symbol: str, timeframe: str, bar_interval_seconds: int,
                 implementation_commit: str, range_config: RangeConfigV2Pinned | None = None,
                 **kwargs: Any) -> None:
        self._n1 = N1IncrementalReplayEngine(
            symbol=symbol, timeframe=timeframe, bar_interval_seconds=bar_interval_seconds,
            implementation_commit=implementation_commit, **kwargs)
        self._cfg = range_config if range_config is not None else RangeConfigV2Pinned.multiday(timeframe=timeframe)
        self._range = RangeStateProducerV2(self._cfg._to_runtime_config())   # 0.3.0, NEATINS, reutilizat direct
        self._symbol = symbol

    @property
    def n1(self) -> N1IncrementalReplayEngine:
        return self._n1

    @property
    def range_config(self) -> RangeConfigV2Pinned:
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

    def replay_batch(self, bars: Any, *, as_of: int | None = None) -> RangeLedgerV2Pinned:
        records: list[RangeReplayRecordV2Pinned] = []
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
            records.append(RangeReplayRecordV2Pinned(
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
        return RangeLedgerV2Pinned(
            run_hash=self._cfg.run_hash(data_identity), range_spec_id=self._cfg.range_spec_id(),
            config_hash=self._cfg.config_hash(), data_identity=data_identity,
            n1_evaluation_identity_fingerprint=self._n1.identity.fingerprint(),
            n1_baseline_version=N1_BASELINE_VERSION,
            predecessor_version=PREDECESSOR_0_3_0_VERSION, predecessor_wheel_sha256=PREDECESSOR_0_3_0_WHEEL_SHA256,
            predecessor_build_commit=PREDECESSOR_0_3_0_BUILD_COMMIT,
            predecessor_delivery_commit=PREDECESSOR_0_3_0_DELIVERY_COMMIT,
            statistician_prereg_commit=RANGE_V2_1_STATISTICIAN_PREREG_COMMIT,
            statistician_result_commit=RANGE_V2_1_STATISTICIAN_RESULT_COMMIT,
            statistician_manifest_commit=RANGE_V2_1_MANIFEST_COMMIT,
            statistician_manifest_fingerprint=RANGE_V2_1_MANIFEST_FINGERPRINT,
            construction_control_episode_id=RANGE_V2_1_CONSTRUCTION_CONTROL_EPISODE_ID,
            w_atr=self._cfg.w_atr, derived_s_max=self._cfg.derived_s_max,
            s_max_derivation_formula=self._cfg.provenance()["s_max_derivation_formula"],
            range_state_contract_version=RANGE_STATE_CONTRACT_VERSION_V2,
            range_event_contract_version=RANGE_EVENT_CONTRACT_VERSION_V2,
            range_state_machine_version=RANGE_STATE_MACHINE_VERSION_V2,
            range_config_schema_version=RANGE_CONFIG_SCHEMA_VERSION_V2_1,
            pkg_n1_contract_version=PKG_N1_CONTRACT_VERSION_V2,
            pkg_raw_axis_schema_version=PKG_RAW_AXIS_SCHEMA_VERSION_V2, pkg_router_version=PKG_ROUTER_VERSION_V2,
            range_ledger_schema_version=RANGE_LEDGER_SCHEMA_VERSION_V2_1, ve_n1_replay_version=VE_N1_REPLAY_VERSION,
            bar_count=len(records), n_guards=n_guards, occupancy=dict(occ), records=tuple(records))

    # ── snapshot / restore 0.3.1 (mărginit, fail-closed, refuză migrare implicită de la 0.2.0/0.3.0) ──
    def snapshot(self) -> RangeSnapshotV2Pinned:
        return RangeSnapshotV2Pinned(
            range_snapshot_schema_version=RANGE_SNAPSHOT_SCHEMA_VERSION_V2_1,
            range_config_schema_version=RANGE_CONFIG_SCHEMA_VERSION_V2_1,
            n1_identity_fingerprint=self._n1.identity.fingerprint(),
            range_spec_id=self._cfg.range_spec_id(), config_hash=self._cfg.config_hash(),
            n1_snapshot=self._n1.snapshot(), range_state=self._range.snapshot_state())

    def restore(self, snapshot: Any) -> None:
        if isinstance(snapshot, (RangeSnapshotV1, RangeSnapshotV2_030)):
            raise RangeSnapshotErrorV2Pinned(
                "refuz: snapshot dintr-o versiune ANTERIOARĂ (0.2.0/0.3.0) NU poate fi restaurat într-un motor "
                "0.3.1 — migrare explicită necesară, niciun rebuild parțial acceptat")
        if not isinstance(snapshot, RangeSnapshotV2Pinned):
            raise RangeSnapshotErrorV2Pinned(f"snapshot de tip necunoscut: {type(snapshot).__name__!r}")
        if snapshot.range_snapshot_schema_version != RANGE_SNAPSHOT_SCHEMA_VERSION_V2_1:
            raise RangeSnapshotErrorV2Pinned(
                f"versiune de schemă snapshot incompatibilă: {snapshot.range_snapshot_schema_version!r} != "
                f"{RANGE_SNAPSHOT_SCHEMA_VERSION_V2_1!r}")
        if snapshot.n1_identity_fingerprint != self._n1.identity.fingerprint():
            raise RangeSnapshotErrorV2Pinned("identitate N1 incompatibilă")
        if snapshot.range_spec_id != self._cfg.range_spec_id() or snapshot.config_hash != self._cfg.config_hash():
            raise RangeSnapshotErrorV2Pinned("range_spec_id / config_hash incompatibil")
        self._n1.restore(snapshot.n1_snapshot)
        self._range = RangeStateProducerV2(self._cfg._to_runtime_config())
        self._range.restore_state(snapshot.range_state)

    def reset(self) -> None:
        self._n1.reset()
        self._range = RangeStateProducerV2(self._cfg._to_runtime_config())
