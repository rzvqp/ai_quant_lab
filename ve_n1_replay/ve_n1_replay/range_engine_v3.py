"""RangeSemanticEngineV3 (0.4.0) — compune N1 (0.1.1, NEATINS) + `RangeSemanticProducerV3` (0.4.0, NOU) cu
`RangeConfigV3`. Nicio linie din motorul N1 nu e reimplementată — doar orchestrarea + identitatea/ledger-ul/
snapshot-ul proprii lui 0.4.0. `range_config` e OBLIGATORIU la construcție (NU are default la nivel de motor
— K/N/w_atr NEIDENTIFICATE, nicio valoare ascunsă).

Refuz fail-closed la restore: snapshot dintr-o versiune STRĂINĂ — 0.2.0 (`RangeSnapshot`), 0.3.0
(`RangeSnapshotV2`), 0.3.1 (`RangeSnapshotV2Pinned`) — sau orice tip necunoscut / corupt / cu identitate ori
contract nepotrivit. Nicio migrare implicită, niciun rebuild parțial: starea nouă e construită și VALIDATĂ
într-un producător IZOLAT înainte ca N1 sau `self._range` să fie atinse — un restore eșuat lasă motorul complet
NESCHIMBAT (fără desincronizare N1↔range în caz de eroare pe jumătate de restore).
"""
from __future__ import annotations

import dataclasses as _dc
from collections import Counter
from typing import Any

from .incremental import N1IncrementalReplayEngine, _bar_parts, _identity_mod
from .range_engine import RangeSnapshot as RangeSnapshotV1                    # 0.2.0 — izolare explicită de tip
from .range_engine_v2 import RangeSnapshotV2 as RangeSnapshotV2_030           # 0.3.0 — idem
from .range_engine_v2_1 import RangeSnapshotV2Pinned as RangeSnapshotV2_031   # 0.3.1 — idem
from .range_semantic_v3 import (
    RangeConfigV3, RangeSemanticProducerV3, RangeSemanticResultV3, RangeEventV3,
    ConfirmedSegmentRecordV3, SAFETY_GUARDS_REGISTER, entry_decision_v3, EntryDecisionV3,
)
from .version import (
    RANGE_SEMANTIC_CONTRACT_VERSION_V3, RANGE_STATE_MACHINE_VERSION_V3, RANGE_EVENT_CONTRACT_VERSION_V3,
    RANGE_SNAPSHOT_SCHEMA_VERSION_V3, RANGE_LEDGER_SCHEMA_VERSION_V3, RANGE_REASON_CODE_CONTRACT_VERSION_V3,
    RANGE_CONFIG_SCHEMA_VERSION_V3, RANGE_EVALUATION_IDENTITY_VERSION_V3, RANGE_PRODUCER_VERSION_V3,
    RANGE_V3_STATISTICIAN_SPEC_COMMIT, RANGE_V3_MANIFEST_COMMIT, RANGE_V3_MANIFEST_VERSION,
    RANGE_V3_MANIFEST_FINGERPRINT, RANGE_V3_HBL_PROVENANCE,
    PREDECESSOR_0_3_1_VERSION, PREDECESSOR_0_3_1_WHEEL_SHA256, PREDECESSOR_0_3_1_BUILD_COMMIT,
    PREDECESSOR_0_3_1_DELIVERY_COMMIT, N1_BASELINE_VERSION, VE_N1_REPLAY_VERSION,
    PKG_N1_CONTRACT_VERSION_V2, PKG_RAW_AXIS_SCHEMA_VERSION_V2, PKG_ROUTER_VERSION_V2,
)


def _trend_context(direction: str | None) -> str | None:
    return direction


@_dc.dataclass(frozen=True, slots=True)
class RangeReplayRecordV3:
    """Un rând per bară — audit conform mandatului §6 (episode/segment ID, ceasuri duale, limite, atingeri,
    pending/confirmed event, sursă/țintă de tranziție, reason codes, fingerprint-ul N1 per-bară)."""
    bar_index: int
    ts_close: int
    n1_output_fingerprint: str
    n1_direction: str | None
    n1_structure: str | None
    range_available: bool
    range_reason: str
    segment_id: int | None
    predecessor_id: int | None
    transition_reason: str | None
    lifecycle: str | None
    structural_start_ts: int | None
    confirm_ts: int | None
    bars_in_segment: int | None
    anchor_lower: float | None
    anchor_upper: float | None
    range_mid: float | None
    w: float | None
    touches_upper: int | None
    touches_lower: int | None
    pending_event: str | None
    confirmed_event: str | None
    slope: float | None
    trend_context: str | None
    range_reason_codes: tuple[str, ...]
    events: tuple[dict[str, Any], ...]
    safety_guard: str | None

    def as_dict(self) -> dict[str, Any]:
        return _dc.asdict(self)


@_dc.dataclass(frozen=True, slots=True)
class RangeLedgerV3:
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
    statistician_spec_commit: str
    statistician_manifest_commit: str
    statistician_manifest_version: str
    statistician_manifest_fingerprint: str
    hbl_provenance: str
    K: int
    N: int
    w_atr: float
    derived_s_max: float
    param_provenance: dict[str, Any]
    range_semantic_contract_version: str
    range_state_machine_version: str
    range_event_contract_version: str
    range_config_schema_version: str
    range_reason_code_contract_version: str
    range_evaluation_identity_version: str
    range_producer_version: str
    pkg_n1_contract_version: str
    pkg_raw_axis_schema_version: str
    pkg_router_version: str
    range_ledger_schema_version: str
    ve_n1_replay_version: str
    bar_count: int
    n_guards: int
    occupancy: dict[str, int]
    confirmed_segments: tuple[dict[str, Any], ...]
    records: tuple[RangeReplayRecordV3, ...]

    def header(self) -> dict[str, Any]:
        d = {k: getattr(self, k) for k in (
            "run_hash", "range_spec_id", "config_hash", "data_identity", "n1_evaluation_identity_fingerprint",
            "n1_baseline_version", "predecessor_version", "predecessor_wheel_sha256", "predecessor_build_commit",
            "predecessor_delivery_commit", "statistician_spec_commit", "statistician_manifest_commit",
            "statistician_manifest_version", "statistician_manifest_fingerprint", "hbl_provenance",
            "K", "N", "w_atr", "derived_s_max",
            "range_semantic_contract_version", "range_state_machine_version", "range_event_contract_version",
            "range_config_schema_version", "range_reason_code_contract_version",
            "range_evaluation_identity_version", "range_producer_version",
            "pkg_n1_contract_version", "pkg_raw_axis_schema_version", "pkg_router_version",
            "range_ledger_schema_version", "ve_n1_replay_version", "bar_count", "n_guards")}
        d["param_provenance"] = dict(self.param_provenance)
        d["occupancy"] = dict(self.occupancy)
        d["safety_guards_register"] = list(SAFETY_GUARDS_REGISTER)
        return d


@_dc.dataclass(frozen=True, slots=True)
class RangeSnapshotV3:
    range_snapshot_schema_version: str
    range_config_schema_version: str
    n1_identity_fingerprint: str
    range_spec_id: str
    config_hash: str
    n1_snapshot: Any
    range_state: dict[str, Any]


class RangeSnapshotErrorV3(Exception):
    pass


class RangeSemanticEngineV3:
    """Motorul 0.4.0: N1 (0.1.1, NEATINS) + `RangeSemanticProducerV3` (0.4.0, NOU) — orchestrare, NU
    reimplementare."""

    def __init__(self, *, symbol: str, timeframe: str, bar_interval_seconds: int,
                 implementation_commit: str, range_config: RangeConfigV3,
                 **kwargs: Any) -> None:
        self._n1 = N1IncrementalReplayEngine(
            symbol=symbol, timeframe=timeframe, bar_interval_seconds=bar_interval_seconds,
            implementation_commit=implementation_commit, **kwargs)
        self._cfg = range_config
        self._range = RangeSemanticProducerV3(self._cfg)
        self._symbol = symbol

    @property
    def n1(self) -> N1IncrementalReplayEngine:
        return self._n1

    @property
    def range_config(self) -> RangeConfigV3:
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
            predecessor_version=PREDECESSOR_0_3_1_VERSION, predecessor_wheel_sha256=PREDECESSOR_0_3_1_WHEEL_SHA256,
            predecessor_build_commit=PREDECESSOR_0_3_1_BUILD_COMMIT,
            predecessor_delivery_commit=PREDECESSOR_0_3_1_DELIVERY_COMMIT,
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
            range_producer_version=RANGE_PRODUCER_VERSION_V3,
            pkg_n1_contract_version=PKG_N1_CONTRACT_VERSION_V2,
            pkg_raw_axis_schema_version=PKG_RAW_AXIS_SCHEMA_VERSION_V2, pkg_router_version=PKG_ROUTER_VERSION_V2,
            range_ledger_schema_version=RANGE_LEDGER_SCHEMA_VERSION_V3, ve_n1_replay_version=VE_N1_REPLAY_VERSION,
            bar_count=len(records), n_guards=n_guards, occupancy=dict(occ),
            confirmed_segments=confirmed, records=tuple(records))

    # ── snapshot / restore 0.4.0 (mărginit, fail-closed, refuză migrare implicită de la 0.2.0/0.3.0/0.3.1) ──
    def snapshot(self) -> RangeSnapshotV3:
        return RangeSnapshotV3(
            range_snapshot_schema_version=RANGE_SNAPSHOT_SCHEMA_VERSION_V3,
            range_config_schema_version=RANGE_CONFIG_SCHEMA_VERSION_V3,
            n1_identity_fingerprint=self._n1.identity.fingerprint(),
            range_spec_id=self._cfg.range_spec_id(), config_hash=self._cfg.config_hash(),
            n1_snapshot=self._n1.snapshot(), range_state=self._range.snapshot_state())

    def restore(self, snapshot: Any) -> None:
        if isinstance(snapshot, (RangeSnapshotV1, RangeSnapshotV2_030, RangeSnapshotV2_031)):
            raise RangeSnapshotErrorV3(
                "refuz: snapshot dintr-o versiune ANTERIOARĂ (0.2.0/0.3.0/0.3.1) NU poate fi restaurat "
                "într-un motor 0.4.0 — migrare explicită necesară, niciun rebuild parțial acceptat")
        if not isinstance(snapshot, RangeSnapshotV3):
            raise RangeSnapshotErrorV3(f"snapshot de tip necunoscut: {type(snapshot).__name__!r}")
        if snapshot.range_snapshot_schema_version != RANGE_SNAPSHOT_SCHEMA_VERSION_V3:
            raise RangeSnapshotErrorV3(
                f"versiune de schemă snapshot incompatibilă: {snapshot.range_snapshot_schema_version!r} != "
                f"{RANGE_SNAPSHOT_SCHEMA_VERSION_V3!r}")
        if snapshot.n1_identity_fingerprint != self._n1.identity.fingerprint():
            raise RangeSnapshotErrorV3("identitate N1 incompatibilă")
        if snapshot.range_spec_id != self._cfg.range_spec_id() or snapshot.config_hash != self._cfg.config_hash():
            raise RangeSnapshotErrorV3("range_spec_id / config_hash incompatibil")
        # construiește + validează starea NOUĂ într-un producător IZOLAT înainte de a atinge orice stare
        # existentă (N1 sau self._range) — restore e ATOMIC: totul sau nimic, fără desincronizare pe eșec parțial.
        fresh = RangeSemanticProducerV3(self._cfg)
        try:
            fresh.restore_state(snapshot.range_state)
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise RangeSnapshotErrorV3(f"snapshot range_state corupt/incomplet: {exc!r}") from exc
        self._n1.restore(snapshot.n1_snapshot)
        self._range = fresh

    def reset(self) -> None:
        self._n1.reset()
        self._range = RangeSemanticProducerV3(self._cfg)
