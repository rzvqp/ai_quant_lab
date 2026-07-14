"""Tests for :mod:`ai_trader.execution_engine.reconciler`."""

from __future__ import annotations

from unittest.mock import patch

from ai_trader.execution_engine.builder import build_order
from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.ledger import OrderLedger, OrderRecord
from ai_trader.execution_engine.reconciler import (
    reconcile_all_open,
    reconcile_one,
    rebuild_from_broker,
    request_cancel,
)
from ai_trader.execution_engine.tests.fixtures.fake_broker import FakeBrokerAdapter, make_capabilities
from ai_trader.execution_engine.tests.fixtures.fake_decision import make_allow_decision
from ai_trader.execution_engine.types import BrokerOrderState, OrderState

CONFIG = ExecConfig()
CAPS = make_capabilities()


def _record(strategy_id: str = "S1", state: OrderState = OrderState.SUBMITTED) -> OrderRecord:
    decision, portfolio = make_allow_decision(strategy_id=strategy_id)
    outcome = build_order(decision, portfolio, CAPS, CONFIG)
    assert outcome.order is not None
    return OrderRecord(order=outcome.order, state=state)


class TestReconcileOne:
    def test_unknown_client_order_id_returns_none(self) -> None:
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS)
        updated, fill = reconcile_one(ledger, adapter, "unknown")
        assert updated is None
        assert fill is None

    def test_terminal_record_returns_unchanged_without_querying(self) -> None:
        ledger = OrderLedger()
        record = _record(state=OrderState.FILLED)
        ledger.put(record)
        adapter = FakeBrokerAdapter(caps=CAPS)
        updated, fill = reconcile_one(ledger, adapter, record.client_order_id)
        assert updated is record
        assert fill is None

    def test_broker_not_found_leaves_record_unchanged(self) -> None:
        ledger = OrderLedger()
        record = _record(state=OrderState.SUBMITTED)
        ledger.put(record)
        adapter = FakeBrokerAdapter(caps=CAPS)  # broker has no knowledge of this id
        updated, fill = reconcile_one(ledger, adapter, record.client_order_id)
        assert updated is record
        assert updated.state is OrderState.SUBMITTED
        assert fill is None

    def test_broker_reports_fill_and_ledger_is_updated(self) -> None:
        ledger = OrderLedger()
        record = _record(state=OrderState.SUBMITTED)
        ledger.put(record)
        adapter = FakeBrokerAdapter(caps=CAPS)
        adapter.push_fill(record.client_order_id, filled_qty=record.order.quantity, avg_price=100.0, full=True)
        updated, fill = reconcile_one(ledger, adapter, record.client_order_id)
        assert updated is not None and updated.state is OrderState.FILLED
        assert fill is not None
        assert ledger.get(record.client_order_id).state is OrderState.FILLED  # type: ignore[union-attr]


class TestReconcileAllOpen:
    def test_reconciles_every_open_order(self) -> None:
        ledger = OrderLedger()
        r1 = _record(strategy_id="S1", state=OrderState.SUBMITTED)
        r2 = _record(strategy_id="S2", state=OrderState.SUBMITTED)
        ledger.put(r1)
        ledger.put(r2)
        adapter = FakeBrokerAdapter(caps=CAPS)
        adapter.push_fill(r1.client_order_id, filled_qty=r1.order.quantity, avg_price=100.0, full=True)
        adapter.push_fill(r2.client_order_id, filled_qty=r2.order.quantity, avg_price=100.0, full=True)
        fills = reconcile_all_open(ledger, adapter)
        assert len(fills) == 2
        r1_after = ledger.get(r1.client_order_id)
        r2_after = ledger.get(r2.client_order_id)
        assert r1_after is not None and r1_after.state is OrderState.FILLED
        assert r2_after is not None and r2_after.state is OrderState.FILLED

    def test_terminal_orders_are_skipped(self) -> None:
        ledger = OrderLedger()
        terminal = _record(state=OrderState.FILLED)
        ledger.put(terminal)
        adapter = FakeBrokerAdapter(caps=CAPS)
        fills = reconcile_all_open(ledger, adapter)
        assert fills == ()

    def test_empty_ledger_returns_no_fills(self) -> None:
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS)
        assert reconcile_all_open(ledger, adapter) == ()


class TestRebuildFromBroker:
    def test_no_preexisting_orders_returns_no_orphans(self) -> None:
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS)
        orphaned = rebuild_from_broker(ledger, adapter)
        assert orphaned == ()

    def test_broker_order_unknown_to_ledger_is_reported_as_orphaned(self) -> None:
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS)
        adapter.seed_preexisting_order(
            BrokerOrderState(client_order_id="CID-ORPHAN", state=OrderState.ACKNOWLEDGED),
        )
        orphaned = rebuild_from_broker(ledger, adapter)
        assert orphaned == ("CID-ORPHAN",)

    def test_broker_order_known_to_ledger_is_reconciled_not_orphaned(self) -> None:
        ledger = OrderLedger()
        record = _record(state=OrderState.SUBMITTED)
        ledger.put(record)
        adapter = FakeBrokerAdapter(caps=CAPS)
        adapter.seed_preexisting_order(
            BrokerOrderState(client_order_id=record.client_order_id, state=OrderState.ACKNOWLEDGED),
        )
        orphaned = rebuild_from_broker(ledger, adapter)
        assert orphaned == ()


class TestExceptionSafety:
    """Regression guards (adversarial review, CRITICAL finding #2): every Broker Adapter call in this
    module must be exception-safe -- a single flaky broker call must never abort reconciling the rest
    of the open orders, and must never propagate past this module's own public functions."""

    def test_query_status_exception_is_treated_as_not_found(self) -> None:
        ledger = OrderLedger()
        record = _record(state=OrderState.SUBMITTED)
        ledger.put(record)
        adapter = FakeBrokerAdapter(caps=CAPS)
        with patch.object(adapter, "query_status", side_effect=RuntimeError("boom")):
            updated, fill = reconcile_one(ledger, adapter, record.client_order_id)
        assert updated is record  # unchanged, exactly like a genuine "not found"
        assert fill is None

    def test_reconcile_all_open_continues_past_one_broker_exception(self) -> None:
        ledger = OrderLedger()
        r1 = _record(strategy_id="S1", state=OrderState.SUBMITTED)
        r2 = _record(strategy_id="S2", state=OrderState.SUBMITTED)
        ledger.put(r1)
        ledger.put(r2)
        adapter = FakeBrokerAdapter(caps=CAPS)
        adapter.push_fill(r2.client_order_id, filled_qty=r2.order.quantity, avg_price=100.0, full=True)

        real_query_status = adapter.query_status

        def _flaky_query_status(client_order_id: str) -> BrokerOrderState | None:
            if client_order_id == r1.client_order_id:
                raise RuntimeError("boom")
            return real_query_status(client_order_id)

        with patch.object(adapter, "query_status", side_effect=_flaky_query_status):
            fills = reconcile_all_open(ledger, adapter)

        assert len(fills) == 1  # r1's failure didn't prevent r2 from being reconciled
        r1_after = ledger.get(r1.client_order_id)
        r2_after = ledger.get(r2.client_order_id)
        assert r1_after is not None and r1_after.state is OrderState.SUBMITTED  # unresolved, unchanged
        assert r2_after is not None and r2_after.state is OrderState.FILLED

    def test_query_open_orders_exception_degrades_to_no_preexisting_orders(self) -> None:
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS)
        with patch.object(adapter, "query_open_orders", side_effect=RuntimeError("boom")):
            orphaned = rebuild_from_broker(ledger, adapter)
        assert orphaned == ()

    def test_cancel_order_exception_still_reconciles_afterward(self) -> None:
        ledger = OrderLedger()
        record = _record(state=OrderState.SUBMITTED)
        ledger.put(record)
        adapter = FakeBrokerAdapter(caps=CAPS)
        adapter.push_fill(record.client_order_id, filled_qty=record.order.quantity, avg_price=100.0, full=True)
        with patch.object(adapter, "cancel_order", side_effect=RuntimeError("boom")):
            updated, fill = request_cancel(ledger, adapter, record.client_order_id)
        # the cancel call itself raised, but request_cancel still reconciled afterward and resolved
        # to the broker's true (already-filled) state -- never propagates, never leaves it SUBMITTED.
        assert updated is not None and updated.state is OrderState.FILLED
        assert fill is not None


class TestRequestCancel:
    def test_unknown_id_returns_none(self) -> None:
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS)
        updated, fill = request_cancel(ledger, adapter, "unknown")
        assert updated is None
        assert fill is None

    def test_terminal_record_is_untouched(self) -> None:
        ledger = OrderLedger()
        record = _record(state=OrderState.FILLED)
        ledger.put(record)
        adapter = FakeBrokerAdapter(caps=CAPS)
        updated, fill = request_cancel(ledger, adapter, record.client_order_id)
        assert updated is record
        assert fill is None

    def test_working_order_is_cancelled(self) -> None:
        ledger = OrderLedger()
        record = _record(state=OrderState.SUBMITTED)
        ledger.put(record)
        adapter = FakeBrokerAdapter(caps=CAPS)
        adapter._orders[record.client_order_id] = BrokerOrderState(
            client_order_id=record.client_order_id, state=OrderState.SUBMITTED,
        )
        updated, _fill = request_cancel(ledger, adapter, record.client_order_id)
        assert updated is not None and updated.state is OrderState.CANCELLED
