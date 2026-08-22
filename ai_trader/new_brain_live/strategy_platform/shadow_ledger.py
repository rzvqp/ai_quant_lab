"""Canonical shadow-decision ledger (AI Trader New Brain Architecture mandate, section 21). One record
per evaluation cycle, sufficient to reconstruct the whole cycle without re-running it. Same
`SqliteStateStore` append-only engine every other journal in this codebase already uses
(`LiveShadowJournal`/`NewBrainTelemetryLog`) -- no new persistence mechanism invented here."""

from __future__ import annotations

import json
from dataclasses import dataclass

from ai_trader.persistent_state.store import SqliteStateStore

_DEFAULT_LOG_NAME = "strategy_platform.shadow_ledger"


@dataclass(frozen=True, slots=True, kw_only=True)
class StrategyPlatformFingerprints:
    """Section 27 -- bound to every record, enabling exact later reproduction."""

    market_intelligence_fingerprint: str  # MarketState.n1_output_fp
    market_state_schema_version: str
    catalog_version: str
    ev_engine_version: str
    risk_engine_version: str
    execution_adapter_version: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ShadowLedgerRecord:
    market_timestamp: int
    market_state_identity: str
    eligible_strategy_ids: tuple[str, ...]
    ineligible: tuple[tuple[str, str], ...]  # (strategy_id, reason_code)
    invalid_output: tuple[tuple[str, str], ...] = ()  # (strategy_id, error) -- section 37 "INVALID STRATEGY OUTPUT"
    hypothesis_dedup_keys: tuple[str, ...]  # "strategy_id|instrument|market_state_identity", one per hypothesis produced
    #: (strategy_id, "TRADE_DECISION"|"NO_TRADE", evidence_fingerprint). Third element added by mandate
    #: VE-S5-REAL-EV-RUNTIME-PACKAGING-001 section 20/23 -- "" when no validated evidence package was
    #: involved (Mock, a fixture, or an honest expected_edge=None), the evidence's own stable fingerprint
    #: otherwise, so a ledger row can never leave it ambiguous which evidence (if any) actually drove a
    #: decision. `_serialize`/`_deserialize` are tuple-arity-generic and need no change for this; a ledger
    #: row persisted before this field existed would deserialize as a 2-tuple -- nothing in this codebase
    #: destructures `ev_decisions` with a fixed-arity unpack, so this is non-breaking, and no live/
    #: production ledger predates this change (BROKER_ORDER_SUBMISSION has never been enabled).
    ev_decisions: tuple[tuple[str, str, str], ...]
    final_decision: str  # "TRADE" | "NO_TRADE"
    final_reason_codes: tuple[str, ...]
    hypothetical_order_intent: str | None  # "strategy_id|instrument|direction|entry|stop", None if NO_TRADE
    broker_submission_state: str  # "DISABLED_NEVER_REACHED" | "BLOCKED_AT_GATE" | risk_decision reason summary
    fingerprints: StrategyPlatformFingerprints


def _serialize(record: ShadowLedgerRecord) -> str:
    return json.dumps({
        "market_timestamp": record.market_timestamp, "market_state_identity": record.market_state_identity,
        "eligible_strategy_ids": list(record.eligible_strategy_ids),
        "ineligible": [list(pair) for pair in record.ineligible],
        "invalid_output": [list(pair) for pair in record.invalid_output],
        "hypothesis_dedup_keys": list(record.hypothesis_dedup_keys),
        "ev_decisions": [list(pair) for pair in record.ev_decisions],
        "final_decision": record.final_decision, "final_reason_codes": list(record.final_reason_codes),
        "hypothetical_order_intent": record.hypothetical_order_intent,
        "broker_submission_state": record.broker_submission_state,
        "fingerprints": {
            "market_intelligence_fingerprint": record.fingerprints.market_intelligence_fingerprint,
            "market_state_schema_version": record.fingerprints.market_state_schema_version,
            "catalog_version": record.fingerprints.catalog_version,
            "ev_engine_version": record.fingerprints.ev_engine_version,
            "risk_engine_version": record.fingerprints.risk_engine_version,
            "execution_adapter_version": record.fingerprints.execution_adapter_version,
        },
    })


def _deserialize(raw: str) -> ShadowLedgerRecord:
    data = json.loads(raw)
    fp = data["fingerprints"]
    return ShadowLedgerRecord(
        market_timestamp=int(data["market_timestamp"]), market_state_identity=str(data["market_state_identity"]),
        eligible_strategy_ids=tuple(data["eligible_strategy_ids"]),
        ineligible=tuple(tuple(pair) for pair in data["ineligible"]),
        invalid_output=tuple(tuple(pair) for pair in data.get("invalid_output", [])),
        hypothesis_dedup_keys=tuple(data["hypothesis_dedup_keys"]),
        ev_decisions=tuple(tuple(pair) for pair in data["ev_decisions"]),
        final_decision=str(data["final_decision"]), final_reason_codes=tuple(data["final_reason_codes"]),
        hypothetical_order_intent=data["hypothetical_order_intent"],
        broker_submission_state=str(data["broker_submission_state"]),
        fingerprints=StrategyPlatformFingerprints(
            market_intelligence_fingerprint=str(fp["market_intelligence_fingerprint"]),
            market_state_schema_version=str(fp["market_state_schema_version"]),
            catalog_version=str(fp["catalog_version"]), ev_engine_version=str(fp["ev_engine_version"]),
            risk_engine_version=str(fp["risk_engine_version"]),
            execution_adapter_version=str(fp["execution_adapter_version"]),
        ),
    )


class ShadowLedger:
    def __init__(self, state_store: SqliteStateStore, log_name: str = _DEFAULT_LOG_NAME) -> None:
        self._state_store = state_store
        self._log_name = log_name
        self._entries = [_deserialize(payload) for payload in state_store.read_log_entries(log_name)]

    def record(self, record: ShadowLedgerRecord) -> None:
        self._entries.append(record)
        self._state_store.append_log_entry(self._log_name, _serialize(record))

    @property
    def entries(self) -> tuple[ShadowLedgerRecord, ...]:
        return tuple(self._entries)
