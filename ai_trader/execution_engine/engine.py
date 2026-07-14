"""``ExecutionEngine`` -- the public facade implementing ``EXECUTION_API.md`` exactly.

Wires together the Order Builder (:mod:`ai_trader.execution_engine.builder`), the Order Validator
(:mod:`ai_trader.execution_engine.validator`), the fixed per-decision pipeline
(:mod:`ai_trader.execution_engine.pipeline`), the Reconciler (:mod:`ai_trader.execution_engine.reconciler`),
and the Reporter (:mod:`ai_trader.execution_engine.reporter`) into the documented, deterministic,
fail-safe execution cycle. It re-decides nothing: no signals, no scoring, no risk decisions, no
learning, no research access, no real broker (``EXECUTION_ENGINE_ARCHITECTURE.md`` §2).

**Determinism note**: no module reached from this file imports ``time``/``random``. ``OrderRequest``
construction/validation are deterministic given ``(decision, portfolio, caps, config)`` -- only the
(future) venue's responses are not, and every response is always reconciled to a definite state.
"""

from __future__ import annotations

import logging

from ai_trader.execution_engine import builder, pipeline, reconciler, reporter
from ai_trader.execution_engine.broker_adapter import BrokerAdapter
from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.exceptions import EngineNotConfiguredError
from ai_trader.execution_engine.ledger import OrderLedger
from ai_trader.execution_engine.types import (
    BrokerCapabilities,
    EngineHealth,
    EngineLifecycleState,
    EngineOverallHealth,
    ExecutionReport,
    Fill,
    FlattenScope,
    NotFound,
    OrderRequest,
    OrderState,
    OrderStatus,
    Statistics,
    ValidationResult,
    VersionInfo,
)
from ai_trader.execution_engine.validator import validate_order as _validate_order_fn
from ai_trader.risk_manager.types import PortfolioState, RiskDecision

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """The Execution Engine. See ``EXECUTION_API.md`` for the full contract."""

    def __init__(self, config: ExecConfig | None = None) -> None:
        self._config = config or ExecConfig()
        self._lifecycle_state = EngineLifecycleState.IDLE
        self._adapter: BrokerAdapter | None = None
        self._caps: BrokerCapabilities | None = None
        self._ledger = OrderLedger()
        self._degraded = False
        self._degraded_reasons: list[str] = []
        self._last_portfolio: PortfolioState | None = None
        self._last_as_of: int = 0
        self._last_risk_schema_version = "0.0.0"
        self._last_risk_policy_version = "0.0.0"
        self._orders_total = 0
        self._by_state: dict[str, int] = {}
        self._fills = 0
        self._rejects = 0
        self._failures = 0
        #: Every confirmed :class:`Fill`, in confirmation order -- ``report()``/``reconcile()`` return
        #: this in full (v1 has no notion of "cycle" boundaries beyond the engine's own lifetime, so
        #: there is nothing meaningful to prune between calls; documented IMPLEMENTATION CHOICE).
        self._fills_log: list[Fill] = []

    # ------------------------------------------------------------------ 0. configuration

    def configure(self, adapter: BrokerAdapter) -> None:
        """Startup (``EXECUTION_SEQUENCE.md`` §1): handshake the Broker Adapter's capabilities, then
        mandatory reconciliation -- query for any pre-existing live orders and rebuild what the Ledger
        can before accepting new decisions. Idempotent full reset."""
        self._adapter = adapter
        self._ledger = OrderLedger()
        self._degraded = False
        self._degraded_reasons = []
        self._orders_total = 0
        self._by_state = {}
        self._fills = 0
        self._rejects = 0
        self._failures = 0
        self._fills_log = []
        self._last_portfolio = None

        self._lifecycle_state = EngineLifecycleState.RECONCILING
        self._caps = adapter.capabilities()
        orphaned = reconciler.rebuild_from_broker(self._ledger, adapter)
        if orphaned:
            self._degraded = True
            reason = f"orphaned broker orders at startup reconciliation: {list(orphaned)}"
            self._degraded_reasons.append(reason)
            logger.warning("ExecutionEngine startup reconciliation found orphaned orders: %s", orphaned)
        self._lifecycle_state = EngineLifecycleState.READY
        self._sync_lifecycle_with_degraded()

    def _require_configured(self) -> None:
        if self._lifecycle_state in (EngineLifecycleState.IDLE, EngineLifecycleState.STOPPED):
            raise EngineNotConfiguredError("ExecutionEngine.configure() must be called first")

    def _sync_lifecycle_with_degraded(self) -> None:
        """``EXECUTION_STATE_MACHINE.md`` §A: ``READY <-> DEGRADED`` on Broker/Portfolio availability
        -- unlike Risk Manager's own lifecycle enum (which has no DEGRADED member and tracks
        degradation purely as a health flag), Execution Engine's ``EngineLifecycleState`` explicitly
        names DEGRADED as one of its 7 states, so this module keeps ``self._lifecycle_state`` itself in
        sync with ``self._degraded`` -- only ever flipping between READY and DEGRADED, never touching
        RECONCILING/EMERGENCY_FLATTEN/DRAINING/STOPPED/IDLE."""
        if self._degraded and self._lifecycle_state is EngineLifecycleState.READY:
            self._lifecycle_state = EngineLifecycleState.DEGRADED
        elif not self._degraded and self._lifecycle_state is EngineLifecycleState.DEGRADED:
            self._lifecycle_state = EngineLifecycleState.READY

    # ------------------------------------------------------------------ 1. execution

    def execute(self, decision: RiskDecision, portfolio: PortfolioState | None) -> OrderStatus:
        """The normal entry point (``EXECUTION_API.md`` §1). Every path here routes through
        :func:`ai_trader.execution_engine.pipeline.execute_one`, the ONE exception-safe implementation
        of build/validate/submit/track -- no logic is duplicated here."""
        self._require_configured()
        assert self._adapter is not None and self._caps is not None

        if self._lifecycle_state in (EngineLifecycleState.RECONCILING, EngineLifecycleState.DRAINING):
            # "accepts decisions? no" for both (EXECUTION_STATE_MACHINE.md §A) -- not reachable via
            # this module's own synchronous configure()/shutdown() (RECONCILING/DRAINING never persist
            # across a return to the caller), but guarded defensively for robustness.
            status = pipeline.synthetic_status(
                decision, self._config, OrderState.REJECTED,
                f"ENGINE_NOT_READY: engine state is {self._lifecycle_state.value}",
            )
            self._record_status(status)
            return status

        if portfolio is None or portfolio.is_stale:
            self._degraded = True
            reason = "PortfolioState unavailable/stale at execute()"
            if reason not in self._degraded_reasons:
                self._degraded_reasons.append(reason)
            self._sync_lifecycle_with_degraded()
            status = pipeline.synthetic_status(decision, self._config, OrderState.FAILED, "PORTFOLIO_UNAVAILABLE")
            self._record_status(status)
            return status

        # A fresh, non-stale portfolio arriving here means the read path is healthy again -- clear any
        # previously recorded portfolio-availability degradation from the start (the exact class of bug
        # the Risk Manager's own adversarial review found and had to retrofit; applied proactively here).
        self._degraded_reasons = [r for r in self._degraded_reasons if "PortfolioState" not in r]
        self._degraded = bool(self._degraded_reasons)
        self._sync_lifecycle_with_degraded()
        self._last_portfolio = portfolio
        self._last_as_of = portfolio.as_of
        self._last_risk_schema_version = decision.risk_schema_version
        self._last_risk_policy_version = decision.risk_policy_version

        if self._lifecycle_state is EngineLifecycleState.EMERGENCY_FLATTEN:
            is_reduce_only = decision.constraints is not None and bool(decision.constraints.reduce_only)
            if not is_reduce_only:
                status = pipeline.synthetic_status(
                    decision, self._config, OrderState.REJECTED,
                    "EMERGENCY_FLATTEN_ACTIVE: only reduce-only orders are accepted",
                )
                self._record_status(status)
                return status

        outcome = pipeline.execute_one(decision, portfolio, self._caps, self._config, self._ledger, self._adapter)
        if not outcome.duplicate:
            # A duplicate (idempotent no-op) call records nothing new -- the SAME decision executing
            # twice must not double-count orders_total/by_state/etc (EXECUTION_API.md §5: "a decision
            # executes at most once").
            self._record_status(outcome.status)
        if outcome.fill is not None:
            self._fills_log.append(outcome.fill)
        return outcome.status

    def build_order(self, decision: RiskDecision, portfolio: PortfolioState, caps: BrokerCapabilities) -> OrderRequest | None:
        """Deterministically construct (but do NOT submit) an ``OrderRequest`` -- for inspection/
        testing (``EXECUTION_API.md`` §1). Returns ``None`` on a build failure (a "rejected build",
        per the documented failure semantics); does not raise."""
        outcome = builder.build_order(decision, portfolio, caps, self._config)
        return outcome.order

    def validate_order(self, order: OrderRequest, caps: BrokerCapabilities, portfolio: PortfolioState) -> ValidationResult:
        """Run the execution-mechanics validation suite WITHOUT submitting (``EXECUTION_API.md`` §1)."""
        return _validate_order_fn(order, caps, portfolio)

    # ------------------------------------------------------------------ 2. lifecycle control & retrieval

    def cancel(self, client_order_id: str) -> OrderStatus | NotFound:
        """Request cancellation of a working order (``EXECUTION_API.md`` §2). Idempotent: an already-
        terminal order returns its terminal status unchanged. Always reconciles after a cancel attempt
        so a cancel<->fill race resolves to the true state (``EXECUTION_SEQUENCE.md`` §5), never trusts
        the broker's immediate ack alone."""
        self._require_configured()
        assert self._adapter is not None
        record = self._ledger.get(client_order_id)
        if record is None:
            return NotFound(requested_id=client_order_id)
        if record.is_terminal:
            return pipeline.status_from_record(record)

        # request_cancel is the exception-safe boundary (reconciler.py) -- never calls the adapter
        # directly here, so a raising cancel_order()/query_status() can never propagate out of cancel().
        updated, fill = reconciler.request_cancel(self._ledger, self._adapter, client_order_id)
        if fill is not None:
            self._fills_log.append(fill)
        # Fill COUNTING (statistics().fills) is handled uniformly by _record_status below (keyed off
        # the resolved state), not here, to avoid double-counting the same fill through two counters.
        final = updated if updated is not None else record
        status = pipeline.status_from_record(final)
        self._record_status(status, already_in_ledger=True)
        return status

    def status(self, client_order_id: str) -> OrderStatus | NotFound:
        """The current lifecycle state + fill progress from the Ledger (``EXECUTION_API.md`` §2)."""
        record = self._ledger.get(client_order_id)
        if record is None:
            return NotFound(requested_id=client_order_id)
        return pipeline.status_from_record(record)

    def reconcile(self, client_order_id: str | None = None) -> OrderStatus | ExecutionReport | NotFound:
        """Force reconciliation for one order (or every open order) against the Broker Adapter
        (``EXECUTION_API.md`` §2). An unknown ``client_order_id`` returns :class:`NotFound` (consistent
        with :meth:`status`/:meth:`cancel`'s own unknown-id handling)."""
        self._require_configured()
        assert self._adapter is not None
        if client_order_id is not None:
            updated, fill = reconciler.reconcile_one(self._ledger, self._adapter, client_order_id)
            if updated is None:
                return NotFound(requested_id=client_order_id)
            if fill is not None:
                self._fills += 1
                self._fills_log.append(fill)
            return pipeline.status_from_record(updated)
        fills = reconciler.reconcile_all_open(self._ledger, self._adapter)
        self._fills += len(fills)
        self._fills_log.extend(fills)
        return reporter.build_report(as_of=self._last_as_of, ledger=self._ledger, fills=tuple(self._fills_log))

    def report(self, as_of: int | None = None) -> ExecutionReport:
        """The ``ExecutionResult``s + fills for the current cycle (``EXECUTION_API.md`` §2)."""
        self._require_configured()
        return reporter.build_report(
            as_of=as_of if as_of is not None else self._last_as_of, ledger=self._ledger,
            fills=tuple(self._fills_log),
        )

    # ------------------------------------------------------------------ 3. operational controls

    def emergency_flatten(self, scope: FlattenScope | None = None) -> ExecutionReport:
        """Executed on the Risk Manager's command (``EXECUTION_API.md`` §3): issue reduce-only closing
        orders for every in-scope open position, refuse new opening orders. The Execution Engine only
        EXECUTES the flatten; it never decides to flatten. Routes each synthesized closing order
        through :func:`ai_trader.execution_engine.pipeline.submit_built_order` -- the SAME exception-
        safe validate/submit/track chain :meth:`execute` uses, so one bad position's closing order can
        never abort flattening the rest of the portfolio."""
        self._require_configured()
        assert self._adapter is not None and self._caps is not None
        self._lifecycle_state = EngineLifecycleState.EMERGENCY_FLATTEN
        logger.warning("ExecutionEngine emergency_flatten commanded; scope=%s", scope)

        portfolio = self._last_portfolio
        if portfolio is None:
            # No PortfolioState has ever been observed (emergency_flatten called before any execute()
            # call) -- there is nothing to flatten FROM. Unlike a silent empty report (which would read
            # as "flattened everything, there was nothing to do"), this is disclosed as degraded: the
            # caller MUST know the flatten command could not actually act on anything.
            reason = "emergency_flatten commanded with no PortfolioState ever observed -- nothing could be flattened"
            self._degraded = True
            if reason not in self._degraded_reasons:
                self._degraded_reasons.append(reason)
            logger.warning(reason)
        else:
            symbols = scope.symbols if scope is not None else None
            for position in portfolio.open_positions:
                if symbols is not None and position.symbol not in symbols:
                    continue
                try:
                    build_outcome = builder.build_flatten_order(
                        position, self._caps, self._config, self._last_as_of,
                        self._last_risk_schema_version, self._last_risk_policy_version,
                    )
                except Exception as exc:  # noqa: BLE001 -- one position's build must never abort
                    # flattening the rest (the exact "one malformed order cannot abort the batch"
                    # requirement, applied to the build stage exactly like the submit stage already was).
                    logger.warning(
                        "emergency_flatten: unexpected exception building a closing order for %s/%s: %s",
                        position.strategy_id, position.symbol, exc,
                    )
                    continue
                if not build_outcome.success or build_outcome.order is None:
                    logger.warning(
                        "emergency_flatten: could not build a closing order for %s/%s: %s",
                        position.strategy_id, position.symbol, build_outcome.reason,
                    )
                    continue
                record, fill, duplicate = pipeline.submit_built_order(
                    build_outcome.order, portfolio, self._caps, self._ledger, self._adapter,
                )
                if record is None:
                    # submit_built_order's own exception safety net returned None -- classify exactly
                    # like execute()'s equivalent INTERNAL_ERROR path, via the SAME counting helper.
                    self._record_status(OrderStatus(
                        order_request_id=build_outcome.order.order_request_id,
                        client_order_id=build_outcome.order.client_order_id,
                        state=OrderState.FAILED,
                        reasons=("INTERNAL_ERROR: unexpected exception during flatten",),
                    ))
                    continue
                if not duplicate:
                    self._record_status(pipeline.status_from_record(record), already_in_ledger=True)
                if fill is not None:
                    self._fills_log.append(fill)

        report = reporter.build_report(as_of=self._last_as_of, ledger=self._ledger, fills=tuple(self._fills_log))
        return report

    # ------------------------------------------------------------------ 4. introspection

    def statistics(self) -> Statistics:
        return Statistics(
            orders_total=self._orders_total, by_state=dict(self._by_state), fills=self._fills,
            rejects=self._rejects, failures=self._failures, avg_submit_ms=0.0,
        )

    def health(self) -> EngineHealth:
        if self._lifecycle_state in (EngineLifecycleState.IDLE, EngineLifecycleState.STOPPED):
            overall = EngineOverallHealth.FAILED
        elif self._degraded_reasons:
            overall = EngineOverallHealth.DEGRADED
        else:
            overall = EngineOverallHealth.OK
        return EngineHealth(
            overall=overall, state=self._lifecycle_state, degraded_reasons=tuple(self._degraded_reasons),
            broker_available=self._adapter is not None,
            supported_versions={"risk_schema_major": self._config.supported_risk_schema_major},
        )

    def versions(self) -> VersionInfo:
        return VersionInfo(
            execution_engine_version=self._config.execution_engine_version,
            order_schema_version=self._config.order_schema_version,
            broker_adapter_contract_version=self._config.broker_adapter_contract_version,
            supported_risk_schema_major=self._config.supported_risk_schema_major,
        )

    # ------------------------------------------------------------------ 5. shutdown

    def shutdown(self) -> EngineHealth:
        """``DRAINING``: reconcile every in-flight order to a definite state before ``STOPPED``
        (``EXECUTION_SEQUENCE.md`` §10) -- never abandon an order in an unknown state."""
        self._require_configured()
        self._lifecycle_state = EngineLifecycleState.DRAINING
        if self._adapter is not None:
            reconciler.reconcile_all_open(self._ledger, self._adapter)
        final_health = self.health()  # captured BEFORE flipping to STOPPED, same precedent as every
        # prior module's own shutdown() -- "stopped" must not be misreported as a synthetic FAILED.
        self._lifecycle_state = EngineLifecycleState.STOPPED
        self._adapter = None
        return final_health

    # ------------------------------------------------------------------ internals

    def _record_status(self, status: OrderStatus, already_in_ledger: bool = False) -> None:
        if not already_in_ledger:
            self._orders_total += 1
        self._by_state[status.state.value] = self._by_state.get(status.state.value, 0) + 1
        if status.state is OrderState.REJECTED:
            self._rejects += 1
        elif status.state is OrderState.FAILED:
            self._failures += 1
        elif status.state in (OrderState.FILLED, OrderState.PARTIALLY_FILLED):
            self._fills += 1
