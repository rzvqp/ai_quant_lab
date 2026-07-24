"""`process_approved_intent` -- Order Manager's single public entry point. Orchestrates: build (own,
narrow builder) -> validate + duplicate-guard + submit + track (REUSED, unmodified
`execution_engine.pipeline.submit_built_order`) -> journal every stage -> wrap into
`OrderExecutionResult`. Never raises; never sends a real order (Phase 3 scope, `DryRunBrokerAdapter`
only). Fail-closed: any build failure journals the failure and returns a REJECTED result.
"""

from __future__ import annotations

from ai_trader.execution_engine.ledger import OrderLedger
from ai_trader.execution_engine.pipeline import submit_built_order
from ai_trader.execution_engine.types import BrokerCapabilities, OrderState
from ai_trader.order_manager import reason_codes as rc
from ai_trader.order_manager.builder import build_order_request
from ai_trader.order_manager.dry_run_adapter import DryRunBrokerAdapter
from ai_trader.order_manager.journal import OrderAuditEvent, OrderManagerAuditJournal
from ai_trader.order_manager.types import ApprovedTradeIntent, OrderExecutionResult, OrderManagerConfig
from ai_trader.risk_manager.types import PortfolioState
from ai_trader.risk_manager_live.types import InstrumentSpecification


def _rejected_result(
    client_order_id: str, reason: str, audit_event_ids: tuple[str, ...],
) -> OrderExecutionResult:
    return OrderExecutionResult(
        order_request_id="", client_order_id=client_order_id, state=OrderState.REJECTED, dry_run=True,
        reasons=(reason,), audit_event_ids=audit_event_ids,
    )


def process_approved_intent(
    intent: ApprovedTradeIntent, instrument: InstrumentSpecification, portfolio: PortfolioState,
    caps: BrokerCapabilities, ledger: OrderLedger, journal: OrderManagerAuditJournal,
    adapter: DryRunBrokerAdapter, config: OrderManagerConfig | None = None,
) -> OrderExecutionResult:
    resolved_config = config if config is not None else OrderManagerConfig()
    event_ids: list[str] = []

    def _journal(stage: str, client_order_id: str, detail: dict[str, object]) -> None:
        event_ids.append(journal.append(OrderAuditEvent(
            stage=stage, client_order_id=client_order_id, correlation_id=intent.correlation_id,
            as_of=intent.as_of, detail=detail,
        )))

    _journal("INTENT_RECEIVED", "", {
        "proposal_id": intent.proposal_id, "strategy_id": intent.strategy_id, "symbol": intent.symbol,
        "direction": intent.direction.value, "volume": intent.volume, "magic_number": intent.magic_number,
        "comment": intent.comment,
    })

    build_outcome = build_order_request(intent, instrument, resolved_config)
    if not build_outcome.success or build_outcome.order is None:
        reason = build_outcome.reason or rc.BUILD_FAILED
        placeholder_client_order_id = f"{resolved_config.client_order_id_prefix}-LIVE-{intent.proposal_id}"
        _journal("ORDER_BUILD_FAILED", placeholder_client_order_id, {"reason": reason})
        return _rejected_result(placeholder_client_order_id, reason, tuple(event_ids))

    order = build_outcome.order
    _journal("ORDER_BUILT", order.client_order_id, {
        "order_request_id": order.order_request_id, "quantity": order.quantity,
        "limit_price": order.limit_price,
        "bracket": {
            "take_profit": order.bracket.take_profit if order.bracket else None,
            "stop_loss": order.bracket.stop_loss if order.bracket else None,
        },
        "magic_number": intent.magic_number, "comment": intent.comment,
        "monetary_risk": intent.monetary_risk,
    })

    record, fill, duplicate = submit_built_order(order, portfolio, caps, ledger, adapter)
    if record is None:
        _journal("ORDER_SUBMIT_INTERNAL_ERROR", order.client_order_id, {})
        return _rejected_result(order.client_order_id, "INTERNAL_ERROR: unexpected exception during submit", tuple(event_ids))

    stage = "ORDER_SUBMIT_DUPLICATE" if duplicate else f"ORDER_STATE_{record.state.value}"
    _journal(stage, order.client_order_id, {
        "state": record.state.value, "filled_qty": record.filled_qty, "reasons": list(record.reasons),
        "broker_order_id": record.broker_order_id, "duplicate": duplicate,
        "fill_price": fill.price if fill is not None else None,
    })

    return OrderExecutionResult(
        order_request_id=order.order_request_id, client_order_id=order.client_order_id,
        state=record.state, dry_run=True, filled_qty=record.filled_qty, avg_price=record.avg_price,
        reasons=record.reasons, audit_event_ids=tuple(event_ids),
    )
