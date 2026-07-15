"""Regression tests for every genuine finding from the mandatory fresh-eyes adversarial review
(``SIMULATION_HANDOFF.md`` §13). Each test is named after, and reproduces, the exact failure scenario
the review reported."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from ai_trader.execution_engine import builder
from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.tests.fixtures.fake_broker import make_capabilities
from ai_trader.execution_engine.tests.fixtures.fake_decision import make_allow_decision
from ai_trader.execution_engine.types import OrderType, TimeInForce
from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.risk_manager.types import Decision, DeniedReason
from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.config import (
    CloseAtEndPolicy, DateRange, FillModel, MarginModel, PartialFillPolicy, SimulationContext,
)
from ai_trader.simulation.execution_simulator import ExecutionSimulator
from ai_trader.simulation.harness import SimulationHarness
from ai_trader.simulation.portfolio_simulator import PortfolioSimulator
from ai_trader.simulation.types import Bar, RunState, SimFillEvent, WorkingOrderState

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data" / "market"
SYMBOL_META = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}


def make_context(**overrides: object) -> SimulationContext:
    defaults: dict[str, object] = dict(
        run_id="ADV-R1", date_range=DateRange(1_600_000_000, 1_600_100_000), symbols=("XAUUSD",),
        timeframes=("M15",), starting_balance=100_000.0, run_seed=1,
    )
    defaults.update(overrides)
    return SimulationContext(**defaults)  # type: ignore[arg-type]


def make_bar(as_of: int, o: float, h: float, l: float, c: float) -> Bar:
    return Bar(symbol="XAUUSD", timeframe="M15", ts_open=as_of - 900, ts_close=as_of, open=o, high=h, low=l, close=c)


def make_close_bar(as_of: int, close: float) -> Bar:
    return Bar(
        symbol="XAUUSD", timeframe="M15", ts_open=as_of - 900, ts_close=as_of,
        open=close, high=close + 0.1, low=close - 0.1, close=close,
    )


class TestFinding1FokPartialFillNeverLeaks:
    def test_fok_partial_that_gets_reverted_is_never_returned(self) -> None:
        context = make_context(fill_model=FillModel(
            partial_fill_policy=PartialFillPolicy.FIXED_FRACTION, partial_fill_fraction=0.3,
        ))
        caps = make_capabilities(symbol="XAUUSD", tick_size=0.01)
        decision, portfolio = make_allow_decision(entry=100.0, stop=99.0)
        outcome = builder.build_order(decision, portfolio, caps, ExecConfig())
        order = replace(outcome.order, order_type=OrderType.MARKET, limit_price=None, time_in_force=TimeInForce.FOK)

        exsim = ExecutionSimulator(context, caps)
        exsim.submit_order(order)
        bar = make_bar(order.as_of + 900, 100.0, 100.5, 99.5, 100.2)
        fills = exsim.advance_bar(order.as_of + 900, {"XAUUSD": bar})

        # FIXED_FRACTION only fills 30% on the first pass -> FOK must revert to CANCELLED with
        # filled_qty=0, and the caller must see NO fill at all (never a partial that later vanishes
        # from the order book while still counted in the caller's own ledger).
        assert fills == ()
        status = exsim.query_status(order.client_order_id)
        assert status is not None
        assert status.state.value == "CANCELLED"
        assert status.filled_qty == 0.0


class TestFinding2HarnessNeverCrashesOnUnexpectedException:
    def test_step_fails_the_run_instead_of_raising(self) -> None:
        context = SimulationContext(
            run_id="ADV-CRASH-1", date_range=DateRange(1_700_000_000, 1_700_020_000), symbols=("XAUUSD",),
            timeframes=("M15", "H1", "H4", "D1"), starting_balance=100_000.0, run_seed=1, warmup_bars=30,
        )
        harness = SimulationHarness(context, SYMBOL_META, DATA_DIR)
        harness.configure()
        harness.load()
        assert harness.state is RunState.WARMUP

        # Poison the composed Scanner so the NEXT bar's _run_one_bar raises mid-RUNNING -- proving the
        # harness fails the run deterministically instead of letting the exception propagate and crash
        # the caller.
        real_scanner = harness._scanner
        assert real_scanner is not None

        def _boom(as_of: int) -> object:
            raise RuntimeError("synthetic failure injected by test")

        real_scanner.advance_clock = _boom  # type: ignore[method-assign]
        harness.step()  # must not raise
        assert harness.state is RunState.FAILED
        assert harness.fail_reason is not None and "RUN_FAILED" in harness.fail_reason


class TestFinding3MarginPreFillRejection:
    def test_opening_fill_rejected_when_it_would_exceed_free_margin(self) -> None:
        context = make_context(margin_model=MarginModel(initial_margin_pct=0.5, maintenance_margin_pct=0.1))
        caps = make_capabilities(symbol="XAUUSD", tick_size=0.01, max_qty=1_000_000.0)
        decision, portfolio = make_allow_decision(entry=100.0, stop=99.0)
        outcome = builder.build_order(decision, portfolio, caps, ExecConfig())
        order = replace(outcome.order, order_type=OrderType.MARKET, limit_price=None)

        exsim = ExecutionSimulator(context, caps)
        exsim.set_free_margin_provider(lambda: 1.0)  # almost no free margin available
        exsim.submit_order(order)
        bar = make_bar(order.as_of + 900, 100.0, 100.5, 99.5, 100.2)
        fills = exsim.advance_bar(order.as_of + 900, {"XAUUSD": bar})

        assert fills == ()
        status = exsim.query_status(order.client_order_id)
        assert status is not None
        assert status.state.value == "REJECTED"
        assert status.reason == "INSUFFICIENT_MARGIN"

    def test_reduce_only_fill_never_blocked_by_margin(self) -> None:
        context = make_context()
        caps = make_capabilities(symbol="XAUUSD", tick_size=0.01)
        decision, portfolio = make_allow_decision(entry=100.0, stop=99.0)
        outcome = builder.build_order(decision, portfolio, caps, ExecConfig())
        order = replace(
            outcome.order, order_type=OrderType.MARKET, limit_price=None,
            constraints=replace(outcome.order.constraints, reduce_only=True),
        )
        exsim = ExecutionSimulator(context, caps)
        exsim.set_free_margin_provider(lambda: 0.0)  # zero free margin -- a closing fill must not care
        exsim.submit_order(order)
        bar = make_bar(order.as_of + 900, 100.0, 100.5, 99.5, 100.2)
        fills = exsim.advance_bar(order.as_of + 900, {"XAUUSD": bar})
        assert len(fills) == 1


class TestFinding4LiquidationThresholdMath:
    def test_liquidation_fires_at_half_of_required_margin_not_near_zero_equity(self) -> None:
        margin_model = MarginModel(initial_margin_pct=0.01, maintenance_margin_pct=0.005)  # shipped defaults
        symbol_meta = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}
        context = make_context(starting_balance=1000.0, margin_model=margin_model)
        psim = PortfolioSimulator(context, symbol_meta)
        fill = SimFillEvent(
            client_order_id="C1", order_request_id="R1", strategy_id="S1", symbol="XAUUSD",
            direction=Direction.LONG, intent_close=False, qty=50.0, price=100.0, spread_cost=0.0,
            slippage_cost=0.0, commission=0.0, as_of=1000,
        )
        psim.apply((fill,), bar_index=0)
        # used_margin = 50 * 100 * 0.01 = 50; equity must fall to 0.5 * 50 = 25 to trigger, at the
        # documented "half of initial margin" intent -- NOT to near-zero (the pre-fix off-by-~100x bug).
        # A price drop to 99.5 leaves equity = 1000 + (99.5-100)*50 = 975 -- still healthy, no liquidation.
        psim.mark_to_market(1900, {"XAUUSD": make_close_bar(1900, 99.5)})
        assert "XAUUSD" in psim.account.positions
        # A drop that pushes equity below the correct threshold (25) DOES liquidate.
        if "XAUUSD" in psim.account.positions:
            psim.mark_to_market(3700, {"XAUUSD": make_close_bar(3700, 80.0)})  # equity = 1000-1000=0 < 25
        assert "XAUUSD" not in psim.account.positions
        assert psim.account.liquidation_halted is True


class TestFinding5CloseAtEndPolicy:
    def test_close_at_last_closes_open_positions_at_run_end(self) -> None:
        context = SimulationContext(
            run_id="ADV-CLOSE-1", date_range=DateRange(1_700_000_000, 1_700_020_000), symbols=("XAUUSD",),
            timeframes=("M15", "H1", "H4", "D1"), starting_balance=100_000.0, run_seed=1, warmup_bars=30,
            close_at_end_policy=CloseAtEndPolicy.CLOSE_AT_LAST,
        )
        harness = SimulationHarness(context, SYMBOL_META, DATA_DIR)
        harness.configure()
        harness.load()
        assert harness.portfolio_simulator is not None
        # Force an open position directly (real strategies never trade in v1 -- see the harness
        # integration test docstring) to exercise close-at-end deterministically.
        harness.portfolio_simulator.apply((SimFillEvent(
            client_order_id="FORCED", order_request_id="FORCED", strategy_id="S1", symbol="XAUUSD",
            direction=Direction.LONG, intent_close=False, qty=1.0, price=100.0, spread_cost=0.0,
            slippage_cost=0.0, commission=0.0, as_of=harness.context.date_range.start,
        ),), bar_index=0)
        assert "XAUUSD" in harness.portfolio_simulator.account.positions
        harness.run_to_completion()
        assert harness.state is RunState.COMPLETED, harness.fail_reason
        assert "XAUUSD" not in harness.portfolio_simulator.account.positions, (
            "CLOSE_AT_LAST must close every open position by end of run"
        )

    def test_hold_and_mark_leaves_open_positions_open(self) -> None:
        context = SimulationContext(
            run_id="ADV-HOLD-1", date_range=DateRange(1_700_000_000, 1_700_020_000), symbols=("XAUUSD",),
            timeframes=("M15", "H1", "H4", "D1"), starting_balance=100_000.0, run_seed=1, warmup_bars=30,
            close_at_end_policy=CloseAtEndPolicy.HOLD_AND_MARK,
        )
        harness = SimulationHarness(context, SYMBOL_META, DATA_DIR)
        harness.configure()
        harness.load()
        assert harness.portfolio_simulator is not None
        harness.portfolio_simulator.apply((SimFillEvent(
            client_order_id="FORCED", order_request_id="FORCED", strategy_id="S1", symbol="XAUUSD",
            direction=Direction.LONG, intent_close=False, qty=1.0, price=100.0, spread_cost=0.0,
            slippage_cost=0.0, commission=0.0, as_of=harness.context.date_range.start,
        ),), bar_index=0)
        harness.run_to_completion()
        assert harness.state is RunState.COMPLETED, harness.fail_reason
        assert "XAUUSD" in harness.portfolio_simulator.account.positions


class TestFinding6ExecutionLogContainsRealFills:
    def test_execution_log_jsonl_contains_fill_records_not_risk_events(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        import json
        from ai_trader.simulation.api import SimulationAPI

        api = SimulationAPI(SYMBOL_META, DATA_DIR, results_dir=tmp_path)
        context = SimulationContext(
            run_id="ADV-EXECLOG-1", date_range=DateRange(1_700_000_000, 1_700_010_000), symbols=("XAUUSD",),
            timeframes=("M15", "H1", "H4", "D1"), starting_balance=100_000.0, run_seed=1, warmup_bars=30,
        )
        api.configure(context)
        harness = api._runs["ADV-EXECLOG-1"]
        harness.load()
        assert harness.portfolio_simulator is not None
        harness.portfolio_simulator.apply((SimFillEvent(
            client_order_id="FORCED", order_request_id="FORCED", strategy_id="S1", symbol="XAUUSD",
            direction=Direction.LONG, intent_close=False, qty=1.0, price=100.0, spread_cost=0.0,
            slippage_cost=1.0, commission=0.5, as_of=context.date_range.start,
        ),), bar_index=0)
        harness.run_to_completion()
        api._finalize("ADV-EXECLOG-1", harness)

        log_path = tmp_path / "ADV-EXECLOG-1" / "execution_log.jsonl"
        assert log_path.exists()
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) >= 1
        record = json.loads(lines[0])
        assert record["client_order_id"] == "FORCED"
        assert record["price"] == 100.0
        assert "type" not in record  # proves this is a Fill record, not a RiskEventRecord


class TestFinding7DenyDecisionsRecordedAsRiskEvents:
    def test_record_risk_event_used_for_deny(self) -> None:
        context = make_context()
        psim = PortfolioSimulator(context, SYMBOL_META)
        psim.record_risk_event("DENY_BELOW_FLOOR", as_of=1000, detail="strength below floor")
        assert len(psim.account.risk_events) == 1
        assert psim.account.risk_events[0].type == "DENY_BELOW_FLOOR"


class TestFinding8IocPartialFillNeverMislabeledFilled:
    def test_ioc_partial_fill_is_cancelled_not_filled(self) -> None:
        context = make_context(fill_model=FillModel(
            partial_fill_policy=PartialFillPolicy.FIXED_FRACTION, partial_fill_fraction=0.4,
        ))
        caps = make_capabilities(symbol="XAUUSD", tick_size=0.01)
        decision, portfolio = make_allow_decision(entry=100.0, stop=99.0)
        outcome = builder.build_order(decision, portfolio, caps, ExecConfig())
        order = replace(outcome.order, order_type=OrderType.MARKET, limit_price=None, time_in_force=TimeInForce.IOC)

        exsim = ExecutionSimulator(context, caps)
        exsim.submit_order(order)
        bar = make_bar(order.as_of + 900, 100.0, 100.5, 99.5, 100.2)
        fills = exsim.advance_bar(order.as_of + 900, {"XAUUSD": bar})
        assert len(fills) == 1  # the 40% partial DOES get reported (unlike FOK)

        status = exsim.query_status(order.client_order_id)
        assert status is not None
        assert status.state.value == "CANCELLED", "a partially-filled IOC must never be labeled FILLED"
        assert status.filled_qty == fills[0].qty
