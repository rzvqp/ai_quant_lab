"""Tests for :mod:`ai_trader.execution_engine.lifecycle`."""

from __future__ import annotations

import pytest

from ai_trader.execution_engine.builder import build_order
from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.ledger import OrderRecord
from ai_trader.execution_engine.lifecycle import apply_broker_update, is_valid_broker_transition
from ai_trader.execution_engine.tests.fixtures.fake_broker import make_capabilities
from ai_trader.execution_engine.tests.fixtures.fake_decision import make_allow_decision
from ai_trader.execution_engine.types import BrokerOrderState, OrderState

CONFIG = ExecConfig()
CAPS = make_capabilities()


def _record(state: OrderState = OrderState.SUBMITTED) -> OrderRecord:
    decision, portfolio = make_allow_decision()
    outcome = build_order(decision, portfolio, CAPS, CONFIG)
    assert outcome.order is not None
    return OrderRecord(order=outcome.order, state=state)


class TestApplyBrokerUpdate:
    def test_full_fill_updates_state_and_returns_a_fill(self) -> None:
        record = _record(OrderState.SUBMITTED)
        broker_state = BrokerOrderState(
            client_order_id=record.client_order_id, state=OrderState.FILLED,
            filled_qty=record.order.quantity, avg_price=100.0,
        )
        updated, fill = apply_broker_update(record, broker_state)
        assert updated.state is OrderState.FILLED
        assert updated.filled_qty == record.order.quantity
        assert fill is not None
        assert fill.qty == record.order.quantity

    def test_partial_fill_accumulates(self) -> None:
        record = _record(OrderState.SUBMITTED)
        half = record.order.quantity / 2
        broker_state = BrokerOrderState(
            client_order_id=record.client_order_id, state=OrderState.PARTIALLY_FILLED,
            filled_qty=half, avg_price=100.0,
        )
        updated, fill = apply_broker_update(record, broker_state)
        assert updated.state is OrderState.PARTIALLY_FILLED
        assert updated.filled_qty == half
        assert fill is not None and fill.qty == half

        # a second update with MORE filled quantity reports only the DELTA as the new fill
        broker_state_2 = BrokerOrderState(
            client_order_id=record.client_order_id, state=OrderState.FILLED,
            filled_qty=record.order.quantity, avg_price=100.0,
        )
        updated_2, fill_2 = apply_broker_update(updated, broker_state_2)
        assert updated_2.state is OrderState.FILLED
        assert fill_2 is not None
        assert fill_2.qty == record.order.quantity - half

    def test_no_new_quantity_reports_no_fill(self) -> None:
        record = _record(OrderState.SUBMITTED)
        broker_state = BrokerOrderState(client_order_id=record.client_order_id, state=OrderState.ACKNOWLEDGED)
        updated, fill = apply_broker_update(record, broker_state)
        assert fill is None
        assert updated.state is OrderState.ACKNOWLEDGED

    def test_terminal_record_is_never_moved_by_a_further_update(self) -> None:
        record = _record(OrderState.FILLED)
        record.filled_qty = record.order.quantity
        broker_state = BrokerOrderState(client_order_id=record.client_order_id, state=OrderState.CANCELLED)
        updated, fill = apply_broker_update(record, broker_state)
        assert updated is record  # unchanged, same object
        assert updated.state is OrderState.FILLED  # never resurrected/overwritten
        assert fill is None

    def test_mismatched_client_order_id_is_a_no_op(self) -> None:
        record = _record(OrderState.SUBMITTED)
        broker_state = BrokerOrderState(client_order_id="SOMETHING_ELSE", state=OrderState.FILLED, filled_qty=1.0)
        updated, fill = apply_broker_update(record, broker_state)
        assert updated is record
        assert fill is None

    def test_reject_reason_is_recorded(self) -> None:
        record = _record(OrderState.SUBMITTED)
        broker_state = BrokerOrderState(client_order_id=record.client_order_id, state=OrderState.REJECTED, reason="MARGIN")
        updated, _fill = apply_broker_update(record, broker_state)
        assert updated.state is OrderState.REJECTED
        assert "MARGIN" in updated.reasons

    def test_idempotent_repeated_identical_update(self) -> None:
        record = _record(OrderState.SUBMITTED)
        broker_state = BrokerOrderState(
            client_order_id=record.client_order_id, state=OrderState.FILLED,
            filled_qty=record.order.quantity, avg_price=100.0,
        )
        updated_1, fill_1 = apply_broker_update(record, broker_state)
        updated_2, fill_2 = apply_broker_update(updated_1, broker_state)
        assert updated_2.state is OrderState.FILLED
        assert fill_2 is None  # no NEW quantity the second time

    def test_fill_without_avg_price_falls_back_to_the_orders_own_limit_price(self) -> None:
        """Regression guard (adversarial review, LOW finding): a malformed broker report (new filled
        quantity but no avg_price) must never fabricate a 0.0 "free trade" price when a better
        reference (the order's own limit_price) is available."""
        record = _record(OrderState.SUBMITTED)
        assert record.order.limit_price is not None
        broker_state = BrokerOrderState(
            client_order_id=record.client_order_id, state=OrderState.FILLED,
            filled_qty=record.order.quantity, avg_price=None,
        )
        _updated, fill = apply_broker_update(record, broker_state)
        assert fill is not None
        assert fill.price == record.order.limit_price
        assert fill.price != 0.0

    def test_fill_without_avg_price_or_limit_price_falls_back_to_zero(self) -> None:
        from dataclasses import replace

        record = _record(OrderState.SUBMITTED)
        record.order = replace(record.order, limit_price=None)  # e.g. a MARKET order
        broker_state = BrokerOrderState(
            client_order_id=record.client_order_id, state=OrderState.FILLED,
            filled_qty=record.order.quantity, avg_price=None,
        )
        _updated, fill = apply_broker_update(record, broker_state)
        assert fill is not None
        assert fill.price == 0.0  # last-resort fallback only, never silently masked as a real price


class TestUnexpectedTransitionIsAdvisoryOnly:
    """Regression guard (adversarial review, MEDIUM finding): ``is_valid_broker_transition`` was dead
    code (never called). It is now wired into ``apply_broker_update`` as an ADVISORY warning -- the
    update is still applied (the broker is always the source of truth), just logged."""

    def test_unexpected_transition_is_still_applied(self, caplog: "pytest.LogCaptureFixture") -> None:
        record = _record(OrderState.SUBMITTED)
        # SUBMITTED -> QUEUED is not in the documented transition table, but the broker is still
        # believed -- the update must be applied, not rejected.
        broker_state = BrokerOrderState(client_order_id=record.client_order_id, state=OrderState.QUEUED)
        updated, _fill = apply_broker_update(record, broker_state)
        assert updated.state is OrderState.QUEUED
        assert any("unexpected broker-reported transition" in msg for msg in caplog.messages)


class TestIsValidBrokerTransition:
    def test_terminal_current_accepts_nothing(self) -> None:
        assert is_valid_broker_transition(OrderState.FILLED, OrderState.CANCELLED) is False

    def test_submitted_to_acknowledged_is_valid(self) -> None:
        assert is_valid_broker_transition(OrderState.SUBMITTED, OrderState.ACKNOWLEDGED) is True

    def test_submitted_to_terminal_is_valid(self) -> None:
        assert is_valid_broker_transition(OrderState.SUBMITTED, OrderState.REJECTED) is True

    def test_acknowledged_to_partially_filled_is_valid(self) -> None:
        assert is_valid_broker_transition(OrderState.ACKNOWLEDGED, OrderState.PARTIALLY_FILLED) is True
