"""Tests for :mod:`ai_trader.execution_engine.pipeline`."""

from __future__ import annotations

from dataclasses import replace
from unittest.mock import patch

from ai_trader.execution_engine.builder import build_order
from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.ledger import OrderLedger
from ai_trader.execution_engine.pipeline import execute_one, submit_built_order
from ai_trader.execution_engine.tests.fixtures.fake_broker import FakeBrokerAdapter, make_capabilities
from ai_trader.execution_engine.tests.fixtures.fake_decision import make_allow_decision, make_deny_decision
from ai_trader.execution_engine.types import MarketStatus, OrderState

CONFIG = ExecConfig()
CAPS = make_capabilities()


class TestIntake:
    def test_deny_decision_is_a_no_op(self) -> None:
        decision, portfolio = make_deny_decision()
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS)
        outcome = execute_one(decision, portfolio, CAPS, CONFIG, ledger, adapter)
        assert outcome.status.state is OrderState.REJECTED
        assert "NOT_ALLOW" in outcome.status.reasons[0]
        assert len(ledger) == 0


class TestHappyPath:
    def test_allow_decision_fills_immediately_with_a_default_broker(self) -> None:
        decision, portfolio = make_allow_decision()
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS)
        outcome = execute_one(decision, portfolio, CAPS, CONFIG, ledger, adapter)
        assert outcome.status.state is OrderState.FILLED
        assert outcome.fill is not None
        assert len(ledger) == 1


class TestDuplicateGuard:
    def test_same_decision_twice_never_double_submits(self) -> None:
        decision, portfolio = make_allow_decision()
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS)
        first = execute_one(decision, portfolio, CAPS, CONFIG, ledger, adapter)
        second = execute_one(decision, portfolio, CAPS, CONFIG, ledger, adapter)
        assert first.status.client_order_id == second.status.client_order_id
        assert len(adapter.submit_calls) == 1  # broker only ever saw ONE submission
        assert len(ledger) == 1

    def test_idempotent_across_broker_rejection(self) -> None:
        decision, portfolio = make_allow_decision()
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS, accept_submits=False)
        first = execute_one(decision, portfolio, CAPS, CONFIG, ledger, adapter)
        second = execute_one(decision, portfolio, CAPS, CONFIG, ledger, adapter)
        assert first.status.state is OrderState.REJECTED
        assert second.status.state is OrderState.REJECTED
        assert len(adapter.submit_calls) == 1  # the second call never resubmits a known-terminal id


class TestDuplicateGuardRunsBeforeValidation:
    """Regression guard (adversarial review, CRITICAL finding #1): the duplicate guard MUST run
    BEFORE validate_order, not after -- otherwise a retry of an already-terminal (e.g. FILLED) order,
    evaluated against a portfolio that has since changed (e.g. now shows the position this very order
    created), can fail validation and have its Ledger record overwritten with a bogus REJECTED,
    corrupting the record of an order that actually filled."""

    def test_retrying_a_filled_order_against_a_now_invalid_portfolio_does_not_corrupt_the_ledger(self) -> None:
        decision, portfolio = make_allow_decision()
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS)
        first = execute_one(decision, portfolio, CAPS, CONFIG, ledger, adapter)
        assert first.status.state is OrderState.FILLED

        # A portfolio that now shows the position this order just created open -- re-validating
        # against it would fail POSITION_LIMIT_CONSISTENCY (an OPEN order for a symbol/strategy that
        # already has an open position) if validation ran again.
        from ai_trader.risk_manager.types import OpenPosition
        position = OpenPosition(
            symbol=decision.symbol, strategy_id=decision.strategy_id, direction=decision.direction,
            size_units=1.0, entry_price=100.0, opened_bars_ago=0, risk_pct=0.001,
        )
        changed_portfolio = replace(portfolio, open_positions=(position,))

        second = execute_one(decision, changed_portfolio, CAPS, CONFIG, ledger, adapter)
        assert second.status.state is OrderState.FILLED  # unchanged, NOT overwritten to REJECTED
        assert second.duplicate is True
        ledger_record = ledger.get(first.status.client_order_id)
        assert ledger_record is not None and ledger_record.state is OrderState.FILLED


class TestBrokerRejection:
    def test_broker_rejects_submit(self) -> None:
        decision, portfolio = make_allow_decision()
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS, accept_submits=False, submit_reject_reason="MARGIN")
        outcome = execute_one(decision, portfolio, CAPS, CONFIG, ledger, adapter)
        assert outcome.status.state is OrderState.REJECTED
        assert "MARGIN" in outcome.status.reasons


class TestValidationFailure:
    def test_invalid_order_is_rejected_before_submit(self) -> None:
        decision, portfolio = make_allow_decision()
        closed_caps = make_capabilities(market_status=MarketStatus.CLOSED)
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=closed_caps)
        outcome = execute_one(decision, portfolio, closed_caps, CONFIG, ledger, adapter)
        assert outcome.status.state is OrderState.REJECTED
        assert len(adapter.submit_calls) == 0  # never reached the broker


class TestExceptionSafety:
    def test_unexpected_exception_during_build_degrades_to_failed_not_a_crash(self) -> None:
        decision, portfolio = make_allow_decision()
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS)
        with patch("ai_trader.execution_engine.pipeline.build_order", side_effect=RuntimeError("boom")):
            outcome = execute_one(decision, portfolio, CAPS, CONFIG, ledger, adapter)
        assert outcome.status.state is OrderState.FAILED
        assert "INTERNAL_ERROR" in outcome.status.reasons[0]

    def test_unexpected_exception_during_submit_degrades_to_failed_not_a_crash(self) -> None:
        decision, portfolio = make_allow_decision()
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS)
        with patch.object(adapter, "submit_order", side_effect=RuntimeError("boom")):
            outcome = execute_one(decision, portfolio, CAPS, CONFIG, ledger, adapter)
        assert outcome.status.state is OrderState.FAILED

    def test_one_malformed_decision_does_not_prevent_the_next_call_from_succeeding(self) -> None:
        """Batch-safety: calling execute_one in a loop, one bad decision never corrupts the ledger or
        blocks subsequent calls (mirrors the CEO's explicit "one malformed order cannot abort the full
        batch" requirement) -- whether it degrades gracefully (REJECTED, this case) or via the
        exception safety net (FAILED, covered by ``TestExceptionSafety`` above)."""
        broken, portfolio = make_allow_decision(strategy_id="S1")
        broken = replace(broken, direction=None)  # type: ignore[arg-type]  # no derivable order side
        healthy, portfolio2 = make_allow_decision(strategy_id="S2")
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS)

        first = execute_one(broken, portfolio, CAPS, CONFIG, ledger, adapter)
        second = execute_one(healthy, portfolio2, CAPS, CONFIG, ledger, adapter)

        assert first.status.state is OrderState.REJECTED
        assert second.status.state is OrderState.FILLED


class TestPostSubmitTrackingFailures:
    """The order was genuinely ACCEPTED by the broker before either of these failure modes -- neither
    may honestly report FAILED; both leave the order SUBMITTED for a later reconcile() (a `not-found`
    /timeout-style scenario, ``EXECUTION_FAILURE_POLICY.md`` §2's "Timeout" row)."""

    def test_query_status_exception_after_accepted_submit_leaves_order_submitted(self) -> None:
        decision, portfolio = make_allow_decision()
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS, fill_on_submit=False)
        with patch.object(adapter, "query_status", side_effect=RuntimeError("timeout")):
            outcome = execute_one(decision, portfolio, CAPS, CONFIG, ledger, adapter)
        assert outcome.status.state is OrderState.SUBMITTED
        ledger_record = ledger.get(outcome.status.client_order_id)
        assert ledger_record is not None and ledger_record.state is OrderState.SUBMITTED

    def test_query_status_returns_none_leaves_order_submitted(self) -> None:
        """``query_status`` returning ``None`` immediately after a successful submit (the broker not
        yet reflecting its own just-accepted order) -- distinct from the exception case, same safe
        SUBMITTED outcome."""
        decision, portfolio = make_allow_decision()
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS, fill_on_submit=False)
        with patch.object(adapter, "query_status", return_value=None):
            outcome = execute_one(decision, portfolio, CAPS, CONFIG, ledger, adapter)
        assert outcome.status.state is OrderState.SUBMITTED


class TestSubmitBuiltOrder:
    def test_builds_and_submits_directly(self) -> None:
        decision, portfolio = make_allow_decision()
        outcome = build_order(decision, portfolio, CAPS, CONFIG)
        assert outcome.order is not None
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS)
        record, fill, _duplicate = submit_built_order(outcome.order, portfolio, CAPS, ledger, adapter)
        assert record is not None
        assert record.state is OrderState.FILLED
        assert fill is not None

    def test_broker_exception_during_submit_finalizes_to_failed_in_the_ledger(self) -> None:
        """A broker-call exception is caught ledger-aware, INSIDE the shared submit chain, so the
        Ledger never ends up with an orphaned QUEUED record behind a caller-visible FAILED status."""
        decision, portfolio = make_allow_decision()
        outcome = build_order(decision, portfolio, CAPS, CONFIG)
        assert outcome.order is not None
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS)
        with patch.object(adapter, "submit_order", side_effect=RuntimeError("boom")):
            record, fill, _duplicate = submit_built_order(outcome.order, portfolio, CAPS, ledger, adapter)
        assert record is not None
        assert record.state is OrderState.FAILED
        assert "INTERNAL_ERROR" in record.reasons[0]
        assert fill is None
        # the Ledger itself (not just the return value) reflects the terminal FAILED state.
        ledger_record = ledger.get(outcome.order.client_order_id)
        assert ledger_record is not None and ledger_record.state is OrderState.FAILED

    def test_outer_safety_net_still_catches_exceptions_outside_the_broker_calls(self) -> None:
        """The outer try/except in submit_built_order remains a safety net for failures that happen
        BEFORE anything is written to the Ledger (e.g. inside validate_order itself) -- those
        genuinely have nothing in the Ledger to finalize, so returning (None, None, False) is correct."""
        decision, portfolio = make_allow_decision()
        outcome = build_order(decision, portfolio, CAPS, CONFIG)
        assert outcome.order is not None
        ledger = OrderLedger()
        adapter = FakeBrokerAdapter(caps=CAPS)
        with patch("ai_trader.execution_engine.pipeline.validate_order", side_effect=RuntimeError("boom")):
            record, fill, duplicate = submit_built_order(outcome.order, portfolio, CAPS, ledger, adapter)
        assert record is None
        assert fill is None
        assert duplicate is False
        assert len(ledger) == 0


class TestDeterminism:
    def test_identical_inputs_produce_identical_outcome(self) -> None:
        decision, portfolio = make_allow_decision()
        ledger1, ledger2 = OrderLedger(), OrderLedger()
        adapter1, adapter2 = FakeBrokerAdapter(caps=CAPS), FakeBrokerAdapter(caps=CAPS)
        first = execute_one(decision, portfolio, CAPS, CONFIG, ledger1, adapter1)
        second = execute_one(decision, portfolio, CAPS, CONFIG, ledger2, adapter2)
        assert first.status == second.status
