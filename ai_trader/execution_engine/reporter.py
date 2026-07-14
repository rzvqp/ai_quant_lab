"""The Result/Reporter (``EXECUTION_ENGINE_ARCHITECTURE.md`` §5): builds ``ExecutionResult``/
``ExecutionReport`` from the Ledger's current state, for the Portfolio Manager and audit
(``EXECUTION_FAILURE_POLICY.md`` §4: fills reported as they are confirmed).
"""

from __future__ import annotations

from ai_trader.execution_engine.ledger import OrderLedger, OrderRecord
from ai_trader.execution_engine.types import TERMINAL_STATES, ExecutionReport, ExecutionResult, Fill


def result_from_record(record: OrderRecord) -> ExecutionResult | None:
    """Only terminal orders have a final ``ExecutionResult`` (§4 of the architecture: "the terminal
    outcome of one order")."""
    if record.state not in TERMINAL_STATES:
        return None
    return ExecutionResult(
        order_request_id=record.order.order_request_id,
        client_order_id=record.client_order_id,
        terminal_state=record.state,
        filled_qty=record.filled_qty,
        avg_price=record.avg_price,
        fees=0.0,
        reasons=record.reasons,
    )


def counts_by_state(records: tuple[OrderRecord, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        counts[record.state.value] = counts.get(record.state.value, 0) + 1
    return counts


def build_report(as_of: int, ledger: OrderLedger, fills: tuple[Fill, ...] = ()) -> ExecutionReport:
    records = ledger.all()
    results = tuple(r for r in (result_from_record(rec) for rec in records) if r is not None)
    return ExecutionReport(
        as_of=as_of, results=results, fills=fills, counts_by_state=counts_by_state(records),
    )
