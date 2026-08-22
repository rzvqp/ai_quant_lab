"""Safety-stop monitor (mandate section 25). Thirteen named conditions; once ANY trips, `soak_loop.py`
blocks all NEW broker submissions -- persisted (survives restart, `SqliteStateStore` append-log, same
engine every other journal in this codebase uses) until explicitly cleared by a human via `clear()`
(never auto-called anywhere in this package). Existing owned positions are left alone, still protected by
their own canonical SL/TP -- a safety trip changes nothing about ALREADY-open positions (section 25's own
"should only be managed according to their canonical protective orders and ownership rules")."""

from __future__ import annotations

import dataclasses
import json

from ai_trader.persistent_state.store import SqliteStateStore

_DEFAULT_LOG_NAME = "strategy_platform.mt5_demo_bridge.soak.safety_events"

ACCOUNT_NOT_DEMO = "ACCOUNT_NOT_DEMO"
STRATEGY_IDENTITY_MISMATCH = "STRATEGY_IDENTITY_MISMATCH"
EVIDENCE_IDENTITY_MISMATCH = "EVIDENCE_IDENTITY_MISMATCH"
MISSING_PROBABILITY_INPUTS = "MISSING_PROBABILITY_INPUTS"
REAL_EV_FAILURE = "REAL_EV_FAILURE"
BROKER_RECONCILIATION_AMBIGUITY = "BROKER_RECONCILIATION_AMBIGUITY"
DUPLICATE_IDENTITY_CONFLICT = "DUPLICATE_IDENTITY_CONFLICT"
SL_UNAVAILABLE = "SL_UNAVAILABLE"
INVALID_SYMBOL_CONTRACT = "INVALID_SYMBOL_CONTRACT"
RISK_CALCULATION_INVALID = "RISK_CALCULATION_INVALID"
RISK_EXCEEDS_5_PERCENT = "RISK_EXCEEDS_5_PERCENT"
PERSISTENT_BROKER_API_CORRUPTION = "PERSISTENT_BROKER_API_CORRUPTION"
LEDGER_CORRUPTION = "LEDGER_CORRUPTION"

ALL_CONDITIONS = frozenset({
    ACCOUNT_NOT_DEMO, STRATEGY_IDENTITY_MISMATCH, EVIDENCE_IDENTITY_MISMATCH, MISSING_PROBABILITY_INPUTS,
    REAL_EV_FAILURE, BROKER_RECONCILIATION_AMBIGUITY, DUPLICATE_IDENTITY_CONFLICT, SL_UNAVAILABLE,
    INVALID_SYMBOL_CONTRACT, RISK_CALCULATION_INVALID, RISK_EXCEEDS_5_PERCENT,
    PERSISTENT_BROKER_API_CORRUPTION, LEDGER_CORRUPTION,
})


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SafetyEvent:
    kind: str  # "TRIP" | "CLEAR"
    condition: str | None  # None for a CLEAR event
    detail: str
    as_of: int


def _serialize(e: SafetyEvent) -> str:
    return json.dumps({"kind": e.kind, "condition": e.condition, "detail": e.detail, "as_of": e.as_of})


def _deserialize(raw: str) -> SafetyEvent:
    d = json.loads(raw)
    return SafetyEvent(**d)


class SafetyMonitor:
    def __init__(self, state_store: SqliteStateStore, log_name: str = _DEFAULT_LOG_NAME) -> None:
        self._state_store = state_store
        self._log_name = log_name
        self._events = [_deserialize(p) for p in state_store.read_log_entries(log_name)]

    @property
    def events(self) -> tuple[SafetyEvent, ...]:
        return tuple(self._events)

    def is_blocked(self) -> bool:
        return self._events != [] and self._events[-1].kind == "TRIP"

    def current_block(self) -> SafetyEvent | None:
        return self._events[-1] if self.is_blocked() else None

    def trip(self, condition: str, detail: str, *, at: int) -> None:
        if condition not in ALL_CONDITIONS:
            raise ValueError(f"unknown safety condition {condition!r} -- must be one of {sorted(ALL_CONDITIONS)}")
        if self.is_blocked():
            return  # already blocked -- the first trip is the one of record, never overwritten by a later one
        event = SafetyEvent(kind="TRIP", condition=condition, detail=detail, as_of=at)
        self._events.append(event)
        self._state_store.append_log_entry(self._log_name, _serialize(event))

    def clear(self, *, note: str, at: int) -> None:
        """Manual-only -- never called by `soak_loop.py` itself. An operator clears a trip after
        investigating; this module has no automatic self-clear path by design."""
        event = SafetyEvent(kind="CLEAR", condition=None, detail=note, as_of=at)
        self._events.append(event)
        self._state_store.append_log_entry(self._log_name, _serialize(event))
