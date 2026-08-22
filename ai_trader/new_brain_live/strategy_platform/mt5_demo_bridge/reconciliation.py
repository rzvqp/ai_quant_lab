"""Restart reconciliation (mandate sections 24-26). On startup, and again before any submission that
follows a possible interruption, every `client_order_id` whose LATEST recorded state is `PENDING_
SUBMISSION` (i.e. this process began a submission but never recorded its confirmed outcome -- a crash
between `order_send` returning and the ledger write, the one genuine "in-doubt" window this design
cannot eliminate) MUST be resolved against real broker state before any NEW submission is permitted.

**Why this can only be heuristic, disclosed rather than hidden**: `MT5DemoBrokerAdapter.submit_order`
(reused unmodified from `mt5_demo_execution`) derives its own MT5 `comment` via `_comment_for(strategy_id,
decision_id) = f"{strategy_id}:{decision_id}"[:27]` -- S5's real `strategy_id`
(`s5_c_2d587447_opening_range_breakout_long`, 44 chars) alone already exceeds that 27-char limit, so
EVERY S5 order's broker-side comment is identical (a constant truncated prefix), not per-event-unique.
This module therefore does NOT attempt exact comment-based identity matching -- it can only confirm
"this position/order/deal belongs to the S5 family" from the comment, then narrow by symbol/side/volume/
approximate price/approximate time window against the specific in-doubt ledger row. If more than one
broker-side candidate remains ambiguous after narrowing, this module BLOCKS rather than guesses (mandate
section 25's own explicit allowance) -- it never silently picks one. If zero candidates remain, that is
treated as mechanical proof the original submission was never accepted (mandate section 24), and a fresh
attempt is permitted. For the ordinary (non-crash) case, no heuristic is needed at all: a `client_order_id`
already at a TERMINAL ledger state (`SUBMITTED_ACK` with its own recorded broker ticket) is resolved by
construction -- this module only ever has real work to do for the rare in-doubt window."""

from __future__ import annotations

import dataclasses
import time

from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.gateway_ext import MT5BridgeGateway
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import (
    RECONCILED_EXISTING,
    RECONCILED_NEVER_ACCEPTED,
    RECONCILIATION_AMBIGUOUS,
    MT5ExecutionLedger,
    MT5ExecutionLedgerRecord,
)

_PRICE_TOLERANCE = 0.50  # XAUUSD price units -- generous enough to survive normal slippage/spread drift
_TIME_WINDOW_SECONDS_BEFORE = 5
_TIME_WINDOW_SECONDS_AFTER = 3600  # a submission's fill/history record may lag its PENDING_SUBMISSION row


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ReconciliationOutcome:
    client_order_id: str
    resolved: bool
    matched_ticket: int | None = None
    blocked: bool = False
    reason: str | None = None


def _candidate_matches(candidate: object, row: MT5ExecutionLedgerRecord) -> bool:
    symbol = getattr(candidate, "symbol", None)
    volume = getattr(candidate, "volume", None)
    price_open = getattr(candidate, "price_open", getattr(candidate, "price", None))
    time_val = getattr(candidate, "time", None)
    if symbol != row.symbol:
        return False
    if volume is None or abs(float(volume) - row.requested_volume) > 1e-9:
        return False
    if price_open is not None and abs(float(price_open) - row.requested_entry) > _PRICE_TOLERANCE:
        return False
    if time_val is not None and not (row.as_of - _TIME_WINDOW_SECONDS_BEFORE <= int(time_val) <= row.as_of + _TIME_WINDOW_SECONDS_AFTER):
        return False
    return True


def reconcile_in_doubt_identities(
    *, ledger: MT5ExecutionLedger, gateway: MT5BridgeGateway, symbol: str,
) -> tuple[ReconciliationOutcome, ...]:
    """Must be called once, before the live runtime loop permits any NEW submission (mandate section 25)
    -- never assumes an empty local process state means an empty broker account."""
    in_doubt = ledger.non_terminal_client_order_ids()
    if not in_doubt:
        return ()

    positions = gateway.positions_get(symbol) or ()
    orders = gateway.orders_get(symbol) or ()
    now = int(time.time())
    deals = gateway.history_deals_get(now - 7 * 86400, now) or ()
    all_candidates = tuple(positions) + tuple(orders) + tuple(deals)

    outcomes: list[ReconciliationOutcome] = []
    for cid in in_doubt:
        row = ledger.latest_state_for(cid)
        assert row is not None
        matches = [c for c in all_candidates if _candidate_matches(c, row)]
        if not matches:
            # Mechanically proven the original submission was never accepted -- safe to permit a fresh
            # attempt for this identity (mandate section 24). A NEW ledger row is written (append-only,
            # same discipline as every other state transition) so this identity no longer shows up as
            # non-terminal/in-doubt on the NEXT reconciliation pass -- leaving it un-recorded would look
            # identical to "never checked" and force every future restart to re-derive the same answer.
            ledger.record(dataclasses.replace(row, state=RECONCILED_NEVER_ACCEPTED, as_of=now, reason="zero_broker_candidates"))
            outcomes.append(ReconciliationOutcome(client_order_id=cid, resolved=True, matched_ticket=None))
        elif len(matches) == 1:
            ticket = getattr(matches[0], "ticket", None) or getattr(matches[0], "order", None)
            ledger.record(dataclasses.replace(row, state=RECONCILED_EXISTING, as_of=now, broker_order_ticket=int(ticket) if ticket else None))
            outcomes.append(ReconciliationOutcome(client_order_id=cid, resolved=True, matched_ticket=int(ticket) if ticket else None))
        else:
            ledger.record(dataclasses.replace(row, state=RECONCILIATION_AMBIGUOUS, as_of=now, reason=f"{len(matches)}_candidates"))
            outcomes.append(ReconciliationOutcome(client_order_id=cid, resolved=False, blocked=True, reason=RECONCILIATION_AMBIGUOUS))
    return tuple(outcomes)


def any_blocked(outcomes: tuple[ReconciliationOutcome, ...]) -> bool:
    return any(o.blocked for o in outcomes)
