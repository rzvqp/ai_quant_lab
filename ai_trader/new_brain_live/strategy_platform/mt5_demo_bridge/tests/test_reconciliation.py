from __future__ import annotations

import time
from pathlib import Path
from types import SimpleNamespace

from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import (
    PENDING_SUBMISSION,
    RECONCILED_EXISTING,
    RECONCILIATION_AMBIGUOUS,
    MT5ExecutionLedgerRecord,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.reconciliation import (
    any_blocked,
    reconcile_in_doubt_identities,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.tests._fixtures import FakeMT5BridgeGateway, make_ledger

SYMBOL = "XAUUSD"


def _pending_row(cid: str = "cid-1", *, as_of: int | None = None) -> MT5ExecutionLedgerRecord:
    now = as_of if as_of is not None else int(time.time())
    return MT5ExecutionLedgerRecord(
        client_order_id=cid, decision_id=f"{cid}-dec", state=PENDING_SUBMISSION, as_of=now,
        strategy_id="s5_c_2d587447_opening_range_breakout_long", strategy_version="rep_7472f3d412f2",
        symbol=SYMBOL, side="LONG", requested_entry=2000.0, actual_quote_bid=2000.0, actual_quote_ask=2000.1,
        sl=1990.0, tp=2030.0, requested_volume=1.0, modeled_risk_money=10.0, modeled_risk_fraction=0.001,
        account_trade_mode="AccountTradeMode.DEMO", evidence_fingerprint="fp-1", order_request_id=f"{cid}-req",
    )


def test_no_in_doubt_identities_returns_empty(tmp_path: Path) -> None:
    gw = FakeMT5BridgeGateway()
    ledger, store = make_ledger(tmp_path)
    outcomes = reconcile_in_doubt_identities(ledger=ledger, gateway=gw, symbol=SYMBOL)
    assert outcomes == ()
    store.close()


def test_zero_broker_candidates_resolves_as_never_accepted(tmp_path: Path) -> None:
    gw = FakeMT5BridgeGateway()  # no positions/orders/deals scripted -- empty
    ledger, store = make_ledger(tmp_path)
    ledger.record(_pending_row())

    outcomes = reconcile_in_doubt_identities(ledger=ledger, gateway=gw, symbol=SYMBOL)
    assert len(outcomes) == 1
    assert outcomes[0].resolved is True
    assert outcomes[0].blocked is False
    assert not any_blocked(outcomes)
    assert ledger.non_terminal_client_order_ids() == ()  # resolved -> no longer stuck in doubt
    store.close()


def test_exactly_one_matching_candidate_reconciles(tmp_path: Path) -> None:
    row = _pending_row()
    gw = FakeMT5BridgeGateway()
    gw._positions = (SimpleNamespace(symbol=SYMBOL, volume=1.0, price_open=2000.0, time=row.as_of, ticket=999888),)
    ledger, store = make_ledger(tmp_path)
    ledger.record(row)

    outcomes = reconcile_in_doubt_identities(ledger=ledger, gateway=gw, symbol=SYMBOL)
    assert len(outcomes) == 1
    assert outcomes[0].resolved is True
    assert outcomes[0].matched_ticket == 999888
    assert ledger.latest_state_for(row.client_order_id).state == RECONCILED_EXISTING  # type: ignore[union-attr]
    store.close()


def test_multiple_ambiguous_candidates_blocks_and_never_guesses(tmp_path: Path) -> None:
    row = _pending_row()
    gw = FakeMT5BridgeGateway()
    gw._positions = (
        SimpleNamespace(symbol=SYMBOL, volume=1.0, price_open=2000.0, time=row.as_of, ticket=1),
        SimpleNamespace(symbol=SYMBOL, volume=1.0, price_open=2000.1, time=row.as_of, ticket=2),
    )
    ledger, store = make_ledger(tmp_path)
    ledger.record(row)

    outcomes = reconcile_in_doubt_identities(ledger=ledger, gateway=gw, symbol=SYMBOL)
    assert len(outcomes) == 1
    assert outcomes[0].resolved is False
    assert outcomes[0].blocked is True
    assert outcomes[0].reason == RECONCILIATION_AMBIGUOUS
    assert any_blocked(outcomes)
    assert ledger.latest_state_for(row.client_order_id).state == RECONCILIATION_AMBIGUOUS  # type: ignore[union-attr]
    store.close()


def test_terminal_state_identities_are_never_reconsidered(tmp_path: Path) -> None:
    import dataclasses

    from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import SUBMITTED_ACK

    row = _pending_row()
    ledger, store = make_ledger(tmp_path)
    ledger.record(row)
    ledger.record(dataclasses.replace(row, state=SUBMITTED_ACK, broker_order_ticket=555))

    assert ledger.non_terminal_client_order_ids() == ()
    outcomes = reconcile_in_doubt_identities(ledger=ledger, gateway=FakeMT5BridgeGateway(), symbol=SYMBOL)
    assert outcomes == ()  # already resolved -- nothing to reconcile
    store.close()
