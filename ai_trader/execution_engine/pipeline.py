"""The fixed per-decision execution pipeline (``EXECUTION_ENGINE_ARCHITECTURE.md`` §6): Intake -> Build
-> Duplicate guard -> Validate -> Submit -> initial track.

**Duplicate guard runs BEFORE validate**, the deliberate reverse of the architecture doc's own prose
ordering (§6 lists "3. Validate ... 4. Duplicate guard") -- a correctness fix, not a style choice: see
:func:`_validate_and_submit`'s own docstring for why re-validating an already-known order against a
possibly-changed ``portfolio`` can silently corrupt a terminal Ledger record. Build is still pure and
deterministic, so a genuine retry naturally re-derives the identical ``OrderRequest``; but validation is
now correctly skipped entirely (not merely re-run and ignored) for any ``client_order_id`` already known
to the Ledger, matching ``EXECUTION_API.md`` §5's own "a decision executes at most once" contract in
letter as well as spirit.

**Exception safety and single-implementation, applied from the start** (the explicit lesson carried
forward from the Risk Manager's own adversarial review, ``NEXT_SESSION.md`` §6/§9: "verify EVERY entry
point routes through the SAME validation/exception-safety helper"): :func:`execute_one` (decision-driven,
used by ``ExecutionEngine.execute``) and :func:`submit_built_order` (already-built-order-driven, used by
``ExecutionEngine.emergency_flatten`` for its synthesized reduce-only closing orders) both delegate the
duplicate-guard -> validate -> submit -> track chain to the SAME private helper, :func:`_validate_and_submit`,
and both are wrapped in their own ``try/except`` so one malformed decision/order can never abort a batch
of calls the caller may be looping over. No sibling entry point re-implements any part of this chain.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.execution_engine.broker_adapter import BrokerAdapter
from ai_trader.execution_engine.builder import build_order
from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.ledger import OrderLedger, OrderRecord
from ai_trader.execution_engine.lifecycle import apply_broker_update
from ai_trader.execution_engine.types import (
    BrokerCapabilities,
    Fill,
    OrderRequest,
    OrderState,
    OrderStatus,
)
from ai_trader.execution_engine.validator import validate_order
from ai_trader.risk_manager.types import Decision, PortfolioState, RiskDecision


@dataclass(frozen=True, slots=True)
class PipelineOutcome:
    status: OrderStatus
    record: OrderRecord | None
    fill: Fill | None = None
    #: True when this call was an idempotent no-op (the ``client_order_id`` was already known --
    #: nothing new was built/validated/submitted). Callers use this to avoid double-counting
    #: statistics for a repeated call on the SAME decision (``EXECUTION_API.md`` §5: "a decision
    #: executes at most once").
    duplicate: bool = False


def status_from_record(record: OrderRecord) -> OrderStatus:
    return OrderStatus(
        order_request_id=record.order.order_request_id,
        client_order_id=record.client_order_id,
        state=record.state,
        filled_qty=record.filled_qty,
        remaining_qty=record.remaining_qty,
        avg_price=record.avg_price,
        reasons=record.reasons,
    )


def synthetic_status(decision: RiskDecision, config: ExecConfig, state: OrderState, reason: str) -> OrderStatus:
    """A reportable status for a decision that never produced a real ``OrderRequest`` (non-ALLOW, or a
    build failure) -- ids are still derived deterministically from ``decision_id`` for a stable,
    reproducible report even though no order was ever built."""
    client_order_id = f"{config.client_order_id_prefix}-{decision.decision_id}"
    order_request_id = f"{config.order_request_id_prefix}-{decision.decision_id}"
    return OrderStatus(
        order_request_id=order_request_id, client_order_id=client_order_id, state=state,
        filled_qty=0.0, remaining_qty=0.0, avg_price=None, reasons=(reason,),
    )


def _validate_and_submit(
    order: OrderRequest, portfolio: PortfolioState, caps: BrokerCapabilities,
    ledger: OrderLedger, adapter: BrokerAdapter,
) -> tuple[OrderRecord, Fill | None, bool]:
    """Stages 2-5 of the pipeline (Validate -> Duplicate guard -> Submit -> Track), shared by every
    caller that has already produced a well-formed ``OrderRequest`` -- the ONE place any of them
    actually touches the Ledger or the Broker Adapter. The optional :class:`Fill` is whatever the
    immediate synchronous post-submit status pull confirmed (v1 has no async event stream) -- reported
    to the Portfolio Manager as it occurs, never silently dropped (``EXECUTION_FAILURE_POLICY.md`` §4).
    The trailing ``bool`` is ``True`` only for the idempotent duplicate-guard no-op.

    **The duplicate guard runs FIRST, before validation** -- deliberately the reverse of the
    architecture doc's own numbered list (§6: "3. Validate ... 4. Duplicate guard"), and a genuine
    correctness fix over an earlier draft that validated first: ``portfolio`` legitimately differs
    between calls (it is the RUNNING view, updated after every earlier ALLOW in a batch, or simply a
    later snapshot on a later call), so re-validating an ALREADY-KNOWN ``client_order_id`` against a
    different portfolio can produce a DIFFERENT (and wrong) verdict than the original submission --
    e.g. a retry of an already-FILLED order failing ``POSITION_LIMIT_CONSISTENCY`` against a portfolio
    that now shows the position open (because it filled), which would silently overwrite the Ledger's
    terminal FILLED record with a bogus REJECTED one. Checking identity FIRST guarantees ``execute()``
    is a true idempotent no-op for any already-known id: the caller's OWN portfolio is irrelevant to
    that decision.
    """
    existing = ledger.get(order.client_order_id)
    if existing is not None:
        return existing, None, True  # idempotent no-op; nothing (re)submitted, nothing newly filled, and
        # critically nothing RE-VALIDATED against a possibly-different portfolio this call.

    validation = validate_order(order, caps, portfolio)
    if not validation.valid:
        record = OrderRecord(order=order, state=OrderState.REJECTED, reasons=validation.reasons)
        ledger.put(record)
        return record, None, False

    queued = OrderRecord(order=order, state=OrderState.QUEUED)
    ledger.put(queued)
    # From here on, the Ledger holds a NON-terminal record for this client_order_id -- every exit path
    # below (including the except blocks) must leave it in a definite state before returning, never an
    # orphaned QUEUED/SUBMITTED record silently abandoned behind a caller-visible FAILED/synthetic
    # status that the Ledger itself never learned about (a real gap the module's own test suite caught:
    # an outer try/except around this whole function would report FAILED to the caller while leaving
    # the Ledger stuck at QUEUED forever -- fixed by handling broker-call failures HERE, ledger-aware).
    try:
        ack = adapter.submit_order(order)
    except Exception as exc:  # noqa: BLE001 -- the broker call itself is the untrusted boundary; we
        # cannot know whether the order was actually received, so REJECT/FAIL it locally rather than
        # leave it QUEUED forever (architecture's own "internal/build/validation error -> fail-safe
        # REJECTED/FAILED" failure-table row).
        failed = OrderRecord(order=order, state=OrderState.FAILED, reasons=(f"INTERNAL_ERROR: broker submit_order raised: {exc}",))
        ledger.put(failed)
        return failed, None, False
    if not ack.accepted:
        rejected = OrderRecord(order=order, state=OrderState.REJECTED, reasons=(ack.reason or "BROKER_REJECTED",))
        ledger.put(rejected)
        return rejected, None, False
    submitted = OrderRecord(order=order, state=OrderState.SUBMITTED, broker_order_id=ack.broker_order_id)
    ledger.put(submitted)

    # Track -- an immediate synchronous status pull (v1 has no async event stream; the broker is
    # always queried, never assumed).
    try:
        broker_state = adapter.query_status(order.client_order_id)
    except Exception:  # noqa: BLE001 -- the order WAS genuinely accepted (ack.accepted=True) -- it
        # would be dishonest to mark it FAILED here; "prefer inaction" (EXECUTION_FAILURE_POLICY.md
        # §1.3) and leave it SUBMITTED for a later reconcile() to resolve to the true state.
        return submitted, None, False
    if broker_state is None:
        return submitted, None, False
    updated, fill = apply_broker_update(submitted, broker_state)
    ledger.put(updated)
    return updated, fill, False


def execute_one(
    decision: RiskDecision, portfolio: PortfolioState, caps: BrokerCapabilities, config: ExecConfig,
    ledger: OrderLedger, adapter: BrokerAdapter,
) -> PipelineOutcome:
    """Run the fixed pipeline for ONE decision. Never raises."""
    try:
        return _execute_one_unsafe(decision, portfolio, caps, config, ledger, adapter)
    except Exception:  # noqa: BLE001 -- the module's own documented exception safety net; any failure
        # anywhere in build/validate/submit/track is classified here, never propagated to crash a batch
        # of execute() calls the caller may be looping over.
        status = synthetic_status(
            decision, config, OrderState.FAILED, "INTERNAL_ERROR: unexpected exception during execution",
        )
        return PipelineOutcome(status=status, record=None)


def _execute_one_unsafe(
    decision: RiskDecision, portfolio: PortfolioState, caps: BrokerCapabilities, config: ExecConfig,
    ledger: OrderLedger, adapter: BrokerAdapter,
) -> PipelineOutcome:
    # 0. Intake.
    if decision.decision is not Decision.ALLOW:
        status = synthetic_status(
            decision, config, OrderState.REJECTED, "NOT_ALLOW: decision.decision is not ALLOW, nothing to execute",
        )
        return PipelineOutcome(status=status, record=None)

    # 1. Build.
    build_outcome = build_order(decision, portfolio, caps, config)
    if not build_outcome.success:
        reason = build_outcome.reason or "BUILD_FAILED"
        status = synthetic_status(decision, config, OrderState.REJECTED, reason)
        return PipelineOutcome(status=status, record=None)
    order = build_outcome.order
    assert order is not None

    # 2-5. Validate -> Duplicate guard -> Submit -> Track.
    record, fill, duplicate = _validate_and_submit(order, portfolio, caps, ledger, adapter)
    return PipelineOutcome(status=status_from_record(record), record=record, fill=fill, duplicate=duplicate)


def submit_built_order(
    order: OrderRequest, portfolio: PortfolioState, caps: BrokerCapabilities,
    ledger: OrderLedger, adapter: BrokerAdapter,
) -> tuple[OrderRecord | None, Fill | None, bool]:
    """The same validate -> duplicate-guard -> submit -> track chain as :func:`execute_one`, for a
    caller that has already built its own ``OrderRequest`` (``ExecutionEngine.emergency_flatten``'s
    synthesized reduce-only closing orders -- there is no ``RiskDecision`` to build FROM for a flatten
    command). Never raises: returns ``(None, None, False)`` (rather than propagating) on an unexpected
    exception, so one bad position's flatten order can never abort flattening the rest of the
    portfolio."""
    try:
        return _validate_and_submit(order, portfolio, caps, ledger, adapter)
    except Exception:  # noqa: BLE001 -- mirrors execute_one's own safety net for the sibling entry point.
        return None, None, False
