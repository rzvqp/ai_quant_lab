"""`LiveShadowJournal` -- CEO authorization 2026-08-17, section 6: a lightweight, DURABLE, classified
index over every LIVE_SHADOW event, separate from (and complementary to) `new_brain_bridge.telemetry.
NewBrainTelemetryLog`'s own rich per-node record. `NewBrainTelemetryLog` already persists the full
`EventIdentity` (market_event_id/trace_id/configuration_fingerprint/worker session+identity/tower
version/chain fingerprint/per-node N2-N3-N4 identities/ATR provenance) and every `NodeTrace` (reason
codes, latency, component version) for each `NewBrainOutcome` -- this module does NOT duplicate that; it
adds exactly the one thing `NewBrainTelemetryLog` doesn't have: a coarse, four-way CLASSIFICATION
(`LIVE_SHADOW_EVENT` / `LIVE_SHADOW_NO_TRADE` / `LIVE_SHADOW_CANDIDATE` / `LIVE_SHADOW_BLOCKED_AT_BROKER`)
plus the broker-evidence fields (reached_broker_gate/broker_blocked/orders/positions) that only exist
downstream of `risk_gate.py`/`execution_shadow.py`, for fast operational scanning without re-parsing every
`NodeTrace` in the full telemetry log.

Same `SqliteStateStore` append-only engine every other journal in this codebase already uses -- no new
persistence mechanism. Never interprets or asserts anything about profit/edge (CEO's own explicit
instruction, section 6: "Nu declara profit sau edge din telemetria operationala") -- this module's own
`LiveShadowRecord` carries no P&L field at all, structurally, not merely by convention."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum

from ai_trader.persistent_state.store import SqliteStateStore

_DEFAULT_LOG_NAME = "new_brain_live.shadow_events"


class LiveShadowCategory(Enum):
    LIVE_SHADOW_EVENT = "LIVE_SHADOW_EVENT"
    LIVE_SHADOW_NO_TRADE = "LIVE_SHADOW_NO_TRADE"
    LIVE_SHADOW_CANDIDATE = "LIVE_SHADOW_CANDIDATE"
    LIVE_SHADOW_BLOCKED_AT_BROKER = "LIVE_SHADOW_BLOCKED_AT_BROKER"


@dataclass(frozen=True, slots=True, kw_only=True)
class LiveShadowRecord:
    category: LiveShadowCategory
    trace_id: str
    market_event_id: str
    strategy_id: str
    as_of: int
    terminal_reason_code: str
    decision: str | None
    """`None` when the decision never reached N6 (e.g. Router refusal) -- honest absence, never guessed."""
    reached_broker_gate: bool | None = None
    broker_blocked: bool | None = None
    order_send_calls: int | None = None
    orders_created: int | None = None
    positions_created: int | None = None


def _serialize(record: LiveShadowRecord) -> str:
    return json.dumps({
        "category": record.category.value, "trace_id": record.trace_id,
        "market_event_id": record.market_event_id, "strategy_id": record.strategy_id,
        "as_of": record.as_of, "terminal_reason_code": record.terminal_reason_code,
        "decision": record.decision, "reached_broker_gate": record.reached_broker_gate,
        "broker_blocked": record.broker_blocked, "order_send_calls": record.order_send_calls,
        "orders_created": record.orders_created, "positions_created": record.positions_created,
    })


def _deserialize(raw: str) -> LiveShadowRecord:
    data = json.loads(raw)
    return LiveShadowRecord(
        category=LiveShadowCategory(data["category"]), trace_id=str(data["trace_id"]),
        market_event_id=str(data["market_event_id"]), strategy_id=str(data["strategy_id"]),
        as_of=int(data["as_of"]), terminal_reason_code=str(data["terminal_reason_code"]),
        decision=None if data["decision"] is None else str(data["decision"]),
        reached_broker_gate=data["reached_broker_gate"], broker_blocked=data["broker_blocked"],
        order_send_calls=data["order_send_calls"], orders_created=data["orders_created"],
        positions_created=data["positions_created"],
    )


class LiveShadowJournal:
    def __init__(self, state_store: SqliteStateStore, log_name: str = _DEFAULT_LOG_NAME) -> None:
        self._state_store = state_store
        self._log_name = log_name
        self._entries = [_deserialize(payload) for payload in state_store.read_log_entries(log_name)]

    def record(self, record: LiveShadowRecord) -> None:
        self._entries.append(record)
        self._state_store.append_log_entry(self._log_name, _serialize(record))

    @property
    def entries(self) -> tuple[LiveShadowRecord, ...]:
        return tuple(self._entries)

    def counts_by_category(self) -> dict[str, int]:
        counts: dict[str, int] = {c.value: 0 for c in LiveShadowCategory}
        for record in self._entries:
            counts[record.category.value] += 1
        return counts
