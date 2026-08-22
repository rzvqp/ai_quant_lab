"""Position open/close detection and exit classification (mandate `AI-TRADER-S5-MT5-DEMO-UNATTENDED-
SOAK-001` sections 18-20).

**Deliberate scope boundary, disclosed not hidden**: this module NEVER issues a new `order_send` of its
own (proven by `soak/tests/test_broker_calls_confined_to_sanctioned_sites.py`'s own extension) -- it only
OBSERVES broker state (`positions_get`/`history_deals_get`) and classifies what already happened. The
immediately-prior mandate (`AI-TRADER-S5-MT5-DEMO-EXECUTION-001`) explicitly established "broker SL/TP
executes the canonical strategy... it does not reinterpret" as the sole exit mechanism -- this mandate
does not add active time-based horizon closing (S5's own `max_hold=48` bars research parameter) on top of
that, since doing so would mean this process deciding, on its own, to CLOSE a live position via a NEW
kind of broker call this codebase has never built or tested -- a materially new capability, not
authorized by this mandate's own text (which asks for HORIZON *classification*, not a new closing
mechanism). A position therefore remains open, protected by its own SL/TP, until the market hits one of
them; `past_horizon_still_open` is tracked and reported (section 29's own health-monitoring spirit) but
never acted on. `HORIZON` remains a valid member of the classification vocabulary (section 20 requires
it exist) but will not be produced by this module's own logic -- disclosed here, not silently omitted."""

from __future__ import annotations

import dataclasses
from typing import Any

from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.gateway_ext import MT5BridgeGateway
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import (
    CLOSED,
    OPEN_CONFIRMED,
    SUBMITTED_ACK,
    MT5ExecutionLedger,
    MT5ExecutionLedgerRecord,
)

TARGET = "TARGET"
STOP = "STOP"
HORIZON = "HORIZON"  # never produced by this module -- see module docstring
OTHER_BROKER_EXCEPTION = "OTHER_BROKER_EXCEPTION"

_PRICE_TOLERANCE = 0.50  # XAUUSD price units -- same tolerance reconciliation.py already uses
_TIME_WINDOW_SECONDS_BEFORE = 5
_TIME_WINDOW_SECONDS_AFTER = 3600


def _candidate_matches(candidate: Any, row: MT5ExecutionLedgerRecord) -> bool:
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


def detect_new_open_positions(*, ledger: MT5ExecutionLedger, gateway: MT5BridgeGateway, symbol: str) -> tuple[str, ...]:
    """For every identity whose latest state is `SUBMITTED_ACK` (order accepted by the broker, per
    `MT5DemoBrokerAdapter.submit_order`'s own retcode check) but not yet confirmed open as a real
    position, look for a matching live position. Records `OPEN_CONFIRMED` with the real position ticket
    once found -- returns the identities newly confirmed this call."""
    candidates_to_check = [cid for cid in ledger.all_client_order_ids() if ledger.latest_state_for(cid).state == SUBMITTED_ACK]  # type: ignore[union-attr]
    if not candidates_to_check:
        return ()

    positions = gateway.positions_get(symbol) or ()
    confirmed: list[str] = []
    for cid in candidates_to_check:
        row = ledger.latest_state_for(cid)
        assert row is not None
        matches = [p for p in positions if _candidate_matches(p, row)]
        if len(matches) == 1:
            ticket = getattr(matches[0], "ticket", None)
            ledger.record(dataclasses.replace(row, state=OPEN_CONFIRMED, broker_position_ticket=int(ticket) if ticket is not None else None))
            confirmed.append(cid)
    return tuple(confirmed)


def _classify_exit(*, exit_price: float, sl: float, tp: float | None) -> str:
    if abs(exit_price - sl) <= _PRICE_TOLERANCE:
        return STOP
    if tp is not None and abs(exit_price - tp) <= _PRICE_TOLERANCE:
        return TARGET
    return OTHER_BROKER_EXCEPTION


def detect_closed_positions(*, ledger: MT5ExecutionLedger, gateway: MT5BridgeGateway, symbol: str, now: int) -> tuple[str, ...]:
    """For every identity at `OPEN_CONFIRMED` whose `broker_position_ticket` no longer appears in live
    positions, searches recent deal history for the matching closing (`entry=1`/OUT) deal via
    `position_id`, classifies the exit, computes gross/net P/L and R-result, and records `CLOSED`.
    Returns the identities closed this call."""
    open_rows = [
        (cid, ledger.latest_state_for(cid)) for cid in ledger.all_client_order_ids()
        if ledger.latest_state_for(cid).state == OPEN_CONFIRMED  # type: ignore[union-attr]
    ]
    if not open_rows:
        return ()

    live_tickets = {getattr(p, "ticket", None) for p in (gateway.positions_get(symbol) or ())}
    still_open = {cid: row for cid, row in open_rows if row is not None and row.broker_position_ticket in live_tickets}
    vanished = {cid: row for cid, row in open_rows if cid not in still_open and row is not None}
    if not vanished:
        return ()

    deals = gateway.history_deals_get(now - 30 * 86400, now) or ()
    closed: list[str] = []
    for cid, row in vanished.items():
        assert row is not None
        exit_deal = next(
            (d for d in deals if getattr(d, "position_id", None) == row.broker_position_ticket and getattr(d, "entry", None) == 1),
            None,
        )
        if exit_deal is None:
            continue  # not yet visible in history (broker lag) -- retried on the next call, never guessed

        exit_price = float(getattr(exit_deal, "price", row.requested_entry))
        exit_ts = int(getattr(exit_deal, "time", now))
        gross_pl = float(getattr(exit_deal, "profit", 0.0))
        commission = float(getattr(exit_deal, "commission", 0.0))
        swap = float(getattr(exit_deal, "swap", 0.0))
        net_pl = gross_pl + commission + swap
        r_result = (net_pl / row.modeled_risk_money) if row.modeled_risk_money else None
        exit_reason = _classify_exit(exit_price=exit_price, sl=row.sl, tp=row.tp)

        ledger.record(dataclasses.replace(
            row, state=CLOSED, as_of=exit_ts, exit_reason=exit_reason, exit_price=exit_price,
            exit_timestamp=exit_ts, gross_pl_money=gross_pl, net_pl_money=net_pl, r_result=r_result,
            holding_seconds=max(0, exit_ts - row.as_of),
        ))
        closed.append(cid)
    return tuple(closed)
