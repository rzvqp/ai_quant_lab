"""RangeSemanticEngineV31 (0.4.1) — compune N1 (0.1.1, NEATINS) + `RangeSemanticProducerV31` (0.4.1, pantă
OLS incrementală O(1)/bară — fix §12 RT-RANGE-0004) cu `RangeConfigV31`. Copie CHIRURGICALĂ a motorului
0.4.0 (`range_engine_v3.py`, BYTE-NEATINS): nicio schimbare de orchestrare, doar identitatea/producătorul
NOI. `RangeLedgerV3`/`RangeReplayRecordV3` (0.4.0) sunt REUTILIZATE direct — forma lor (câmpuri) nu s-a
schimbat, doar VALORILE (`range_producer_version`, `predecessor_*`) populate de acest motor diferă.

Refuz fail-closed la restore: snapshot dintr-o versiune STRĂINĂ — 0.2.0/0.3.0/0.3.1 (ca în 0.4.0) și ACUM
ȘI 0.3.0/0.3.1/**0.4.0** (`RangeSnapshotV3`, structura internă a segmentului s-a schimbat — noile câmpuri
`_slope_sum_y`/`_slope_sum_xy` nu au corespondent în starea 0.4.0) — sau orice tip necunoscut/corupt/cu
identitate ori contract nepotrivit. Nicio migrare implicită, niciun rebuild parțial: aceeași atomicitate
validate-apoi-swap ca 0.4.0 (un restore eșuat lasă motorul complet NESCHIMBAT).
"""
from __future__ import annotations

import dataclasses as _dc
from collections import Counter
from typing import Any

from .incremental import N1IncrementalReplayEngine, _bar_parts, _identity_mod
from .range_engine import RangeSnapshot as RangeSnapshotV1                    # 0.2.0 — izolare explicită de tip
from .range_engine_v2 import RangeSnapshotV2 as RangeSnapshotV2_030           # 0.3.0 — idem
from .range_engine_v2_1 import RangeSnapshotV2Pinned as RangeSnapshotV2_031   # 0.3.1 — idem
from .range_engine_v3 import (
    RangeSnapshotV3 as RangeSnapshotV3_040,   # 0.4.0 — idem (predecesorul IMEDIAT, refuzat fail-closed)
    RangeLedgerV3, RangeReplayRecordV3, _trend_context,
)
from .range_semantic_v3 import (
    RangeSemanticResultV3, RangeEventV3, ConfirmedSegmentRecordV3,
    SAFETY_GUARDS_REGISTER, entry_decision_v3, EntryDecisionV3,
)
from .range_semantic_v3_1 import RangeConfigV31, RangeSemanticProducerV31
from .version import (
    RANGE_SEMANTIC_CONTRACT_VERSION_V3, RANGE_STATE_MACHINE_VERSION_V3, RANGE_EVENT_CONTRACT_VERSION_V3,
    RANGE_CONFIG_SCHEMA_VERSION_V3, RANGE_LEDGER_SCHEMA_VERSION_V3, RANGE_REASON_CODE_CONTRACT_VERSION_V3,
    RANGE_EVALUATION_IDENTITY_VERSION_V3, RANGE_PRODUCER_VERSION_V3_1, RANGE_SNAPSHOT_SCHEMA_VERSION_V3_1,
    RANGE_V3_STATISTICIAN_SPEC_COMMIT, RANGE_V3_MANIFEST_COMMIT, RANGE_V3_MANIFEST_VERSION,
    RANGE_V3_MANIFEST_FINGERPRINT, RANGE_V3_HBL_PROVENANCE,
    PREDECESSOR_0_4_0_VERSION, PREDECESSOR_0_4_0_WHEEL_SHA256, PREDECESSOR_0_4_0_BUILD_COMMIT,
    PREDECESSOR_0_4_0_DELIVERY_COMMIT, N1_BASELINE_VERSION, VE_N1_REPLAY_VERSION,
    PKG_N1_CONTRACT_VERSION_V2, PKG_RAW_AXIS_SCHEMA_VERSION_V2, PKG_ROUTER_VERSION_V2,
)

__all__ = ["RangeSnapshotV31", "RangeSnapshotErrorV31", "RangeSemanticEngineV31"]


@_dc.dataclass(frozen=True, slots=True)
class RangeSnapshotV31:
    range_snapshot_schema_version: str
    range_config_schema_version: str
    n1_identity_fingerprint: str
    range_spec_id: str
    config_hash: str
    n1_snapshot: Any
    range_state: dict[str, Any]


class RangeSnapshotErrorV31(Exception):
    pass


class RangeSemanticEngineV31:
    """Motorul 0.4.1: N1 (0.1.1, NEATINS) + `RangeSemanticProducerV31` (0.4.1, pantă O(1)) — orchestrare,
    NU reimplementare. Copie chirurgicală a `RangeSemanticEngineV3` (0.4.0, `range_engine_v3.py`, NEATINS)."""

    def __init__(self, *, symbol: str, timeframe: str, bar_interval_seconds: int,
                 implementation_commit: str, range_config: RangeConfigV31,
                 **kwargs: Any) -> None:
        self._n1 = N1IncrementalReplayEngine(
            symbol=symbol, timeframe=timeframe, bar_interval_seconds=bar_interval_seconds,
            implementation_commit=implementation_commit, **kwargs)
        self._cfg = range_config
        self._range = RangeSemanticProducerV31(self._cfg)
        self._symbol = symbol

    @property
    def n1(self) -> N1IncrementalReplayEngine:
        return self._n1

    @property
    def range_config(self) -> RangeConfigV31:
        return self._cfg

    @property
    def bars_observed(self) -> int:
        return self._n1.bars_observed

    @property
    def segment_history(self) -> tuple[ConfirmedSegmentRecordV3, ...]:
        return self._range.history

    def observe_closed_bar(self, bar: Any, *, as_of: int | None = None
                           ) -> tuple[Any, RangeSemanticResultV3, list[RangeEventV3]]:
        n1_result = self._n1.observe_closed_bar(bar, as_of=as_of)
        atr = self._n1._axes_builder.atr14()
        tctx = _trend_context(n1_result.raw_axes.direction)
        range_result, events = self._range.observe(
            ts_close=bar.ts_close, open_=bar.open, high=bar.high, low=bar.low, close=bar.close,
            atr=atr, trend_context=tctx)
        return n1_result, range_result, events

    def entry_decision_for(self, event: RangeEventV3 | None) -> EntryDecisionV3:
        return entry_decision_v3(event)

    def replay_batch(self, bars: Any, *, as_of: int | None = None) -> RangeLedgerV3:
        records: list[RangeReplayRecordV3] = []
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
            if range_result.available:
                occ[f"LIFECYCLE_{range_result.lifecycle}"] += 1
            else:
                occ[f"UNAVAILABLE_{range_result.reason}"] += 1
            records.append(RangeReplayRecordV3(
                bar_index=range_result.bar_index, ts_close=range_result.ts_close,
                n1_output_fingerprint=n1_result.output_fingerprint,
                n1_direction=n1_result.raw_axes.direction, n1_structure=n1_result.raw_axes.structure,
                range_available=range_result.available, range_reason=range_result.reason,
                segment_id=range_result.segment_id, predecessor_id=range_result.predecessor_id,
                transition_reason=range_result.transition_reason, lifecycle=range_result.lifecycle,
                structural_start_ts=range_result.structural_start_ts, confirm_ts=range_result.confirm_ts,
                bars_in_segment=range_result.bars_in_segment,
                anchor_lower=range_result.anchor_lower, anchor_upper=range_result.anchor_upper,
                range_mid=range_result.range_mid, w=range_result.w,
                touches_upper=range_result.touches_upper, touches_lower=range_result.touches_lower,
                pending_event=range_result.pending_event, confirmed_event=range_result.confirmed_event,
                slope=range_result.slope, trend_context=range_result.trend_context,
                range_reason_codes=range_result.reason_codes, events=ev_dicts, safety_guard=guard))
        bars_tuple = tuple(bars)
        data_identity = _identity_mod.bars_content_hash(bars_tuple, bar_to_parts=_bar_parts)
        confirmed = tuple(_dc.asdict(r) for r in self._range.history)
        return RangeLedgerV3(
            run_hash=self._cfg.run_hash(data_identity), range_spec_id=self._cfg.range_spec_id(),
            config_hash=self._cfg.config_hash(), data_identity=data_identity,
            n1_evaluation_identity_fingerprint=self._n1.identity.fingerprint(),
            n1_baseline_version=N1_BASELINE_VERSION,
            predecessor_version=PREDECESSOR_0_4_0_VERSION, predecessor_wheel_sha256=PREDECESSOR_0_4_0_WHEEL_SHA256,
            predecessor_build_commit=PREDECESSOR_0_4_0_BUILD_COMMIT,
            predecessor_delivery_commit=PREDECESSOR_0_4_0_DELIVERY_COMMIT,
            statistician_spec_commit=RANGE_V3_STATISTICIAN_SPEC_COMMIT,
            statistician_manifest_commit=RANGE_V3_MANIFEST_COMMIT,
            statistician_manifest_version=RANGE_V3_MANIFEST_VERSION,
            statistician_manifest_fingerprint=RANGE_V3_MANIFEST_FINGERPRINT,
            hbl_provenance=RANGE_V3_HBL_PROVENANCE,
            K=self._cfg.K, N=self._cfg.N, w_atr=self._cfg.w_atr, derived_s_max=self._cfg.s_max,
            param_provenance=self._cfg.provenance(),
            range_semantic_contract_version=RANGE_SEMANTIC_CONTRACT_VERSION_V3,
            range_state_machine_version=RANGE_STATE_MACHINE_VERSION_V3,
            range_event_contract_version=RANGE_EVENT_CONTRACT_VERSION_V3,
            range_config_schema_version=RANGE_CONFIG_SCHEMA_VERSION_V3,
            range_reason_code_contract_version=RANGE_REASON_CODE_CONTRACT_VERSION_V3,
            range_evaluation_identity_version=RANGE_EVALUATION_IDENTITY_VERSION_V3,
            range_producer_version=RANGE_PRODUCER_VERSION_V3_1,
            pkg_n1_contract_version=PKG_N1_CONTRACT_VERSION_V2,
            pkg_raw_axis_schema_version=PKG_RAW_AXIS_SCHEMA_VERSION_V2, pkg_router_version=PKG_ROUTER_VERSION_V2,
            range_ledger_schema_version=RANGE_LEDGER_SCHEMA_VERSION_V3, ve_n1_replay_version=VE_N1_REPLAY_VERSION,
            bar_count=len(records), n_guards=n_guards, occupancy=dict(occ),
            confirmed_segments=confirmed, records=tuple(records))

    # ── snapshot / restore 0.4.1 (mărginit, fail-closed, refuză migrare implicită de la 0.2.0/0.3.0/0.3.1/0.4.0) ──
    def snapshot(self) -> RangeSnapshotV31:
        return RangeSnapshotV31(
            range_snapshot_schema_version=RANGE_SNAPSHOT_SCHEMA_VERSION_V3_1,
            range_config_schema_version=RANGE_CONFIG_SCHEMA_VERSION_V3,
            n1_identity_fingerprint=self._n1.identity.fingerprint(),
            range_spec_id=self._cfg.range_spec_id(), config_hash=self._cfg.config_hash(),
            n1_snapshot=self._n1.snapshot(), range_state=self._range.snapshot_state())

    def restore(self, snapshot: Any) -> None:
        if isinstance(snapshot, (RangeSnapshotV1, RangeSnapshotV2_030, RangeSnapshotV2_031, RangeSnapshotV3_040)):
            raise RangeSnapshotErrorV31(
                "refuz: snapshot dintr-o versiune ANTERIOARĂ (0.2.0/0.3.0/0.3.1/0.4.0) NU poate fi restaurat "
                "într-un motor 0.4.1 — migrare explicită necesară, niciun rebuild parțial acceptat "
                "(structura internă a segmentului s-a schimbat: statistici suficiente pt. panta incrementală)")
        if not isinstance(snapshot, RangeSnapshotV31):
            raise RangeSnapshotErrorV31(f"snapshot de tip necunoscut: {type(snapshot).__name__!r}")
        if snapshot.range_snapshot_schema_version != RANGE_SNAPSHOT_SCHEMA_VERSION_V3_1:
            raise RangeSnapshotErrorV31(
                f"versiune de schemă snapshot incompatibilă: {snapshot.range_snapshot_schema_version!r} != "
                f"{RANGE_SNAPSHOT_SCHEMA_VERSION_V3_1!r}")
        if snapshot.n1_identity_fingerprint != self._n1.identity.fingerprint():
            raise RangeSnapshotErrorV31("identitate N1 incompatibilă")
        if snapshot.range_spec_id != self._cfg.range_spec_id() or snapshot.config_hash != self._cfg.config_hash():
            raise RangeSnapshotErrorV31("range_spec_id / config_hash incompatibil")
        # construiește + validează starea NOUĂ într-un producător IZOLAT înainte de a atinge orice stare
        # existentă (N1 sau self._range) — restore e ATOMIC: totul sau nimic, fără desincronizare pe eșec parțial.
        fresh = RangeSemanticProducerV31(self._cfg)
        try:
            fresh.restore_state(snapshot.range_state)
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise RangeSnapshotErrorV31(f"snapshot range_state corupt/incomplet: {exc!r}") from exc
        self._n1.restore(snapshot.n1_snapshot)
        self._range = fresh

    def reset(self) -> None:
        self._n1.reset()
        self._range = RangeSemanticProducerV31(self._cfg)
