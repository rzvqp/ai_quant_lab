"""`NewBrainTelemetryLog` -- Mandate 2, section 6 (CEO, 2026-08-14): "Aceeasi identitate de eveniment
prin TOATE nodurile: N1 -> Router -> Eligibility -> EV -> N6 -> Risk -> Execution. Persista: reason
codes, versiuni, latente, decizia fiecarui nod si CAUZA EXACTA a fiecarui NO_TRADE." Same
`SqliteStateStore` engine and append-only convention every other journal in this codebase already uses
(`structural_observer.journal.StructuralObservationLog`, `live_signal_source.journal.LiveSignalJournal`)
-- no new persistence mechanism.

**One record per `NewBrainOutcome`** (one per bar per catalog strategy) -- `EventIdentity` and every
`NodeTrace` produced for it travel together, so "the same identity through every node" is enforced by
the record's own shape, not by a convention callers could violate. `RiskManager`/`ExecutionAdapter`
node traces (from `risk_gate.py`/`execution_shadow.py`) are appended to the SAME list before persisting
-- see `record_outcome`'s own `extra_traces` parameter.

**The decision is summarized, never the raw `ve_brain.DecisionResponse` object** -- that type is
external and untyped; round-tripping it generically through JSON would either lose fidelity silently or
require this module to understand its internals (forbidden -- `ve_brain` is never modified, and its
shape is not this module's to assume stable). `DecisionSummary` captures exactly the fields the CEO's
own requirement names (decision, reason_codes) plus `configuration_fingerprint` for cross-referencing
against `EventIdentity`/`NodeTrace`."""

from __future__ import annotations

import json
from dataclasses import dataclass

from ai_trader.mandate2_readiness.event_identity import EventIdentity, NodeTrace
from ai_trader.new_brain_bridge.bridge import NewBrainOutcome
from ai_trader.persistent_state.store import SqliteStateStore

_DEFAULT_LOG_NAME = "new_brain_bridge.telemetry"


@dataclass(frozen=True, slots=True, kw_only=True)
class DecisionSummary:
    decision: str
    reason_codes: tuple[str, ...]
    configuration_fingerprint: str


@dataclass(frozen=True, slots=True, kw_only=True)
class TelemetryRecord:
    event_identity: EventIdentity
    strategy_id: str
    strategy_version: str
    node_traces: tuple[NodeTrace, ...]
    decision_summary: DecisionSummary | None


def _serialize_event_identity(ei: EventIdentity) -> dict[str, object]:
    return {
        "trace_id": ei.trace_id, "market_event_id": ei.market_event_id, "symbol": ei.symbol,
        "timeframe": ei.timeframe, "bar_id": ei.bar_id, "market_timestamp": ei.market_timestamp,
        "received_timestamp": ei.received_timestamp, "brain_version": ei.brain_version,
        "catalog_hash": ei.catalog_hash, "configuration_fingerprint": ei.configuration_fingerprint,
    }


def _deserialize_event_identity(data: dict[str, object]) -> EventIdentity:
    market_timestamp = data["market_timestamp"]
    received_timestamp = data["received_timestamp"]
    assert isinstance(market_timestamp, int) and isinstance(received_timestamp, int)
    return EventIdentity(
        trace_id=str(data["trace_id"]), market_event_id=str(data["market_event_id"]),
        symbol=str(data["symbol"]), timeframe=str(data["timeframe"]), bar_id=str(data["bar_id"]),
        market_timestamp=market_timestamp, received_timestamp=received_timestamp,
        brain_version=str(data["brain_version"]), catalog_hash=str(data["catalog_hash"]),
        configuration_fingerprint=str(data["configuration_fingerprint"]),
    )


def _serialize_node_trace(nt: NodeTrace) -> dict[str, object]:
    return {
        "trace_id": nt.trace_id, "node_name": nt.node_name, "input_fingerprint": nt.input_fingerprint,
        "output": nt.output, "reason_codes": list(nt.reason_codes), "latency_seconds": nt.latency_seconds,
        "component_version": nt.component_version,
    }


def _deserialize_node_trace(data: dict[str, object]) -> NodeTrace:
    reason_codes_raw = data["reason_codes"]
    latency_seconds = data["latency_seconds"]
    assert isinstance(reason_codes_raw, list)
    assert isinstance(latency_seconds, (int, float))
    return NodeTrace(
        trace_id=str(data["trace_id"]), node_name=str(data["node_name"]),
        input_fingerprint=str(data["input_fingerprint"]), output=str(data["output"]),
        reason_codes=tuple(str(rc) for rc in reason_codes_raw),
        latency_seconds=float(latency_seconds), component_version=str(data["component_version"]),
    )


def _serialize(record: TelemetryRecord) -> str:
    payload: dict[str, object] = {
        "event_identity": _serialize_event_identity(record.event_identity),
        "strategy_id": record.strategy_id, "strategy_version": record.strategy_version,
        "node_traces": [_serialize_node_trace(nt) for nt in record.node_traces],
        "decision_summary": None if record.decision_summary is None else {
            "decision": record.decision_summary.decision,
            "reason_codes": list(record.decision_summary.reason_codes),
            "configuration_fingerprint": record.decision_summary.configuration_fingerprint,
        },
    }
    return json.dumps(payload)


def _deserialize(raw: str) -> TelemetryRecord:
    data = json.loads(raw)
    decision_summary_data = data["decision_summary"]
    decision_summary = None
    if decision_summary_data is not None:
        decision_summary = DecisionSummary(
            decision=str(decision_summary_data["decision"]),
            reason_codes=tuple(str(rc) for rc in decision_summary_data["reason_codes"]),
            configuration_fingerprint=str(decision_summary_data["configuration_fingerprint"]),
        )
    return TelemetryRecord(
        event_identity=_deserialize_event_identity(data["event_identity"]),
        strategy_id=str(data["strategy_id"]), strategy_version=str(data["strategy_version"]),
        node_traces=tuple(_deserialize_node_trace(nt) for nt in data["node_traces"]),
        decision_summary=decision_summary,
    )


class NewBrainTelemetryLog:
    def __init__(
        self, state_store: SqliteStateStore | None = None, log_name: str = _DEFAULT_LOG_NAME,
    ) -> None:
        self._state_store = state_store
        self._log_name = log_name
        if state_store is None:
            self._entries: list[TelemetryRecord] = []
        else:
            self._entries = [_deserialize(payload) for payload in state_store.read_log_entries(log_name)]

    def record_outcome(self, outcome: NewBrainOutcome, extra_traces: tuple[NodeTrace, ...] = ()) -> None:
        """`extra_traces` -- `RiskManager`/`ExecutionAdapter`/`BrokerGate` `NodeTrace` entries produced
        downstream of `bridge.evaluate_bar` (by `risk_gate.py`/`execution_shadow.py`), appended to the
        SAME `trace_id`'s record so the complete N1-through-broker chain persists as one entry."""
        decision_summary = None
        if outcome.decision is not None:
            decision_summary = DecisionSummary(
                decision=str(outcome.decision.decision),
                reason_codes=tuple(str(rc) for rc in outcome.decision.reason_codes),
                configuration_fingerprint=str(outcome.decision.configuration_fingerprint),
            )
        record = TelemetryRecord(
            event_identity=outcome.event_identity, strategy_id=outcome.strategy_id,
            strategy_version=outcome.strategy_version, node_traces=outcome.node_traces + extra_traces,
            decision_summary=decision_summary,
        )
        self._entries.append(record)
        if self._state_store is not None:
            self._state_store.append_log_entry(self._log_name, _serialize(record))

    @property
    def entries(self) -> tuple[TelemetryRecord, ...]:
        return tuple(self._entries)

    def no_trade_causes(self) -> tuple[tuple[str, tuple[str, ...]], ...]:
        """(`trace_id`, `reason_codes`) for every persisted record whose decision was `NO_TRADE` or was
        never reached at all (Router/ATR refusal, no `decision_summary`) -- the CAUZA EXACTA the CEO's
        section 6 requires, read back from what was actually persisted, not recomputed."""
        out: list[tuple[str, tuple[str, ...]]] = []
        for record in self._entries:
            if record.decision_summary is not None and record.decision_summary.decision != "NO_TRADE":
                continue
            reasons = record.decision_summary.reason_codes if record.decision_summary is not None else tuple(
                rc for trace in record.node_traces for rc in trace.reason_codes
            )
            out.append((record.event_identity.trace_id, reasons))
        return tuple(out)
