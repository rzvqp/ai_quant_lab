"""Tests for :mod:`ai_trader.execution_engine.reporter`."""

from __future__ import annotations

from ai_trader.execution_engine.builder import build_order
from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.ledger import OrderLedger, OrderRecord
from ai_trader.execution_engine.reporter import build_report, counts_by_state, result_from_record
from ai_trader.execution_engine.tests.fixtures.fake_broker import make_capabilities
from ai_trader.execution_engine.tests.fixtures.fake_decision import make_allow_decision
from ai_trader.execution_engine.types import OrderState

CONFIG = ExecConfig()
CAPS = make_capabilities()


def _record(strategy_id: str = "S1", state: OrderState = OrderState.SUBMITTED) -> OrderRecord:
    decision, portfolio = make_allow_decision(strategy_id=strategy_id)
    outcome = build_order(decision, portfolio, CAPS, CONFIG)
    assert outcome.order is not None
    return OrderRecord(order=outcome.order, state=state)


class TestResultFromRecord:
    def test_non_terminal_record_has_no_result(self) -> None:
        record = _record(state=OrderState.SUBMITTED)
        assert result_from_record(record) is None

    def test_terminal_record_has_a_result(self) -> None:
        record = _record(state=OrderState.FILLED)
        record.filled_qty = record.order.quantity
        result = result_from_record(record)
        assert result is not None
        assert result.terminal_state is OrderState.FILLED
        assert result.filled_qty == record.order.quantity


class TestCountsByState:
    def test_counts_each_state(self) -> None:
        records = (_record("S1", OrderState.FILLED), _record("S2", OrderState.REJECTED), _record("S3", OrderState.FILLED))
        counts = counts_by_state(records)
        assert counts == {"FILLED": 2, "REJECTED": 1}

    def test_empty_records(self) -> None:
        assert counts_by_state(()) == {}


class TestBuildReport:
    def test_report_includes_only_terminal_results(self) -> None:
        ledger = OrderLedger()
        terminal = _record("S1", OrderState.FILLED)
        terminal.filled_qty = terminal.order.quantity
        working = _record("S2", OrderState.SUBMITTED)
        ledger.put(terminal)
        ledger.put(working)
        report = build_report(as_of=123, ledger=ledger)
        assert len(report.results) == 1
        assert report.results[0].client_order_id == terminal.client_order_id
        assert report.counts_by_state == {"FILLED": 1, "SUBMITTED": 1}

    def test_report_carries_supplied_fills(self) -> None:
        from ai_trader.execution_engine.types import Fill
        from ai_trader.signal_engine.types import Direction

        ledger = OrderLedger()
        fill = Fill(client_order_id="CID-1", symbol="XAUUSD", direction=Direction.LONG, qty=1.0, price=100.0, as_of=1)
        report = build_report(as_of=1, ledger=ledger, fills=(fill,))
        assert report.fills == (fill,)

    def test_empty_ledger_produces_empty_report(self) -> None:
        report = build_report(as_of=1, ledger=OrderLedger())
        assert report.results == ()
        assert report.counts_by_state == {}
