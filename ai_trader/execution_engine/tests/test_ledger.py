"""Tests for :mod:`ai_trader.execution_engine.ledger`."""

from __future__ import annotations

from ai_trader.execution_engine.ledger import OrderLedger, OrderRecord
from ai_trader.execution_engine.tests.fixtures.fake_broker import make_capabilities
from ai_trader.execution_engine.tests.fixtures.fake_decision import make_allow_decision
from ai_trader.execution_engine.builder import build_order
from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.types import OrderState

CONFIG = ExecConfig()
CAPS = make_capabilities()


def _record(state: OrderState = OrderState.QUEUED, strategy_id: str = "S1") -> OrderRecord:
    decision, portfolio = make_allow_decision(strategy_id=strategy_id)
    outcome = build_order(decision, portfolio, CAPS, CONFIG)
    assert outcome.order is not None
    return OrderRecord(order=outcome.order, state=state)


class TestOrderRecord:
    def test_remaining_qty_is_quantity_minus_filled(self) -> None:
        record = _record()
        record.filled_qty = record.order.quantity * 0.4
        assert record.remaining_qty == record.order.quantity * 0.6

    def test_remaining_qty_never_negative(self) -> None:
        record = _record()
        record.filled_qty = record.order.quantity * 2  # overfilled defensively
        assert record.remaining_qty == 0.0

    def test_is_terminal_reflects_state(self) -> None:
        assert _record(OrderState.FILLED).is_terminal is True
        assert _record(OrderState.SUBMITTED).is_terminal is False


class TestOrderLedger:
    def test_put_and_get(self) -> None:
        ledger = OrderLedger()
        record = _record()
        ledger.put(record)
        assert ledger.get(record.client_order_id) is record

    def test_get_missing_returns_none(self) -> None:
        ledger = OrderLedger()
        assert ledger.get("unknown") is None

    def test_contains(self) -> None:
        ledger = OrderLedger()
        record = _record()
        assert record.client_order_id not in ledger
        ledger.put(record)
        assert record.client_order_id in ledger

    def test_len(self) -> None:
        ledger = OrderLedger()
        assert len(ledger) == 0
        ledger.put(_record())
        assert len(ledger) == 1

    def test_open_orders_excludes_terminal(self) -> None:
        ledger = OrderLedger()
        open_record = _record(OrderState.SUBMITTED, strategy_id="S1")
        terminal_decision_record = _record(OrderState.FILLED, strategy_id="S2")
        ledger.put(open_record)
        ledger.put(terminal_decision_record)
        open_ids = {r.client_order_id for r in ledger.open_orders()}
        assert open_record.client_order_id in open_ids
        assert terminal_decision_record.client_order_id not in open_ids

    def test_all_returns_every_record(self) -> None:
        ledger = OrderLedger()
        r1 = _record(OrderState.SUBMITTED)
        ledger.put(r1)
        assert ledger.all() == (r1,)

    def test_put_overwrites_existing_record_for_same_id(self) -> None:
        ledger = OrderLedger()
        record = _record(OrderState.SUBMITTED)
        ledger.put(record)
        record.state = OrderState.FILLED
        ledger.put(record)
        assert len(ledger) == 1
        fetched = ledger.get(record.client_order_id)
        assert fetched is not None
        assert fetched.state is OrderState.FILLED
