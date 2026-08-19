"""RangeSemanticEngineV43 (prototip `range-hierarchical-v4.3`) — compune N1 (0.1.1, NEATINS) +
`RangeSemanticProducerV43` (nou, izolat) cu `ConfigV43`. Nicio linie din motorul N1 nu e reimplementată —
doar orchestrarea + identitatea/ledger-ul/snapshot-ul proprii acestui prototip. ATR canonic IMPORTAT din N1
(`self._n1._axes_builder.atr14()`), nu reimplementat — identic cu convenția V3/V3.1.

Prototip, NU wheel — vezi mandatul CEO "IMPLEMENTARE PROTOTIP RANGE HIERARCHICAL V4.3": autorizat exclusiv
pt. construire + evaluare, nu integrare/tranzacționare. `VE_N1_REPLAY_VERSION` (0.4.1) rămâne NEATINS — acest
modul e ADITIV, izolat, fără bump de versiune publică, fără wheel, fără atingere `release/`/`SHA256SUMS`.

Refuz fail-closed la restore: snapshot dintr-un alt tip (orice altă versiune RANGE — V1/V2/V2.1/V3/V3.1 sau
un viitor V4.x), sau cu `contract_version`/`config_id` nepotrivit. Nicio migrare implicită, niciun rebuild
parțial: starea nouă e construită și VALIDATĂ într-un producător IZOLAT înainte ca N1 sau `self._range` să
fie atinse.
"""
from __future__ import annotations

import dataclasses as _dc
from collections import Counter
from typing import Any

from .incremental import N1IncrementalReplayEngine, _bar_parts, _identity_mod
from .range_semantic_v4_3 import (
    ConfigV43, ConfigNotRatifiedErrorV43, ContractErrorV43, RangeSemanticProducerV43,
    RangeSemanticResultV43, RangeEventV43, SNAPSHOT_CONTRACT_MISMATCH,
    RANGE_HIERARCHICAL_V4_3_NORMATIVE_CONFIG_ID,
)


def _trend_context(direction: str | None) -> str | None:
    return direction


@_dc.dataclass(frozen=True, slots=True)
class RangeReplayRecordV43:
    bar_index: int
    ts_close: int
    n1_output_fingerprint: str
    n1_direction: str | None
    n1_structure: str | None
    macro_id: int | None
    macro_reason: str
    macro_state: str | None
    macro_boundary_upper: float | None
    macro_boundary_lower: float | None
    macro_confirm_ts: int | None
    macro_role: str | None
    regime: str | None
    internal_id: int | None
    internal_reason: str | None
    internal_state: str | None
    internal_boundary_upper: float | None
    internal_boundary_lower: float | None
    internal_role: str | None
    events: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return _dc.asdict(self)


@_dc.dataclass(frozen=True, slots=True)
class RangeLedgerV43:
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
    records: tuple[RangeReplayRecordV43, ...]

    def header(self) -> dict[str, Any]:
        return {k: getattr(self, k) for k in (
            "run_hash", "contract_version", "config_id", "data_identity",
            "n1_evaluation_identity_fingerprint", "n1_baseline_version",
            "predecessor_wheel_sha256", "predecessor_version", "bar_count", "occupancy")}


@_dc.dataclass(frozen=True, slots=True)
class RangeSnapshotV43:
    contract_version: str
    config_id: str
    n1_identity_fingerprint: str
    n1_snapshot: Any
    range_state: dict[str, Any]


class RangeSnapshotErrorV43(Exception):
    pass


class RangeSemanticEngineV43:
    """Prototip `range-hierarchical-v4.3`: N1 (0.1.1, NEATINS) + `RangeSemanticProducerV43` (nou) —
    orchestrare, NU reimplementare. `range_config` OBLIGATORIU la construcție; `config.config_id()` TREBUIE
    să fie identic cu valoarea normativă `24f72a60…` (Statistician/Red Team) — orice altă configurație e
    refuzată aici, la GRANIȚA de construcție a motorului (mandat §4: "orice nepotrivire cu config_id trebuie
    refuzată"). Config-ul brut (`ConfigV43`) rămâne testabil separat cu valori alternative (paritate cu
    harness-ul, gărzi de refuz), dar NU poate ajunge la un motor de producție live prin acest constructor."""

    def __init__(self, *, symbol: str, timeframe: str, bar_interval_seconds: int,
                 implementation_commit: str, range_config: ConfigV43,
                 acknowledge_construction_only: bool = False, **kwargs: Any) -> None:
        if not acknowledge_construction_only:
            raise ConfigNotRatifiedErrorV43(
                "RangeSemanticEngineV43 e un PROTOTIP -- construcția refuză fără "
                "acknowledge_construction_only=True explicit (mandat: nu wheel, nu integrare, nu tranzacționare)")
        if range_config.config_id() != RANGE_HIERARCHICAL_V4_3_NORMATIVE_CONFIG_ID:
            raise ContractErrorV43(
                f"CONFIG_ID_MISMATCH: {range_config.config_id()} != normativ "
                f"{RANGE_HIERARCHICAL_V4_3_NORMATIVE_CONFIG_ID} (mandat §4: orice nepotrivire e refuzată)")
        self._n1 = N1IncrementalReplayEngine(
            symbol=symbol, timeframe=timeframe, bar_interval_seconds=bar_interval_seconds,
            implementation_commit=implementation_commit, **kwargs)
        self._cfg = range_config
        self._range = RangeSemanticProducerV43(self._cfg)
        self._symbol = symbol

    @property
    def n1(self) -> N1IncrementalReplayEngine:
        return self._n1

    @property
    def range_config(self) -> ConfigV43:
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

    def observe_closed_bar(self, bar: Any, *, as_of: int | None = None
                           ) -> tuple[Any, RangeSemanticResultV43, list[RangeEventV43]]:
        n1_result = self._n1.observe_closed_bar(bar, as_of=as_of)
        atr = self._n1._axes_builder.atr14()
        tctx = _trend_context(n1_result.raw_axes.direction)
        range_result, events = self._range.observe(
            ts_close=bar.ts_close, open_=bar.open, high=bar.high, low=bar.low, close=bar.close,
            atr=atr, trend_context=tctx)
        return n1_result, range_result, events

    def replay_batch(self, bars: Any, *, as_of: int | None = None) -> RangeLedgerV43:
        records: list[RangeReplayRecordV43] = []
        occ: Counter[str] = Counter()
        for bar in bars:
            n1_result, range_result, events = self.observe_closed_bar(bar, as_of=as_of)
            ev_dicts = tuple(_dc.asdict(e) for e in events)
            for e in events:
                occ[e.kind] += 1
            occ[f"MACRO_{range_result.macro_reason}"] += 1
            occ[f"INTERNAL_{range_result.internal_reason}"] += 1
            records.append(RangeReplayRecordV43(
                bar_index=range_result.bar_index, ts_close=range_result.ts_close,
                n1_output_fingerprint=n1_result.output_fingerprint,
                n1_direction=n1_result.raw_axes.direction, n1_structure=n1_result.raw_axes.structure,
                macro_id=range_result.macro_id, macro_reason=range_result.macro_reason,
                macro_state=range_result.macro_state, macro_boundary_upper=range_result.macro_boundary_upper,
                macro_boundary_lower=range_result.macro_boundary_lower,
                macro_confirm_ts=range_result.macro_confirm_ts, macro_role=range_result.macro_role,
                regime=range_result.regime,
                internal_id=range_result.internal_id, internal_reason=range_result.internal_reason,
                internal_state=range_result.internal_state,
                internal_boundary_upper=range_result.internal_boundary_upper,
                internal_boundary_lower=range_result.internal_boundary_lower,
                internal_role=range_result.internal_role, events=ev_dicts))
        bars_tuple = tuple(bars)
        data_identity = _identity_mod.bars_content_hash(bars_tuple, bar_to_parts=_bar_parts)
        run_hash_payload = f"{self._cfg.config_id()}|{data_identity}"
        import hashlib as _hashlib
        run_hash = _hashlib.sha256(run_hash_payload.encode()).hexdigest()
        return RangeLedgerV43(
            run_hash=run_hash, contract_version=self._cfg.contract_version, config_id=self._cfg.config_id(),
            data_identity=data_identity, n1_evaluation_identity_fingerprint=self._n1.identity.fingerprint(),
            n1_baseline_version="0.1.1",
            predecessor_wheel_sha256=self._cfg.atr_provenance_wheel_sha256,
            predecessor_version="0.4.1",
            bar_count=len(records), occupancy=dict(occ),
            macro_history=self._range.macro_history, internal_history=self._range.internal_history,
            records=tuple(records))

    # ── snapshot / restore (mărginit, fail-closed) ──
    def snapshot(self) -> RangeSnapshotV43:
        return RangeSnapshotV43(
            contract_version=self._cfg.contract_version, config_id=self._cfg.config_id(),
            n1_identity_fingerprint=self._n1.identity.fingerprint(),
            n1_snapshot=self._n1.snapshot(), range_state=self._range.snapshot_state())

    def restore(self, snapshot: Any) -> None:
        if not isinstance(snapshot, RangeSnapshotV43):
            raise RangeSnapshotErrorV43(
                f"refuz: snapshot de tip {type(snapshot).__name__!r}, nu RangeSnapshotV43 -- nicio migrare "
                "implicită de la altă versiune/contract, niciun rebuild parțial acceptat")
        if snapshot.contract_version != self._cfg.contract_version or snapshot.config_id != self._cfg.config_id():
            raise RangeSnapshotErrorV43(SNAPSHOT_CONTRACT_MISMATCH)
        if snapshot.n1_identity_fingerprint != self._n1.identity.fingerprint():
            raise RangeSnapshotErrorV43("identitate N1 incompatibilă")
        fresh = RangeSemanticProducerV43(self._cfg)
        try:
            fresh.restore_state(snapshot.range_state)
        except (KeyError, TypeError, ValueError, AttributeError, ContractErrorV43) as exc:
            raise RangeSnapshotErrorV43(f"snapshot range_state corupt/incomplet: {exc!r}") from exc
        self._n1.restore(snapshot.n1_snapshot)
        self._range = fresh

    def reset(self) -> None:
        self._n1.reset()
        self._range = RangeSemanticProducerV43(self._cfg)
