"""Unit tests for :mod:`ai_trader.execution_engine.engine` -- ``ExecutionEngine`` against a fully
controllable :class:`FakeBrokerAdapter`. Real-upstream integration lives in
``test_engine_integration.py``.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.engine import ExecutionEngine
from ai_trader.execution_engine.exceptions import EngineNotConfiguredError
from ai_trader.execution_engine.tests.fixtures.fake_broker import FakeBrokerAdapter, make_capabilities
from ai_trader.execution_engine.tests.fixtures.fake_decision import (
    make_allow_decision,
    make_deny_decision,
    make_reduce_only_allow_decision,
)
from ai_trader.execution_engine.types import (
    BrokerOrderState,
    EngineLifecycleState,
    EngineOverallHealth,
    FlattenScope,
    NotFound,
    OrderState,
)
from ai_trader.risk_manager.tests.fixtures.fake_opportunity import make_portfolio

CAPS = make_capabilities()


def _configured_engine(**kwargs: Any) -> tuple[ExecutionEngine, FakeBrokerAdapter]:
    adapter = FakeBrokerAdapter(caps=CAPS, **kwargs)
    engine = ExecutionEngine(ExecConfig())
    engine.configure(adapter)
    return engine, adapter


class TestConfigurationGate:
    def test_execute_before_configure_raises(self) -> None:
        engine = ExecutionEngine()
        decision, portfolio = make_allow_decision()
        with pytest.raises(EngineNotConfiguredError):
            engine.execute(decision, portfolio)

    def test_shutdown_before_configure_raises(self) -> None:
        engine = ExecutionEngine()
        with pytest.raises(EngineNotConfiguredError):
            engine.shutdown()

    def test_health_before_configure_is_failed(self) -> None:
        engine = ExecutionEngine()
        assert engine.health().overall is EngineOverallHealth.FAILED
        assert engine.health().state is EngineLifecycleState.IDLE


class TestConfigureLifecycle:
    def test_clean_configure_reaches_ready(self) -> None:
        engine, _adapter = _configured_engine()
        assert engine.health().state is EngineLifecycleState.READY
        assert engine.health().overall is EngineOverallHealth.OK

    def test_configure_is_idempotent_and_resets_statistics(self) -> None:
        engine, _adapter = _configured_engine()
        decision, portfolio = make_allow_decision()
        engine.execute(decision, portfolio)
        engine.configure(FakeBrokerAdapter(caps=CAPS))
        assert engine.statistics().orders_total == 0

    def test_orphaned_broker_orders_at_startup_are_disclosed_not_dropped(self) -> None:
        adapter = FakeBrokerAdapter(caps=CAPS)
        adapter.seed_preexisting_order(BrokerOrderState(client_order_id="CID-ORPHAN", state=OrderState.ACKNOWLEDGED))
        engine = ExecutionEngine(ExecConfig())
        engine.configure(adapter)
        health = engine.health()
        assert health.overall is EngineOverallHealth.DEGRADED
        assert health.state is EngineLifecycleState.DEGRADED
        assert any("CID-ORPHAN" in r for r in health.degraded_reasons)


class TestExecuteHappyPath:
    def test_allow_decision_returns_filled(self) -> None:
        engine, _adapter = _configured_engine()
        decision, portfolio = make_allow_decision()
        status = engine.execute(decision, portfolio)
        assert status.state is OrderState.FILLED

    def test_deny_decision_is_a_no_op(self) -> None:
        engine, _adapter = _configured_engine()
        decision, portfolio = make_deny_decision()
        status = engine.execute(decision, portfolio)
        assert status.state is OrderState.REJECTED
        assert "NOT_ALLOW" in status.reasons[0]


class TestDefensiveLifecycleGuard:
    def test_execute_while_reconciling_or_draining_is_refused(self) -> None:
        """Not reachable via this module's own synchronous configure()/shutdown() (§ engine.py's own
        docstring) -- guarded defensively anyway; verified by forcing the state directly."""
        engine, _adapter = _configured_engine()
        decision, portfolio = make_allow_decision()
        engine._lifecycle_state = EngineLifecycleState.DRAINING
        status = engine.execute(decision, portfolio)
        assert status.state is OrderState.REJECTED
        assert "ENGINE_NOT_READY" in status.reasons[0]


class TestPortfolioUnavailable:
    def test_none_portfolio_fails_safe(self) -> None:
        engine, _adapter = _configured_engine()
        decision, _portfolio = make_allow_decision()
        status = engine.execute(decision, None)
        assert status.state is OrderState.FAILED
        assert "PORTFOLIO_UNAVAILABLE" in status.reasons
        assert engine.health().overall is EngineOverallHealth.DEGRADED
        assert engine.health().state is EngineLifecycleState.DEGRADED

    def test_stale_portfolio_fails_safe(self) -> None:
        engine, _adapter = _configured_engine()
        decision, _portfolio = make_allow_decision()
        stale = make_portfolio(is_stale=True)
        status = engine.execute(decision, stale)
        assert status.state is OrderState.FAILED

    def test_health_recovers_after_a_fresh_portfolio_arrives(self) -> None:
        engine, _adapter = _configured_engine()
        decision, portfolio = make_allow_decision(strategy_id="S1")
        engine.execute(decision, None)
        assert engine.health().overall is EngineOverallHealth.DEGRADED
        decision2, portfolio2 = make_allow_decision(strategy_id="S2")
        engine.execute(decision2, portfolio2)
        assert engine.health().overall is EngineOverallHealth.OK
        assert engine.health().state is EngineLifecycleState.READY


class TestIdempotency:
    def test_same_decision_executed_twice_returns_the_same_status(self) -> None:
        engine, adapter = _configured_engine()
        decision, portfolio = make_allow_decision()
        first = engine.execute(decision, portfolio)
        second = engine.execute(decision, portfolio)
        assert first.client_order_id == second.client_order_id
        assert len(adapter.submit_calls) == 1

    def test_orders_total_counts_once_per_decision_not_per_call(self) -> None:
        engine, _adapter = _configured_engine()
        decision, portfolio = make_allow_decision()
        engine.execute(decision, portfolio)
        engine.execute(decision, portfolio)
        assert engine.statistics().orders_total == 1


class TestBuildOrderAndValidateOrder:
    def test_build_order_for_inspection(self) -> None:
        engine, _adapter = _configured_engine()
        decision, portfolio = make_allow_decision()
        order = engine.build_order(decision, portfolio, CAPS)
        assert order is not None
        assert order.decision_id == decision.decision_id

    def test_build_order_returns_none_for_deny(self) -> None:
        engine, _adapter = _configured_engine()
        decision, portfolio = make_deny_decision()
        order = engine.build_order(decision, portfolio, CAPS)
        assert order is None

    def test_validate_order_without_submitting(self) -> None:
        engine, adapter = _configured_engine()
        decision, portfolio = make_allow_decision()
        order = engine.build_order(decision, portfolio, CAPS)
        assert order is not None
        result = engine.validate_order(order, CAPS, portfolio)
        assert result.valid is True
        assert len(adapter.submit_calls) == 0  # never touched the broker


class TestStatusCancelReconcile:
    def test_status_of_unknown_id_is_not_found(self) -> None:
        engine, _adapter = _configured_engine()
        assert isinstance(engine.status("unknown"), NotFound)

    def test_status_of_known_order(self) -> None:
        engine, _adapter = _configured_engine()
        decision, portfolio = make_allow_decision()
        status = engine.execute(decision, portfolio)
        fetched = engine.status(status.client_order_id)
        assert not isinstance(fetched, NotFound)
        assert fetched.state is OrderState.FILLED

    def test_cancel_unknown_id_is_not_found(self) -> None:
        engine, _adapter = _configured_engine()
        assert isinstance(engine.cancel("unknown"), NotFound)

    def test_cancel_terminal_order_is_idempotent(self) -> None:
        engine, _adapter = _configured_engine()
        decision, portfolio = make_allow_decision()
        status = engine.execute(decision, portfolio)  # FILLED (fake broker fills on submit)
        result = engine.cancel(status.client_order_id)
        assert not isinstance(result, NotFound)
        assert result.state is OrderState.FILLED  # unchanged, never "un-filled"

    def test_cancel_working_order(self) -> None:
        engine, adapter = _configured_engine(fill_on_submit=False)
        decision, portfolio = make_allow_decision()
        status = engine.execute(decision, portfolio)
        assert status.state is OrderState.ACKNOWLEDGED
        result = engine.cancel(status.client_order_id)
        assert not isinstance(result, NotFound)
        assert result.state is OrderState.CANCELLED

    def test_cancel_with_a_raising_broker_never_propagates(self) -> None:
        """Regression guard (adversarial review, CRITICAL finding #2): cancel() must route through
        the exception-safe reconciler boundary, not call the adapter directly."""
        engine, adapter = _configured_engine(fill_on_submit=False)
        decision, portfolio = make_allow_decision()
        status = engine.execute(decision, portfolio)
        with patch.object(adapter, "cancel_order", side_effect=RuntimeError("boom")):
            result = engine.cancel(status.client_order_id)  # must not raise
        assert not isinstance(result, NotFound)
        assert result.state is OrderState.ACKNOWLEDGED  # unresolved but intact, never crashed

    def test_cancel_fill_race_resolves_to_filled(self) -> None:
        """EXECUTION_SEQUENCE.md §5: a fill arrives during cancel -> the fill wins. ``cancel()``
        always reconciles AFTER attempting the cancel, so even a broker that reports the cancel as
        having raced a fill resolves to the true (FILLED) state, never trusting the cancel ack alone."""
        engine, adapter = _configured_engine(fill_on_submit=False)
        decision, portfolio = make_allow_decision()
        status = engine.execute(decision, portfolio)
        assert status.state is OrderState.ACKNOWLEDGED
        # simulate the broker having ALREADY filled the order by the time cancel is processed
        adapter.push_fill(status.client_order_id, filled_qty=1.0, avg_price=100.0, full=True)

        result = engine.cancel(status.client_order_id)
        assert not isinstance(result, NotFound)
        assert result.state is OrderState.FILLED

    def test_reconcile_unknown_id_is_not_found(self) -> None:
        engine, _adapter = _configured_engine()
        assert isinstance(engine.reconcile("unknown"), NotFound)

    def test_reconcile_single_order(self) -> None:
        from ai_trader.execution_engine.types import OrderStatus

        engine, adapter = _configured_engine(fill_on_submit=False)
        decision, portfolio = make_allow_decision()
        status = engine.execute(decision, portfolio)
        adapter.push_fill(status.client_order_id, filled_qty=1.0, avg_price=100.0, full=True)
        result = engine.reconcile(status.client_order_id)
        assert isinstance(result, OrderStatus)
        assert result.state is OrderState.FILLED

    def test_reconcile_all_open_returns_a_report(self) -> None:
        from ai_trader.execution_engine.types import ExecutionReport

        engine, adapter = _configured_engine(fill_on_submit=False)
        decision, portfolio = make_allow_decision()
        status = engine.execute(decision, portfolio)
        adapter.push_fill(status.client_order_id, filled_qty=1.0, avg_price=100.0, full=True)
        report = engine.reconcile()
        assert isinstance(report, ExecutionReport)
        assert len(report.fills) == 1


class TestReport:
    def test_report_accumulates_fills_across_calls(self) -> None:
        engine, _adapter = _configured_engine()
        d1, p1 = make_allow_decision(strategy_id="S1")
        d2, p2 = make_allow_decision(strategy_id="S2")
        engine.execute(d1, p1)
        engine.execute(d2, p2)
        report = engine.report()
        assert len(report.fills) == 2
        assert len(report.results) == 2


class TestEmergencyFlatten:
    def test_flattens_open_positions_and_refuses_new_opens(self) -> None:
        engine, adapter = _configured_engine()
        existing = make_portfolio()
        from ai_trader.risk_manager.types import OpenPosition
        from ai_trader.signal_engine.types import Direction
        position = OpenPosition(
            symbol="XAUUSD", strategy_id="S1", direction=Direction.LONG, size_units=5.0,
            entry_price=100.0, opened_bars_ago=3, risk_pct=0.005,
        )
        portfolio_with_position = make_portfolio(open_positions=(position,))
        # prime _last_portfolio via a harmless prior execute() with a DIFFERENT symbol so the flatten
        # scope sees the position.
        decoy, _pf = make_deny_decision(strategy_id="S9", symbol="EURUSD")
        engine.execute(decoy, portfolio_with_position)

        report = engine.emergency_flatten()
        assert engine.health().state is EngineLifecycleState.EMERGENCY_FLATTEN
        assert len(report.results) >= 1
        closing_result = next(r for r in report.results if "FLATTEN" in r.client_order_id)
        assert closing_result.terminal_state is OrderState.FILLED

        # new OPENING decisions are refused while EMERGENCY_FLATTEN is active
        opening, _pf2 = make_allow_decision(strategy_id="S2")
        status = engine.execute(opening, portfolio_with_position)
        assert status.state is OrderState.REJECTED
        assert "EMERGENCY_FLATTEN_ACTIVE" in status.reasons[0]

    def test_reduce_only_decisions_still_accepted_during_emergency_flatten(self) -> None:
        engine, adapter = _configured_engine()
        decoy, pf = make_deny_decision(strategy_id="S9")
        engine.execute(decoy, pf)
        engine.emergency_flatten()
        reduce_decision, portfolio = make_reduce_only_allow_decision(strategy_id="S3")
        status = engine.execute(reduce_decision, portfolio)
        assert status.state is OrderState.FILLED

    def test_scope_restricts_to_named_symbols(self) -> None:
        engine, adapter = _configured_engine()
        from ai_trader.risk_manager.types import OpenPosition
        from ai_trader.signal_engine.types import Direction
        gold = OpenPosition(symbol="XAUUSD", strategy_id="S1", direction=Direction.LONG, size_units=1.0, entry_price=100.0, opened_bars_ago=1, risk_pct=0.001)
        eur = OpenPosition(symbol="EURUSD", strategy_id="S2", direction=Direction.LONG, size_units=1.0, entry_price=1.0, opened_bars_ago=1, risk_pct=0.001)
        portfolio = make_portfolio(open_positions=(gold, eur))
        decoy, _pf = make_deny_decision(strategy_id="S9", symbol="GBPUSD")
        engine.execute(decoy, portfolio)

        report = engine.emergency_flatten(FlattenScope(symbols=frozenset({"XAUUSD"})))
        flatten_ids = [r.client_order_id for r in report.results if "FLATTEN" in r.client_order_id]
        assert any("XAUUSD" in cid for cid in flatten_ids)
        assert not any("EURUSD" in cid for cid in flatten_ids)

    def test_no_portfolio_yet_flatten_is_disclosed_as_degraded_not_a_silent_no_op(self) -> None:
        """Regression guard (adversarial review, HIGH finding): emergency_flatten() called before any
        PortfolioState has ever been observed must NOT silently report an empty "nothing to do" --
        that would be indistinguishable from a genuine successful flatten of zero positions. It must
        be disclosed as degraded, since it's a safety mechanism that couldn't actually act."""
        engine, _adapter = _configured_engine()
        report = engine.emergency_flatten()
        assert report.results == ()
        assert engine.health().state is EngineLifecycleState.EMERGENCY_FLATTEN
        assert engine.health().overall is EngineOverallHealth.DEGRADED
        assert any("PortfolioState" in r for r in engine.health().degraded_reasons)

    def test_a_position_that_fails_to_build_does_not_abort_flattening_the_rest(self) -> None:
        from dataclasses import replace as dc_replace
        from ai_trader.risk_manager.types import OpenPosition
        from ai_trader.signal_engine.types import Direction
        from ai_trader.execution_engine.types import MarketStatus

        multi_symbol_caps = dc_replace(
            make_capabilities(),
            market_status={"XAUUSD": MarketStatus.OPEN, "EURUSD": MarketStatus.OPEN, "GBPUSD": MarketStatus.OPEN},
        )
        engine, adapter = _configured_engine()
        adapter.caps = multi_symbol_caps
        engine.configure(adapter)  # re-handshake so engine._caps picks up the multi-symbol profile

        unbuildable = OpenPosition(
            symbol="XAUUSD", strategy_id="S1", direction=Direction.NONE, size_units=5.0,
            entry_price=100.0, opened_bars_ago=1, risk_pct=0.001,
        )
        buildable = OpenPosition(
            symbol="EURUSD", strategy_id="S2", direction=Direction.LONG, size_units=5.0,
            entry_price=1.0, opened_bars_ago=1, risk_pct=0.001,
        )
        portfolio = make_portfolio(open_positions=(unbuildable, buildable))
        decoy, _pf = make_deny_decision(strategy_id="S9", symbol="GBPUSD")
        engine.execute(decoy, portfolio)

        report = engine.emergency_flatten()
        flatten_results = [r for r in report.results if "FLATTEN" in r.client_order_id]
        assert any("EURUSD" in r.client_order_id and r.terminal_state is OrderState.FILLED for r in flatten_results)
        assert not any("XAUUSD" in r.client_order_id for r in flatten_results)

    def test_submit_exception_during_flatten_is_classified_not_a_crash(self) -> None:
        from unittest.mock import patch
        from ai_trader.risk_manager.types import OpenPosition
        from ai_trader.signal_engine.types import Direction

        engine, adapter = _configured_engine()
        position = OpenPosition(
            symbol="XAUUSD", strategy_id="S1", direction=Direction.LONG, size_units=5.0,
            entry_price=100.0, opened_bars_ago=1, risk_pct=0.001,
        )
        portfolio = make_portfolio(open_positions=(position,))
        decoy, _pf = make_deny_decision(strategy_id="S9", symbol="GBPUSD")
        engine.execute(decoy, portfolio)

        with patch.object(adapter, "submit_order", side_effect=RuntimeError("boom")):
            report = engine.emergency_flatten()
        failures = [r for r in report.results if r.terminal_state is OrderState.FAILED]
        assert len(failures) == 1
        assert "INTERNAL_ERROR" in failures[0].reasons[0]

    def test_build_exception_during_flatten_does_not_abort_flattening_the_rest(self) -> None:
        """Regression guard (adversarial review, HIGH finding): the BUILD stage of emergency_flatten
        (unlike the submit stage) previously had no exception safety net at all."""
        from ai_trader.risk_manager.types import OpenPosition
        from ai_trader.signal_engine.types import Direction

        engine, adapter = _configured_engine()
        p1 = OpenPosition(
            symbol="XAUUSD", strategy_id="S1", direction=Direction.LONG, size_units=5.0,
            entry_price=100.0, opened_bars_ago=1, risk_pct=0.001,
        )
        p2 = OpenPosition(
            symbol="XAUUSD", strategy_id="S2", direction=Direction.LONG, size_units=5.0,
            entry_price=100.0, opened_bars_ago=1, risk_pct=0.001,
        )
        portfolio = make_portfolio(open_positions=(p1, p2))
        decoy, _pf = make_deny_decision(strategy_id="S9", symbol="GBPUSD")
        engine.execute(decoy, portfolio)

        from ai_trader.execution_engine import builder as builder_module
        from ai_trader.execution_engine.builder import BuildOutcome
        from ai_trader.execution_engine.config import ExecConfig as _ExecConfig
        from ai_trader.execution_engine.types import BrokerCapabilities as _BrokerCapabilities
        from ai_trader.risk_manager.types import OpenPosition as _OpenPosition

        call_count = 0
        real_build_flatten_order = builder_module.build_flatten_order

        def _flaky_build(
            position: _OpenPosition, caps: _BrokerCapabilities, config: _ExecConfig, as_of: int,
            risk_schema_version: str, risk_policy_version: str,
        ) -> BuildOutcome:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("boom")
            return real_build_flatten_order(position, caps, config, as_of, risk_schema_version, risk_policy_version)

        with patch("ai_trader.execution_engine.engine.builder.build_flatten_order", side_effect=_flaky_build):
            report = engine.emergency_flatten()
        # the second position was still flattened despite the first one's build raising.
        flatten_results = [r for r in report.results if "FLATTEN" in r.client_order_id]
        assert any(r.terminal_state is OrderState.FILLED for r in flatten_results)


class TestStatisticsHealthVersions:
    def test_statistics_track_orders_and_fills(self) -> None:
        engine, _adapter = _configured_engine()
        decision, portfolio = make_allow_decision()
        engine.execute(decision, portfolio)
        stats = engine.statistics()
        assert stats.orders_total == 1
        assert stats.fills == 1

    def test_statistics_track_rejects(self) -> None:
        engine, _adapter = _configured_engine()
        decision, portfolio = make_deny_decision()
        engine.execute(decision, portfolio)
        assert engine.statistics().rejects == 1

    def test_versions_reflect_config(self) -> None:
        engine = ExecutionEngine(ExecConfig(execution_engine_version="9.9.9"))
        engine.configure(FakeBrokerAdapter(caps=CAPS))
        info = engine.versions()
        assert info.execution_engine_version == "9.9.9"
        assert info.supported_risk_schema_major == 1

    def test_health_broker_available_reflects_configuration(self) -> None:
        engine = ExecutionEngine()
        assert engine.health().broker_available is False
        engine.configure(FakeBrokerAdapter(caps=CAPS))
        assert engine.health().broker_available is True


class TestShutdown:
    def test_shutdown_reports_true_last_known_health(self) -> None:
        engine, _adapter = _configured_engine()
        health = engine.shutdown()
        assert health.overall is EngineOverallHealth.OK

    def test_execute_after_shutdown_raises(self) -> None:
        engine, _adapter = _configured_engine()
        engine.shutdown()
        decision, portfolio = make_allow_decision()
        with pytest.raises(EngineNotConfiguredError):
            engine.execute(decision, portfolio)

    def test_shutdown_with_pending_orders_reconciles_them_to_a_definite_state(self) -> None:
        engine, adapter = _configured_engine(fill_on_submit=False)
        decision, portfolio = make_allow_decision()
        status = engine.execute(decision, portfolio)
        assert status.state is OrderState.ACKNOWLEDGED
        adapter.push_fill(status.client_order_id, filled_qty=1.0, avg_price=100.0, full=True)
        calls_before = len(adapter.query_status_calls)
        engine.shutdown()
        # DRAINING queried the broker again (reconciled), never abandoning the order at ACKNOWLEDGED --
        # confirmed via the adapter's own call log, since configure() would otherwise wipe the Ledger
        # this test would need to inspect directly.
        assert len(adapter.query_status_calls) > calls_before
        assert status.client_order_id in adapter.query_status_calls[calls_before:]

    def test_shutdown_releases_the_adapter(self) -> None:
        engine, _adapter = _configured_engine()
        engine.shutdown()
        assert engine.health().broker_available is False

    def test_shutdown_with_a_flaky_broker_still_reaches_stopped(self) -> None:
        """Regression guard (adversarial review, CRITICAL finding #2): a broker exception during
        DRAINING's reconciliation must never leave the engine stuck mid-shutdown."""
        engine, adapter = _configured_engine(fill_on_submit=False)
        decision, portfolio = make_allow_decision()
        engine.execute(decision, portfolio)
        with patch.object(adapter, "query_status", side_effect=RuntimeError("boom")):
            health = engine.shutdown()  # must not raise
        assert health is not None
        assert engine.health().state is EngineLifecycleState.STOPPED


class TestDeterminism:
    def test_execute_is_deterministic_across_engines(self) -> None:
        decision, portfolio = make_allow_decision()
        engine1, _a1 = _configured_engine()
        engine2, _a2 = _configured_engine()
        status1 = engine1.execute(decision, portfolio)
        status2 = engine2.execute(decision, portfolio)
        assert status1 == status2
