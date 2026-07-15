"""Tests for the Performance Analyzer's metric formulas against a hand-built account (fixed inputs,
hand-computed expected outputs)."""

from __future__ import annotations

from dataclasses import replace

from ai_trader.signal_engine.types import Direction
from ai_trader.simulation import performance_analyzer
from ai_trader.simulation.config import DateRange, SimulationContext
from ai_trader.simulation.portfolio_simulator import EquityPoint, SimAccount, TradeRecord


def make_context(**overrides: object) -> SimulationContext:
    defaults: dict[str, object] = dict(
        run_id="R1", date_range=DateRange(1_600_000_000, 1_600_100_000), symbols=("XAUUSD",),
        timeframes=("M15",), starting_balance=1000.0, run_seed=1,
    )
    defaults.update(overrides)
    return SimulationContext(**defaults)  # type: ignore[arg-type]


def make_trade(net_pnl: float, exit_as_of: int, pnl_r: float | None = None, holding_bars: int = 4) -> TradeRecord:
    return TradeRecord(
        client_order_id="C", strategy_id="S1", symbol="XAUUSD", direction=Direction.LONG,
        entry_price=100.0, exit_price=100.0 + net_pnl, entry_as_of=exit_as_of - 3600, exit_as_of=exit_as_of,
        qty=1.0, gross_pnl=net_pnl, fees=0.0, net_pnl=net_pnl, pnl_r=pnl_r, holding_bars=holding_bars,
        mfe=0.0, mae=0.0,
    )


def test_win_rate_profit_factor_expectancy() -> None:
    context = make_context()
    account = SimAccount(starting_balance=1000.0, balance=1100.0, equity=1100.0, equity_hwm=1100.0)
    account.trade_ledger = [
        make_trade(50.0, 1000, pnl_r=1.0), make_trade(-20.0, 2000, pnl_r=-1.0), make_trade(70.0, 3000, pnl_r=2.0),
    ]
    report = performance_analyzer.analyze(context, account)
    assert report.performance.trades == 3
    assert abs(report.performance.win_rate - (2 / 3)) < 1e-9
    assert abs(report.performance.profit_factor - (120.0 / 20.0)) < 1e-9
    assert abs(report.performance.expectancy_currency - (100.0 / 3)) < 1e-9
    assert abs(report.performance.expectancy_R - (2.0 / 3)) < 1e-9


def test_no_trades_yields_none_metrics_not_fabricated() -> None:
    context = make_context()
    account = SimAccount(starting_balance=1000.0, balance=1000.0, equity=1000.0, equity_hwm=1000.0)
    report = performance_analyzer.analyze(context, account)
    assert report.performance.trades == 0
    assert report.performance.win_rate is None
    assert report.performance.profit_factor is None
    assert report.performance.expectancy_R is None


def test_no_losses_yields_none_profit_factor_not_infinity() -> None:
    context = make_context()
    account = SimAccount(starting_balance=1000.0, balance=1050.0, equity=1050.0, equity_hwm=1050.0)
    account.trade_ledger = [make_trade(50.0, 1000)]
    report = performance_analyzer.analyze(context, account)
    assert report.performance.profit_factor is None  # gross_loss == 0, never fabricated as inf


def test_net_profit_uses_equity_not_just_balance() -> None:
    context = make_context()
    account = SimAccount(starting_balance=1000.0, balance=1000.0, equity=1030.0, equity_hwm=1030.0, floating_pnl=30.0)
    report = performance_analyzer.analyze(context, account)
    assert report.portfolio_summary.net_profit == 30.0
    assert report.portfolio_summary.floating_pnl == 30.0
    assert report.portfolio_summary.closed_pnl == 0.0


def test_attribution_grouped_by_strategy() -> None:
    context = make_context()
    account = SimAccount(starting_balance=1000.0, balance=1050.0, equity=1050.0, equity_hwm=1050.0)
    t1 = make_trade(50.0, 1000)
    t2 = replace(t1, strategy_id="S2", net_pnl=-10.0, gross_pnl=-10.0)
    account.trade_ledger = [t1, t2]
    report = performance_analyzer.analyze(context, account)
    ids = {a.strategy_id for a in report.attribution}
    assert ids == {"S1", "S2"}


def test_max_losing_streak() -> None:
    context = make_context()
    account = SimAccount(starting_balance=1000.0, balance=1000.0, equity=1000.0, equity_hwm=1000.0)
    account.trade_ledger = [
        make_trade(10.0, 1000), make_trade(-5.0, 2000), make_trade(-5.0, 3000),
        make_trade(-5.0, 4000), make_trade(10.0, 5000),
    ]
    report = performance_analyzer.analyze(context, account)
    assert report.performance.max_losing_streak == 3


def test_warmup_phase_excluded_from_exposure_stat() -> None:
    context = make_context()
    account = SimAccount(starting_balance=1000.0, balance=1000.0, equity=1000.0, equity_hwm=1000.0)
    account.equity_curve = [
        EquityPoint(as_of=100, balance=1000, equity=1000, drawdown_pct=0.0, open_positions=1, phase_running=False),
        EquityPoint(as_of=200, balance=1000, equity=1000, drawdown_pct=0.0, open_positions=0, phase_running=True),
        EquityPoint(as_of=300, balance=1000, equity=1000, drawdown_pct=0.0, open_positions=0, phase_running=True),
    ]
    report = performance_analyzer.analyze(context, account)
    assert report.performance.avg_exposure_pct == 0.0  # only the two RUNNING points count, both flat


def test_schema_dict_round_trips_through_validator() -> None:
    from ai_trader.simulation.schema_validation import validate_simulation_run_dict
    context = make_context()
    account = SimAccount(starting_balance=1000.0, balance=1050.0, equity=1050.0, equity_hwm=1050.0)
    account.trade_ledger = [make_trade(50.0, 1000)]
    report = performance_analyzer.analyze(context, account)
    schema_dict = performance_analyzer.to_schema_dict(context, report, "COMPLETED", {}, generated_at=123)
    errors = validate_simulation_run_dict(schema_dict)
    assert errors == [], errors
