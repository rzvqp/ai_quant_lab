from __future__ import annotations

from pathlib import Path

from ai_trader.execution_engine.ledger import OrderLedger
from ai_trader.execution_engine.types import OrderState
from ai_trader.order_manager.types import OrderExecutionResult
from ai_trader.order_manager.engine import process_approved_intent
from ai_trader.order_manager.journal import OrderManagerAuditJournal
from ai_trader.order_manager.tests._fixtures import (
    make_capabilities,
    make_connected_adapter,
    make_instrument,
    make_intent,
    make_ledger,
    make_portfolio,
)


def _run(
    tmp_path: Path, **intent_overrides: object,
) -> tuple[OrderExecutionResult, OrderLedger, OrderManagerAuditJournal]:
    intent = make_intent(**intent_overrides)
    instrument = make_instrument()
    caps = make_capabilities()
    adapter = make_connected_adapter(caps)
    ledger = make_ledger()
    journal = OrderManagerAuditJournal(tmp_path / "journal.jsonl")
    result = process_approved_intent(intent, instrument, make_portfolio(), caps, ledger, journal, adapter)
    return result, ledger, journal


def test_well_formed_intent_reaches_acknowledged_dry_run(tmp_path: Path) -> None:
    result, ledger, journal = _run(tmp_path)
    assert result.dry_run is True
    assert result.state is OrderState.ACKNOWLEDGED
    assert result.client_order_id in ledger
    assert len(journal) >= 3  # INTENT_RECEIVED, ORDER_BUILT, ORDER_STATE_*
    assert len(result.audit_event_ids) >= 3


def test_build_failure_returns_rejected_and_journals_the_failure(tmp_path: Path) -> None:
    result, ledger, journal = _run(tmp_path, symbol="EURUSD")  # mismatches the XAUUSD instrument fixture
    assert result.state is OrderState.REJECTED
    assert any("INSTRUMENT_SYMBOL_MISMATCH" in r for r in result.reasons)
    assert len(journal) == 2  # INTENT_RECEIVED, ORDER_BUILD_FAILED


def test_repeated_intent_is_an_idempotent_no_op_on_the_ledger(tmp_path: Path) -> None:
    intent = make_intent()
    instrument = make_instrument()
    caps = make_capabilities()
    adapter = make_connected_adapter(caps)
    ledger = make_ledger()
    journal = OrderManagerAuditJournal(tmp_path / "journal.jsonl")

    first = process_approved_intent(intent, instrument, make_portfolio(), caps, ledger, journal, adapter)
    second = process_approved_intent(intent, instrument, make_portfolio(), caps, ledger, journal, adapter)

    assert first.client_order_id == second.client_order_id
    assert len(ledger) == 1  # never double-submitted


def test_disconnected_adapter_produces_a_ledger_rejected_record_not_a_crash(tmp_path: Path) -> None:
    intent = make_intent()
    instrument = make_instrument()
    caps = make_capabilities()
    adapter = make_connected_adapter(caps)
    adapter.disconnect()
    ledger = make_ledger()
    journal = OrderManagerAuditJournal(tmp_path / "journal.jsonl")

    result = process_approved_intent(intent, instrument, make_portfolio(), caps, ledger, journal, adapter)
    assert result.state is OrderState.REJECTED
    assert any("NOT_CONNECTED" in r for r in result.reasons)


def test_result_never_reports_filled_this_phase(tmp_path: Path) -> None:
    result, _, _ = _run(tmp_path)
    assert result.state not in (OrderState.FILLED, OrderState.PARTIALLY_FILLED)
