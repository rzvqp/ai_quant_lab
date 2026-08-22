"""RangeSemanticEngineVNext -- composes N1 (0.1.1, UNTOUCHED) + `RangeSemanticProducerVNext` with
`ConfigVNext`. Direct mirror of `range_engine_v4_4.py`/`range_engine_v4_5.py` (no N1 line reimplemented,
canonical ATR imported from N1 unchanged) -- only the producer/config/result types differ. Additive,
isolated, no wheel bump (mandate `VE-RANGE-LIFECYCLE-VNEXT-MULTI-CANDIDATE-RESEARCH-001`)."""
from __future__ import annotations

import dataclasses as _dc
import hashlib as _hashlib
from collections import Counter
from typing import Any

from .incremental import N1IncrementalReplayEngine, _bar_parts, _identity_mod
from .range_semantic_vnext import (
    ConfigVNext, ConfigNotRatifiedErrorV43, ContractErrorV43, RangeSemanticProducerVNext,
    RangeSemanticResultVNext, RangeEventV43, SNAPSHOT_CONTRACT_MISMATCH,
    RANGE_HIERARCHICAL_VNEXT_NORMATIVE_CONFIG_ID,
)


@_dc.dataclass(frozen=True, slots=True)
class RangeReplayRecordVNext:
    bar_index: int
    ts_close: int
    n1_output_fingerprint: str
    n1_direction: str | None
    n1_structure: str | None
    macro_id: int | None
    macro_reason: str
    macro_state: str | None
    macro_weakening_reason: str | None
    macro_boundary_upper: float | None
    macro_boundary_lower: float | None
    macro_confirm_ts: int | None
    macro_role: str | None
    macro_continued_from_id: int | None
    regime: str | None
    internal_id: int | None
    internal_reason: str | None
    internal_state: str | None
    internal_boundary_upper: float | None
    internal_boundary_lower: float | None
    internal_role: str | None
    active_macro_count: int
    active_macro_ids: tuple[int, ...]
    active_internal_count: int
    events: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return _dc.asdict(self)


@_dc.dataclass(frozen=True, slots=True)
class RangeLedgerVNext:
    run_hash: str
    contract_version: str
    config_id: str
    data_identity: str
    n1_evaluation_identity_fingerprint: str
    n1_baseline_version: str
    predecessor_wheel_sha256: str
    predecessor_version: str
    bar_count: int
    occupancy: dict[str, int]
    macro_history: tuple[dict[str, Any], ...]
    internal_history: tuple[dict[str, Any], ...]
    records: tuple[RangeReplayRecordVNext, ...]

    def header(self) -> dict[str, Any]:
        return {k: getattr(self, k) for k in (
            "run_hash", "contract_version", "config_id", "data_identity",
            "n1_evaluation_identity_fingerprint", "n1_baseline_version",
            "predecessor_wheel_sha256", "predecessor_version", "bar_count", "occupancy")}


@_dc.dataclass(frozen=True, slots=True)
class RangeSnapshotVNext:
    contract_version: str
    config_id: str
    n1_identity_fingerprint: str
    n1_snapshot: Any
    range_state: dict[str, Any]


class RangeSnapshotErrorVNext(Exception):
    pass


class RangeSemanticEngineVNext:
    """Fails closed: mismatched `config_id`, missing `acknowledge_construction_only`, a snapshot of any
    other type/version/config/fingerprint. No implicit migration, no partial rebuild -- new state is built
    and VALIDATED in an ISOLATED producer before either N1 or `self._range` is touched (same discipline as
    every prior `RangeSemanticEngine*`)."""

    def __init__(self, *, symbol: str, timeframe: str, bar_interval_seconds: int,
                 implementation_commit: str, range_config: ConfigVNext,
                 acknowledge_construction_only: bool = False, **kwargs: Any) -> None:
        if not acknowledge_construction_only:
            raise ConfigNotRatifiedErrorV43(
                "RangeSemanticEngineVNext is a RESEARCH PROTOTYPE -- construction refuses without explicit "
                "acknowledge_construction_only=True (mandate: no Strategy Catalog/Alpha/AI Trader/"
                "LIVE_SHADOW/broker promotion authorized by this mandate; candidate engineering artifact "
                "requiring independent validation before any ratification)")
        if range_config.config_id() != RANGE_HIERARCHICAL_VNEXT_NORMATIVE_CONFIG_ID:
            raise ContractErrorV43(
                f"CONFIG_ID_MISMATCH: {range_config.config_id()} != normative "
                f"{RANGE_HIERARCHICAL_VNEXT_NORMATIVE_CONFIG_ID}")
        self._n1 = N1IncrementalReplayEngine(
            symbol=symbol, timeframe=timeframe, bar_interval_seconds=bar_interval_seconds,
            implementation_commit=implementation_commit, **kwargs)
        self._cfg = range_config
        self._range = RangeSemanticProducerVNext(self._cfg)
        self._symbol = symbol

    @property
    def n1(self) -> N1IncrementalReplayEngine:
        return self._n1

    @property
    def range_config(self) -> ConfigVNext:
        return self._cfg

    @property
    def bars_observed(self) -> int:
        return self._n1.bars_observed

    @property
    def macro_history(self) -> tuple[dict[str, Any], ...]:
        return self._range.macro_history

    @property
    def internal_history(self) -> tuple[dict[str, Any], ...]:
        return self._range.internal_history

    @property
    def active_macros(self) -> tuple[dict[str, Any], ...]:
        return self._range.active_macros

    def observe_closed_bar(self, bar: Any, *, as_of: int | None = None
                           ) -> tuple[Any, RangeSemanticResultVNext, list[RangeEventV43]]:
        n1_result = self._n1.observe_closed_bar(bar, as_of=as_of)
        atr = self._n1._axes_builder.atr14()
        range_result, events = self._range.observe(
            ts_close=bar.ts_close, open_=bar.open, high=bar.high, low=bar.low, close=bar.close, atr=atr)
        return n1_result, range_result, events

    def replay_batch(self, bars: Any, *, as_of: int | None = None) -> RangeLedgerVNext:
        records: list[RangeReplayRecordVNext] = []
        occ: Counter[str] = Counter()
        for bar in bars:
            n1_result, range_result, events = self.observe_closed_bar(bar, as_of=as_of)
            ev_dicts = tuple(_dc.asdict(e) for e in events)
            for e in events:
                occ[e.kind] += 1
            occ[f"MACRO_{range_result.macro_reason}"] += 1
            occ[f"INTERNAL_{range_result.internal_reason}"] += 1
            records.append(RangeReplayRecordVNext(
                bar_index=range_result.bar_index, ts_close=range_result.ts_close,
                n1_output_fingerprint=n1_result.output_fingerprint,
                n1_direction=n1_result.raw_axes.direction, n1_structure=n1_result.raw_axes.structure,
                macro_id=range_result.macro_id, macro_reason=range_result.macro_reason,
                macro_state=range_result.macro_state,
                macro_weakening_reason=range_result.macro_weakening_reason,
                macro_boundary_upper=range_result.macro_boundary_upper,
                macro_boundary_lower=range_result.macro_boundary_lower,
                macro_confirm_ts=range_result.macro_confirm_ts, macro_role=range_result.macro_role,
                macro_continued_from_id=range_result.macro_continued_from_id,
                regime=range_result.regime,
                internal_id=range_result.internal_id, internal_reason=range_result.internal_reason,
                internal_state=range_result.internal_state,
                internal_boundary_upper=range_result.internal_boundary_upper,
                internal_boundary_lower=range_result.internal_boundary_lower,
                internal_role=range_result.internal_role,
                active_macro_count=range_result.active_macro_count,
                active_macro_ids=range_result.active_macro_ids,
                active_internal_count=range_result.active_internal_count,
                events=ev_dicts))
        bars_tuple = tuple(bars)
        data_identity = _identity_mod.bars_content_hash(bars_tuple, bar_to_parts=_bar_parts)
        run_hash_payload = f"{self._cfg.config_id()}|{data_identity}"
        run_hash = _hashlib.sha256(run_hash_payload.encode()).hexdigest()
        return RangeLedgerVNext(
            run_hash=run_hash, contract_version=self._cfg.contract_version, config_id=self._cfg.config_id(),
            data_identity=data_identity, n1_evaluation_identity_fingerprint=self._n1.identity.fingerprint(),
            n1_baseline_version="0.1.1",
            predecessor_wheel_sha256=self._cfg.atr_provenance_wheel_sha256,
            predecessor_version="0.4.1",
            bar_count=len(records), occupancy=dict(occ),
            macro_history=self._range.macro_history, internal_history=self._range.internal_history,
            records=tuple(records))

    def snapshot(self) -> RangeSnapshotVNext:
        return RangeSnapshotVNext(
            contract_version=self._cfg.contract_version, config_id=self._cfg.config_id(),
            n1_identity_fingerprint=self._n1.identity.fingerprint(),
            n1_snapshot=self._n1.snapshot(), range_state=self._range.snapshot_state())

    def restore(self, snapshot: Any) -> None:
        if not isinstance(snapshot, RangeSnapshotVNext):
            raise RangeSnapshotErrorVNext(
                f"refusing: snapshot of type {type(snapshot).__name__!r}, not RangeSnapshotVNext -- no "
                "implicit migration from any other version, no partial rebuild accepted")
        if snapshot.contract_version != self._cfg.contract_version or snapshot.config_id != self._cfg.config_id():
            raise RangeSnapshotErrorVNext(SNAPSHOT_CONTRACT_MISMATCH)
        if snapshot.n1_identity_fingerprint != self._n1.identity.fingerprint():
            raise RangeSnapshotErrorVNext("incompatible N1 identity")
        fresh = RangeSemanticProducerVNext(self._cfg)
        try:
            fresh.restore_state(snapshot.range_state)
        except (KeyError, TypeError, ValueError, AttributeError, ContractErrorV43) as exc:
            raise RangeSnapshotErrorVNext(f"corrupt/incomplete range_state snapshot: {exc!r}") from exc
        self._n1.restore(snapshot.n1_snapshot)
        self._range = fresh

    def reset(self) -> None:
        self._n1.reset()
        self._range = RangeSemanticProducerVNext(self._cfg)
