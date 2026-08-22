"""Persisted, append-only S5 MT5 execution ledger (mandate sections 21-25). Same `SqliteStateStore`
append-only engine every other journal in this codebase already uses (`ShadowLedger`'s own precedent) --
no new persistence mechanism invented here. Unlike `ShadowLedger` (one row per evaluation cycle, written
once), this ledger records one row per STATE TRANSITION of a given `client_order_id` -- `PENDING_
SUBMISSION` written BEFORE `order_send` is ever called, then `SUBMITTED_ACK`/`SUBMITTED_REJECTED`/
`SUBMISSION_FAILED` after -- so a crash between "the broker accepted the order" and "this process
recorded that fact" is itself visible and auditable (a `client_order_id` stuck at `PENDING_SUBMISSION`
with no later row), rather than silently indistinguishable from "never attempted". `latest_state_for`
returns the most recent row for an identity -- the ledger's own append-only history is never mutated in
place, exactly `ShadowLedger`'s own discipline."""

from __future__ import annotations

import json
from dataclasses import dataclass

from ai_trader.persistent_state.store import SqliteStateStore

_DEFAULT_LOG_NAME = "strategy_platform.mt5_demo_bridge.execution_ledger"

PENDING_SUBMISSION = "PENDING_SUBMISSION"
SUBMITTED_ACK = "SUBMITTED_ACK"
SUBMITTED_REJECTED = "SUBMITTED_REJECTED"
SUBMISSION_FAILED = "SUBMISSION_FAILED"
RECONCILED_EXISTING = "RECONCILED_EXISTING"
RECONCILED_NEVER_ACCEPTED = "RECONCILED_NEVER_ACCEPTED"
RECONCILIATION_AMBIGUOUS = "RECONCILIATION_AMBIGUOUS"

#: RECONCILIATION_AMBIGUOUS is deliberately NOT terminal -- an unresolved ambiguity should be retried on
#: every subsequent reconciliation pass (e.g. a candidate position may close, resolving the ambiguity),
#: never permanently frozen. Preflight's own duplicate-identity check (`preflight.DUPLICATE_IDENTITY`) is
#: a SEPARATE, independent "any row exists at all" check -- an ambiguous identity is already blocked from
#: a fresh submission by that check regardless of this set's membership.
TERMINAL_STATES = frozenset({SUBMITTED_ACK, SUBMITTED_REJECTED, SUBMISSION_FAILED, RECONCILED_EXISTING, RECONCILED_NEVER_ACCEPTED})


@dataclass(frozen=True, slots=True, kw_only=True)
class MT5ExecutionLedgerRecord:
    client_order_id: str
    decision_id: str
    state: str
    as_of: int
    strategy_id: str
    strategy_version: str
    symbol: str
    side: str
    requested_entry: float
    actual_quote_bid: float | None
    actual_quote_ask: float | None
    sl: float
    tp: float | None
    requested_volume: float
    modeled_risk_money: float | None
    modeled_risk_fraction: float | None
    account_trade_mode: str
    evidence_fingerprint: str
    order_request_id: str
    broker_retcode: int | None = None
    broker_comment: str | None = None
    broker_order_ticket: int | None = None
    broker_deal_ticket: int | None = None
    filled_volume: float | None = None
    avg_price: float | None = None
    reason: str | None = None


def _serialize(r: MT5ExecutionLedgerRecord) -> str:
    return json.dumps({
        "client_order_id": r.client_order_id, "decision_id": r.decision_id, "state": r.state, "as_of": r.as_of,
        "strategy_id": r.strategy_id, "strategy_version": r.strategy_version, "symbol": r.symbol, "side": r.side,
        "requested_entry": r.requested_entry, "actual_quote_bid": r.actual_quote_bid, "actual_quote_ask": r.actual_quote_ask,
        "sl": r.sl, "tp": r.tp, "requested_volume": r.requested_volume,
        "modeled_risk_money": r.modeled_risk_money, "modeled_risk_fraction": r.modeled_risk_fraction,
        "account_trade_mode": r.account_trade_mode, "evidence_fingerprint": r.evidence_fingerprint,
        "order_request_id": r.order_request_id, "broker_retcode": r.broker_retcode, "broker_comment": r.broker_comment,
        "broker_order_ticket": r.broker_order_ticket, "broker_deal_ticket": r.broker_deal_ticket,
        "filled_volume": r.filled_volume, "avg_price": r.avg_price, "reason": r.reason,
    })


def _deserialize(raw: str) -> MT5ExecutionLedgerRecord:
    d = json.loads(raw)
    return MT5ExecutionLedgerRecord(**d)


class MT5ExecutionLedger:
    def __init__(self, state_store: SqliteStateStore, log_name: str = _DEFAULT_LOG_NAME) -> None:
        self._state_store = state_store
        self._log_name = log_name
        self._entries = [_deserialize(p) for p in state_store.read_log_entries(log_name)]

    def record(self, r: MT5ExecutionLedgerRecord) -> None:
        self._entries.append(r)
        self._state_store.append_log_entry(self._log_name, _serialize(r))

    @property
    def entries(self) -> tuple[MT5ExecutionLedgerRecord, ...]:
        return tuple(self._entries)

    def entries_for(self, client_order_id: str) -> tuple[MT5ExecutionLedgerRecord, ...]:
        return tuple(e for e in self._entries if e.client_order_id == client_order_id)

    def latest_state_for(self, client_order_id: str) -> MT5ExecutionLedgerRecord | None:
        rows = self.entries_for(client_order_id)
        return rows[-1] if rows else None

    def all_client_order_ids(self) -> tuple[str, ...]:
        seen: dict[str, None] = {}
        for e in self._entries:
            seen[e.client_order_id] = None
        return tuple(seen.keys())

    def non_terminal_client_order_ids(self) -> tuple[str, ...]:
        """Every identity whose LATEST recorded state is not yet terminal -- i.e. a submission that was
        started (`PENDING_SUBMISSION` written) but never reached a confirmed outcome in THIS ledger. On
        restart, these are exactly the identities `reconciliation.py` must resolve against broker state
        before any new submission may proceed (mandate section 25)."""
        return tuple(cid for cid in self.all_client_order_ids() if self.latest_state_for(cid).state not in TERMINAL_STATES)  # type: ignore[union-attr]
