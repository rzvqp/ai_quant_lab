"""The Performance Analyzer -- metrics, attribution & reporting (``PERFORMANCE_ANALYZER.md``).

Read-only analytics: turns the Portfolio Simulator's trade ledger + equity curve into the
``SimulationReport`` (``SIMULATION_SCHEMA.json``). Every metric is a deterministic function of the
recorded inputs -- no decisions, no learning, no optimization (``PERFORMANCE_ANALYZER.md`` §1).

Metrics the frozen docs name without a documented tolerance/formula-gap are computed with a
straightforward, disclosed, industry-standard formula; where the docs name a quantity this module
genuinely cannot compute from the recorded inputs without fabricating data (``max_drawdown_R`` at the
portfolio level, per-period ``return_pct``/``max_drawdown_pct`` for session/daily/monthly rollups, a
full time-series capital-allocation report), the field is left ``None`` rather than invented -- listed
in ``SIMULATION_FRAMEWORK_VALIDATION_REPORT.md``'s known-limitations section.
"""

from __future__ import annotations

import math
import statistics
from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone

from ai_trader.simulation.config import SimulationContext
from ai_trader.simulation.portfolio_simulator import EquityPoint, SimAccount, TradeRecord

_SECONDS_PER_YEAR = 365.25 * 86400


@dataclass(frozen=True, slots=True)
class PortfolioSummary:
    starting_balance: float
    final_balance: float
    final_equity: float
    net_profit: float
    return_pct: float
    max_drawdown_pct: float
    closed_pnl: float | None = None
    floating_pnl: float | None = None
    max_drawdown_R: float | None = None


@dataclass(frozen=True, slots=True)
class PerformanceMetrics:
    trades: int
    expectancy_R: float | None
    profit_factor: float | None
    win_rate: float | None
    sharpe: float | None
    max_drawdown_pct: float
    expectancy_currency: float | None = None
    payoff_ratio: float | None = None
    sortino: float | None = None
    cagr_pct: float | None = None
    recovery_factor: float | None = None
    avg_exposure_pct: float | None = None
    avg_holding_bars: float | None = None
    calmar: float | None = None
    turnover: float | None = None
    total_commission: float = 0.0
    total_spread_cost: float = 0.0
    total_slippage_cost: float = 0.0
    long_trades: int = 0
    short_trades: int = 0
    long_net_pnl: float = 0.0
    short_net_pnl: float = 0.0
    max_losing_streak: int = 0


@dataclass(frozen=True, slots=True)
class AttributionEntry:
    strategy_id: str
    trades: int
    net_pnl: float
    expectancy_R: float | None = None
    correlation_group: str | None = None
    win_rate: float | None = None
    profit_factor: float | None = None
    contribution_pct: float | None = None
    max_drawdown_contribution_pct: float | None = None
    exposure_share_pct: float | None = None


@dataclass(frozen=True, slots=True)
class AllocationReport:
    avg_allocation_by_strategy: dict[str, float] | None = None
    concentration_max_share_pct: float | None = None


@dataclass(frozen=True, slots=True)
class RiskEventSummary:
    type: str
    count: int
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class PeriodStat:
    period: str
    pnl: float
    trades: int
    return_pct: float | None = None
    win_rate: float | None = None
    max_drawdown_pct: float | None = None


@dataclass(frozen=True, slots=True)
class StatsRollup:
    session: tuple[PeriodStat, ...] = ()
    daily: tuple[PeriodStat, ...] = ()
    monthly: tuple[PeriodStat, ...] = ()


@dataclass(frozen=True, slots=True)
class Artifacts:
    trade_history_ref: str | None = None
    execution_log_ref: str | None = None
    equity_curve_ref: str | None = None


@dataclass(frozen=True, slots=True)
class SimulationReportData:
    portfolio_summary: PortfolioSummary
    performance: PerformanceMetrics
    attribution: tuple[AttributionEntry, ...]
    stats: StatsRollup
    allocation: AllocationReport | None = None
    risk_events: tuple[RiskEventSummary, ...] = ()
    artifacts: Artifacts | None = None


def to_schema_dict(
    context: SimulationContext, report: SimulationReportData, state: str,
    module_versions: dict[str, str], generated_at: int,
) -> dict[str, object]:
    """The exact ``SIMULATION_SCHEMA.json``-shaped dict for one finalized run -- used for schema
    validation and artifact persistence (``IMPLEMENTATION_CHOICES.md`` §8)."""
    from ai_trader.simulation.config import (
        COST_MODEL_VERSION, FILL_MODEL_VERSION, SIMULATION_FRAMEWORK_VERSION, SIMULATION_SCHEMA_VERSION,
    )

    def period_stats(stats: tuple[PeriodStat, ...]) -> list[dict[str, object]]:
        return [
            {"period": s.period, "pnl": s.pnl, "return_pct": s.return_pct, "trades": s.trades,
             "win_rate": s.win_rate, "max_drawdown_pct": s.max_drawdown_pct}
            for s in stats
        ]

    return {
        "simulation_schema_version": SIMULATION_SCHEMA_VERSION,
        "meta": {
            "run_id": context.run_id, "batch_id": context.batch_id, "state": state,
            "simulation_framework_version": SIMULATION_FRAMEWORK_VERSION,
            "fill_model_version": FILL_MODEL_VERSION, "cost_model_version": COST_MODEL_VERSION,
            "module_versions": module_versions, "generated_at": generated_at,
        },
        "context": {
            "run_id": context.run_id,
            "date_range": {"start": context.date_range.start, "end": context.date_range.end},
            "symbols": list(context.symbols), "timeframes": list(context.timeframes),
            "data_source": context.data_source, "warmup_bars": context.warmup_bars,
            "starting_balance": context.starting_balance, "base_currency": context.base_currency,
            "leverage_max": context.margin_model.leverage_max,
            "margin_model": {
                "initial_margin_pct": context.margin_model.initial_margin_pct,
                "maintenance_margin_pct": context.margin_model.maintenance_margin_pct,
            },
            "cost_model": {
                "spread_model": context.cost_model.spread_model,
                "commission_model": context.cost_model.commission_model,
            },
            "fill_model": {
                "entry_timing": context.fill_model.entry_timing.value,
                "intrabar": context.fill_model.intrabar.value,
                "partial_fill_policy": context.fill_model.partial_fill_policy.value,
                "limit_touch_rule": context.fill_model.limit_touch_rule,
                "slippage_model": context.fill_model.slippage_model.type.value,
            },
            "strategy_set": list(context.strategy_set) if isinstance(context.strategy_set, tuple) else context.strategy_set,
            "run_seed": context.run_seed, "deterministic": context.deterministic,
        },
        "report": {
            "portfolio_summary": {
                "starting_balance": report.portfolio_summary.starting_balance,
                "final_balance": report.portfolio_summary.final_balance,
                "final_equity": report.portfolio_summary.final_equity,
                "net_profit": report.portfolio_summary.net_profit,
                "return_pct": report.portfolio_summary.return_pct,
                "closed_pnl": report.portfolio_summary.closed_pnl,
                "floating_pnl": report.portfolio_summary.floating_pnl,
                "max_drawdown_pct": report.portfolio_summary.max_drawdown_pct,
                "max_drawdown_R": report.portfolio_summary.max_drawdown_R,
            },
            "performance": {
                "trades": report.performance.trades, "expectancy_R": report.performance.expectancy_R,
                "expectancy_currency": report.performance.expectancy_currency,
                "profit_factor": report.performance.profit_factor, "win_rate": report.performance.win_rate,
                "payoff_ratio": report.performance.payoff_ratio, "sharpe": report.performance.sharpe,
                "sortino": report.performance.sortino, "cagr_pct": report.performance.cagr_pct,
                "recovery_factor": report.performance.recovery_factor,
                "avg_exposure_pct": report.performance.avg_exposure_pct,
                "avg_holding_bars": report.performance.avg_holding_bars,
                "max_drawdown_pct": report.performance.max_drawdown_pct,
                "calmar": report.performance.calmar, "turnover": report.performance.turnover,
                "total_commission": report.performance.total_commission,
                "long_trades": report.performance.long_trades, "short_trades": report.performance.short_trades,
                "max_losing_streak": report.performance.max_losing_streak,
            },
            "attribution": [
                {"strategy_id": a.strategy_id, "correlation_group": a.correlation_group, "trades": a.trades,
                 "win_rate": a.win_rate, "expectancy_R": a.expectancy_R, "profit_factor": a.profit_factor,
                 "net_pnl": a.net_pnl, "contribution_pct": a.contribution_pct,
                 "max_drawdown_contribution_pct": a.max_drawdown_contribution_pct,
                 "exposure_share_pct": a.exposure_share_pct}
                for a in report.attribution
            ],
            "allocation": (
                {"avg_allocation_by_strategy": report.allocation.avg_allocation_by_strategy,
                 "concentration_max_share_pct": report.allocation.concentration_max_share_pct}
                if report.allocation is not None else None
            ),
            "risk_events": [{"type": e.type, "count": e.count, "detail": e.detail} for e in report.risk_events],
            "stats": {
                "session": period_stats(report.stats.session), "daily": period_stats(report.stats.daily),
                "monthly": period_stats(report.stats.monthly),
            },
            "artifacts": (
                {"trade_history_ref": report.artifacts.trade_history_ref,
                 "execution_log_ref": report.artifacts.execution_log_ref,
                 "equity_curve_ref": report.artifacts.equity_curve_ref}
                if report.artifacts is not None else None
            ),
        },
    }


def _mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def _session_of(as_of: int) -> str:
    """UTC-hour-bucket session classifier -- IMPLEMENTATION CHOICE (module docstring): a simple,
    disclosed approximation, not the Market Scanner's own internal session-anchoring logic (not part
    of its public API)."""
    hour = datetime.fromtimestamp(as_of, tz=timezone.utc).hour
    if hour < 7:
        return "asia"
    if hour < 12:
        return "london"
    if hour < 20:
        return "ny"
    return "late"


def _day_key(as_of: int) -> str:
    return datetime.fromtimestamp(as_of, tz=timezone.utc).strftime("%Y-%m-%d")


def _month_key(as_of: int) -> str:
    return datetime.fromtimestamp(as_of, tz=timezone.utc).strftime("%Y-%m")


def _rollup(trades: list[TradeRecord], key_fn: Callable[[int], str]) -> tuple[PeriodStat, ...]:
    groups: dict[str, list[TradeRecord]] = defaultdict(list)
    for t in trades:
        groups[key_fn(t.exit_as_of)].append(t)
    out: list[PeriodStat] = []
    for period in sorted(groups):
        ts = groups[period]
        wins = [t for t in ts if t.net_pnl > 0]
        out.append(PeriodStat(
            period=period, pnl=sum(t.net_pnl for t in ts), trades=len(ts),
            win_rate=(len(wins) / len(ts)) if ts else None,
        ))
    return tuple(out)


def _max_losing_streak(trades: list[TradeRecord]) -> int:
    streak = 0
    worst = 0
    for t in sorted(trades, key=lambda t: t.exit_as_of):
        if t.net_pnl < 0:
            streak += 1
            worst = max(worst, streak)
        else:
            streak = 0
    return worst


def analyze(context: SimulationContext, account: SimAccount) -> SimulationReportData:
    """Build the full ``SimulationReport`` from the finalized (or current) account state."""
    trades = list(account.trade_ledger)
    running_curve = [p for p in account.equity_curve if p.phase_running]

    net_profit = account.equity - account.starting_balance
    return_pct = (net_profit / account.starting_balance) if account.starting_balance else 0.0
    portfolio_summary = PortfolioSummary(
        starting_balance=account.starting_balance, final_balance=account.balance,
        final_equity=account.equity, net_profit=net_profit, return_pct=return_pct,
        max_drawdown_pct=account.max_drawdown_pct,
        closed_pnl=account.balance - account.starting_balance, floating_pnl=account.floating_pnl,
    )

    wins = [t for t in trades if t.net_pnl > 0]
    losses = [t for t in trades if t.net_pnl <= 0]
    gross_profit = sum(t.net_pnl for t in wins)
    gross_loss = -sum(t.net_pnl for t in losses)
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else None
    win_rate = (len(wins) / len(trades)) if trades else None
    r_values = [t.pnl_r for t in trades if t.pnl_r is not None]
    avg_win = _mean([t.net_pnl for t in wins])
    avg_loss = _mean([abs(t.net_pnl) for t in losses])
    payoff_ratio = (avg_win / avg_loss) if (avg_win is not None and avg_loss) else None

    sharpe, sortino = _risk_adjusted_returns(running_curve)
    cagr_pct = _cagr_pct(running_curve, account.starting_balance)
    recovery_factor = (
        net_profit / (account.max_drawdown_pct * account.starting_balance)
        if account.max_drawdown_pct > 0 else None
    )
    calmar = (cagr_pct / 100.0 / account.max_drawdown_pct) if (cagr_pct is not None and account.max_drawdown_pct > 0) else None
    avg_exposure_pct = (
        _mean([1.0 if p.open_positions > 0 else 0.0 for p in running_curve]) if running_curve else None
    )
    avg_equity = _mean([p.equity for p in running_curve]) or account.starting_balance
    turnover = (sum(t.qty * t.entry_price for t in trades) / avg_equity) if avg_equity else None

    long_trades = [t for t in trades if t.direction.value == "LONG"]
    short_trades = [t for t in trades if t.direction.value == "SHORT"]

    performance = PerformanceMetrics(
        trades=len(trades), expectancy_R=_mean(r_values), expectancy_currency=_mean([t.net_pnl for t in trades]),
        profit_factor=profit_factor, win_rate=win_rate, payoff_ratio=payoff_ratio, sharpe=sharpe,
        sortino=sortino, cagr_pct=cagr_pct, recovery_factor=recovery_factor, avg_exposure_pct=avg_exposure_pct,
        avg_holding_bars=_mean([float(t.holding_bars) for t in trades]), max_drawdown_pct=account.max_drawdown_pct,
        calmar=calmar, turnover=turnover, total_commission=sum(t.fees for t in trades),
        long_trades=len(long_trades), short_trades=len(short_trades),
        long_net_pnl=sum(t.net_pnl for t in long_trades), short_net_pnl=sum(t.net_pnl for t in short_trades),
        max_losing_streak=_max_losing_streak(trades),
    )

    attribution = _attribution(trades)
    risk_events = tuple(
        RiskEventSummary(type=t, count=c) for t, c in sorted(Counter(e.type for e in account.risk_events).items())
    )
    stats = StatsRollup(
        session=_rollup(trades, _session_of) if context.stats_rollups.session else (),
        daily=_rollup(trades, _day_key) if context.stats_rollups.daily else (),
        monthly=_rollup(trades, _month_key) if context.stats_rollups.monthly else (),
    )
    allocation = _allocation(trades)

    return SimulationReportData(
        portfolio_summary=portfolio_summary, performance=performance, attribution=attribution,
        stats=stats, allocation=allocation, risk_events=risk_events,
    )


def _attribution(trades: list[TradeRecord]) -> tuple[AttributionEntry, ...]:
    by_strategy: dict[str, list[TradeRecord]] = defaultdict(list)
    for t in trades:
        by_strategy[t.strategy_id].append(t)
    total_abs_net = sum(abs(t.net_pnl) for t in trades) or None
    out: list[AttributionEntry] = []
    for strategy_id in sorted(by_strategy):
        ts = by_strategy[strategy_id]
        wins = [t for t in ts if t.net_pnl > 0]
        gp = sum(t.net_pnl for t in ts if t.net_pnl > 0)
        gl = -sum(t.net_pnl for t in ts if t.net_pnl <= 0)
        net_pnl = sum(t.net_pnl for t in ts)
        r_values = [t.pnl_r for t in ts if t.pnl_r is not None]
        out.append(AttributionEntry(
            strategy_id=strategy_id, trades=len(ts), net_pnl=net_pnl,
            expectancy_R=_mean(r_values), win_rate=(len(wins) / len(ts)) if ts else None,
            profit_factor=(gp / gl) if gl > 0 else None,
            contribution_pct=(abs(net_pnl) / total_abs_net * 100.0) if total_abs_net else None,
        ))
    return tuple(out)


def _allocation(trades: list[TradeRecord]) -> AllocationReport | None:
    if not trades:
        return None
    notional_by_strategy: dict[str, float] = defaultdict(float)
    for t in trades:
        notional_by_strategy[t.strategy_id] += abs(t.qty * t.entry_price)
    total = sum(notional_by_strategy.values())
    if total <= 0:
        return None
    shares = {k: v / total for k, v in notional_by_strategy.items()}
    return AllocationReport(avg_allocation_by_strategy=shares, concentration_max_share_pct=max(shares.values()) * 100.0)


def _risk_adjusted_returns(curve: list[EquityPoint]) -> tuple[float | None, float | None]:
    if len(curve) < 3:
        return None, None
    returns: list[float] = []
    for prev, cur in zip(curve, curve[1:]):
        if prev.equity > 0:
            returns.append((cur.equity - prev.equity) / prev.equity)
    if len(returns) < 2:
        return None, None
    intervals = [b.as_of - a.as_of for a, b in zip(curve, curve[1:]) if b.as_of > a.as_of]
    median_interval = statistics.median(intervals) if intervals else 900
    periods_per_year = _SECONDS_PER_YEAR / median_interval if median_interval > 0 else 0.0

    mean_r = statistics.fmean(returns)
    stdev_r = statistics.pstdev(returns)
    sharpe = (mean_r / stdev_r * math.sqrt(periods_per_year)) if stdev_r > 0 else None

    downside = [r for r in returns if r < 0]
    downside_dev = statistics.pstdev(downside) if len(downside) >= 2 else None
    sortino = (mean_r / downside_dev * math.sqrt(periods_per_year)) if downside_dev else None
    return sharpe, sortino


def _cagr_pct(curve: list[EquityPoint], starting_balance: float) -> float | None:
    if len(curve) < 2 or starting_balance <= 0:
        return None
    duration_seconds = curve[-1].as_of - curve[0].as_of
    final_equity = curve[-1].equity
    if duration_seconds <= 0 or final_equity <= 0:
        return None
    years = duration_seconds / _SECONDS_PER_YEAR
    if years <= 0:
        return None
    growth: float = (final_equity / starting_balance) ** (1.0 / years)
    return (growth - 1.0) * 100.0
